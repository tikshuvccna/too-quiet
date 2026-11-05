"""Shared builders for the world-2 interiors (re-uses env_blocks / interiors_objs helpers)."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from interiors_objs import *  # noqa  (table, round_table, paper_sheet, scratches, cut_thread, weaver_knot, frame_picture, ...)
import env_lib as EL

TEAL = "#35d3b0"
BLUE = "#4fc3ff"
GREY = "#8c96a8"


def T():
    return EL.TRUTH


def tthread(R, pts, r=0.014, s=3.0, col=TEAL):
    """Glowing thread tube."""
    if col in (TEAL, BLUE, "#ffd86a", "#ffffff"):
        return tube("th", pts, r, glow(col, s), R)
    return tube("th", pts, r, toon(col, rim=0), R)


def sag(p0, p1, drop=0.2, n=8):
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append((p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t,
                    p0[2] + (p1[2] - p0[2]) * t - drop * 4 * t * (1 - t)))
    return pts


def halo(R, loc, r=0.4, a=0.35, col=TEAL, s=1.2, sc=(1, 1, 1)):
    return ellipsoid("halo", r, glow(col, s, alpha=a, soft=True), R, loc=loc, scale=sc, seg=10, rings=6)


def glass_col():
    return "#cfe8e0"


def rope(R, pts, r=0.03, col="#c9b48a"):
    return tube("rope", pts, r, tex_toon("weave", col, "#8a7450", scale=40, plane="xz", bump=1.0, rim=0.3, ao=0), R)


def sack(R, loc, r=0.3, col="#c9b48a", h=1.15, tiec="#8a5a30"):
    p = pivot("sack", loc, R)
    ellipsoid("s", r, FAB("weave", col, "#a89870", scale=18, bump=1.0), p, loc=(0, 0, r * h), scale=(1, 0.9, h), seg=14, rings=10)
    ellipsoid("n", r * 0.45, toon(col, rim=0.3), p, loc=(0, 0, r * h * 2 - 0.02), scale=(1, 1, 0.8), seg=8, rings=6)
    frustum("tie", r * 0.4, r * 0.4, 0.04, toon(tiec, rim=0), p, loc=(0, 0, r * h * 1.9), seg=8)
    return p


def bench(R, loc, w=1.8, d=0.4, h=0.5, col="#8a5a30", rot=0.0):
    p = pivot("bench", loc, R, rot=(0, 0, rot))
    box("seat", (w, d, 0.07), WD(col, "#6a4220", scale=3, plane="xy"), p, loc=(0, 0, h - 0.035))
    for sx in (-1, 1):
        box("leg", (0.07, d * 0.85, h - 0.07), WDT(), p, loc=(sx * (w / 2 - 0.15), 0, 0), base=True)
    box("brace", (w - 0.3, 0.05, 0.06), WDT(), p, loc=(0, 0, 0.18))
    return p


def candle(R, loc, h=0.16, lit=True, col="#f3e4c4"):
    p = pivot("candle", loc, R)
    frustum("c", 0.03, 0.03, h, toon(col, rim=0.3), p, seg=8)
    if lit:
        ellipsoid("f", 0.028, glow("#ffd070", 6), p, loc=(0, 0, h + 0.035), scale=(1, 1, 1.6), seg=6, rings=5)
        ellipsoid("h", 0.18, glow("#ffd070", 1.2, alpha=0.35, soft=True), p, loc=(0, 0, h + 0.05), seg=8, rings=6)
    return p


def chest(R, loc, w=1.0, d=0.6, h=0.55, col="#7a4a2a", band="#3a2a22", rot=0.0, open_=False):
    p = pivot("chest", loc, R, rot=(0, 0, rot))
    wm = WD(col, "#5a3520", scale=3, bump=0.7)
    box("b", (w, d, h * 0.62), wm, p, base=True, bevel=0.02)
    lid = frustum("lid", d / 2, d / 2, w, wm, p, loc=(-w / 2, 0, h * 0.62), rot=(0, RAD(90), 0), seg=12, scale=(1, 1, 1))
    lid.scale = (1, 1, 1)
    for x in (-w * 0.35, w * 0.35):
        box("band", (0.07, d + 0.02, h * 0.62), toon(band, rim=0.3), p, loc=(x, 0, 0), base=True)
    box("lock", (0.12, 0.04, 0.14), toon("gold", rim=0.6), p, loc=(0, -d / 2 - 0.01, h * 0.58))
    return p


def cloth_roll(R, loc, L=1.0, r=0.13, col="#c44b3f", col2="#f3e4c4", kind="weave", rot=(0, 0, 0), axis="x"):
    """Bolt of cloth lying with axis along x (axis='x') or standing up (axis='z')."""
    p = pivot("roll", loc, R, rot=rot)
    m = FAB(kind, col, col2, scale=18, plane="xz" if axis == "x" else "xy", bump=0.9)
    if axis == "x":
        frustum("r", r, r, L, m, p, loc=(-L / 2, 0, 0), rot=(0, RAD(90), 0), seg=14)
        frustum("core", r * 0.5, r * 0.5, L + 0.1, toon("#d9c9a8", rim=0.3), p, loc=(-L / 2 - 0.05, 0, 0), rot=(0, RAD(90), 0), seg=8)
    else:
        frustum("r", r, r, L, m, p, seg=14)
    return p


def gear(R, loc, r=0.5, n=12, th=0.1, col="#b4854a", hub=True, rot=(RAD(90), 0, 0), spokes=True, dark=False):
    """Gear whose axis points at the camera (rot x=90). R-local loc."""
    p = pivot("gear", loc, R, rot=rot)
    m = toon(col, rim=0.5)
    ring_in = r * 0.72
    frustum("rim", r * 0.88, r * 0.88, th, m, p, seg=max(16, n * 2), caps=(True, True))
    for i in range(n):
        a = i * 2 * math.pi / n
        box("tooth", (r * 0.24, r * 0.22, th), m, p, loc=(math.cos(a) * r * 0.94, math.sin(a) * r * 0.94, th / 2), rot=(0, 0, a))
    if spokes:
        frustum("hole", ring_in, ring_in, th + 0.01, toon("#1c1620", rim=0), p, loc=(0, 0, -0.005), seg=max(16, n * 2))
        frustum("rim2", ring_in, ring_in, th, m, p, seg=max(16, n * 2), caps=(False, False))
        for k in range(5):
            a = k * 2 * math.pi / 5
            box("sp", (ring_in * 0.9, r * 0.12, th * 0.9), m, p, loc=(math.cos(a) * ring_in * 0.45, math.sin(a) * ring_in * 0.45, th / 2), rot=(0, 0, a))
    if hub:
        frustum("hub", r * 0.22, r * 0.22, th * 1.6, toon("gold" if not dark else col, rim=0.6), p, seg=10)
    return p


def banner(R, loc, w=0.9, h=1.8, col="#a94a62", col2="#e8b04a", torn=False, notch=True, emblem=True, rod=True):
    """Hanging banner: cloth panel with a swallow-tail, a rod and a woven emblem (no text)."""
    p = pivot("banner", loc, R)
    m = FAB("weave", col, col, scale=14, bump=0.8, plane="xz")
    n = 8
    v, f = [], []
    for i in range(n + 1):
        t = i / n
        x = -w / 2 + w * t
        bot = 0.0
        if notch:
            bot = (1 - abs(2 * t - 1)) * 0.0 + (0.28 * h * (1 - abs(2 * t - 1)) if True else 0)
        if torn and i % 3 == 1:
            bot += 0.18
        v += [(x, 0, h * 0.0 + bot * 0), (x, 0, h)]
    v = []
    for i in range(n + 1):
        t = i / n
        x = -w / 2 + w * t
        zlow = 0.22 * h * (1 - abs(2 * t - 1)) if notch else 0.0
        zlow = 0.22 * h - zlow if notch else 0.0
        if torn and i % 3 == 1:
            zlow += 0.14
        v += [(x, 0, zlow), (x, 0, h)]
    f = [(2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1) for i in range(n)]
    mesh_obj("cloth", v, f, m, p, smooth=False)
    if rod:
        link_cyl("rod", (-w / 2 - 0.1, -0.01, h), (w / 2 + 0.1, -0.01, h), 0.03, toon("wood_d", rim=0.3), p, seg=6)
        for s in (-1, 1):
            ellipsoid("fin", 0.05, toon("gold", rim=0.5), p, loc=(s * (w / 2 + 0.12), -0.01, h), seg=6, rings=4)
    if emblem:
        frustum("em", w * 0.2, w * 0.2, 0.02, FAB("weave", col2, col2, scale=16, plane="xz"), p, loc=(0, -0.012, h * 0.56), rot=(RAD(90), 0, 0), seg=16)
        ellipsoid("ne", w * 0.09, glow(TEAL if T() else "#fff3c8", 1.0 if not T() else 2.4), p, loc=(0, -0.04, h * 0.56), scale=(1, 0.3, 1), seg=8, rings=6)
    return p


def mushroom(R, loc, r=0.2, h=0.3, cap="#e8884a", stem="#f3e4c4", glowing=False, spots=True):
    p = pivot("mush", loc, R)
    frustum("st", r * 0.28, r * 0.22, h, toon(stem, rim=0.3), p, seg=8)
    cm = glow(cap, 1.8) if glowing else toon(cap, rim=0.35)
    ellipsoid("cap", r, cm, p, loc=(0, 0, h), scale=(1, 1, 0.62), seg=14, rings=8)
    if spots:
        for k in range(4):
            a = k * 1.7
            ellipsoid("sp", r * 0.12, toon("#fff7e0", rim=0), p, loc=(math.cos(a) * r * 0.55, math.sin(a) * r * 0.5, h + r * 0.5), seg=6, rings=4)
    if glowing:
        halo(p, (0, 0, h), r * 1.4, 0.3, cap, 1.0, (1, 1, 0.8))
    return p


def sign_board(R, loc, w=1.0, h=0.6, col="#c98a52", border="#6a4220", lines=3, ink="#3a2a22", rot=(0, 0, 0)):
    """Plank sign; text lines are dark bars (no readable text)."""
    p = pivot("sign", loc, R, rot=rot)
    box("fr", (w, 0.07, h), WD(border, border, scale=3), p, loc=(0, 0, 0))
    box("bd", (w - 0.12, 0.05, h - 0.12), WD(col, col, scale=3, along="u"), p, loc=(0, -0.025, 0))
    for k in range(lines):
        ww = (w - 0.34) * (0.9 - 0.18 * (k % 2) - (0.25 if k == lines - 1 and lines > 1 else 0))
        box("ln", (ww, 0.02, 0.035), toon(ink, rim=0), p, loc=(-(w - 0.34) / 2 + ww / 2 + 0.02, -0.06, h / 2 - 0.18 - k * (h - 0.36) / max(1, lines - 1 if lines > 1 else 1)))
    return p


def key_obj(R, loc, c="gold", size=0.22, rot=(0, 0, 0)):
    p = pivot("key", loc, R, rot=rot)
    m = toon(c, rim=0.6)
    frustum("bow", size * 0.28, size * 0.28, 0.03, m, p, rot=(RAD(90), 0, 0), seg=12)
    frustum("hole", size * 0.14, size * 0.14, 0.032, toon("#1c1620", rim=0), p, loc=(0, 0.001, 0), rot=(RAD(90), 0, 0), seg=8)
    box("sh", (0.035, 0.03, size), m, p, loc=(0, 0, -size * 0.5))
    box("t1", (0.09, 0.03, 0.04), m, p, loc=(0.05, 0, -size * 0.85))
    box("t2", (0.07, 0.03, 0.04), m, p, loc=(0.04, 0, -size * 0.6))
    return p


def pot_clay(R, loc, r=0.22, h=0.3, col="#c0693f"):
    p = pivot("pot", loc, R)
    frustum("p", r * 0.7, r, h, tex_toon("plain", col, "#9a4a2c", scale=3, bump=0, wear=0.3), p, seg=14)
    frustum("rim", r * 1.05, r * 1.05, h * 0.16, toon(col, rim=0.3), p, loc=(0, 0, h * 0.86), seg=14)
    return p


def beam_x(R, y, z, w=14, t=0.22, col="#5a3a24"):
    box("beam", (w, t, t), WDT(col, col), R, loc=(0, y, z))


def post_z(R, x, y, h=5.0, t=0.28, col="#5a3a24"):
    box("post", (t, t, h), WD(col, col, scale=3, along="v"), R, loc=(x, y, 0), base=True)


def ceil_threads(R, xs, y, z_top=5.0, z_bot=2.6, col=GREY, wob=0.1):
    """Truth: thin pale threads hanging from the ceiling line."""
    for i, x in enumerate(xs):
        tube("ct", [(x, y, z_top), (x + wob * math.sin(i), y, (z_top + z_bot) / 2), (x, y, z_bot)], 0.008, toon(col, rim=0), R)


def stool_round(R, loc, r=0.28, h=0.5, col="#8a5a30"):
    p = pivot("stool", loc, R)
    frustum("seat", r, r, 0.07, WD(col, col, scale=3, plane="xy"), p, loc=(0, 0, h), seg=14)
    for k in range(3):
        a = k * 2.094 + 0.5
        link_cyl("leg", (math.cos(a) * r * 0.5, math.sin(a) * r * 0.5, h), (math.cos(a) * r * 1.0, math.sin(a) * r * 1.0, 0), 0.035, WDT(), p, seg=5)
    return p


def lectern(R, loc, h=1.15, w=0.6, col="#7a4a2a", rot=0.0, tilt=18):
    """Standing reading desk; returns the pivot of the sloped top (local x/z)."""
    p = pivot("lect", loc, R, rot=(0, 0, rot))
    wm = WD(col, "#5a3520", scale=3)
    frustum("foot", w * 0.45, w * 0.5, 0.07, wm, p, seg=10)
    frustum("stem", 0.06, 0.07, h, WDT(), p, seg=8)
    top = pivot("top", (0, 0, h), p, rot=(RAD(-tilt), 0, 0))
    box("tp", (w, 0.45, 0.05), wm, top, loc=(0, 0, 0.0))
    box("lip", (w, 0.04, 0.07), wm, top, loc=(0, -0.2, 0.05))
    return top


def open_book(R, loc, w=0.5, d=0.34, cover="wine", rot=(0, 0, 0), lines=6, page="#f3e8cc", ink="#2a3a8a"):
    p = pivot("obook", loc, R, rot=rot)
    box("cv", (w + 0.06, d + 0.04, 0.03), toon(cover, rim=0.3), p, loc=(0, 0, 0.015))
    for s in (-1, 1):
        pg = tex_toon("paper", page, ink, scale=6, plane="xy", bump=0.15, wear=0)
        box("pg", (w / 2 - 0.01, d, 0.03), pg, p, loc=(s * (w / 4 + 0.005), 0, 0.045), rot=(0, s * RAD(-4), 0))
    return p


def hook_peg(R, loc, c="wood_d"):
    box("peg", (0.06, 0.12, 0.06), toon(c, rim=0), R, loc=loc)


def crack_fx(R, loc, L=0.5, rot=(0, 0, 0)):
    p = pivot("crk", loc, R, rot=rot)
    pts = [(0, 0, 0), (L * 0.2, 0, -L * 0.25), (-L * 0.05, 0, -L * 0.5), (L * 0.15, 0, -L * 0.8), (0, 0, -L)]
    for a, b in zip(pts, pts[1:]):
        link_cyl("c", a, b, 0.006, toon("#14121c", rim=0), p, seg=3)
    return p


def lantern_floor(R, loc, h=1.6, col="amber", lit=True):
    p = pivot("lf", loc, R)
    frustum("base", 0.18, 0.15, 0.06, toon("leather_d", rim=0.3), p, seg=8)
    frustum("pole", 0.025, 0.025, h, toon("leather_d", rim=0.3), p, seg=6)
    link_cyl("arm", (0, 0, h), (0.22, 0, h + 0.05), 0.02, toon("leather_d", rim=0.3), p, seg=5)
    lantern2(p, (0.22, 0, h + 0.05), col, 4 if lit else 0.5, 0.2 if lit else 0.1, hang=False)
    return p


def cleanup_dust(R, loc, r=0.5):
    """Truth: dusty patch on the floor."""
    ellipsoid("dust", r, toon("#4a4e5c", rim=0), R, loc=loc, scale=(1.4, 1, 0.03), seg=10, rings=4)
