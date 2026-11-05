"""Split per-character recordings (voice_in/<character name>.mp3, all of that character's lines read in script order)
into one file per line id, using silences, and write them to voice_in/lines/<id>.wav for pack_voice.py.

    python split_voice.py analyze     # show, per file, how many speech segments each silence setting finds
    python split_voice.py split       # cut using the setting that matches the expected line count
"""
import collections, json, os, re, subprocess, sys

ROOT = r"E:\Tikshuv Games"
CONTENT = os.path.join(ROOT, "too-quiet", "content", "he")
SRC = os.path.join(ROOT, "voice_in")
OUT = os.path.join(SRC, "lines")

FILES = {  # file name -> speaker key (same order and filtering as VOICE_RECORDING_SCRIPT_FULL.md)
    "קריין": "narrator", "דבורה האורגת": "dvora", "גברת תמר": "innkeeper", "גברת אסתר": "mender", "מר צבי": "dockHand",
    "מר מנחם": "guildMaster", "הנחתום": "baker", "סבתא שושנה": "grandma", "רופאת הכפר": "clinicDoctor", "הטוחן": "miller",
    "סבא הד": "hubGrandpa", "הילד": "child", "תושב": "villager1", "תושבת": "villager2", "תושב שלישי": "villager3",
    "מר אליהו": "bellKeeper", "מר ברוך": "tailor",
}
EXTRA = {
    'boss.narrator.0001': ('narrator', 'x'), 'boss.narrator.0002': ('narrator', 'x'), 'boss.dvora.0003': ('dvora', 'x'),
    'end.narrator.0001': ('narrator', 'x'), 'end.narrator.0002': ('narrator', 'x'), 'end.narrator.0003': ('narrator', 'x'),
}


def key(k):
    return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', k)]


def lines_by_speaker():
    L = {}
    for f, k in (('lines.json', None), ('world/lines_world.json', None), ('problems_2_5.json', 'lines')):
        d = json.load(open(os.path.join(CONTENT, f), encoding='utf-8'))
        d = d[k] if k else d
        for i, v in d.items():
            L[i] = (v['speaker'], v['text'])
    L.update(EXTRA)
    by = collections.defaultdict(list)
    for i, (sp, t) in L.items():
        if sp == 'player' or '{name}' in t:
            continue
        by[sp].append(i)
    return {sp: sorted(v, key=key) for sp, v in by.items()}


def segments(path, noise, dur):
    r = subprocess.run(['ffmpeg', '-v', 'info', '-i', path, '-af', f'silencedetect=n={noise}dB:d={dur}', '-f', 'null', '-'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    total = None
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', r.stderr)
    if m:
        total = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', r.stderr)]
    ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', r.stderr)]
    segs, cur = [], 0.0
    for s, e in zip(starts, ends):
        if s - cur > 0.25:
            segs.append((cur, s))
        cur = e
    if total and total - cur > 0.25:
        segs.append((cur, total))
    return segs, total


def best(path, want):
    hits = []
    for noise in (-50, -46, -42, -38, -34, -30):
        for dur in (0.35, 0.5, 0.7, 0.9, 1.2, 1.6):
            segs, _ = segments(path, noise, dur)
            if len(segs) == want:
                hits.append((noise, dur, segs))
    return hits


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'analyze'
    want = lines_by_speaker()
    os.makedirs(OUT, exist_ok=True)
    for name, sp in FILES.items():
        path = os.path.join(SRC, name + '.mp3')
        if not os.path.exists(path):
            print('MISSING', name)
            continue
        n = len(want[sp])
        hits = best(path, n)
        _, total = segments(path, -40, 0.7)
        print(f"{sp:13} expect {n:3} lines | {round(total or 0)}s | exact matches: {len(hits)} of 36 settings")
        if mode == 'split' and hits:
            noise, dur, segs = hits[len(hits) // 2]
            for (a, b), lid in zip(segs, want[sp]):
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(max(0, a - 0.12)), '-to', str(b + 0.15), '-i', path,
                                '-ac', '1', os.path.join(OUT, lid + '.wav')], check=True)
            print('   split with', noise, 'dB /', dur, 's')
