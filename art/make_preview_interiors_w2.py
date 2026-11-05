"""Contact sheet for the world-2 interiors.

python art/make_preview_interiors_w2.py            # -> art/preview_interiors_w2.png (all houses: facade room | truth room at 0.5, then objects at true scale)
python art/make_preview_interiors_w2.py view inn bell_tower   # -> art/_raw/pv_<house>.png (rooms + atlases at 0.75, for eyeballing)
"""
import json
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "public", "assets", "interiors")
sys.path.insert(0, os.path.join(ROOT, "art", "blender"))
from iw2_layout import ORDER  # noqa


def crop(sh, f):
    r = f["frame"]
    return sh.crop((r["x"], r["y"], r["x"] + r["w"], r["y"] + r["h"]))


def room(house, variant):
    d = os.path.join(A, house)
    lay = json.load(open(os.path.join(d, "layout.json"), encoding="utf-8"))
    shell = Image.open(os.path.join(d, f"shell{variant}.png")).convert("RGBA")
    sh = Image.open(os.path.join(d, f"objects{variant}.png")).convert("RGBA")
    fr = json.load(open(os.path.join(d, f"objects{variant}.json")))["frames"]
    canvas = Image.new("RGBA", shell.size, (40, 40, 52, 255))
    canvas.alpha_composite(shell)
    for o in sorted(lay["objects"], key=lambda o: o["sortY"]):
        f = fr.get(o["frame"] + variant)
        if not f:
            continue
        im = crop(sh, f)
        canvas.alpha_composite(im, (int(o["place"]["x"] - f["anchor"]["x"] * im.width), int(o["place"]["y"] - f["anchor"]["y"] * im.height)))
    return canvas


def atlas(house, variant):
    d = os.path.join(A, house)
    im = Image.open(os.path.join(d, f"objects{variant}.png")).convert("RGBA")
    bb = im.getchannel("A").getbbox()
    im = im.crop((0, 0, im.width, bb[3] + 4)) if bb else im
    bg = Image.new("RGBA", im.size, (92, 96, 112, 255))
    bg.alpha_composite(im)
    return bg


def panel(house, s_room, s_atlas):
    r1, r2 = room(house, ""), room(house, "_truth")
    a1, a2 = atlas(house, ""), atlas(house, "_truth")
    rs = (int(1024 * s_room), int(640 * s_room))
    r1, r2 = r1.resize(rs, Image.LANCZOS), r2.resize(rs, Image.LANCZOS)
    if s_atlas != 1:
        a1 = a1.resize((int(a1.width * s_atlas), int(a1.height * s_atlas)), Image.LANCZOS)
        a2 = a2.resize((int(a2.width * s_atlas), int(a2.height * s_atlas)), Image.LANCZOS)
    W = max(r1.width * 2, a1.width + a2.width)
    H = rs[1] + max(a1.height, a2.height) + 22
    out = Image.new("RGBA", (W, H), (28, 28, 38, 255))
    out.alpha_composite(r1, (0, 0))
    out.alpha_composite(r2, (rs[0], 0))
    out.alpha_composite(a1, (0, rs[1] + 22))
    out.alpha_composite(a2, (a1.width, rs[1] + 22))
    ImageDraw.Draw(out).text((8, 6), house, fill=(255, 255, 255, 255))
    return out


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "view":
        for h in sys.argv[2:]:
            p = panel(h, 0.75, 0.75)
            p.convert("RGB").save(os.path.join(ROOT, "art", "_raw", f"pv_{h}.png"))
            print(h, p.size)
    else:
        hs = [h for h in ORDER if os.path.exists(os.path.join(A, h, "layout.json"))]
        ps = [panel(h, 0.5, 1.0) for h in hs]
        W = max(p.width for p in ps)
        H = sum(p.height for p in ps)
        out = Image.new("RGB", (W, H), (28, 28, 38))
        y = 0
        for p in ps:
            out.paste(p.convert("RGB"), (0, y))
            y += p.height
        out.save(os.path.join(ROOT, "art", "preview_interiors_w2.png"), optimize=True)
        print(out.size, len(ps), "houses")
