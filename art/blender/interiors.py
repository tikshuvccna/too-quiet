"""Dollhouse room shells + object sprites for the three enterable houses.

blender -b --python interiors.py -- <rawdir> <house_id|all> [truth] [shell|objects]
Output: <rawdir>/env/int/<house>/shell[_truth].png and <obj>[_truth].png, plus layout_meta.json (world placements).

World frame of a room: x in [-7,7] (left..right), y in [-4.5,4.5] (front..back wall), z up, back wall at y=+4.5.
Shell canvas 1024x640, world origin (0,0,0) projected to pixel (512, 430).
"""
import json
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env_blocks import *  # noqa
import env_lib as EL

SHELL = (1024, 640)
S_ANCHOR = (512, 430)
RW, RD, RH = 7.0, 4.5, 5.0


def sky_mat(truth):
    """Evening sky seen through the window: emissive gradient + stars. Truth: cold dusk, teal glow low."""
    m = bpy.data.materials.new("sky")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = EL._n(nt, "ShaderNodeOutputMaterial")
    em = EL._n(nt, "ShaderNodeEmission")
    tc = EL._n(nt, "ShaderNodeTexCoord")
    sep = EL._n(nt, "ShaderNodeSeparateXYZ")
    EL._lk(nt, tc.outputs["Generated"], sep.inputs["Vector"])
    stops = ([(0.0, "#ffb86a"), (0.35, "#e8806a"), (0.62, "#8a5a9a"), (1.0, "#2e2c66")] if not truth else
             [(0.0, "#6a8a9a"), (0.35, "#4a5a7a"), (0.62, "#33406a"), (1.0, "#141a38")])
    col = EL._ramp(nt, sep.outputs["Z"], stops)
    st = EL._noise(nt, tc.outputs["Generated"], 90, 0, 0.5)
    sm = EL._maprange(nt, st, 0.80, 0.84, 0, 1)
    top = EL._maprange(nt, sep.outputs["Z"], 0.45, 0.8, 0, 1)
    col = EL._mix(nt, "ADD", EL._math(nt, "MULTIPLY", sm, top), col, (1, 1, 0.9, 1))
    EL._lk(nt, col, em.inputs["Color"])
    em.inputs["Strength"].default_value = 1.0 if not truth else 0.6
    EL._lk(nt, em.outputs["Emission"], out.inputs["Surface"])
    return m


def light_patch(parent, pts, alpha=0.35, color="#ffd49a", fade=True):
    """Soft translucent light polygon on the floor (additive-looking): vertices pts (x,y,z), fades along y."""
    m = bpy.data.materials.new("lp")
    m.surface_render_method = 'BLENDED'
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = EL._n(nt, "ShaderNodeOutputMaterial")
    em = EL._n(nt, "ShaderNodeEmission")
    em.inputs["Color"].default_value = (*srgb(color), 1)
    em.inputs["Strength"].default_value = 1.4
    tr = EL._n(nt, "ShaderNodeBsdfTransparent")
    mx = EL._n(nt, "ShaderNodeMixShader")
    tc = EL._n(nt, "ShaderNodeTexCoord")
    sep = EL._n(nt, "ShaderNodeSeparateXYZ")
    EL._lk(nt, tc.outputs["Generated"], sep.inputs["Vector"])
    g = EL._maprange(nt, sep.outputs["Y"], 0.0, 1.0, alpha, 0.03)
    EL._lk(nt, g, mx.inputs["Fac"])
    EL._lk(nt, tr.outputs["BSDF"], mx.inputs[1])
    EL._lk(nt, em.outputs["Emission"], mx.inputs[2])
    EL._lk(nt, mx.outputs["Shader"], out.inputs["Surface"])
    o = mesh_obj("lightpatch", pts, [tuple(range(len(pts)))], m, parent, smooth=False)
    no_shadow(o)
    return o


def build_room(cfg, truth):
    """Back wall (with window), leaning left wall, floor, skirting, window + sky, rug. Returns the root pivot."""
    R = pivot("room")
    wallm = cfg["wall"]()
    floorm = cfg["floor"]()
    trim = cfg["trim"]()
    cut = PL("#efe3cc", "#dccfb4", wear=0.2, plane="xy")
    side = WD("#5a3c28", "#4a3020", scale=3, plane="xz")
    # floor slab
    box("slab", (2 * RW + 0.3, 2 * RD + 0.3, 0.5), side, R, loc=(0, 0, -0.5), base=True)
    f = box("floor", (2 * RW, 2 * RD, 0.04), floorm, R, loc=(0, 0, -0.02), base=True)
    # back wall with a window opening
    wx, wzb, wzt, ww = cfg["win_x"], 1.55, 4.1, 2.4
    pieces = [(-RW, wx - ww / 2, 0, RH), (wx + ww / 2, RW, 0, RH), (wx - ww / 2, wx + ww / 2, 0, wzb), (wx - ww / 2, wx + ww / 2, wzt, RH)]
    for x0, x1, z0, z1 in pieces:
        box("bw", (x1 - x0, 0.4, z1 - z0), wallm, R, loc=((x0 + x1) / 2, RD + 0.2, z0), base=True)
    # lower wainscot / tiles band
    if cfg.get("wain"):
        wm = cfg["wain"]()
        for x0, x1 in ((-RW, wx - ww / 2), (wx + ww / 2, RW)):
            box("wain", (x1 - x0, 0.06, cfg["wain_h"]), wm, R, loc=((x0 + x1) / 2, RD - 0.03, 0), base=True)
        box("wain", (ww, 0.06, min(cfg["wain_h"], wzb)), wm, R, loc=(wx, RD - 0.03, 0), base=True)
        box("rail", (2 * RW, 0.1, 0.09), trim, R, loc=(0, RD - 0.07, cfg["wain_h"]))
    box("capb", (2 * RW + 0.5, 0.55, 0.28), cut, R, loc=(0, RD + 0.15, RH), base=True)
    # skirting boards
    box("skirt", (2 * RW, 0.1, 0.4), trim, R, loc=(0, RD - 0.12, 0), base=True)
    # leaning left wall: bottom edge on x=-RW, top edge leans outward, height tapers to the front (cutaway)
    L = RW
    lean_b, lean_f = 1.2, 0.3
    hb, hf = RH, 1.3
    lw = mesh_obj("leftwall", [(-L, RD, 0), (-L, -RD, 0), (-L - lean_f, -RD, hf), (-L - lean_b, RD, hb)], [(0, 1, 2, 3)],
                  cfg["wall"](plane="yz"), R, smooth=False)
    mesh_obj("leftcap", [(-L - lean_b, RD, hb), (-L - lean_f, -RD, hf), (-L - lean_f - 0.22, -RD, hf - 0.15), (-L - lean_b - 0.25, RD, hb - 0.17)],
             [(0, 1, 2, 3)], cut, R, smooth=False)
    mesh_obj("leftcap2", [(-L - lean_b - 0.25, RD, hb - 0.17), (-L - lean_f - 0.22, -RD, hf - 0.15), (-L - lean_f - 0.22, -RD, hf - 0.6), (-L - lean_b - 0.25, RD, hb - 0.65)],
             [(0, 1, 2, 3)], WD("#6a4a34", "#5a3c28", plane="yz", scale=3), R, smooth=False)
    mesh_obj("leftskirt", [(-L, RD, 0), (-L, -RD, 0), (-L - 0.07, -RD, 0.4), (-L - 0.07, RD, 0.4)], [(0, 1, 2, 3)], trim, R, smooth=False)
    for o in list(R.children):
        if o.name.startswith(("leftwall", "leftcap", "leftskirt")):
            no_shadow(o)
    # window: frame, mullions, sill, sky + silhouettes
    fm = trim
    for x in (wx - ww / 2 - 0.12, wx + ww / 2 + 0.12):
        box("wfv", (0.24, 0.35, wzt - wzb + 0.3), fm, R, loc=(x, RD - 0.05, (wzb + wzt) / 2))
    box("wft", (ww + 0.5, 0.35, 0.24), fm, R, loc=(wx, RD - 0.05, wzt + 0.1))
    box("wfs", (ww + 0.7, 0.55, 0.14), fm, R, loc=(wx, RD - 0.2, wzb - 0.07))
    sky = pivot("sky", (wx, RD + 0.75, (wzb + wzt) / 2))
    mesh_obj("skyp", [(-ww, 0, -(wzt - wzb) / 2 - 0.3), (ww, 0, -(wzt - wzb) / 2 - 0.3), (ww, 0, (wzt - wzb) / 2 + 0.3), (-ww, 0, (wzt - wzb) / 2 + 0.3)],
             [(0, 1, 2, 3)], sky_mat(truth), sky, smooth=False)
    # hills and the Weavers' tower silhouette, teal glow dots
    hill = glow("#2a2250" if not truth else "#10142a", 0.0001)
    hill = toon("#2a2250" if not truth else "#10142a", rim=0, shade=(1, 1, 1))
    ellipsoid("hill1", 1.6, hill, sky, loc=(-1.1, -0.15, -1.35), scale=(1.7, 0.1, 0.8), seg=14, rings=8)
    ellipsoid("hill2", 1.4, hill, sky, loc=(1.3, -0.15, -1.3), scale=(1.9, 0.1, 0.7), seg=14, rings=8)
    frustum("towr", 0.18, 0.13, 1.6, hill, sky, loc=(0.9, -0.2, -1.15), seg=8)
    frustum("towc", 0.26, 0.0, 0.5, hill, sky, loc=(0.9, -0.2, 0.43), seg=8)
    for k in range(7):
        ellipsoid("spark", 0.025, glow("#35d3b0", 4 if not truth else 2), sky, loc=(0.9 + (k % 3 - 1) * 0.1, -0.22, -0.9 + k * 0.17), seg=5, rings=4)
    ellipsoid("tg", 0.35, glow("#35d3b0", 0.8, alpha=0.4, soft=True), sky, loc=(0.9, -0.25, -0.3), scale=(1, 0.2, 2.2), seg=10, rings=6)
    # moon / sun disc
    ellipsoid("moon", 0.25, glow("#fff3c8" if not truth else "#c8d4e8", 3 if not truth else 1.5), sky, loc=(-0.7, -0.22, 0.55), scale=(1, 0.15, 1), seg=14, rings=8)
    # window light on the floor
    lx0, lx1 = wx - ww / 2, wx + ww / 2
    if not truth:
        light_patch(R, [(lx0 - 0.1, RD - 0.3, 0.03), (lx1 + 0.1, RD - 0.3, 0.03), (lx1 - 2.6, 0.2, 0.03), (lx0 - 2.8, 0.2, 0.03)], 0.42, cfg["light"])
    else:
        light_patch(R, [(lx0 - 0.1, RD - 0.3, 0.03), (lx1 + 0.1, RD - 0.3, 0.03), (lx1 - 1.8, -0.4, 0.03), (lx0 - 2.0, -0.4, 0.03)], 0.2, "#7a9ad8")
    cfg["decor"](R, wx, truth)
    cfg["rug"](R, truth)
    return R


# ================================================================== room configs
def cfg_grandma():
    def wall(plane="xz"):
        return PL("#f0b576", "#e49c5e", plane=plane, wear=0.3, bump=0.6, scale=1.0)
    def wain(): return WD("#c98a52", "#b0733e", scale=3.0, along="v", bump=0.8)
    def floor(): return WD("#c78a50", "#a96f3a", plane="xy", scale=2.2, bump=0.7, wear=0.3)
    def trim(): return WD("#f3e4c4", "#e0cfa8", scale=3, bump=0.4)

    def decor(R, wx, truth):
        # knitted bunting across the wall + stitched frieze + skeins on pegs
        cols = ["#4f7ad8", "#e8b04a", "#c44b3f", "#35b39a", "#f3e4c4", "#a07ad8"]
        pts = [(-6.4 + 12.8 * t / 40, RD - 0.08, 4.35 - 0.38 * math.sin(math.pi * t / 40)) for t in range(41)]
        pts = [p for p in pts if not (wx - 1.5 < p[0] < wx + 1.5)]
        tube("bunt", pts, 0.012, toon("#d9c9a8", rim=0.2), R)
        for i in range(17):
            t = i / 16
            x = -6.2 + 12.4 * t
            if wx - 1.5 < x < wx + 1.5:
                continue
            z = 4.35 - 0.38 * math.sin(math.pi * (x + 6.4) / 12.8)
            mesh_obj("flag", [(x - 0.17, RD - 0.09, z), (x + 0.17, RD - 0.09, z), (x, RD - 0.12, z - 0.45 * (0.7 if truth and i % 4 == 0 else 1))], [(0, 1, 2)],
                     FAB("knit", cols[i % 6], cols[(i + 2) % 6], scale=12, bump=0.9), R, smooth=False)
        for i, x in enumerate((-5.8, -1.2, 5.4)):
            box("peg", (0.1, 0.12, 0.1), toon("wood_d", rim=0), R, loc=(x, RD - 0.12, 2.7))
            yarn_ball(R, (x, RD - 0.25, 2.18), 0.26, cols[i], cols[i + 3])

    def rug(R, truth):
        rug_round(R, (0.4, -1.0, 0.04), 2.7, "#c44b3f", "#f3e4c4", "#35b39a")
    return dict(wall=wall, wain=wain, wain_h=1.3, floor=floor, trim=trim, decor=decor, rug=rug, win_x=3.0,
                light="#ffcf8a", key=("#ffc080", 3.4), world="#8a6fa0")


def cfg_clinic():
    def wall(plane="xz"):
        return PL("#eef3e6", "#dde8d6", plane=plane, wear=0.25, bump=0.4, scale=1.0)
    def wain(): return tex_toon("tiles", "#dfeee0", "#c8dcc8", scale=3.0, plane="xz", bump=0.9, wear=0.3)
    def floor(): return tex_toon("checker", "#dfe8d8", "#a9c2ae", scale=1.1, plane="xy", bump=0.8, wear=0.3)
    def trim(): return WD("#f3f0e4", "#e2e6d8", scale=3, bump=0.4)

    def decor(R, wx, truth):
        # emblem painted on the wall: mortar-and-leaf; hanging herb bunches on a line; framed leaf prints
        pl = pivot("emb", (-3.8, RD - 0.08, 3.1), R)
        frustum("d", 0.55, 0.55, 0.05, PL("#e6f0e0", "#d2e2cc", plane="xz"), pl, rot=(RAD(90), 0, 0), seg=24)
        frustum("r", 0.58, 0.58, 0.04, toon("#3f8f6f", rim=0.2), pl, loc=(0, 0.02, 0), rot=(RAD(90), 0, 0), seg=24)
        ellipsoid("b", 0.22, toon("#6a6a78", rim=0.5), pl, loc=(-0.05, -0.05, -0.12), scale=(1.3, 0.3, 0.8), seg=12, rings=8)
        link_cyl("p", (0.0, -0.08, -0.08), (0.32, -0.08, 0.28), 0.04, toon("#c9bfae", rim=0.5), pl, seg=8)
        ellipsoid("l", 0.18, toon("#3fa05a", rim=0.5), pl, loc=(-0.2, -0.07, 0.2), scale=(0.45, 0.2, 1), rot=(0, RAD(-25), 0), seg=10, rings=8)
        pts = [(-6.5 + 13 * t / 40, RD - 0.2, 4.45 - 0.3 * math.sin(math.pi * t / 40)) for t in range(41)]
        pts = [p for p in pts if not (wx - 1.7 < p[0] < wx + 1.7)]
        tube("hl", pts, 0.01, toon("#d9c9a8", rim=0.2), R)
        rnd = random.Random(3)
        hc = ["#6f9a3c", "#8fb04a", "#a8a04a", "#7a5a8a", "#c9a24a", "#4f8a5a"]
        for i in range(13):
            x = -6.2 + i * 0.95
            if wx - 1.7 < x < wx + 1.7:
                continue
            z = 4.45 - 0.3 * math.sin(math.pi * (x + 6.5) / 13)
            link_cyl("s", (x, RD - 0.2, z), (x, RD - 0.2, z - 0.3), 0.008, toon("#d9c9a8", rim=0), R, seg=3)
            ellipsoid("h", 0.1, toon(hc[i % 6], rim=0.3), R, loc=(x, RD - 0.2, z - 0.5), scale=(0.8, 0.8, 1.9), seg=8, rings=6)
        for k in range(3):
            fx = 0.2 + k * 1.1
            box("fr", (0.8, 0.07, 1.0), toon("#c9b48a", rim=0.3), R, loc=(fx - 1.2, RD - 0.1, 2.7 + 0.15 * (k % 2)))
            box("pr", (0.66, 0.05, 0.86), PL("#f3f0e4", "#e6e2d2", plane="xz", wear=0.1), R, loc=(fx - 1.2, RD - 0.14, 2.7 + 0.15 * (k % 2)))
            ellipsoid("lf", 0.22, toon("#4f9a5a", rim=0.3), R, loc=(fx - 1.2, RD - 0.17, 2.7 + 0.15 * (k % 2)), scale=(0.6, 0.15, 1.2), rot=(0, RAD(20 * (k - 1)), 0), seg=10, rings=8)

    def rug(R, truth):
        box("mat", (3.6, 2.2, 0.02), FAB("weave", "#4f9a7a", "#cfe8d8", scale=7, plane="xy", bump=0.7), R, loc=(0.4, -1.5, 0.0), base=True)
        box("matb", (3.9, 2.5, 0.015), toon("#3f7a6a", rim=0.2), R, loc=(0.4, -1.5, 0.0), base=True)
    return dict(wall=wall, wain=wain, wain_h=1.5, floor=floor, trim=trim, decor=decor, rug=rug, win_x=3.2,
                light="#dfffe8", key=("#e8fff0", 3.0), world="#8aa0b8")


def cfg_print():
    def wall(plane="xz"):
        return PL("#a88898", "#947684", plane=plane, wear=0.5, bump=0.6, scale=1.0)
    def wain(): return WD("#4a3040", "#3c2434", scale=2.6, along="v", bump=0.8)
    def floor(): return WD("#5c4048", "#4a323a", plane="xy", scale=2.0, bump=0.7, wear=0.5)
    def trim(): return WD("#3e2a36", "#32202c", scale=3, bump=0.5)

    def decor(R, wx, truth):
        # exposed timber frame on the wall, pinned notices, a drying line of printed sheets
        tm = WDT("#3e2a36", "#32202c")
        for x in (-6.9, -3.4, 0.0, 6.9):
            box("ptm", (0.28, 0.1, RH), tm, R, loc=(x, RD - 0.06, 0), base=True)
        for z in (2.9,):
            box("pbm", (2 * RW, 0.1, 0.24), tm, R, loc=(0, RD - 0.06, z))
        link_cyl("br", (-3.4, RD - 0.07, 2.9), (-2.4, RD - 0.07, 4.2), 0.07, tm, R, seg=5)
        link_cyl("br", (0, RD - 0.07, 2.9), (-1.0, RD - 0.07, 4.2), 0.07, tm, R, seg=5)
        ln = [(-6.4 + 5.5 * t / 20, RD - 0.35, 4.3 - 0.25 * math.sin(math.pi * t / 20)) for t in range(21)]
        tube("dl", ln, 0.01, toon("#d9c9a8", rim=0.2), R)
        for i in range(8):
            x = -6.2 + i * 0.68
            z = 4.3 - 0.25 * math.sin(math.pi * (x + 6.4) / 5.5)
            box("sh", (0.4, 0.02, 0.6), tex_toon("paper", "#f3e8cc", "#2a3a8a", scale=3.2, plane="xz", bump=0.1), R,
                loc=(x, RD - 0.36, z - 0.32), rot=(0, RAD(((i * 7) % 5 - 2) * 3), 0))
        rnd = random.Random(7)
        for i in range(9):
            box("note", (0.4, 0.02, 0.5), tex_toon("paper", "#f1e6c8", "#2a2a60", scale=3.6, plane="xz", bump=0.1), R,
                loc=(2.2 + (i % 3) * 0.52 + 3.6, RD - 0.1, 2.0 + (i // 3) * 0.62), rot=(0, RAD(rnd.uniform(-5, 5)), 0))

    def rug(R, truth):
        box("rug", (4.2, 2.6, 0.02), tex_toon("paper", "#8a6a8a", "#2a2a60", scale=2.6, plane="xy", bump=0.5, wear=0), R, loc=(-0.3, -1.4, 0.0), base=True)
        box("rugb", (4.5, 2.9, 0.015), toon("#4a3040", rim=0.2), R, loc=(-0.3, -1.4, 0.0), base=True)
    return dict(wall=wall, wain=wain, wain_h=1.1, floor=floor, trim=trim, decor=decor, rug=rug, win_x=-3.4,
                light="#d8b8ff", key=("#e0b8ff", 3.0), world="#6a5a8a")


CFGS = {"house_grandma": cfg_grandma, "house_clinic": cfg_clinic, "house_print": cfg_print}


# ================================================================== harness
def render_shell(house, outdir, truth):
    cfg = CFGS[house]()
    EL.set_truth(truth)
    reset_env()
    EL.set_truth(truth)
    kc, ke = cfg["key"]
    EL.env_lights(key_col=kc, key_e=ke, rim_col="#9fb8ff", rim_e=1.2, world=cfg["world"], world_e=0.7, key_dir=(-0.6, -1.0, 1.1))
    build_room(cfg, truth)
    render_scene(SHELL, S_ANCHOR, os.path.join(outdir, "shell" + ("_truth" if truth else "") + ".png"), samples=24)


def render_object(name, fn, cfg_key, outdir, truth, cell=(384, 320), anchor=(192, 236)):
    cfg = CFGS[cfg_key]()
    reset_env()
    EL.set_truth(truth)
    kc, ke = cfg["key"]
    EL.env_lights(key_col=kc, key_e=ke, rim_col="#9fb8ff", rim_e=1.2, world=cfg["world"], world_e=0.7, key_dir=(-0.6, -1.0, 1.1))
    R = pivot("obj")
    extra = fn(R) or {}
    cell = extra.get("cell", cell)
    anchor = extra.get("anchor", anchor)
    render_scene(cell, anchor, os.path.join(outdir, name + ("_truth" if truth else "") + ".png"), samples=24)
    return {"cell": list(cell), "anchor": list(anchor)}


def main():
    a = script_args()
    rawdir = a[0]
    which = a[1]
    truth = "truth" in a
    only = [x for x in a[2:] if x in ("shell", "objects")]
    houses = list(CFGS) if which == "all" else [which]
    mpath = os.path.join(rawdir, "env", "int", "layout_meta.json")
    meta = json.load(open(mpath)) if os.path.exists(mpath) else {}
    for h in houses:
        out = os.path.join(rawdir, "env", "int", h)
        os.makedirs(out, exist_ok=True)
        t0 = time.time()
        if not only or "shell" in only:
            render_shell(h, out, truth)
            print(f"SHELL {h} truth={truth}: {time.time() - t0:.1f}s")
        if not only or "objects" in only:
            from interiors_objs import OBJECTS
            hm = meta.setdefault(h, {})
            for nm, fn in OBJECTS[h].items():
                t1 = time.time()
                hm[nm + ("_truth" if truth else "")] = render_object(nm, fn, h, out, truth)
                print(f"  OBJ {h}/{nm} truth={truth}: {time.time() - t1:.1f}s")
    json.dump(meta, open(mpath, "w"), indent=1)


if __name__ == "__main__":
    main()
