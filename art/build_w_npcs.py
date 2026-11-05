"""Rebuild the 23 world-NPC sheets (needs Blender 5.2 + Pillow). About 2.5 min on this machine.

python art/build_w_npcs.py                    # render all -> pack -> preview
python art/build_w_npcs.py w_tailor,w_dyer    # only these keys (pack/preview still cover all rendered keys)
Raw frames: art/_raw/v2w (git-ignored). Outputs: public/assets/characters_v2/npcs/w_*.png|json (+ keys added to
index.json), art/w_npc_keys.txt, art/preview_w_npcs.png. Specs: art/blender/w_npc_specs.py; parts: art/blender/w_npcs.py.
"""
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLENDER = os.environ.get("BLENDER", r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
RAW = os.path.join(ROOT, "art", "_raw", "v2w")
PY = sys.executable


def run(*a):
    t = time.time()
    subprocess.check_call(list(a))
    print(f"  -> {time.time() - t:.0f}s")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    os.makedirs(RAW, exist_ok=True)
    run(BLENDER, "-b", "--python", os.path.join(ROOT, "art", "blender", "w_npcs.py"), "--", which, RAW)
    run(PY, os.path.join(ROOT, "art", "pack_w_npcs.py"), RAW)
    run(PY, os.path.join(ROOT, "art", "make_preview_w_npcs.py"))
