"""Rebuild every sprite asset: python art/build_all.py   (needs Blender 5.2 + Pillow)"""
import os, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLENDER = os.environ.get("BLENDER", r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
RAW = os.path.join(ROOT, "art", "_raw")
PY = sys.executable
def run(*a):
    t = time.time(); subprocess.check_call(list(a)); print(f"  -> {time.time() - t:.0f}s")
ONLY_ENV = "--env-only" in sys.argv
if not ONLY_ENV:
  run(BLENDER, "-b", "--python", os.path.join(ROOT, "art", "blender", "characters.py"), "--", "all", RAW)
  run(PY, os.path.join(ROOT, "art", "pack.py"), "characters", RAW)
  run(BLENDER, "-b", "--python", os.path.join(ROOT, "art", "blender", "props.py"), "--", RAW)
  run(PY, os.path.join(ROOT, "art", "pack.py"), "props", RAW)
  run(PY, os.path.join(ROOT, "art", "make_preview.py"))

# ---- environment art (buildings, interiors, FX): facade + truth variants. Does NOT re-render characters/props.
if "--env" in sys.argv or ONLY_ENV or os.environ.get("ENV_ART") == "1":
    INT = os.path.join(ROOT, "art", "blender", "interiors.py")
    for truth in ([], ["truth"]):
        run(BLENDER, "-b", "--python", os.path.join(ROOT, "art", "blender", "buildings.py"), "--", RAW, *truth)
        run(BLENDER, "-b", "--python", INT, "--", RAW, "all", *truth)
    run(PY, os.path.join(ROOT, "art", "pack_env.py"), "buildings", RAW)
    run(PY, os.path.join(ROOT, "art", "pack_env.py"), "interiors", RAW)
    run(PY, os.path.join(ROOT, "art", "pack_env.py"), "fx", RAW)
    run(PY, os.path.join(ROOT, "art", "make_preview_env.py"))
