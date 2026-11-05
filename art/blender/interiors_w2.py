"""Render the 15 world-2 interiors (shell + object sprites, facade and truth).

blender -b --python interiors_w2.py -- <ABS rawdir> <house[,house]|all> [facade] [truth] [shell] [objects] [only=id,id]
Output: <rawdir>/env/int2/<house>/shell[_truth].png, <obj>[_truth].png, meta.json  (cell+anchor of each object render).
One Blender process renders every requested house in both variants (facade then truth) unless facade/truth is given.
"""
import importlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iw2_lib import *  # noqa
import interiors as I
import iw2_layout as L
import iw2_rooms as RM

CELL = (512, 480)
ANCHOR = (256, 380)


def load_objs():
    objs = {}
    for mod in ("iw2_objs_a", "iw2_objs_b", "iw2_objs_c"):
        try:
            m = importlib.import_module(mod)
        except ModuleNotFoundError as e:
            if e.name != mod:
                raise
            continue
        objs.update(m.OBJ)
    return objs


def setup(cfg, truth):
    reset_env()
    EL.set_truth(truth)
    kc, ke = cfg["key"]
    EL.env_lights(key_col=kc, key_e=ke, rim_col="#9fb8ff", rim_e=1.2, world=cfg["world"], world_e=0.7, key_dir=(-0.6, -1.0, 1.1))


def render_shell(house, outdir, truth):
    cfg = RM.CFGS[house]()
    setup(cfg, truth)
    I.build_room(cfg, truth)
    # the hills seen through the window must not poke out of the room when the window is far from the centre
    for o in bpy.data.objects:
        if o.name.startswith("hill"):
            o.scale.x = 0.5
    render_scene(I.SHELL, I.S_ANCHOR, os.path.join(outdir, "shell" + ("_truth" if truth else "") + ".png"), samples=24)


def render_object(house, name, fn, outdir, truth):
    cfg = RM.CFGS[house]()
    setup(cfg, truth)
    R = pivot("obj")
    extra = fn(R) or {}
    cell = extra.get("cell", CELL)
    anchor = extra.get("anchor", ANCHOR)
    render_scene(cell, anchor, os.path.join(outdir, name + ("_truth" if truth else "") + ".png"), samples=24)
    return {"cell": list(cell), "anchor": list(anchor)}


def main():
    a = script_args()
    rawdir = a[0]
    which = a[1]
    flags = a[2:]
    variants = [v == "truth" for v in (["facade", "truth"] if not ({"facade", "truth"} & set(flags)) else [f for f in flags if f in ("facade", "truth")])]
    only_part = [f for f in flags if f in ("shell", "objects")]
    only_ids = []
    for f in flags:
        if f.startswith("only="):
            only_ids = f[5:].split(",")
    houses = L.ORDER if which == "all" else which.split(",")
    OBJS = load_objs()
    for h in houses:
        out = os.path.join(rawdir, "env", "int2", h)
        os.makedirs(out, exist_ok=True)
        mpath = os.path.join(out, "meta.json")
        meta = json.load(open(mpath)) if os.path.exists(mpath) else {}
        ids = list(L.PLACE[h])
        missing = [i for i in ids if i not in OBJS.get(h, {})]
        if missing and (not only_part or "objects" in only_part):
            print("WARN missing builders", h, missing)
        for truth in variants:
            t0 = time.time()
            if not only_part or "shell" in only_part:
                if not only_ids:
                    render_shell(h, out, truth)
                    print(f"SHELL {h} truth={truth}: {time.time() - t0:.1f}s", flush=True)
            if not only_part or "objects" in only_part:
                for nm in ids:
                    if only_ids and nm not in only_ids:
                        continue
                    fn = OBJS.get(h, {}).get(nm)
                    if not fn:
                        continue
                    t1 = time.time()
                    meta[nm + ("_truth" if truth else "")] = render_object(h, nm, fn, out, truth)
                    print(f"  OBJ {h}/{nm} truth={truth}: {time.time() - t1:.1f}s", flush=True)
            print(f"DONE {h} truth={truth}: {time.time() - t0:.1f}s", flush=True)
        json.dump(meta, open(mpath, "w"), indent=1)


if __name__ == "__main__":
    main()
