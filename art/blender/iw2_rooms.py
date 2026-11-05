"""Room shell configs for the 15 world-2 interiors (consumed by interiors.build_room)."""
import math
import random

from iw2_lib import *  # noqa

RD_, RH_ = 4.5, 5.0


def _pegged(R, xs, z, items):
    for x, it in zip(xs, items):
        it(x, z)


def _rail(R, x0, x1, z, col="wood_d"):
    link_cyl("rail", (x0, RD_ - 0.14, z), (x1, RD_ - 0.14, z), 0.035, toon(col, rim=0.2), R, seg=6)


def _bunting(R, x0, x1, z0, sagv, cols, wx, n=15, truth=False, kind="knit", skip=1.5):
    pts = [(x0 + (x1 - x0) * t / 40, RD_ - 0.08, z0 - sagv * math.sin(math.pi * t / 40)) for t in range(41)]
    pts = [p for p in pts if not (wx - skip < p[0] < wx + skip)]
    tube("bunt", pts, 0.012, toon("#d9c9a8", rim=0.2), R)
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        if wx - skip < x < wx + skip:
            continue
        z = z0 - sagv * math.sin(math.pi * (x - x0) / (x1 - x0))
        mesh_obj("flag", [(x - 0.17, RD_ - 0.09, z), (x + 0.17, RD_ - 0.09, z), (x, RD_ - 0.12, z - 0.42 * (0.65 if truth and i % 4 == 0 else 1))], [(0, 1, 2)],
                 FAB(kind, cols[i % len(cols)], cols[(i + 2) % len(cols)], scale=12, bump=0.9), R, smooth=False)


def _web_corners(R, truth, wx):
    if truth:
        cobweb(R, (-6.4, RD_ - 0.1, 4.9), 0.7)
        cobweb(R, (6.4, RD_ - 0.1, 4.9), 0.7, rot=(0, RAD(-90), 0))


# =========================================================================== INN
def cfg_inn():
    def wall(plane="xz"): return WD("#b9824a", "#a06a38", plane=plane, scale=2.2, along="v", bump=0.9, wear=0.35)
    def wain(): return WD("#6a4228", "#573820", scale=2.8, along="v", bump=0.8)
    def floor(): return WD("#6e4a2a", "#573820", plane="xy", scale=2.2, bump=0.8, wear=0.45)
    def trim(): return WD("#4a3020", "#3a2418", scale=3, bump=0.5)

    def decor(R, wx, truth):
        for x in (-6.7, -4.2, -1.9, 1.5, 6.7):
            post_z(R, x, RD_ - 0.1, 5.0, 0.3)
        beam_x(R, RD_ - 0.12, 3.75, 14, 0.26)
        beam_x(R, RD_ - 0.12, 0.9, 14, 0.12)
        for x in (-3.0, 0.2):
            lantern2(R, (x, RD_ - 0.2, 3.7), "amber", 5, 0.17, hang=True)
        box("rugr", (6.6, 1.7, 0.02), FAB("weave", "#8a3a2e", "#e8b04a", scale=7, plane="xy", bump=0.7), R, loc=(-1.8, -0.5, 0.0), base=True)
        box("rugb", (6.9, 1.95, 0.015), toon("#4a2a22", rim=0.2), R, loc=(-1.8, -0.5, 0.0), base=True)
        if truth:
            bm = WD("#6a5a4a", "#5a4a3c", scale=3, bump=0.6)
            for k, (z, r) in enumerate([(2.0, 4), (2.8, -5), (3.6, 3)]):
                box("board", (3.2, 0.06, 0.38), bm, R, loc=(wx, RD_ - 0.42 - k * 0.01, z), rot=(0, RAD(r), 0))
            _web_corners(R, True, wx)
            ceil_threads(R, [-3.2, 0.6], RD_ - 0.3, 3.7, 2.8)
    return dict(wall=wall, wain=wain, wain_h=1.1, floor=floor, trim=trim, decor=decor, rug=lambda R, t: None, win_x=WIN["inn"],
                light="#ffc27a", key=("#ffb878", 3.4), world="#8a6a58")


# =========================================================================== BELL TOWER
def cfg_bell_tower():
    def wall(plane="xz"): return ST("#bdb4a6", "#a79e92", plane=plane, scale=2.0, bump=1.0, wear=0.5, moss=0.1)
    def floor(): return tex_toon("cobble", "#8e8a86", "#807c80", plane="xy", scale=2.2, bump=1.0, wear=0.4)
    def trim(): return ST("#8a847c", "#6e6a6a", scale=3, bump=0.8)

    def decor(R, wx, truth):
        box("band", (14, 0.1, 0.32), PL("#e0d6c2", "#cfc4ae", wear=0.3), R, loc=(0, RD_ - 0.07, 3.5))
        for x in (-5.4, -2.4):
            box("slitf", (0.7, 0.16, 2.1), ST("#a79e92", "#8a847c", scale=3), R, loc=(x, RD_ - 0.1, 1.9))
            box("slit", (0.34, 0.1, 1.8), glow("#ffb070" if not truth else "#4a5a82", 1.6 if not truth else 0.8), R, loc=(x, RD_ - 0.17, 2.0))
            frustum("slita", 0.35, 0.35, 0.16, ST("#a79e92", "#8a847c", scale=3), R, loc=(x, RD_ - 0.02, 3.0), rot=(RAD(90), 0, 0), seg=12)
        for z in (4.6,):
            beam_x(R, RD_ - 0.25, z, 14, 0.3, "#4a3220")
        for x in (-3.0, 3.0, 6.4):
            link_cyl("brace", (x, RD_ - 0.25, 4.6), (x - 0.9, RD_ - 0.25, 3.8), 0.09, WDT(), R, seg=5)
        for i, x in enumerate((-6.0, -4.0, 6.0)):
            rope_hook = pivot("hk", (x, RD_ - 0.15, 2.8), R)
            ellipsoid("hk", 0.07, toon("gold", rim=0.5), rope_hook, seg=6, rings=4)
        frustum("med", 2.4, 2.4, 0.015, tex_toon("stone", "#b9b0a2", "#9a9288", scale=3, plane="xy", bump=0.6), R, loc=(0.4, 0.4, 0.0), seg=36)
        frustum("med2", 2.0, 2.0, 0.025, tex_toon("cobble", "#8c8884", "#6e6a72", scale=4, plane="xy", bump=0.9), R, loc=(0.4, 0.4, 0.0), seg=36)
        if truth:
            crack_fx(R, (-1.5, RD_ - 0.1, 3.3), 2.5)
            _web_corners(R, True, wx)
    return dict(wall=wall, wain=None, wain_h=0, floor=floor, trim=trim, decor=decor, rug=lambda R, t: None, win_x=WIN["bell_tower"],
                light="#ffd8a0", key=("#ffd098", 3.2), world="#7a7aa8")


# =========================================================================== TAILOR
def cfg_tailor():
    def wall(plane="xz"): return PL("#e9b7ae", "#dba198", plane=plane, wear=0.3, bump=0.5)
    def wain(): return tex_toon("stripes", "#2f7d6f", "#f3e4c4", scale=3.0, plane="xz", bump=0.5, wear=0.3)
    def floor(): return WD("#c9a06a", "#b08850", plane="xy", scale=2.4, bump=0.7, wear=0.3)
    def trim(): return WD("#f3e4c4", "#e0cfa8", scale=3, bump=0.4)

    def decor(R, wx, truth):
        # measuring tape frieze
        box("tape", (14, 0.05, 0.28), toon("#f2d36a", rim=0.3), R, loc=(0, RD_ - 0.07, 4.25))
        for i in range(70):
            box("tk", (0.018, 0.02, 0.1 if i % 5 == 0 else 0.06), toon("#3a2a22", rim=0), R, loc=(-6.9 + i * 0.2, RD_ - 0.1, 4.27 + (0.06 if i % 5 == 0 else 0.0) * 0))
        beam_x(R, RD_ - 0.3, 4.75, 14, 0.24, "#5a3a24")
        _bunting(R, -6.4, 6.4, 3.9, 0.35, ["#c44b3f", "#e8b04a", "#4f7ad8", "#35b39a", "#a07ad8", "#f3e4c4"], wx, 17, truth, "weave", 1.9)
        box("rugr", (4.4, 2.6, 0.02), FAB("stripes", "#2f7d6f", "#f3e4c4", scale=5, plane="xy", bump=0.7), R, loc=(1.8, -0.9, 0.0), base=True)
        if truth:
            _web_corners(R, True, wx)
            ceil_threads(R, [-5.0, -1.0, 2.0, 5.0], RD_ - 0.3, 5.0, 3.4)
    return dict(wall=wall, wain=wain, wain_h=1.2, floor=floor, trim=trim, decor=decor, rug=lambda R, t: None, win_x=WIN["tailor"],
                light="#ffd0c0", key=("#ffd4b0", 3.3), world="#9a7aa0")


# =========================================================================== SCHOOL
def cfg_school():
    def wall(plane="xz"): return PL("#f2e0a0", "#e6cf88", plane=plane, wear=0.3, bump=0.5)
    def wain(): return BR("#b4553a", "#9c4630", plane="xz", scale=2.2, bump=0.9, wear=0.3)
    def floor(): return WD("#b88a58", "#9e7242", plane="xy", scale=2.4, bump=0.7, wear=0.4)
    def trim(): return WD("#f6efe0", "#e6dcc6", scale=3, bump=0.4)

    def decor(R, wx, truth):
        cols = ["#c44b3f", "#4f7ad8", "#e8b04a", "#35b39a", "#a07ad8"]
        if not truth:
            for i in range(30):
                box("fr", (0.4, 0.04, 0.4), toon(cols[i % 5], rim=0.2), R, loc=(-6.6 + i * 0.45, RD_ - 0.07, 4.5))
                box("sq", (0.2, 0.02, 0.025), toon("#f6efe0", rim=0), R, loc=(-6.6 + i * 0.45, RD_ - 0.1, 4.5 + (i % 3 - 1) * 0.07))
            # round wall clock
            frustum("ck", 0.4, 0.4, 0.08, WD("#8a5a30", "#704826", scale=3), R, loc=(-0.2, RD_ - 0.1, 3.5), rot=(RAD(90), 0, 0), seg=24)
            frustum("ckf", 0.33, 0.33, 0.04, toon("#f6efe0", rim=0.2), R, loc=(-0.2, RD_ - 0.17, 3.5), rot=(RAD(90), 0, 0), seg=24)
            link_cyl("h1", (-0.2, RD_ - 0.22, 3.5), (-0.2, RD_ - 0.22, 3.75), 0.02, toon("#2a2a2a", rim=0), R, seg=4)
            link_cyl("h2", (-0.2, RD_ - 0.23, 3.5), (0.0, RD_ - 0.23, 3.4), 0.015, toon("#2a2a2a", rim=0), R, seg=4)
        # coat pegs with caps
        for i, x in enumerate((-6.3, -5.7, -5.1)):
            hook_peg(R, (x, RD_ - 0.12, 2.5))
            ellipsoid("cap", 0.17, FAB("weave", ["#4f7ad8", "#c44b3f", "#7a5a3a"][i], "#f3e4c4", scale=14), R, loc=(x, RD_ - 0.2, 2.35), scale=(1, 0.7, 0.6), seg=10, rings=6)
        rug_round(R, (0.6, 1.6, 0.0), 1.7, "#4f7ad8", "#f6efe0", "#e8b04a")
        if truth:
            _web_corners(R, True, wx)
            ceil_threads(R, [-6.0, -4.4, -2.8, -1.2, 0.4, 2.0, 3.6, 5.0], RD_ - 0.3, 5.0, 2.9, GREY, 0.05)
    return dict(wall=wall, wain=wain, wain_h=1.0, floor=floor, trim=trim, decor=decor, rug=lambda R, t: None, win_x=WIN["school"],
                light="#fff0b8", key=("#fff0c0", 3.4), world="#9a9ac0")


# =========================================================================== FISHER
def cfg_fisher():
    def wall(plane="xz"): return WD("#5a4636", "#4a382a", plane=plane, scale=2.2, along="v", bump=0.9, wear=0.6)
    def wain(): return WD("#3a2c22", "#2e231a", scale=2.6, along="v", bump=0.8, wear=0.9)
    def floor(): return WD("#6a5240", "#54402e", plane="xy", scale=2.6, bump=0.8, wear=0.7)
    def trim(): return WD("#3a2c22", "#2e231a", scale=3, bump=0.6)

    def decor(R, wx, truth):
        # glass floats on a rope garland
        pts = [(-6.6 + 13.2 * t / 30, RD_ - 0.2, 4.4 - 0.45 * math.sin(math.pi * t / 30)) for t in range(31)]
        pts = [p for p in pts if not (wx - 1.6 < p[0] < wx + 1.6)]
        rope(R, pts, 0.025)
        for i in range(12):
            x = -6.3 + i * 1.08
            if wx - 1.6 < x < wx + 1.6:
                continue
            z = 4.4 - 0.45 * math.sin(math.pi * (x + 6.6) / 13.2)
            ellipsoid("fl", 0.2, glow(["#35d3b0", "#7ad8c8", "#9ad8f0"][i % 3], 1.0 if not truth else 0.5, alpha=0.85), R, loc=(x, RD_ - 0.25, z - 0.28), seg=12, rings=8)
            tube("net", [(x - 0.2, RD_ - 0.25, z - 0.1), (x, RD_ - 0.25, z - 0.5), (x + 0.2, RD_ - 0.25, z - 0.1)], 0.01, toon("#c9b48a", rim=0), R)
        # ship's wheel
        wp = pivot("wheel", (-5.0, RD_ - 0.2, 3.1), R)
        frustum("w", 0.52, 0.52, 0.07, WD("#8a5a30", "#704826", scale=4), wp, rot=(RAD(90), 0, 0), seg=24, caps=(False, False))
        frustum("w2", 0.3, 0.3, 0.07, WD("#8a5a30", "#704826", scale=4), wp, rot=(RAD(90), 0, 0), seg=16, caps=(False, False))
        for k in range(8):
            a = k * math.pi / 4
            link_cyl("sp", (0, 0, 0), (math.cos(a) * 0.62, 0, math.sin(a) * 0.62), 0.025, WD("#8a5a30", "#704826", scale=4), wp, seg=5)
        ellipsoid("hub", 0.08, toon("gold", rim=0.5), wp, seg=8, rings=6)
        # braided rope mat
        for i, (rr, c) in enumerate([(2.6, "#b99a6a"), (2.2, "#9a7e52"), (1.8, "#b99a6a"), (1.4, "#9a7e52"), (1.0, "#b99a6a")]):
            frustum("rg", rr, rr, 0.012 + i * 0.004, FAB("weave", c, c, scale=20, plane="xy", bump=1.0), R, loc=(0.5, -0.9, 0.0), seg=28, scale=(1.35, 0.8, 1))
        if truth:
            ellipsoid("pud", 1.0, glow("#3a4a6a", 0.5, alpha=0.8), R, loc=(3.2, -2.9, 0.03), scale=(1.8, 0.8, 0.02), seg=12, rings=4)
            _web_corners(R, True, wx)
            for x in (-4.0, -1.0, 4.0):
                cobweb(R, (x, RD_ - 0.2, 4.5), 0.9)
    return dict(wall=wall, wain=wain, wain_h=1.0, floor=floor, trim=trim, decor=decor, rug=lambda R, t: None, win_x=WIN["fisher"],
                light="#ffe0a8", key=("#ffd8a0", 3.0), world="#6a7aa0")


# =========================================================================== WORKSHOP
def cfg_workshop():
    def wall(plane="xz"): return BR("#9a5a42", "#85483a", plane=plane, scale=2.0, bump=1.0, wear=0.6, soot=0.25)
    def wain(): return WD("#4a3a30", "#3a2c24", scale=2.6, along="v", bump=0.8)
    def floor(): return tex_toon("cobble", "#8a8480", "#7c7878", plane="xy", scale=2.4, bump=1.0, wear=0.6)
    def trim(): return WD("#3a3036", "#2e262c", scale=3, bump=0.6)

    def decor(R, wx, truth):
        beam_x(R, RD_ - 0.25, 4.65, 14, 0.3, "#3a2c24")
        for x in (-5.9, -1.8, 3.4):
            post_z(R, x, RD_ - 0.1, 5.0, 0.28, "#3a2c24")
        # overhead belt gears
        gear(R, (-5.9, RD_ - 0.3, 4.1), 0.55, 12, 0.1, "#9a7a4a")
        gear(R, (-4.7, RD_ - 0.3, 4.55), 0.38, 9, 0.1, "#b4854a")
        gear(R, (3.4, RD_ - 0.3, 4.2), 0.5, 11, 0.1, "#9a7a4a")
        gear(R, (4.4, RD_ - 0.3, 4.55), 0.32, 8, 0.1, "#b4854a")
        link_cyl("pipe", (-6.8, RD_ - 0.3, 0.55), (6.8, RD_ - 0.3, 0.55), 0.07, toon("#5a5a64", rim=0.5), R, seg=8)
        for x in (-6.4, -0.6, 5.2):
            box("pbr", (0.12, 0.1, 0.18), toon("#3a3a44", rim=0.3), R, loc=(x, RD_ - 0.3, 0.55))
        box("plate", (4.2, 2.6, 0.025), toon("#4a4a56", rim=0.5), R, loc=(0.4, -0.2, 0.0), base=True)
        for i in range(8):
            for j in range(4):
                ellipsoid("rv", 0.03, toon("#7a7a88", rim=0.6), R, loc=(-1.5 + i * 0.43, -1.3 + j * 0.8, 0.03), scale=(1, 1, 0.5), seg=5, rings=3)
        if truth:
            _web_corners(R, True, wx)
            for gx in (-5.9, 3.4):
                tube("gt", [(gx - 0.8, RD_ - 0.4, 5.0), (gx, RD_ - 0.4, 4.1), (gx + 0.7, RD_ - 0.4, 5.0)], 0.01, toon(GREY, rim=0), R)
    return dict(wall=wall, wain=wain, wain_h=1.0, floor=floor, trim=trim, decor=decor, rug=lambda R, t: None, win_x=WIN["workshop"],
                light="#ffd8a0", key=("#ffc890", 3.2), world="#7a6a7a")


# =========================================================================== LIBRARY
def cfg_library():
    def wall(plane="xz"): return WD("#5c3a28", "#4a2e20", plane=plane, scale=3.0, along="v", bump=0.8, wear=0.4)
    def floor(): return tex_toon("checker", "#8a5a38", "#6a4228", plane="xy", scale=1.3, bump=0.8, wear=0.4)
    def trim(): return WD("#3a2418", "#2e1c12", scale=3, bump=0.5)

    def decor(R, wx, truth):
        rnd = random.Random(11)
        box("shb", (9.2, 0.45, 0.07), WD("#6a4630", "#553622", scale=3), R, loc=(-2.6, RD_ - 0.22, 3.95))
        cols = ("wine", "#4f7ad8", "forest", "gold", "plum", "#c9b48a", "#35b39a")
        x = -7.0
        while x < 1.9:
            if truth and rnd.random() < 0.35:
                x += 0.22
                continue
            t = rnd.uniform(0.07, 0.13)
            hh = rnd.uniform(0.55, 0.85)
            box("bk", (t, 0.3, hh), toon(cols[int(rnd.random() * 7)], rim=0.3), R, loc=(x + t / 2, RD_ - 0.25, 3.98), base=True)
            x += t + 0.01
        link_cyl("rod", (-7.0, RD_ - 0.5, 3.8), (2.0, RD_ - 0.5, 3.8), 0.03, toon("gold", rim=0.6), R, seg=6)
        box("rug", (5.4, 3.2, 0.02), FAB("weave", "#7a2a3a", "#e8b04a", scale=8, plane="xy", bump=0.7), R, loc=(1.2, 0.1, 0.0), base=True)
        box("rugb", (5.7, 3.45, 0.015), toon("#3a1a20", rim=0.2), R, loc=(1.2, 0.1, 0.0), base=True)
        if truth:
            _web_corners(R, True, wx)
            # threads join the shelf rows like puppet strings
            for k in range(7):
                xx = -6.3 + k * 1.15
                tube("pt", [(xx, RD_ - 0.5, 5.0), (xx + 0.1, RD_ - 0.5, 4.4), (xx, RD_ - 0.4, 4.0)], 0.008, toon(GREY, rim=0), R)
    return dict(wall=wall, wain=None, wain_h=0, floor=floor, trim=trim, decor=decor, rug=lambda R, t: None, win_x=WIN["library"],
                light="#ffcf98", key=("#ffc888", 3.0), world="#7a5a6a")


# =========================================================================== OBSERVATORY
def cfg_observatory():
    def wall(plane="xz"): return PL("#33407a", "#2a3570", plane=plane, wear=0.3, bump=0.4)
    def wain(): return WD("#2e3252", "#26294a", scale=2.6, along="v", bump=0.8)
    def floor(): return WD("#4a4a64", "#3a3a54", plane="xy", scale=2.4, bump=0.7, wear=0.4)
    def trim(): return WD("#9a7a3a", "#7a5e2c", scale=3, bump=0.5)

    def decor(R, wx, truth):
        rnd = random.Random(5)
        pts = []
        for i in range(30):
            x, z = rnd.uniform(-6.5, 6.5), rnd.uniform(1.9, 4.8)
            if wx - 1.8 < x < wx + 1.8 or (-4.4 < x < -2.4 and 0.9 < z < 3.4):
                continue
            if truth and rnd.random() < 0.4:
                continue
            pts.append((x, z))
            ellipsoid("st", 0.05 + rnd.random() * 0.04, glow("#ffe9a8", 3 if not truth else 0.5), R, loc=(x, RD_ - 0.08, z), scale=(1, 0.3, 1), seg=6, rings=4)
        for a, b in zip(pts[:-1:2], pts[1::2]):
            if abs(a[0] - b[0]) < 1.6:
                link_cyl("cn", (a[0], RD_ - 0.08, a[1]), (b[0], RD_ - 0.08, b[1]), 0.008, toon("#c9b070" if not truth else "#4a4e66", rim=0), R, seg=3)
        # astrolabe ring
        ap = pivot("astro", (-0.6, RD_ - 0.1, 3.4), R)
        for rr, c in ((0.95, "#d9b05a"), (0.72, "#b4854a"), (0.45, "#d9b05a")):
            frustum("ar", rr, rr, 0.04, toon(c if not truth else "#6a6a7a", rim=0.5), ap, rot=(RAD(90), 0, 0), seg=32, caps=(False, False))
        for k in range(12):
            a = k * math.pi / 6
            link_cyl("ray", (math.cos(a) * 0.45, -0.02, math.sin(a) * 0.45), (math.cos(a) * 0.95, -0.02, math.sin(a) * 0.95), 0.015, toon("#d9b05a" if not truth else "#6a6a7a", rim=0.4), ap, seg=4)
        if truth:
            # the big painted eye in the sky
            ep = pivot("eye", (-1.8, RD_ - 0.12, 4.15), R)
            ellipsoid("ey", 0.8, toon("#d8dcec", rim=0), ep, scale=(1.7, 0.08, 0.65), seg=20, rings=10)
            ellipsoid("ir", 0.34, toon("#4a6a8a", rim=0), ep, loc=(0.05, -0.06, 0), scale=(1, 0.2, 1), seg=14, rings=8)
            ellipsoid("pu", 0.14, toon("#0a0c18", rim=0), ep, loc=(0.05, -0.11, 0), scale=(1, 0.2, 1), seg=10, rings=6)
            _web_corners(R, True, wx)
            crack_fx(R, (5.4, RD_ - 0.1, 4.8), 1.8)
        rug_round(R, (0.4, -0.9, 0.0), 3.0, "#2a3a8a", "#e8b04a", "#4f7ad8")
    return dict(wall=wall, wain=wain, wain_h=0.9, floor=floor, trim=trim, decor=decor, rug=lambda R, t: None, win_x=WIN["observatory"],
                light="#c8d8ff", key=("#b8c8ff", 2.6), world="#4a5aa0")


# =========================================================================== STORIES
def cfg_stories():
    def wall(plane="xz"): return WD("#8a5a32", "#704826", plane=plane, scale=1.6, along="u", bump=1.2, wear=0.4)
    def floor(): return tex_toon("cobble", "#7a7068", "#6a625c", plane="xy", scale=2.2, bump=1.0, wear=0.5)
    def trim(): return WD("#4a3020", "#3a2418", scale=3, bump=0.6)

    def decor(R, wx, truth):
        for x in (-6.5, -2.0, 1.8, 6.5):
            post_z(R, x, RD_ - 0.12, 5.0, 0.34)
        beam_x(R, RD_ - 0.14, 4.4, 14, 0.3)
        # paper-lantern garland
        cols = ["#e8884a", "#e8b04a", "#c44b3f", "#4f9a8a", "#a07ad8"]
        for k in range(9):
            x = -6.0 + k * 1.5
            if wx - 1.5 < x < wx + 1.5:
                continue
            z = 3.9 - 0.2 * math.sin(k)
            link_cyl("str", (x, RD_ - 0.2, 4.4), (x, RD_ - 0.2, z + 0.3), 0.008, toon("#d9c9a8", rim=0), R, seg=3)
            ellipsoid("pl", 0.24, glow(cols[k % 5], 2.2 if not truth else 0.4), R, loc=(x, RD_ - 0.2, z), scale=(0.9, 0.9, 1.15), seg=12, rings=8)
        # hearth ring stones + big round rug
        rug_round(R, (0.0, 0.7, 0.0), 3.9, "#8a3a2e", "#e8b04a", "#4f7a5a")
        if truth:
            _web_corners(R, True, wx)
            for x in (-4.0, 0.5, 5.0):
                cobweb(R, (x, RD_ - 0.2, 4.3), 1.0)
    return dict(wall=wall, wain=None, wain_h=0, floor=floor, trim=trim, decor=decor, rug=lambda R, t: None, win_x=WIN["stories"],
                light="#ffb868", key=("#ffa860", 3.4), world="#7a5a60")


# =========================================================================== FARM
def cfg_farm():
    def wall(plane="xz"): return PL("#efdcb6", "#e2c89a", plane=plane, wear=0.35, bump=0.5)
    def wain(): return WD("#9a3a2e", "#842f26", scale=2.8, along="v", bump=0.8, wear=0.4)
    def floor(): return tex_toon("checker", "#c9895c", "#a8683f", plane="xy", scale=1.1, bump=0.8, wear=0.4)
    def trim(): return WD("#e8d6b0", "#d4c298", scale=3, bump=0.4)

    def decor(R, wx, truth):
        _rail(R, -6.4, 0.2, 3.6)
        for i, x in enumerate((-6.0, -5.2, -4.4, -3.6, -2.8, -2.0, -1.2, -0.4)):
            r = 0.2 + 0.05 * (i % 3)
            link_cyl("hg", (x, RD_ - 0.14, 3.6), (x, RD_ - 0.14, 3.42), 0.012, toon("leather_d", rim=0), R, seg=3)
            frustum("pot", r, r * 0.85, r * 0.9, toon("#c0693f" if not truth else "#8a8a94", rim=0.7), R, loc=(x, RD_ - 0.16, 3.42 - r * 0.9), rot=(RAD(-90), 0, 0), seg=12)
        # onion / garlic strings
        for x in (1.4, 2.2):
            if truth:
                continue
            tube("str", [(x, RD_ - 0.14, 4.7), (x, RD_ - 0.14, 3.3)], 0.012, toon("#d9c9a8", rim=0), R)
            for k in range(7):
                ellipsoid("on", 0.1, toon("#e8d6a0" if x < 2 else "#f3e4c4", rim=0.3), R, loc=(x + (k % 2 - 0.5) * 0.08, RD_ - 0.16, 4.5 - k * 0.2), scale=(1, 0.8, 1.1), seg=8, rings=6)
        # embroidered sampler
        box("smp", (0.9, 0.05, 0.7), WD("#8a5a30", "#704826", scale=3), R, loc=(-0.4, RD_ - 0.08, 2.3))
        box("smp2", (0.76, 0.03, 0.56), FAB("weave", "#f3e4c4", "#c44b3f", scale=18, plane="xz"), R, loc=(-0.4, RD_ - 0.12, 2.3))
        box("rag", (4.2, 2.6, 0.02), FAB("stripes", "#c44b3f", "#f3e4c4", scale=6, plane="xy", bump=0.8), R, loc=(2.8, -0.9, 0.0), base=True)
        if truth:
            _web_corners(R, True, wx)
    return dict(wall=wall, wain=wain, wain_h=1.4, floor=floor, trim=trim, decor=decor, rug=lambda R, t: None, win_x=WIN["farm"],
                light="#ffe0a0", key=("#ffd8a0", 3.3), world="#9a8070")


# =========================================================================== SHEPHERD
def cfg_shepherd():
    def wall(plane="xz"): return WD("#a68a62", "#8e7450", plane=plane, scale=2.4, along="v", bump=0.9, wear=0.6)
    def floor(): return tex_toon("thatch", "#d2a24e", "#b38238", plane="xy", scale=2.6, bump=0.9)
    def trim(): return WD("#6a4a30", "#54382a", scale=3, bump=0.6)

    def decor(R, wx, truth):
        # wool skein garland
        cols = ["#f3e4c4", "#c44b3f", "#4f7ad8", "#e8b04a", "#35b39a", "#a07ad8"]
        _rail(R, -6.3, 1.8, 4.1)
        for i in range(8):
            x = -6.0 + i * 1.0
            tube("sk", [(x, RD_ - 0.16, 4.1), (x - 0.08, RD_ - 0.2, 3.75), (x + 0.02, RD_ - 0.2, 3.5), (x + 0.08, RD_ - 0.2, 3.75), (x, RD_ - 0.16, 4.1)], 0.055,
                 FAB("knit", cols[i % 6], cols[(i + 3) % 6], scale=20, bump=1.0), R)
        # shelf with bowls + candle
        box("shl", (1.8, 0.35, 0.07), WD("#6a4a30", "#54382a", scale=3), R, loc=(1.0, RD_ - 0.22, 3.0))
        for k, x in enumerate((0.4, 0.8)):
            frustum("bw", 0.15, 0.1, 0.12, toon("#c0693f" if k == 0 else "#f3e4c4", rim=0.3), R, loc=(x, RD_ - 0.22, 3.04), seg=12)
        candle(R, (1.5, RD_ - 0.22, 3.04), 0.14, not truth)
        # sheepskin rug
        for k, (dx, dy, rr) in enumerate([(0, 0, 1.3), (0.9, 0.2, 0.8), (-0.9, 0.3, 0.8), (0.3, -0.7, 0.7), (-0.5, -0.6, 0.6)]):
            ellipsoid("sk", rr, FAB("knit", "#f6f0e6", "#e6dcc6", scale=14, plane="xy", bump=1.0), R, loc=(1.6 + dx, -1.2 + dy, 0.015), scale=(1, 0.78, 0.04), seg=14, rings=6)
        if truth:
            for k in range(5):
                tube("rt", [(1.0 + k * 0.5, -1.0, 0.1), (1.0 + k * 0.5, -1.0, 1.4), (1.0 + k * 0.5 + 0.1, -1.0, 2.8)], 0.008, toon(GREY, rim=0), R)
            _web_corners(R, True, wx)
    return dict(wall=wall, wain=None, wain_h=0, floor=floor, trim=trim, decor=decor, rug=lambda R, t: None, win_x=WIN["shepherd"],
                light="#ffd8a0", key=("#ffd098", 3.2), world="#8a7a70")


# =========================================================================== HERBS
def cfg_herbs():
    def wall(plane="xz"): return PL("#dcecd0", "#c9e0c0", plane=plane, wear=0.35, bump=0.4)
    def floor(): return BR("#c4784a", "#a8603a", plane="xy", scale=1.8, bump=0.9, wear=0.4)
    def trim(): return WD("#f3f0e4", "#dfe0d0", scale=3, bump=0.4)

    def decor(R, wx, truth):
        fr = WD("#f3f0e4", "#e2e6d8", scale=3, bump=0.3)
        for x in (-6.8, -4.0, -1.2, 1.6, 6.8):
            box("mul", (0.14, 0.12, 5.0), fr, R, loc=(x, RD_ - 0.07, 0), base=True)
        for z in (3.4, 4.8):
            box("tr", (14, 0.12, 0.12), fr, R, loc=(0, RD_ - 0.07, z))
        # pane tint behind frames (mint glass)
        for x0, x1 in ((-6.8, -4.0), (-4.0, -1.2), (-1.2, 1.6)):
            box("pane", (x1 - x0 - 0.1, 0.03, 1.2), glow("#bfe8d8" if not truth else "#5a6a72", 0.6 if not truth else 0.3, alpha=0.5), R, loc=((x0 + x1) / 2, RD_ - 0.1, 4.1))
        # bean vines
        rnd = random.Random(2)
        for x in (-6.7, -3.9, 1.7, 6.7):
            pts = [(x + math.sin(k * 1.3) * 0.12, RD_ - 0.2, 5.0 - k * 0.45) for k in range(9)]
            tube("vn", pts, 0.02, toon("#2f6b48" if not truth else "#6a5a44", rim=0), R)
            for k, p in enumerate(pts):
                ellipsoid("lf", 0.1, toon(("leaf1", "leaf2", "leaf3")[k % 3] if not truth else "#5a4c3c", rim=0.3), R, loc=(p[0] + (0.09 if k % 2 else -0.09), p[1] - 0.03, p[2]), scale=(1, 0.3, 0.8), seg=8, rings=5)
        # hanging herb bundles
        for k in range(10):
            x = -6.0 + k * 1.3
            if wx - 1.5 < x < wx + 1.5:
                continue
            link_cyl("hs", (x, RD_ - 0.25, 4.8), (x, RD_ - 0.25, 4.45), 0.008, toon("#d9c9a8", rim=0), R, seg=3)
            ellipsoid("hb", 0.1, toon(["#6f9a3c", "#8fb04a", "#a8a04a", "#7a5a8a"][k % 4] if not truth else "#4a4236", rim=0.3), R, loc=(x, RD_ - 0.25, 4.3), scale=(0.8, 0.8, 1.9), seg=8, rings=6)
        box("slab", (6.4, 1.1, 0.03), ST("#b9b0a2", "#9a9288", plane="xy", scale=3, bump=0.8), R, loc=(0.2, -0.1, 0.0), base=True)
        if truth:
            for x in (-5.4, -2.6, 0.2):
                crack_fx(R, (x, RD_ - 0.12, 4.9), 1.4)
            _web_corners(R, True, wx)
    return dict(wall=wall, wain=None, wain_h=0, floor=floor, trim=trim, decor=decor, rug=lambda R, t: None, win_x=WIN["herbs"],
                light="#e8ffd0", key=("#f0ffd8", 3.2), world="#8aa88a")


# =========================================================================== FAIRY
def cfg_fairy():
    def wall(plane="xz"): return WD("#6a4a30", "#58391f", plane=plane, scale=3.4, along="v", bump=1.3, wear=0.7, moss=0.45)
    def floor(): return tex_toon("plain", "#6bb25a", "#4a8a3e", plane="xy", scale=3.0, bump=0.7, wear=0.2)
    def trim(): return WD("#58391f", "#47301a", scale=3, bump=0.9, moss=0.3)

    def decor(R, wx, truth):
        rnd = random.Random(8)
        bark = WD("#58391f", "#47301a", scale=3, bump=1.0, moss=0.3)
        for x in (-6.6, -2.2, 1.9, 6.7):
            pts = [(x + math.sin(k) * 0.25, RD_ - 0.15, 5.0 - k * 0.65) for k in range(8)]
            tube("root", pts, 0.16, bark, R)
        # round fairy windows
        for x, z in ((-5.0, 3.3), (-0.4, 3.9)):
            wp = pivot("rw", (x, RD_ - 0.1, z), R)
            frustum("fr", 0.42, 0.42, 0.1, WD("#6a4a30", "#58391f", scale=4), wp, rot=(RAD(90), 0, 0), seg=20)
            frustum("gl", 0.33, 0.33, 0.04, glow("#ffd890" if not truth else "#1a2030", 3 if not truth else 0.4), wp, loc=(0, -0.08, 0), rot=(RAD(90), 0, 0), seg=20)
            box("mv", (0.03, 0.03, 0.66), toon("wood_d", rim=0), wp, loc=(0, -0.14, 0))
            box("mh", (0.66, 0.03, 0.03), toon("wood_d", rim=0), wp, loc=(0, -0.14, 0))
        # hanging glow orbs
        for k in range(8):
            x = -6.0 + k * 1.7
            z = 3.9 - 0.4 * (k % 3)
            tube("st", [(x, RD_ - 0.3, 5.0), (x + 0.05, RD_ - 0.3, z + 0.3)], 0.008, toon("#6a5a3a", rim=0), R)
            ellipsoid("orb", 0.11, glow("#ffe9a8" if not truth else GREY, 3.5 if not truth else 0.5), R, loc=(x + 0.05, RD_ - 0.3, z), seg=8, rings=6)
            if not truth:
                halo(R, (x + 0.05, RD_ - 0.3, z), 0.4, 0.3, "#ffe9a8", 1.0)
        # leaf rug
        rug_round(R, (0.6, -0.4, 0.0), 3.2, "#5a9a4a", "#e8d890", "#8fc267")
        if truth:
            _web_corners(R, True, wx)
    return dict(wall=wall, wain=None, wain_h=0, floor=floor, trim=trim, decor=decor, rug=lambda R, t: None, win_x=WIN["fairy"],
                light="#fff0a8", key=("#ffe8a8", 3.0), world="#6a9a7a")


# =========================================================================== GUILD
def cfg_guild():
    def wall(plane="xz"): return ST("#a09a94", "#8a847e", plane=plane, scale=2.0, bump=1.0, wear=0.5)
    def wain(): return WD("#4a3a38", "#3a2c2a", scale=2.8, along="v", bump=0.8)
    def floor(): return tex_toon("cobble", "#86828c", "#78747e", plane="xy", scale=2.2, bump=1.0, wear=0.4)
    def trim(): return WD("#3a2c2a", "#2e2220", scale=3, bump=0.6)

    def decor(R, wx, truth):
        beam_x(R, RD_ - 0.22, 4.7, 14, 0.3, "#3a2c2a")
        # wall sconces
        for x in (-1.9, 1.7, -5.8):
            box("scb", (0.12, 0.14, 0.35), toon("#3a3a44", rim=0.4), R, loc=(x, RD_ - 0.12, 2.8))
            candle(R, (x, RD_ - 0.22, 3.1), 0.2, not truth)
        # spool-peg rail with hanks of yarn
        _rail(R, 1.2, 2.8, 3.0)
        cols = ["#c44b3f", "#4f7ad8", "#e8b04a", "#35b39a", "#a07ad8"]
        for i in range(5):
            x = 1.4 + i * 0.33
            tube("hk", [(x, RD_ - 0.16, 3.0), (x - 0.07, RD_ - 0.2, 2.6), (x, RD_ - 0.2, 2.4), (x + 0.07, RD_ - 0.2, 2.6), (x, RD_ - 0.16, 3.0)], 0.04,
                 FAB("knit", cols[i], cols[(i + 2) % 5], scale=20, bump=1.0), R)
        # long red runner with gold edging
        box("rn", (8.4, 1.9, 0.02), FAB("weave", "#7a2a3a", "#a04a5a", scale=8, plane="xy", bump=0.7), R, loc=(0.2, -1.6, 0.0), base=True)
        box("rb", (8.7, 2.15, 0.015), toon("#e8b04a", rim=0.3), R, loc=(0.2, -1.6, 0.0), base=True)
        if truth:
            _web_corners(R, True, wx)
            ceil_threads(R, [-1.6, -0.4, 0.8, 2.0], -1.6, 5.0, 3.2, GREY, 0.04)
    return dict(wall=wall, wain=wain, wain_h=1.2, floor=floor, trim=trim, decor=decor, rug=lambda R, t: None, win_x=WIN["guild"],
                light="#ffd8b0", key=("#ffd0a0", 3.1), world="#7a7090")


# =========================================================================== LIGHTHOUSE
def cfg_lighthouse():
    def wall(plane="xz"): return PL("#f2eee6", "#e0dad0", plane=plane, wear=0.4, bump=0.4)
    def wain(): return tex_toon("plain", "#c44b3f", "#a83a30", scale=2.0, plane="xz", bump=0.4, wear=0.4)
    def floor(): return tex_toon("cobble", "#98979f", "#8a8992", plane="xy", scale=2.4, bump=1.0, wear=0.4)
    def trim(): return WD("#8a4a38", "#6e3a2c", scale=3, bump=0.5)

    def decor(R, wx, truth):
        cols = ["#4f7ad8", "#f6efe0", "#c44b3f", "#e8b04a"]
        _bunting(R, -6.4, 6.4, 4.5, 0.4, cols, wx, 16, truth, "weave", 1.9)
        # lifebuoy
        lp = pivot("buoy", (1.0, RD_ - 0.2, 3.1), R)
        for k in range(8):
            a0, a1 = k * math.pi / 4, (k + 1) * math.pi / 4
            pts = [(math.cos(a0 + (a1 - a0) * t / 3) * 0.46, 0, math.sin(a0 + (a1 - a0) * t / 3) * 0.46) for t in range(4)]
            tube("lb", pts, 0.1, toon("#c44b3f" if k % 2 == 0 else "#f6efe0", rim=0.3), lp)
        # brass barometer
        bp = pivot("baro", (-5.3, RD_ - 0.12, 3.0), R)
        frustum("bo", 0.3, 0.3, 0.08, toon("gold", rim=0.6), bp, rot=(RAD(90), 0, 0), seg=20)
        frustum("bf", 0.24, 0.24, 0.04, toon("#f6efe0", rim=0.2), bp, loc=(0, -0.08, 0), rot=(RAD(90), 0, 0), seg=20)
        link_cyl("nd", (0, -0.14, 0), (0.1, -0.14, 0.17), 0.012, toon("#2a2a2a", rim=0), bp, seg=4)
        # wall lamps
        for x in (-1.6, 2.4):
            box("lb", (0.1, 0.1, 0.3), toon("gold", rim=0.6), R, loc=(x, RD_ - 0.1, 2.6))
            lantern2(R, (x, RD_ - 0.12, 3.3), "#fff0c0", 3, 0.16, hang=False)
        rug_round(R, (4.0, -1.8, 0.0), 2.0, "#2a3a6a", "#f6efe0", "#c44b3f")
        if truth:
            _web_corners(R, True, wx)
    return dict(wall=wall, wain=wain, wain_h=1.1, floor=floor, trim=trim, decor=decor, rug=lambda R, t: None, win_x=WIN["lighthouse"],
                light="#f0f4ff", key=("#e8f0ff", 3.2), world="#8a9ab8")


from iw2_layout import WIN_X as WIN  # noqa  (used by the cfg functions at call time)

CFGS = {"inn": cfg_inn, "bell_tower": cfg_bell_tower, "tailor": cfg_tailor, "school": cfg_school, "fisher": cfg_fisher,
        "workshop": cfg_workshop, "library": cfg_library, "observatory": cfg_observatory, "stories": cfg_stories,
        "farm": cfg_farm, "shepherd": cfg_shepherd, "herbs": cfg_herbs, "fairy": cfg_fairy, "guild": cfg_guild,
        "lighthouse": cfg_lighthouse}
