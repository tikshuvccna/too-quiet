"""Transcribe every packed voice line and compare it with the expected text. Lines that do not match well are
moved to public/assets/voice/_rejected/ and dropped from index.json (they stay subtitle-only)."""
import difflib, json, os, re, shutil
from faster_whisper import WhisperModel
V = 'public/assets/voice'
ids = json.load(open(f'{V}/index.json'))['ids']
texts = {}
for f, k in (('lines.json', None), ('world/lines_world.json', None), ('problems_2_5.json', 'lines')):
    d = json.load(open('content/he/' + f, encoding='utf-8')); d = d[k] if k else d
    for i, v in d.items(): texts[i] = v['text']
texts.update({'boss.narrator.0001': 'הענן הענק יורד אל הכפר. החוטים בשמיים רועדים.',
 'boss.narrator.0002': 'הוא לא נראה כועס. הוא נראה סקרן, והוא חותך חוטים.',
 'boss.dvora.0003': 'המחט רואה אותם עכשיו. רוצו אל החוט החתוך, וחברו אותו נכון.',
 'end.narrator.0001': 'הראש מרפה את אצבעותיו. החוטים יורדים בשקט, וכל אחד נקשר לבית שלו.',
 'end.narrator.0002': 'הוא לא נעלם. הוא מביט, ושואל: מה עוד אפשר ללמוד?',
 'end.narrator.0003': 'בעמק זמזום חדש. לא קול של הד: קול של רשת.'})
def toks(s):
    s = re.sub(r'[\u0591-\u05C7]', '', s)
    return [t for t in (re.sub(r'[^\u05D0-\u05EA0-9]', '', x) for x in s.split()) if t]
m = WhisperModel("ivrit-ai/whisper-large-v3-turbo-ct2", device="cpu", compute_type="int8")
rep, keep = {}, []
os.makedirs(f'{V}/_rejected', exist_ok=True)
for n, i in enumerate(ids, 1):
    segs, _ = m.transcribe(f'{V}/{i}.mp3', language='he')
    heard = ' '.join(s.text for s in segs).strip()
    e, h = toks(texts[i]), toks(heard)
    sm = difflib.SequenceMatcher(None, e, h, autojunk=False)
    match = sum(b.size for b in sm.get_matching_blocks())
    rec, prec = match / max(1, len(e)), match / max(1, len(h))
    ok = rec >= 0.8 and prec >= 0.7
    rep[i] = {'recall': round(rec, 2), 'precision': round(prec, 2), 'ok': ok, 'heard': heard}
    (keep.append(i) if ok else shutil.move(f'{V}/{i}.mp3', f'{V}/_rejected/{i}.mp3'))
    print(n, len(ids), i, 'OK' if ok else 'REJECT', rep[i]['recall'], rep[i]['precision'], flush=True)
json.dump({'ids': keep}, open(f'{V}/index.json', 'w'))
json.dump(rep, open('cutscene_work/voice_verify.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('kept', len(keep), 'of', len(ids))
