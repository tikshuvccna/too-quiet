"""Pack the world-2 interiors (15 houses) into public/assets/interiors/<house_id>/ in the same format as the first three.

python art/pack_interiors_w2.py <ABS rawdir> [house ...]
Reads <rawdir>/env/int2/<house>/{shell,shell_truth,<obj>,<obj>_truth}.png + meta.json; layout data from art/blender/iw2_layout.py;
Hebrew names from content/he/world/houses_world.json. Never touches the existing three houses.
"""
import json
import math
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "blender"))
from pack_env import finish, trim, shelf_pack, frame_json, save, contact_shadows, proj, SHELL_SIZE, S_ANCHOR, PPU, E, OUT, ROOT  # noqa
import iw2_layout as L  # noqa


def main(raw, houses):
    hw = json.load(open(os.path.join(ROOT, "content", "he", "world", "houses_world.json"), encoding="utf-8"))["houses"]
    byid = {h["id"]: h for h in hw}
    total = 0
    for house in houses:
        place = L.PLACE[house]
        h = byid[house]
        he = {o["id"]: o["name"] for o in h["objects"]}
        inter = {k for k in place if not k.startswith("x_")}
        assert inter == set(he), (house, inter ^ set(he))
        hdir = os.path.join(raw, "env", "int2", house)
        odir = os.path.join(OUT, "interiors", house)
        meta = json.load(open(os.path.join(hdir, "meta.json")))
        layout = {"house": house, "name": h["name"], "shellSize": list(SHELL_SIZE), "worldOriginPx": list(S_ANCHOR),
                  "note": ("Assemble: draw shell.png at (0,0); for each object draw frame from objects.png at place with setOrigin(anchor). "
                           "depth = world y (smaller y is closer to the camera): sort objects by place.y pixel. 'truth' atlas/shell have identical frames, anchors and places."),
                  "floorPolygonPx": [[round(v, 1) for v in proj(x, y)] for x, y in ((-7, 4.5), (7, 4.5), (7, -4.5), (-7, -4.5))],
                  "windowCenterPx": [round(v, 1) for v in proj(L.WIN_X[house], 4.5, 2.8)],
                  "objects": []}
        for variant in ("", "_truth"):
            sp = os.path.join(hdir, "shell" + variant + ".png")
            if os.path.exists(sp):
                im = Image.open(sp).convert("RGBA")
                sh = im.convert("RGBa").resize(SHELL_SIZE, Image.LANCZOS).convert("RGBA")
                sh = contact_shadows(sh, list(place.values()))
                total += save(sh, os.path.join(odir, "shell" + variant + ".png"), 256)
            items, info = [], {}
            for nm in place:
                key = nm + variant
                p = os.path.join(hdir, key + ".png")
                if not os.path.exists(p) or key not in meta:
                    print("  missing", house, key)
                    continue
                m = meta[key]
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
            json.dump({"frames": frames, "meta": {"app": "too-quiet art pipeline", "image": "objects" + variant + ".png",
                                                  "size": {"w": sheet.width, "h": sheet.height}, "scale": "1",
                                                  "note": "anchor = ground contact (wall objects: bottom centre on the wall, place.y is raised by the z of the hanging height)"}},
                      open(os.path.join(odir, "objects" + variant + ".json"), "w"), indent=1)
            print(f"{house}/objects{variant}: {len(frames)} frames, {sheet.size}, {sz / 1024:.0f} KB")
        for nm, (x, y, z, fp) in place.items():
            px, py = proj(x, y, z)
            layout["objects"].append({
                "id": nm, "interactive": not nm.startswith("x_"), "nameHe": he.get(nm, ""), "frame": nm, "frameTruth": nm + "_truth",
                "place": {"x": round(px, 1), "y": round(py, 1)}, "world": {"x": x, "y": y, "z": z},
                "wall": fp is None, "sortY": round(py, 1),
                "footprintPx": ([round(fp[0] * PPU), round(fp[1] * PPU * math.sin(E))] if fp else None)})
        json.dump(layout, open(os.path.join(odir, "layout.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"interiors w2 total {total / 1024:.0f} KB")


if __name__ == "__main__":
    raw = sys.argv[1]
    hs = sys.argv[2:] or L.ORDER
    main(raw, hs)
