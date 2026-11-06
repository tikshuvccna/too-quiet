"""Match the uploaded recordings (voice_in/new/rec*.m4a) to characters by transcript, cut one wav per line id into
voice_in/lines/ (in the order the lines were listed to the player) and print a report."""
import difflib, json, os, re, subprocess, sys, glob
from faster_whisper import WhisperModel
ROOT = r"E:\Tikshuv Games"
SETS = {
 'narrator': ['r1.p2.narrator.0003','r1.p3.narrator.0003','r1.p4.narrator.0003','r1.p5.narrator.0003','boss.narrator.0001','r1.p0.narrator.0008','r1.p1.narrator.0004','r1.p1.narrator.0008','r1.p1.narrator.0013','r1.p1.narrator.0015'],
 'innkeeper': ['r1.p2.innkeeper.0003','t.p2.innkeeper.0001','t.p2.innkeeper.0002'],
 'mender': ['t.p3.mender.0001','t.p3.mender.0002'],
 'dockHand': ['t.p4.dockHand.0001','t.p4.dockHand.0002'],
 'guildMaster': ['r1.p5.guildMaster.0003','t.p5.guildMaster.0001','t.p5.guildMaster.0002'],
}
texts = {}
for f, k in (('lines.json', None), ('world/lines_world.json', None), ('problems_2_5.json', 'lines'), ('world/teacher_intro.json', 'lines')):
    d = json.load(open(os.path.join(ROOT, 'too-quiet', 'content', 'he', f), encoding='utf-8')); d = d[k] if k else d
    for i, v in d.items(): texts[i] = v['text']
texts['boss.narrator.0001'] = 'הענן הענק יורד אל הכפר. החוטים בשמיים רועדים.'
def toks(s):
    s = re.sub(r'[\u0591-\u05C7]', '', s)
    return [t for t in (re.sub(r'[^\u05D0-\u05EA0-9]', '', x) for x in s.split()) if t]
m = WhisperModel("ivrit-ai/whisper-large-v3-turbo-ct2", device="cpu", compute_type="int8")
OUT = os.path.join(ROOT, 'voice_in', 'lines'); os.makedirs(OUT, exist_ok=True)
rep = {}
ONLY = set(sys.argv[1:])
for f in sorted(glob.glob(os.path.join(ROOT, 'voice_in', 'new', 'rec*.m4a'))):
    if ONLY and os.path.basename(f) not in ONLY: continue
    segs, _ = m.transcribe(f, language='he', word_timestamps=True, beam_size=5)
    words = [(re.sub(r'[^\u05D0-\u05EA0-9]', '', w.word), w.start, w.end) for s in segs for w in s.words]
    words = [w for w in words if w[0]]
    got = [w[0] for w in words]
    best = (0, None)
    for ch, ids in SETS.items():
        exp = [t for i in ids for t in toks(texts[i])]
        sc = difflib.SequenceMatcher(None, exp, got, autojunk=False).ratio()
        if sc > best[0]: best = (sc, ch)
    sc, ch = best
    ids = SETS[ch]
    exp, owner = [], []
    for li, i in enumerate(ids):
        for t in toks(texts[i]): exp.append(t); owner.append(li)
    sm = difflib.SequenceMatcher(None, exp, got, autojunk=False)
    first, last, hit = {}, {}, {}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            li = owner[a + k]; gi = b + k
            first[li] = min(first.get(li, gi), gi); last[li] = max(last.get(li, gi), gi); hit[li] = hit.get(li, 0) + 1
    res = []
    for li, i in enumerate(ids):
        score = hit.get(li, 0) / max(1, len(toks(texts[i])))
        if li not in first or score < 0.6:
            res.append((i, round(score, 2), 'NOT FOUND')); continue
        s = words[first[li]][1]; e = words[last[li]][2]
        pe = words[last[li - 1]][2] if li > 0 and (li - 1) in last else 0.0
        ns = words[first[li + 1]][1] if (li + 1) in first else e + 1.0
        a = max(pe + (s - pe) * 0.35, s - 0.35) if li > 0 else max(0, s - 0.35)
        z = min(e + (ns - e) * 0.65, e + 0.45)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.2f}', '-to', f'{z:.2f}', '-i', f, '-ac', '1', os.path.join(OUT, i + '.wav')], check=True)
        res.append((i, round(score, 2), 'cut'))
    print(os.path.basename(f), '->', ch, 'match', round(sc, 2), flush=True)
    for r in res: print('   ', r, flush=True)
