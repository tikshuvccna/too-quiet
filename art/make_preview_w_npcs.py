"""Contact sheet for the 23 world NPCs -> art/preview_w_npcs.png
Top: every NPC in S SE E SW W (true scale, frame 0) + blink. Bottom: S and SE at 2x.
python art/make_preview_w_npcs.py [rawdir quick]   # 'quick' previews raw frame-0 renders before packing
"""
import json
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "art", "blender"))
sys.path.insert(0, os.path.join(ROOT, "art"))
from w_npc_specs import ORDER  # noqa: E402

ND = os.path.join(ROOT, "public", "assets", "characters_v2", "npcs")
BG = (96, 120, 84, 255)
DIRS = ["S", "SE", "E", "SW", "W"]


def frame(name, fn, raw=None):
    if raw:
        from pack_v2 import finish
        return finish(os.path.join(raw, "npcs", name, fn + ".png"))
    sh = Image.open(os.path.join(ND, name + ".png")).convert("RGBA")
    js = json.load(open(os.path.join(ND, name + ".json")))
    f = js["frames"][fn]["frame"]
    return sh.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))


def main(raw=None):
    names = [n for n in ORDER if raw or os.path.exists(os.path.join(ND, n + ".png"))]
    cols = 3
    cw = 128 * (5 if raw else 6) + 24
    rows = (len(names) + cols - 1) // cols
    top = Image.new("RGBA", (cw * cols, rows * 146), BG)
    d = ImageDraw.Draw(top)
    for k, n in enumerate(names):
        x0, y0 = (k % cols) * cw, (k // cols) * 146
        for j, dn in enumerate(DIRS):
            top.alpha_composite(frame(n, f"idle_{dn}_0", raw), (x0 + j * 128, y0 + 14))
        if not raw:
            top.alpha_composite(frame(n, "idle_S_3"), (x0 + 5 * 128, y0 + 14))
        d.text((x0 + 4, y0 + 2), n, fill=(255, 250, 230, 255))
    per = 8
    brows = (len(names) + per - 1) // per
    big = Image.new("RGBA", (per * 256, brows * 2 * 220), BG)
    db = ImageDraw.Draw(big)
    for k, n in enumerate(names):
        x0, y0 = (k % per) * 256, (k // per) * 440
        for j, dn in enumerate(("S", "SE")):
            im = frame(n, f"idle_{dn}_0", raw).crop((0, 8, 128, 118)).resize((220, 220), Image.LANCZOS)
            big.alpha_composite(im, (x0 + 18, y0 + j * 220))
        db.text((x0 + 4, y0 + 2), n, fill=(255, 250, 230, 255))
    W = max(top.width, big.width)
    out = Image.new("RGBA", (W, top.height + big.height), BG)
    out.alpha_composite(top, (0, 0))
    out.alpha_composite(big, (0, top.height))
    path = os.path.join(ROOT, "art", "preview_w_npcs_quick.png" if raw else "preview_w_npcs.png")
    out.convert("RGB").save(path, optimize=True)
    print("preview", path, out.size)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 2 and sys.argv[2] == "quick" else None)
