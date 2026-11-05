"""Pack the world-2 atlases (never touches the existing buildings/props atlases).

python art/pack_world2.py <rawdir>
Reads <rawdir>/env2/*.png + buildings2_meta.json and <rawdir>/env2p/*.png + props2_meta.json.
Writes public/assets/buildings/buildings2[a|b][_truth].png|json (+ buildings2_index.json) and public/assets/props/props2[_truth].png|json.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pack_env import finish, trim, shelf_pack, frame_json, save, OUT  # noqa

BUILD = ["inn", "bell_tower", "tailor", "school", "fisher", "workshop", "library", "observatory",
         "stories", "farm", "shepherd", "herbs", "fairy", "guild", "lighthouse", "great_tower"]
PROPS = ["rock_a", "rock_b", "standing_stone", "stone_circle", "reeds", "boat", "dock_segment", "hay_bale", "haystack",
         "fairy_door_tree", "giant_tree_hollow", "market_stall_b", "market_stall_c", "market_stall_d", "fountain",
         "signpost_b", "crate_stack", "barrel", "lantern_post_b", "scarecrow", "flower_bush", "mushroom_ring", "bridge_small"]
PROPS_TRUTH = ["fairy_door_tree", "giant_tree_hollow", "lantern_post_b", "flower_bush", "mushroom_ring", "reeds"]
LABEL = {"inn": "inn with the lantern sign", "bell_tower": "bell tower (open belfry)", "tailor": "tailor shop", "school": "school",
         "fisher": "fisher's shack", "workshop": "workshop", "library": "spool library", "observatory": "observatory",
         "stories": "stories hall", "farm": "farm (barn, house, silo)", "shepherd": "shepherd's wagon + pen", "herbs": "herb glasshouse",
         "fairy": "fairy tree house", "guild": "weavers' guild hall", "lighthouse": "lighthouse", "great_tower": "the great tower (locked)"}


def load(raw, sub, metaname, names, sfx, trimmed=True):
    meta = json.load(open(os.path.join(raw, sub, metaname)))
    out = []
    for nm in names:
        key = nm + sfx
        p = os.path.join(raw, sub, key + ".png")
        if not os.path.exists(p) or key not in meta:
            print("  missing", key)
            continue
        im = finish(p)
        t, off = trim(im)
        m = meta[key]
        ax, ay = m["anchor"][0] - off[0], m["anchor"][1] - off[1]
        ex = {"cellBeforeTrim": m["cell"]}
        if m.get("smoke"):
            ex["smoke"] = [{"x": round(s[0] - off[0] - ax, 1), "y": round(s[1] - off[1] - ay, 1)} for s in m["smoke"]]
            ex["smokeNote"] = "emitter offsets in px from the anchor (+y down)"
        out.append((key, t, (ax, ay), ex, nm))
    return out


def write_atlas(items, outdir, name, note, W=1024):
    sheet, pos = shelf_pack([(k, t, None) for (k, t, a, e, n) in items], W)
    sheet = sheet.crop((0, 0, sheet.width, sheet.getchannel("A").getbbox()[3] + 1))
    sz = save(sheet, os.path.join(OUT, outdir, name + ".png"))
    frames = {}
    for (k, t, a, e, n) in items:
        ex = dict(e)
        ex["anchorPx"] = {"x": round(a[0], 1), "y": round(a[1], 1)}
        frames[k] = frame_json(k, t, pos[k], a, ex)
    json.dump({"frames": frames, "meta": {"app": "too-quiet art pipeline", "image": name + ".png", "format": "RGBA8888",
                                          "size": {"w": sheet.width, "h": sheet.height}, "scale": "1", "note": note}},
              open(os.path.join(OUT, outdir, name + ".json"), "w"), indent=1)
    print(f"{outdir}/{name}: {len(frames)} frames, {sheet.size}, {sz / 1024:.0f} KB")
    return sheet.size, frames


def main(raw):
    bnote = ("anchor = footprint centre on the ground (setOrigin(anchor.x, anchor.y)); same convention as buildings.json. "
             "The truth atlas has identical silhouettes/anchors; frame name = <id>_truth.")
    # decide the page split from the facade variant (same split for truth)
    fac = load(raw, "env2", "buildings2_meta.json", BUILD, "")
    area = sum(t.width * t.height for (_, t, _, _, _) in fac)
    pages = [BUILD]
    sheet, _pos = shelf_pack([(k, t, None) for (k, t, a, e, n) in fac], 2048)
    if sheet.getchannel("A").getbbox()[3] + 1 > 2048:
        half = len(BUILD) // 2
        pages = [BUILD[:half], BUILD[half:]]
    index = {}
    for pi, names in enumerate(pages):
        suffix = "" if len(pages) == 1 else "ab"[pi]
        for variant in ("", "_truth"):
            items = load(raw, "env2", "buildings2_meta.json", names, variant)
            for it in items:
                it[3]["label"] = LABEL[it[4]]
            nm = "buildings2" + suffix + variant
            write_atlas(items, "buildings", nm, bnote, 2048)
            if not variant:
                for it in items:
                    index[it[4]] = {"atlas": "buildings2" + suffix, "atlasTruth": "buildings2" + suffix + "_truth", "frame": it[0], "frameTruth": it[0] + "_truth"}
    json.dump(index, open(os.path.join(OUT, "buildings", "buildings2_index.json"), "w"), indent=1)
    # props
    pnote = "anchor = ground contact point (normalised), like props.json: setOrigin(anchor.x, anchor.y). Truth frames exist for trees/lamp/plants only (<id>_truth)."
    write_atlas(load(raw, "env2p", "props2_meta.json", PROPS, ""), "props", "props2", pnote, 1024)
    write_atlas(load(raw, "env2p", "props2_meta.json", PROPS_TRUTH, "_truth"), "props", "props2_truth", pnote, 512)


if __name__ == "__main__":
    main(sys.argv[1])
