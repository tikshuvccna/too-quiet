"""World-2 interior objects, part B: workshop, library, observatory, stories, farm."""
import math
import random

from iw2_lib import *  # noqa
from iw2_objs_a import fire, steam, mug, plate


# ------------------------------------------------------------------ shared bits
BRASS = "#d9b05a"


def clock_face(parent, loc, r=0.3, hands=True, hh=0.7, mm=2.4, frame="#8a5a30", face="#f3f0e4"):
    p = pivot("clk", loc, parent)
    frustum("fr", r * 1.15, r * 1.15, 0.1, WD(frame, frame, scale=4), p, rot=(RAD(90), 0, 0), seg=24)
    frustum("fc", r, r, 0.04, toon(face, rim=0.2), p, loc=(0, -0.08, 0), rot=(RAD(90), 0, 0), seg=24)
    for k in range(12):
        a = k * math.pi / 6
        box("tk", (0.02, 0.01, 0.06 if k % 3 == 0 else 0.035), toon("#3a2a22", rim=0), p, loc=(math.sin(a) * r * 0.82, -0.125, math.cos(a) * r * 0.82), rot=(0, -a, 0))
    if hands:
        link_cyl("hh", (0, -0.14, 0), (math.sin(hh) * r * 0.5, -0.14, math.cos(hh) * r * 0.5), 0.016, toon("#2a2a2a", rim=0), p, seg=4)
        link_cyl("mh", (0, -0.15, 0), (math.sin(mm) * r * 0.75, -0.15, math.cos(mm) * r * 0.75), 0.011, toon("#2a2a2a", rim=0), p, seg=4)
    ellipsoid("pin", 0.03, toon("gold", rim=0.5), p, loc=(0, -0.16, 0), seg=6, rings=4)
    return p


def wrench(R, loc, L=0.5, col="#9aa6b8", rot=(0, 0, 0)):
    p = pivot("wr", loc, R, rot=rot)
    m = toon(col, rim=0.7)
    box("h", (0.05, 0.03, L), m, p, loc=(0, 0, -L / 2))
    frustum("hd", 0.08, 0.08, 0.03, m, p, rot=(RAD(90), 0, 0), seg=6)
    box("jw", (0.05, 0.03, 0.08), toon("#2a2a30", rim=0.3), p, loc=(0.05, 0, 0.0))
    return p


def hammer(R, loc, L=0.5, rot=(0, 0, 0)):
    p = pivot("hm", loc, R, rot=rot)
    box("h", (0.045, 0.045, L), WD("#a06a3e", "#85502c", scale=5, along="v"), p, loc=(0, 0, -L / 2))
    box("hd", (0.2, 0.07, 0.08), toon("#6a6a74", rim=0.7), p, loc=(0, 0, 0.02))
    return p


def pliers(R, loc, L=0.4, rot=(0, 0, 0)):
    p = pivot("pl", loc, R, rot=rot)
    for s in (-1, 1):
        link_cyl("a", (s * 0.015, 0, -L), (s * 0.04, 0, 0), 0.016, toon("#c44b3f", rim=0.4), p, seg=5)
    box("j", (0.1, 0.02, 0.08), toon("#6a6a74", rim=0.7), p, loc=(0, 0, 0.04))
    return p


def pegboard(R, w, h, col="#8a6a48"):
    box("bd", (w, 0.06, h), WD(col, col, scale=3, along="v"), R, loc=(0, -0.03, h / 2))
    for i in range(int(w / 0.25)):
        for j in range(int(h / 0.25)):
            ellipsoid("pg", 0.012, toon("#2a1e1a", rim=0), R, loc=(-w / 2 + 0.15 + i * 0.25, -0.065, 0.15 + j * 0.25), scale=(1, 0.3, 1), seg=4, rings=3)


def brass_dial(R, loc, r=0.14, ang=0.8):
    p = pivot("dial", loc, R)
    frustum("rim", r, r, 0.04, toon(BRASS, rim=0.7), p, rot=(RAD(90), 0, 0), seg=18)
    frustum("fc", r * 0.82, r * 0.82, 0.03, toon("#f3f0e4", rim=0.2), p, loc=(0, -0.035, 0), rot=(RAD(90), 0, 0), seg=18)
    link_cyl("nd", (0, -0.07, 0), (math.sin(ang) * r * 0.7, -0.07, math.cos(ang) * r * 0.7), 0.01, toon("#a02a2a", rim=0), p, seg=4)
    return p


# ==================================================================== WORKSHOP
def w_gears(R):
    box("bd", (3.5, 0.08, 3.2), WD("#5a3a24", "#4a2e1c", scale=3, along="v"), R, loc=(0, -0.04, 1.6))
    box("fr", (3.7, 0.1, 0.12), WDT(), R, loc=(0, -0.06, 3.22))
    box("fr", (3.7, 0.1, 0.12), WDT(), R, loc=(0, -0.06, -0.02))
    spec = [(-0.85, 1.85, 0.85, 14, "#9a7a4a"), (0.45, 2.15, 0.5, 9, "#b4854a"), (1.05, 1.15, 0.5, 9, "#8a6a40"), (-1.15, 0.5, 0.5, 9, "#b4854a"),
            (0.0, 1.0, 0.36, 7, "#9a7a4a"), (1.15, 2.6, 0.3, 6, "#8a6a40"), (-0.35, 0.3, 0.3, 6, "#b4854a")]
    cols = {}
    for (x, z, r, n, c) in spec:
        gear(R, (x, -0.1, z), r, n, 0.12, c if not T() else "#7a7a84", spokes=r > 0.4)
    # gold thread weaving between the gears
    pts = [(-1.5, -0.3, 1.2), (-1.6, -0.3, 2.2), (-0.85, -0.3, 2.75), (0.0, -0.3, 2.2), (0.45, -0.3, 1.62), (0.9, -0.3, 1.75), (1.05, -0.3, 0.6), (0.4, -0.3, 0.7),
           (0.0, -0.3, 0.6), (-0.7, -0.3, 0.25), (-1.3, -0.3, 0.1)]
    tthread(R, pts, 0.022, 3.4, "#ffd86a")
    halo(R, (0.0, -0.3, 1.5), 1.6, 0.1, "#ffd86a", 0.8)
    if T():
        for k in range(5):
            tube("gt", [(-1.5 + k * 0.7, -0.2, 3.1), (-1.2 + k * 0.7, -0.25, 2.2), (-1.4 + k * 0.7, -0.2, 1.0)], 0.007, toon(GREY, rim=0), R)
        cobweb(R, (-1.7, -0.15, 3.1), 0.5)
    return {"cell": (512, 520), "anchor": (256, 400)}


def w_tester(R):
    table(R, (0, 0, 0), 0.9, 0.7, 0.8, "#8a6a48", "#5a3a24")
    p = pivot("dev", (0, 0, 0.82), R)
    box("bx", (0.7, 0.45, 0.4), toon("#c0693f", rim=0.7), p, loc=(0, 0, 0), base=True, bevel=0.03)
    box("pn", (0.62, 0.03, 0.32), toon("#6a3a28", rim=0.4), p, loc=(0, -0.24, 0.2))
    brass_dial(p, (-0.16, -0.27, 0.22), 0.11, 0.9)
    brass_dial(p, (0.14, -0.27, 0.22), 0.09, -0.6)
    for k in range(3):
        ellipsoid("kn", 0.03, toon(BRASS, rim=0.7), p, loc=(-0.18 + k * 0.18, -0.27, 0.07), seg=6, rings=4)
    # crank handle
    link_cyl("ck", (0.35, 0, 0.2), (0.5, 0, 0.2), 0.02, toon(BRASS, rim=0.7), p, seg=5)
    link_cyl("ck2", (0.5, 0, 0.2), (0.5, -0.12, 0.28), 0.02, toon(BRASS, rim=0.7), p, seg=5)
    # bell on top
    frustum("bl", 0.2, 0.05, 0.22, toon(BRASS, rim=0.8), p, loc=(0, 0, 0.4), seg=16)
    ellipsoid("cl", 0.04, toon("#2a2a30", rim=0.5), p, loc=(0, 0, 0.42), seg=6, rings=4)
    link_cyl("st", (0, 0, 0.62), (0, 0, 0.7), 0.012, toon("#2a2a30", rim=0.5), p, seg=4)
    # coiled wire / thread leaving the box
    tube("wr", [(-0.35, 0, 0.1), (-0.7, -0.1, 0.0), (-1.1, -0.2, 0.02), (-1.5, -0.3, 0.03)], 0.02, toon("#2a2a30", rim=0.3), R)
    if T():
        # the bell rings silently in blue: concentric rings, then the thread stops
        for k, rr in enumerate((0.26, 0.38, 0.5)):
            frustum("rg", rr, rr, 0.015, glow(BLUE, 3.0 - k * 0.6, alpha=0.7), p, loc=(0, 0, 0.5 + k * 0.1), seg=20, caps=(False, False))
        halo(p, (0, 0, 0.55), 0.7, 0.3, BLUE)
        tthread(R, [(-0.35, 0, 0.9), (-0.8, -0.1, 0.8), (-1.2, -0.2, 0.5), (-1.5, -0.3, 0.15)], 0.012, 3.0)
        ellipsoid("end", 0.04, glow(TEAL, 5), R, loc=(-1.5, -0.3, 0.15), seg=6, rings=4)
        cobweb(R, (0.4, 0.2, 1.4), 0.3)
    else:
        ellipsoid("gl", 0.03, glow("#ffd890", 4), p, loc=(0.0, 0.0, 0.7), seg=5, rings=4)
    return {}


def w_clocks(R):
    shelf = WD("#6a4630", "#553622", scale=3)
    box("sh", (3.0, 0.4, 0.08), shelf, R, loc=(0, -0.2, 0.0))
    for s in (-1, 1):
        box("br", (0.08, 0.3, 0.4), shelf, R, loc=(s * 1.35, -0.2, -0.2))
    spec = [(-1.1, 0.34, 0.7, 2.4), (-0.4, 0.28, 1.4, 0.3), (0.35, 0.36, 4.0, 1.2), (1.1, 0.3, None, None)]
    for x, r, hh, mm in spec:
        if T():
            clock_face(R, (x, -0.15, 0.1 + r * 1.15), r, hh is not None, 3 * math.pi / 2 * 0 + math.pi / 2, 0.0, "#5a5a64", "#8a8e98")
        else:
            clock_face(R, (x, -0.15, 0.1 + r * 1.15), r, hh is not None, hh or 0, mm or 0)
        link_cyl("pen", (x, -0.1, 0.1), (x, -0.1, -0.55), 0.008, toon("gold", rim=0.5), R, seg=3) if False else None
    if T():
        # the handless clock leads a fine thread to the tower
        tthread(R, [(1.1, -0.2, 0.4), (1.3, -0.2, 1.0), (1.6, -0.25, 1.8), (2.1, -0.3, 2.6)], 0.012, 3.2)
        halo(R, (1.1, -0.2, 0.4), 0.45, 0.25)
        for x in (-1.1, -0.4, 0.35):
            crack_fx(R, (x + 0.1, -0.22, 0.5), 0.25)
    return {}


def w_bench(R):
    wd = WD("#9a6a3e", "#7a4e2a", scale=3, bump=0.8)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box("lg", (0.14, 0.14, 0.85), WDT(), R, loc=(sx * 0.75, sy * 0.3, 0), base=True)
    box("tp", (1.9, 0.8, 0.12), wd, R, loc=(0, 0, 0.85))
    box("sh", (1.7, 0.6, 0.05), WDT(), R, loc=(0, 0, 0.3))
    # vise on the left end
    box("vs", (0.3, 0.2, 0.18), toon("#3a3a44", rim=0.6), R, loc=(-0.78, -0.45, 0.97))
    link_cyl("vh", (-0.78, -0.55, 1.0), (-0.78, -0.8, 1.0), 0.02, toon("#3a3a44", rim=0.6), R, seg=5)
    ellipsoid("vk", 0.04, toon("#3a3a44", rim=0.6), R, loc=(-0.78, -0.82, 1.0), seg=6, rings=4)
    # half-made gear, ruler, clamp, mallet, shavings, pencil jar
    gear(R, (0.1, -0.1, 1.04), 0.2, 8, 0.05, "#c9a06a", rot=(0, 0, 0), spokes=False)
    box("ru", (0.7, 0.07, 0.015), toon("#e8d6a0", rim=0.2), R, loc=(0.35, 0.22, 0.92), rot=(0, 0, RAD(6)))
    for k in range(8):
        box("tk", (0.01, 0.07, 0.016), toon("#3a2a22", rim=0), R, loc=(0.05 + k * 0.09, 0.22, 0.925), rot=(0, 0, RAD(6)))
    hammer(R, (-0.1, 0.25, 0.9), 0.3, rot=(RAD(90), 0, RAD(40)))
    for k in range(8):
        ellipsoid("sv", 0.04, toon("#e8d6a0", rim=0.2), R, loc=(0.4 + (k % 4) * 0.1, -0.2 + (k // 4) * 0.12, 0.92), scale=(1.6, 1, 0.3), seg=6, rings=4)
    jar(R, (0.75, 0.2, 0.92), 0.07, 0.16, content="#6a4a2a")
    for k in range(3):
        link_cyl("pc", (0.72 + k * 0.03, 0.2, 1.08), (0.72 + k * 0.05, 0.2, 1.28), 0.01, toon(["#c44b3f", "#e8b04a", "#4f7ad8"][k], rim=0.3), R, seg=4)
    # a rope off-cut with a perfectly clean, flat cut
    rm = tex_toon("weave", "#c9b48a", "#8a7450", scale=40, plane="xz", bump=1.0, rim=0.3, ao=0)
    tube("rp", [(0.55, -0.15, 0.93), (0.75, -0.2, 0.93), (0.95, -0.12, 0.93)], 0.03, rm, R)
    box("ct", (0.02, 0.07, 0.07), toon("#f6efe0", rim=0.6) if not T() else glow(TEAL, 4), R, loc=(0.55, -0.15, 0.93))
    if T():
        tthread(R, [(0.55, -0.15, 0.95), (0.3, -0.25, 0.98), (0.0, -0.3, 0.95)], 0.012, 3.2)
        halo(R, (0.55, -0.15, 0.95), 0.35, 0.3)
        cobweb(R, (-0.85, 0.3, 1.3), 0.4)
    return {}


def w_note(R):
    box("bd", (0.95, 0.06, 1.15), WD("#6a4630", "#553622", scale=3), R, loc=(0, -0.03, 0.58))
    box("ck", (0.85, 0.04, 1.05), tex_toon("plain", "#c49a64", "#a9824e", scale=7, plane="xz", bump=1.2, wear=0, rim=0.2) if not T() else toon("#8a7a64", rim=0.2), R, loc=(0, -0.07, 0.58))
    box("pp", (0.55, 0.03, 0.7), tex_toon("paper", "#f3e8cc", "#2a3a8a", scale=4, plane="xz", bump=0.1, wear=0), R, loc=(0, -0.11, 0.6), rot=(0, RAD(3), 0))
    inkc = glow(TEAL, 3.4) if T() else toon("#1f2f66", rim=0)
    for k in range(5):
        box("ln", (0.4 - 0.06 * (k % 2), 0.012, 0.03), inkc, R, loc=(-0.02, -0.135, 0.8 - k * 0.1), rot=(0, RAD(3), 0))
    # erased line below (smudge) and a second hint
    box("er", (0.38, 0.012, 0.035), toon("#d8cca8", rim=0), R, loc=(0.0, -0.135, 0.3), rot=(0, RAD(3), 0))
    if T():
        box("er2", (0.3, 0.012, 0.02), glow(TEAL, 1.6), R, loc=(0.0, -0.14, 0.3), rot=(0, RAD(3), 0))
        halo(R, (0, -0.15, 0.6), 0.6, 0.18)
    ellipsoid("pin", 0.04, toon("#c44b3f", rim=0.6), R, loc=(0, -0.14, 0.97), seg=6, rings=4)
    return {}


def w_tool_rack(R):
    # tall pegboard cabinet with tools
    wd = WD("#5a3a24", "#4a2e1c", scale=3)
    box("fr", (1.7, 0.3, 2.4), wd, R, loc=(0, 0.1, 0), base=True, bevel=0.02)
    pb = pivot("pb", (0, -0.05, 0.1), R)
    pegboard(pb, 1.5, 2.2)
    for i, x in enumerate((-0.55, -0.25, 0.05, 0.35, 0.6)):
        wrench(R, (x, -0.1, 1.9), 0.55 - 0.05 * (i % 3), rot=(0, 0, 0))
    hammer(R, (-0.5, -0.1, 1.1), 0.5)
    hammer(R, (-0.15, -0.1, 1.1), 0.42)
    pliers(R, (0.25, -0.1, 1.15), 0.4)
    pliers(R, (0.55, -0.1, 1.15), 0.32)
    box("sh", (1.4, 0.2, 0.05), WDT(), R, loc=(0, -0.12, 0.55))
    for k in range(4):
        frustum("tn", 0.07, 0.07, 0.12, toon(["#c44b3f", "#e8b04a", "#4f7ad8", "#6a6a74"][k], rim=0.5), R, loc=(-0.5 + k * 0.33, -0.12, 0.6), seg=8)
    if T():
        cobweb(R, (-0.8, -0.1, 2.4), 0.4)


def w_grinder(R):
    frustum("ft", 0.3, 0.32, 0.07, toon("#3a3a44", rim=0.6), R, seg=10)
    frustum("po", 0.08, 0.08, 0.85, toon("#3a3a44", rim=0.6), R, loc=(0, 0, 0.05), seg=8)
    box("fm", (0.7, 0.12, 0.1), toon("#3a3a44", rim=0.6), R, loc=(0, 0, 0.9))
    for s in (-1, 1):
        frustum("wh", 0.2, 0.2, 0.1, tex_toon("stone", "#a8a09a", "#8c848a", scale=6, plane="xz", bump=0.6), R, loc=(s * 0.36, 0.0, 1.0), rot=(RAD(90), 0, 0), seg=18)
    box("sh", (0.2, 0.1, 0.12), toon("#2a2a30", rim=0.4), R, loc=(0, -0.1, 1.0))
    link_cyl("hd", (0.4, 0.1, 0.9), (0.5, 0.1, 1.2), 0.02, toon("#3a3a44", rim=0.6), R, seg=5)
    if not T():
        for k in range(4):
            ellipsoid("sp", 0.025, glow("#ffd070", 6), R, loc=(-0.5 - k * 0.1, -0.22 - k * 0.04, 1.0 - k * 0.08), seg=5, rings=4)
    else:
        cobweb(R, (0.2, 0.0, 1.3), 0.3)


def w_gear_bin(R):
    box("bn", (1.1, 0.8, 0.5), WD("#7a5a38", "#5a3a24", scale=4), R, base=True, bevel=0.02)
    box("in", (1.0, 0.7, 0.04), toon("#1a1214", rim=0), R, loc=(0, 0, 0.5))
    rnd = random.Random(3)
    for k in range(9):
        gear(R, (rnd.uniform(-0.35, 0.35), -0.0 + rnd.uniform(-0.1, 0.1), 0.5 + (k % 3) * 0.06), rnd.uniform(0.14, 0.26), 8 + k % 4, 0.05,
             ["#b4854a", "#9a7a4a", "#8a8a94"][k % 3], rot=(RAD(rnd.uniform(-70, -20)), 0, RAD(rnd.uniform(0, 360))), spokes=False)
    if T():
        cobweb(R, (-0.5, 0.3, 0.8), 0.3)


def w_anvil(R):
    frustum("st", 0.3, 0.34, 0.5, WD("#6a4630", "#553622", scale=4, along="v"), R, seg=12)
    am = toon("#4a4a58", rim=0.8)
    box("bs", (0.5, 0.3, 0.16), am, R, loc=(0, 0, 0.5), base=True)
    box("wt", (0.3, 0.2, 0.15), am, R, loc=(0, 0, 0.62), base=True)
    box("fc", (0.8, 0.3, 0.1), am, R, loc=(0, 0, 0.77), base=True)
    frustum("hn", 0.12, 0.0, 0.3, am, R, loc=(0.52, 0, 0.82), rot=(0, RAD(90), 0), seg=8)
    if not T():
        ellipsoid("gl", 0.1, glow("#ff7a22", 3.0), R, loc=(-0.1, 0, 0.9), scale=(1.6, 0.8, 0.3), seg=8, rings=5)
    else:
        cobweb(R, (-0.3, 0.1, 0.95), 0.3)


def w_parts_shelf(R):
    box("bd", (1.5, 0.45, 1.5), toon("#5a5a66", rim=0.6), R, base=True, bevel=0.02)
    for r in range(5):
        for c in range(4):
            box("dr", (0.3, 0.03, 0.2), toon("#7a7a88", rim=0.6), R, loc=(-0.55 + c * 0.37, -0.24, 0.15 + r * 0.28))
            box("lb", (0.16, 0.012, 0.06), toon("#e8d6a0", rim=0.2), R, loc=(-0.55 + c * 0.37, -0.26, 0.2 + r * 0.28))
            ellipsoid("kn", 0.022, toon(BRASS, rim=0.7), R, loc=(-0.55 + c * 0.37, -0.27, 0.13 + r * 0.28), seg=5, rings=4)
    if T():
        cobweb(R, (-0.7, -0.2, 1.5), 0.35)


# ==================================================================== LIBRARY
def book_blk(R, loc, n, h, seed, rot=0.0, d=0.28):
    books_row(R, loc, n, h, seed)


def l_catalog(R):
    wd = WD("#7a4a2a", "#5a3520", scale=3, bump=0.8)
    box("bd", (1.7, 0.6, 2.0), wd, R, base=True, bevel=0.02)
    box("tp", (1.8, 0.66, 0.07), WDT(), R, loc=(0, 0, 2.0), base=True)
    for r in range(8):
        for c in range(4):
            x, z = -0.62 + c * 0.41, 0.1 + r * 0.23
            out = 0.0
            if T() and r == 4 and c == 1:
                out = 0.25
            box("dr", (0.36, 0.04 + out, 0.19), WD("#9a6a3e", "#7a4e2a", scale=4), R, loc=(x, -0.32 - out / 2, z))
            box("lb", (0.2, 0.012, 0.07), toon("#e8d6a0", rim=0.2), R, loc=(x, -0.355 - out, z + 0.03))
            ellipsoid("kn", 0.022, toon(BRASS, rim=0.7), R, loc=(x, -0.37 - out, z - 0.04), seg=5, rings=4)
    if T():
        # cards pour out of one drawer; threads run from them to shelves on the left
        for k in range(5):
            box("cd", (0.2, 0.01, 0.12), toon("#e8d6a0", rim=0), R, loc=(-0.2 + k * 0.03, -0.6 + k * 0.0, 1.1 - 0.05 * k), rot=(RAD(-20), 0, RAD(k * 6)))
            tthread(R, [(-0.18 + k * 0.03, -0.55, 1.1), (-0.8 - k * 0.2, -0.5, 1.3 + k * 0.3), (-1.6 - k * 0.2, -0.45, 2.0 + k * 0.4)], 0.007, 3.0)
        halo(R, (-0.3, -0.5, 1.2), 0.7, 0.14)
        cobweb(R, (0.8, -0.3, 2.0), 0.4)
    return {}


def l_cover(R):
    top = lectern(R, (0, 0, 0), 1.05, 0.9, "#5a3a24", tilt=14)
    # big leather cover lying open, no pages
    lm = tex_toon("weave", "#6a2a30", "#4a1a22", scale=18, plane="xy", bump=0.8, rim=0.4, ao=0.3)
    for s in (-1, 1):
        box("cv", (0.42, 0.52, 0.04), lm, top, loc=(s * 0.21, 0.0, 0.05))
        box("rim", (0.42, 0.02, 0.05), toon("gold", rim=0.5), top, loc=(s * 0.21, 0.25, 0.06))
        box("rim", (0.42, 0.02, 0.05), toon("gold", rim=0.5), top, loc=(s * 0.21, -0.25, 0.06))
    box("sp", (0.03, 0.52, 0.06), toon("#4a1a22", rim=0.3), top, loc=(0, 0, 0.05))
    # inked "removed" stamp: round ring with a bar
    frustum("rg", 0.14, 0.14, 0.008, toon("#a02a2a", rim=0), top, loc=(0.2, -0.02, 0.075), seg=18, caps=(False, False))
    frustum("rg2", 0.11, 0.11, 0.008, toon("#a02a2a", rim=0), top, loc=(0.2, -0.02, 0.075), seg=18, caps=(False, False))
    box("br", (0.3, 0.03, 0.01), toon("#a02a2a", rim=0), top, loc=(0.2, -0.02, 0.08), rot=(0, 0, RAD(20)))
    # a thin slit (the gutter) where a weaver's knot is caught
    if T():
        weaver_knot(top, (0.0, -0.0, 0.14), 0.08)
        halo(top, (0, 0, 0.15), 0.4, 0.3)
        cobweb(R, (-0.4, 0.2, 1.4), 0.3)
    return {}


def l_stamp(R):
    table(R, (0, 0, 0), 1.2, 0.7, 0.8, "#7a4a2a", "#5a3520")
    # inkpad, stamp, strips of labels
    box("pd", (0.3, 0.22, 0.05), toon("#2a3a6a", rim=0.4), R, loc=(-0.3, 0.1, 0.84))
    box("pdi", (0.26, 0.18, 0.02), toon("#1f2f66", rim=0.5), R, loc=(-0.3, 0.1, 0.89))
    box("sb", (0.14, 0.14, 0.07), WD("#c98a52", "#85502c", scale=4), R, loc=(0.0, 0.0, 0.85))
    frustum("sh", 0.035, 0.03, 0.14, WD("#c98a52", "#85502c", scale=4), R, loc=(0.0, 0.0, 0.88), seg=8)
    ellipsoid("sk", 0.05, WD("#c98a52", "#85502c", scale=4), R, loc=(0.0, 0.0, 1.04), seg=8, rings=6)
    for k in range(6):
        c = ["#e8d6a0", "#c9e0b0", "#f0c8c8", "#c8d8f0", "#e8d6a0", "#d8c8f0"][k]
        lb = glow(TEAL if T() else c, 1.6 if T() else 1.0) if T() else toon(c, rim=0.2)
        box("lb", (0.2, 0.07, 0.012), lb, R, loc=(0.35 + (k % 2) * 0.1, -0.2 + (k // 2) * 0.1, 0.82 + k * 0.012), rot=(0, 0, RAD(k * 9 - 20)))
    if T():
        # every label leads to exactly one shelf: one thread each
        for k in range(3):
            tthread(R, [(0.35 + (k % 2) * 0.1, -0.2 + k * 0.1, 0.88), (0.2 - k * 0.3, -0.3, 1.5 + k * 0.4), (-0.6 - k * 0.6, -0.3, 2.4 + k * 0.4)], 0.007, 3.0)
        halo(R, (0.4, -0.1, 0.9), 0.5, 0.2)
    else:
        for k in range(3):
            ellipsoid("lbl", 0.035, toon("#c44b3f", rim=0.4), R, loc=(0.6, 0.15 + k * 0.05, 0.83), scale=(1, 1, 0.3), seg=6, rings=4)
    stool_round(R, (0, -0.8, 0), 0.26, 0.5)
    return {}


def l_ladder(R):
    # rolling library ladder, leaning to the shelves
    wd = WD("#8a5a30", "#6a4220", scale=4, along="v", bump=0.8)
    h = 3.0
    for s in (-1, 1):
        link_cyl("rl", (s * 0.35, 0.0, 0.0), (s * 0.3, 0.55, h), 0.04, wd, R, seg=6)
    for k in range(9):
        t = (k + 0.7) / 9.5
        y = 0.55 * t
        link_cyl("rg", (-0.35 + 0.05 * t, y, t * h), (0.35 - 0.05 * t, y, t * h), 0.03, wd, R, seg=5)
    link_cyl("hk", (-0.3, 0.55, h), (0.3, 0.55, h), 0.03, toon("#3a3a44", rim=0.6), R, seg=6)
    for s in (-1, 1):
        ellipsoid("wh", 0.07, toon("#3a3a44", rim=0.6), R, loc=(s * 0.36, 0.0, 0.07), scale=(0.4, 1, 1), seg=8, rings=6)
    if T():
        tthread(R, [(0.0, 0.55, h), (0.05, 0.3, 2.0), (0.2, -0.3, 0.9), (0.5, -0.9, 0.04), (1.0, -1.3, 0.02)], 0.012, 3.0, "#ffffff")
        halo(R, (0.0, 0.5, 2.8), 0.6, 0.15, "#ffffff")
        cobweb(R, (-0.3, 0.5, 3.0), 0.4)
    return {"cell": (384, 520), "anchor": (192, 440)}


def l_table(R):
    table(R, (0, 0, 0), 2.2, 1.1, 0.82, "#8a5a30", "#5a3520")
    # open big book with a map of two routes, one cut
    open_book(R, (-0.2, 0.0, 0.84), 1.0, 0.62, "forest", rot=(0, 0, RAD(3)), page="#efe0b0")
    for s in (-1, 1):
        box("map", (0.44, 0.52, 0.004), toon("#e8d6a0", rim=0), R, loc=(-0.2 + s * 0.25, 0.0, 0.905), rot=(0, 0, RAD(3)))
    pa = [(-0.6, -0.15), (-0.45, 0.05), (-0.3, -0.05), (-0.18, 0.12)]
    pb = [(-0.6, 0.18), (-0.4, 0.2), (-0.2, 0.05), (0.0, 0.1), (0.2, 0.2)]
    for a, b in zip(pa[:-1], pa[1:]):
        link_cyl("p1", (a[0], a[1], 0.915), (b[0], b[1], 0.915), 0.012, toon("#2a4a8a", rim=0), R, seg=3)
    for i, (a, b) in enumerate(zip(pb[:-1], pb[1:])):
        if i == 2:
            ellipsoid("cut", 0.025, glow(TEAL, 4) if T() else toon("#a02a2a", rim=0), R, loc=(a[0] + 0.0, a[1], 0.92), seg=5, rings=4)
            continue
        link_cyl("p2", (a[0], a[1], 0.915), (b[0], b[1], 0.915), 0.012, toon("#2a4a8a", rim=0), R, seg=3)
    ellipsoid("vl", 0.03, toon("#a02a2a", rim=0.3), R, loc=(0.2, 0.2, 0.92), seg=6, rings=4)
    desk_lamp(R, (0.8, 0.3, 0.82), "#4f9a7a") if not T() else None
    for k in range(2):
        chair_wood(R, (-0.5 + k * 1.0, -0.95, 0), rot=math.pi, col="#6a4630", seat="#2f7d6f")
    if T():
        # the cut route glows where it ends
        tthread(R, [(-0.2, 0.05, 0.92), (-0.1, 0.1, 1.2), (0.0, 0.2, 1.6)], 0.01, 3.0)
        halo(R, (-0.2, 0.05, 0.95), 0.4, 0.3)
        cobweb(R, (-1.0, 0.45, 0.95), 0.4)
        cleanup_dust(R, (0.6, 0.2, 0.84), 0.3)
    return {}


def l_shelf_fill(R, w, h, seed, truth_gaps=True):
    shelf_unit(R, (0, 0, 0), w, h, 0.45, int(h / 0.72), "#6a4630")
    rnd = random.Random(seed)
    cols = ("wine", "#4f7ad8", "forest", "gold", "plum", "#c9b48a", "#35b39a", "#c44b3f")
    levels = int(h / 0.72)
    step = (h - 0.06) / levels
    for lv in range(levels):
        x = -w / 2 + 0.1
        while x < w / 2 - 0.2:
            if T() and truth_gaps and (lv + int(x * 2)) % 3 == 0 and lv != 1:
                x += 0.2
                continue
            if rnd.random() < 0.12:
                spool(R, (x + 0.08, 0.0, 0.06 + lv * step + 0.06), 0.07, 0.18, ["#c44b3f", "#4f7ad8", "#e8b04a", TEAL][int(rnd.random() * 4)] if not T() else "#8a8e98")
                x += 0.2
                continue
            t = rnd.uniform(0.06, 0.12)
            hh = rnd.uniform(0.4, step - 0.16)
            box("bk", (t, 0.28, hh), toon(cols[int(rnd.random() * 8)], rim=0.3), R, loc=(x + t / 2, 0.0, 0.06 + lv * step), base=True)
            x += t + 0.004
    if T():
        cobweb(R, (-w / 2 + 0.1, -0.2, h), 0.5)
        for k in range(3):
            tube("pt", [(-w / 2 + 0.5 + k * 0.9, -0.2, h), (-w / 2 + 0.5 + k * 0.9, -0.2, h - 0.5)], 0.006, toon(GREY, rim=0), R)


def l_shelves_a(R):
    l_shelf_fill(R, 2.9, 3.6, 5)


def l_shelves_b(R):
    l_shelf_fill(R, 2.9, 3.6, 9)


def l_spool_rack(R):
    shelf_unit(R, (0, 0, 0), 1.5, 2.2, 0.4, 3, "#6a4630")
    rnd = random.Random(2)
    cols = ["#c44b3f", "#4f7ad8", "#e8b04a", "#35b39a", "#a07ad8", "#f3e4c4", "#e8884a"]
    for lv in range(3):
        for i in range(8):
            c = cols[(i * 3 + lv) % 7] if not T() else "#8a8e98"
            spool(R, (-0.6 + i * 0.17, 0.0, 0.06 + lv * 0.72), 0.075, 0.26, c, False)
            if i % 3 == lv % 3:
                spool(R, (-0.6 + i * 0.17, 0.0, 0.32 + lv * 0.72), 0.06, 0.2, cols[(i + lv) % 7] if not T() else "#8a8e98", False)
    if T():
        cobweb(R, (-0.7, -0.2, 2.2), 0.4)


def l_reading_chair(R):
    up = FAB("knit", "#2f6b48", "#1f5a3a", scale=10, bump=0.9, rim=0.4)
    box("base", (1.2, 1.0, 0.35), up, R, loc=(0, 0, 0.1), base=True, bevel=0.06)
    box("seat", (0.9, 0.78, 0.2), FAB("knit", "#3f8a5a", "#2f6b48", scale=10, bump=0.9), R, loc=(0, -0.05, 0.42), base=True, bevel=0.05)
    box("back", (1.2, 0.3, 1.05), up, R, loc=(0, 0.38, 0.35), base=True, bevel=0.07)
    for s in (-1, 1):
        box("arm", (0.24, 0.9, 0.5), up, R, loc=(s * 0.58, -0.02, 0.35), base=True, bevel=0.07)
        box("ft", (0.1, 0.1, 0.12), WDT(), R, loc=(s * 0.5, -0.4, 0), base=True)
        box("ft", (0.1, 0.1, 0.12), WDT(), R, loc=(s * 0.5, 0.4, 0), base=True)
    book(R, (0.55, -0.05, 0.86), (0.28, 0.2, 0.05), "wine", rot=0.5)
    if T():
        cobweb(R, (0.5, 0.3, 1.4), 0.3)


def l_lamp(R):
    lamp_floor(R, (0, 0, 0), 1.9, shade="#7ad0a0", glow_c="#ffe8a8")


# ==================================================================== OBSERVATORY
def o_telescope(R):
    # giant brass telescope on a stout wooden tripod, aimed up and to the right
    wd = WD("#6a4630", "#553622", scale=4, bump=0.8)
    for a in (0.5, 2.6, 4.7):
        link_cyl("lg", (math.cos(a) * 0.9, math.sin(a) * 0.9, 0.0), (0, 0, 1.55), 0.07, wd, R, seg=6)
    ellipsoid("jt", 0.18, toon(BRASS, rim=0.7), R, loc=(0, 0, 1.6), seg=10, rings=8)
    dirv = (0.55, 0.0, 0.84)
    L = [(1.5, 0.2, "#c69a4a"), (1.1, 0.17, "#d9b05a"), (0.8, 0.14, "#c69a4a")]
    pos = (-0.35 * dirv[0], 0, 1.6 - 0.35 * dirv[2])
    for ln, r, c in L:
        e = (pos[0] + dirv[0] * ln, pos[1], pos[2] + dirv[2] * ln)
        link_cyl("tb", pos, e, r, toon(c, rim=0.8), R, seg=14)
        link_cyl("rb", e, (e[0] + dirv[0] * 0.04, 0, e[2] + dirv[2] * 0.04), r * 1.12, toon("#8a6a2a", rim=0.8), R, seg=14)
        pos = (e[0] - dirv[0] * 0.15, 0, e[2] - dirv[2] * 0.15)
    tip = pos
    ellipsoid("lens", 0.14, glow(TEAL if T() else "#ffe9a8", 3.0 if T() else 1.4, alpha=0.9), R, loc=(tip[0] + dirv[0] * 0.18, -0.02, tip[2] + dirv[2] * 0.18), scale=(0.4, 1, 0.55), rot=(0, RAD(-33), 0), seg=10, rings=8)
    # eyepiece + finder
    link_cyl("ey", (-0.35 * dirv[0], 0, 1.6 - 0.35 * dirv[2]), (-0.62 * dirv[0], 0, 1.6 - 0.62 * dirv[2]), 0.06, toon("#2a2a30", rim=0.6), R, seg=8)
    link_cyl("fd", (0.2, -0.2, 1.9), (0.9, -0.2, 2.5), 0.045, toon("#2a2a30", rim=0.6), R, seg=8)
    if T():
        # three threads fall from the lens
        for k in range(3):
            x0, z0 = tip[0] + dirv[0] * 0.2, tip[2] + dirv[2] * 0.2
            tthread(R, [(x0, -0.03, z0), (x0 + 0.1 * (k - 1), -0.1 - 0.1 * k, z0 - 1.0), (x0 + 0.2 * (k - 1), -0.2 - 0.1 * k, 0.3), (x0 + 0.3 * (k - 1), -0.3 - 0.2 * k, 0.02)], 0.012, 3.2)
        halo(R, (tip[0] + dirv[0] * 0.2, -0.05, tip[2] + dirv[2] * 0.2), 0.6, 0.35)
        cobweb(R, (-0.6, 0.0, 1.7), 0.4)
    return {"cell": (512, 560), "anchor": (200, 470)}


def o_log(R):
    table(R, (0, 0, 0), 1.5, 0.85, 0.8, "#5a4a64", "#3a2c48")
    p = pivot("bk", (0, 0, 0.82), R)
    open_book(p, (-0.15, 0, 0), 0.78, 0.5, "#2a3a8a", page="#ece4d0", rot=(0, 0, RAD(5)))
    # rows of zeros and ones: small rings and bars
    rnd = random.Random(7)
    dc = glow(BLUE, 2.8) if T() else toon("#1f2f66", rim=0)
    for r in range(6):
        for c in range(10):
            x = -0.45 + c * 0.065 + (0.07 if c >= 5 else 0)
            y = 0.17 - r * 0.065
            if rnd.random() < 0.5:
                frustum("z", 0.014, 0.014, 0.004, dc, p, loc=(x - 0.15, y, 0.065), seg=8)
                frustum("z0", 0.007, 0.007, 0.006, toon("#ece4d0", rim=0), p, loc=(x - 0.15, y, 0.066), seg=6)
            else:
                box("o", (0.006, 0.02, 0.004), dc, p, loc=(x - 0.15, y, 0.067))
    candle(R, (0.55, 0.2, 0.82), 0.14, not T())
    ellipsoid("gl", 0.05, toon("#4a8ad8", rim=0.5), R, loc=(0.5, -0.2, 0.86), seg=8, rings=6)
    link_cyl("pn", (0.45, -0.2, 0.9), (0.58, -0.3, 1.1), 0.01, toon("#f3e4c4", rim=0.3), R, seg=4)
    chair_wood(R, (0, -0.95, 0), rot=math.pi, col="#3a2c48", seat="#4f7ad8")
    if T():
        halo(p, (-0.1, 0, 0.1), 0.8, 0.12, BLUE)
        cobweb(R, (-0.7, 0.3, 0.95), 0.35)
    return {}


def o_chart(R):
    box("fr", (2.0, 0.07, 1.5), WD("#9a7a3a", "#7a5e2c", scale=3), R, loc=(0, -0.035, 0.75))
    box("bd", (1.85, 0.05, 1.35), toon("#1a2250", rim=0), R, loc=(0, -0.07, 0.75))
    # grid
    for k in range(-3, 4):
        box("gl", (0.006, 0.01, 1.3), toon("#3a4a8a", rim=0), R, loc=(k * 0.25, -0.1, 0.75))
    for k in range(-2, 3):
        box("gl", (1.8, 0.01, 0.006), toon("#3a4a8a", rim=0), R, loc=(0, -0.1, 0.75 + k * 0.25))
    # cloud shape
    for dx, dz, rr in ((-0.3, -0.05, 0.28), (0.0, 0.1, 0.34), (0.32, -0.02, 0.28), (0.1, -0.18, 0.3), (-0.15, -0.2, 0.25)):
        ellipsoid("cl", rr, toon("#dfe6f4" if not T() else "#8a909e", rim=0.2), R, loc=(dx, -0.12, 0.8 + dz), scale=(1, 0.08, 0.75), seg=12, rings=8)
    # the pulsing dot (like a slow heart) with rings
    for k, rr in enumerate((0.07, 0.13, 0.19)):
        frustum("rg", rr, rr, 0.01, glow("#ff6a5a" if not T() else TEAL, 3.0 - k * 0.8, alpha=0.8), R, loc=(0.05, -0.15, 0.82), rot=(RAD(90), 0, 0), seg=18, caps=(False, False))
    ellipsoid("dt", 0.045, glow("#ff6a5a" if not T() else TEAL, 5), R, loc=(0.05, -0.16, 0.82), seg=8, rings=6)
    for k in range(4):
        box("lb", (0.3 - 0.05 * k, 0.012, 0.025), toon("#c9b070", rim=0), R, loc=(-0.55, -0.1, 1.2 - k * 0.07))
    if T():
        halo(R, (0.05, -0.2, 0.82), 0.8, 0.2)
        crack_fx(R, (0.8, -0.1, 1.45), 1.0)
        cobweb(R, (-0.98, -0.08, 1.48), 0.35)
    return {}


def o_orrery(R):
    round_table(R, (0, 0, 0), 0.55, 0.72, "#5a4a64")
    p = pivot("or", (0, 0, 0.74), R)
    frustum("bs", 0.35, 0.38, 0.06, toon(BRASS, rim=0.7), p, seg=16)
    frustum("pl", 0.05, 0.05, 0.45, toon(BRASS, rim=0.7), p, loc=(0, 0, 0.05), seg=8)
    ellipsoid("sun", 0.13, glow("#ffd070", 3 if not T() else 1.0), p, loc=(0, 0, 0.62), seg=12, rings=8)
    spec = [(0.28, "#c9b48a", 0.07, 0.8, 0.45), (0.5, "#4f8ad8", 0.09, 2.4, 0.38), (0.72, "#c44b3f", 0.08, 4.2, 0.3)]
    for r, c, pr, a, z in spec:
        x, y = math.cos(a) * r, math.sin(a) * r * 0.9
        link_cyl("ar", (0, 0, z + 0.2), (x, y, z + 0.2), 0.012, toon(BRASS, rim=0.7), p, seg=4)
        link_cyl("sp", (x, y, z + 0.2), (x, y, 0.1), 0.01, toon(BRASS, rim=0.7), p, seg=4)
        ellipsoid("pn", pr, toon(c if not T() else "#8a8e98", rim=0.6), p, loc=(x, y, z + 0.2 + pr), seg=10, rings=8)
    # the missing ball: an empty arm; the ball dangles on a short thread
    a, r = 5.5, 0.88
    x, y = math.cos(a) * r, math.sin(a) * r * 0.9
    link_cyl("ar", (0, 0, 0.55), (x, y, 0.55), 0.012, toon(BRASS, rim=0.7), p, seg=4)
    tube("th", [(x, y, 0.55), (x + 0.02, y - 0.03, 0.45), (x, y - 0.05, 0.38)], 0.008, toon("#ffffff", rim=0) if not T() else glow(TEAL, 3.2), p)
    ellipsoid("pn", 0.06, toon("#a07ad8" if not T() else "#8a8e98", rim=0.6), p, loc=(x, y - 0.05, 0.33), seg=10, rings=8)
    if T():
        halo(p, (x, y - 0.03, 0.45), 0.3, 0.3)
        cobweb(R, (-0.4, 0.2, 1.3), 0.3)
    return {}


def o_tea(R):
    round_table(R, (0, 0, 0), 0.4, 0.7, "#5a4a64", cloth="#2a3a6a")
    p = pivot("cp", (0, 0, 0.71), R)
    cup(p, (0, 0, 0.0), 0.12, 0.13, color="#f3e4c4", tea="#6a3a1a", full=True)
    frustum("sc", 0.05, 0.05, 0.02, toon("#f3e4c4", rim=0.4), p, loc=(0.28, 0.1, 0.0), seg=8)
    if not T():
        steam(p, (0, 0, 0.14), 4, 0.9)
    else:
        for k in range(4):
            tthread(p, [(0.0 + 0.02 * k, 0, 0.14), (0.02 * k, 0.0, 0.5), (0.03 * (k - 2), 0.1, 1.2), (0.06 * (k - 2), 0.2, 2.2)], 0.008, 2.8)
        halo(p, (0, 0, 0.3), 0.4, 0.12)
    return {"cell": (384, 520), "anchor": (192, 420)}


def o_chart_table(R):
    table(R, (0, 0, 0), 2.2, 1.2, 0.85, "#5a4a64", "#3a2c48")
    box("mp", (1.9, 0.95, 0.012), tex_toon("paper", "#e8d8b0", "#4a6a8a", scale=2.2, plane="xy", bump=0.1, wear=0), R, loc=(0, 0, 0.87), rot=(0, 0, RAD(-3)))
    tube("c", [(math.cos(t) * 0.3 - 0.4, math.sin(t) * 0.25, 0.885) for t in [i * 0.4 for i in range(17)]], 0.008, toon("#2a3a8a", rim=0), R)
    for k in range(3):
        link_cyl("cn", (0.2 + k * 0.2, -0.2 + 0.1 * (k % 2), 0.885), (0.3 + k * 0.2, 0.15, 0.885), 0.006, toon("#8a3a2e", rim=0), R, seg=3)
    # compass + dividers + rolled maps
    frustum("cp", 0.1, 0.1, 0.03, toon(BRASS, rim=0.7), R, loc=(0.7, -0.3, 0.87), seg=14)
    link_cyl("nd", (0.7, -0.3, 0.9), (0.75, -0.25, 0.9), 0.006, toon("#a02a2a", rim=0), R, seg=3)
    for k in range(2):
        cloth_roll(R, (-0.6, 0.45 - k * 0.05, 0.98 + k * 0.1), 0.6, 0.06, "#e8d8b0", "#c9b48a", "paper" if False else "weave", rot=(0, 0, RAD(8)))
    for k in range(2):
        chair_wood(R, (-0.5 + k * 1.0, -1.0, 0), rot=math.pi, col="#3a2c48", seat="#4f7ad8")
    if T():
        cobweb(R, (-1.0, 0.5, 0.95), 0.4)


def o_armillary(R):
    wd = WD("#6a4630", "#553622", scale=4)
    frustum("ft", 0.28, 0.3, 0.07, wd, R, seg=12)
    frustum("st", 0.06, 0.07, 0.75, wd, R, loc=(0, 0, 0.05), seg=8)
    cp = pivot("sp", (0, 0, 1.05), R, rot=(RAD(-23), 0, 0))
    for rot_, rr in (((RAD(90), 0, 0), 0.42), ((0, 0, 0), 0.42), ((0, RAD(90), 0), 0.42), ((RAD(60), 0, 0), 0.34)):
        frustum("rg", rr, rr, 0.025, toon(BRASS if not T() else "#8a8a7a", rim=0.8), cp, rot=rot_, seg=28, caps=(False, False))
    ellipsoid("ea", 0.1, toon("#4f8ad8" if not T() else "#4a5a7a", rim=0.5), cp, seg=10, rings=8)
    link_cyl("ax", (0, 0, -0.55), (0, 0, 0.55), 0.015, toon(BRASS, rim=0.8), cp, seg=5)
    if T():
        cobweb(R, (0.3, 0.1, 1.5), 0.3)


def o_stool(R):
    stool_round(R, (0, 0, 0), 0.26, 0.5, "#5a4a64")
    book(R, (0, 0, 0.58), (0.3, 0.2, 0.05), "#4f7ad8", rot=0.4)


def o_book_cart(R):
    wd = WD("#5a4a64", "#3a2c48", scale=4)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box("lg", (0.06, 0.06, 0.75), WDT("#3a2c48", "#3a2c48"), R, loc=(sx * 0.6, sy * 0.25, 0.08), base=True)
            ellipsoid("wh", 0.07, toon("#2a2a30", rim=0.4), R, loc=(sx * 0.6, sy * 0.25, 0.07), seg=8, rings=6)
    for z in (0.4, 0.85):
        box("sh", (1.4, 0.6, 0.05), wd, R, loc=(0, 0, z))
    box("bk", (0.05, 0.6, 0.35), wd, R, loc=(-0.7, 0, 0.88), base=True)
    books_row(R, (-0.6, 0.0, 0.88), 14, 0.34, 4)
    books_row(R, (-0.6, 0.0, 0.43), 12, 0.32, 6)
    for k in range(2):
        cloth_roll(R, (0.0, -0.1 + k * 0.1, 1.28 + k * 0.08), 0.5, 0.05, "#e8d8b0", "#c9b48a", "weave", rot=(0, 0, RAD(5 - k * 8)))
    if T():
        cobweb(R, (-0.6, 0.2, 1.4), 0.3)


def o_blanket_chair(R):
    up = FAB("knit", "#3a4a8a", "#2a3a7a", scale=10, bump=0.9, rim=0.4)
    box("base", (1.2, 1.0, 0.35), up, R, loc=(0, 0, 0.1), base=True, bevel=0.06)
    box("seat", (0.9, 0.78, 0.2), FAB("knit", "#4a5aa8", "#3a4a8a", scale=10, bump=0.9), R, loc=(0, -0.05, 0.42), base=True, bevel=0.05)
    box("back", (1.2, 0.3, 1.1), up, R, loc=(0, 0.38, 0.35), base=True, bevel=0.07)
    for s in (-1, 1):
        box("arm", (0.24, 0.9, 0.5), up, R, loc=(s * 0.58, -0.02, 0.35), base=True, bevel=0.07)
        box("ft", (0.1, 0.1, 0.12), WDT(), R, loc=(s * 0.5, -0.4, 0), base=True)
    box("bl", (0.95, 0.55, 0.06), FAB("stripes", "#e8b04a", "#c44b3f", scale=8, plane="xy", bump=0.8), R, loc=(0.0, -0.1, 0.68), rot=(RAD(-4), 0, RAD(8)))
    ellipsoid("cu", 0.28, FAB("knit", "#e8b04a", "#d9983a", scale=12), R, loc=(-0.3, 0.2, 0.9), scale=(1, 0.5, 0.9), seg=12, rings=8)
    if T():
        cobweb(R, (0.5, 0.3, 1.45), 0.3)


# ==================================================================== STORIES
def st_fire(R):
    # stone ring fire pit with iron tripod and pot
    st = ST("#9a9288", "#7a7270", plane="xy", scale=3, bump=1.2, wear=0.5, soot=0.2)
    for k in range(14):
        a = k * 2 * math.pi / 14
        ellipsoid("rk", 0.2, st, R, loc=(math.cos(a) * 0.95, math.sin(a) * 0.8, 0.14), scale=(1, 1, 0.75), seg=8, rings=6)
    frustum("gr", 0.85, 0.85, 0.05, toon("#2a2428", rim=0), R, loc=(0, 0, 0.02), seg=20, scale=(1, 0.85, 1))
    fire(R, (0, 0, 0.05), 1.5, not T())
    for k in range(3):
        a = k * 2.094 + 0.5
        link_cyl("tp", (math.cos(a) * 0.7, math.sin(a) * 0.6, 0.0), (0, 0, 1.9), 0.035, toon("#2a2a30", rim=0.5), R, seg=5)
    ellipsoid("pt", 0.24, toon("#2a2a30", rim=0.6), R, loc=(0, 0, 1.25), scale=(1, 1, 0.8), seg=12, rings=8)
    link_cyl("ch", (0, 0, 1.9), (0, 0, 1.45), 0.012, toon("#2a2a30", rim=0.5), R, seg=3)
    if T():
        for k in range(7):
            a = k * 0.9
            tthread(R, [(0, 0, 0.1), (math.cos(a) * 0.8, math.sin(a) * 0.5 - 0.1, 0.35), (math.cos(a) * 1.6, math.sin(a) * 1.0 - 0.1, 0.1), (math.cos(a) * 2.3, math.sin(a) * 1.3 - 0.1, 0.02)], 0.012, 3.0)
        halo(R, (0, 0, 0.3), 1.3, 0.12, TEAL, 1.0, (1.4, 1.0, 0.6))
        cobweb(R, (0.0, 0.0, 1.9), 0.4)
    return {"cell": (640, 520), "anchor": (320, 380)}


def st_curtain(R):
    w, h = 3.6, 3.9
    link_cyl("rod", (-w / 2 - 0.1, -0.05, h), (w / 2 + 0.1, -0.05, h), 0.04, WDT(), R, seg=6)
    gold = "gold" if not T() else "#8a8a7a"
    # raised stage, dark opening behind the curtains
    box("stg", (3.4, 0.8, 0.24), WD("#6a4630", "#553622", scale=3, plane="xy"), R, loc=(0, -0.4, 0.0), base=True, bevel=0.02)
    box("bk", (1.6, 0.04, 3.5), toon("#1a1220", rim=0), R, loc=(0, 0.0, 0.2), base=True)
    for s in (-1, 1):
        for k in range(9):
            x0 = s * (0.72 + k * 0.125)
            c = ("#a02a3a" if k % 2 == 0 else "#821e2e") if not T() else ("#6a6a78" if k % 2 == 0 else "#5a5a66")
            hk = h - 0.25 - 0.06 * (k % 2) - 0.03 * k
            box("pl", (0.13, 0.05 + 0.05 * (k % 2), hk), toon(c, rim=0.3), R, loc=(x0, -0.1 - 0.03 * (k % 2), 0.2), base=True)
        box("sash", (1.25, 0.07, 0.09), toon(gold, rim=0.6), R, loc=(s * 1.28, -0.2, 1.7))
        ellipsoid("tl", 0.07, toon(gold, rim=0.6), R, loc=(s * 0.7, -0.22, 1.55), scale=(1, 1, 1.5), seg=8, rings=6)
    # valance with scallops
    box("va", (w, 0.1, 0.3), toon("#7a1a28" if not T() else "#4a4a56", rim=0.3), R, loc=(0, -0.1, h - 0.2))
    for k in range(12):
        ellipsoid("sc", 0.15, toon("#7a1a28" if not T() else "#4a4a56", rim=0.3), R, loc=(-w / 2 + 0.15 + k * (w - 0.3) / 11, -0.1, h - 0.35), scale=(1, 0.4, 0.9), seg=8, rings=6)
    # cushion with a blue notebook, double thread beneath
    box("cu", (0.8, 0.5, 0.18), FAB("knit", "#e8b04a" if not T() else "#8a8a7a", "#c98a2c", scale=10, plane="xy", bump=1.0), R, loc=(0, -0.5, 0.33), bevel=0.06)
    for s in (-1, 1):
        ellipsoid("ct", 0.05, toon("gold", rim=0.5), R, loc=(s * 0.4, -0.5, 0.3), seg=6, rings=4)
    box("nb", (0.3, 0.2, 0.05), toon("#2a4ad8" if not T() else "#4a5a8a", rim=0.4), R, loc=(0.0, -0.5, 0.46), rot=(0, 0, RAD(12)))
    box("nbs", (0.02, 0.2, 0.052), toon("#c9b48a", rim=0.4), R, loc=(-0.14, -0.5, 0.46), rot=(0, 0, RAD(12)))
    if T():
        for dz in (0.0, 0.02):
            tthread(R, [(-0.4, -0.7, 0.26 + dz), (-0.1, -0.78, 0.25 + dz), (0.3, -0.75, 0.26 + dz), (0.45, -0.65, 0.25 + dz)], 0.013, 3.4)
        halo(R, (0, -0.5, 0.5), 0.7, 0.25)
        cobweb(R, (-1.7, -0.1, 3.8), 0.7)
    return {"cell": (640, 560), "anchor": (320, 440)}


def st_book(R):
    top = lectern(R, (0, 0, 0), 1.2, 0.8, "#6a4630")
    open_book(top, (0, 0, 0.04), 0.75, 0.5, "#6a2a30", page="#ece0c0")
    for s in (-1, 1):
        for k in range(5):
            box("tx", (0.24, 0.01, 0.01), toon("#3a2a22", rim=0), top, loc=(s * 0.19, 0.14 - k * 0.06, 0.07))
    # torn edge: a ragged smooth tear on the right edge, held by a two-turn knot
    box("tr", (0.02, 0.5, 0.04), toon("#ece0c0", rim=0), top, loc=(0.38, 0.0, 0.065))
    weaver_knot(top, (0.4, 0.0, 0.14), 0.07) if T() else None
    if T():
        halo(top, (0.4, 0.0, 0.14), 0.4, 0.3)
        cobweb(R, (-0.4, 0.2, 1.5), 0.3)
    ellipsoid("rb", 0.06, toon("#c44b3f", rim=0.4), top, loc=(-0.3, -0.22, 0.07), scale=(1, 2.5, 0.3), seg=6, rings=4)


def st_puppets(R):
    p = pivot("cr", (0, 0, 0), R)
    box("bx", (1.2, 0.8, 0.5), WD("#8a5a30", "#6a4220", scale=4), p, base=True, bevel=0.02)
    box("in", (1.1, 0.7, 0.03), toon("#2a1e1a", rim=0), p, loc=(0, 0, 0.5))
    cols = ["#c44b3f", "#4f7ad8", "#e8b04a", "#35b39a"]
    for k in range(4):
        x = -0.4 + k * 0.27
        ellipsoid("hd", 0.1, toon("#f1c4a0" if k % 2 == 0 else "#d9b088", rim=0.4), p, loc=(x, 0.0, 0.88 + (k % 2) * 0.05), seg=10, rings=8)
        frustum("bd", 0.1, 0.16, 0.34, FAB("weave", cols[k], "#f3e4c4", scale=14), p, loc=(x, 0.0, 0.5 + (k % 2) * 0.02), seg=8)
        frustum("hat", 0.1, 0.0, 0.18, toon(cols[(k + 1) % 4], rim=0.4), p, loc=(x, 0.0, 0.96 + (k % 2) * 0.05), seg=8)
        link_cyl("sv", (x - 0.12, 0, 0.7), (x - 0.2, -0.1, 0.55), 0.03, toon("#d9c9a8", rim=0.3), p, seg=4)
    # controllers
    for k in range(2):
        box("ct", (0.4, 0.04, 0.04), WDT(), p, loc=(-0.3 + k * 0.6, 0.1, 1.5), rot=(0, RAD(10 - k * 20), RAD(k * 15)))
    # tangled strings
    rnd = random.Random(9)
    sc = toon("#d9c9a8", rim=0) if not T() else toon("#9aa0ae", rim=0)
    for k in range(10):
        x0 = rnd.uniform(-0.5, 0.5)
        pts = [(x0, 0.1, 1.5), (x0 + rnd.uniform(-0.3, 0.3), 0.0, 1.2), (rnd.uniform(-0.5, 0.5), -0.05, 1.0), (rnd.uniform(-0.4, 0.4), 0.0, 0.9)]
        tube("sg", pts, 0.006, sc, p)
    if T():
        # only one thread is free: it runs straight up out of the tangle
        tthread(p, [(0.35, 0.05, 1.0), (0.4, 0.05, 1.8), (0.45, 0.0, 2.8), (0.5, 0.0, 3.8)], 0.012, 3.4)
        halo(p, (0.35, 0.05, 1.1), 0.4, 0.2)
        cobweb(p, (-0.6, 0.35, 0.9), 0.35)
    return {}


def st_drum(R):
    wd = WD("#8a4a2a", "#6a3820", scale=5, along="v", bump=0.8)
    frustum("bd", 0.55, 0.5, 0.7, wd, R, loc=(0, 0, 0.55), seg=24)
    frustum("tp", 0.57, 0.57, 0.04, toon("#f0e6cc" if not T() else "#a8a8b0", rim=0.3), R, loc=(0, 0, 1.25), seg=24)
    for k in range(12):
        a = k * math.pi / 6
        link_cyl("rp", (math.cos(a) * 0.55, math.sin(a) * 0.55, 1.25), (math.cos(a + 0.26) * 0.5, math.sin(a + 0.26) * 0.5, 0.58), 0.012, toon("#c9b48a", rim=0.3), R, seg=3)
    frustum("hp", 0.58, 0.58, 0.05, toon("#c44b3f", rim=0.4), R, loc=(0, 0, 0.5), caps=(False, False), seg=24) if False else None
    for s in (-1, 1):
        link_cyl("lg", (s * 0.4, 0, 0.55), (s * 0.55, 0.2, 0.0), 0.05, WDT(), R, seg=5)
        link_cyl("lg", (s * 0.4, 0, 0.55), (s * 0.5, -0.25, 0.0), 0.05, WDT(), R, seg=5)
    # mallets
    for s in (-1, 1):
        link_cyl("ml", (s * 0.15, -0.1, 1.3), (s * 0.35, -0.35, 1.38), 0.02, WDT(), R, seg=5)
        ellipsoid("mh", 0.06, FAB("weave", "#c9b48a", "#a89870", scale=12), R, loc=(s * 0.15, -0.1, 1.3), seg=8, rings=6)
    if T():
        # one hit and the ripples keep going
        for k, rr in enumerate((0.25, 0.4, 0.55)):
            frustum("rp", rr, rr, 0.012, glow(TEAL, 3.2 - k * 0.6, alpha=0.8), R, loc=(0, 0, 1.28 + k * 0.05), seg=24, caps=(False, False))
        for k, rr in enumerate((0.8, 1.1, 1.4)):
            frustum("rp", rr, rr, 0.01, glow(TEAL, 1.6, alpha=0.4), R, loc=(0, 0, 0.02), seg=28, caps=(False, False), scale=(1, 0.8, 1))
        halo(R, (0, 0, 1.3), 0.7, 0.2)
        cobweb(R, (-0.5, 0.1, 1.3), 0.3)
    return {"cell": (512, 480), "anchor": (256, 380)}


def st_bench_x(R, rot=0.0, L=3.2):
    bench(R, (0, 0, 0), L, 0.5, 0.52, "#8a5a30", rot=rot)
    if T():
        cobweb(R, (0.0, 0.0, 0.9), 0.3)


def st_bench_front(R):
    st_bench_x(R, 0.0, 3.2)


def st_bench_left(R):
    st_bench_x(R, math.pi / 2, 2.4)


def st_bench_right(R):
    st_bench_x(R, math.pi / 2, 2.4)


def st_log_stack(R):
    wd = WD("#8a5a30", "#6a4220", scale=5, along="v")
    ends = toon("#c9a06a", rim=0.3)
    for row, n in ((0, 4), (1, 3), (2, 2)):
        for k in range(n):
            x = -0.5 + row * 0.15 + k * 0.33
            frustum("lg", 0.15, 0.15, 0.9, wd, R, loc=(x, 0.0, 0.15 + row * 0.27), rot=(RAD(90), 0, 0), seg=10)
            ellipsoid("en", 0.15, ends, R, loc=(x, -0.9, 0.15 + row * 0.27), scale=(1, 0.05, 1), seg=10, rings=6)
    box("sk", (0.1, 0.1, 0.8), WDT(), R, loc=(-0.65, -0.4, 0), base=True)
    box("sk", (0.1, 0.1, 0.8), WDT(), R, loc=(0.9, -0.4, 0), base=True)
    if T():
        cobweb(R, (-0.5, 0.0, 0.9), 0.3)


def st_lantern(R):
    lantern_floor(R, (0, 0, 0), 1.7, "amber", not T())


# ==================================================================== FARM
def fa_horn(R):
    # coiled copper horn on a wall bracket
    cm = toon("#c0693f" if not T() else "#8a7a72", rim=0.8)
    cm2 = toon("#d98a4a" if not T() else "#9a8a82", rim=0.8)
    pts = [(-0.9, -0.2, 0.0), (-0.5, -0.25, 0.05), (0.0, -0.3, 0.1), (0.45, -0.3, 0.3), (0.8, -0.25, 0.7), (0.95, -0.2, 1.1), (1.0, -0.15, 1.5)]
    rr = [0.06, 0.07, 0.09, 0.12, 0.17, 0.25, 0.4]
    for i in range(len(pts) - 1):
        link_cyl("hn", pts[i], pts[i + 1], rr[i], cm if i % 2 == 0 else cm2, R, seg=14, r2=rr[i + 1])
        ellipsoid("jn", rr[i + 1] * 1.03, cm2, R, loc=pts[i + 1], seg=12, rings=8) if i < len(pts) - 2 else None
    frustum("bl", 0.4, 0.46, 0.06, toon("#a8502c" if not T() else "#7a6a62", rim=0.8), R, loc=(pts[-1][0], pts[-1][1], pts[-1][2]), seg=18)
    frustum("in", 0.34, 0.34, 0.03, toon("#2a1a14", rim=0), R, loc=(pts[-1][0], pts[-1][1], pts[-1][2] + 0.04), seg=16)
    ellipsoid("mp", 0.1, cm2, R, loc=(-0.95, -0.2, 0.0), scale=(1.4, 1, 1), seg=10, rings=8)
    for x in (-0.3, 0.4):
        box("br", (0.08, 0.2, 0.12), toon("#3a3a44", rim=0.5), R, loc=(x, -0.12, 0.0 if x < 0 else 0.15))
    if T():
        # a silver thread goes in from the north and comes out the other side
        tthread(R, [(-1.6, -0.1, 2.0), (-1.2, -0.2, 0.9), (-0.95, -0.2, 0.1)], 0.014, 3.0, "#ffffff")
        tthread(R, [(0.95, -0.2, 1.5), (1.4, -0.2, 1.1), (1.9, -0.2, 0.5), (2.3, -0.2, 0.2)], 0.014, 3.0, "#ffffff")
        halo(R, (1.0, -0.2, 1.5), 0.6, 0.2, "#ffffff")
    return {"cell": (512, 460), "anchor": (200, 280)}


def fa_barn(R):
    # private store door: plank door in a stone frame, strong lock; a brown thread ends at the sill
    sm = ST("#a79e92", "#8a847c", plane="xz", scale=3, bump=1.0, wear=0.5)
    w, h = 1.3, 2.4
    box("fl", (w + 0.5, 0.18, h + 0.2), sm, R, loc=(0, -0.09, 0), base=True)
    box("dr", (w, 0.1, h), WD("#7a4a2a", "#5a3520", scale=3, along="v", bump=1.0), R, loc=(0, -0.2, 0.0), base=True)
    for z in (0.4, 1.2, 2.0):
        box("bd", (w, 0.04, 0.1), toon("#2a2a30", rim=0.6), R, loc=(0, -0.27, z))
    for z in (0.4, 2.0):
        ellipsoid("hg", 0.07, toon("#2a2a30", rim=0.6), R, loc=(-w / 2 + 0.05, -0.28, z), seg=6, rings=4)
    box("lk", (0.2, 0.06, 0.26), toon("#b9b0a2", rim=0.8), R, loc=(0.35, -0.3, 1.1))
    frustum("sh", 0.07, 0.07, 0.04, toon("#b9b0a2", rim=0.8), R, loc=(0.35, -0.34, 1.3), rot=(RAD(90), 0, 0), seg=10, caps=(False, False))
    box("st", (w + 0.6, 0.5, 0.1), sm, R, loc=(0, -0.4, 0.0), base=True)
    if T():
        bc = toon("#b8844a", rim=0.2)
        tube("bth", [(-1.5, -0.9, 0.04), (-1.0, -0.8, 0.05), (-0.5, -0.7, 0.06), (0.0, -0.6, 0.12), (0.25, -0.45, 0.14)], 0.02, glow("#ffb060", 3.0), R)
        ellipsoid("end", 0.04, glow("#ffb060", 4), R, loc=(0.25, -0.45, 0.14), seg=6, rings=4)
        cobweb(R, (-0.7, -0.22, 2.4), 0.4)
    return {}


def fa_cart(R):
    wd = WD("#9a6238", "#7a4a2a", scale=3, bump=0.8)
    box("bd", (1.8, 0.9, 0.12), wd, R, loc=(0, 0, 0.55))
    for sx in (-1, 1):
        box("sd", (0.06, 0.9, 0.35), wd, R, loc=(sx * 0.9, 0, 0.6), base=True)
    box("fr", (1.8, 0.06, 0.35), wd, R, loc=(0, -0.45, 0.6), base=True)
    box("bk", (1.8, 0.06, 0.35), wd, R, loc=(0, 0.45, 0.6), base=True)
    for s in (-1, 1):
        wp = pivot("wh", (s * 0.75, 0.0, 0.38), R)
        frustum("rm", 0.38, 0.38, 0.08, wd, wp, loc=(0, 0.5 if s > 0 else 0.5, 0), rot=(0, RAD(90), 0), seg=20, caps=(False, False)) if False else None
        frustum("rm", 0.38, 0.38, 0.07, WDT(), wp, loc=(0, -0.0, 0), rot=(RAD(90), 0, RAD(90)), seg=22, caps=(False, False)) if False else None
        frustum("rm", 0.38, 0.38, 0.07, WDT(), wp, loc=(s * 0.0, 0.0, 0.0), rot=(0, RAD(90), 0), seg=22, caps=(False, False))
        frustum("rm2", 0.3, 0.3, 0.07, WD("#6a4220", "#6a4220", scale=4), wp, rot=(0, RAD(90), 0), seg=22, caps=(False, False))
        for k in range(8):
            a = k * math.pi / 4
            link_cyl("sp", (0, 0, 0), (0, math.cos(a) * 0.36, math.sin(a) * 0.36), 0.02, WDT(), wp, seg=4)
        ellipsoid("hb", 0.06, toon("#3a3a44", rim=0.6), wp, seg=6, rings=4)
    link_cyl("hd", (-0.5, 0.0, 0.5), (-1.45, 0.0, 0.1), 0.04, wd, R, seg=5) if False else None
    # produce: crates of carrots, cabbages, pumpkins
    for k in range(5):
        ellipsoid("cb", 0.17, toon(["#6cb257", "#8fc267"][k % 2] if not T() else "#5a5a4a", rim=0.4), R, loc=(-0.6 + (k % 3) * 0.3, -0.2 + (k // 3) * 0.35, 0.78), scale=(1, 1, 0.9), seg=10, rings=8)
    for k in range(4):
        ellipsoid("pk", 0.22, toon("#e8884a" if not T() else "#6a5a4a", rim=0.5), R, loc=(0.4 + (k % 2) * 0.4, -0.15 + (k // 2) * 0.4, 0.82), scale=(1.1, 1, 0.8), seg=12, rings=8)
    for k in range(7):
        link_cyl("cr", (0.0 + k * 0.05, 0.3, 0.7), (0.05 + k * 0.05, 0.3 + k * 0.01, 0.95), 0.03, toon("#e8884a" if not T() else "#6a5a4a", rim=0.4), R, seg=5, r2=0.012) if False else None
    # striped awning on two poles
    for sx in (-1, 1):
        link_cyl("pp", (sx * 0.85, 0.4, 0.6), (sx * 0.85, 0.4, 1.9), 0.03, WDT(), R, seg=5)
    box("aw", (2.0, 1.0, 0.04), FAB("stripes", "#c44b3f", "#f6efe0", scale=6, plane="xy", bump=0.6), R, loc=(0, 0.1, 1.95), rot=(RAD(14), 0, 0))
    link_cyl("hd", (0.9, 0.0, 0.5), (1.55, 0.0, 0.15), 0.04, wd, R, seg=5)
    if T():
        for k in range(9):
            a = -1.3 + k * 0.32
            tthread(R, [(math.cos(a) * 3.0, math.sin(a) * 1.5 - 0.5, 1.2 + 0.4 * (k % 3)), (math.cos(a) * 1.6, math.sin(a) * 0.8 - 0.3, 1.1), (0.0, 0.0, 0.9)], 0.007, 2.8, GREY)
        halo(R, (0, 0, 1.0), 0.8, 0.12)
    return {"cell": (640, 460), "anchor": (320, 320)}


def fa_ledger(R):
    # slanted accountant's desk with a fat ledger
    top = lectern(R, (0, 0, 0), 1.1, 0.9, "#7a4a2a", tilt=14)
    open_book(top, (0, 0, 0.04), 0.82, 0.52, "#3a4a3a", page="#ece0c0")
    for s in (-1, 1):
        for k in range(6):
            box("rw", (0.24, 0.01, 0.008), toon("#3a2a22", rim=0), top, loc=(s * 0.2 - 0.0, 0.17 - k * 0.062, 0.07))
            box("rw2", (0.24, 0.01, 0.008), toon("#3a2a22", rim=0), top, loc=(s * 0.2, 0.17 - k * 0.062 - 0.012, 0.07)) if k % 2 == 0 else None
    for k in range(2):
        frustum("ik", 0.04, 0.04, 0.06, toon("#1f2f66", rim=0.5), top, loc=(0.5, -0.1 + k * 0.1, 0.03), seg=8) if k == 0 else None
    tube("bm", [(0.0, 0.25, 0.08), (0.05, 0.32, 0.0), (0.1, 0.3, -0.5)], 0.01, toon("#c44b3f", rim=0.3), top)
    if T():
        # the doubled line is tied by an old thread to another valley
        tthread(R, [(-0.2, 0.0, 1.2), (-0.6, -0.1, 1.5), (-1.2, -0.1, 2.0), (-2.0, -0.2, 2.6)], 0.012, 2.8, "#c9b48a")
        halo(R, (-0.2, 0.0, 1.2), 0.5, 0.2)
        cobweb(R, (-0.4, 0.2, 1.4), 0.3)
    return {}


def fa_cow(R):
    wm = tex_toon("stripes", "#f6f0e6", "#f6f0e6", scale=5, plane="xz", bump=0.3, rim=0.5, ao=0.3)
    cream = "#f6f0e6" if not T() else "#bfc2cc"
    blk = "#3a2c28" if not T() else "#4a4a52"
    wm = toon(cream, rim=0.5)
    bm = toon(blk, rim=0.3)
    ellipsoid("bd", 0.55, wm, R, loc=(0, 0, 0.95), scale=(1.5, 0.85, 0.95), seg=18, rings=12)
    # patches
    for (x, y, z, sx, sz) in ((-0.2, -0.38, 1.05, 0.3, 0.25), (0.35, -0.3, 0.9, 0.25, 0.3), (-0.55, 0.25, 1.15, 0.28, 0.2), (0.1, 0.4, 1.2, 0.3, 0.2)):
        ellipsoid("pt", 0.5, bm, R, loc=(x, y, z), scale=(sx, 0.15, sz), seg=10, rings=8)
    # legs
    for (x, y) in ((-0.55, -0.3), (-0.55, 0.3), (0.55, -0.3), (0.55, 0.3)):
        frustum("lg", 0.09, 0.07, 0.55, wm, R, loc=(x, y, 0.1), seg=8)
        frustum("hf", 0.09, 0.09, 0.1, bm, R, loc=(x, y, 0.0), seg=8)
    # head
    ellipsoid("hd", 0.28, wm, R, loc=(-0.95, -0.05, 1.25), scale=(1.1, 0.9, 0.95), seg=14, rings=10)
    ellipsoid("sn", 0.18, toon("#f0b0b0" if not T() else "#a8a0a8", rim=0.4), R, loc=(-1.18, -0.05, 1.12), scale=(0.9, 1.1, 0.8), seg=10, rings=8)
    for s in (-1, 1):
        ellipsoid("ey", 0.04, toon("#1a1220", rim=0), R, loc=(-1.05, s * 0.18 - 0.05, 1.33), seg=6, rings=4)
        ellipsoid("er", 0.1, wm, R, loc=(-0.82, s * 0.3 - 0.05, 1.33), scale=(0.5, 1.2, 0.5), seg=8, rings=6)
        link_cyl("hn", (-0.88, s * 0.14 - 0.05, 1.5), (-0.84, s * 0.2 - 0.05, 1.65), 0.03, toon("#f3e4c4", rim=0.3), R, seg=5, r2=0.012)
        ellipsoid("nt", 0.025, toon("#d8a0a0", rim=0), R, loc=(-1.32, s * 0.08 - 0.05, 1.12), seg=5, rings=4)
    ellipsoid("ud", 0.2, toon("#f0b0b0" if not T() else "#a8a0a8", rim=0.4), R, loc=(0.4, 0.0, 0.5), scale=(1, 0.9, 0.7), seg=10, rings=8)
    tube("tl", [(0.8, 0.0, 1.2), (0.95, 0.05, 0.9), (0.98, 0.08, 0.5)], 0.035, wm, R)
    ellipsoid("tf", 0.07, bm, R, loc=(0.98, 0.08, 0.45), scale=(1, 1, 1.5), seg=8, rings=6)
    # collar with a bell; in truth a fine thread is tied to the neck
    tube("cl", [(-0.75, -0.3, 1.28), (-0.75, -0.0, 1.05), (-0.75, 0.3, 1.28)], 0.04, toon("#c44b3f" if not T() else "#6a4a52", rim=0.4), R)
    frustum("bl", 0.08, 0.04, 0.1, toon("gold" if not T() else "#8a8a7a", rim=0.8), R, loc=(-0.75, -0.0, 0.88), seg=10)
    if T():
        tthread(R, [(-0.75, 0.0, 1.05), (-0.5, 0.2, 1.8), (0.0, 0.1, 3.0), (0.6, 0.0, 4.2)], 0.012, 3.2)
        halo(R, (-0.75, 0.0, 1.1), 0.5, 0.25)
    return {"cell": (512, 480), "anchor": (256, 380)}


def fa_stove(R):
    iron = toon("#2a2a30", rim=0.6)
    box("bd", (1.2, 0.8, 0.95), iron, R, loc=(0, 0, 0.12), base=True, bevel=0.03)
    box("tp", (1.3, 0.85, 0.06), toon("#3a3a44", rim=0.6), R, loc=(0, 0, 1.07), base=True)
    for s in (-1, 1):
        box("ft", (0.1, 0.1, 0.14), iron, R, loc=(s * 0.5, -0.3, 0), base=True)
    for k in range(2):
        box("dr", (0.4, 0.03, 0.4), toon("#1a1a20", rim=0.4), R, loc=(-0.3 + k * 0.6, -0.41, 0.55))
        ellipsoid("gl", 0.06, glow("#ff8a2a", 2.0) if not T() else toon("#2a2a30", rim=0), R, loc=(-0.3 + k * 0.6, -0.44, 0.5), scale=(2, 0.3, 1), seg=6, rings=4)
        ellipsoid("kb", 0.03, toon(BRASS, rim=0.7), R, loc=(-0.3 + k * 0.6 + 0.12, -0.44, 0.7), seg=5, rings=4)
    ellipsoid("pot", 0.22, toon("#4a5a6a", rim=0.7), R, loc=(-0.3, 0, 1.28), scale=(1, 1, 0.85), seg=12, rings=8)
    frustum("lid", 0.14, 0.05, 0.07, toon("#4a5a6a", rim=0.7), R, loc=(-0.3, 0, 1.42), seg=10)
    kt = toon("#c0693f", rim=0.7)
    ellipsoid("kt", 0.17, kt, R, loc=(0.35, 0, 1.2), scale=(1, 1, 0.85), seg=12, rings=8)
    link_cyl("sp", (0.48, 0, 1.18), (0.62, 0, 1.35), 0.02, kt, R, seg=5)
    frustum("pipe", 0.08, 0.08, 1.8, iron, R, loc=(0.4, 0.3, 1.1), seg=8)
    box("rail", (1.2, 0.04, 0.04), toon("#b9b0a2", rim=0.7), R, loc=(0, -0.45, 0.95))
    if not T():
        steam(R, (-0.3, 0, 1.5), 3, 0.6)
    else:
        cobweb(R, (-0.6, 0.2, 1.6), 0.35)


def fa_kitchen_table(R):
    table(R, (0, 0, 0), 1.5, 0.9, 0.82, "#c98a52", "#85502c", cloth="#c44b3f")
    frustum("lf", 0.14, 0.14, 0.1, toon("#c98a3c", rim=0.4), R, loc=(0.1, 0, 0.84), rot=(0, RAD(90), 0), seg=8)
    ellipsoid("lf", 0.14, toon("#c98a3c", rim=0.4), R, loc=(0.05, 0.0, 0.95), scale=(1.5, 1, 0.8), seg=10, rings=6)
    plate(R, (-0.3, -0.2, 0.85), 0.12)
    mug(R, (0.4, 0.2, 0.85), col="#4f7ad8")
    chair_wood(R, (-0.5, -0.9, 0), rot=math.pi, col="#8a5a30", seat="#c44b3f")
    chair_wood(R, (0.5, 0.9, 0), rot=0.0, col="#8a5a30", seat="#c44b3f")
    if T():
        cobweb(R, (-0.7, 0.4, 0.95), 0.3)


def fa_milk_cans(R):
    for k, (x, y) in enumerate(((-0.3, 0.0), (0.25, 0.05), (0.0, -0.3))):
        p = pivot("can", (x, y, 0), R)
        frustum("cn", 0.2, 0.18, 0.7, toon("#b9b0a2", rim=0.8), p, seg=14)
        frustum("nk", 0.1, 0.1, 0.12, toon("#b9b0a2", rim=0.8), p, loc=(0, 0, 0.7), seg=12)
        frustum("lid", 0.14, 0.12, 0.06, toon("#8a8a94", rim=0.8), p, loc=(0, 0, 0.82), seg=12)
        for s in (-1, 1):
            tube("hd", [(s * 0.2, 0, 0.65), (s * 0.26, 0, 0.55), (s * 0.2, 0, 0.45)], 0.015, toon("#8a8a94", rim=0.8), p)
    if T():
        cobweb(R, (-0.3, 0.1, 1.0), 0.3)


def fa_sacks(R):
    for k, (x, y, r) in enumerate(((-0.3, 0.0, 0.34), (0.3, 0.05, 0.32), (0.0, -0.3, 0.3), (0.0, 0.3, 0.28))):
        sack(R, (x, y, 0.0), r, "#e8dcc0" if k % 2 == 0 else "#c9b48a", 1.1)
    box("lb", (0.2, 0.01, 0.12), toon("#c44b3f", rim=0), R, loc=(0.3, -0.12, 0.35))
    if T():
        cobweb(R, (-0.4, 0.2, 1.0), 0.3)


def fa_tool_rack(R):
    for s in (-1, 1):
        box("po", (0.07, 0.07, 1.9), WDT(), R, loc=(s * 0.45, 0, 0), base=True)
    box("br", (1.0, 0.07, 0.07), WDT(), R, loc=(0, 0, 1.5))
    box("br", (1.0, 0.07, 0.07), WDT(), R, loc=(0, 0, 0.6))
    # rake, hoe, shovel, broom
    wm = WD("#c9a06a", "#a8804a", scale=5, along="v")
    link_cyl("rk", (-0.3, -0.1, 0.05), (-0.3, -0.1, 1.9), 0.022, wm, R, seg=5)
    box("rh", (0.3, 0.03, 0.04), toon("#6a6a74", rim=0.7), R, loc=(-0.3, -0.1, 0.1))
    for k in range(5):
        link_cyl("tn", (-0.43 + k * 0.065, -0.1, 0.1), (-0.43 + k * 0.065, -0.1, 0.0), 0.008, toon("#6a6a74", rim=0.7), R, seg=3)
    link_cyl("ho", (0.0, -0.1, 0.1), (0.0, -0.1, 1.85), 0.022, wm, R, seg=5)
    box("hb", (0.22, 0.03, 0.14), toon("#6a6a74", rim=0.7), R, loc=(0.0, -0.1, 0.1))
    link_cyl("sv", (0.3, -0.1, 0.35), (0.3, -0.1, 1.95), 0.022, wm, R, seg=5)
    ellipsoid("sb", 0.14, toon("#6a6a74", rim=0.7), R, loc=(0.3, -0.1, 0.22), scale=(1, 0.15, 1.2), seg=8, rings=6)
    link_cyl("bm", (0.55, -0.12, 0.3), (0.55, -0.12, 1.8), 0.02, wm, R, seg=5)
    frustum("bh", 0.1, 0.16, 0.34, toon("#d9c24a", rim=0.3), R, loc=(0.55, -0.12, 0.0), seg=8)
    if T():
        cobweb(R, (-0.4, -0.1, 1.9), 0.4)


OBJ = {
    "workshop": {"w_gears": w_gears, "w_note": w_note, "w_clocks": w_clocks, "w_bench": w_bench, "w_tester": w_tester,
                 "x_tool_rack": w_tool_rack, "x_grinder": w_grinder, "x_gear_bin": w_gear_bin, "x_anvil": w_anvil, "x_parts_shelf": w_parts_shelf},
    "library": {"l_catalog": l_catalog, "l_ladder": l_ladder, "l_table": l_table, "l_cover": l_cover, "l_stamp": l_stamp,
                "x_shelves_a": l_shelves_a, "x_shelves_b": l_shelves_b, "x_spool_rack": l_spool_rack, "x_reading_chair": l_reading_chair, "x_lamp": l_lamp},
    "observatory": {"o_chart": o_chart, "o_telescope": o_telescope, "o_orrery": o_orrery, "o_log": o_log, "o_tea": o_tea,
                    "x_chart_table": o_chart_table, "x_armillary": o_armillary, "x_stool": o_stool, "x_book_cart": o_book_cart, "x_blanket_chair": o_blanket_chair},
    "stories": {"st_fire": st_fire, "st_curtain": st_curtain, "st_book": st_book, "st_puppets": st_puppets, "st_drum": st_drum,
                "x_bench_front": st_bench_front, "x_bench_left": st_bench_left, "x_bench_right": st_bench_right, "x_log_stack": st_log_stack, "x_lantern": st_lantern},
    "farm": {"fa_horn": fa_horn, "fa_barn": fa_barn, "fa_cart": fa_cart, "fa_ledger": fa_ledger, "fa_cow": fa_cow,
             "x_stove": fa_stove, "x_kitchen_table": fa_kitchen_table, "x_milk_cans": fa_milk_cans, "x_sacks": fa_sacks, "x_tool_rack": fa_tool_rack},
}
