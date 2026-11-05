import json, os, subprocess, sys
sys.path.insert(0, '.')
import split_voice as sv
from faster_whisper import WhisperModel
r = json.load(open(os.path.join(sv.OUT, '_report.json'), encoding='utf-8'))
want = sv.lines_by_speaker()
model = WhisperModel("ivrit-ai/whisper-large-v3-turbo-ct2", device="cpu", compute_type="int8")
for name, sp, lid in (("הטוחן", "miller", "r1.p0.miller.0001"), ("סבא הד", "hubGrandpa", "r1.p1.hubGrandpa.0002")):
    ids = want[sp]; i = ids.index(lid)
    path = os.path.join(sv.SRC, name + '.mp3')
    prev = r[sp].get(ids[i - 1]) if i > 0 else None
    nxt = r[sp].get(ids[i + 1]) if i + 1 < len(ids) else None
    a = prev['end'] if prev and prev.get('ok') else 0.0
    z = nxt['start'] if nxt and nxt.get('ok') else None
    out = os.path.join(sv.OUT, lid + '.wav')
    cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.2f}'] + (['-to', f'{z:.2f}'] if z else []) + ['-i', path, '-ac', '1', out]
    subprocess.run(cmd, check=True)
    segs, _ = model.transcribe(out, language='he')
    print(lid, f'[{a:.1f}-{z}]', '|', ' '.join(s.text for s in segs))
