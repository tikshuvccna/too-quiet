"""Pick one song per mood from music/, compress to 96 kbps and write public/assets/music/<mood>.mp3 + index.json.
Songs are named <mood>-<n> <title>.mp3; the first (-1) wins unless a pick is given in PICKS.
'win' is cut to a short jingle with a fade-out."""
import glob, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'public', 'assets', 'music')
PICKS = {}  # e.g. {'village': 2}
os.makedirs(OUT, exist_ok=True)
found = {}
for f in sorted(glob.glob(os.path.join(HERE, 'music', '*.mp3'))):
    m = re.match(r'([a-z]+)-(\d+) ', os.path.basename(f))
    if m:
        found.setdefault(m.group(1), {})[int(m.group(2))] = f
ids = []
for mood, songs in sorted(found.items()):
    n = PICKS.get(mood, min(songs))
    src = songs[n]
    dst = os.path.join(OUT, mood + '.mp3')
    cmd = ['ffmpeg', '-v', 'error', '-y', '-i', src, '-vn', '-ac', '2', '-ar', '44100', '-b:a', '96k']
    if mood == 'win':
        cmd += ['-t', '12', '-af', 'afade=t=out:st=9:d=3']
    cmd.append(dst)
    subprocess.run(cmd, check=True)
    ids.append(mood)
    print(mood, os.path.basename(src), round(os.path.getsize(dst) / 1e6, 2), 'MB')
json.dump({'ids': ids}, open(os.path.join(OUT, 'index.json'), 'w'))
print('total', round(sum(os.path.getsize(os.path.join(OUT, i + '.mp3')) for i in ids) / 1e6, 1), 'MB')
