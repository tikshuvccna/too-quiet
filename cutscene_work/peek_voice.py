import json, os, sys
from faster_whisper import WhisperModel
m = WhisperModel("ivrit-ai/whisper-large-v3-turbo-ct2", device="cpu", compute_type="int8")
L = r'E:\Tikshuv Games\voice_in\lines'
out = {}
for name in ('r1.p3.narrator.0003', 'r1.p0.narrator.0008', 'r1.p1.narrator.0013'):
    segs, _ = m.transcribe(os.path.join(L, name + '.wav'), language='he')
    out[name] = ' '.join(s.text for s in segs).strip()
for f in ('rec4.m4a', 'rec2.m4a'):
    segs, _ = m.transcribe(os.path.join(r'E:\Tikshuv Games\voice_in\new', f), language='he', word_timestamps=True)
    out[f] = [(round(s.start, 1), round(s.end, 1), s.text.strip()) for s in segs]
json.dump(out, open('cutscene_work/peek_voice.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
