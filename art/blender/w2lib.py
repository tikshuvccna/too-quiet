"""Shared helpers for the world-2 art (buildings_c/d, props_b): auto-fit cell + anchor, banners, prism roofs, lanterns, truth extras."""
import json
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env_blocks import *  # noqa
import env_lib as EL
import env_blocks as EB
_WIN_N = EB._WIN_N
from buildings import ridge_cap, eave_trim, roof_z_at  # noqa
from buildings_b import roof_hole, sagging_threads, bead_cloud, np_range  # noqa

COS = math.cos(math.radians(ELEVATION_DEG))
SIN = math.sin(math.radians(ELEVATION_DEG))


def autofit(margin=20, extra_bottom=6):
    """Bounding box of every mesh/curve in oblique pixels around the world origin -> (cell, anchor)."""
    bpy.context.view_layer.update()
    x0 = y0 = 1e9
    x1 = y1 = -1e9
    for o in bpy.context.scene.objects:
        if o.type not in ("MESH", "CURVE"):
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            px = w.x * PPU
            py = -(w.z * COS + w.y * SIN) * PPU
            x0, x1, y0, y1 = min(x0, px), max(x1, px), min(y0, py), max(y1, py)
    cw = int(math.ceil((x1 - x0 + 2 * margin) / 8.0) * 8)
    ch = int(math.ceil((y1 - y0 + 2 * margin + extra_bottom) / 8.0) * 8)
    ax = -x0 + margin + (cw - (x1 - x0 + 2 * margin)) / 2
    ay = -y0 + margin
    return (cw, ch), (round(ax, 1), round(ay, 1))


def run_main(BUILDERS, subdir="env2", metaname="buildings2_meta.json", fit_extra=None):
    a = script_args()
    rawdir = a[0]
    truth = "truth" in a
    a = [x for x in a if x != "truth"]
    names = a[1:] or list(BUILDERS)
    out = os.path.join(rawdir, subdir)
    os.makedirs(out, exist_ok=True)
    mp = os.path.join(out, metaname)
    meta = json.load(open(mp)) if os.path.exists(mp) else {}
    sfx = "_truth" if truth else ""
    for nm in names:
        t0 = time.time()
        reset_env()
        EL.set_truth(truth)
        env_lights()
        r = BUILDERS[nm]()
        if "cell" in meta.get(nm, {}) and truth:      # truth reuses the facade cell/anchor: identical framing
            cell, anchor = tuple(meta[nm]["cell"]), tuple(meta[nm]["anchor"])
        else:
            cell, anchor = autofit()
        render_scene(cell, anchor, os.path.join(out, nm + sfx + ".png"), samples=24)
        info = {"cell": cell, "anchor": anchor}
        info["smoke"] = [[round(project(x, y, z, anchor)[0], 1), round(project(x, y, z, anchor)[1], 1)] for (x, y, z) in r.get("smoke", [])]
        if not truth:
            meta[nm] = info
        meta[nm + sfx] = info
        json.dump(meta, open(mp, "w"), indent=1)
        print(f"W2 {nm}{sfx}: {time.time() - t0:.1f}s cell={cell}")


# ------------------------------------------------------------------ geometry
def prism_roof(name, profile, length, mat, parent, loc=(0, 0, 0), caps=True):
    """Extrude a (y,z) profile along X (centred). Used for gambrel / barrel / jerkin roofs."""
    L = length / 2
    n = len(profile)
    v = [(x, y, z) for x in (-L, L) for (y, z) in profile]
    f = [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)]
    if caps:
        f.append(tuple(range(n)))
        f.append(tuple(reversed(range(n, 2 * n))))
    return mesh_obj(name, v, f, mat, parent, loc, smooth=False)


def gable_wall(parent, w, h, z, y, mat):
    """Front triangle wall (ridge along Y roofs)."""
    return mesh_obj("gtri", [(-w / 2, y, z), (w / 2, y, z), (0, y, z + h)], [(0, 2, 1)], mat, parent, smooth=False)


def banner(parent, loc, w, h, c1, c2, emblem="#e8b04a", fring=True):
    p = pivot("banner", loc, parent)
    box("rod", (w + 0.24, 0.06, 0.06), WDT(), p)
    for s in (-1, 1):
        ellipsoid("kn", 0.05, toon("gold", rim=0.5), p, loc=(s * (w / 2 + 0.12), 0, 0), seg=6, rings=4)
    m = FAB("weave", c1, c2, scale=11, bump=0.5)
    box("cloth", (w, 0.03, h), m, p, loc=(0, -0.03, -h / 2 - 0.04))
    mesh_obj("tail", [(-w / 2, -0.03, -h - 0.04), (w / 2, -0.03, -h - 0.04), (0, -0.03, -h - 0.04 - w * 0.4)], [(0, 2, 1)],
             toon(c1, rim=0.3), p, smooth=False)
    mesh_obj("tailin", [(-w / 2 + 0.08, -0.036, -h - 0.04), (w / 2 - 0.08, -0.036, -h - 0.04), (0, -0.036, -h - 0.04 - w * 0.3)],
             [(0, 2, 1)], toon(c2, rim=0.3), p, smooth=False)
    # emblem: gold spool-ish disc with a thread loop
    ellipsoid("emb", w * 0.2, toon(emblem, rim=0.5), p, loc=(0, -0.05, -h * 0.4), scale=(1, 0.2, 1), seg=12, rings=8)
    box("embb", (w * 0.55, 0.035, 0.06), toon(emblem, rim=0.5), p, loc=(0, -0.05, -h * 0.4 - w * 0.3))
    return p


def big_lantern(parent, loc, s=1.0, color="#ffc66a", glow_s=7):
    p = pivot("blantern", loc, parent)
    d = toon("#2e2a30", rim=0.3)
    box("base", (0.5 * s, 0.5 * s, 0.1 * s), d, p, loc=(0, 0, 0.0))
    box("glass", (0.4 * s, 0.4 * s, 0.6 * s), glow(color, glow_s), p, loc=(0, 0, 0.35 * s))
    for sx in (-1, 1):
        for sy in (-1, 1):
            box("post", (0.05 * s, 0.05 * s, 0.66 * s), d, p, loc=(sx * 0.2 * s, sy * 0.2 * s, 0.35 * s))
    frustum("cap", 0.42 * s, 0.03 * s, 0.3 * s, d, p, loc=(0, 0, 0.66 * s), seg=4, rot=(0, 0, RAD(45)))
    ellipsoid("fin", 0.06 * s, toon("gold", rim=0.5), p, loc=(0, 0, 1.0 * s), seg=8, rings=6)
    ellipsoid("halo", 0.7 * s, glow(color, 2.5, alpha=0.5, soft=True), p, loc=(0, -0.05, 0.35 * s), seg=12, rings=8)
    return p


def arch_window(parent, loc, w=0.8, h=1.2, frame="#e8d6b0", light="window", glow_s=3.2, bars=True):
    """Tall window with a round top and mullions (front plane), loc = centre of the rectangular part."""
    p = pivot("awin", loc, parent)
    fm = toon(frame, rim=0.15)
    box("fr", (w + 0.2, 0.1, h + 0.2), fm, p, loc=(0, -0.03, 0))
    frustum("fra", w / 2 + 0.1, w / 2 + 0.1, 0.1, fm, p, loc=(0, 0.0, h / 2 + 0.1), rot=(RAD(90), 0, 0), seg=18)
    kind_dark = EL.TRUTH and (_WIN_N[0] % 3 != 1)
    _WIN_N[0] += 1
    g = toon("#141a28", rim=0) if kind_dark else glow(light, glow_s)
    box("pane", (w, 0.05, h), g, p, loc=(0, -0.08, 0))
    frustum("pana", w / 2, w / 2, 0.05, g, p, loc=(0, -0.05, h / 2), rot=(RAD(90), 0, 0), seg=18)
    if bars:
        box("mv", (0.05, 0.07, h + w / 2), fm, p, loc=(0, -0.1, w / 4))
        for z in (-h * 0.2, h * 0.2):
            box("mh", (w, 0.07, 0.045), fm, p, loc=(0, -0.1, z))
    box("sill", (w + 0.34, 0.22, 0.08), ST("#a8a09a", "#8c848a", scale=3, bump=0.5), p, loc=(0, -0.1, -h / 2 - 0.12))
    if EL.TRUTH and kind_dark and (_WIN_N[0] % 2 == 0):
        link_cyl("crk", (-w * .3, -0.11, h * .4), (w * .2, -0.11, -h * .2), 0.012, toon("#9aa6b8", rim=0), p, seg=4)
    return p


def truth_extras(R, cob=(), threads=(), dead=(), holes=()):
    if not EL.TRUTH:
        return
    for c in cob:
        cobweb(R, c[:3], c[3] if len(c) > 3 else 0.45)
    if threads:
        sagging_threads(R, list(threads), seed=len(threads) + 3)
    for d_ in dead:
        dead_plant(R, d_[:3], d_[3] if len(d_) > 3 else 0.5, seed=int(abs(d_[0] * 7)) % 9 + 1)
    for h_ in holes:
        roof_hole(R, *h_[:2], **h_[2])


def sheep(parent, loc, rot=0.0, s=1.0):
    p = pivot("sheep", loc, parent, rot=(0, 0, rot))
    wool = tex_toon("knit", "#f3eee4", "#d9d2c6", scale=9, plane="xz", bump=1.0, rim=0.5, ao=0.3)
    ellipsoid("body", 0.34 * s, wool, p, loc=(0, 0, 0.42 * s), scale=(1.2, 0.85, 0.9), seg=14, rings=10)
    ellipsoid("head", 0.14 * s, toon("#3a3238", rim=0.4), p, loc=(0.4 * s, -0.02, 0.5 * s), scale=(1.1, 0.8, 1.0), seg=10, rings=8)
    ellipsoid("cap", 0.12 * s, wool, p, loc=(0.32 * s, -0.02, 0.62 * s), seg=8, rings=6)
    for sx in (-1, 1):
        for sy in (-1, 1):
            link_cyl("leg", (sx * 0.2 * s, sy * 0.12 * s, 0.2 * s), (sx * 0.2 * s, sy * 0.12 * s, 0.0), 0.03 * s, toon("#3a3238", rim=0), p, seg=5)
    ellipsoid("ear", 0.06 * s, toon("#3a3238", rim=0.3), p, loc=(0.4 * s, 0.1 * s, 0.56 * s), scale=(0.5, 1, 0.5), seg=6, rings=4)
    ellipsoid("ear", 0.06 * s, toon("#3a3238", rim=0.3), p, loc=(0.4 * s, -0.14 * s, 0.56 * s), scale=(0.5, 1, 0.5), seg=6, rings=4)
    return p


def fence_run(parent, x0, x1, y, n=None, h=0.7, col="#9a6238"):
    wd = WD(col, "#7d4a2a", scale=4, bump=0.5)
    n = n or max(2, int((x1 - x0) / 0.8))
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        box("fp", (0.1, 0.1, h + 0.15), wd, parent, loc=(x, y, (h + 0.15) / 2))
    for z in (h * 0.4, h * 0.85):
        box("fr", (x1 - x0, 0.06, 0.08), wd, parent, loc=((x0 + x1) / 2, y, z))


def rocks_at(parent, pts, col="#8d8794", seed=1):
    rnd = random.Random(seed)
    for (x, y, r) in pts:
        ellipsoid("rock", r, ST(col, "#6f6874", scale=3, bump=0.8, moss=0.5), parent, loc=(x, y, r * 0.35),
                  scale=(1.2, 1.0, 0.7), rot=(0, 0, rnd.uniform(0, 3)), seg=9, rings=6)
