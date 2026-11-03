"""Rebuild every v2 character/creature asset (needs Blender 5.2 + Pillow).

python art/build_characters_v2.py            # everything (~6-8 min on this machine)
python art/build_characters_v2.py portraits  # one stage: portraits | sprites | npcs | creatures | head | pack
Raw renders go to art/_raw/v2 (git-ignored). Outputs: public/assets/{characters_v2,portraits,creatures}/.
"""
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLENDER = os.environ.get("BLENDER", r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
RAW = os.path.join(ROOT, "art", "_raw", "v2")
BL = os.path.join(ROOT, "art", "blender")
PY = sys.executable
HEROES = "apprentice_girl,apprentice_girl_scarf,apprentice_boy,apprentice_boy_hat,dvora"
NPCS = ("dvora,noam,shoshana,miriam,hillel,miller,asaf,hed,child_girl,shepherd,fisherman,bell_ringer,spool_gatherer,"
        "innkeeper,merchant,bard,warden,messenger,gardener,teacher,lamplighter,potter,elder_cane")


def run(*a):
    t = time.time()
    subprocess.check_call(list(a))
    print(f"  -> {time.time() - t:.0f}s")


def blender(script, *a):
    run(BLENDER, "-b", "--python", os.path.join(BL, script), "--", *a)


STAGES = {
    "portraits": lambda: blender("v2_render.py", "portrait", "all", RAW),
    "sprites": lambda: blender("v2_render.py", "sprite", HEROES, RAW),
    "npcs": lambda: blender("v2_render.py", "npc", NPCS, RAW),
    "creatures": lambda: blender("v2_creatures.py", "all", RAW),
    "head": lambda: blender("v2_head.py", RAW),
    "pack": lambda: [run(PY, os.path.join(ROOT, "art", "pack_v2.py"), k, RAW)
                     for k in ("characters", "npcs", "portraits", "creatures", "head")] +
                    [run(PY, os.path.join(ROOT, "art", "make_preview_v2.py"))],
}

if __name__ == "__main__":
    want = sys.argv[1:] or list(STAGES)
    for s in want:
        print("==", s)
        STAGES[s]()
