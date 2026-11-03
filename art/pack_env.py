"""Pack environment art: buildings, interiors (shell + object atlas + layout), FX.

python art/pack_env.py buildings <rawdir>
python art/pack_env.py interiors <rawdir>
python art/pack_env.py fx <rawdir>
Raw inputs: <rawdir>/env/*.png (+buildings_meta.json), <rawdir>/env/int/<house>/*.png (+../layout_meta.json), <rawdir>/env/fx/*.png.
"""
import json
import math
import os
import sys

from PIL import Image, ImageChops, ImageFilter, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pack import finish as _finish, ROOT, OUT  # noqa


def finish(path):
    return _finish(path, thr=120)   # outline only solid pixels (soft glow halos get no outline ring)

PPU = 56.0
E = math.radians(35.0)
S_ANCHOR = (512, 430)
SHELL_SIZE = (1024, 640)


def quant(img, colors=256):
    """Palette-quantise keeping alpha (fast octree, no dither: keeps flat toon areas clean)."""
    return img.quantize(colors=colors, method=Image.FASTOCTREE, dither=Image.NONE)


def save(img, path, colors=256):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    q = quant(img, colors) if colors else img
    q.save(path, optimize=True)
    return os.path.getsize(path)


def shelf_pack(items, W=1024):
    """items: [(name, Image, extra)] -> sheet, {name: (x,y)}"""
    items = sorted(items, key=lambda t: -t[1].height)
    x = y = rowh = 0
    pos = {}
    for nm, im, _ in items:
        w, h = im.size
        if x + w + 2 > W:
            x, y, rowh = 0, y + rowh + 2, 0
        pos[nm] = (x, y)
        x += w + 2
        rowh = max(rowh, h)
    H = y + rowh
    H2 = 1
    while H2 < H:
        H2 *= 2
    sheet = Image.new("RGBA", (W, H2), (0, 0, 0, 0))
    for nm, im, _ in items:
        sheet.alpha_composite(im, pos[nm])
    return sheet, pos


def trim(im, pad=1):
    bb = im.getchannel("A").point(lambda v: 255 if v > 6 else 0).getbbox()
    if not bb:
        return im, (0, 0)
    x0, y0, x1, y1 = max(0, bb[0] - pad), max(0, bb[1] - pad), min(im.width, bb[2] + pad), min(im.height, bb[3] + pad)
    return im.crop((x0, y0, x1, y1)), (x0, y0)


def frame_json(name, im, pos, anchor_px, extra=None):
    f = {"frame": {"x": pos[0], "y": pos[1], "w": im.width, "h": im.height}, "rotated": False, "trimmed": False,
         "spriteSourceSize": {"x": 0, "y": 0, "w": im.width, "h": im.height}, "sourceSize": {"w": im.width, "h": im.height},
         "anchor": {"x": round(anchor_px[0] / im.width, 4), "y": round(anchor_px[1] / im.height, 4)}}
    if extra:
        f.update(extra)
    return f


# ---------------------------------------------------------------- buildings
PROP_TRUTH = ["tree_round", "tree_pine", "lamppost"]
BUILD_ORDER = ["cottage_shoshana", "clinic", "print_house", "bakery", "mill", "tower"]
HOUSE_IDS = {"cottage_shoshana": "grandma shoshana's cottage", "clinic": "village clinic", "print_house": "print house",
             "bakery": "bakery", "mill": "mill (body; sails separate)", "tower": "weavers' tower", "mill_sails": "windmill sails (rotate around the centre)",
             "tree_round": "bare tree (same anchor as props tree_round)", "tree_pine": "dead pine (same anchor as props tree_pine)", "lamppost": "dark lamppost (same anchor as props lamppost)"}


def pack_buildings(raw):
    meta = json.load(open(os.path.join(raw, "env", "buildings_meta.json")))
    for variant in ("", "_truth"):
        items = []
        info = {}
        for nm in BUILD_ORDER + ["mill_sails"] + (PROP_TRUTH if variant else []):
            key = nm + variant
            p = os.path.join(raw, "env", key + ".png")
            if not os.path.exists(p) or key not in meta:
                print("  missing", key)
                continue
            im = finish(p)
            m = meta[key]
            if nm == "mill_sails":      # keep the cell centred on the hub: trim symmetrically, never shift the hub
                bb = im.getchannel("A").getbbox()
                r = max(im.width // 2 - bb[0], bb[2] - im.width // 2, im.height // 2 - bb[1], bb[3] - im.height // 2) + 2
                cx, cy = im.width // 2, im.height // 2
                t = im.crop((cx - r, cy - r, cx + r, cy + r))
                off = (cx - r, cy - r)
            else:
                t, off = trim(im)
            ax, ay = m["anchor"][0] - off[0], m["anchor"][1] - off[1]
            ex = {"cellBeforeTrim": m["cell"], "label": HOUSE_IDS[nm]}
            if m.get("smoke"):
                ex["smoke"] = [{"x": round(s[0] - off[0] - ax, 1), "y": round(s[1] - off[1] - ay, 1)} for s in m["smoke"]]
                ex["smokeNote"] = "emitter offsets in px from the anchor (+y down)"
            if m.get("extra", {}).get("hub"):
                h = m["extra"]["hub"]
                ex["hub"] = {"x": round(h[0] - off[0] - ax, 1), "y": round(h[1] - off[1] - ay, 1)}
                ex["hubNote"] = "windmill sail pivot: offset in px from the anchor; place mill_sails with origin (0.5,0.5) there"
            if nm == "mill_sails":
                ax, ay = t.width / 2, t.height / 2
            items.append((key, t, ex))
            info[key] = (t, (ax, ay), ex)
        if not items:
            continue
        sheet, pos = shelf_pack(items, 1024)
        name = "buildings" + variant
        sz = save(sheet, os.path.join(OUT, "buildings", name + ".png"))
        frames = {}
        for k, (t, a, ex) in info.items():
            ex = dict(ex)
            ex["anchorPx"] = {"x": round(a[0], 1), "y": round(a[1], 1)}
            frames[k] = frame_json(k, t, pos[k], a, ex)
        json.dump({"frames": frames, "meta": {"app": "too-quiet art pipeline", "image": name + ".png", "format": "RGBA8888",
                                              "size": {"w": sheet.width, "h": sheet.height}, "scale": "1",
                                              "note": "anchor = footprint centre on the ground (setOrigin(anchor.x, anchor.y)); the front edge is about 0.5*depth*sin(35deg)*56 px below it. truth atlas has identical anchors and silhouettes."}},
                  open(os.path.join(OUT, "buildings", name + ".json"), "w"), indent=1)
        print(f"{name}: {len(frames)} frames, sheet {sheet.size}, {sz / 1024:.0f} KB")


# ---------------------------------------------------------------- interiors
# world placements (x, y, z): y = depth (back wall = 4.5), z = height above floor for wall objects.
# fp = soft contact-shadow footprint (rx, ry) in world units; None for wall objects.
PLACE = {
    "house_grandma": {
        "g_photos": (-3.6, 4.45, 1.9, None), "g_window": (3.0, 4.2, 1.48, None), "g_tablet": (-4.6, 2.6, 0, (0.6, 0.45)),
        "g_scarf": (-2.6, -0.6, 0, (0.8, 0.5)), "g_cookies": (5.4, 1.4, 0, (0.5, 0.35)), "g_cat": (2.4, -1.6, 0, (0.7, 0.45)),
        "x_armchair": (-5.4, 0.4, 0, (0.9, 0.7)), "x_wool_basket": (-3.9, -2.8, 0, (0.55, 0.4)), "x_spinning_wheel": (5.2, -1.6, 0, (0.8, 0.45)),
        "x_floor_lamp": (6.2, 3.4, 0, (0.3, 0.2)), "x_tea_table": (0.2, 3.7, 0, (0.65, 0.45)), "x_plant": (-6.2, 3.6, 0, (0.5, 0.35)),
        "x_bookshelf": (-1.8, 4.1, 0, (1.0, 0.35)), "x_footstool": (-4.0, -0.2, 0, (0.4, 0.3))},
    "house_clinic": {
        "c_cabinet": (-5.8, 4.05, 0, (0.8, 0.4)), "c_notes": (-2.2, 4.45, 1.7, None), "c_clock": (0.2, 4.45, 3.55, None),
        "c_drawer": (-2.0, 4.1, 0, (0.75, 0.4)), "c_password": (1.2, 2.2, 0, (0.6, 0.4)), "c_bed": (4.4, -1.0, 0, (1.3, 0.8)),
        "x_herb_shelf": (5.6, 4.45, 1.9, None), "x_desk": (-3.2, 1.8, 0, (1.0, 0.8)), "x_stool": (3.0, -2.6, 0, (0.35, 0.25)),
        "x_trolley": (6.0, 2.4, 0, (0.6, 0.4)), "x_screen": (-5.4, -1.5, 0, (1.1, 0.4)), "x_planter": (1.0, 4.15, 0, (0.8, 0.3)),
        "x_basin": (-6.2, 2.0, 0, (0.5, 0.35))},
    "house_print": {
        "p_printer": (3.6, 3.0, 0, (1.1, 0.7)), "p_stack": (-0.4, 3.6, 0, (0.8, 0.5)), "p_pc_yoel": (-4.6, 2.8, 0, (0.9, 0.6)),
        "p_pc_rachel": (-1.8, 2.4, 0, (0.9, 0.6)), "p_cal": (1.8, 4.45, 1.9, None), "p_box": (3.2, -2.0, 0, (0.7, 0.5)),
        "x_type_case": (6.1, 1.0, 0, (0.8, 0.5)), "x_paper_cabinet": (6.2, 3.9, 0, (0.7, 0.4)), "x_ink_shelf": (-0.2, 4.25, 0, (0.9, 0.3)),
        "x_bin": (-6.0, 0.4, 0, (0.4, 0.3)), "x_lamp": (-6.3, -2.0, 0, (0.3, 0.2)), "x_stool": (-3.0, 0.6, 0, (0.35, 0.25)),
        "x_newspapers": (2.4, 0.8, 0, (0.6, 0.3))},
}
HOUSE_NAMES = {"house_grandma": "בית סבתא שושנה", "house_clinic": "מרפאת הכפר", "house_print": "בית הדפוס הקטן"}


def proj(x, y, z=0.0, a=S_ANCHOR):
    return (a[0] + x * PPU, a[1] - (z * math.cos(E) + y * math.sin(E)) * PPU)


def contact_shadows(shell, objs):
    """Soft violet blobs on the floor under each floor object (clipped to the shell alpha)."""
    lay = Image.new("RGBA", shell.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for (x, y, z, fp) in objs:
        if not fp:
            continue
        cx, cy = proj(x, y, 0)
        rx, ry = fp[0] * PPU, fp[1] * PPU * math.sin(E) * 1.4
        d.ellipse((cx - rx, cy - ry * 0.6, cx + rx, cy + ry * 1.3), fill=(26, 14, 40, 110))
    lay = lay.filter(ImageFilter.GaussianBlur(7))
    a = ImageChops.multiply(lay.getchannel("A"), shell.getchannel("A"))
    lay.putalpha(a)
    return Image.alpha_composite(shell, lay)


def pack_interiors(raw):
    hj = json.load(open(os.path.join(ROOT, "content", "he", "houses.json"), encoding="utf-8"))
    he = {}
    for h in hj["houses"]:
        for o in h["objects"]:
            he[o["id"]] = o["name"]
    meta = json.load(open(os.path.join(raw, "env", "int", "layout_meta.json")))
    total = 0
    for house, place in PLACE.items():
        hdir = os.path.join(raw, "env", "int", house)
        odir = os.path.join(OUT, "interiors", house)
        layout = {"house": house, "name": HOUSE_NAMES[house], "shellSize": list(SHELL_SIZE), "worldOriginPx": list(S_ANCHOR),
                  "note": ("Assemble: draw shell.png at (0,0); for each object draw frame from objects.png at place with setOrigin(anchor). "
                           "depth = world y (smaller y is closer to the camera): sort objects by place.y pixel. 'truth' atlas/shell have identical frames, anchors and places."),
                  "floorPolygonPx": [[round(v, 1) for v in proj(x, y)] for x, y in ((-7, 4.5), (7, 4.5), (7, -4.5), (-7, -4.5))],
                  "windowCenterPx": [round(v, 1) for v in proj({"house_grandma": 3.0, "house_clinic": 3.2, "house_print": -3.4}[house], 4.5, 2.8)],
                  "objects": []}
        for variant in ("", "_truth"):
            sp = os.path.join(hdir, "shell" + variant + ".png")
            if os.path.exists(sp):
                im = Image.open(sp).convert("RGBA")
                sh = im.convert("RGBa").resize(SHELL_SIZE, Image.LANCZOS).convert("RGBA")
                sh = contact_shadows(sh, list(place.values()))
                total += save(sh, os.path.join(odir, "shell" + variant + ".png"), 256)
            items, info = [], {}
            for nm, (x, y, z, fp) in place.items():
                key = nm + variant
                p = os.path.join(hdir, key + ".png")
                if not os.path.exists(p) or key not in meta.get(house, {}):
                    print("  missing", house, key)
                    continue
                m = meta[house][key]
                im = finish(p)
                t, off = trim(im)
                a = (m["anchor"][0] - off[0], m["anchor"][1] - off[1])
                items.append((key, t, None))
                info[key] = (t, a)
            if not items:
                continue
            sheet, pos = shelf_pack(items, 1024)
            sz = save(sheet, os.path.join(odir, "objects" + variant + ".png"))
            total += sz
            frames = {k: frame_json(k, t, pos[k], a) for k, (t, a) in info.items()}
            json.dump({"frames": frames, "meta": {"app": "too-quiet art pipeline", "image": "objects" + variant + ".png", "size": {"w": sheet.width, "h": sheet.height},
                                                  "scale": "1", "note": "anchor = ground contact (wall objects: bottom centre on the wall; g_window: centre of the sill)"}},
                      open(os.path.join(odir, "objects" + variant + ".json"), "w"), indent=1)
            print(f"{house}/objects{variant}: {len(frames)} frames, {sheet.size}, {sz / 1024:.0f} KB")
        for nm, (x, y, z, fp) in place.items():
            px, py = proj(x, y, z)
            layout["objects"].append({
                "id": nm, "interactive": not nm.startswith("x_"), "nameHe": he.get(nm, ""), "frame": nm, "frameTruth": nm + "_truth",
                "place": {"x": round(px, 1), "y": round(py, 1)}, "world": {"x": x, "y": y, "z": z},
                "wall": fp is None, "sortY": round(py, 1), "footprintPx": ([round(fp[0] * PPU), round(fp[1] * PPU * math.sin(E))] if fp else None)})
        json.dump(layout, open(os.path.join(odir, "layout.json"), "w"), indent=1, ensure_ascii=False)
    print(f"interiors total {total / 1024:.0f} KB")


if __name__ == "__main__":
    what, raw = sys.argv[1], sys.argv[2]
    {"buildings": pack_buildings, "interiors": pack_interiors}.get(what, lambda r: None)(raw)
    if what == "fx":
        import pack_fx
        pack_fx.pack(raw)
