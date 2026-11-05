"""Rebuild the 14 wc_ world creatures (needs Blender 5.2 + Pillow). About 2 minutes.

python art/build_wc_creatures.py              # render (one Blender process) + pack + preview
python art/build_wc_creatures.py pack         # stages: render | pack
Raw renders: art/_raw/wc (git-ignored). Outputs: public/assets/creatures/wc_*.png|json, wc_codex.png|json,
new wc_ entries in creatures/index.json, art/wc_keys.txt, art/preview_wc_creatures.png.
"""
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLENDER = os.environ.get("BLENDER", r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
RAW = os.path.join(ROOT, "art", "_raw", "wc")
PY = sys.executable


def run(*a):
    t = time.time()
    subprocess.check_call(list(a))
    print(f"  -> {time.time() - t:.0f}s")


STAGES = {
    "render": lambda: run(BLENDER, "-b", "--python", os.path.join(ROOT, "art", "blender", "wc_creatures.py"), "--", "all", RAW),
    "pack": lambda: [run(PY, os.path.join(ROOT, "art", "pack_wc.py"), RAW),
                     run(PY, os.path.join(ROOT, "art", "make_preview_wc.py"))],
}

if __name__ == "__main__":
    for s in sys.argv[1:] or list(STAGES):
        print("==", s)
        STAGES[s]()
