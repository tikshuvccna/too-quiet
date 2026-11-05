"""Pack the wc_ world creatures (raw renders from blender/wc_creatures.py) into atlases.

python art/pack_wc.py <ABSOLUTE rawdir>      # reads <rawdir>/creatures/wc_*/

Same layout and JSON structure as pack_v2.pack_creatures (small: 768x1024, 128 px cells, idle 4 + walk 6 in S SE E N;
legendary: one facing, idle_0..3). Hebrew name/concept/legend come from content/he/world/creatures_world.json.
Writes public/assets/creatures/wc_<key>.png|json, wc_codex.png|json (separate codex atlas, the original codex.png is
left untouched) and ADDS wc_ entries to creatures/index.json (other entries are never changed). Also art/wc_keys.txt.
"""
import json
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pack_v2 import finish, save_png, frame_rec, CDIRS, OUT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content", "he", "world", "creatures_world.json")


def main(rawdir):
    base = os.path.join(rawdir, "creatures")
    od = os.path.join(OUT, "creatures")
    world = json.load(open(CONTENT, encoding="utf8"))["creatures"]
    names = sorted(n for n in os.listdir(base) if n.startswith("wc_") and os.path.isdir(os.path.join(base, n)))
    entries, codex = {}, []
    for nm in names:
        d = os.path.join(base, nm)
        meta = json.load(open(os.path.join(d, "meta.json"), encoding="utf8"))
        src = world[nm[3:]]
        legendary = bool(src.get("legendary", False))
        frames, anims = {}, {}
        if not legendary:
            cell = 128
            sheet = Image.new("RGBA", (6 * cell, 8 * cell), (0, 0, 0, 0))
            r = 0
            for anim, n in (("idle", 4), ("walk", 6)):
                for dn in CDIRS:
                    for i in range(n):
                        sheet.alpha_composite(finish(os.path.join(d, f"{anim}_{dn}_{i}.png")), (i * cell, r * cell))
                        frames[f"{anim}_{dn}_{i}"] = frame_rec(i * cell, r * cell, cell, cell)
                    anims[f"{anim}_{dn}"] = {"frames": [f"{anim}_{dn}_{i}" for i in range(n)],
                                             "frameRate": 5 if anim == "idle" else 9, "repeat": -1}
                    r += 1
            info = {"cell": [cell, cell], "origin": {"x": 0.5, "y": 110 / 128}, "world_scale": 0.667,
                    "directions": CDIRS, "mirror": {"W": "E flipX", "SW": "SE flipX", "NE": "E or N", "NW": "W or N"},
                    "note": "Rendered at 1.5x world scale for readability: setScale(0.667) for exact world size. "
                            "Ground contact (64,110); flyers hover above it (draw the blob shadow at the origin)."}
        else:
            s0 = Image.open(os.path.join(d, "idle_S_0.png"))
            cw, ch = s0.width // 3, s0.height // 3
            sheet = Image.new("RGBA", (4 * cw, ch), (0, 0, 0, 0))
            for i in range(4):
                sheet.alpha_composite(finish(os.path.join(d, f"idle_S_{i}.png"), ssaa=3, outline_px=1.2), (i * cw, 0))
                frames[f"idle_{i}"] = frame_rec(i * cw, 0, cw, ch)
            anims["idle"] = {"frames": [f"idle_{i}" for i in range(4)], "frameRate": 3, "repeat": -1, "yoyo": True}
            anc = meta.get("anchor", [cw / 2, ch - 20])
            info = {"cell": [cw, ch], "origin": {"x": anc[0] / cw, "y": anc[1] / ch}, "world_scale": 1.0,
                    "note": "Legendary: one facing, idle only (yoyo). origin = ground point under it."}
        sz = save_png(sheet, os.path.join(od, nm + ".png"), colors=None if legendary else 192, max_kb=200)
        out = {"frames": frames, "anims": anims,
               "meta": dict(info, app="too-quiet art pipeline v2 (wc)", image=nm + ".png", size={"w": sheet.width, "h": sheet.height},
                            scale="1", name_he=src.get("name_he"), concept_he=src.get("concept_he"),
                            legend_he=src.get("legend_he"), movement=meta.get("move"), legendary=legendary,
                            codex={"atlas": "wc_codex.png", "frame": nm})}
        with open(os.path.join(od, nm + ".json"), "w", encoding="utf8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        codex.append((nm, finish(os.path.join(d, f"{nm}_codex.png"), ssaa=2, outline_px=1.0)))
        entries[nm] = {"name_he": src.get("name_he"), "concept_he": src.get("concept_he"), "legend_he": src.get("legend_he"),
                       "legendary": legendary, "kb": round(sz / 1024)}
        print(f"creature {nm}: {sz / 1024:.0f} KB")
    # separate codex atlas for the wc_ creatures
    cols = 4
    rows = (len(codex) + cols - 1) // cols
    cs = Image.new("RGBA", (cols * 256, rows * 256), (0, 0, 0, 0))
    cf = {}
    for k, (nm, im) in enumerate(codex):
        x, y = (k % cols) * 256, (k // cols) * 256
        cs.alpha_composite(im, (x, y))
        cf[nm] = frame_rec(x, y, 256, 256)
    sz = save_png(cs, os.path.join(od, "wc_codex.png"))
    with open(os.path.join(od, "wc_codex.json"), "w") as f:
        json.dump({"frames": cf, "meta": {"image": "wc_codex.png", "size": {"w": cs.width, "h": cs.height}, "scale": "1",
                                          "note": "256x256 3/4 collection-card renders of the wc_ creatures, transparent"}}, f, indent=1)
    print(f"wc_codex: {sz / 1024:.0f} KB")
    # add (never change) entries in index.json
    ip = os.path.join(od, "index.json")
    index = json.load(open(ip, encoding="utf8"))
    for nm, e in entries.items():
        if nm.startswith("wc_"):
            index[nm] = e
    with open(ip, "w", encoding="utf8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    small = [n for n, e in entries.items() if not e["legendary"]]
    legend = [n for n, e in entries.items() if e["legendary"]]
    with open(os.path.join(ROOT, "art", "wc_keys.txt"), "w", encoding="utf8") as f:
        f.write("SMALL:\n" + "\n".join(small) + "\n\nLEGENDARY:\n" + "\n".join(legend) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
