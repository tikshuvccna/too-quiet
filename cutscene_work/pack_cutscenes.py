"""Turn the Flow clips in this folder into game assets: strip the audio, compress, write public/assets/cutscenes/<id>.mp4
and index.json (all ids found). Run after the clips are approved."""
import glob, json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'public', 'assets', 'cutscenes')
os.makedirs(OUT, exist_ok=True)
ids = []
for f in sorted(glob.glob(os.path.join(HERE, '*.mp4'))):
    cid = os.path.splitext(os.path.basename(f))[0]
    dst = os.path.join(OUT, cid + '.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-an', '-c:v', 'libx264', '-crf', '28', '-preset', 'slow',
                    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', dst], check=True)
    ids.append(cid)
    print(cid, round(os.path.getsize(dst) / 1e6, 2), 'MB')
json.dump({'ids': ids}, open(os.path.join(OUT, 'index.json'), 'w'))
print(len(ids), 'clips')
