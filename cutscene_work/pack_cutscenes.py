"""Turn the Flow clips in this folder into game assets: strip the audio, compress, write public/assets/cutscenes/<id>.mp4
and index.json (all ids found). Run after the clips are approved."""
import glob, json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'public', 'assets', 'cutscenes')
os.makedirs(OUT, exist_ok=True)
ids = []
for f0 in sorted(glob.glob(os.path.join(HERE, '*.mp4'))):
    cid = os.path.splitext(os.path.basename(f0))[0]
    hd = os.path.join(HERE, 'hd', cid + '.mp4')
    f = hd if os.path.exists(hd) else f0   # the 720p upscale when there is one
    dst = os.path.join(OUT, cid + '.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-an', '-c:v', 'libx264', '-crf', '28', '-preset', 'slow',
                    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', dst], check=True)
    ids.append(cid)
    print(cid, round(os.path.getsize(dst) / 1e6, 2), 'MB')
json.dump({'ids': ids}, open(os.path.join(OUT, 'index.json'), 'w'))
print(len(ids), 'clips')
