"""Six distinct village buildings with procedural textures (oblique camera, 56 px/unit).

blender -b --python buildings.py -- <rawdir> [name ...]
Writes <rawdir>/env/<name>.png (+ mill_sails.png) and <rawdir>/env/buildings_meta.json.
Anchor = projected footprint centre (world origin); front = pixel row of the front ground edge;
smoke = chimney emitter points in pixels of the raw canvas (pack_env.py trims and shifts them).
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


def gable_rows_tex():
    pass


def ridge_cap(parent, w, z, mat, loc_y=0.0, r=0.1):
    return frustum("ridgecap", r, r, w, mat, parent, loc=(-w / 2, loc_y, z), rot=(0, RAD(90), 0), seg=8)


def eave_trim(parent, w, d, ov, z, mat, r=0.08):
    W, D = w / 2 + ov, d / 2 + ov
    for s in (-1, 1):
        frustum("eave", r, r, 2 * W, mat, parent, loc=(-W, s * D, z), rot=(0, RAD(90), 0), seg=8)


def roof_z_at(y, wall_h, roof_h, d, ov):
    D = d / 2 + ov
    return wall_h + roof_h * (1 - abs(y) / D)


# =============================================================== (a) Shoshana's cottage
def cottage_shoshana():
    R = pivot("A")
    w, d, wh, rh, ov = 4.2, 2.8, 2.85, 0.95, 0.4
    box("found", (w + 0.16, d + 0.16, 0.34), ST("#b0a49a", "#8c8088", scale=2.4), R, base=True)
    wall = PL("#f2cfa6", "#e8b790", wear=0.55, moss=0.35)
    box("walls", (w, d, wh - 0.3), wall, R, loc=(0, 0, 0.34), base=True)
    # painted timber + painted flower frieze under the eaves
    tm = WDT("#7a4a30", "#6a3c26")
    for x in (-w / 2 + 0.05, w / 2 - 0.05, 0.9):
        box("post", (0.14, 0.07, wh - 0.3), tm, R, loc=(x, -d / 2 - 0.02, 0.34), base=True)
    box("beamt", (w, 0.07, 0.14), tm, R, loc=(0, -d / 2 - 0.02, wh - 0.18))
    box("beamb", (w, 0.07, 0.12), tm, R, loc=(0, -d / 2 - 0.02, 0.5))
    rnd = random.Random(4)
    for i in range(18):
        x = -w / 2 + 0.3 + i * (w - 0.6) / 17
        ellipsoid("pf", 0.05, toon(["red", "#4f7ad8", "gold", "white"][i % 4], rim=0.2), R, loc=(x, -d / 2 - 0.07, wh - 0.38),
                  scale=(1, 0.4, 1), seg=8, rings=6)
        ellipsoid("pl", 0.04, toon("leaf1", rim=0), R, loc=(x + 0.11, -d / 2 - 0.07, wh - 0.42), scale=(1.4, 0.4, 0.7), seg=6, rings=4)
    # roof: knitted terracotta
    rz = wh - 0.05
    roof = tex_toon("knit", "#e07a3c", "#c9622e", scale=7.0, plane="xy", bump=1.0, wear=0.3, moss=0.2)
    sloped_roof("roof", w, d, rh, ov, roof, R, loc=(0, 0, rz))
    ridge_cap(R, w + 2 * ov + 0.04, rz + rh, FAB("weave", "#f3e4c4", "#4f7ad8", scale=16, plane="xy"), r=0.11)
    eave_trim(R, w, d, ov, rz + 0.02, FAB("weave", "#f3e4c4", "#e8884a", scale=14, plane="xy"), r=0.1)
    # chimney (soot) with pot
    box("chim", (0.62, 0.62, 2.2), ST("#a8a09a", "#7c7480", soot=0.8, scale=3), R, loc=(1.35, 0.35, 2.4), base=True)
    box("chimcap", (0.78, 0.78, 0.14), ST("#8c848a", "#6c6470", scale=3), R, loc=(1.35, 0.35, 4.6), base=True)
    frustum("pot", 0.2, 0.17, 0.3, tex_toon("plain", "#b4553a", "#8e3f2c", scale=3, bump=0, wear=0.4), R, loc=(1.35, 0.35, 4.74), seg=10)
    # yarn-pattern stripes on the chimney (painted band)
    box("chband", (0.64, 0.64, 0.12), FAB("weave", "#4f7ad8", "#f3e4c4", scale=22), R, loc=(1.35, 0.35, 3.5), base=True)
    # door + windows
    door(R, (-1.05, -d / 2, 0.0), w=0.95, h=1.75, color="#2f7d6f")
    lantern2(R, (-0.2, -d / 2, 1.95))
    window(R, (0.95, -d / 2, 1.3), w=0.9, h=0.8, shutter="#4f9a9a", curtain="#c44b3f")
    window(R, (-1.85, -d / 2, 1.4), w=0.55, h=0.6, shutter="#c44b3f", flowers=True, curtain="#f3e4c4")
    window(R, (1.85, -d / 2, 1.3), w=0.55, h=0.7, shutter="#4f9a9a", curtain="#c44b3f")
    # dormer
    dp = pivot("dormer", (0.1, -0.55, roof_z_at(-0.55, wh, rh, d, ov) - 0.1), R)
    box("dbody", (0.95, 0.6, 0.7), wall, dp, base=True)
    sloped_roof("droof", 0.95, 0.6, 0.38, 0.12, roof, dp, loc=(0, 0, 0.7), ends=True, ridge_x=False)
    box("dframe", (0.62, 0.05, 0.5), toon("#f3e4c4", rim=0.1), dp, loc=(0, -0.31, 0.38))
    box("dpane", (0.5, 0.05, 0.4), glow("window", 3.4), dp, loc=(0, -0.335, 0.38))
    # hanging sign: wool ball + needles
    sp = pivot("sign", (-1.9, -d / 2 - 0.05, 2.0), R)
    link_cyl("arm", (0, 0, 0.25), (-0.0, -0.55, 0.25), 0.03, tm, sp, seg=5)
    box("plate", (0.5, 0.05, 0.5), WD("#c98d4e", "#a96d36", scale=4, bump=0.5), sp, loc=(0, -0.6, -0.05))
    yarn_ball(sp, (0, -0.68, -0.28), 0.17, "#4f7ad8", "#f3e4c4", needles=True)
    # doorside: big wool ball with needles, basket of wool, flowerpots, bench
    yarn_ball(R, (-2.35, -1.75, 0), 0.4, "#c44b3f", "#f3e4c4", needles=True)
    frustum("basket", 0.34, 0.28, 0.3, FAB("weave", "#b07a46", "#8a5a30", scale=14), R, loc=(-0.2, -1.8, 0), seg=14)
    for i, (dx, dy, c) in enumerate([(-0.1, -0.05, "#4f7ad8"), (0.1, 0.03, "#e8b04a"), (-0.02, 0.1, "#35b39a"), (0.14, -0.08, "#c44b3f")]):
        ellipsoid("wool", 0.14, FAB("weave", c, "#f3e4c4", scale=12), R, loc=(-0.2 + dx, -1.8 + dy, 0.38 + (i % 2) * 0.06), seg=12, rings=8)
    plant_pot(R, (0.35, -1.7, 0), 0.2, 0.3, kind="flower", seed=4)
    plant_pot(R, (-1.9, -1.55, 0), 0.22, 0.34, kind="fern", seed=2, pot="#d68f3a")
    bush(R, (1.75, -1.7, 0), r=0.4, seed=5)
    bush(R, (-2.55, -0.9, 0), r=0.3, col="leaf2", seed=9)
    for (x, y) in [(-1.05, -2.0), (-0.95, -2.45), (-1.1, -2.9)]:
        ellipsoid("stp", 0.24, ST(scale=3, bump=0.5), R, loc=(x, y, 0.02), scale=(1.2, 0.8, 0.2), seg=10, rings=5)
    # laundry line (right) with the long blue scarf
    px0, px1, py = 2.2, 4.0, -1.5
    for x in (px0, px1):
        frustum("pole", 0.05, 0.05, 2.1, WDT(), R, loc=(x, py, 0), seg=6)
    pts = [(px0 + (px1 - px0) * t / 10, py, 1.95 - 0.12 * math.sin(math.pi * t / 10)) for t in range(11)]
    tube("line", pts, 0.012, toon("#d9c9a8", rim=0.2), R)
    sx = 2.75
    n = 12
    sc_mat = FAB("knit", "#3a6ad0", "#5b8ae8", scale=18, plane="xz", bump=1.0)
    st_mat = FAB("knit", "#f3e4c4", "#d9c9a8", scale=18, plane="xz", bump=1.0)
    sw = 0.42
    # scarf hangs folded over the line: two panels, long fringe, cream stripes
    for side, (yy, zdrop) in enumerate([(py - 0.03, 1.45), (py + 0.03, 1.2)]):
        sag = lambda t: 1.95 - 0.12 * math.sin(math.pi * ((sx - px0 + t * sw) / (px1 - px0)) * 1.0)
        v, f = [], []
        N = 10
        for i in range(N + 1):
            x0 = sx + i * (0.06) - 0.3
            zt = 1.95 - 0.12 * math.sin(math.pi * (x0 - px0) / (px1 - px0)) - 0.015
            v += [(x0, yy, zt), (x0 + 0.03 * math.sin(i * 0.9), yy - 0.02 * side, zt - zdrop + 0.05 * math.sin(i * 1.3))]
        for i in range(N):
            f.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
        mesh_obj("scarf", v, f, sc_mat if side == 0 else sc_mat, R, smooth=False)
        # stripe bands
        for bz in (0.35, 0.55):
            vv = [(v[2 * i][0], yy - 0.004, v[2 * i][2] - zdrop * bz) for i in range(N + 1)]
            vv2 = [(p[0], p[1], p[2] - 0.07) for p in vv]
            mesh_obj("band", [*vv, *vv2], [(i, i + 1, N + 1 + i + 1, N + 1 + i) for i in range(N)], st_mat, R, smooth=False)
    for i in range(9):   # fringe
        x0 = sx - 0.3 + i * 0.075
        box("fringe", (0.025, 0.02, 0.18), toon("#f3e4c4", rim=0.2), R, loc=(x0, py - 0.04, 1.95 - 1.45 - 0.07))
    # other laundry: small socks and a cloth
    box("cloth", (0.32, 0.03, 0.5), FAB("weave", "#f3e4c4", "#e8b04a", scale=20), R, loc=(3.45, py, 1.65))
    for x, c in ((3.1, "#c44b3f"), (3.2, "#e8b04a")):
        box("sock", (0.1, 0.03, 0.3), toon(c, rim=0.2), R, loc=(x + 0.55, py, 1.78))
    # the cat: grey tabby sitting on the roof next to the chimney
    cy = -0.35
    cz = roof_z_at(cy, wh, rh, d, ov) + 0.02
    cat = pivot("cat", (-0.9, cy, cz), R, rot=(RAD(-0), 0, 0))
    gm = tex_toon("stripes", "#8e8a98", "#6e6a7a", scale=9, plane="xz", bump=0.2, rim=0.5, ao=0.3)
    ellipsoid("body", 0.22, gm, cat, loc=(0, 0.02, 0.24), scale=(0.9, 0.9, 1.25), seg=14, rings=10)
    ellipsoid("head", 0.15, toon("#9a96a6", rim=0.5), cat, loc=(0, -0.05, 0.55), seg=14, rings=10)
    for s in (-1, 1):
        frustum("ear", 0.06, 0.0, 0.11, toon("#8e8a98", rim=0.4), cat, loc=(s * 0.09, -0.05, 0.64), seg=3, rot=(0, s * RAD(12), 0))
        ellipsoid("eye", 0.025, glow("#ffd86a", 5), cat, loc=(s * 0.06, -0.18, 0.57), seg=6, rings=4)
    ellipsoid("nose", 0.02, toon("#e8a0a0", rim=0), cat, loc=(0, -0.2, 0.52), seg=6, rings=4)
    tube("tail", [(0.12, 0.05, 0.05), (0.32, 0.0, 0.05), (0.42, -0.1, 0.2), (0.38, -0.12, 0.42)], 0.045, gm, cat)
    # a blue thread from the cat down to the eave (the cat "walks on the thread")
    if EL.TRUTH:
        from buildings_b import roof_hole, sagging_threads
        roof_hole(R, -0.3, -0.5, wh, rh, d, ov, s=0.7, rz0=wh - 0.05)
        roof_hole(R, 1.5, -0.9, wh, rh, d, ov, s=0.5, rz0=wh - 0.05)
        cobweb(R, (-1.4, -d / 2 - 0.1, wh - 0.15), 0.45)
        sagging_threads(R, [(-1.0, -d / 2 - 0.3, wh + 0.2), (0.7, -d / 2 - 0.3, wh + 0.1)], seed=2)
        dead_plant(R, (-1.9, -1.55, 0), 0.6, seed=3)
    return dict(cell=(448, 448), anchor=(224, 330), smoke=[(1.35, 0.35, 4.95)])


# =============================================================== (b) clinic
def clinic():
    R = pivot("B")
    w, d, wh = 3.4, 3.0, 3.1
    stone = ST("#bdb8b0", "#9aa3a0", scale=2.0, wear=0.5, moss=0.5)
    box("found", (w + 0.2, d + 0.2, 0.4), ST("#9a948c", "#7c7882", scale=2.2, moss=0.7), R, base=True)
    box("walls", (w, d, wh), stone, R, loc=(0, 0, 0.0), base=True)
    # white plaster upper band with green trim
    box("upper", (w + 0.06, d + 0.06, 0.55), PL("#f3f0e4", "#e2e6d8", wear=0.2), R, loc=(0, 0, wh - 0.55), base=True)
    gm = WD("#3f8f6f", "#357a5e", scale=3, bump=0.5)
    box("trimb", (w + 0.1, d + 0.1, 0.1), gm, R, loc=(0, 0, wh - 0.6), base=True)
    # copper (verdigris) hipped roof
    vr = tex_toon("tiles", "#4f9a8c", "#3f8478", scale=4.0, plane="xy", bump=1.0, wear=0.6, moss=0.15)
    hip_roof("roof", w + 0.5, d + 0.5, 0.85, vr, R, loc=(0, 0, wh), ridge_frac=0.5)
    # roof lantern (glass cupola) on top
    box("cupb", (0.8, 0.8, 0.35), gm, R, loc=(0, 0, wh + 0.8), base=True)
    box("cupg", (0.7, 0.7, 0.45), glow("#bff0d8", 2.6), R, loc=(0, 0, wh + 0.85), base=True)
    hip_roof("cupr", 1.0, 1.0, 0.55, vr, R, loc=(0, 0, wh + 1.3), ridge_frac=0.0)
    frustum("fin", 0.03, 0.01, 0.4, toon("gold", rim=0.5), R, loc=(0, 0, wh + 1.8), seg=5)
    ellipsoid("finb", 0.07, glow("#7ff0c0", 5), R, loc=(0, 0, wh + 1.75), seg=8, rings=6)
    # chimney small
    box("chim", (0.4, 0.4, 1.2), BR("#a8a09a", "#8c848a", scale=3), R, loc=(1.15, 0.5, wh + 0.6), base=True)
    # glasshouse bay (left) with white frame
    gx = -2.5
    gp = pivot("glass", (gx, -0.2, 0), R)
    box("gbase", (1.8, 1.9, 0.45), ST("#a8a09a", "#8c848a", scale=3, moss=0.8), gp, base=True)
    fr = toon("#f3f0e4", rim=0.2)
    box("gglass", (1.6, 1.7, 1.7), glow("#a8f0d0", 1.5, alpha=0.85), gp, loc=(0, 0, 0.45), base=True)
    for i in range(5):
        box("gmul", (0.05, 0.05, 1.7), fr, gp, loc=(-0.8 + i * 0.4, -0.86, 0.45), base=True)
    for z in (0.45, 0.95, 1.45, 2.15):
        box("gbar", (1.7, 0.05, 0.05), fr, gp, loc=(0, -0.86, z))
    hip_roof("groof", 1.9, 2.0, 0.65, vr, gp, loc=(0, 0, 2.15), ridge_frac=0.6)
    # plants seen through the glass
    for i, x in enumerate((-0.5, 0.0, 0.5)):
        ellipsoid("gp", 0.28, toon(["leaf1", "leaf2", "leaf3"][i], rim=0.3), gp, loc=(x, -0.4, 0.9 + (i % 2) * 0.2), scale=(1, 0.8, 1.4), seg=10, rings=8)
    # door (white with green), windows with arched frames
    door(R, (0.35, -d / 2, 0.0), w=0.95, h=2.0, color="#f3f0e4", frame="#3f8f6f", window_=True)
    for wx in (1.2,):
        window(R, (wx + 0.3, -d / 2, 1.7), w=0.7, h=0.95, frame="#f3f0e4", shutter="#3f8f6f", curtain="#bfe8d0", light="#e8ffe0",
               flowers=False)
    # porch with pillars & hanging herbs
    box("porch", (3.2, 0.95, 0.12), ST("#c2bdb4", "#a7a49e", scale=3, bump=0.6), R, loc=(0.6, -d / 2 - 0.5, 0.06))
    for x in (-0.95, 2.1):
        frustum("pil", 0.09, 0.09, 2.5, WD("#f3f0e4", "#e2e6d8", scale=3, along="v"), R, loc=(x, -d / 2 - 0.85, 0.12), seg=8)
    box("pbeam", (3.2, 0.14, 0.14), gm, R, loc=(0.6, -d / 2 - 0.85, 2.6))
    sloped_roof("proof", 3.2, 0.85, 0.3, 0.12, vr, R, loc=(0.6, -d / 2 - 0.45, 2.55), ridge_x=True, ends=True)
    rnd = random.Random(11)
    hanks = ["#6f9a3c", "#8fb04a", "#a8a04a", "#7a5a8a", "#c9a24a", "#4f8a5a"]
    for i in range(8):   # dried herb bundles
        x = 0.3 + i * 0.24
        link_cyl("str", (x, -d / 2 - 0.85, 2.6), (x, -d / 2 - 0.85, 2.3), 0.008, toon("#d9c9a8", rim=0), R, seg=4)
        ellipsoid("herb", 0.09, toon(hanks[i % 6], rim=0.3), R, loc=(x, -d / 2 - 0.85, 2.2), scale=(0.8, 0.8, 1.9), seg=8, rings=6)
        ellipsoid("herb2", 0.06, toon(hanks[(i + 2) % 6], rim=0.3), R, loc=(x + 0.04, -d / 2 - 0.9, 2.08), scale=(0.8, 0.8, 1.5), seg=8, rings=6)
    for i, x in enumerate((0.5, 0.85, 1.5, 1.9)):   # hanging jars
        link_cyl("jstr", (x, -d / 2 - 0.85, 2.6), (x, -d / 2 - 0.85, 2.0), 0.008, toon("#d9c9a8", rim=0), R, seg=4)
        jar(R, (x, -d / 2 - 0.85, 1.76), 0.1, 0.22, content=["#d68f3a", "#6fa04a", "#c44b3f", "#8a6ac8"][i], gl=True)
    # green lantern (glow green)
    lantern2(R, (-0.35, -d / 2 - 0.85, 2.55), color="#5fe0a0", glow_s=7, halo=0.22)
    # sign: round plaque with mortar-and-leaf
    sp = pivot("sign", (1.62, -d / 2 - 0.05, 2.95), R)
    link_cyl("arm", (0, 0, 0), (0, -0.6, 0), 0.03, gm, sp, seg=5)
    link_cyl("ch", (0, -0.6, 0), (0, -0.6, -0.2), 0.012, toon("leather_d", rim=0), sp, seg=4)
    pl = pivot("plaque", (0, -0.6, -0.65), sp)
    frustum("disc", 0.45, 0.45, 0.07, WD("#f3f0e4", "#dfe6d6", scale=3, along="v"), pl, rot=(RAD(90), 0, 0), seg=24)
    frustum("ring", 0.47, 0.47, 0.05, gm, pl, loc=(0, 0.02, 0), rot=(RAD(90), 0, 0), seg=24)
    # mortar bowl (half sphere) + pestle + leaf
    ellipsoid("bowl", 0.19, toon("#6a6a78", rim=0.6), pl, loc=(-0.02, -0.07, -0.08), scale=(1.2, 0.4, 0.8), seg=14, rings=8)
    link_cyl("pestle", (0.05, -0.1, -0.04), (0.27, -0.1, 0.24), 0.04, toon("#c9bfae", rim=0.5), pl, seg=8)
    ellipsoid("leaf", 0.15, toon("#3fa05a", rim=0.5), pl, loc=(-0.15, -0.09, 0.2), scale=(0.45, 0.2, 1.0), rot=(0, RAD(-25), 0), seg=10, rings=8)
    ellipsoid("leaf2", 0.11, toon("#6cb257", rim=0.5), pl, loc=(0.02, -0.09, 0.28), scale=(0.4, 0.2, 1.0), rot=(0, RAD(15), 0), seg=10, rings=8)
    # herb garden beds in front
    soil = toon("#4a3426", rim=0)
    hz = ["#4f9a4f", "#6cb257", "#2f6b48", "#8fb04a", "#7a5a9a", "#c79ae8"]
    for bi, (bx, by, bw) in enumerate([(-1.9, -2.5, 1.5), (-0.1, -2.9, 1.4), (1.7, -2.5, 1.5)]):
        bp = pivot("bed", (bx, by, 0), R)
        box("frame", (bw, 0.7, 0.2), WD("#9a6238", "#7d4a2a", scale=3, bump=0.5), bp, loc=(0, 0, 0.1))
        box("soil", (bw - 0.1, 0.6, 0.04), soil, bp, loc=(0, 0, 0.21))
        for k in range(14):
            x = -bw / 2 + 0.15 + (k % 7) * (bw - 0.3) / 6
            y = -0.15 + (k // 7) * 0.3
            c = hz[(k + bi * 2) % 6]
            rr = 0.1 + 0.04 * ((k * 7) % 3)
            ellipsoid("herb", rr, toon(c, rim=0.35), bp, loc=(x, y, 0.28 + rr * 0.5), scale=(1, 1, 1.2), seg=8, rings=6)
        if bi == 0:
            for k in range(4):   # lavender
                x = -bw / 2 + 0.25 + k * 0.3
                for j in range(3):
                    link_cyl("lav", (x + j * .03, -0.2, 0.25), (x + j * .05, -0.2, 0.62), 0.008, toon("leaf3", rim=0), bp, seg=4)
                    ellipsoid("lv", 0.035, toon("#a07ad8", rim=0.3), bp, loc=(x + j * .05, -0.2, 0.64), scale=(0.7, 0.7, 2), seg=6, rings=4)
    # stepping path
    for (x, y) in [(0.35, -2.1), (0.3, -2.5)]:
        ellipsoid("stp", 0.26, ST(scale=3, bump=0.5), R, loc=(x, y, 0.02), scale=(1.2, 0.8, 0.2), seg=10, rings=5)
    barrel(R, (-0.95, -2.2, 0), 0.28, 0.6, col="#9aa38a")
    plant_pot(R, (2.7, -1.7, 0), 0.24, 0.4, seed=6, kind="flower", pot="#6aa090")
    if EL.TRUTH:
        from buildings_b import roof_hole, sagging_threads
        roof_hole(R, -0.8, -0.4, wh, 1.05, d + 0.6, 0.0, s=0.6, rz0=wh)
        cobweb(R, (0.0, -d / 2 - 0.9, 2.5), 0.5)
        sagging_threads(R, [(-0.9, -d / 2 - 0.9, 2.3), (1.9, -d / 2 - 0.9, 2.3)], seed=5)
        dead_plant(R, (-1.9, -2.5, 0.2), 0.5, seed=4)
    return dict(cell=(448, 448), anchor=(224, 340), smoke=[(1.15, 0.5, wh + 1.25)])


BUILDERS = {"cottage_shoshana": cottage_shoshana, "clinic": clinic}


def main():
    import buildings_b
    BUILDERS.update(buildings_b.BUILDERS)
    a = script_args()
    rawdir = a[0]
    truth = "truth" in a
    a = [x for x in a if x != "truth"]
    names = a[1:] or [n for n in BUILDERS if truth or n not in buildings_b.TRUTH_ONLY]
    out = os.path.join(rawdir, "env")
    os.makedirs(out, exist_ok=True)
    mp = os.path.join(out, "buildings_meta.json")
    meta = json.load(open(mp)) if os.path.exists(mp) else {}
    sfx = "_truth" if truth else ""
    for nm in names:
        t0 = time.time()
        reset_env()
        EL.set_truth(truth)
        env_lights()
        r = BUILDERS[nm]()
        cell, anchor = r["cell"], r["anchor"]
        render_scene(cell, anchor, os.path.join(out, nm + sfx + ".png"), samples=24)
        info = {"cell": cell, "anchor": anchor}
        info["smoke"] = [[round(project(x, y, z, anchor)[0], 1), round(project(x, y, z, anchor)[1], 1)] for (x, y, z) in r.get("smoke", [])]
        if "extra" in r:
            info["extra"] = r["extra"]
        meta[nm + sfx] = info
        print(f"BUILDING {nm}{sfx}: {time.time() - t0:.1f}s")
    json.dump(meta, open(mp, "w"), indent=1)


if __name__ == "__main__":
    main()
