import difflib, json, os, re, subprocess, sys
from faster_whisper import WhisperModel
sys.path.insert(0, 'cutscene_work')
ids = sys.argv[1:]
V = 'public/assets/voice'; L = r'E:\Tikshuv Games\voice_in\lines'
texts = {}
for f, k in (('lines.json', None), ('world/lines_world.json', None), ('problems_2_5.json', 'lines'), ('world/teacher_intro.json', 'lines')):
    d = json.load(open('content/he/' + f, encoding='utf-8')); d = d[k] if k else d
    for i, v in d.items(): texts[i] = v['text']
texts['boss.narrator.0001'] = 'הענן הענק יורד אל הכפר. החוטים בשמיים רועדים.'
def toks(s):
    s = re.sub(r'[\u0591-\u05C7]', '', s)
    return [t for t in (re.sub(r'[^\u05D0-\u05EA0-9]', '', x) for x in s.split()) if t]
m = WhisperModel("ivrit-ai/whisper-large-v3-turbo-ct2", device="cpu", compute_type="int8")
idx = json.load(open(f'{V}/index.json'))['ids']
for i in ids:
    src = os.path.join(L, i + '.wav')
    if not os.path.exists(src): print('no wav', i); continue
    dst = f'{V}/{i}.mp3'
    af = ('loudnorm=I=-16:TP=-1.5:LRA=11,apad=pad_dur=0.15' if os.environ.get('RAW') else 'silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=1:stop_threshold=-45dB:stop_duration=0.4,loudnorm=I=-16:TP=-1.5:LRA=11,apad=pad_dur=0.15')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-ac', '1', '-ar', '44100', '-af', af, '-b:a', '64k', dst], check=True)
    segs, _ = m.transcribe(dst, language='he')
    heard = ' '.join(s.text for s in segs).strip()
    e, h = toks(texts[i]), toks(heard)
    match = sum(b.size for b in difflib.SequenceMatcher(None, e, h, autojunk=False).get_matching_blocks())
    rec, prec = match / max(1, len(e)), match / max(1, len(h))
    ok = rec >= float(os.environ.get('MINREC', '0.8')) and prec >= 0.7
    print(('OK ' if ok else 'REJECT '), i, round(rec, 2), round(prec, 2), flush=True)
    if ok and i not in idx: idx.append(i)
    if not ok: os.remove(dst)
json.dump({'ids': sorted(set(idx))}, open(f'{V}/index.json', 'w'))
print('voice lines now', len(set(idx)))
