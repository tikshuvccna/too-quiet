"""Second chance for rejected lines: transcribe each character file into sentence segments and pick, for every rejected
line, the run of consecutive segments whose text best matches it (token F1 >= 0.85). Cut, normalise, add to public/assets/voice."""
import difflib, json, os, re, subprocess, sys
sys.path.insert(0, 'cutscene_work')
import split_voice as sv
from faster_whisper import WhisperModel
V = 'public/assets/voice'
rep = json.load(open('cutscene_work/voice_verify.json', encoding='utf-8'))
rej = [i for i, v in rep.items() if not v['ok']]
texts = {}
for f, k in (('lines.json', None), ('world/lines_world.json', None), ('problems_2_5.json', 'lines')):
    d = json.load(open('content/he/' + f, encoding='utf-8')); d = d[k] if k else d
    for i, v in d.items(): texts[i] = v['text']
texts.update({'boss.narrator.0001': 'הענן הענק יורד אל הכפר. החוטים בשמיים רועדים.',
 'boss.narrator.0002': 'הוא לא נראה כועס. הוא נראה סקרן, והוא חותך חוטים.', 'boss.dvora.0003': 'המחט רואה אותם עכשיו. רוצו אל החוט החתוך, וחברו אותו נכון.',
 'end.narrator.0001': 'הראש מרפה את אצבעותיו. החוטים יורדים בשקט, וכל אחד נקשר לבית שלו.', 'end.narrator.0002': 'הוא לא נעלם. הוא מביט, ושואל: מה עוד אפשר ללמוד?',
 'end.narrator.0003': 'בעמק זמזום חדש. לא קול של הד: קול של רשת.'})
def toks(s):
    s = re.sub(r'[\u0591-\u05C7]', '', s)
    return [t for t in (re.sub(r'[^\u05D0-\u05EA0-9]', '', x) for x in s.split()) if t]
def f1(e, h):
    m = sum(b.size for b in difflib.SequenceMatcher(None, e, h, autojunk=False).get_matching_blocks())
    if not m: return 0, 0, 0
    r, p = m / len(e), m / len(h)
    return 2 * r * p / (r + p), r, p
m = WhisperModel("ivrit-ai/whisper-large-v3-turbo-ct2", device="cpu", compute_type="int8")
by = {}
for i in rej:
    by.setdefault(i.split('.')[-2], []).append(i)
ids = json.load(open(f'{V}/index.json'))['ids']
added = []
for name, sp in sv.FILES.items():
    if sp not in by: continue
    path = os.path.join(sv.SRC, name + '.mp3')
    segs = [(s.start, s.end, s.text) for s in m.transcribe(path, language='he', beam_size=5)[0]]
    for lid in by[sp]:
        e = toks(texts[lid]); best = (0, None)
        for a in range(len(segs)):
            for b in range(a, min(len(segs), a + 6)):
                h = toks(' '.join(x[2] for x in segs[a:b + 1]))
                sc, r, p = f1(e, h)
                if sc > best[0]: best = (sc, (a, b, r, p))
        if best[0] >= 0.85:
            a, b, r, p = best[1]
            s0 = segs[a][0]; s1 = segs[b][1]
            lo = (segs[a - 1][1] + s0) / 2 if a > 0 else max(0, s0 - 0.3); hi = (s1 + segs[b + 1][0]) / 2 if b + 1 < len(segs) else s1 + 0.4
            lo = max(lo, s0 - 0.4); hi = min(hi, s1 + 0.5)
            dst = os.path.join(V, lid + '.mp3')
            af = 'silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=1:stop_threshold=-45dB:stop_duration=0.4,loudnorm=I=-16:TP=-1.5:LRA=11,apad=pad_dur=0.15'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{lo:.2f}', '-to', f'{hi:.2f}', '-i', path, '-ac', '1', '-ar', '44100', '-af', af, '-b:a', '64k', dst], check=True)
            ids.append(lid); added.append(lid)
            print('SAVED', lid, round(best[0], 2), flush=True)
        else:
            print('no match', lid, round(best[0], 2), flush=True)
json.dump({'ids': sorted(set(ids))}, open(f'{V}/index.json', 'w'))
print('added', len(added), 'total', len(set(ids)))
