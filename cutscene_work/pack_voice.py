"""Turn the recordings in E:\Tikshuv Games\voice_in into game voice lines.
File name = line id (e.g. r1.p0.narrator.0001.wav / .mp3 / .m4a). Each is trimmed of silence, loudness-normalised
(-16 LUFS, mono) and written as public/assets/voice/<id>.mp3 (64 kbps), then index.json lists them."""
import glob, json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join("E:/Tikshuv Games", "voice_in", "lines")
OUT = os.path.join(HERE, '..', 'public', 'assets', 'voice')
os.makedirs(OUT, exist_ok=True)
best = {}
for f in sorted(glob.glob(os.path.join(SRC, '*'))):
    stem, ext = os.path.splitext(os.path.basename(f))
    if ext.lower() not in ('.wav', '.mp3', '.m4a', '.ogg', '.flac') or stem.startswith('_'):
        continue
    # a second take is named <id>__2 or <id>_2: the last file wins unless you delete it
    lid = stem.split('__')[0]
    best[lid] = f
ids = []
for lid, f in sorted(best.items()):
    dst = os.path.join(OUT, lid + '.mp3')
    af = ('silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=1:stop_threshold=-45dB:stop_duration=0.4,'
          'loudnorm=I=-16:TP=-1.5:LRA=11,apad=pad_dur=0.15')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-ac', '1', '-ar', '44100', '-af', af, '-b:a', '64k', dst], check=True)
    ids.append(lid)
    print(lid, round(os.path.getsize(dst) / 1e3), 'KB')
json.dump({'ids': ids}, open(os.path.join(OUT, 'index.json'), 'w'))
print(len(ids), 'voice lines')
