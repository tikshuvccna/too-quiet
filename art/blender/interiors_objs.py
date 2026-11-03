"""Object sprites for the three houses. Each builder gets a pivot R at the sprite's ground-contact point
(wall objects: bottom-centre at the wall). They may return {"cell":(w,h),"anchor":(x,y)}.
EL.TRUTH switches on the clue / damage details."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env_blocks import *  # noqa
import env_lib as EL

# ------------------------------------------------------------------ helpers
def table(R, loc, w, d, h, top="#a06a3e", leg="#85502c", rot=0.0, cloth=None):
    p = pivot("table", loc, R, rot=(0, 0, rot))
    box("top", (w, d, 0.08), WD(top, leg, scale=3, plane="xy"), p, loc=(0, 0, h - 0.04))
    for sx in (-1, 1):
        for sy in (-1, 1):
            box("leg", (0.08, 0.08, h - 0.07), WDT(leg, leg), p, loc=(sx * (w / 2 - 0.08), sy * (d / 2 - 0.08), 0), base=True)
    if cloth:
        box("cloth", (w * 0.8, d * 0.8, 0.012), FAB("weave", cloth, "#f3e4c4", scale=12, plane="xy"), p, loc=(0, 0, h + 0.005))
    return p


def round_table(R, loc, r, h, top="#a06a3e", cloth=None):
    p = pivot("rt", loc, R)
    frustum("top", r, r, 0.07, WD(top, top, scale=3, plane="xy"), p, loc=(0, 0, h - 0.07), seg=24)
    frustum("stem", 0.07, 0.09, h - 0.07, WDT(), p, seg=8)
    frustum("foot", r * 0.5, r * 0.5, 0.05, WDT(), p, seg=16)
    if cloth:
        frustum("cl", r * 0.85, r * 0.85, 0.012, FAB("weave", cloth, "#f3e4c4", scale=12, plane="xy"), p, loc=(0, 0, h), seg=24)
    return p


def paper_sheet(R, loc, size=(0.4, 0.55), rot=(0, 0, 0), a="#f3e8cc", b="#2a3a8a", scale=3.4):
    return box("sheet", (size[0], 0.015, size[1]), tex_toon("paper", a, b, scale=scale, plane="xz", bump=0.1, wear=0), R, loc=loc, rot=rot)


def scratches(R, loc, n=3, length=0.4, rot=(0, 0, 0), plane="xz"):
    """Truth clue: three parallel claw/scratch marks."""
    p = pivot("scr", loc, R, rot=rot)
    for k in range(n):
        link_cyl("sc", (k * 0.05, -0.012, 0.0), (k * 0.05 + 0.03, -0.012, -length), 0.007, toon("#1a1420", rim=0), p, seg=3)
    return p


def cut_thread(R, loc, length=0.5, seed=1):
    """Truth clue: a teal thread whose end is cut clean (flat, bright)."""
    pts = [(loc[0], loc[1], loc[2]), (loc[0] + 0.15, loc[1] - 0.1, loc[2] - length * 0.3), (loc[0] + 0.3, loc[1] - 0.05, loc[2] - length * 0.6),
           (loc[0] + 0.45, loc[1] - 0.12, loc[2] - length)]
    tube("cth", pts, 0.015, glow("#35d3b0", 3.0), R)
    box("cutend", (0.05, 0.02, 0.02), toon("#f3f0e4", rim=0.5), R, loc=pts[-1])


def weaver_knot(R, loc, s=0.2):
    """Truth clue: the weaver's two-turn knot: two loops through each other, teal."""
    m = glow("#35d3b0", 3.2)
    for k in range(2):
        a = k * 0.5
        pts = [(loc[0] + math.cos(t) * s * (1 + 0.25 * k), loc[1] - 0.04 * k, loc[2] + math.sin(t) * s * 0.7) for t in [i * 0.4 + a for i in range(17)]]
        tube("knot", pts, 0.02, m, R)
    tube("tail1", [(loc[0] + s, loc[1], loc[2]), (loc[0] + s * 2, loc[1] - 0.05, loc[2] - 0.2), (loc[0] + s * 2.2, loc[1] - 0.05, loc[2] - 0.5)], 0.015, m, R)
    tube("tail2", [(loc[0] - s, loc[1], loc[2]), (loc[0] - s * 1.8, loc[1] - 0.05, loc[2] + 0.15)], 0.015, m, R)


def frame_picture(R, loc, w, h, c1, c2, frame="#c9b48a", empty=False, rot=0.0):
    p = pivot("pic", loc, R, rot=(0, 0, rot))
    box("fr", (w, 0.06, h), WD(frame, "#a88a5a", scale=4, bump=0.5), p, loc=(0, -0.03, 0))
    if empty:
        box("in", (w - 0.14, 0.04, h - 0.14), PL("#e8d6b8", "#d6c4a4", wear=0.4), p, loc=(0, -0.055, 0))
        box("ghost", (w - 0.2, 0.01, h - 0.2), toon("#f3e8cc", rim=0), p, loc=(0, -0.078, 0))
    else:
        m = tex_toon("plain", c1, c2, scale=1.5, bump=0.1, wear=0, rim=0.2)
        box("in", (w - 0.14, 0.04, h - 0.14), m, p, loc=(0, -0.055, 0))
        box("sun", (w * 0.2, 0.03, w * 0.2), toon("#ffe08a", rim=0.2), p, loc=(w * 0.12, -0.08, h * 0.1))
        box("hill", (w - 0.16, 0.03, h * 0.3), toon(c2, rim=0.2), p, loc=(0, -0.08, -h * 0.28))
    return p


def lamp_floor(R, loc, h=2.2, shade="#f3d29a", glow_c="#ffcf7a"):
    p = pivot("lamp", loc, R)
    frustum("base", 0.22, 0.2, 0.06, WDT(), p, seg=12)
    frustum("pole", 0.03, 0.03, h, WDT(), p, seg=6)
    frustum("shade", 0.34, 0.2, 0.42, FAB("weave", shade, "#f3e4c4", scale=10, bump=0.3), p, loc=(0, 0, h - 0.1), seg=14, caps=(False, False))
    ellipsoid("bulb", 0.14, glow(glow_c, 5), p, loc=(0, 0, h + 0.05), seg=10, rings=8)
    ellipsoid("halo", 0.7, glow(glow_c, 1.5, alpha=0.35, soft=True), p, loc=(0, 0, h + 0.05), seg=12, rings=8)
    return p


def book_stack(R, loc, n=4, seed=1, cols=("wine", "#4f7ad8", "forest", "gold", "plum")):
    rnd = random.Random(seed)
    z = 0
    for i in range(n):
        s = (rnd.uniform(0.35, 0.5), rnd.uniform(0.25, 0.32), rnd.uniform(0.05, 0.09))
        book(R, (loc[0] + rnd.uniform(-.02, .02), loc[1], loc[2] + z), s, cols[i % len(cols)], rot=rnd.uniform(-0.2, 0.2))
        z += s[2]


def books_row(R, loc, n, h=0.4, seed=1, cols=("wine", "#4f7ad8", "forest", "gold", "plum", "#c9b48a")):
    rnd = random.Random(seed)
    x = loc[0]
    for i in range(n):
        t = rnd.uniform(0.05, 0.1)
        hh = h * rnd.uniform(0.75, 1.0)
        box("bk", (t, 0.22, hh), toon(cols[i % len(cols)], rim=0.3), R, loc=(x + t / 2, loc[1], loc[2]), base=True)
        x += t + 0.005


def shelf_unit(R, loc, w, h, d=0.4, levels=3, col="#8a5a30"):
    p = pivot("shelf", loc, R)
    wm = WD(col, "#6a4220", scale=3, bump=0.6)
    for sx in (-1, 1):
        box("side", (0.07, d, h), wm, p, loc=(sx * (w / 2 - 0.035), 0, 0), base=True)
    box("back", (w, 0.03, h), WDT("#5a3a24", "#4a2e1e"), p, loc=(0, d / 2 - 0.015, 0), base=True)
    for k in range(levels + 1):
        box("lev", (w, d, 0.06), wm, p, loc=(0, 0, k * (h - 0.06) / levels), base=True)
    return p


def jar_cookie(R, loc, r=0.28, h=0.55):
    jar(R, loc, r, h, content="#c98a3c", lid="#a06a3e", gl=False)
    for i in range(4):
        ellipsoid("ck", 0.1, toon("#b87a30", rim=0.4), R, loc=(loc[0] + math.cos(i * 1.6) * r * 0.45, loc[1] + math.sin(i * 1.6) * r * 0.4, loc[2] + 0.1 + (i % 2) * 0.08),
                  scale=(1, 1, 0.4), seg=8, rings=6)


def desk_lamp(R, loc, c="#e8b04a"):
    p = pivot("dl", loc, R)
    frustum("b", 0.12, 0.1, 0.04, toon("#3a3a4a", rim=0.4), p, seg=10)
    link_cyl("a1", (0, 0, 0.04), (0.1, 0, 0.35), 0.015, toon("#3a3a4a", rim=0.4), p, seg=5)
    link_cyl("a2", (0.1, 0, 0.35), (-0.05, 0, 0.55), 0.015, toon("#3a3a4a", rim=0.4), p, seg=5)
    frustum("sh", 0.14, 0.05, 0.14, toon(c, rim=0.5), p, loc=(-0.05, 0, 0.5), seg=10, caps=(False, False))
    ellipsoid("bu", 0.06, glow("#ffd98a", 5), p, loc=(-0.05, 0, 0.5), seg=8, rings=6)
    ellipsoid("ha", 0.4, glow("#ffd98a", 1.4, alpha=0.3, soft=True), p, loc=(-0.05, -0.05, 0.45), seg=10, rings=6)


def monitor(R, loc, screen_col="#2a8f6a", kind="folder", body="#d9cfb8"):
    p = pivot("mon", loc, R)
    bm = PL(body, "#c9bea6", wear=0.4, plane="xz", bump=0.3)
    box("body", (0.7, 0.62, 0.58), bm, p, loc=(0, 0.0, 0.13), base=False, bevel=0.04)
    box("scr", (0.54, 0.04, 0.42), toon("#0c1a1a", rim=0.6), p, loc=(0, -0.33, 0.14))
    box("glass", (0.5, 0.03, 0.38), glow(screen_col, 1.6), p, loc=(0, -0.35, 0.14))
    if kind == "folder":
        box("fold", (0.2, 0.02, 0.14), toon("#f2c24a", rim=0.2), p, loc=(-0.06, -0.37, 0.14))
        box("fold2", (0.1, 0.02, 0.05), toon("#f2c24a", rim=0.2), p, loc=(-0.11, -0.37, 0.23))
    else:
        box("note", (0.2, 0.02, 0.2), toon("#fff07a", rim=0.2), p, loc=(0.1, -0.37, 0.16), rot=(0, RAD(6), 0))
        for k in range(3):
            box("ln", (0.14, 0.02, 0.012), toon("#6a4a2a", rim=0), p, loc=(0.1, -0.385, 0.2 - k * 0.05), rot=(0, RAD(6), 0))
    box("neck", (0.4, 0.4, 0.1), bm, p, loc=(0, 0.05, -0.2))
    box("kb", (0.62, 0.22, 0.04), bm, p, loc=(0, -0.55, -0.27), rot=(RAD(-6), 0, 0))
    for r in range(3):
        box("keys", (0.54, 0.05, 0.02), toon("#a89e8a", rim=0.3), p, loc=(0, -0.5 - r * 0.06, -0.24 + 0.0), rot=(RAD(-6), 0, 0))
    ellipsoid("led", 0.02, glow("#7dffb0", 4), p, loc=(0.28, -0.33, -0.12), seg=5, rings=4)


def chair_wood(R, loc, rot=0.0, col="#9a6238", seat="#c44b3f", back=True):
    p = pivot("chair", loc, R, rot=(0, 0, rot))
    for sx in (-1, 1):
        for sy in (-1, 1):
            box("leg", (0.06, 0.06, 0.5), WDT(col, col), p, loc=(sx * 0.22, sy * 0.22, 0), base=True)
    box("seat", (0.52, 0.52, 0.07), FAB("weave", seat, "#f3e4c4", scale=10, plane="xy", bump=0.5), p, loc=(0, 0, 0.5))
    if back:
        for sx in (-1, 1):
            box("post", (0.06, 0.06, 0.55), WDT(col, col), p, loc=(sx * 0.22, 0.22, 0.5), base=True)
        box("rail", (0.5, 0.05, 0.12), WD(col, col, scale=3), p, loc=(0, 0.22, 0.95))
        box("rail2", (0.5, 0.05, 0.1), WD(col, col, scale=3), p, loc=(0, 0.22, 0.75))
    return p


# ================================================================== GRANDMA
def g_tablet(R):
    wm = WD("#a06a3e", "#85502c", scale=3, bump=0.7)
    for sx in (-1, 1):
        link_cyl("leg", (sx * 0.45, -0.2, 0), (sx * 0.12, 0.1, 1.35), 0.05, wm, R, seg=6)
    link_cyl("legb", (0, 0.5, 0), (0, 0.1, 1.35), 0.05, wm, R, seg=6)
    box("ledge", (1.0, 0.18, 0.07), wm, R, loc=(0, -0.12, 0.7))
    p = pivot("tab", (0, -0.15, 0.78), R, rot=(RAD(-18), 0, 0))
    box("tab", (0.9, 0.06, 0.62), toon("#2a2a30", rim=0.5), p, loc=(0, 0, 0.31), bevel=0.03)
    box("scr", (0.78, 0.03, 0.5), toon("#08080c", rim=0.8), p, loc=(0, -0.04, 0.31))
    box("refl", (0.2, 0.01, 0.4), toon("#26263a", rim=0), p, loc=(-0.25, -0.06, 0.31), rot=(0, RAD(18), 0))
    ellipsoid("btn", 0.03, glow("#4f7ad8", 3), p, loc=(0.0, -0.04, 0.03), seg=6, rings=4)
    paper_sheet(R, (0.0, -0.3, 0.52), (0.42, 0.3), rot=(RAD(-18), 0, 0))
    box("tape", (0.1, 0.015, 0.04), toon("#4f7ad8", rim=0.2), R, loc=(0.0, -0.31, 0.65), rot=(RAD(-18), 0, 0))
    if EL.TRUTH:
        for a, b in (((-0.3, 0.3), (0.0, 0.0)), ((0.0, 0.0), (0.25, -0.15)), ((0.0, 0.0), (0.1, 0.25))):
            link_cyl("crack", (a[0], -0.08, 0.31 + a[1]), (b[0], -0.08, 0.31 + b[1]), 0.006, toon("#9aa6b8", rim=0), p, seg=3)
        cobweb(R, (-0.5, -0.2, 1.4), 0.4)


def g_scarf(R):
    round_table(R, (0, 0, 0), 0.55, 0.62, "#a06a3e")
    sm = FAB("knit", "#3a6ad0", "#5b8ae8", scale=16, plane="xz", bump=1.0)
    W = 0.36
    # scarf lying across the table and sliding over the edge to the floor, with a wavy tail
    v, f = [], []
    N = 18
    path = []
    for i in range(N + 1):
        t = i / N
        x = -0.5 + t * 1.6
        z = 0.66 if x < 0.45 else max(0.03, 0.66 - (x - 0.45) * 1.4 + 0.02 * math.sin(i))
        path.append((x, -0.05 + 0.18 * math.sin(t * 5) * (t > 0.6), z))
    for (x, y, z) in path:
        v += [(x, y - W / 2, z), (x, y + W / 2, z)]
    for i in range(N):
        f.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
    mesh_obj("scarf", v, f, sm, R, smooth=False)
    for k in (4, 8, 12):
        a = path[k]
        box("band", (0.05, W + 0.02, 0.012), FAB("knit", "#f3e4c4", "#d9c9a8", scale=18, plane="xy"), R, loc=(a[0], a[1], a[2] + 0.006))
    for i in range(7):
        box("fr", (0.025, 0.02, 0.14), toon("#f3e4c4", rim=0.2), R, loc=(path[-1][0] + 0.02, path[-1][1] - W / 2 + i * W / 6, 0.07))
    # unfinished end on the table with two needles through live stitches and a wool ball
    ball = yarn_ball(R, (-0.3, 0.2, 0.66), 0.18, "#3a6ad0", "#f3e4c4")
    for s in (-1, 1):
        link_cyl("needle", (-0.55, s * 0.12 - 0.02, 0.72), (-0.05, s * 0.1, 0.9), 0.014, toon("#d9c9a8", rim=0.5), R, seg=5)
        ellipsoid("nk", 0.03, toon("gold", rim=0.5), R, loc=(-0.05, s * 0.1, 0.9), seg=6, rings=4)
    box("tag", (0.18, 0.012, 0.12), toon("#f3e4c4", rim=0.2), R, loc=(-0.45, -0.3, 0.66))
    if EL.TRUTH:
        cut_thread(R, (-0.2, -0.28, 0.7), 0.5)


def g_photos(R):
    cols = [("#e8884a", "#6a3a7a"), ("#4f7ad8", "#2f6b48"), ("#e8b04a", "#a94a62"), ("#35b39a", "#3e4486"), ("#c44b3f", "#6a3f73")]
    pos = [(-0.9, 1.45, 0.62, 0.8), (-0.1, 1.55, 0.7, 0.9), (0.75, 1.4, 0.6, 0.75), (-0.7, 0.55, 0.7, 0.8), (0.2, 0.5, 0.6, 0.7)]
    for (x, z, w, h), (a, b) in zip(pos, cols):
        frame_picture(R, (x, 0, z), w, h, a, b)
    frame_picture(R, (1.0, 0, 0.5), 0.62, 0.78, "#ffffff", "#ffffff", empty=True)     # the missing last picture
    box("note", (0.34, 0.02, 0.2), tex_toon("paper", "#f3e8cc", "#2a2a60", scale=5, plane="xz", bump=0.1), R, loc=(1.0, -0.1, 0.45), rot=(0, RAD(4), 0))
    for k in range(6):   # nails + string
        pass
    tube("str", [(-1.3, -0.03, 2.2), (0, -0.03, 2.0), (1.3, -0.03, 2.2)], 0.008, toon("#d9c9a8", rim=0), R)
    if EL.TRUTH:
        box("outline", (0.5, 0.012, 0.66), toon("#e0d8c4", rim=0), R, loc=(1.0, -0.085, 0.5))   # clean rectangle where a frame hung
        scratches(R, (0.7, -0.09, 0.9), 3, 0.35)
    return {"cell": (384, 320), "anchor": (192, 280)}


def g_cookies(R):
    round_table(R, (0, 0, 0), 0.5, 0.85, "#c98a52", cloth="#c44b3f")
    jar_cookie(R, (0, 0, 0.86), 0.26, 0.5)
    paper_sheet(R, (0.0, -0.3, 1.02), (0.22, 0.14), rot=(RAD(-60), 0, 0), a="#f3e4c4", b="#c44b3f", scale=6)
    for i in range(3):   # crumbs / loose cookies
        ellipsoid("c", 0.07, toon("#b87a30", rim=0.4), R, loc=(0.3 + i * 0.07, -0.15 + 0.1 * i, 0.89), scale=(1, 1, 0.35), seg=8, rings=5)
    cup(R, (-0.28, -0.1, 0.86), full=not EL.TRUTH)


def g_cat(R):
    gm = tex_toon("stripes", "#8e8a98", "#6e6a7a", scale=9, plane="xz", bump=0.2, rim=0.5, ao=0.3)
    th = glow("#4f7ad8", 2.4)
    for k in range(4):   # coil of blue thread
        frustum("coil", 0.55 - k * 0.08, 0.55 - k * 0.08, 0.03, th, R, loc=(0, 0, 0.02 + k * 0.03), seg=20)
    tube("tail_thread", [(0.4, -0.2, 0.05), (0.9, -0.5, 0.02), (1.4, -0.4, 0.015), (1.8, -0.1, 0.012)], 0.02, th, R)
    ellipsoid("body", 0.38, gm, R, loc=(0, 0.02, 0.5), scale=(0.9, 0.9, 1.15), seg=16, rings=10)
    ellipsoid("head", 0.26, toon("#9a96a6", rim=0.5), R, loc=(0, -0.12, 1.0), seg=14, rings=10)
    for s in (-1, 1):
        frustum("ear", 0.1, 0.0, 0.2, toon("#8e8a98", rim=0.4), R, loc=(s * 0.16, -0.1, 1.17), seg=3, rot=(0, s * RAD(12), 0))
        ellipsoid("eye", 0.05, glow("#ffd86a", 5), R, loc=(s * 0.1, -0.34, 1.04), seg=6, rings=4)
        ellipsoid("paw", 0.1, gm, R, loc=(s * 0.14, -0.3, 0.1), scale=(1, 1.3, 0.7), seg=8, rings=6)
    ellipsoid("nose", 0.03, toon("#e8a0a0", rim=0), R, loc=(0, -0.38, 0.95), seg=6, rings=4)
    tube("tail", [(0.3, 0.1, 0.1), (0.7, 0.0, 0.08), (0.85, -0.15, 0.25), (0.8, -0.3, 0.5)], 0.075, gm, R)
    if EL.TRUTH:
        scratches(R, (-0.5, -0.1, 0.4), 3, 0.25)


def g_window(R):
    # sill overlay: curtains tied back, two teacups (one extra, empty), a small plant
    cm = FAB("weave", "#e07a3c", "#f3e4c4", scale=14, bump=0.6)
    rod_z = 2.9
    link_cyl("rod", (-1.55, -0.12, rod_z), (1.55, -0.12, rod_z), 0.03, toon("gold", rim=0.5), R, seg=6)
    for s in (-1, 1):
        N = 8
        v, f = [], []
        torn = EL.TRUTH
        for i in range(N + 1):
            t = i / N
            x0 = s * (1.35 - 0.0) + s * 0.0
            xw = s * (0.65 + 0.7 * (1 - abs(0.5 - t) * 0)) if False else None
        for i in range(N + 1):
            z = rod_z - 0.05 - i * (3.6 / N) * 0.82
            tie = 0.35 if 3 <= i <= 4 else 0.7        # tie-back pinches the curtain
            xin = s * (1.35 - tie)
            xout = s * 1.42
            if torn and i > 5:
                xin = s * (1.35 - tie * (0.4 + 0.15 * (i % 2)))
                z -= 0.12 * (i % 2)
            v += [(xin, -0.14 - 0.03 * math.sin(i), z), (xout, -0.12, z)]
        for i in range(N):
            f.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
        mesh_obj("curtain", v, f, cm, R, smooth=False)
        box("tie", (0.5, 0.06, 0.05), toon("gold", rim=0.5), R, loc=(s * 1.15, -0.2, rod_z - 3 * 0.47))
    cup(R, (-0.55, -0.15, 0.02), full=not EL.TRUTH)
    cup(R, (0.0, -0.2, 0.02), full=False)                                   # the extra, empty cup
    plant_pot(R, (0.75, -0.15, 0.0), 0.16, 0.2, kind="flower" if not EL.TRUTH else "fern", seed=7, pot="#6aa090")
    if EL.TRUTH:
        dead_plant(R, (0.75, -0.15, 0.25), 0.4, seed=5)
        paper_sheet(R, (-0.2, -0.3, 0.12), (0.24, 0.16), rot=(RAD(-80), 0, 0), a="#efe4cc", b="#9a9ab0", scale=6)
    return {"cell": (384, 400), "anchor": (192, 330)}


def g_armchair(R):
    fm = WD("#7a4a2a", "#6a3c20", scale=3)
    up = FAB("knit", "#c44b3f", "#a53a30", scale=10, bump=0.9, rim=0.4)
    box("base", (1.3, 1.1, 0.35), up, R, loc=(0, 0, 0.1), base=True, bevel=0.05)
    box("seat", (1.0, 0.85, 0.22), FAB("knit", "#d95a4a", "#c44b3f", scale=10, bump=0.9, rim=0.4), R, loc=(0, -0.05, 0.42), base=True, bevel=0.05)
    box("back", (1.3, 0.3, 1.15), up, R, loc=(0, 0.4, 0.35), base=True, bevel=0.07)
    for s in (-1, 1):
        box("arm", (0.25, 1.0, 0.55), up, R, loc=(s * 0.62, -0.02, 0.35), base=True, bevel=0.07)
        box("foot", (0.1, 0.1, 0.12), fm, R, loc=(s * 0.55, -0.45, 0), base=True)
        box("foot", (0.1, 0.1, 0.12), fm, R, loc=(s * 0.55, 0.45, 0), base=True)
    box("blanket", (0.9, 0.5, 0.05), FAB("weave", "#4f7ad8", "#f3e4c4", scale=8, plane="xy"), R, loc=(0.1, -0.1, 0.64), rot=(0, 0, RAD(12)))
    ellipsoid("cush", 0.3, FAB("knit", "#e8b04a", "#d9983a", scale=12), R, loc=(-0.3, 0.1, 0.9), scale=(1, 0.5, 0.9), seg=12, rings=8)
    if EL.TRUTH:
        ellipsoid("dent", 0.4, toon("#3a3040", rim=0), R, loc=(0, -0.05, 0.56), scale=(1, 0.8, 0.12), seg=10, rings=6)    # empty chair, a dent
        cobweb(R, (0.6, 0.3, 1.45), 0.3)


def g_wool_basket(R):
    frustum("bk", 0.5, 0.42, 0.45, FAB("weave", "#b07a46", "#8a5a30", scale=12, bump=1.0), R, seg=18)
    frustum("bkr", 0.52, 0.52, 0.06, toon("#8a5a30", rim=0.3), R, loc=(0, 0, 0.42), seg=18)
    cols = ["#4f7ad8", "#e8b04a", "#c44b3f", "#35b39a", "#a07ad8", "#f3e4c4", "#e8884a"]
    for i in range(8):
        a = i * 0.8
        yarn_ball(R, (math.cos(a) * 0.22, math.sin(a) * 0.2, 0.4 + (i % 2) * 0.1), 0.13, cols[i % 7], cols[(i + 3) % 7])
    for s in (-1, 1):
        link_cyl("n", (s * 0.1, 0, 0.5), (s * 0.35, -0.05, 1.1), 0.014, toon("#d9c9a8", rim=0.5), R, seg=5)
    if EL.TRUTH:
        weaver_knot(R, (0.35, -0.5, 0.3), 0.07)


def g_spinning_wheel(R):
    wd = WD("#a06a3e", "#85502c", scale=4, bump=0.7)
    p = pivot("sw", (0, 0, 0), R, rot=(0, 0, RAD(0)))
    box("bench", (1.2, 0.2, 0.1), wd, p, loc=(0, 0, 0.55))
    for sx in (-1, 1):
        link_cyl("leg", (sx * 0.5, 0, 0.55), (sx * 0.6, sx * 0.0 + 0.2, 0), 0.04, wd, p, seg=5)
        link_cyl("leg", (sx * 0.5, 0, 0.55), (sx * 0.65, -0.2, 0), 0.04, wd, p, seg=5)
    wr = 0.6
    wp = pivot("wheel", (0.2, -0.15, 1.2), p)
    frustum("rim", wr, wr, 0.06, wd, wp, rot=(RAD(90), 0, 0), seg=28, caps=(False, False))
    for k in range(8):
        a = k * math.pi / 4
        link_cyl("sp", (0, 0, 0), (math.cos(a) * wr, 0, math.sin(a) * wr), 0.02, wd, wp, seg=4)
    ellipsoid("hub", 0.07, toon("gold", rim=0.5), wp, seg=8, rings=6)
    for s in (-1, 1):
        link_cyl("post", (-0.4, s * 0.0, 0.6), (-0.4, 0, 1.4), 0.04, wd, p, seg=5)
    link_cyl("spindle", (-0.55, 0, 1.15), (-0.1, 0, 1.15), 0.025, toon("#d9c9a8", rim=0.5), p, seg=5)
    ellipsoid("wool", 0.14, toon("#f3e4c4", rim=0.3), p, loc=(-0.6, 0, 1.15), scale=(1.5, 1, 1), seg=10, rings=8)
    tube("band", [(0.2 + wr, -0.15, 1.2), (-0.1, -0.1, 1.15), (0.2 - wr, -0.15, 1.2)], 0.008, toon("#d9c9a8", rim=0), p)
    box("treadle", (0.6, 0.18, 0.04), wd, p, loc=(0.2, -0.2, 0.15), rot=(0, RAD(8), 0))
    if EL.TRUTH:
        cobweb(R, (-0.6, 0.0, 1.5), 0.35)


def g_floor_lamp(R):
    lamp_floor(R, (0, 0, 0), 2.0)


def g_tea_table(R):
    table(R, (0, 0, 0), 1.0, 0.7, 0.75, "#c98a52", "#85502c", cloth="#f3e4c4")
    frustum("pot", 0.17, 0.2, 0.2, toon("#4f7ad8", rim=0.5), R, loc=(0, 0, 0.77), seg=14)
    frustum("lid", 0.11, 0.03, 0.08, toon("#4f7ad8", rim=0.5), R, loc=(0, 0, 0.96), seg=10)
    link_cyl("spout", (0.16, 0, 0.88), (0.34, 0, 1.0), 0.03, toon("#4f7ad8", rim=0.5), R, seg=6)
    cup(R, (-0.3, -0.12, 0.76), full=not EL.TRUTH)
    cup(R, (0.25, -0.15, 0.76), full=not EL.TRUTH)
    for i in range(5):
        ellipsoid("ck", 0.06, toon("#c98a3c", rim=0.4), R, loc=(0.0 + i * 0.0 - 0.1 + (i % 3) * 0.1, -0.2 + (i // 3) * 0.1, 0.8), scale=(1, 1, 0.4), seg=8, rings=5)
    if EL.TRUTH:
        cobweb(R, (-0.4, 0.3, 1.0), 0.3)


def g_plant_big(R):
    plant_pot(R, (0, 0, 0), 0.4, 0.6, kind="fern", seed=12, leaf="leaf3")
    for k in range(5):
        a = k * 1.3
        ellipsoid("big", 0.22, toon(["leaf1", "leaf2", "leaf3"][k % 3], rim=0.4), R, loc=(math.cos(a) * 0.3, math.sin(a) * 0.25, 1.0 + 0.15 * k), scale=(1, 0.4, 1.6), rot=(0, 0, a), seg=10, rings=8)
    if EL.TRUTH:
        dead_plant(R, (0, 0, 0.6), 1.1, seed=4, n=9)


def g_bookshelf(R):
    shelf_unit(R, (0, 0, 0), 1.7, 1.9, 0.45, 3, "#8a5a30")
    books_row(R, (-0.75, 0, 0.62), 12, 0.42, seed=3)
    books_row(R, (-0.75, 0, 1.24), 9, 0.42, seed=5)
    yarn_ball(R, (0.4, 0, 1.28), 0.16, "#4f7ad8", "#f3e4c4")
    jar_cookie(R, (0.0, 0, 0.06), 0.18, 0.35)
    for i, c in enumerate(("#c44b3f", "#e8b04a", "#35b39a")):
        yarn_ball(R, (-0.5 + i * 0.4, 0, 0.07), 0.14, c, "#f3e4c4")
    plant_pot(R, (0.5, 0, 1.87), 0.13, 0.15, kind="flower", seed=3)
    if EL.TRUTH:
        cobweb(R, (-0.8, -0.2, 1.9), 0.35)
        book(R, (0.2, -0.4, 0.0), (0.4, 0.28, 0.06), "wine", rot=0.3)   # a book fallen to the floor


def g_footstool(R):
    frustum("st", 0.3, 0.3, 0.3, FAB("knit", "#35b39a", "#2a9a82", scale=10, bump=0.9), R, seg=14)
    frustum("top", 0.32, 0.3, 0.05, FAB("weave", "#f3e4c4", "#e8b04a", scale=14, plane="xy"), R, loc=(0, 0, 0.3), seg=14)
    yarn_ball(R, (0.1, -0.05, 0.35), 0.12, "#c44b3f", "#f3e4c4", needles=True)


GRANDMA = {"g_tablet": g_tablet, "g_scarf": g_scarf, "g_photos": g_photos, "g_cookies": g_cookies, "g_cat": g_cat,
           "g_window": g_window, "x_armchair": g_armchair, "x_wool_basket": g_wool_basket, "x_spinning_wheel": g_spinning_wheel,
           "x_floor_lamp": g_floor_lamp, "x_tea_table": g_tea_table, "x_plant": g_plant_big, "x_bookshelf": g_bookshelf,
           "x_footstool": g_footstool}


# ================================================================== CLINIC
def c_cabinet(R):
    mm = tex_toon("plain", "#5a7a72", "#4a6a62", scale=2.5, bump=0.4, wear=0.6, rim=0.5)
    box("body", (1.3, 0.7, 2.5), mm, R, loc=(0, 0, 0), base=True, bevel=0.03)
    box("top", (1.4, 0.8, 0.08), toon("#3f5a54", rim=0.4), R, loc=(0, 0, 2.5), base=True)
    box("win", (0.9, 0.04, 1.0), toon("#101818", rim=0.8), R, loc=(0, -0.37, 1.5))
    box("glass", (0.82, 0.03, 0.92), glow("#7ad8b0", 0.6, alpha=0.25), R, loc=(0, -0.39, 1.5))
    # old computer inside: beige tower + CRT with a green glow
    box("tower", (0.34, 0.4, 0.8), PL("#d9cfb8", "#c9bea6", plane="xz", wear=0.4), R, loc=(-0.2, -0.1, 1.15), base=True)
    box("crt", (0.4, 0.3, 0.32), PL("#d9cfb8", "#c9bea6", plane="xz", wear=0.4), R, loc=(0.18, -0.12, 1.15), base=True)
    box("crts", (0.3, 0.02, 0.22), glow("#4fe0a0", 2.4), R, loc=(0.18, -0.28, 1.31))
    for k in range(3):
        ellipsoid("led", 0.02, glow(["#7dffb0", "#ffd86a", "#7dffb0"][k], 5), R, loc=(-0.28 + k * 0.08, -0.31, 1.7), seg=5, rings=4)
    for k in range(5):
        box("vent", (0.5, 0.02, 0.03), toon("#2a3a36", rim=0), R, loc=(0, -0.36, 0.7 + k * 0.08))
    box("lock", (0.18, 0.05, 0.22), toon("#c9bfae", rim=0.6), R, loc=(0.52, -0.37, 1.1))
    frustum("shackle", 0.06, 0.06, 0.08, toon("#c9bfae", rim=0.6), R, loc=(0.52, -0.4, 1.17), rot=(RAD(90), 0, 0), seg=10, caps=(False, False))
    box("plate", (0.5, 0.02, 0.14), toon("#f3f0e4", rim=0.3), R, loc=(0, -0.36, 2.25))
    for k in range(4):
        box("txt", (0.36 - k * 0.05, 0.01, 0.012), toon("#4a4a50", rim=0), R, loc=(-0.02, -0.375, 2.29 - k * 0.03))
    ellipsoid("hum", 0.6, glow("#35d3b0", 0.5, alpha=0.2, soft=True), R, loc=(0, -0.5, 1.4), scale=(1, 0.3, 1.2), seg=10, rings=6)
    if EL.TRUTH:
        scratches(R, (-0.5, -0.37, 2.1), 4, 0.9)
        weaver_knot(R, (0.0, -0.45, 0.45), 0.08)


def c_notes(R):
    paper_sheet(R, (0, -0.02, 0.4), (0.7, 0.9), a="#fff07a", b="#4a3a2a", scale=5)
    for s in (-1, 1):
        ellipsoid("pin", 0.04, toon("#c44b3f", rim=0.6), R, loc=(s * 0.2, -0.05, 0.8), seg=6, rings=4)
    ln = tex_toon("paper", "#fff07a", "#2a4a9a", scale=7, plane="xz", bump=0, wear=0)
    box("second", (0.55, 0.012, 0.3), ln, R, loc=(0, -0.035, 0.18))        # second handwriting (blue)
    if EL.TRUTH:
        box("erase", (0.5, 0.014, 0.18), toon("#d9d070", rim=0), R, loc=(0.0, -0.045, 0.24), rot=(0, RAD(-4), 0))   # half-erased
        paper_sheet(R, (0.1, -0.06, 0.14), (0.26, 0.16), rot=(0, RAD(10), 0), a="#efe4cc", b="#8a8aa0", scale=8)
    return {"cell": (256, 256), "anchor": (128, 200)}


def c_drawer(R):
    wm = WD("#9a6238", "#85502c", scale=3, bump=0.7)
    box("body", (1.2, 0.7, 1.7), wm, R, loc=(0, 0, 0), base=True, bevel=0.03)
    box("top", (1.3, 0.78, 0.07), WDT("#7a4a2a", "#6a3c20"), R, loc=(0, 0, 1.7), base=True)
    for k in range(3):
        z = 0.12 + k * 0.52
        out = 0.0
        if k == 1:
            out = 0.28
        box("dr", (1.0, 0.04 + out, 0.45), WD("#a8703c", "#8a5a30", scale=4, bump=0.6), R, loc=(0, -0.36 - out / 2, z), base=True)
        box("hand", (0.3, 0.06, 0.05), toon("gold", rim=0.6), R, loc=(0, -0.42 - out, z + 0.3))
        box("lab", (0.26, 0.02, 0.1), toon("#f3f0e4", rim=0.2), R, loc=(0, -0.4 - out, z + 0.12))
        if k == 1:
            for j in range(4):
                paper_sheet(R, (-0.3 + j * 0.2, -0.5 - out, z + 0.46), (0.2, 0.3), rot=(RAD(-8 - 4 * j), 0, RAD(j * 5 - 8)), a="#f3e8cc", b="#5a5a70", scale=5)
    if EL.TRUTH:
        scratches(R, (0.45, -0.37, 1.45), 3, 0.5)


def c_password(R):
    wd = WD("#8a5a30", "#704826", scale=3)
    for sx in (-1, 1):
        link_cyl("leg", (sx * 0.5, -0.2, 0), (sx * 0.2, 0.15, 1.5), 0.04, wd, R, seg=5)
    link_cyl("legb", (0, 0.5, 0), (0, 0.15, 1.5), 0.04, wd, R, seg=5)
    box("board", (1.0, 0.06, 0.9), PL("#d8c4a0", "#c9b48a", plane="xz", wear=0.2), R, loc=(0, -0.12, 1.2))
    paper_sheet(R, (0, -0.17, 1.2), (0.78, 0.7), a="#fff07a", b="#222222", scale=2.2)
    link_cyl("big1", (-0.28, -0.19, 1.2), (0.3, -0.19, 1.2), 0.03, toon("#2a2a2a", rim=0), R, seg=4)
    tube("circ", [(math.cos(t) * 0.22 + 0.1, -0.2, math.sin(t) * 0.18 + 1.2) for t in [i * 0.4 for i in range(17)]], 0.014, toon("#c44b3f", rim=0.2), R)
    box("ledge", (0.9, 0.12, 0.05), wd, R, loc=(0, -0.2, 0.74))
    if EL.TRUTH:
        scratches(R, (-0.4, -0.2, 1.5), 3, 0.4)


def c_bed(R):
    wd = WD("#e8e4d4", "#d4d0c0", scale=3, bump=0.5)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box("leg", (0.1, 0.1, 0.5), toon("#9aa8a4", rim=0.5), R, loc=(sx * 0.95, sy * 0.5, 0), base=True)
    box("frame", (2.2, 1.2, 0.12), wd, R, loc=(0, 0, 0.5))
    box("mat", (2.1, 1.1, 0.22), FAB("weave", "#f3f0e4", "#dfe8d8", scale=14, plane="xy", bump=0.5), R, loc=(0, 0, 0.62), bevel=0.04)
    ellipsoid("pil", 0.38, FAB("weave", "#ffffff", "#dfe8d8", scale=16), R, loc=(-0.7, 0, 0.9), scale=(1, 1.3, 0.45), seg=12, rings=8)
    box("blank", (1.0, 1.14, 0.12), FAB("weave", "#8fc4aa", "#cfe8d8", scale=9, plane="xy", bump=0.8), R, loc=(0.5, 0, 0.8))
    box("head", (0.1, 1.3, 0.6), wd, R, loc=(-1.1, 0, 0.5))
    box("stool", (0.4, 0.4, 0.05), WD("#c9b48a", "#a88a5a", scale=3, plane="xy"), R, loc=(-1.0, -0.95, 0.5), rot=(0, 0, 0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            box("sl", (0.04, 0.04, 0.5), WDT(), R, loc=(-1.0 + sx * 0.15, -0.95 + sy * 0.15, 0), base=True)
    frustum("mug", 0.09, 0.08, 0.13, toon("#f3f0e4", rim=0.5), R, loc=(-1.0, -0.95, 0.55), seg=12)
    frustum("milk", 0.075, 0.075, 0.01, toon("#fff7e8", rim=0.2), R, loc=(-1.0, -0.95, 0.66), seg=10)
    ellipsoid("steam", 0.1, glow("#ffffff", 1, alpha=0.2, soft=True), R, loc=(-1.0, -0.95, 0.8), scale=(1, 1, 1.5), seg=8, rings=6)
    if EL.TRUTH:
        scratches(R, (0.3, -0.62, 0.7), 4, 0.15, rot=(0, 0, 0))
        box("tear", (0.25, 1.0, 0.01), toon("#2a2a34", rim=0), R, loc=(1.0, 0.0, 0.75))
        cobweb(R, (-1.15, 0.5, 1.05), 0.3)


def c_clock(R):
    wm = WD("#8a5a30", "#704826", scale=3, along="v")
    frustum("fr", 0.45, 0.45, 0.1, wm, R, loc=(0, -0.05, 0.6), rot=(RAD(90), 0, 0), seg=28)
    frustum("face", 0.38, 0.38, 0.04, toon("#f3f0e4", rim=0.2), R, loc=(0, -0.11, 0.6), rot=(RAD(90), 0, 0), seg=28)
    for k in range(12):
        a = k * math.pi / 6
        box("tick", (0.03, 0.01, 0.07 if k % 3 == 0 else 0.04), toon("#3a2a22", rim=0), R,
            loc=(math.sin(a) * 0.31, -0.135, 0.6 + math.cos(a) * 0.31), rot=(0, -a, 0))
    h = 3 * math.pi / 2 if EL.TRUTH else 0.7           # truth: stopped at 3:00 (and cracked)
    link_cyl("hh", (0, -0.14, 0.6), (math.sin(h) * 0.2, -0.14, 0.6 + math.cos(h) * 0.2), 0.02, toon("#2a2a2a", rim=0), R, seg=4)
    m = 0.0 if EL.TRUTH else 2.4
    link_cyl("mh", (0, -0.15, 0.6), (math.sin(m) * 0.3, -0.15, 0.6 + math.cos(m) * 0.3), 0.014, toon("#2a2a2a", rim=0), R, seg=4)
    ellipsoid("pin", 0.03, toon("gold", rim=0.5), R, loc=(0, -0.16, 0.6), seg=6, rings=4)
    link_cyl("pend", (0, -0.1, 0.15), (0, -0.1, -0.55), 0.01, toon("gold", rim=0.5), R, seg=4)
    frustum("bob", 0.1, 0.1, 0.04, toon("gold", rim=0.6), R, loc=(0, -0.1, -0.62), rot=(RAD(90), 0, 0), seg=14)
    if EL.TRUTH:
        for a, b in (((-0.3, 0.25), (0.0, 0.0)), ((0.0, 0.0), (0.25, -0.2)), ((0.0, 0.0), (-0.1, -0.3))):
            link_cyl("crk", (a[0], -0.14, 0.6 + a[1]), (b[0], -0.14, 0.6 + b[1]), 0.005, toon("#8a96a8", rim=0), R, seg=3)
    return {"cell": (256, 320), "anchor": (128, 140)}


def c_herb_shelf(R):
    box("b1", (1.6, 0.3, 0.06), WD("#9a6238", "#85502c", scale=3, plane="xy"), R, loc=(0, -0.12, 0.0))
    box("b2", (1.6, 0.3, 0.06), WD("#9a6238", "#85502c", scale=3, plane="xy"), R, loc=(0, -0.12, 0.75))
    for x in (-0.7, 0.7):
        box("br", (0.05, 0.28, 0.75), WDT(), R, loc=(x, -0.12, 0.0), base=True)
    cs = ["#d68f3a", "#6fa04a", "#c44b3f", "#8a6ac8", "#d9c24a", "#4f8a5a"]
    for i in range(6):
        jar(R, (-0.62 + i * 0.25, -0.12, 0.03), 0.09, 0.24, content=cs[i], gl=False)
        jar(R, (-0.55 + i * 0.22, -0.12, 0.78), 0.08, 0.2, content=cs[(i + 2) % 6], gl=False)
    return {"cell": (320, 256), "anchor": (160, 180)}


def c_desk(R):
    table(R, (0, 0, 0), 1.6, 0.8, 0.8, "#c9b48a", "#8a6a40")
    for k in range(2):
        box("dr", (0.5, 0.7, 0.2), WD("#b89a6a", "#8a6a40", scale=3), R, loc=(-0.5, 0, 0.35 + k * 0.2), base=False)
    book_stack(R, (0.4, 0, 0.8), 4, seed=3)
    paper_sheet(R, (-0.3, -0.15, 0.82), (0.5, 0.35), rot=(RAD(-88), 0, 0), a="#f3f0e4", b="#4a4a70", scale=5)
    desk_lamp(R, (-0.65, 0.2, 0.8), "#4f9a7a")
    cup(R, (0.1, -0.2, 0.81), 0.07, 0.09, full=not EL.TRUTH)
    chair_wood(R, (0, -0.95, 0), rot=math.pi, col="#8a6a40", seat="#4f9a7a")
    return {"cell": (384, 320), "anchor": (192, 236)}


def c_stool(R):
    frustum("seat", 0.3, 0.3, 0.07, FAB("weave", "#4f9a7a", "#cfe8d8", scale=10, plane="xy"), R, loc=(0, 0, 0.5), seg=14)
    for k in range(3):
        a = k * 2.094
        link_cyl("leg", (math.cos(a) * 0.15, math.sin(a) * 0.15, 0.5), (math.cos(a) * 0.3, math.sin(a) * 0.3, 0), 0.03, WDT(), R, seg=5)


def c_trolley(R):
    mt = toon("#9aa8a4", rim=0.6)
    for sx in (-1, 1):
        for sy in (-1, 1):
            frustum("post", 0.025, 0.025, 1.0, mt, R, loc=(sx * 0.45, sy * 0.28, 0.1), seg=5)
            ellipsoid("wheel", 0.07, toon("#3a3a44", rim=0.3), R, loc=(sx * 0.45, sy * 0.28, 0.07), seg=8, rings=6)
    for z in (0.3, 0.7, 1.1):
        box("shelf", (1.0, 0.64, 0.04), mt, R, loc=(0, 0, z))
    for i in range(4):
        frustum("bt", 0.06, 0.05, 0.2, glow(["#d68f3a", "#6fa04a", "#c44b3f", "#8a6ac8"][i], 1.2), R, loc=(-0.35 + i * 0.22, 0, 0.72), seg=8)
    box("bowl", (0.3, 0.2, 0.1), toon("#f3f0e4", rim=0.5), R, loc=(0.0, 0, 0.34 + 0.0))
    for i in range(3):
        ellipsoid("roll", 0.07, toon("#ffffff", rim=0.4), R, loc=(-0.3 + i * 0.18, 0.05, 1.18), scale=(1.4, 1, 1), seg=8, rings=6)
    return {"cell": (256, 288), "anchor": (128, 200)}


def c_screen(R):
    pm = FAB("weave", "#f3f0e4", "#dfe8d8", scale=10, bump=0.4)
    for k in range(3):
        p = pivot("pan", (-0.7 + k * 0.7, 0.1 * (k % 2), 0), R, rot=(0, 0, RAD(15 if k % 2 else -15)))
        box("fr", (0.72, 0.06, 1.8), WD("#c9b48a", "#a88a5a", scale=3), p, loc=(0, 0, 0), base=True)
        box("pn", (0.6, 0.04, 1.65), pm, p, loc=(0, -0.04, 0.08), base=True)
        ellipsoid("lf", 0.25, toon("#6fa07a", rim=0.3), p, loc=(0, -0.08, 0.9), scale=(0.5, 0.1, 1.3), rot=(0, RAD(20 * (k - 1)), 0), seg=10, rings=8)
    if EL.TRUTH:
        cobweb(R, (-1.0, 0.0, 1.8), 0.4)
    return {"cell": (352, 288), "anchor": (176, 210)}


def c_planter(R):
    box("pl", (1.4, 0.4, 0.4), WD("#9a6238", "#7d4a2a", scale=3), R, base=True)
    box("so", (1.3, 0.34, 0.04), toon("#4a3426", rim=0), R, loc=(0, 0, 0.4), base=True)
    hz = ["#4f9a4f", "#6cb257", "#2f6b48", "#8fb04a", "#7a5a9a", "#c79ae8"]
    for k in range(9):
        ellipsoid("h", 0.13, toon(hz[k % 6], rim=0.35), R, loc=(-0.55 + k * 0.14, 0, 0.55 + 0.06 * (k % 3)), scale=(1, 1, 1.2), seg=8, rings=6)
    if EL.TRUTH:
        dead_plant(R, (0, 0, 0.42), 0.6, seed=8, n=10)


def c_basin(R):
    box("tb", (0.8, 0.5, 0.8), WD("#c9b48a", "#8a6a40", scale=3), R, base=True)
    frustum("bowl", 0.26, 0.2, 0.1, toon("#f3f0e4", rim=0.5), R, loc=(0, 0, 0.8), seg=14)
    frustum("water", 0.22, 0.22, 0.01, glow("#bfe8f0", 0.8), R, loc=(0, 0, 0.88), seg=12)
    frustum("jug", 0.1, 0.12, 0.3, toon("#4f9a7a", rim=0.5), R, loc=(0.25, 0.1, 0.8), seg=12)
    box("towel", (0.3, 0.04, 0.4), FAB("weave", "#f3f0e4", "#cfe8d8", scale=14), R, loc=(-0.5, 0.0, 0.5), rot=(0, RAD(5), 0))
    link_cyl("rail", (-0.5, 0, 0.7), (-0.5, 0, 0.7), 0.01, WDT(), R, seg=3) if False else None
    return {"cell": (256, 256), "anchor": (128, 190)}


CLINIC = {"c_cabinet": c_cabinet, "c_notes": c_notes, "c_drawer": c_drawer, "c_password": c_password, "c_bed": c_bed,
          "c_clock": c_clock, "x_herb_shelf": c_herb_shelf, "x_desk": c_desk, "x_stool": c_stool, "x_trolley": c_trolley,
          "x_screen": c_screen, "x_planter": c_planter, "x_basin": c_basin}


# ================================================================== PRINT HOUSE
def p_printer(R):
    pw = WD("#c48a50", "#a87238", scale=3, along="v")
    for x in (-0.75, 0.75):
        box("post", (0.2, 0.3, 2.2), pw, R, loc=(x, 0, 0), base=True)
    box("topb", (1.9, 0.34, 0.26), WD("#c48a50", "#a87238", scale=3), R, loc=(0, 0, 2.2), base=True)
    frustum("screw", 0.12, 0.12, 1.5, WD("#6a4220", "#583518", scale=5, along="v"), R, loc=(0, 0, 0.8), seg=10)
    for z in [0.95 + i * 0.12 for i in range(10)]:
        frustum("thr", 0.16, 0.16, 0.04, toon("#4a2e16", rim=0.2), R, loc=(0, 0, z), seg=10)
    link_cyl("bar", (-1.1, 0, 1.55), (1.1, 0, 1.8), 0.05, toon("#3a2a22", rim=0.3), R, seg=6)
    for s in (-1, 1):
        ellipsoid("wt", 0.13, toon("#3a2a22", rim=0.4), R, loc=(s * 1.1, 0, 1.55 + (0.25 if s > 0 else 0)), seg=8, rings=6)
    box("platen", (1.2, 0.9, 0.14), WD("#a06a3e", "#85502c", scale=4), R, loc=(0, 0, 0.65), base=True)
    box("bed", (1.8, 1.0, 0.2), WD("#7a5030", "#6a4426", scale=3), R, loc=(0, 0, 0.0), base=True)
    box("tray", (0.7, 0.5, 0.05), WD("#8a5a30", "#704826", scale=4, plane="xy"), R, loc=(0.0, -0.75, 0.22))
    for i in range(4):
        paper_sheet(R, (-0.2 + i * 0.1, -0.78, 0.26 + i * 0.012), (0.32, 0.01), rot=(RAD(90), 0, 0), a="#f3e8cc", b="#2a3a8a", scale=4)
    box("pg", (0.5, 0.4, 0.012), tex_toon("paper", "#f3e8cc", "#2a3a8a", scale=3, plane="xy", bump=0.1), R, loc=(0, -0.2, 0.2), base=True)
    ellipsoid("ink", 0.2, toon("#1f2f66", rim=0.5), R, loc=(0.8, -0.45, 0.14), scale=(1.6, 1, 0.4), seg=10, rings=6)
    frustum("roller", 0.06, 0.06, 0.4, toon("#1f2f66", rim=0.5), R, loc=(0.8, -0.45, 0.25), rot=(0, RAD(90), 0), seg=8)
    if EL.TRUTH:
        cobweb(R, (-0.75, -0.15, 2.2), 0.5)
    return {"cell": (384, 400), "anchor": (192, 290)}


def p_stack(R):
    table(R, (0, 0, 0), 1.2, 0.8, 0.7, "#8a6a60", "#5a3a30")
    for k, (x, y) in enumerate([(-0.3, 0.0), (0.3, 0.0)]):
        z = 0.7
        for j in range(5):
            box("pile", (0.5, 0.4, 0.07), tex_toon("paper", "#f3e8cc", "#2a3a8a", scale=4, plane="xy", bump=0.15), R, loc=(x + 0.01 * (j % 2), y, z + j * 0.07), base=True)
        paper_sheet(R, (x, y - 0.2, z + 0.18), (0.46, 0.34), rot=(RAD(-80), 0, 0), a="#f3e8cc", b="#2a3a8a", scale=4)
    ellipsoid("warm", 0.7, glow("#ff9a4a", 0.5, alpha=0.25, soft=True), R, loc=(0, 0, 0.9), scale=(1.2, 1, 0.6), seg=10, rings=6)
    return {"cell": (320, 288), "anchor": (160, 200)}


def _pc_desk(R, col, screen, kind, chair_c):
    table(R, (0, 0, 0), 1.5, 0.85, 0.78, col, "#4a3040")
    monitor(R, (-0.15, 0.05, 1.2), screen, kind)
    chair_wood(R, (0, -0.95, 0), rot=math.pi, col="#4a3040", seat=chair_c)
    cup(R, (0.55, -0.1, 0.79), 0.07, 0.09, full=not EL.TRUTH)
    paper_sheet(R, (0.5, 0.15, 0.8), (0.3, 0.2), rot=(RAD(-88), 0, 0), a="#f3e8cc", b="#2a3a8a", scale=5)
    return {"cell": (384, 340), "anchor": (192, 250)}


def p_pc_yoel(R):
    r = _pc_desk(R, "#8a6a60", "#4f9ad8", "folder", "#4f7ad8")
    if EL.TRUTH:
        cobweb(R, (-0.7, 0.4, 1.6), 0.3)
    return r


def p_pc_rachel(R):
    r = _pc_desk(R, "#7a5a70", "#e8d86a", "note", "#a07ad8")
    tube("cable", [(-0.6, 0.3, 0.7), (-1.2, 0.2, 0.3), (-1.4, 0.0, 0.02)], 0.02, toon("#2a2a3a", rim=0.2), R)
    if EL.TRUTH:
        cut_thread(R, (0.7, 0.2, 0.78), 0.5)
    return r


def p_cal(R):
    box("pg", (0.9, 0.04, 1.25), PL("#f3e8cc", "#e0d4b0", plane="xz", wear=0.2), R, loc=(0, -0.03, 0.6))
    box("hd", (0.9, 0.05, 0.3), toon("#4f7ad8" if not EL.TRUTH else "#3a4a6a", rim=0.3), R, loc=(0, -0.06, 1.1))
    for r in range(5):
        for c in range(6):
            box("cell", (0.1, 0.012, 0.11), toon("#d9cfb8", rim=0), R, loc=(-0.38 + c * 0.15, -0.055, 0.82 - r * 0.2 + 0.0))
            box("num", (0.06, 0.012, 0.02), toon("#4a3a5a", rim=0), R, loc=(-0.38 + c * 0.15, -0.065, 0.84 - r * 0.2))
    tube("circ", [(-0.08 + math.cos(t) * 0.1, -0.075, 0.42 + math.sin(t) * 0.1) for t in [i * 0.4 for i in range(17)]], 0.012, toon("#2a3a9a", rim=0.2), R)
    box("quiet", (0.08, 0.012, 0.018), toon("#2a3a9a", rim=0), R, loc=(-0.08, -0.08, 0.42))
    ellipsoid("pin", 0.04, toon("#c44b3f", rim=0.6), R, loc=(0, -0.06, 1.2), seg=6, rings=4)
    if EL.TRUTH:
        box("smudge", (0.5, 0.012, 0.2), toon("#c8b898", rim=0), R, loc=(0.1, -0.07, 0.62), rot=(0, RAD(6), 0))
    return {"cell": (256, 256), "anchor": (128, 150)}


def p_box(R):
    cm = PL("#b08a5a", "#9a7646", wear=0.5, plane="xz", bump=0.6)
    box("bx", (1.0, 0.8, 0.55), cm, R, loc=(0, 0, 0), base=True, bevel=0.02)
    box("flapl", (0.5, 0.3, 0.03), cm, R, loc=(-0.45, -0.5, 0.45), rot=(0, RAD(-30), 0), base=True)
    box("flapr", (0.5, 0.3, 0.03), cm, R, loc=(0.45, -0.5, 0.45), rot=(0, RAD(30), 0), base=True)
    for k in range(6):
        box("strip", (0.8, 0.04, 0.03), tex_toon("paper", "#f3e8cc", "#2a3a8a", scale=6, plane="xz", bump=0.1), R, loc=(0, -0.2 + 0.1 * (k % 3) - 0.1, 0.55 + 0.02 * k), rot=(0, RAD(k * 3), RAD(k * 8)), base=True)
    # sleeping messenger: glowing round envelope with a little cap and closed eyes
    ellipsoid("env", 0.2, glow("#ffe9a8", 1.6), R, loc=(0, -0.05, 0.7), scale=(1.2, 0.8, 0.9), seg=12, rings=8)
    box("flap", (0.3, 0.02, 0.1), toon("#f3e4c4", rim=0.4), R, loc=(0, -0.28, 0.82), rot=(RAD(-30), 0, 0))
    for s in (-1, 1):
        link_cyl("eye", (s * 0.1 - 0.04, -0.27, 0.72), (s * 0.1 + 0.04, -0.27, 0.72), 0.008, toon("#3a2a22", rim=0), R, seg=3)
    frustum("cap", 0.1, 0.03, 0.12, toon("#c44b3f", rim=0.4), R, loc=(0.0, -0.05, 0.86), seg=10)
    ellipsoid("z", 0.05, glow("#ffffff", 2, alpha=0.5, soft=True), R, loc=(0.3, -0.25, 1.05), seg=6, rings=4)
    if EL.TRUTH:
        # a teal thread tied round the box in a two-turn weaver's knot
        for z in (0.2, 0.3):
            frustum("tw", 0.51, 0.51, 0.02, glow("#35d3b0", 3), R, loc=(0, 0, z), seg=4, rot=(0, 0, RAD(45)), caps=(False, False), scale=(1.0, 0.82, 1))
        weaver_knot(R, (0.0, -0.45, 0.35), 0.09)
    return {"cell": (288, 288), "anchor": (144, 200)}


def p_type_case(R):
    box("cs", (1.3, 0.8, 0.9), WD("#8a5a30", "#704826", scale=3), R, base=True, bevel=0.02)
    box("tp", (1.4, 0.7, 0.06), WDT("#6a4220", "#583518"), R, loc=(0, -0.05, 0.9), base=True)
    for r in range(3):
        for c in range(5):
            box("cmp", (0.18, 0.02, 0.18), toon("#3a2a22", rim=0), R, loc=(-0.45 + c * 0.22, -0.405, 0.15 + r * 0.25))
            box("typ", (0.1, 0.02, 0.1), toon("#c9bfae", rim=0.6), R, loc=(-0.45 + c * 0.22, -0.415, 0.15 + r * 0.25))
        box("hand", (0.12, 0.04, 0.03), toon("gold", rim=0.5), R, loc=(0.58, -0.42, 0.15 + r * 0.25))
    return {"cell": (288, 256), "anchor": (144, 190)}


def p_paper_cabinet(R):
    box("cs", (1.0, 0.7, 2.2), WD("#7a5638", "#6a4830", scale=3, along="v"), R, base=True, bevel=0.02)
    for k in range(6):
        box("dr", (0.84, 0.04, 0.3), WD("#8a6444", "#6a4830", scale=4), R, loc=(0, -0.36, 0.1 + k * 0.34), base=True)
        box("hd", (0.2, 0.05, 0.04), toon("gold", rim=0.6), R, loc=(0, -0.4, 0.22 + k * 0.34))
        paper_sheet(R, (0.0, -0.39, 0.3 + k * 0.34), (0.16, 0.07), a="#f3e8cc", b="#2a3a8a", scale=8)
    box("top", (1.1, 0.78, 0.07), WDT("#5a4030", "#4a3228"), R, loc=(0, 0, 2.2), base=True)
    if EL.TRUTH:
        cobweb(R, (-0.5, -0.4, 2.2), 0.35)
    return {"cell": (288, 352), "anchor": (144, 260)}


def p_ink_shelf(R):
    shelf_unit(R, (0, 0, 0), 1.5, 1.6, 0.35, 2, "#6a4a58")
    cs = ["#4f7ad8", "#1f2f66", "#a07ad8", "#2f6b48", "#c44b3f"]
    for r in range(2):
        for i in range(7):
            frustum("ink", 0.07, 0.06, 0.18, glow(cs[(i + r) % 5], 1.0), R, loc=(-0.6 + i * 0.2, 0, 0.06 + r * 0.77), seg=8)
            frustum("cap", 0.035, 0.035, 0.05, toon("#2a2a2a", rim=0.4), R, loc=(-0.6 + i * 0.2, 0, 0.24 + r * 0.77), seg=6)
    books_row(R, (-0.6, 0, 1.54), 0, 0)
    return {"cell": (288, 288), "anchor": (144, 210)}


def p_bin(R):
    frustum("bn", 0.32, 0.26, 0.5, FAB("weave", "#8a6a50", "#6a4a38", scale=12, bump=1.0), R, seg=12, caps=(False, True))
    rnd = random.Random(2)
    for i in range(9):
        ellipsoid("cr", 0.12, tex_toon("paper", "#f3e8cc", "#2a3a8a", scale=6, bump=0.8, wear=0), R, loc=(rnd.uniform(-.18, .18), rnd.uniform(-.18, .18), 0.5 + rnd.uniform(0, 0.15)), seg=6, rings=4)
    for i in range(3):
        ellipsoid("cr", 0.1, toon("#f3e8cc", rim=0.3), R, loc=(0.35 + i * 0.15, -0.2 + i * 0.1, 0.08), seg=6, rings=4)
    return {"cell": (224, 224), "anchor": (112, 150)}


def p_lamp(R):
    lamp_floor(R, (0, 0, 0), 1.9, shade="#b8a0d8", glow_c="#e8c8ff")


def p_stool(R):
    frustum("seat", 0.28, 0.28, 0.07, WD("#8a5a30", "#704826", scale=3, plane="xy"), R, loc=(0, 0, 0.55), seg=14)
    for k in range(3):
        a = k * 2.094 + 0.5
        link_cyl("leg", (math.cos(a) * 0.15, math.sin(a) * 0.15, 0.55), (math.cos(a) * 0.3, math.sin(a) * 0.3, 0), 0.035, WDT(), R, seg=5)
    book(R, (0.0, 0, 0.62), (0.3, 0.22, 0.06), "#4f7ad8", rot=0.3)


def p_newspapers(R):
    for sx in (-1, 1):
        box("post", (0.06, 0.4, 1.2), WDT(), R, loc=(sx * 0.5, 0, 0), base=True)
    for z in (0.1, 0.6):
        box("rail", (1.0, 0.06, 0.05), WDT(), R, loc=(0, -0.15, z))
    for i in range(6):
        c = ["#e8e0c8", "#d8d0b8", "#f3e8cc"][i % 3]
        box("np", (0.14, 0.05, 0.55), tex_toon("paper", c, "#2a2a60", scale=5, plane="xz", bump=0.1), R, loc=(-0.36 + i * 0.15, -0.16, 0.63), rot=(RAD(-4), 0, 0), base=True)
    return {"cell": (256, 256), "anchor": (128, 190)}


PRINT = {"p_printer": p_printer, "p_stack": p_stack, "p_pc_yoel": p_pc_yoel, "p_pc_rachel": p_pc_rachel, "p_cal": p_cal,
         "p_box": p_box, "x_type_case": p_type_case, "x_paper_cabinet": p_paper_cabinet, "x_ink_shelf": p_ink_shelf,
         "x_bin": p_bin, "x_lamp": p_lamp, "x_stool": p_stool, "x_newspapers": p_newspapers}

OBJECTS = {"house_grandma": GRANDMA, "house_clinic": CLINIC, "house_print": PRINT}
