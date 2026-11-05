"""Rebuild the 15 world-2 interiors (shell + objects, facade + truth), then pack and make the contact sheet.

python art/build_interiors_w2.py                 # all 15 houses, 3 per Blender run, one process at a time (about 10 minutes)
python art/build_interiors_w2.py inn tailor      # only these houses
python art/build_interiors_w2.py --no-render     # pack + preview only
Writes public/assets/interiors/<house_id>/ (never touches house_grandma / house_clinic / house_print) and art/preview_interiors_w2.png.
"""
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "art", "blender"))
from iw2_layout import ORDER  # noqa

BLENDER = os.environ.get("BLENDER", r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
RAW = os.path.join(ROOT, "art", "_raw")
PY = sys.executable


def run(*a):
    t = time.time()
    subprocess.check_call(list(a))
    print(f"  -> {time.time() - t:.0f}s", flush=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    houses = args or ORDER
    if "--no-render" not in sys.argv:
        for i in range(0, len(houses), 3):
            batch = houses[i:i + 3]
            run(BLENDER, "-b", "--python", os.path.join(ROOT, "art", "blender", "interiors_w2.py"), "--", RAW, ",".join(batch))
    run(PY, os.path.join(ROOT, "art", "pack_interiors_w2.py"), RAW, *houses)
    run(PY, os.path.join(ROOT, "art", "make_preview_interiors_w2.py"))
