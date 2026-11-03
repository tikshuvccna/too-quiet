"""Preview sheet for environment art -> art/preview_env.png (buildings facade row + truth row, assembled rooms, FX)."""
import json, os
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "public", "assets")
GREEN = (96, 120, 84, 255)

def atlas(png, js):
    return Image.open(png).convert("RGBA"), json.load(open(js))["frames"]

def crop(sh, f):
    r = f["frame"]; return sh.crop((r["x"], r["y"], r["x"] + r["w"], r["y"] + r["h"]))

def building_row(variant, order, gap=24):
    sh, fr = atlas(os.path.join(A, "buildings", f"buildings{variant}.png"), os.path.join(A, "buildings", f"buildings{variant}.json"))
    ims = [(n, crop(sh, fr[n + variant]), fr[n + variant]["anchor"]) for n in order if n + variant in fr]
    H = max(int(i.height) for _, i, _ in ims) + 20
    base = H - 14
    W = sum(i.width + gap for _, i, _ in ims) + gap
    row = Image.new("RGBA", (W, H), GREEN if not variant else (58, 66, 84, 255))
    x = gap
    for n, im, an in ims:
        # align ground-contact anchors on one baseline
        y = base - int(an["y"] * im.height)
        row.alpha_composite(im, (x, y))
        x += im.width + gap
        if n == "mill" and "mill_sails" + variant in fr:
            s = crop(sh, fr["mill_sails" + variant])
    return row

def room(house, variant):
    d = os.path.join(A, "interiors", house)
    lay = json.load(open(os.path.join(d, "layout.json")))
    shell = Image.open(os.path.join(d, f"shell{variant}.png")).convert("RGBA")
    sh, fr = atlas(os.path.join(d, f"objects{variant}.png"), os.path.join(d, f"objects{variant}.json"))
    canvas = Image.new("RGBA", shell.size, (40, 40, 52, 255)); canvas.alpha_composite(shell)
    for o in sorted(lay["objects"], key=lambda o: o["sortY"]):
        f = fr.get(o["frame"] + variant)
        if not f: continue
        im = crop(sh, f)
        canvas.alpha_composite(im, (int(o["place"]["x"] - f["anchor"]["x"] * im.width), int(o["place"]["y"] - f["anchor"]["y"] * im.height)))
    return canvas

def fx_strip():
    p = os.path.join(A, "fx", "fx.json")
    if not os.path.exists(p): return None
    sh, fr = atlas(os.path.join(A, "fx", "fx.png"), p)
    sh = sh.crop((0, 0, sh.width, sh.getchannel("A").getbbox()[3] + 8))
    out = []
    for bg in ((26, 28, 48, 255), (214, 222, 236, 255)):
        S = Image.new("RGBA", (sh.width, sh.height), bg); S.alpha_composite(sh); out.append(S)
    return out

if __name__ == "__main__":
    order = ["cottage_shoshana", "clinic", "print_house", "bakery", "mill", "tower"]
    r1, r2 = building_row("", order), building_row("_truth", order)
    rooms = [[room(h, v).resize((512, 320), Image.LANCZOS) for h in ("house_grandma", "house_clinic", "house_print")] for v in ("", "_truth")]
    W = max(r1.width, r2.width, 1536)
    strips = fx_strip() or []
    H = r1.height + r2.height + 2 * 320 + sum(s.height for s in strips)
    out = Image.new("RGBA", (W, H), (30, 30, 40, 255))
    y = 0
    for r in (r1, r2):
        out.alpha_composite(r, (0, y)); y += r.height
    for rr in rooms:
        for i, im in enumerate(rr): out.alpha_composite(im, (i * 512, y))
        y += 320
    for s in strips:
        out.alpha_composite(s, (0, y)); y += s.height
    out.convert("RGB").save(os.path.join(ROOT, "art", "preview_env.png"), optimize=True)
    print(out.size)
