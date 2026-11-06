import json
from faster_whisper import WhisperModel
m = WhisperModel("ivrit-ai/whisper-large-v3-turbo-ct2", device="cpu", compute_type="int8")
segs, _ = m.transcribe(r'E:\Tikshuv Games\voice_in\new\rec1.m4a', language='he', word_timestamps=True)
json.dump([(round(s.start,1),round(s.end,1),s.text.strip()) for s in segs], open('cutscene_work/peek_rec1.json','w',encoding='utf-8'), ensure_ascii=False, indent=0)
