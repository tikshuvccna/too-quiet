"""Model + render the village props (single oblique angle, camera looking from the south).

blender -b --python props.py -- <rawdir> [name ...]
Writes <rawdir>/props/<name>.png and <rawdir>/props/props_meta.json (cell size + ground anchor).
art/pack.py props <rawdir> outlines/downsamples/packs them into public/assets/props/props.{png,json}.
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from common import *

T = toon  # shorthand
RAD = math.radians


# ----------------------------------------------------------- building blocks
def gable(name, w, d, h, ov, mat, parent, loc=(0, 0, 0), ends=True):
    """Roof with ridge along local X, eaves at z=0 (local origin = centre of the footprint)."""
    W, D = w / 2 + ov, d / 2 + ov
    v = [(-W, -D, 0), (W, -D, 0), (W, D, 0), (-W, D, 0), (-W, 0, h), (W, 0, h)]
    f = [(0, 1, 5, 4), (3, 4, 5, 2)]
    if ends:
        f += [(0, 4, 3), (1, 2, 5)]
    return mesh_obj(name, v, f, mat, parent, loc, smooth=False)


def gable_rows(w, d, h, ov, mat, parent, loc, n=7, thick=0.05, drop=0.0):
    W, D = w / 2 + ov, d / 2 + ov
    th = math.atan2(h, D)
    for side in (-1, 1):
        for k in range(1, n):
            t = k / n
            y, z = side * D * (1 - t), h * t
            nrm = (0, -side * math.sin(th), math.cos(th))
            box("row", (2 * W + 0.01, thick, 0.035), mat, parent,
                loc=(loc[0], loc[1] + y + nrm[1] * 0.022, loc[2] + z + nrm[2] * 0.022), rot=(side * -1 * th * -1 if False else (th if side == -1 else -th), 0, 0))
    # ridge cap
    frustum("ridge", 0.1, 0.1, 2 * W + 0.04, mat, parent, loc=(loc[0] - W - 0.02, loc[1], loc[2] + h), rot=(0, RAD(90), 0), seg=8)


def eave_roll(w, d, ov, mat, parent, loc, r=0.1):
    W, D = w / 2 + ov, d / 2 + ov
    for s in (-1, 1):
        frustum("roll", r, r, 2 * W, mat, parent, loc=(loc[0] - W, loc[1] + s * D, loc[2]), rot=(0, RAD(90), 0), seg=8)


def window(parent, loc, rotz=0.0, w=0.8, h=0.75, shutter="teal_roof", flowers=True, glow_s=3.2, round_=False):
    p = pivot("win", loc, parent, rot=(0, 0, rotz))   # wall surface at local y=0, outward = -y
    frame = T("wood_d", rim=0.1)
    box("frame", (w + 0.16, 0.08, h + 0.16), frame, p, loc=(0, -0.03, 0))
    box("pane", (w, 0.05, h), glow("window", glow_s), p, loc=(0, -0.075, 0))
    box("mull_v", (0.045, 0.06, h), frame, p, loc=(0, -0.09, 0))
    box("mull_h", (w, 0.06, 0.045), frame, p, loc=(0, -0.09, 0.0))
    box("sill", (w + 0.3, 0.2, 0.07), T("stone"), p, loc=(0, -0.1, -h / 2 - 0.1))
    for s in (-1, 1):
        box("shutter", (0.3, 0.05, h + 0.08), T(shutter), p, loc=(s * (w / 2 + 0.3), -0.06, 0), rot=(0, 0, s * RAD(-8)))
    if flowers:
        box("fbox", (w + 0.1, 0.16, 0.14), T("wood"), p, loc=(0, -0.2, -h / 2 - 0.22))
        cols = ["red", "gold", "white", "wine"]
        for i in range(5):
            ellipsoid("fl", 0.065, T(cols[i % 4], rim=0), p, loc=(-w / 2 + 0.08 + i * (w - 0.16) / 4, -0.2, -h / 2 - 0.1), seg=8, rings=6)
        for i in range(4):
            ellipsoid("leaf", 0.07, T("leaf1", rim=0), p, loc=(-w / 2 + 0.2 + i * (w - 0.3) / 3, -0.2, -h / 2 - 0.18), scale=(1.3, 1, 0.7), seg=8, rings=6)
    return p


def door(parent, loc, w=0.95, h=1.8, rotz=0.0, color="wood", arch=True):
    p = pivot("door", loc, parent, rot=(0, 0, rotz))
    frame = T("wood_d", rim=0.1)
    box("dframe", (w + 0.22, 0.1, h + 0.1), frame, p, loc=(0, -0.03, h / 2 + 0.02))
    box("leaf", (w, 0.08, h - 0.1), T(color), p, loc=(0, -0.08, (h - 0.1) / 2), bevel=0.01)
    if arch:
        fr = frustum("arch", w / 2, w / 2, 0.08, T(color), p, loc=(0, -0.04, h - 0.1), rot=(RAD(90), 0, 0), seg=16, caps=(True, True))
        frustum("archf", w / 2 + 0.11, w / 2 + 0.11, 0.1, frame, p, loc=(0, 0.0, h - 0.1), rot=(RAD(90), 0, 0), seg=16)
    for i in (-1, 0, 1):
        box("plank", (0.03, 0.03, h - 0.25), T("wood_d", rim=0), p, loc=(i * w * 0.3, -0.125, (h - 0.1) / 2))
    for z in (0.35, h - 0.45):
        box("hinge", (w, 0.04, 0.06), T("leather_d", rim=0), p, loc=(0, -0.13, z))
    ellipsoid("knob", 0.045, T("gold", rim=0), p, loc=(w * 0.32, -0.15, h * 0.46), seg=8, rings=6)
    box("step", (w + 0.5, 0.45, 0.14), T("stone"), p, loc=(0, -0.3, 0.07))
    return p


def lantern(parent, loc, rotz=0.0):
    p = pivot("lantern", loc, parent, rot=(0, 0, rotz))
    link_cyl("arm", (0, 0, 0), (0, -0.3, 0), 0.02, T("leather_d", rim=0), p, seg=5)
    link_cyl("hook", (0, -0.3, 0), (0, -0.3, -0.1), 0.012, T("leather_d", rim=0), p, seg=5)
    box("cage", (0.18, 0.18, 0.24), T("leather_d", rim=0), p, loc=(0, -0.3, -0.24))
    box("glass", (0.13, 0.13, 0.2), glow("amber", 6), p, loc=(0, -0.3, -0.24))
    frustum("lcap", 0.16, 0.02, 0.1, T("leather_d", rim=0), p, loc=(0, -0.3, -0.12), seg=4, rot=(0, 0, RAD(45)))
    ellipsoid("lhalo", 0.26, glow("amber", 3, alpha=0.9, soft=True), p, loc=(0, -0.3, -0.24), seg=12, rings=8)
    return p


def barrel(parent, loc, r=0.28, h=0.55):
    p = pivot("barrel", loc, parent)
    frustum("b", r, r * 0.92, h, T("wood"), p, seg=14)
    frustum("b2", r * 1.0, r * 1.0, h * 0.2, T("wood"), p, loc=(0, 0, h * 0.4), caps=(False, False), seg=14)
    for z in (0.12, h - 0.18):
        frustum("band", r * 1.04, r * 1.04, 0.05, T("leather_d", rim=0), p, loc=(0, 0, z), caps=(False, False), seg=14)
    ellipsoid("lid", r * 0.9, T("wood_d"), p, loc=(0, 0, h), scale=(1, 1, 0.12), seg=14, rings=6)
    return p


def crate(parent, loc, s=0.42, rot=0.0):
    p = pivot("crate", loc, parent, rot=(0, 0, rot))
    box("c", (s, s, s), T("wood"), p, loc=(0, 0, s / 2), bevel=0.02)
    for sx in (-1, 1):
        box("cs", (0.05, s + 0.01, s + 0.01), T("wood_d", rim=0), p, loc=(sx * s * 0.36, 0, s / 2))
    return p


def bush(parent, loc, r=0.4, col="leaf1", flowers=True, seed=1):
    rnd = random.Random(seed)
    p = pivot("bush", loc, parent)
    for dx, dy, dz, k in [(0, 0, 0.55, 1), (0.5, 0.05, 0.4, .75), (-0.5, 0.0, 0.4, .75), (0.2, -0.3, 0.35, .6)]:
        ellipsoid("b", r * k, T(col if dx >= 0 else "leaf2"), p, loc=(dx * r * 1.3, dy * r, dz * r), scale=(1, 1, 0.9), seg=12, rings=8)
    if flowers:
        for i in range(6):
            a = rnd.uniform(0, 6.28)
            ellipsoid("fl", 0.05, T(rnd.choice(["red", "gold", "white"]), rim=0), p,
                      loc=(math.cos(a) * r * 1.1, -abs(math.sin(a)) * r * 0.9, r * rnd.uniform(0.5, 1.1)), seg=6, rings=5)
    return p


def stone_blocks(parent, w, h, y, rnd, cols=("stone", "stone_d", "#b8afa6"), nx=7, ny=5, z0=0.0, skip=None):
    bw, bh = w / nx, h / ny
    for j in range(ny):
        off = (bw / 2) if j % 2 else 0
        for i in range(nx + 1):
            cx = -w / 2 + i * bw + off
            if cx - bw / 2 < -w / 2 - 0.01 or cx + bw / 2 > w / 2 + 0.01:
                continue
            if skip and skip(cx, z0 + j * bh + bh / 2):
                continue
            box("blk", (bw * 0.92, 0.05, bh * 0.85), T(rnd.choice(cols)), parent, loc=(cx, y, z0 + j * bh + bh / 2), bevel=0.012)


# ----------------------------------------------------------- cottages
def cottage_a():
    """Timber-frame cottage, golden thatch, chimney, ridge parallel to the street."""
    cell = (256, 256)
    R = pivot("A")
    w, d, wh = 3.5, 2.6, 2.25
    box("found", (w + 0.1, d + 0.1, 0.35), T("stone"), R, loc=(0, 0, 0), base=True)
    box("walls", (w, d, wh - 0.3), T("plaster"), R, loc=(0, 0, 0.35), base=True)
    # timber frame on the front
    tm = T("wood_d", rim=0.05)
    for x in (-w / 2 + 0.06, -0.2, w / 2 - 0.06):
        box("post", (0.12, 0.06, wh - 0.3), tm, R, loc=(x, -d / 2 - 0.02, 0.35), base=True)
    box("beam", (w, 0.06, 0.13), tm, R, loc=(0, -d / 2 - 0.02, wh - 0.1))
    box("beam2", (w, 0.06, 0.1), tm, R, loc=(0, -d / 2 - 0.02, 0.45))
    link_cyl("brace", (1.0, -d / 2 - 0.02, 0.5), (w / 2 - 0.1, -d / 2 - 0.02, wh - 0.2), 0.05, tm, R, seg=5)
    # side walls just darker plaster tint: fine
    # roof: thatch
    roof_z = wh - 0.05
    ov = 0.42
    gable("thatch", w, d, 1.3, ov, T("thatch", rim=0.5), R, loc=(0, 0, roof_z))
    gable_rows(w, d, 1.3, ov, T("#a97b36", rim=0.3), R, (0, 0, roof_z), n=9, thick=0.09)
    eave_roll(w, d, ov, T("#e0b866", rim=0.3), R, (0, 0, roof_z + 0.02), r=0.12)
    # chimney
    box("chim", (0.5, 0.5, 2.0), T("stone"), R, loc=(1.0, 0.25, 2.2), base=True)
    box("chimcap", (0.62, 0.62, 0.12), T("stone_d"), R, loc=(1.0, 0.25, 4.2), base=True)
    # glowing door + windows
    door(R, (-0.85, -d / 2, 0.0), w=0.95, h=1.75)
    window(R, (0.85, -d / 2, 1.25), w=0.9, h=0.8, shutter="teal_roof")
    window(R, (-1.45, -d / 2, 1.5), w=0.5, h=0.55, shutter="red", flowers=False)
    lantern(R, (-0.05, -d / 2, 1.9))
    # roof dormer window
    dp = pivot("dormer", (0.2, -0.85, roof_z + 0.5), R)
    box("dbody", (0.9, 0.5, 0.65), T("plaster"), dp, loc=(0, 0, 0))
    drp = pivot("drp", (0, 0, 0.32), dp, rot=(0, 0, RAD(90)))
    gable("dthatch", 0.5, 0.9, 0.3, 0.1, T("thatch", rim=0.5), drp, ends=True)
    box("dpane", (0.5, 0.04, 0.42), glow("window", 3.2), dp, loc=(0, -0.27, -0.02))
    box("dfr", (0.6, 0.05, 0.52), T("wood_d"), dp, loc=(0, -0.26, -0.02))
    barrel(R, (1.45, -1.55, 0.0))
    crate(R, (1.95, -1.4, 0.0), 0.4, RAD(15))
    crate(R, (1.9, -1.4, 0.4), 0.3, RAD(-10))
    bush(R, (-1.9, -1.55, 0), r=0.38, seed=3)
    # stepping stones path
    for i, (x, y) in enumerate([(-0.85, -1.75), (-0.8, -2.15)]):
        ellipsoid("stp", 0.22, T("stone"), R, loc=(x, y, 0.02), scale=(1.2, 0.8, 0.18), seg=10, rings=5)
    R.scale = (0.92, 0.92, 0.92)
    return (288, 288), (144, 216)


def cottage_b():
    """Stone cottage, red clay tile roof with gable facing the street, bay of flowers."""
    cell = (256, 256)
    rnd = random.Random(7)
    R = pivot("B")
    w, d, wh = 3.2, 3.0, 2.3
    box("found", (w + 0.1, d + 0.1, 0.3), T("stone_d"), R, base=True)
    box("walls", (w, d, wh), T("stone"), R, base=True)
    door_x, wins = 0.0, [(-1.0, 1.35), (1.0, 1.35)]

    def skip(cx, cz):
        if abs(cx - door_x) < 0.75 and cz < 1.95:
            return True
        for wx, wz in wins:
            if abs(cx - wx) < 0.7 and abs(cz - wz) < 0.62:
                return True
        return False
    stone_blocks(R, w, wh - 0.3, -d / 2 - 0.01, rnd, nx=8, ny=7, z0=0.3, skip=skip)
    # front gable (plaster with timber) – ridge along y
    gw = pivot("gablewall", (0, -d / 2, wh), R)
    v = [(-w / 2, 0, 0), (w / 2, 0, 0), (0, 0, 1.65)]
    mesh_obj("gtri", [(-w / 2, 0, 0), (w / 2, 0, 0), (0, 0, 1.65)], [(0, 2, 1)], T("plaster2"), gw, smooth=False)
    tm = T("wood_d", rim=0.05)
    link_cyl("gb1", (-w / 2 + 0.02, -0.03, 0.03), (0, -0.03, 1.6), 0.05, tm, gw, seg=5)
    link_cyl("gb2", (w / 2 - 0.02, -0.03, 0.03), (0, -0.03, 1.6), 0.05, tm, gw, seg=5)
    box("gbeam", (w, 0.06, 0.1), tm, gw, loc=(0, -0.03, 0.05))
    box("gpost", (0.09, 0.06, 1.6), tm, gw, loc=(0, -0.03, 0.0), base=True)
    # roof (tile), ridge along y: rotate a local roof by 90 deg
    rp = pivot("roofp", (0, 0, wh), R, rot=(0, 0, RAD(90)))
    ov = 0.35
    gable("tile", d, w, 1.65, ov, T("tile", rim=0.4), rp, ends=False)
    gable_rows(d, w, 1.65, ov, T("#8e3f2c", rim=0.2), rp, (0, 0, 0), n=10, thick=0.05)
    eave_roll(d, w, ov, T("#d77a52", rim=0.3), rp, (0, 0, 0.02), r=0.07)
    # attic round window
    frustum("atticf", 0.3, 0.3, 0.08, tm, gw, loc=(0, -0.04, 0.6), rot=(RAD(90), 0, 0), seg=18)
    frustum("attic", 0.23, 0.23, 0.08, glow("window", 3.4), gw, loc=(0, -0.07, 0.6), rot=(RAD(90), 0, 0), seg=18)
    # chimney on the left
    box("chim", (0.55, 0.55, 2.1), T("stone_d"), R, loc=(-1.0, 0.4, 2.3), base=True)
    box("chimcap", (0.7, 0.7, 0.12), T("stone"), R, loc=(-1.0, 0.4, 4.4), base=True)
    door(R, (door_x, -d / 2, 0.0), w=1.0, h=1.85, color="forest")
    for wx, wz in wins:
        window(R, (wx, -d / 2 - 0.01, wz), w=0.78, h=0.75, shutter="red" if wx < 0 else "ochre")
    lantern(R, (0.85, -d / 2, 2.0))
    # vine of lanterns? simple hanging sign with a needle
    barrel(R, (-1.85, -1.3, 0.0), 0.3, 0.6)
    bush(R, (1.95, -1.4, 0), r=0.42, seed=11)
    bush(R, (-1.75, -1.75, 0), r=0.3, col="leaf2", seed=5)
    R.scale = (0.92, 0.92, 0.92)
    return (288, 288), (144, 216)


def cottage_c():
    """Round storybook tower-cottage with a teal conical tile roof and an annex."""
    cell = (256, 256)
    R = pivot("C")
    r, wh = 1.55, 2.3
    frustum("base", r + 0.1, r + 0.07, 0.4, T("stone"), R, seg=24)
    frustum("walls", r, r, wh - 0.4, T("blue_plaster"), R, loc=(0, 0, 0.4), seg=24, caps=(False, True))
    # roof: stacked courses
    n = 7
    rh = 2.25
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        r0 = (r + 0.4) * (1 - t0) + 0.05
        r1 = (r + 0.4) * (1 - t1) + 0.05
        col = "teal_roof" if i % 2 == 0 else "#357f84"
        frustum("course", r0, r1 + 0.02, rh / n, T(col, rim=0.4), R, loc=(0, 0, wh + rh * t0), seg=24, caps=(False, False))
        frustum("lip", r0 + 0.035, r0 + 0.035, 0.04, T("#2b6d72", rim=0.2), R, loc=(0, 0, wh + rh * t0), seg=24, caps=(False, False))
    frustum("rolltop", r + 0.45, r + 0.45, 0.001, T("#2b6d72"), R, loc=(0, 0, wh), seg=24)
    ellipsoid("fin", 0.12, T("gold", rim=0.1), R, loc=(0, 0, wh + rh + 0.08), seg=10, rings=8)
    link_cyl("pole", (0, 0, wh + rh), (0, 0, wh + rh + 0.55), 0.025, T("wood_d", rim=0), R, seg=5)
    mesh_obj("flag", [(0, 0, wh + rh + 0.5), (0.4, 0.02, wh + rh + 0.4), (0, 0, wh + rh + 0.3)], [(0, 1, 2)], T("gold", rim=0), R, smooth=False)
    # door + windows around the curve (front = -Y = angle -90 deg)
    def on_wall(a_deg, z, builder_fn, **kw):
        a = RAD(a_deg)
        loc = (math.cos(a) * r, math.sin(a) * r, z)
        return builder_fn(R, loc, rotz=a + RAD(90), **kw)
    on_wall(-90, 0.0, door, w=1.0, h=1.85, color="plum")
    on_wall(-90 - 48, 1.35, window, w=0.62, h=0.7, shutter="gold")
    on_wall(-90 + 48, 1.35, window, w=0.62, h=0.7, shutter="gold")
    on_wall(-90 + 100, 1.7, window, w=0.5, h=0.55, shutter="gold", flowers=False)
    # lamp by the door
    a = RAD(-90 + 17)
    lantern(R, (math.cos(a) * r, math.sin(a) * r, 2.0), rotz=a + RAD(90))
    # small annex on the right
    A = pivot("annex", (2.0, -0.2, 0), R)
    box("aw", (1.5, 1.6, 1.5), T("plaster2"), A, base=True)
    box("af", (1.6, 1.7, 0.25), T("stone"), A, base=True)
    gable("ar", 1.5, 1.6, 0.8, 0.25, T("wood_d", rim=0.3), A, loc=(0, 0, 1.5))
    gable_rows(1.5, 1.6, 0.8, 0.25, T("#4f321f", rim=0.1), A, (0, 0, 1.5), n=5, thick=0.04)
    window(A, (0, -0.8, 0.85), w=0.55, h=0.55, shutter="red")
    # steps, pumpkin, bush
    for i, (x, y, s) in enumerate([(1.45, -1.95, 0.22), (1.1, -2.0, 0.17)]):
        ellipsoid("pump", s, T("ochre", rim=0.2), R, loc=(x, y, s * 0.8), scale=(1.2, 1.2, 0.85), seg=12, rings=8)
        ellipsoid("pstem", 0.04, T("leaf3", rim=0), R, loc=(x, y, s * 1.5), seg=6, rings=4)
    bush(R, (-1.9, -1.35, 0), r=0.42, seed=21)
    bush(R, (0.85, -1.8, 0), r=0.28, col="leaf2", seed=2)
    for i, (x, y) in enumerate([(0.0, -1.75), (0.1, -2.15)]):
        ellipsoid("stp", 0.22, T("stone"), R, loc=(x, y, 0.02), scale=(1.2, 0.8, 0.18), seg=10, rings=5)
    R.scale = (0.85, 0.85, 0.85)
    return (288, 288), (130, 226)


# ----------------------------------------------------------- trees
def tree_round():
    cell = (192, 256)
    R = pivot("T1")
    frustum("trunk", 0.3, 0.17, 1.6, T("bark"), R, seg=10)
    for a in (0, 120, 240):    # root flare
        ellipsoid("root", 0.14, T("bark"), R, loc=(math.cos(RAD(a)) * 0.22, math.sin(RAD(a)) * 0.22, 0.08), scale=(1.4, 1, 0.7), seg=8, rings=6)
    link_cyl("br1", (0, 0, 1.2), (-0.55, -0.1, 1.9), 0.08, T("bark"), R, seg=6)
    link_cyl("br2", (0, 0, 1.3), (0.55, 0.1, 2.0), 0.08, T("bark"), R, seg=6)
    blobs = [(0, 0, 2.55, 0.95, "leaf1"), (-0.75, -0.1, 2.15, 0.65, "leaf3"), (0.75, 0.15, 2.25, 0.7, "leaf3"),
             (-0.35, -0.4, 2.45, 0.6, "leaf2"), (0.4, -0.35, 2.7, 0.62, "leaf2"), (0.05, 0.2, 3.2, 0.62, "leaf2"),
             (-0.5, 0.35, 2.7, 0.55, "leaf1"), (0.55, 0.4, 2.8, 0.5, "leaf1")]
    for x, y, z, rr, c in blobs:
        ellipsoid("canopy", rr, T(c, rim=0.5), R, loc=(x, y, z), seg=14, rings=10)
    rnd = random.Random(4)
    for i in range(9):    # blossoms/lights
        a, b = rnd.uniform(0, 6.28), rnd.uniform(0.2, 1.2)
        ellipsoid("blossom", 0.05, T(rnd.choice(["#f4c4c4", "gold", "white"]), rim=0), R,
                  loc=(math.cos(a) * 0.9, -abs(math.sin(a)) * 0.8 - 0.1, 2.3 + b), seg=6, rings=5)
    return cell, (96, 226)


def tree_pine():
    cell = (160, 288)
    R = pivot("T2")
    frustum("trunk", 0.2, 0.12, 0.9, T("bark"), R, seg=8)
    tiers = [(0.95, 0.9, 0.6), (0.82, 0.8, 1.2), (0.68, 0.75, 1.75), (0.52, 0.7, 2.25), (0.36, 0.65, 2.7)]
    for i, (rr, hh, z) in enumerate(tiers):
        c = "leaf3" if i % 2 == 0 else "#3c7f52"
        frustum("tier", rr, 0.03, hh, T(c, rim=0.5), R, loc=(0, 0, z), seg=10)
        frustum("tierlip", rr, rr, 0.001, T("#255a3c"), R, loc=(0, 0, z), seg=10)
    ellipsoid("star", 0.07, glow("amber", 3), R, loc=(0, 0, 3.4), seg=8, rings=6)
    return cell, (80, 258)


# ----------------------------------------------------------- small props
def fence():
    cell = (160, 96)
    R = pivot("fence")
    L = 2.4
    for x in (-L / 2, 0, L / 2):
        box("post", (0.15, 0.15, 1.0), T("wood"), R, loc=(x, 0, 0), base=True, bevel=0.02)
        frustum("cap", 0.11, 0.01, 0.1, T("wood_d"), R, loc=(x, 0, 1.0), seg=4, rot=(0, 0, RAD(45)))
    for z in (0.35, 0.72):
        box("rail", (L + 0.1, 0.07, 0.1), T("wood_d"), R, loc=(0, 0.08, z))
    for i in range(6):
        x = -L / 2 + 0.2 + i * (L - 0.4) / 5
        box("picket", (0.17, 0.05, 0.82), T("wood"), R, loc=(x, -0.06, 0.04), base=True, bevel=0.012)
        frustum("ptip", 0.1, 0.005, 0.1, T("wood"), R, loc=(x, -0.06, 0.86), seg=4, rot=(0, 0, RAD(45)), scale=(1, 0.4, 1))
    return cell, (80, 76)


def signpost():
    cell = (96, 144)
    R = pivot("sign")
    box("post", (0.16, 0.16, 2.0), T("wood"), R, base=True, bevel=0.02)
    frustum("cap", 0.14, 0.01, 0.12, T("wood_d"), R, loc=(0, 0, 2.0), seg=4, rot=(0, 0, RAD(45)))
    for z, d, col in ((1.62, 1, "wood_d"), (1.12, -1, "wood")):
        bp = pivot("board", (0, -0.12, z), R, rot=(0, 0, RAD(-6 * d)))
        box("board", (1.05, 0.07, 0.34), T(col), bp, loc=(d * 0.5, 0, 0), bevel=0.012)
        mesh_obj("arrow", [(d * 1.02, -0.0, 0.17), (d * 1.02, 0.0, -0.17), (d * 1.28, 0.0, 0.0)], [(0, 1, 2)], T(col), bp, smooth=False)
        for dx in (0.1, 0.9):
            ellipsoid("nail", 0.025, T("gold", rim=0), bp, loc=(d * dx, -0.04, 0), seg=6, rings=4)
        # carved glowing glyph: a thread loop
        ellipsoid("glyph", 0.045, glow("teal", 4), bp, loc=(d * 0.5, -0.045, 0), scale=(2.4, 0.4, 0.5), seg=8, rings=6)
    return cell, (48, 124)


def lamppost():
    cell = (112, 192)
    R = pivot("lamp")
    iron = T("#3b3346", rim=0.3)
    frustum("base", 0.2, 0.12, 0.3, iron, R, seg=8)
    frustum("pole", 0.07, 0.05, 2.5, iron, R, loc=(0, 0, 0.3), seg=8)
    frustum("collar", 0.11, 0.11, 0.08, iron, R, loc=(0, 0, 1.1), seg=8)
    link_cyl("arm", (0, 0, 2.7), (0, -0.0, 2.8), 0.04, iron, R)
    box("lcage", (0.38, 0.38, 0.5), iron, R, loc=(0, 0, 2.8), base=True)
    box("lglass", (0.3, 0.3, 0.44), glow("amber", 7), R, loc=(0, 0, 2.83), base=True)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box("lpost", (0.04, 0.04, 0.5), iron, R, loc=(sx * 0.18, sy * 0.18, 2.8), base=True)
    frustum("lroof", 0.34, 0.02, 0.28, iron, R, loc=(0, 0, 3.3), seg=4, rot=(0, 0, RAD(45)))
    ellipsoid("lfin", 0.05, T("gold", rim=0), R, loc=(0, 0, 3.6), seg=8, rings=6)
    ellipsoid("halo", 0.55, glow("amber", 2.5, alpha=0.8, soft=True), R, loc=(0, 0, 3.05), seg=14, rings=10)
    ld = bpy.data.lights.new("lamp", 'POINT')
    ld.color, ld.energy, ld.shadow_soft_size = srgb("#ffb860"), 60, 0.2
    lo = bpy.data.objects.new("lamp", ld)
    bpy.context.scene.collection.objects.link(lo)
    lo.parent, lo.location = R, (0, -0.4, 3.0)
    return cell, (56, 172)


def well():
    cell = (160, 192)
    R = pivot("well")
    rnd = random.Random(2)
    n = 12
    for k in range(2):
        for i in range(n):
            a = 2 * math.pi * (i + 0.5 * k) / n
            c = rnd.choice(["stone", "stone_d", "#b8afa6"])
            box("stone", (0.42, 0.3, 0.3), T(c), R, loc=(math.cos(a) * 0.78, math.sin(a) * 0.78, 0.15 + k * 0.3),
                rot=(0, 0, a + RAD(90)), bevel=0.02)
    frustum("water", 0.62, 0.62, 0.01, glow("#3aa6b0", 0.9), R, loc=(0, 0, 0.45), seg=18)
    frustum("inner", 0.64, 0.64, 0.3, T("stone_d"), R, loc=(0, 0, 0.3), caps=(False, False), seg=18)
    for sx in (-1, 1):
        box("wpost", (0.14, 0.14, 1.7), T("wood"), R, loc=(sx * 0.78, 0, 0.6), base=True, bevel=0.015)
    frustum("beam", 0.065, 0.065, 1.7, T("wood_d"), R, loc=(-0.85, 0, 1.55), rot=(0, RAD(90), 0), seg=8)
    # little tile roof
    rp = pivot("wroof", (0, 0, 2.2), R, rot=(0, 0, RAD(90)))
    gable("wtile", 1.1, 1.5, 0.6, 0.2, T("tile", rim=0.4), rp, ends=True)
    gable_rows(1.1, 1.5, 0.6, 0.2, T("#8e3f2c", rim=0.2), rp, (0, 0, 0), n=4, thick=0.04)
    link_cyl("rope", (0, 0, 1.55), (0, 0, 1.0), 0.012, T("leather", rim=0), R, seg=5)
    frustum("bucket", 0.12, 0.09, 0.18, T("wood"), R, loc=(0, 0, 0.82), seg=10)
    return cell, (80, 164)


def stall():
    cell = (224, 192)
    R = pivot("stall")
    # counter
    box("counter", (2.5, 0.9, 0.85), T("wood"), R, loc=(0, 0, 0), base=True, bevel=0.02)
    box("ctop", (2.7, 1.0, 0.1), T("wood_d"), R, loc=(0, 0, 0.85), base=True)
    for z in (0.3, 0.6):
        box("plank", (2.5, 0.02, 0.03), T("wood_d", rim=0), R, loc=(0, -0.46, z))
    # posts
    for sx in (-1, 1):
        for sy in (-1, 1):
            box("post", (0.1, 0.1, 2.3), T("wood"), R, loc=(sx * 1.3, sy * 0.45, 0), base=True)
    # striped awning, sloping down to the front
    stripes = 10
    sw = 2.9 / stripes
    zb, zf = 2.55, 2.15
    yb, yf = 0.7, -0.85
    for i in range(stripes):
        x0, x1 = -1.45 + i * sw, -1.45 + (i + 1) * sw
        col = "red" if i % 2 == 0 else "cream"
        mesh_obj("stripe", [(x0, yb, zb), (x1, yb, zb), (x1, yf, zf), (x0, yf, zf)], [(0, 1, 2, 3)], T(col, rim=0.4), R, smooth=False)
        # scalloped valance
        mesh_obj("val", [(x0, yf, zf), (x1, yf, zf), ((x0 + x1) / 2, yf - 0.03, zf - 0.22)], [(0, 2, 1)], T(col, rim=0.4), R, smooth=False)
    # goods
    for i, (x, c) in enumerate([(-0.9, "red"), (-0.6, "red"), (-0.75, "gold")]):
        ellipsoid("apple", 0.1, T(c, rim=0.3), R, loc=(x, -0.1, 1.05), seg=10, rings=8)
    frustum("basket", 0.35, 0.28, 0.22, T("leather"), R, loc=(-0.75, -0.1, 0.95), seg=12)
    for i in range(7):
        a = i * 0.9
        ellipsoid("fruit", 0.095, T(["red", "ochre", "gold"][i % 3], rim=0.3), R,
                  loc=(-0.75 + math.cos(a) * 0.15, -0.1 + math.sin(a) * 0.12, 1.2 + (i % 2) * 0.05), seg=10, rings=8)
    box("cloth", (0.9, 0.5, 0.04), T("teal_roof"), R, loc=(0.55, -0.05, 0.95))
    for i in range(3):   # jars with soft glow
        frustum("jar", 0.11, 0.1, 0.24, glow("window", 2.5), R, loc=(0.2 + i * 0.35, -0.05, 0.98), seg=10)
        frustum("jlid", 0.1, 0.1, 0.04, T("leather_d", rim=0), R, loc=(0.2 + i * 0.35, -0.05, 1.22), seg=10)
    crate(R, (1.75, -0.4, 0.0), 0.5, RAD(10))
    ellipsoid("melon", 0.2, T("leaf1", rim=0.3), R, loc=(1.75, -0.4, 0.7), seg=10, rings=8)
    mesh_obj("sign", [(-0.5, -0.5, 1.55), (0.5, -0.5, 1.55), (0.5, -0.5, 1.9), (-0.5, -0.5, 1.9)], [(0, 1, 2, 3)], T("plaster"), R, smooth=False)
    ellipsoid("signglyph", 0.06, glow("teal", 4), R, loc=(0, -0.52, 1.72), scale=(3, 0.3, 1), seg=8, rings=6)
    lantern(R, (1.3, -0.45, 2.3))
    return cell, (104, 168)


BUILDERS = {
    "cottage_a": cottage_a, "cottage_b": cottage_b, "cottage_c": cottage_c,
    "tree_round": tree_round, "tree_pine": tree_pine,
    "fence": fence, "signpost": signpost, "lamppost": lamppost, "well": well, "market_stall": stall,
}


def main():
    a = script_args()
    rawdir = a[0]
    names = a[1:] or list(BUILDERS)
    import time
    out = os.path.join(rawdir, "props")
    os.makedirs(out, exist_ok=True)
    mp = os.path.join(out, "props_meta.json")
    meta = json.load(open(mp)) if os.path.exists(mp) else {}
    for nm in names:
        t0 = time.time()
        reset_scene()
        setup_render(samples=24)
        setup_world_and_lights()
        # builders return (cell, anchor) but need camera first -> build, then camera
        (cell, anchor) = BUILDERS[nm]()
        setup_camera(cell[0], cell[1], anchor=anchor)
        bpy.context.view_layer.update()
        render_to(os.path.join(out, nm + ".png"))
        meta[nm] = {"cell": cell, "anchor": anchor}
        print(f"PROP {nm}: {time.time() - t0:.1f}s")
    json.dump(meta, open(mp, "w"), indent=1)


main()
