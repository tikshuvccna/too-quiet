"""World-2 props (24): rocks, standing stones, reeds, boat, dock, hay, trees, stalls, fountain, signpost, crates, barrel,
lamp, scarecrow, flower bush, mushroom ring, bridge.  Same pipeline as buildings_c (auto-fit cell, anchor = ground contact point).
blender -b --python props_b.py -- <rawdir> [truth] [name ...]   -> <rawdir>/env2p/<name>[_truth].png + props2_meta.json
Truth variants exist for: fairy_door_tree giant_tree_hollow lantern_post_b flower_bush mushroom_ring reeds.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w2lib import *  # noqa
import env_lib as EL

TRUTH_PROPS = ["fairy_door_tree", "giant_tree_hollow", "lantern_post_b", "flower_bush", "mushroom_ring", "reeds"]


def rock(parent, loc, r, scale=(1.2, 1.0, 0.75), rot=0.0, col="#9a949c", moss=0.5, seed=0):
    return ellipsoid("rock", r, ST(col, "#6f6874", scale=3, bump=0.9, moss=moss, seed=seed), parent, loc=(loc[0], loc[1], loc[2] + r * scale[2] * 0.7),
                     scale=scale, rot=(0, 0, rot), seg=10, rings=7)


def rock_a():
    R = pivot("p")
    rock(R, (0, 0, 0), 0.7, (1.2, 1.0, 0.8), 0.3)
    rock(R, (0.85, -0.25, 0), 0.4, (1.1, 1.0, 0.8), 1.0, seed=2)
    rock(R, (-0.7, -0.45, 0), 0.3, (1.0, 1.0, 0.7), 2.0, "#8f8a96", seed=3)
    bush(R, (-0.1, 0.55, 0), r=0.22, flowers=False, seed=3)
    return {}


def rock_b():
    R = pivot("p")
    slab = ST("#8d8794", "#6f6874", scale=2.6, bump=1.0, moss=0.5)
    frustum("slab", 0.7, 0.45, 1.7, slab, R, seg=6, scale=(1.0, 0.6, 1.0), loc=(0, 0, 0))
    ellipsoid("cap", 0.5, slab, R, loc=(-0.05, 0, 1.65), scale=(1.0, 0.65, 0.5), seg=10, rings=6)
    rock(R, (0.9, -0.3, 0), 0.4, (1.2, 1.0, 0.7), 0.5, seed=4)
    rock(R, (-0.8, -0.35, 0), 0.28, (1.1, 1.0, 0.8), 1.5, "#a29aa4", seed=5)
    rock(R, (0.3, -0.7, 0), 0.2, (1.1, 1.0, 0.8), 0.2, seed=6)
    return {}


def standing_stone():
    R = pivot("p")
    st = ST("#8a8696", "#6c6878", scale=2.4, bump=1.0, moss=0.5, wear=0.8)
    frustum("st", 0.62, 0.38, 2.7, st, R, seg=7, scale=(1.0, 0.62, 1.0))
    ellipsoid("top", 0.34, st, R, loc=(0, 0, 2.65), scale=(1.0, 0.65, 0.7), seg=8, rings=6)
    for k in range(4):
        a = k * 1.6
        ellipsoid("base", 0.25, st, R, loc=(math.cos(a) * 0.55, math.sin(a) * 0.4, 0.1), scale=(1, 1, 0.6), seg=8, rings=5)
    th = glow("#35d3b0", 3.2)
    # glowing engraving: spiral + vertical line + notches on the front face (y ~ -0.38*0.62 at mid height)
    spi = [(math.cos(t) * (0.05 + t * 0.025), -0.27, 1.55 + math.sin(t) * (0.05 + t * 0.025)) for t in [k * 0.35 for k in range(26)]]
    tube("spi", spi, 0.018, th, R)
    tube("v", [(0, -0.27, 1.0), (0, -0.27, 0.45)], 0.018, th, R)
    tube("v2", [(0, -0.25, 2.0), (0, -0.25, 2.35)], 0.018, th, R)
    for z in (0.7, 0.9):
        tube("n", [(-0.12, -0.27, z), (0.12, -0.27, z)], 0.016, th, R)
    ellipsoid("eh", 0.5, glow("#35d3b0", 0.8, alpha=0.2, soft=True), R, loc=(0, -0.3, 1.5), scale=(1, 0.3, 1.2), seg=10, rings=8)
    return {}


def stone_circle():
    R = pivot("p")
    st = ST("#8a8696", "#6c6878", scale=2.4, bump=1.0, moss=0.5, wear=0.8)
    n = 8
    for k in range(n):
        a = 2 * math.pi * k / n + 0.2
        x, y = math.cos(a) * 2.2, math.sin(a) * 2.2
        h = 1.2 + 0.4 * ((k * 5) % 3) / 2
        p = pivot("s", (x, y, 0), R, rot=(0, 0, a + 1.57))
        frustum("st", 0.38, 0.26, h, st, p, seg=6, scale=(1.0, 0.55, 1.0))
        ellipsoid("t", 0.22, st, p, loc=(0, 0, h - 0.02), scale=(1.0, 0.6, 0.6), seg=8, rings=5)
        if k % 2 == 0:
            tube("g", [(0, -0.16, h * 0.55), (0, -0.16, h * 0.3)], 0.014, glow("#35d3b0", 2.6), p)
            tube("g2", [(-0.07, -0.16, h * 0.45), (0.07, -0.16, h * 0.45)], 0.014, glow("#35d3b0", 2.6), p)
    ellipsoid("alt", 0.7, ST("#a29aa4", "#7a7484", scale=2.4, bump=0.8, moss=0.3), R, loc=(0, 0, 0.12), scale=(1.4, 1.0, 0.3), seg=12, rings=6)
    ellipsoid("ah", 0.9, glow("#35d3b0", 0.6, alpha=0.2, soft=True), R, loc=(0, 0, 0.1), scale=(1.4, 1.0, 0.25), seg=10, rings=6)
    return {}


def reeds():
    R = pivot("p")
    rnd = random.Random(4)
    lm = [toon("#7a9a4a", rim=0.3), toon("#5a8a3e", rim=0.3), toon("#8aa855", rim=0.3)]
    for i in range(26):
        a = rnd.uniform(0, 6.28)
        rad = rnd.uniform(0, 0.8)
        x, y = math.cos(a) * rad, math.sin(a) * rad * 0.6
        h = rnd.uniform(1.0, 2.0)
        lean = (rnd.uniform(-0.25, 0.25), rnd.uniform(-0.1, 0.1))
        link_cyl("b", (x, y, 0), (x + lean[0] * h, y + lean[1] * h, h), 0.02, lm[i % 3], R, seg=4, r2=0.006)
        if i % 5 == 0:
            ellipsoid("cat", 0.06, toon("#6a4a30", rim=0.3), R, loc=(x + lean[0] * h * 0.85, y + lean[1] * h * 0.85, h * 0.85), scale=(1, 1, 2.8), seg=6, rings=4)
    for k in range(4):
        a = k * 1.6
        ellipsoid("mud", 0.3, toon("#5a4a3a", rim=0.1), R, loc=(math.cos(a) * 0.6, math.sin(a) * 0.4, 0.02), scale=(1.4, 1, 0.12), seg=8, rings=4)
    return {}


def boat():
    R = pivot("p")
    L, Wd = 1.75, 0.68
    N, M = 14, 9
    outer, inner = [], []
    for i in range(N + 1):
        x = -L + 2 * L * i / N
        f = math.sqrt(max(0.0, 1 - (x / L) ** 2))
        zg = 0.55 + 0.18 * (abs(x) / L) ** 2
        w = Wd * (f ** 0.8)
        dep = 0.42 * f ** 0.6
        for j in range(M + 1):
            t = math.pi * j / M
            outer.append((x, -w * math.cos(t), zg - dep * math.sin(t)))
            inner.append((x, -(w - 0.06) * math.cos(t), zg - (dep - 0.06) * math.sin(t) + 0.02))
    faces = [(i * (M + 1) + j, i * (M + 1) + j + 1, (i + 1) * (M + 1) + j + 1, (i + 1) * (M + 1) + j) for i in range(N) for j in range(M)]
    mesh_obj("hull", outer, faces, WD("#9a6a3c", "#7a4e2a", scale=3, along="u", bump=0.8, wear=0.5), R, smooth=True)
    mesh_obj("hin", inner, faces, WD("#6a4426", "#583620", scale=3, along="u", bump=0.5), R, smooth=True)
    rim = []
    for i in range(N):
        for j in (0, M):
            a = i * (M + 1) + j
            b = (i + 1) * (M + 1) + j
            rim.append((a, b))
    rv = outer + inner
    off = len(outer)
    rf = [(a, b, b + off, a + off) for (a, b) in rim]
    mesh_obj("rim", rv, rf, toon("#d9c9a8", rim=0.4), R, smooth=False)
    stripe = [(i * (M + 1) + 1, i * (M + 1) + 2, (i + 1) * (M + 1) + 2, (i + 1) * (M + 1) + 1) for i in range(N)]
    mesh_obj("stripe", outer, stripe, toon("#2f7a8a", rim=0.4), R, smooth=False)
    for x in (-0.6, 0.45):
        box("thw", (0.22, 1.1, 0.07), WD("#c9a870", "#a98850", scale=3), R, loc=(x, 0, 0.5))
    for s in (-1, 1):
        link_cyl("oar", (0.0, s * 0.7, 0.62), (-0.5, s * 1.7, 0.1), 0.03, toon("#c9a870", rim=0.4), R, seg=6)
        ellipsoid("blade", 0.18, toon("#c9a870", rim=0.4), R, loc=(-0.55, s * 1.78, 0.08), scale=(0.35, 1.0, 0.1), seg=8, rings=5)
    tube("rope", [(1.6, 0.0, 0.66), (2.0, 0.2, 0.2), (2.3, 0.5, 0.04), (2.0, 0.8, 0.04)], 0.035, toon("#c9b98e", rim=0.2), R)
    return {}


def dock_segment():
    R = pivot("p")
    L, Wd = 2.4, 1.5
    pm = WD("#8a6a4a", "#6a4e36", scale=4, along="v", bump=0.9, wear=0.8, moss=0.3)
    for i in range(10):
        box("pl", (0.22, Wd, 0.09), pm, R, loc=(-L / 2 + 0.12 + i * 0.24, 0, 0.62), rot=(0, 0, RAD((i % 3 - 1) * 0.8)))
    for s in (-1, 1):
        box("str", (L + 0.1, 0.1, 0.12), WDT(), R, loc=(0, s * (Wd / 2 - 0.1), 0.52))
    for x in (-L / 2 + 0.05, L / 2 - 0.05):
        for s in (-1, 1):
            frustum("pile", 0.11, 0.1, 1.3, WD("#6a4e36", "#54402c", scale=5, along="v", wear=1.0, moss=0.7), R, loc=(x, s * (Wd / 2 + 0.02), 0.0), seg=8)
            ellipsoid("pt", 0.11, toon("#6a4e36", rim=0.3), R, loc=(x, s * (Wd / 2 + 0.02), 1.3), scale=(1, 1, 0.5), seg=8, rings=5)
    tube("rope", [(-L / 2 + 0.05, -Wd / 2, 1.2), (0, -Wd / 2 - 0.05, 1.0), (L / 2 - 0.05, -Wd / 2, 1.2)], 0.028, toon("#c9b98e", rim=0.2), R)
    lantern2(R, (L / 2 - 0.05, -Wd / 2 - 0.05, 1.45), hang=False) if False else None
    barrel(R, (-0.5, 0.35, 0.66), 0.22, 0.45, col="#8a6a4a")
    return {}


def hay_bale():
    R = pivot("p")
    hay = TH("#e0b858", "#c8a040", scale=4, wear=0.2)
    frustum("round", 0.55, 0.55, 0.9, hay, R, loc=(-0.4, 0.45, 0.55), rot=(RAD(-90), 0, 0), seg=18)
    for rr_ in (0.2, 0.38, 0.5):
        frustum("ring", rr_, rr_, 0.02, toon("#b8903a", rim=0.2), R, loc=(-0.4, -0.46, 0.55), rot=(RAD(-90), 0, 0), seg=18, caps=(False, False))
    frustum("band", 0.57, 0.57, 0.05, toon("#7a5a30", rim=0.2), R, loc=(-0.4, 0.1, 0.55), rot=(RAD(-90), 0, 0), seg=18, caps=(False, False))
    box("sq", (0.9, 0.55, 0.45), hay, R, loc=(0.7, -0.5, 0.0), base=True)
    box("sq2", (0.9, 0.55, 0.45), hay, R, loc=(0.8, -0.45, 0.45), base=True, rot=(0, 0, RAD(8)))
    for z in (0.22, 0.67):
        for x in (0.45, 0.85):
            box("sb", (0.04, 0.58, 0.47), toon("#7a5a30", rim=0.2), R, loc=(x + (0.05 if z > 0.5 else 0), -0.5 + (0.0), z))
    for k in range(5):
        link_cyl("strw", (-0.3 + k * 0.2, -1.1, 0.01), (-0.1 + k * 0.2, -1.2, 0.05), 0.02, toon("#e0b858", rim=0.2), R, seg=3)
    return {}


def haystack():
    R = pivot("p")
    hay = TH("#dcb050", "#bf9238", scale=3, wear=0.5, moss=0.1)
    frustum("lo", 1.15, 0.95, 1.1, hay, R, seg=20)
    frustum("hi", 0.98, 0.0, 1.6, hay, R, loc=(0, 0, 1.0), seg=20, caps=(False, False))
    ellipsoid("bulge", 1.05, hay, R, loc=(0, 0, 1.0), scale=(1, 1, 0.3), seg=18, rings=6)
    frustum("pole", 0.04, 0.03, 0.7, WDT(), R, loc=(0, 0, 2.5), seg=6)
    for z in (0.55, 1.4):
        frustum("band", 1.1 if z < 1 else 0.85, 1.1 if z < 1 else 0.85, 0.05, toon("#6a4a28", rim=0.2), R, loc=(0, 0, z), seg=20, caps=(False, False))
    link_cyl("lad", (0.9, -0.5, 0.0), (0.45, -0.3, 1.9), 0.03, WDT(), R, seg=5)
    link_cyl("lad2", (1.05, -0.35, 0.0), (0.6, -0.15, 1.9), 0.03, WDT(), R, seg=5)
    for k in range(6):
        link_cyl("rg", (0.97 - k * 0.08, -0.43 + k * 0.025, 0.2 + k * 0.28), (0.82 - k * 0.07, -0.27 + k * 0.025, 0.2 + k * 0.28), 0.02, WDT(), R, seg=4)
    for k in range(6):
        link_cyl("strw", (-0.9 + k * 0.3, -1.2, 0.01), (-0.8 + k * 0.3, -1.3, 0.05), 0.02, toon("#e0b858", rim=0.2), R, seg=3)
    return {}


def canopy(R, cx, cy, cz, rad, n, seed, cols=None, hs=0.85, rs=(0.9, 1.4)):
    rnd = random.Random(seed)
    cols = cols or [tex_toon("plain", "#4fa86a", "#3a8a54", scale=3, bump=0, wear=0, ao=0.4),
                    tex_toon("plain", "#6cc27a", "#4fa86a", scale=3, bump=0, wear=0, ao=0.4),
                    tex_toon("plain", "#2f8a6a", "#257558", scale=3, bump=0, wear=0, ao=0.4)]
    for i in range(n):
        a = i * 2.4
        rr = 0.2 + math.sqrt(i / n) * rad
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.8
        z = cz + (rad - rr) * 0.4 + rnd.uniform(-0.15, 0.4)
        s = rnd.uniform(*rs) * (rad / 2.4)
        ellipsoid("lf", s, cols[i % 3], R, loc=(x, y, z), scale=(1, 1, hs), seg=12, rings=8)


def tiny_door(parent, loc, r=0.2, color="#3fa890"):
    dp = pivot("door", loc, parent)
    frustum("ring", r * 1.25, r * 1.25, 0.1, ST("#a8a09a", "#8c848a", scale=4, moss=0.9), dp, loc=(0, 0.05, 0), rot=(RAD(90), 0, 0), seg=18)
    frustum("leaf", r, r, 0.08, WD(color, color, scale=4, along="v"), dp, loc=(0, -0.03, 0), rot=(RAD(90), 0, 0), seg=18)
    box("dh", (r * 1.4, 0.03, 0.025), toon("#2a4a46", rim=0.3), dp, loc=(0, -0.12, r * 0.3))
    ellipsoid("dk", r * 0.14, toon("gold", rim=0.6), dp, loc=(r * 0.5, -0.13, 0), seg=6, rings=4)
    ellipsoid("dl", r * 2.4, glow("#6fe8c8", 0.8, alpha=0.3, soft=True), dp, loc=(0, -0.2, 0), scale=(1, 0.2, 1), seg=10, rings=6)


def fairy_door_tree():
    R = pivot("p")
    bark = tex_toon("wood", "#7a5a42", "#5f4430", scale=4.0, plane="xz", along="v", bump=1.4, moss=0.9, wear=0.4)
    frustum("trunk", 0.7, 0.42, 2.8, bark, R, seg=16)
    for k in range(5):
        a = k * 1.26 + 0.3
        ellipsoid("root", 0.3, bark, R, loc=(math.cos(a) * 0.62, math.sin(a) * 0.55, 0.1), scale=(1.5, 0.55, 0.45), rot=(0, 0, a), seg=8, rings=5)
    tiny_door(R, (0, -0.68, 0.38), 0.2)
    for (x, z) in ((-0.28, 1.6), (0.25, 2.05)):
        yy = -math.sqrt(max(0.05, (0.7 - 0.1 * z) ** 2 - x * x)) + 0.02
        frustum("wr", 0.12, 0.12, 0.06, WD("#6a4326", "#5a3720", scale=4), R, loc=(x, yy + 0.04, z), rot=(RAD(90), 0, 0), seg=10)
        frustum("wg", 0.08, 0.08, 0.05, glow("#ffd070", 3.4), R, loc=(x, yy - 0.0, z), rot=(RAD(90), 0, 0), seg=10)
    canopy(R, 0, 0, 3.1, 1.5, 14, 3)
    for i in range(7):
        a = i * 2.1
        ellipsoid("ff", 0.045, glow("#ffe890", 5), R, loc=(math.cos(a) * 1.3, -abs(math.sin(a)) * 1.1 - 0.2, 3.0 + (i % 3) * 0.4), seg=6, rings=4)
    for k in range(5):
        a = k * 1.3 + 0.4
        mx, my = math.cos(a) * 1.0, math.sin(a) * 0.8 - 0.3
        frustum("ms", 0.03, 0.04, 0.12, toon("#efe6d0", rim=0.3), R, loc=(mx, my, 0), seg=6)
        ellipsoid("mc", 0.09, toon("#c44b3f", rim=0.4), R, loc=(mx, my, 0.13), scale=(1, 1, 0.65), seg=8, rings=5)
    truth_extras(R, threads=[(0.3, -0.5, 2.6), (-0.5, -0.4, 3.0)])
    return {}


def giant_tree_hollow():
    R = pivot("p")
    bark = tex_toon("wood", "#6d5a4a", "#54443a", scale=3.0, plane="xz", along="v", bump=1.5, moss=0.8, wear=0.5)
    frustum("trunk", 1.4, 0.95, 5.0, bark, R, seg=22)
    for k in range(8):
        a = k * 0.785 + 0.2
        ellipsoid("root", 0.8, bark, R, loc=(math.cos(a) * 1.3, math.sin(a) * 1.2, 0.2), scale=(1.5, 0.5, 0.4), rot=(0, 0, a), seg=10, rings=6)
    # hollow arch
    box("hd", (0.9, 0.2, 1.5), toon("#14101a", rim=0), R, loc=(0, -1.33, 0.1), base=True)
    frustum("hda", 0.45, 0.45, 0.2, toon("#14101a", rim=0), R, loc=(0, -1.2, 1.6), rot=(RAD(90), 0, 0), seg=14)
    ellipsoid("hin", 0.5, glow("#35d3b0", 1.2, alpha=0.35, soft=True), R, loc=(0, -1.35, 0.8), scale=(1, 0.2, 1.4), seg=10, rings=6)
    for s in (-1, 1):
        ellipsoid("lip", 0.35, bark, R, loc=(s * 0.55, -1.32, 0.9), scale=(0.5, 0.5, 2.4), seg=8, rings=6)
    ellipsoid("liptop", 0.55, bark, R, loc=(0, -1.3, 1.95), scale=(1.1, 0.5, 0.45), seg=10, rings=6)
    ellipsoid("moss", 0.5, tex_toon("plain", "#5a9a4a", "#4a7a3a", scale=3, bump=0, ao=0.3), R, loc=(-0.5, -1.4, 2.1), scale=(1.2, 0.4, 0.5), seg=8, rings=5)
    for a in (0.5, 2.4, 4.0):
        link_cyl("br", (math.cos(a) * 0.5, math.sin(a) * 0.4, 4.1), (math.cos(a) * 1.7, math.sin(a) * 1.3, 5.4), 0.28, bark, R, seg=8, r2=0.12)
    canopy(R, 0, 0, 5.4, 2.7, 24, 11, rs=(1.0, 1.5))
    for k in range(7):   # glowing fungus + hanging lights
        a = k * 0.9
        ellipsoid("fg", 0.12, glow("#7fe8d0", 1.6), R, loc=(math.cos(a) * 1.35, -abs(math.sin(a)) * 1.2, 0.5 + (k % 4) * 0.35), scale=(1.2, 0.7, 0.4), seg=8, rings=5)
    for i in range(6):
        a = i * 1.3
        tube("vine", [(math.cos(a) * 1.8, -abs(math.sin(a)) * 1.4, 5.2), (math.cos(a) * 1.8, -abs(math.sin(a)) * 1.4 - 0.05, 4.2)], 0.02, toon("#4a7a3a", rim=0), R)
        ellipsoid("vf", 0.07, glow("#ffe890", 5), R, loc=(math.cos(a) * 1.8, -abs(math.sin(a)) * 1.4 - 0.05, 4.2), seg=6, rings=4)
    truth_extras(R, threads=[(0.8, -1.3, 4.4), (-0.9, -1.2, 3.4)])
    return {}


def stall_base(R, w, d, cols, post="#6a4326", counter="#a06a3e", h=2.1):
    wd = WD(counter, "#85502c", scale=3, bump=0.6)
    for sx in (-1, 1):
        for sy in (-1, 1):
            frustum("post", 0.06, 0.06, h, WD(post, post, scale=4, along="v"), R, loc=(sx * w / 2, sy * d / 2, 0), seg=6)
    box("cnt", (w, 0.55, 0.75), wd, R, loc=(0, -d / 2 + 0.2, 0), base=True)
    box("ctop", (w + 0.1, 0.65, 0.07), WD("#c49060", "#a87444", scale=3), R, loc=(0, -d / 2 + 0.2, 0.78))
    zb, zf = h + 0.35, h - 0.1
    aw = tex_toon("stripes", cols[0], cols[1], scale=3.0 * 2.4 / w, plane="xy", bump=0.5, rim=0.4, ao=0.2)
    mesh_obj("awn", [(-w / 2 - 0.15, d / 2, zb), (w / 2 + 0.15, d / 2, zb), (w / 2 + 0.15, -d / 2 - 0.45, zf), (-w / 2 - 0.15, -d / 2 - 0.45, zf)], [(0, 1, 2, 3)], aw, R, smooth=False)
    n = 8
    for i in range(n):
        x0 = -w / 2 - 0.15 + i * (w + 0.3) / n
        x1 = x0 + (w + 0.3) / n
        mesh_obj("val", [(x0, -d / 2 - 0.45, zf), (x1, -d / 2 - 0.45, zf), ((x0 + x1) / 2, -d / 2 - 0.47, zf - 0.22)], [(0, 2, 1)],
                 toon(cols[0] if i % 2 == 0 else cols[1], rim=0.4), R, smooth=False)
    box("back", (w, 0.06, h - 0.6), PL("#d9c9a8", "#c4b38e", wear=0.5), R, loc=(0, d / 2, 0.7), base=True)
    return wd


def market_stall_b():
    R = pivot("p")
    stall_base(R, 2.2, 1.3, ("#3f9a5a", "#f3e4c4"))
    cols = ["#c44b3f", "#e8884a", "#e8b04a", "#6cb257", "#a07ad8"]
    for k in range(5):   # fruit crates
        x = -0.85 + k * 0.42
        box("fc", (0.38, 0.3, 0.12), WD("#a06a3e", "#85502c", scale=4), R, loc=(x, -0.5, 0.86))
        for j in range(5):
            ellipsoid("fr", 0.075, toon(cols[k], rim=0.5), R, loc=(x - 0.12 + (j % 3) * 0.12, -0.5 + (j // 3) * 0.1 - 0.05, 0.98), seg=8, rings=6)
    crate(R, (-1.4, 0.2, 0), 0.45, 0.2)
    barrel(R, (1.4, 0.1, 0), 0.26, 0.55, col="#8a6a4a")
    for i in range(4):
        ellipsoid("hang", 0.08, toon(cols[i], rim=0.5), R, loc=(-0.6 + i * 0.4, -0.3, 1.75 - (i % 2) * 0.12), seg=8, rings=6)
        link_cyl("hs", (-0.6 + i * 0.4, -0.3, 2.05), (-0.6 + i * 0.4, -0.3, 1.8 - (i % 2) * 0.12), 0.008, toon("#d9c9a8", rim=0), R, seg=3)
    return {}


def market_stall_c():
    R = pivot("p")
    stall_base(R, 2.6, 1.3, ("#3f6fc4", "#f3f0e4"), post="#4a5a6a", counter="#7a8a96")
    for k in range(3):
        box("ice", (0.7, 0.5, 0.08), toon("#cfe8f4", rim=0.5), R, loc=(-0.85 + k * 0.85, -0.48, 0.86))
        for j in range(4):
            ellipsoid("fish", 0.12, toon(["#b9c6d6", "#a8b8cc", "#d6a8a0"][(j + k) % 3], rim=0.6), R, loc=(-1.05 + k * 0.85 + j * 0.14, -0.5 + (j % 2) * 0.12, 0.96),
                      scale=(2.0, 0.7, 0.7), rot=(0, 0, 0.3 * (j - 1.5)), seg=8, rings=5)
    for i in range(5):
        link_cyl("fs", (-1.0 + i * 0.5, -0.1, 1.95), (-1.0 + i * 0.5, -0.1, 1.7), 0.008, toon("#d9c9a8", rim=0), R, seg=3)
        ellipsoid("hf", 0.07, toon("#b9c6d6", rim=0.6), R, loc=(-1.0 + i * 0.5, -0.1, 1.5), scale=(0.6, 0.4, 2.2), seg=8, rings=5)
    barrel(R, (-1.6, -0.4, 0), 0.28, 0.6, col="#4a6a8a")
    crate(R, (1.65, -0.3, 0), 0.5, -0.2, col="#8a6a4a")
    ellipsoid("net", 0.3, toon("#c9b98e", rim=0.2), R, loc=(1.6, 0.4, 0.2), scale=(1.2, 1, 0.5), seg=8, rings=5)
    return {}


def market_stall_d():
    R = pivot("p")
    stall_base(R, 2.4, 1.3, ("#c44b3f", "#e8b04a"), post="#5a3a26", counter="#8a5a40")
    cl = ["#c44b3f", "#4f7ad8", "#e8b04a", "#35b39a", "#a07ad8", "#f3e4c4"]
    for k in range(6):
        frustum("bolt", 0.1, 0.1, 0.5, FAB("weave", cl[k], "#f3e4c4", scale=16), R, loc=(-0.9 + k * 0.36, -0.48, 0.82), seg=10)
    for k in range(4):   # hanging cloth lengths
        x = -0.9 + k * 0.6
        box("cl", (0.4, 0.04, 0.9), FAB("weave", cl[(k + 1) % 6], "#f3e4c4", scale=16), R, loc=(x, 0.0, 1.45), rot=(0, RAD(3 * (k - 1.5)), 0))
    box("rod", (2.3, 0.05, 0.05), WDT(), R, loc=(0, 0, 1.95))
    barrel(R, (1.65, 0.0, 0), 0.24, 0.5, col="#7a5a4a")
    for i in range(3):
        spool(R, (-1.5 + i * 0.28, -0.3, 0), 0.1, 0.2, cl[i])
    return {}


def fountain():
    R = pivot("p")
    st = ST("#b0aab4", "#8c8694", scale=2.4, bump=0.9, moss=0.4, wear=0.6)
    frustum("basin", 1.4, 1.25, 0.65, st, R, seg=28)
    frustum("rim", 1.46, 1.46, 0.12, ST("#c0bac4", "#9c96a4", plane="xy", scale=2.4, bump=0.6), R, loc=(0, 0, 0.62), seg=28)
    frustum("water", 1.25, 1.25, 0.02, glow("#7fe0e0", 1.1, alpha=0.7), R, loc=(0, 0, 0.58), seg=28)
    frustum("ped", 0.3, 0.22, 1.1, st, R, loc=(0, 0, 0.5), seg=12)
    frustum("bowl", 0.7, 0.28, 0.3, st, R, loc=(0, 0, 1.2), seg=18)
    frustum("bw", 0.62, 0.62, 0.02, glow("#7fe0e0", 1.1, alpha=0.7), R, loc=(0, 0, 1.47), seg=18)
    frustum("top", 0.14, 0.1, 0.4, st, R, loc=(0, 0, 1.45), seg=10)
    ellipsoid("fin", 0.16, st, R, loc=(0, 0, 1.9), seg=10, rings=8)
    for k in range(8):
        a = k * math.pi / 4
        pts = [(math.cos(a) * r_, math.sin(a) * r_, 1.95 + 0.38 * math.sin(math.pi * r_ / 0.6 * 0.5) - 0.7 * (r_ / 0.6) ** 2) for r_ in [0.0, 0.15, 0.3, 0.45, 0.6]]
        tube("jet", pts, 0.025, glow("#bff4f0", 2.0, alpha=0.8), R)
    ellipsoid("spl", 0.7, glow("#bff4f0", 1.0, alpha=0.3, soft=True), R, loc=(0, 0, 1.5), scale=(1, 1, 0.5), seg=12, rings=6)
    for k in range(6):
        a = k * 1.05
        ellipsoid("lil", 0.12, toon("#6cb257", rim=0.3), R, loc=(math.cos(a) * 0.95, math.sin(a) * 0.95, 0.62), scale=(1.3, 1.3, 0.15), seg=8, rings=4)
        if k % 2 == 0:
            ellipsoid("lf", 0.06, toon("#ffb4d8", rim=0.3), R, loc=(math.cos(a) * 0.95, math.sin(a) * 0.95, 0.68), seg=6, rings=4)
    return {}


def signpost_b():
    R = pivot("p")
    frustum("post", 0.1, 0.08, 2.5, WD("#6a4326", "#5a3720", scale=3, along="v"), R, seg=8)
    frustum("pc", 0.17, 0.17, 0.12, ST("#a8a09a", "#8c848a", scale=3), R, seg=8)
    boards = [(2.1, 0.0, "#c9944a", 0.9), (1.7, 0.0, "#4f9a7a", -0.8), (1.3, 0.0, "#c44b3f", 0.8)]
    for (z, _, c, dirx) in boards:
        p = pivot("bd", (0, -0.1, z), R, rot=(0, 0, RAD(8 * dirx)))
        box("b", (0.9, 0.06, 0.28), WD(c, c, scale=4, bump=0.5), p, loc=(dirx * 0.45, 0, 0))
        mesh_obj("tip", [(dirx * 0.9, 0, 0.14), (dirx * 0.9, 0, -0.14), (dirx * 1.12, 0, 0.0)], [(0, 1, 2)], WD(c, c, scale=4), p, smooth=False)
        for k in range(3):
            box("ln", (0.12, 0.01, 0.03), toon("#f3e4c4", rim=0), p, loc=(dirx * (0.2 + k * 0.2), -0.04, 0))
    big_lantern(R, (0, 0, 2.5), 0.45, glow_s=5)
    return {}


def crate_stack():
    R = pivot("p")
    crate(R, (-0.5, 0, 0), 0.7, 0.05, col="#a06a3e")
    crate(R, (0.4, -0.2, 0), 0.6, -0.2, col="#8a5a38")
    crate(R, (0.0, 0.5, 0), 0.6, 0.1, col="#9a6a40")
    crate(R, (-0.4, 0.0, 0.7), 0.5, 0.35, col="#b07a46")
    crate(R, (0.1, 0.5, 0.6), 0.45, -0.1, col="#a06a3e")
    s2 = pivot("sack", (0.9, -0.6, 0), R, rot=(0, 0, 0.4))
    ellipsoid("sk", 0.3, tex_toon("weave", "#efe4cc", "#d9c9a8", scale=18, plane="xz", bump=0.9, rim=0.4, ao=0.3), s2, loc=(0, 0, 0.3), scale=(1, 0.75, 1.0), seg=12, rings=8)
    frustum("tie", 0.1, 0.06, 0.12, toon("#efe4cc", rim=0.3), s2, loc=(0, 0, 0.55), seg=8)
    tube("rope", [(-0.9, -0.6, 0.02), (-0.7, -0.9, 0.02), (-0.4, -0.85, 0.03)], 0.03, toon("#c9b98e", rim=0.2), R)
    return {}


def barrel_p():
    R = pivot("p")
    barrel(R, (0, 0, 0), 0.42, 0.9, col="#a06a3e")
    barrel(R, (0.7, -0.25, 0), 0.28, 0.6, col="#8a6a4a")
    frustum("ladle", 0.0, 0.0, 0.0, toon("#6a6a74"), R) if False else None
    return {}


def lantern_post_b():
    R = pivot("p")
    iron = toon("#2e2a30", rim=0.4)
    frustum("base", 0.2, 0.14, 0.4, ST("#8a8088", "#6c6470", scale=3), R, seg=8)
    frustum("pole", 0.05, 0.04, 2.7, iron, R, loc=(0, 0, 0.35), seg=8)
    for z in (0.7, 2.6):
        frustum("ring", 0.09, 0.09, 0.08, iron, R, loc=(0, 0, z), seg=8)
    pts = [(0, 0, 3.0), (0.15, 0, 3.35), (0.5, 0, 3.45), (0.85, 0, 3.3), (0.95, 0, 3.1)]
    tube("arm", pts, 0.035, iron, R)
    tube("scr", [(0, 0, 2.7), (0.3, 0, 2.7), (0.4, 0, 2.9), (0.3, 0, 3.05), (0.2, 0, 2.95)], 0.025, iron, R)
    link_cyl("ch", (0.95, 0, 3.1), (0.95, 0, 2.95), 0.012, iron, R, seg=4)
    big_lantern(R, (0.95, 0, 2.2), 0.7, glow_s=7)
    frustum("hook", 0.0, 0.0, 0.0, iron, R) if False else None
    if EL.TRUTH:
        snapped_thread(R, (0.95, -0.1, 2.9), 1.2, 0.08, seed=8, cut=False)
    return {}


def scarecrow():
    R = pivot("p")
    wood = WD("#6a4326", "#5a3720", scale=3, along="v")
    frustum("pole", 0.06, 0.05, 2.2, wood, R, seg=6)
    box("arms", (1.7, 0.08, 0.08), wood, R, loc=(0, 0, 1.55))
    sack = tex_toon("weave", "#c9a878", "#a98858", scale=14, plane="xz", bump=0.9, rim=0.4, ao=0.3)
    ellipsoid("torso", 0.36, sack, R, loc=(0, -0.02, 1.2), scale=(0.95, 0.7, 1.3), seg=12, rings=8)
    cl = tex_toon("knit", "#4f6aa8", "#3a528c", scale=10, plane="xz", bump=0.8, rim=0.4, ao=0.3)
    ellipsoid("shirt", 0.4, cl, R, loc=(0, -0.03, 1.28), scale=(1.0, 0.72, 0.85), seg=12, rings=8)
    for s in (-1, 1):
        ellipsoid("sl", 0.17, cl, R, loc=(s * 0.55, 0, 1.55), scale=(2.6, 0.55, 0.55), seg=10, rings=6)
        for k in range(5):
            link_cyl("hay", (s * (0.88 + k * 0.01), 0, 1.55), (s * (1.05 + k * 0.02), -0.02 + k * 0.02, 1.4 + k * 0.05 + 0.05 * s), 0.018, toon("#e0b858", rim=0.2), R, seg=3)
    ellipsoid("head", 0.24, sack, R, loc=(0, -0.02, 1.98), scale=(1, 0.9, 1.05), seg=12, rings=8)
    for s in (-1, 1):
        ellipsoid("eye", 0.03, toon("#2a1c20", rim=0), R, loc=(s * 0.08, -0.22, 2.02), seg=6, rings=4)
    for k in range(5):
        ellipsoid("st", 0.016, toon("#2a1c20", rim=0), R, loc=(-0.08 + k * 0.04, -0.23, 1.9 - 0.02 * abs(k - 2)), seg=4, rings=3)
    frustum("hbrim", 0.4, 0.4, 0.05, toon("#7a5a3a", rim=0.4), R, loc=(0, 0, 2.17), seg=16)
    frustum("hcrown", 0.2, 0.17, 0.3, toon("#7a5a3a", rim=0.4), R, loc=(0, 0, 2.2), seg=12)
    frustum("hband", 0.205, 0.205, 0.05, toon("#c44b3f", rim=0.3), R, loc=(0, 0, 2.24), seg=12, caps=(False, False))
    for k in range(7):
        link_cyl("hair", (-0.18 + k * 0.06, -0.1, 2.15), (-0.25 + k * 0.08, -0.2, 2.0), 0.015, toon("#e0b858", rim=0.2), R, seg=3)
    box("patch", (0.15, 0.02, 0.15), toon("#c44b3f", rim=0.2), R, loc=(0.15, -0.26, 1.15))
    crow = pivot("crow", (-0.8, 0, 1.68), R)
    cm = toon("#1e1a28", rim=0.6)
    ellipsoid("cb", 0.1, cm, crow, scale=(1.3, 0.8, 1), seg=8, rings=6)
    ellipsoid("ch", 0.06, cm, crow, loc=(-0.12, -0.03, 0.08), seg=8, rings=6)
    mesh_obj("cbk", [(-0.18, -0.03, 0.08), (-0.18, -0.03, 0.06), (-0.26, -0.03, 0.07)], [(0, 1, 2)], toon("#e8b04a", rim=0.3), crow, smooth=False)
    mesh_obj("ct", [(0.1, 0, 0.0), (0.1, 0, 0.04), (0.28, 0, -0.04)], [(0, 1, 2)], cm, crow, smooth=False)
    bush(R, (0.7, -0.3, 0), r=0.2, flowers=False, seed=2)
    return {}


def flower_bush():
    R = pivot("p")
    m = [tex_toon("plain", "#4f9a4f", "#3a7a3e", scale=3, bump=0, wear=0, ao=0.4), tex_toon("plain", "#6cb257", "#4f9a4f", scale=3, bump=0, wear=0, ao=0.4)]
    for k, (dx, dy, dz, r_) in enumerate([(0, 0, 0.55, 0.55), (0.55, 0.05, 0.42, 0.42), (-0.55, 0.0, 0.42, 0.42), (0.2, -0.35, 0.38, 0.35), (-0.25, 0.3, 0.4, 0.38)]):
        ellipsoid("b", r_, m[k % 2], R, loc=(dx, dy, dz), scale=(1, 1, 0.85), seg=12, rings=8)
    rnd = random.Random(2)
    cols = ["#ff8ac0", "#ffd86a", "#f6f0e6", "#c79ae8", "#ff7a6a"]
    for i in range(34):
        a = rnd.uniform(0, 6.28)
        el = rnd.uniform(0.2, 1.3)
        rr = 0.85 * (1 - el * 0.3)
        x, y, z = math.cos(a) * rr * math.cos(el) * 0.95, math.sin(a) * rr * math.cos(el) * 0.75 - 0.08, 0.35 + math.sin(el) * 0.75
        if y > 0.15:
            y = -y * 0.3
        c = cols[i % 5]
        ellipsoid("fl", 0.075, toon(c, rim=0.4), R, loc=(x, y - 0.1, z), scale=(1, 0.6, 1), seg=7, rings=5)
        ellipsoid("fc", 0.03, toon("#e8b04a", rim=0), R, loc=(x, y - 0.17, z), seg=5, rings=3)
    return {}


def mushroom_ring():
    R = pivot("p")
    rnd = random.Random(7)
    for k in range(10):
        a = k * 2 * math.pi / 10 + rnd.uniform(-0.1, 0.1)
        mx, my = math.cos(a) * 1.25, math.sin(a) * 0.95
        s_ = rnd.uniform(0.8, 1.4)
        frustum("ms", 0.07 * s_, 0.1 * s_, 0.3 * s_, toon("#efe6d0", rim=0.3), R, loc=(mx, my, 0.0), seg=8)
        cap = toon(["#c44b3f", "#e8884a", "#a07ad8"][k % 3], rim=0.4)
        ellipsoid("mc", 0.24 * s_, cap, R, loc=(mx, my, 0.32 * s_), scale=(1, 1, 0.62), seg=12, rings=7)
        for j in range(4):
            aa = j * 1.6
            ellipsoid("md", 0.04 * s_, toon("#f6f0e6", rim=0), R, loc=(mx + math.cos(aa) * 0.13 * s_, my + math.sin(aa) * 0.1 * s_ - 0.05, 0.32 * s_ + 0.11 * s_), seg=5, rings=3)
    ellipsoid("ringg", 1.3, glow("#7fe8d0", 0.5, alpha=0.18, soft=True), R, loc=(0, 0, 0.06), scale=(1.0, 0.78, 0.05), seg=14, rings=6)
    for k in range(6):
        a = k * 1.1
        ellipsoid("sp", 0.035, glow("#ffe890", 4), R, loc=(math.cos(a) * 0.7, math.sin(a) * 0.5, 0.35 + (k % 3) * 0.15), seg=6, rings=4)
    return {}


def bridge_small():
    R = pivot("p")
    L = 3.4
    pm = WD("#9a7a52", "#7a5e3c", scale=4, along="v", bump=0.9, wear=0.7, moss=0.2)
    N = 14
    for i in range(N):
        x = -L / 2 + 0.12 + i * (L - 0.24) / (N - 1)
        z = 0.35 + 0.35 * math.sin(math.pi * (x + L / 2) / L)
        slope = 0.35 * math.pi / L * math.cos(math.pi * (x + L / 2) / L)
        box("pl", (0.26, 1.2, 0.08), pm, R, loc=(x, 0, z), rot=(0, -math.atan(slope), 0))
    for s in (-1, 1):
        pts = [(-L / 2 + L * t / 10, s * 0.62, 0.35 + 0.35 * math.sin(math.pi * t / 10) + 0.05) for t in range(11)]
        tube("stringer", pts, 0.05, WDT(), R)
        pts2 = [(x, y, z + 0.8) for (x, y, z) in pts]
        tube("rail", pts2, 0.04, WD("#8a6a4a", "#6a4e36", scale=4), R)
        for t in (0, 2, 4, 6, 8, 10):
            x, y, z = pts[t]
            frustum("bp", 0.05, 0.05, 0.85, WD("#6a4e36", "#54402c", scale=5, along="v"), R, loc=(x, y, z - 0.02), seg=6)
        for t in (0, 10):
            x, y, z = pts[t]
            ellipsoid("pt", 0.07, toon("#6a4e36", rim=0.3), R, loc=(x, y, z + 0.85), seg=6, rings=4)
    for sx in (-1, 1):
        rock(R, (sx * (L / 2 + 0.25), 0.7, 0), 0.3, (1.2, 1, 0.7), 0.3, seed=sx + 3)
        rock(R, (sx * (L / 2 + 0.25), -0.7, 0), 0.25, (1.2, 1, 0.7), 1.0, seed=sx + 5)
    return {}


BUILDERS = {"rock_a": rock_a, "rock_b": rock_b, "standing_stone": standing_stone, "stone_circle": stone_circle, "reeds": reeds,
            "boat": boat, "dock_segment": dock_segment, "hay_bale": hay_bale, "haystack": haystack, "fairy_door_tree": fairy_door_tree,
            "giant_tree_hollow": giant_tree_hollow, "market_stall_b": market_stall_b, "market_stall_c": market_stall_c,
            "market_stall_d": market_stall_d, "fountain": fountain, "signpost_b": signpost_b, "crate_stack": crate_stack,
            "barrel": barrel_p, "lantern_post_b": lantern_post_b, "scarecrow": scarecrow, "flower_bush": flower_bush,
            "mushroom_ring": mushroom_ring, "bridge_small": bridge_small}

if __name__ == "__main__":
    a = script_args()
    if "truth" in a:
        # default truth set only
        if len(a) <= 2:
            a = a + TRUTH_PROPS
        run_main(BUILDERS, subdir="env2p", metaname="props2_meta.json") if False else None
    import w2lib
    sys.argv = sys.argv[:sys.argv.index("--") + 1] + a
    run_main(BUILDERS, subdir="env2p", metaname="props2_meta.json")
