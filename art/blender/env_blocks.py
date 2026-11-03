"""Reusable textured props for buildings and interiors (all builders take a parent pivot and a local loc)."""
import math
import random
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env_lib import *  # noqa
import env_lib as EL

_WIN_N = [0]

# ----------------------------------------------------------- material presets
def PL(c1="#efd0a8", c2="#e3bb94", plane="xz", **kw):
    kw.setdefault("bump", 0.5)
    kw.setdefault("wear", 0.45)
    kw.setdefault("scale", 1.0)
    return tex_toon("plaster", c1, c2, plane=plane, **kw)


def WD(c1="#9a6238", c2="#85502c", plane="xz", along="u", scale=2.4, **kw):
    kw.setdefault("bump", 0.6)
    return tex_toon("wood", c1, c2, scale=scale, plane=plane, along=along, **kw)


def WDT(c1="#6b4326", c2="#5a3720", **kw):
    """Dark trim wood, finer."""
    return WD(c1, c2, scale=3.5, rim=0.1, **kw)


def ST(c1="#a8a09a", c2="#8c848a", plane="xz", scale=2.0, **kw):
    kw.setdefault("bump", 1.0)
    kw.setdefault("wear", 0.7)
    return tex_toon("stone", c1, c2, scale=scale, plane=plane, **kw)


def BR(c1="#b4553a", c2="#9a4630", plane="xz", scale=2.0, **kw):
    kw.setdefault("bump", 0.9)
    kw.setdefault("wear", 0.5)
    return tex_toon("brick", c1, c2, scale=scale, plane=plane, **kw)


def TL(c1="#b4553a", c2="#9c4630", scale=3.0, plane="xy", **kw):
    kw.setdefault("bump", 0.9)
    return tex_toon("tiles", c1, c2, scale=scale, plane=plane, **kw)


def TH(c1="#d2a24e", c2="#b38238", scale=2.2, **kw):
    kw.setdefault("bump", 0.9)
    return tex_toon("thatch", c1, c2, scale=scale, plane="xy", **kw)


def FAB(kind, c1, c2, scale=14, plane="xz", **kw):
    kw.setdefault("bump", 0.8)
    kw.setdefault("rim", 0.2)
    return tex_toon(kind, c1, c2, scale=scale, plane=plane, **kw)


def FLAT(c, rim=0.3):
    return toon(c, rim=rim)


# ----------------------------------------------------------- small things
def lantern2(parent, loc, color="amber", glow_s=6, halo=0.3, rotz=0.0, hang=True):
    p = pivot("lantern", loc, parent, rot=(0, 0, rotz))
    d = T = toon("leather_d", rim=0)
    if hang:
        link_cyl("arm", (0, 0, 0), (0, -0.3, 0), 0.02, d, p, seg=5)
        link_cyl("hook", (0, -0.3, 0), (0, -0.3, -0.1), 0.012, d, p, seg=5)
        c = (0, -0.3, -0.24)
    else:
        c = (0, 0, 0.12)
    box("cage", (0.18, 0.18, 0.24), d, p, loc=c)
    box("glass", (0.13, 0.13, 0.2), glow(color, glow_s), p, loc=c)
    frustum("lcap", 0.16, 0.02, 0.1, d, p, loc=(c[0], c[1], c[2] + 0.12), seg=4, rot=(0, 0, RAD(45)))
    ellipsoid("lhalo", halo, glow(color, 3, alpha=0.9, soft=True), p, loc=c, seg=12, rings=8)
    return p


def window(parent, loc, w=0.8, h=0.8, frame="#e8d6b0", shutter=None, flowers=True, curtain=None, glow_s=3.2,
           arch=False, light="window", rotz=0.0, sill="#a8a09a"):
    p = pivot("win", loc, parent, rot=(0, 0, rotz))
    fm = toon(frame, rim=0.15)
    box("frame", (w + 0.2, 0.1, h + 0.2), fm, p, loc=(0, -0.03, 0))
    _WIN_N[0] += 1
    kind = "lit"
    if EL.TRUTH:
        kind = ["dark", "boarded", "teal", "dark", "broken"][_WIN_N[0] % 5]
    if kind in ("dark", "boarded", "broken"):
        box("pane", (w, 0.05, h), toon("#141a28", rim=0), p, loc=(0, -0.08, 0))
        if kind == "broken":
            link_cyl("crk", (-w * .4, -0.11, h * .4), (w * .1, -0.11, -h * .1), 0.012, toon("#9aa6b8", rim=0), p, seg=4)
            link_cyl("crk", (w * .1, -0.11, -h * .1), (w * .4, -0.11, -h * .45), 0.012, toon("#9aa6b8", rim=0), p, seg=4)
            link_cyl("crk", (w * .1, -0.11, -h * .1), (-w * .1, -0.11, -h * .45), 0.012, toon("#9aa6b8", rim=0), p, seg=4)
        if kind == "boarded":
            bm = WD("#6a5a4a", "#5a4a3c", scale=3, bump=0.6)
            for k, (zz, rr) in enumerate([(h * .25, 8), (-h * .15, -6), (-h * .38, 4)]):
                box("board", (w + 0.3, 0.05, 0.14), bm, p, loc=(0, -0.13 - k * 0.01, zz), rot=(0, RAD(rr), 0))
    else:
        gcol = "#35d3b0" if kind == "teal" else light
        box("pane", (w, 0.05, h), glow(gcol, glow_s if kind != "teal" else 1.6), p, loc=(0, -0.08, 0))
        if kind == "lit":
            box("dim", (w, 0.052, h * 0.35), glow("#d9822a", glow_s * 0.7), p, loc=(0, -0.082, -h * 0.325))
    box("mullv", (0.05, 0.07, h), fm, p, loc=(0, -0.1, 0))
    box("mullh", (w, 0.07, 0.045), fm, p, loc=(0, -0.1, 0.08))
    if curtain and not (EL.TRUTH and kind != "teal"):
        cm = FAB("weave", curtain, "#f3e4c4", scale=22, bump=0.4)
        for s in (-1, 1):
            box("curt", (w * 0.28, 0.04, h * 0.95), cm, p, loc=(s * w * 0.36, -0.115, 0.0), rot=(0, 0, s * RAD(5)))
    box("sill", (w + 0.34, 0.22, 0.08), ST(sill, "#8c848a", scale=3, bump=0.5), p, loc=(0, -0.1, -h / 2 - 0.12))
    if shutter:
        sm = WD(shutter, shutter, scale=3, bump=0.5)
        for s in (-1, 1):
            if EL.TRUTH and s == 1:     # one shutter hangs crooked
                box("shutter", (0.3, 0.05, h + 0.12), sm, p, loc=(s * (w / 2 + 0.35), -0.15, -0.05), rot=(0, RAD(14), s * RAD(-30)))
                continue
            box("shutter", (0.3, 0.05, h + 0.12), sm, p, loc=(s * (w / 2 + 0.3), -0.065, 0), rot=(0, 0, s * RAD(-7)))
            box("shslat", (0.22, 0.02, 0.03), toon("wood_d", rim=0), p, loc=(s * (w / 2 + 0.3), -0.1, 0.1))
            box("shslat", (0.22, 0.02, 0.03), toon("wood_d", rim=0), p, loc=(s * (w / 2 + 0.3), -0.1, -0.12))
    if flowers:
        flower_box(p, (0, -0.22, -h / 2 - 0.22), w + 0.1)
    if EL.TRUTH and kind == "teal":
        tube("tdang", [(w * .3, -0.12, h / 2), (w * .35, -0.14, h * .1), (w * .2, -0.15, -h * .2)], 0.012, glow("#35d3b0", 2.4), p)
    return p


def flower_box(parent, loc, w, seed=1, colors=("red", "gold", "white", "wine"), box_c="#9a6238"):
    rnd = random.Random(seed)
    p = pivot("fbox", loc, parent)
    box("fb", (w, 0.17, 0.16), WD(box_c, "#7d4a2a", scale=4, bump=0.4), p)
    box("soil", (w - 0.04, 0.12, 0.03), toon("#3a2a20", rim=0), p, loc=(0, 0, 0.08))
    n = int(w / 0.14)
    for i in range(n):
        x = -w / 2 + 0.1 + i * (w - 0.2) / max(1, n - 1)
        ellipsoid("leaf", 0.075, toon(rnd.choice(["leaf1", "leaf2", "leaf3"]), rim=0), p, loc=(x, 0, 0.14),
                  scale=(1.1, 1, 0.9), seg=8, rings=6)
        ellipsoid("fl", 0.06, toon(colors[i % len(colors)], rim=0.2), p, loc=(x + rnd.uniform(-.03, .03), -0.05, 0.22 + rnd.uniform(0, .06)),
                  seg=8, rings=6)
    # trailing vine
    for k in range(3):
        x = -w / 2 + 0.2 + k * w / 3
        link_cyl("vine", (x, -0.08, 0.05), (x + rnd.uniform(-.05, .05), -0.1, -0.22), 0.012, toon("leaf3", rim=0), p, seg=4)
        ellipsoid("vl", 0.04, toon("leaf2", rim=0), p, loc=(x, -0.1, -0.2), scale=(1, 0.6, 1.4), seg=6, rings=4)
    return p


def door(parent, loc, w=0.95, h=1.8, color="#2f7d6f", frame="#e8d6b0", arch=True, step=True, knob=True, window_=False):
    p = pivot("door", loc, parent)
    fm = toon(frame, rim=0.15)
    wm = WD(color, color, scale=3.0, bump=0.7, along="v")
    box("dframe", (w + 0.26, 0.12, h + 0.12), fm, p, loc=(0, -0.03, h / 2 + 0.03))
    box("leaf", (w, 0.08, h - 0.08), wm, p, loc=(0, -0.09, (h - 0.08) / 2), bevel=0.01)
    if arch:
        frustum("arch", w / 2, w / 2, 0.08, wm, p, loc=(0, -0.05, h - 0.1), rot=(RAD(90), 0, 0), seg=16)
        frustum("archf", w / 2 + 0.13, w / 2 + 0.13, 0.1, fm, p, loc=(0, 0.0, h - 0.1), rot=(RAD(90), 0, 0), seg=16)
    for z in (0.35, h - 0.5):
        box("hinge", (w, 0.04, 0.07), toon("leather_d", rim=0), p, loc=(0, -0.14, z))
    if window_:
        box("dwin", (w * 0.45, 0.04, 0.3), glow("window", 3.4), p, loc=(0, -0.15, h * 0.7))
    if knob:
        ellipsoid("knob", 0.05, toon("gold", rim=0.5), p, loc=(w * 0.32, -0.16, h * 0.46), seg=8, rings=6)
    if step:
        box("step", (w + 0.6, 0.55, 0.14), ST(scale=3, bump=0.6), p, loc=(0, -0.33, 0.07))
        box("step2", (w + 0.9, 0.35, 0.07), ST(scale=3, bump=0.6), p, loc=(0, -0.62, 0.035))
    return p


def bush(parent, loc, r=0.4, col="leaf1", flowers=True, seed=1, fcols=("red", "gold", "white")):
    rnd = random.Random(seed)
    p = pivot("bush", loc, parent)
    mats = [tex_toon("plain", "#4f9a4f", "#3a7a3e", scale=3, bump=0.0, wear=0, ao=0.4),
            tex_toon("plain", "#6cb257", "#4f9a4f", scale=3, bump=0.0, wear=0, ao=0.4)]
    for dx, dy, dz, k in [(0, 0, 0.55, 1), (0.5, 0.05, 0.4, .75), (-0.5, 0.0, 0.4, .75), (0.2, -0.3, 0.35, .6)]:
        ellipsoid("b", r * k, mats[0 if dx >= 0 else 1], p, loc=(dx * r * 1.3, dy * r, dz * r), scale=(1, 1, 0.9), seg=12, rings=8)
    if flowers:
        for i in range(8):
            a = rnd.uniform(0, 6.28)
            ellipsoid("fl", 0.055, toon(rnd.choice(fcols), rim=0.2), p,
                      loc=(math.cos(a) * r * 1.1, -abs(math.sin(a)) * r * 0.9, r * rnd.uniform(0.5, 1.1)), seg=6, rings=5)
    return p


def barrel(parent, loc, r=0.28, h=0.55, col="#a06a3e"):
    p = pivot("barrel", loc, parent)
    m = WD(col, "#85502c", scale=4, along="v", bump=0.6)
    frustum("b", r, r * 0.92, h, m, p, seg=14)
    frustum("b2", r, r, h * 0.2, m, p, loc=(0, 0, h * 0.4), caps=(False, False), seg=14)
    for z in (0.12, h - 0.18):
        frustum("band", r * 1.04, r * 1.04, 0.05, toon("leather_d", rim=0), p, loc=(0, 0, z), caps=(False, False), seg=14)
    ellipsoid("lid", r * 0.9, WDT(), p, loc=(0, 0, h), scale=(1, 1, 0.12), seg=14, rings=6)
    return p


def crate(parent, loc, s=0.42, rot=0.0, col="#a06a3e"):
    p = pivot("crate", loc, parent, rot=(0, 0, rot))
    box("c", (s, s, s), WD(col, "#85502c", scale=4, bump=0.7), p, loc=(0, 0, s / 2), bevel=0.02)
    for sx in (-1, 1):
        box("cs", (0.05, s + 0.01, s + 0.01), WDT(), p, loc=(sx * s * 0.36, 0, s / 2))
    return p


def yarn_ball(parent, loc, r, color, color2=None, needles=False, rot=(0, 0, 0)):
    """Ball of wool: wave-band 'wound thread' texture on a sphere, trailing end."""
    p = pivot("yarn", loc, parent, rot=rot)
    m = tex_toon("weave", color, color2 or color, scale=1.0 / max(r, 0.05) * 9, plane="xz", bump=1.0, rim=0.35, ao=0.4)
    ellipsoid("ball", r, m, p, loc=(0, 0, r), seg=18, rings=12)
    # wound loops
    for i, (rx, rz) in enumerate([(35, 20), (-30, 70), (10, 120)]):
        frustum("loop", r * 1.01, r * 1.01, r * 0.07, toon(color2 or color, rim=0.3), p, loc=(0, 0, r - r * 0.035),
                rot=(RAD(rx), RAD(rz), 0), caps=(False, False), seg=20)
    tube("tail", [(r * .8, -r * .5, r * .3), (r * 1.4, -r * .9, r * .08), (r * 2.0, -r * 0.7, 0.012)], max(0.012, r * 0.05),
         toon(color, rim=0.2), p)
    if needles:
        for s in (-1, 1):
            link_cyl("needle", (s * r * 0.9, -r * 0.2, r * 1.8), (-s * r * 0.5, -r * 0.1, r * 0.3), r * 0.05,
                     toon("#d9c9a8", rim=0.5), p, seg=5)
            ellipsoid("nk", r * 0.1, toon("gold", rim=0.5), p, loc=(s * r * 0.9, -r * 0.2, r * 1.8), seg=6, rings=4)
    return p


def jar(parent, loc, r=0.11, h=0.24, content="#d68f3a", lid="leather_d", glass_a=0.0, gl=False):
    p = pivot("jar", loc, parent)
    frustum("j", r, r * 0.95, h, glow(content, 1.8) if gl else tex_toon("plain", content, content, scale=6, bump=0, wear=0, rim=0.5, ao=0), p, seg=12)
    frustum("jglass", r * 1.04, r * 1.0, h, glow("#cfe8e0", 1.0, alpha=0.30), p, seg=12, caps=(False, False))
    frustum("jlid", r * 0.98, r * 0.98, h * 0.18, toon(lid, rim=0), p, loc=(0, 0, h), seg=12)
    return p


def plant_pot(parent, loc, r=0.25, h=0.35, leaf="leaf1", kind="fern", pot="#b4553a", seed=3):
    rnd = random.Random(seed)
    p = pivot("pot", loc, parent)
    frustum("pot", r * 0.75, r, h, tex_toon("plain", pot, "#8e3f2c", scale=3, bump=0, wear=0.3), p, seg=14)
    frustum("rim", r * 1.05, r * 1.05, h * 0.15, toon(pot, rim=0.3), p, loc=(0, 0, h * 0.9), seg=14)
    frustum("soil", r * 0.95, r * 0.95, 0.02, toon("#3a2a20", rim=0), p, loc=(0, 0, h), seg=12)
    lm = [toon(leaf, rim=0.3), toon("leaf2", rim=0.3), toon("leaf3", rim=0.3)]
    for i in range(9):
        a = i * 0.7 + rnd.uniform(0, 0.4)
        L = rnd.uniform(0.35, 0.65) if kind == "fern" else rnd.uniform(0.25, 0.4)
        tip = (math.cos(a) * L * 0.8, math.sin(a) * L * 0.6, h + L * rnd.uniform(0.7, 1.1))
        if kind == "fern":
            link_cyl("stem", (0, 0, h), tip, 0.012, lm[2], p, seg=4)
            ellipsoid("leaf", 0.09, lm[i % 3], p, loc=tip, scale=(1.0, 0.45, 1.8), rot=(0, 0, a), seg=8, rings=6)
            mid = tuple(c * 0.55 + o * 0.45 for c, o in zip(tip, (0, 0, h)))
            ellipsoid("leaf", 0.07, lm[(i + 1) % 3], p, loc=mid, scale=(1.0, 0.4, 1.5), rot=(0, 0, a), seg=8, rings=6)
        else:   # flowery
            link_cyl("stem", (0, 0, h), tip, 0.012, lm[2], p, seg=4)
            ellipsoid("fl", 0.07, toon(rnd.choice(["red", "gold", "white", "#c79ae8"]), rim=0.3), p, loc=tip, seg=8, rings=6)
    return p


def book(parent, loc, size=(0.3, 0.2, 0.06), color="wine", rot=0.0):
    p = pivot("book", loc, parent, rot=(0, 0, rot))
    box("cov", size, toon(color, rim=0.3), p, base=True)
    box("pages", (size[0] * 0.96, size[1] * 0.98, size[2] * 0.7), toon("cream", rim=0), p, loc=(0.012, 0, size[2] * 0.15), base=True)
    box("spine", (0.012, size[1], size[2]), toon("gold", rim=0.5), p, loc=(-size[0] / 2 + 0.01, 0, 0), base=True)
    return p


def cup(parent, loc, r=0.09, h=0.1, color="#f6f0e6", tea="#8a4a20", full=True, steam=False):
    p = pivot("cup", loc, parent)
    frustum("c", r, r * 0.7, h, toon(color, rim=0.4), p, seg=14)
    if full:
        frustum("t", r * 0.9, r * 0.9, 0.01, toon(tea, rim=0.2), p, loc=(0, 0, h * 0.88), seg=12)
    ellipsoid("handle", r * 0.45, toon(color, rim=0.4), p, loc=(r * 1.0, 0, h * 0.55), scale=(0.5, 0.25, 1), seg=8, rings=6)
    frustum("saucer", r * 1.5, r * 1.3, 0.02, toon(color, rim=0.4), p, loc=(0, 0, -0.01), seg=14)
    return p


def rug_round(parent, loc, r, c1, c2, c3):
    p = pivot("rug", loc, parent)
    for i, (rr, c) in enumerate([(r, c1), (r * 0.82, c2), (r * 0.62, c3), (r * 0.42, c2), (r * 0.24, c1)]):
        frustum("ring", rr, rr, 0.012 + i * 0.004, FAB("knit", c, c, scale=22 - i * 2, plane="xy", bump=0.9), p, seg=32)
    return p


def spool(parent, loc, r=0.1, h=0.2, thread="#35d3b0", glowing=False, rot=(0, 0, 0)):
    p = pivot("spool", loc, parent, rot=rot)
    wood = toon("wood", rim=0.3)
    frustum("fl1", r * 1.15, r * 1.15, h * 0.12, wood, p, seg=10)
    frustum("fl2", r * 1.15, r * 1.15, h * 0.12, wood, p, loc=(0, 0, h * 0.88), seg=10)
    frustum("core", r * 0.55, r * 0.55, h, wood, p, seg=8)
    th = glow(thread, 2.6) if glowing else tex_toon("weave", thread, thread, scale=40, plane="xz", bump=0.7, rim=0.4, ao=0)
    frustum("thread", r * 0.98, r * 0.98, h * 0.76, th, p, loc=(0, 0, h * 0.12), seg=12)
    return p


# ----------------------------------------------------------- truth-only details
def snapped_thread(parent, p0, length=0.9, sway=0.15, seed=1, cut=True):
    """Teal thread hanging from p0, dangling to the ground, frayed (or cleanly cut) at the top end."""
    rnd = random.Random(seed)
    x, y, z = p0
    pts = [(x, y, z)]
    for i in range(1, 7):
        t = i / 6
        pts.append((x + sway * math.sin(t * 3 + seed), y - 0.05 * t, z - length * t))
    tube("thread", pts, 0.014, glow("#35d3b0", 3.0), parent)
    if not cut:
        for k in range(3):
            tube("fray", [(x, y, z), (x + rnd.uniform(-.1, .1), y, z - 0.1 - k * .03)], 0.008, glow("#35d3b0", 2.0), parent)
    return pts[-1]


def cobweb(parent, loc, size=0.5, rot=(0, 0, 0)):
    """Corner cobweb made of pale thread (fan of spokes + arcs), in the XZ plane."""
    p = pivot("web", loc, parent, rot=rot)
    m = toon("#c9d2e0", rim=0)
    for k in range(5):
        a = k * RAD(90) / 4
        link_cyl("sp", (0, 0, 0), (math.cos(a) * size, 0, -math.sin(a) * size), 0.005, m, p, seg=3)
    for r in (0.35, 0.65, 1.0):
        pts = [(math.cos(k * RAD(90) / 4) * size * r, 0, -math.sin(k * RAD(90) / 4) * size * r) for k in range(5)]
        for a, b in zip(pts, pts[1:]):
            link_cyl("arc", a, b, 0.004, m, p, seg=3)
    return p


def dead_plant(parent, loc, h=0.5, seed=1, n=7):
    rnd = random.Random(seed)
    p = pivot("dead", loc, parent)
    for i in range(n):
        a = rnd.uniform(0, 6.28)
        tip = (math.cos(a) * h * 0.5, math.sin(a) * h * 0.35, h * rnd.uniform(0.6, 1.0))
        link_cyl("stalk", (0, 0, 0), tip, 0.012, toon("#6a5a44", rim=0), p, seg=4)
        link_cyl("droop", tip, (tip[0] * 1.5, tip[1] * 1.5, tip[2] - 0.25), 0.01, toon("#5a4c3c", rim=0), p, seg=4)
    return p
