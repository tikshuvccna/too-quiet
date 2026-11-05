import json, os, random
from faster_whisper import WhisperModel
ids=json.load(open('public/assets/voice/index.json'))['ids']
random.seed(7); pick=random.sample(ids,6)
texts={}
for f,k in (('lines.json',None),('world/lines_world.json',None),('problems_2_5.json','lines')):
    d=json.load(open('content/he/'+f,encoding='utf-8')); d=d[k] if k else d
    for i,v in d.items(): texts[i]=v['text']
m=WhisperModel("ivrit-ai/whisper-large-v3-turbo-ct2",device="cpu",compute_type="int8")
out=[]
for i in pick:
    segs,_=m.transcribe(f'public/assets/voice/{i}.mp3',language='he')
    out.append({'id':i,'heard':' '.join(s.text for s in segs).strip(),'expected':texts.get(i,'(inline)')})
json.dump(out,open('cutscene_work/spot.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
