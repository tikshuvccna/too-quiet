"""Rebuild every sprite asset: python art/build_all.py   (needs Blender 5.2 + Pillow)"""
import os, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLENDER = os.environ.get("BLENDER", r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
RAW = os.path.join(ROOT, "art", "_raw")
PY = sys.executable
def run(*a):
    t = time.time(); subprocess.check_call(list(a)); print(f"  -> {time.time() - t:.0f}s")
run(BLENDER, "-b", "--python", os.path.join(ROOT, "art", "blender", "characters.py"), "--", "all", RAW)
run(PY, os.path.join(ROOT, "art", "pack.py"), "characters", RAW)
run(BLENDER, "-b", "--python", os.path.join(ROOT, "art", "blender", "props.py"), "--", RAW)
run(PY, os.path.join(ROOT, "art", "pack.py"), "props", RAW)
run(PY, os.path.join(ROOT, "art", "make_preview.py"))
