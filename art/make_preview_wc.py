"""Contact sheet for the wc_ creatures -> art/preview_wc_creatures.png
Rows: per small creature idle S SE E N + walk E2 (true sprite cell), SE at 2x, S at exact world scale (0.667);
a world-scale line-up next to some existing creatures; legendaries (idle 0 and 2); codex cards."""
import json
import os

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CD = os.path.join(ROOT, "public", "assets", "creatures")
BG = (96, 120, 84, 255)
BG2 = (110, 112, 128, 255)
W = 2048


def load(n):
    return Image.open(os.path.join(CD, n + ".png")).convert("RGBA"), json.load(open(os.path.join(CD, n + ".json"), encoding="utf8"))


def crop(sh, js, fn):
    f = js["frames"][fn]["frame"]
    return sh.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))


idx = json.load(open(os.path.join(CD, "index.json"), encoding="utf8"))
small = [n for n, v in idx.items() if n.startswith("wc_") and not v["legendary"]]
legend = [n for n, v in idx.items() if n.startswith("wc_") and v["legendary"]]
blocks = []
per = 2
rowh = 256
crow = Image.new("RGBA", (W, rowh * ((len(small) + per - 1) // per)), BG)
for k, n in enumerate(small):
    sh, js = load(n)
    x0, y0 = (k % per) * 1024, (k // per) * rowh
    for j, d in enumerate(["S", "SE", "E", "N"]):
        crow.alpha_composite(crop(sh, js, f"idle_{d}_0"), (x0 + j * 112, y0))
    crow.alpha_composite(crop(sh, js, "walk_E_2"), (x0 + 4 * 112, y0))
    crow.alpha_composite(crop(sh, js, "idle_S_2"), (x0 + 5 * 112, y0))
    crow.alpha_composite(crop(sh, js, "idle_SE_0").resize((256, 256), Image.LANCZOS), (x0 + 690, y0))
    crow.alpha_composite(crop(sh, js, "idle_S_0").resize((85, 85), Image.LANCZOS), (x0 + 20, y0 + 150))
    crow.alpha_composite(crop(sh, js, "walk_SE_3").resize((85, 85), Image.LANCZOS), (x0 + 120, y0 + 150))
    ImageDraw.Draw(crow).text((x0 + 230, y0 + 200), n, fill=(255, 250, 230, 255))
blocks.append(("wc_ creatures: idle S SE E N, walk E2, idle S2 | SE at 2x | below: S idle and SE walk at world scale (0.667)", BG, [crow]))
# world-scale line-up with existing creatures
old = ["paper_crane", "trail_fox", "librarian_owl", "spool_hedgehog", "gargar_cat", "lantern_moth", "echo_parrot"]
lu = Image.new("RGBA", (W, 100), BG)
x = 0
for n in old + small:
    if not os.path.exists(os.path.join(CD, n + ".png")):
        continue
    sh, js = load(n)
    lu.alpha_composite(crop(sh, js, "idle_SE_0").resize((85, 85), Image.LANCZOS), (x, 8))
    x += 78
blocks.append(("World-scale line-up: 7 existing (crane fox owl hedgehog cat moth parrot) then the 12 new ones", BG, [lu]))
lrow = Image.new("RGBA", (W, 384), BG2)
x = 0
for n in legend + ["thread_serpent"]:
    sh, js = load(n)
    for i in range(2):
        im = crop(sh, js, f"idle_{i * 2}")
        lrow.alpha_composite(im, (x, 384 - im.height))
        x += im.width
blocks.append(("Legendaries (idle 0 and 2): " + ", ".join(legend) + " + existing thread_serpent for scale", BG2, [lrow]))
cx = Image.open(os.path.join(CD, "wc_codex.png")).convert("RGBA")
crow2 = Image.new("RGBA", (W, cx.height // 2), BG2)
crow2.alpha_composite(cx.resize((cx.width // 2, cx.height // 2), Image.LANCZOS), (0, 0))
blocks.append(("wc_codex cards (256 px each, shown at half size)", BG2, [crow2]))

H = sum(22 + sum(im.height for im in ims) for _, _, ims in blocks)
out = Image.new("RGBA", (W, H), (60, 60, 70, 255))
y = 0
for title, bg, ims in blocks:
    ImageDraw.Draw(out).text((8, y + 4), title, fill=(255, 250, 230, 255))
    y += 22
    for im in ims:
        bgim = Image.new("RGBA", (W, im.height), bg)
        bgim.alpha_composite(im.crop((0, 0, min(W, im.width), im.height)), (0, 0))
        out.alpha_composite(bgim, (0, y))
        y += im.height
out.convert("RGB").save(os.path.join(ROOT, "art", "preview_wc_creatures.png"), optimize=True)
print("preview", out.size)
