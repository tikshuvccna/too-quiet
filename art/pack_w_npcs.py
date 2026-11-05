"""Pack the world-NPC raw renders into sheets identical in layout to pack_v2.pack_npcs.

python art/pack_w_npcs.py <ABS rawdir> [key,key...]
Reads <rawdir>/npcs/w_*/idle_<DIR>_<i>.png, writes public/assets/characters_v2/npcs/w_<name>.png|json,
ADDS the keys to npcs/index.json (existing entries kept) and writes art/w_npc_keys.txt.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image

from pack_v2 import finish, save_png, frame_rec, OUT, NPC_DIRS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "art", "blender"))
from w_npc_specs import ORDER  # noqa: E402  (plain data module, no bpy)


def pack(rawdir, names):
    cell = 128
    od = os.path.join(OUT, "characters_v2", "npcs")
    idx_path = os.path.join(od, "index.json")
    with open(idx_path, encoding="utf8") as f:
        index = json.load(f)
    for name in names:
        d = os.path.join(rawdir, "npcs", name)
        sheet = Image.new("RGBA", (4 * cell, 5 * cell), (0, 0, 0, 0))
        frames, anims = {}, {}
        for r, dn in enumerate(NPC_DIRS):
            for i in range(4):
                fp = os.path.join(d, f"idle_{dn}_{i}.png")
                if not os.path.exists(fp):
                    raise SystemExit(f"missing {fp}")
                sheet.alpha_composite(finish(fp), (i * cell, r * cell))
                frames[f"idle_{dn}_{i}"] = frame_rec(i * cell, r * cell, cell, cell)
            anims[f"idle_{dn}"] = {"frames": [f"idle_{dn}_{i}" for i in range(4)], "frameRate": 5, "repeat": -1}
        sz = save_png(sheet, os.path.join(od, name + ".png"), colors=128, max_kb=120)
        meta = {"frames": frames, "anims": anims,
                "meta": {"app": "too-quiet art pipeline v2", "image": name + ".png", "size": {"w": sheet.width, "h": sheet.height},
                         "scale": "1", "origin": {"x": 0.5, "y": 110 / 128},
                         "mirror": {"NE": "SE flipX", "NW": "SW flipX", "N": "use S/SE"},
                         "note": "Idle only, frame 3 = blink. Rows: S, SE, E, SW, W. Ground contact (64,110)."}}
        with open(os.path.join(od, name + ".json"), "w") as f:
            json.dump(meta, f, indent=1)
        index[name] = {"image": name + ".png", "json": name + ".json", "kb": round(sz / 1024)}
        print(f"npc {name}: {sz / 1024:.0f} KB")
    with open(idx_path, "w") as f:
        json.dump(dict(sorted(index.items())), f, indent=1)
    with open(os.path.join(ROOT, "art", "w_npc_keys.txt"), "w") as f:
        f.write("\n".join(ORDER) + "\n")


if __name__ == "__main__":
    raw = sys.argv[1]
    names = sys.argv[2].split(",") if len(sys.argv) > 2 else ORDER
    pack(raw, names)
