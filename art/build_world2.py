"""Rebuild ONLY the world-2 art (16 buildings + 23 props, facade + truth): python art/build_world2.py
Does not touch build_all.py outputs. Needs Blender 5.2 + Pillow. Runs one Blender process at a time (~2 min total)."""
import os, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLENDER = os.environ.get("BLENDER", r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
RAW = os.path.join(ROOT, "art", "_raw")
PY = sys.executable
BL = os.path.join(ROOT, "art", "blender")


def run(*a):
    t = time.time(); subprocess.check_call(list(a)); print(f"  -> {time.time() - t:.0f}s")


for script in ("buildings_c.py", "props_b.py"):
    for truth in ([], ["truth"]):
        run(BLENDER, "-b", "--python", os.path.join(BL, script), "--", RAW, *truth)
run(PY, os.path.join(ROOT, "art", "pack_world2.py"), RAW)
run(PY, os.path.join(ROOT, "art", "make_preview_world2.py"))
