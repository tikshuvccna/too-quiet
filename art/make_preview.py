"""Contact sheet: all characters (8 directions, walk frame 2) + idle S, and all props. -> art/preview.png"""
import json, os
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "public", "assets")
DIRS = ["S", "SW", "W", "NW", "N", "NE", "E", "SE"]
BG = (96, 120, 84, 255)
K = 1.5
rows = []
for n in ("apprentice_girl", "apprentice_boy", "dvora"):
    sh = Image.open(os.path.join(A, "characters", n + ".png")).convert("RGBA")
    js = json.load(open(os.path.join(A, "characters", n + ".json")))["frames"]
    row = Image.new("RGBA", (128 * 8, 128), BG)
    for i, d in enumerate(DIRS):
        f = js[f"walk_{d}_2"]["frame"]
        row.alpha_composite(sh.crop((f["x"], f["y"], f["x"] + 128, f["y"] + 128)), (i * 128, 0))
    row = row.resize((int(row.width * K), int(row.height * K)), Image.LANCZOS)
    rows.append(row)
ps = Image.open(os.path.join(A, "props", "props.png")).convert("RGBA")
pj = json.load(open(os.path.join(A, "props", "props.json")))["frames"]
W = max(r.width for r in rows)
pr = Image.new("RGBA", (W, 300), BG)
x = 0
y_ground = 285
tall = ["cottage_a", "cottage_b", "cottage_c"]
order = tall + ["tree_round", "tree_pine", "well", "market_stall", "lamppost", "signpost", "fence"]
for nm in order:
    f = pj[nm]["frame"]; im = ps.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))
    s = 1.0 if nm in tall else 1.0
    if x + im.width > W:
        break
    ay = int(pj[nm]["anchor"]["y"] * im.height)
    pr.alpha_composite(im, (x, max(0, y_ground - ay - 0 if False else min(300 - im.height, 300 - im.height))))
    x += int(im.width * 0.74)
H = sum(r.height for r in rows) + pr.height
out = Image.new("RGBA", (W, H), BG)
y = 0
for r in rows + [pr]:
    out.alpha_composite(r, (0, y)); y += r.height
out.convert("RGB").save(os.path.join(ROOT, "art", "preview.png"), optimize=True)
print("preview", out.size)
