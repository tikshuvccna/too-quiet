"""Transcribe each per-character recording with the Hebrew Whisper model, align the words to the expected line texts
(in script order) and cut one wav per line id into voice_in/lines/. Writes voice_in/lines/_report.json with a score per line."""
import difflib, json, os, re, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import split_voice as sv
from faster_whisper import WhisperModel

only = set(sys.argv[1:])
os.makedirs(sv.OUT, exist_ok=True)
texts = {}
for f, k in (('lines.json', None), ('world/lines_world.json', None), ('problems_2_5.json', 'lines')):
    d = json.load(open(os.path.join(sv.CONTENT, f), encoding='utf-8'))
    d = d[k] if k else d
    for i, v in d.items():
        texts[i] = v['text']
texts.update({
    'boss.narrator.0001': 'הענן הענק יורד אל הכפר. החוטים בשמיים רועדים.',
    'boss.narrator.0002': 'הוא לא נראה כועס. הוא נראה סקרן, והוא חותך חוטים.',
    'boss.dvora.0003': 'המחט רואה אותם עכשיו. רוצו אל החוט החתוך, וחברו אותו נכון.',
    'end.narrator.0001': 'הראש מרפה את אצבעותיו. החוטים יורדים בשקט, וכל אחד נקשר לבית שלו.',
    'end.narrator.0002': 'הוא לא נעלם. הוא מביט, ושואל: מה עוד אפשר ללמוד?',
    'end.narrator.0003': 'בעמק זמזום חדש. לא קול של הד: קול של רשת.',
})


def norm(w):
    w = re.sub(r'[֑-ׇ]', '', w)
    return re.sub(r'[^א-ת0-9a-zA-Z]', '', w)


def toks(s):
    return [t for t in (norm(x) for x in s.split()) if t]


t0 = time.time()
model = WhisperModel("ivrit-ai/whisper-large-v3-turbo-ct2", device="cpu", compute_type="int8")
print("model loaded", round(time.time() - t0), "s", flush=True)
want = sv.lines_by_speaker()
report = {}
for name, sp in sv.FILES.items():
    if only and sp not in only:
        continue
    path = os.path.join(sv.SRC, name + '.mp3')
    ids = want[sp]
    segs, _ = model.transcribe(path, language='he', word_timestamps=True, vad_filter=False, beam_size=5)
    words = [(norm(w.word), w.start, w.end) for s in segs for w in s.words if norm(w.word)]
    exp, owner = [], []
    for li, lid in enumerate(ids):
        for t in toks(texts[lid]):
            exp.append(t)
            owner.append(li)
    got = [w[0] for w in words]
    sm = difflib.SequenceMatcher(None, exp, got, autojunk=False)
    first, last, hit = {}, {}, {}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            li = owner[a + k]
            gi = b + k
            first[li] = min(first.get(li, gi), gi)
            last[li] = max(last.get(li, gi), gi)
            hit[li] = hit.get(li, 0) + 1
    # line boundaries: midpoint of the gap between the last word of a line and the first word of the next
    bounds = []
    for li in range(len(ids)):
        if li not in first:
            bounds.append(None)
            continue
        bounds.append((first[li], last[li]))
    out = {}
    for li, lid in enumerate(ids):
        b = bounds[li]
        score = hit.get(li, 0) / max(1, len(toks(texts[lid])))
        if b is None or score < 0.5:
            out[lid] = {'ok': False, 'score': round(score, 2)}
            continue
        s = words[b[0]][1]
        e = words[b[1]][2]
        prev_end = words[bounds[li - 1][1]][2] if li > 0 and bounds[li - 1] else 0.0
        next_start = words[bounds[li + 1][0]][1] if li + 1 < len(ids) and bounds[li + 1] else e + 1.0
        a = max(prev_end + (s - prev_end) * 0.35, s - 0.35) if li > 0 else max(0, s - 0.35)
        z = min(e + (next_start - e) * 0.65, e + 0.45)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.2f}', '-to', f'{z:.2f}', '-i', path, '-ac', '1',
                        os.path.join(sv.OUT, lid + '.wav')], check=True)
        out[lid] = {'ok': True, 'score': round(score, 2), 'start': round(a, 2), 'end': round(z, 2)}
    bad = [k for k, v in out.items() if not v['ok']]
    print(f"{sp:13} lines {len(ids):3} cut {len(ids) - len(bad):3} unmatched {bad}", flush=True)
    report[sp] = out
    json.dump(report, open(os.path.join(sv.OUT, '_report.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("done", round(time.time() - t0), "s")
