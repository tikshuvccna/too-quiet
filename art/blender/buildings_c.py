"""World-2 buildings, part 1: inn, bell_tower, tailor, school, fisher, workshop, library, observatory.
Entry: blender -b --python buildings_c.py -- <rawdir> [truth] [name ...]   (also loads buildings_d: the other 8)
Cell + anchor are auto-fitted to the geometry (w2lib.autofit). Anchor = projected footprint centre.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w2lib import *  # noqa
import env_lib as EL


def tilesm(c1, c2, scale=3.4, **kw):
    kw.setdefault("wear", 0.4)
    kw.setdefault("moss", 0.2)
    return tex_toon("tiles", c1, c2, scale=scale, plane="xy", bump=1.0, **kw)


def cog(parent, loc, r, n, mat, thick=0.14, hubmat=None):
    p = pivot("cog", loc, parent)
    frustum("disc", r, r, thick, mat, p, loc=(0, thick / 2, 0), rot=(RAD(90), 0, 0), seg=28)
    for i in range(n):
        a = 2 * math.pi * i / n
        box("tooth", (r * 0.26, thick, r * 0.3), mat, p, loc=(math.cos(a) * r * 1.0, 0, math.sin(a) * r * 1.0), rot=(0, -a, 0))
    dm = hubmat or toon("#2e2430", rim=0.3)
    for k in range(5):
        a = 2 * math.pi * k / 5 + 0.3
        frustum("hole", r * 0.14, r * 0.14, thick + 0.02, dm, p, loc=(math.cos(a) * r * 0.55, thick / 2 + 0.01, math.sin(a) * r * 0.55), rot=(RAD(90), 0, 0), seg=10)
    frustum("hub", r * 0.26, r * 0.26, thick + 0.06, dm, p, loc=(0, thick / 2 + 0.03, 0), rot=(RAD(90), 0, 0), seg=12)
    return p


# =============================================================== inn: wide, warm, lantern sign
def inn():
    R = pivot("inn")
    w, d = 7.0, 3.4
    plaster = PL("#f0c692", "#e0a874", wear=0.5, moss=0.15)
    tm = WDT("#5a3420", "#4a2a1a")
    box("found", (w + 0.2, d + 0.2, 0.36), ST("#b5a698", "#8c8088", scale=2.2, moss=0.4), R, base=True)
    lh = 2.3
    box("low", (w, d, lh - 0.3), plaster, R, loc=(0, 0, 0.3), base=True)
    ud = d + 0.45
    box("up", (w + 0.45, ud, 1.9), plaster, R, loc=(0, -0.12, lh), base=True)
    yf = -d / 2 - 0.02
    yu = -ud / 2 - 0.12 - 0.02
    for x in np_range(-w / 2 + 0.1, w / 2 + 0.01, 1.4):
        box("lp", (0.16, 0.08, lh - 0.35), tm, R, loc=(x, yf, 0.34), base=True)
    for x in np_range(-w / 2 - 0.1, w / 2 + 0.3, 1.17):
        box("up_", (0.14, 0.08, 1.9), tm, R, loc=(x, yu, lh), base=True)
    box("beam1", (w + 0.5, 0.14, 0.18), tm, R, loc=(0, yu, lh + 0.02))
    box("beam2", (w + 0.5, 0.14, 0.14), tm, R, loc=(0, yu, lh + 1.85))
    box("beam0", (w, 0.1, 0.12), tm, R, loc=(0, yf, 0.5))
    for x in (-2.2, 2.2):   # braces
        link_cyl("brc", (x - 0.5, yu, lh + 0.1), (x + 0.5, yu, lh + 1.8), 0.05, tm, R, seg=5)
    rz = lh + 1.9 - 0.05
    rh = 1.75
    roof = tilesm("#b04b30", "#8f3626", scale=3.6)
    sloped_roof("roof", w + 0.45, ud, rh, 0.5, roof, R, loc=(0, -0.12, rz), ends=True)
    ridge_cap(R, w + 1.5, rz + rh, toon("#6e2a1c", rim=0.4), loc_y=-0.12, r=0.12)
    eave_trim(R, w + 0.45, ud, 0.5, rz + 0.02, toon("#6e2a1c", rim=0.3), r=0.09)
    sm = []
    for cx in (-2.5, 2.4):
        zc = rz + rh * (1 - 0.7 / (ud / 2 + 0.5))
        box("chim", (0.7, 0.7, rh + 0.9), BR("#a0583e", "#8a4632", scale=3, soot=0.8), R, loc=(cx, 0.6, zc - 0.5), base=True)
        box("chcap", (0.88, 0.88, 0.14), ST("#8c848a", "#6c6470", scale=3), R, loc=(cx, 0.6, zc + rh + 0.4), base=True)
        sm.append((cx, 0.6, zc + rh + 0.65))
    for k, x in enumerate((-1.7, 1.7)):   # dormers
        zz = roof_z_at(-0.95, rz, rh, ud, 0.5) - rz
        dp = pivot("dormer", (x, -1.1, rz + rh * (1 - 1.1 / (ud / 2 + 0.5)) - 0.15), R)
        box("db", (1.1, 0.7, 0.9), plaster, dp, base=True)
        sloped_roof("dr", 1.1, 0.7, 0.55, 0.12, roof, dp, loc=(0, 0, 0.9), ends=True, ridge_x=False)
        box("dfr", (0.74, 0.05, 0.56), toon("#f3e4c4", rim=0.1), dp, loc=(0, -0.37, 0.5))
        box("dpn", (0.62, 0.05, 0.46), glow("#ffc66a", 3.6), dp, loc=(0, -0.4, 0.5))
    door(R, (0, -d / 2, 0.3), w=1.15, h=1.85, color="#6a3a2a", frame="#f3e4c4", window_=False, step=False)
    # wide porch with hanging lanterns
    box("porch", (2.6, 0.9, 0.12), ST("#c2bdb4", "#a7a49e", scale=3, bump=0.6), R, loc=(0, -d / 2 - 0.5, 0.06))
    for x in (-1.2, 1.2):
        frustum("pil", 0.09, 0.09, 1.9, WD("#6a4326", "#5a3720", scale=3, along="v"), R, loc=(x, -d / 2 - 0.9, 0.12), seg=8)
    box("pbeam", (2.7, 0.16, 0.14), tm, R, loc=(0, -d / 2 - 0.9, 2.0))
    sloped_roof("proof", 2.7, 0.9, 0.35, 0.1, roof, R, loc=(0, -d / 2 - 0.5, 2.0), ends=True)
    for x in (-0.75, 0.75):
        lantern2(R, (x, -d / 2 - 0.9, 1.9), hang=False) if False else None
    xs = [(-2.0, 1.2), (-3.0, 1.2), (2.0, 1.2), (3.0, 1.2)]
    for (x, z) in xs:
        window(R, (x, -d / 2, z + 0.1), w=0.62, h=0.75, frame="#5a3420", shutter="#2f7d6f", flowers=(x < 0), curtain="#c44b3f")
    for x in (-2.55, -0.95, 0.95, 2.55):
        window(R, (x, yu, lh + 1.0), w=0.6, h=0.7, frame="#f3e4c4", shutter=None, flowers=False, curtain="#e8b04a", light="#ffd89a")
    # lantern sign on a post
    px, py = 4.25, -2.35
    frustum("spost", 0.08, 0.06, 3.5, WD("#4a2e1a", "#3a2214", scale=3, along="v"), R, loc=(px, py, 0), seg=8)
    link_cyl("arm", (px, py, 3.2), (px - 0.8, py, 3.2), 0.04, toon("#2e2a30", rim=0.3), R, seg=6)
    link_cyl("brace", (px, py, 2.6), (px - 0.5, py, 3.1), 0.03, toon("#2e2a30", rim=0.3), R, seg=5)
    tube("scroll", [(px - 0.5, py, 3.2), (px - 0.5, py, 3.0), (px - 0.4, py, 2.9), (px - 0.3, py, 3.0)], 0.02, toon("#2e2a30", rim=0.3), R)
    link_cyl("ch", (px - 0.75, py, 3.2), (px - 0.75, py, 2.62), 0.012, toon("#2e2a30", rim=0), R, seg=4)
    big_lantern(R, (px - 0.75, py, 1.6), 1.0, glow_s=6)
    # benches, barrels, notice board
    for (x, y, rr) in ((-3.5, -2.4, 0), (-3.05, -2.6, 25)):
        barrel(R, (x, y, 0), 0.3, 0.6, col="#a06a3e")
    bm = WD("#a06a3e", "#85502c", scale=3, bump=0.5)
    box("bench", (1.5, 0.4, 0.1), bm, R, loc=(-1.9, -2.4, 0.5))
    for x in (-2.5, -1.3):
        box("bl", (0.1, 0.35, 0.5), bm, R, loc=(x, -2.4, 0.25))
    for x in (-2.3, -1.6):
        cup(R, (x, -2.4, 0.55), 0.07, 0.09, color="#c9a060", tea="#e8c060")
    nb = pivot("board", (1.95, -2.55, 0), R)
    for x in (-0.55, 0.55):
        box("np", (0.1, 0.1, 1.7), WDT(), nb, loc=(x, 0, 0), base=True)
    box("nbd", (1.3, 0.08, 0.9), WD("#8a6238", "#6a4a2a", scale=3, bump=0.5), nb, loc=(0, -0.06, 1.2))
    box("nrf", (1.5, 0.2, 0.08), WDT(), nb, loc=(0, -0.06, 1.72))
    for i, (x, z, c) in enumerate([(-0.4, 1.35, "#f3e8cc"), (0.1, 1.25, "#efe0b8"), (0.45, 1.4, "#f3e8cc"), (-0.1, 1.05, "#e8d6b0")]):
        box("note", (0.3, 0.02, 0.36), tex_toon("paper", c, "#2a3a8a", scale=4, plane="xz", bump=0.1), nb, loc=(x, -0.11, z), rot=(0, RAD(6 * (i - 1.5)), 0))
    plant_pot(R, (-0.9, -2.0, 0), 0.2, 0.3, kind="flower", seed=3)
    plant_pot(R, (1.0, -2.0, 0), 0.2, 0.3, kind="fern", seed=5, pot="#d68f3a")
    bush(R, (-3.9, -1.4, 0), r=0.4, seed=2)
    bush(R, (3.9, -1.2, 0), r=0.35, col="leaf2", seed=6, fcols=("#ffd86a", "white"))
    truth_extras(R, cob=[(-2.6, yf - 0.2, 2.1, 0.5)], threads=[(-1.0, yf - 0.5, 2.3), (1.8, yf - 0.5, 2.3)],
                 dead=[(-0.9, -2.0, 0.3, 0.55)], holes=[(-1.0, -1.1, dict(wh=rz, rh=rh, d=ud, ov=0.5, s=0.65, rz0=rz))])
    return dict(smoke=sm)


# =============================================================== bell tower: open belfry with a bell
def bell_tower():
    R = pivot("bt")
    s = 2.8
    stone = ST("#d6c3a0", "#b9a47e", scale=2.3, wear=0.7, moss=0.3)
    cream = PL("#efe3c8", "#dccdaa", wear=0.3)
    box("found", (s + 0.5, s + 0.5, 0.4), ST("#a89c90", "#85787c", scale=2.4, moss=0.7), R, base=True)
    for k in range(2):
        box("step", (1.8 - k * 0.1, 0.5, 0.14), ST(scale=3, bump=0.6), R, loc=(0, -s / 2 - 0.4 - k * 0.4, 0.07 - k * 0.0))
    box("shaft", (s, s, 4.4), stone, R, loc=(0, 0, 0.4), base=True)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box("quoin", (0.34, 0.34, 4.4), cream, R, loc=(sx * (s / 2 - 0.1), sy * (s / 2 - 0.1), 0.4), base=True)
    for z in (2.5, 4.75):
        box("band", (s + 0.14, s + 0.14, 0.16), cream, R, loc=(0, 0, z))
    door(R, (0, -s / 2, 0.4), w=0.95, h=1.55, color="#7a4a2a", frame="#efe3c8", step=False)
    for z in (2.0, 3.3):
        arch_window(R, (0, -s / 2, z), w=0.32, h=0.7, frame="#efe3c8", glow_s=2.5, bars=False)
    # clock face
    cf = pivot("clock", (0, -s / 2 - 0.02, 3.95), R)
    frustum("cfr", 0.42, 0.42, 0.08, toon("#b88a3a", rim=0.5), cf, rot=(RAD(90), 0, 0), seg=24)
    frustum("cfc", 0.36, 0.36, 0.06, toon("#f6f0e6", rim=0.2), cf, loc=(0, -0.06, 0), rot=(RAD(90), 0, 0), seg=24)
    box("h1", (0.04, 0.03, 0.26), toon("#2a2230", rim=0), cf, loc=(0, -0.13, 0.1))
    box("h2", (0.2, 0.03, 0.04), toon("#2a2230", rim=0), cf, loc=(0.08, -0.13, 0.0))
    # belfry (open)
    z0 = 4.9
    box("slab", (s + 0.35, s + 0.35, 0.2), stone, R, loc=(0, 0, z0 - 0.1))
    box("back", (s - 0.3, 0.1, 3.0), toon("#1a1424", rim=0), R, loc=(0, s / 2 - 0.3, z0), base=True)
    box("backg", (s - 0.9, 0.05, 2.5), glow("#3a3a78", 0.7), R, loc=(0, s / 2 - 0.36, z0 + 0.1), base=True)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box("pil", (0.36, 0.36, 3.1), cream, R, loc=(sx * (s / 2 - 0.05), sy * (s / 2 - 0.05), z0), base=True)
            box("cap", (0.5, 0.5, 0.12), stone, R, loc=(sx * (s / 2 - 0.05), sy * (s / 2 - 0.05), z0 + 3.1), base=True)
    box("lintel", (s + 0.25, 0.34, 0.3), stone, R, loc=(0, -s / 2 + 0.05, z0 + 2.95))
    box("lintelb", (s + 0.25, 0.34, 0.3), stone, R, loc=(0, s / 2 - 0.05, z0 + 2.95))
    for sx in (-1, 1):
        box("lintels", (0.34, s + 0.25, 0.3), stone, R, loc=(sx * (s / 2 - 0.05), 0, z0 + 2.95))
        # bell
    bz = z0 + 2.8
    box("beam", (s - 0.2, 0.2, 0.2), WD("#6a4326", "#5a3720", scale=3, along="v"), R, loc=(0, 0, bz))
    box("yoke", (0.9, 0.22, 0.14), WDT(), R, loc=(0, 0, bz - 0.3))
    link_cyl("hang", (0, 0, bz - 0.3), (0, 0, bz - 0.6), 0.08, WDT(), R, seg=6)
    bm = tex_toon("plain", "#d9a53a", "#b88a2c", scale=5, bump=0.3, rim=0.8, ao=0.2)
    frustum("bell", 0.85, 0.3, 1.55, bm, R, loc=(0, 0, bz - 2.0), seg=20, caps=(False, True))
    frustum("bellip", 0.9, 0.85, 0.12, toon("#e8c060", rim=0.7), R, loc=(0, 0, bz - 2.04), seg=20, caps=(False, False))
    ellipsoid("crown", 0.3, bm, R, loc=(0, 0, bz - 0.5), scale=(1, 1, 0.5), seg=12, rings=8)
    ellipsoid("clap", 0.12, toon("#3a2a22", rim=0.4), R, loc=(0, 0, bz - 2.1), seg=8, rings=6)
    # spire
    zr = z0 + 3.1
    sp = tilesm("#8a3a3a", "#702e2e", scale=2.6, moss=0.1)
    hip_roof("spire", s + 0.9, s + 0.9, 3.4, sp, R, loc=(0, 0, zr), ridge_frac=0.0)
    box("eave", (s + 1.0, s + 1.0, 0.12), toon("#5a2424", rim=0.3), R, loc=(0, 0, zr + 0.02))
    frustum("fin", 0.05, 0.02, 0.9, toon("gold", rim=0.5), R, loc=(0, 0, zr + 3.35), seg=6)
    ellipsoid("finb", 0.12, toon("gold", rim=0.6), R, loc=(0, 0, zr + 3.4), seg=8, rings=6)
    box("vane", (0.5, 0.03, 0.12), toon("gold", rim=0.6), R, loc=(0.2, 0, zr + 4.0))
    mesh_obj("vtip", [(0.45, 0, zr + 3.9), (0.45, 0, zr + 4.12), (0.72, 0, zr + 4.0)], [(0, 2, 1)], toon("gold", rim=0.6), R, smooth=False)
    # rope pulled through a tiny hatch + base garden
    lantern2(R, (0.95, -s / 2, 1.9))
    bush(R, (-1.8, -1.6, 0), r=0.4, seed=4, fcols=("#c79ae8", "white"))
    bush(R, (1.9, -1.2, 0), r=0.35, col="leaf2", seed=7)
    rocks_at(R, [(-2.3, -0.6, 0.4), (2.3, -0.3, 0.3), (-1.9, -2.3, 0.25)], seed=2)
    truth_extras(R, cob=[(-0.7, -s / 2 - 0.1, 2.0, 0.45)], threads=[(0.6, -s / 2 - 0.3, 3.8), (-1.0, -s / 2 - 0.3, 3.4)],
                 dead=[(-1.8, -1.6, 0, 0.6)])
    return dict(smoke=[])


# =============================================================== tailor: striped awning, mannequin in the window, button sign
def tailor():
    R = pivot("tailor")
    w, d, wh = 3.9, 3.0, 3.5
    plaster = PL("#dba1ac", "#c98a98", wear=0.5, moss=0.1)
    tm = WDT("#5a3048", "#4a2438")
    box("found", (w + 0.16, d + 0.16, 0.32), ST("#a8909a", "#86707c", scale=2.4), R, base=True)
    box("walls", (w, d, wh - 0.3), plaster, R, loc=(0, 0, 0.3), base=True)
    for x in (-w / 2 + 0.07, w / 2 - 0.07, 0.35):
        box("post", (0.14, 0.07, wh - 0.3), tm, R, loc=(x, -d / 2 - 0.02, 0.3), base=True)
    box("bm", (w, 0.07, 0.14), tm, R, loc=(0, -d / 2 - 0.02, 2.35))
    box("bt", (w, 0.07, 0.14), tm, R, loc=(0, -d / 2 - 0.02, wh - 0.1))
    rz = wh - 0.05
    roof = tilesm("#4a4f86", "#3a3f78", scale=3.2)
    hip_roof("roof", w + 0.6, d + 0.6, 1.3, roof, R, loc=(0, 0, rz), ridge_frac=0.45)
    box("reave", (w + 0.64, d + 0.64, 0.1), toon("#2e3266", rim=0.3), R, loc=(0, 0, rz + 0.02))
    # shop window with a dress-form silhouette
    sx = -1.05
    box("sfr", (1.7, 0.1, 1.3), toon("#f3e4c4", rim=0.1), R, loc=(sx, -d / 2 - 0.02, 1.15))
    box("spn", (1.5, 0.05, 1.1), glow("#ffc66a", 4.2), R, loc=(sx, -d / 2 - 0.08, 1.15))
    sil = toon("#2a1c34", rim=0.0)
    frustum("mbase", 0.2, 0.15, 0.06, sil, R, loc=(sx, -d / 2 - 0.12, 0.72), seg=10)
    frustum("mpole", 0.03, 0.03, 0.5, sil, R, loc=(sx, -d / 2 - 0.12, 0.76), seg=6)
    ellipsoid("mtorso", 0.28, sil, R, loc=(sx, -d / 2 - 0.12, 1.45), scale=(0.9, 0.35, 1.5), seg=12, rings=8)
    ellipsoid("mskirt", 0.3, sil, R, loc=(sx, -d / 2 - 0.12, 1.0), scale=(1.0, 0.35, 0.9), seg=12, rings=8)
    ellipsoid("mneck", 0.07, sil, R, loc=(sx, -d / 2 - 0.12, 1.85), scale=(1, 1, 1.3), seg=8, rings=6)
    for k, x in enumerate((sx - 0.58, sx + 0.58)):   # fabric bolts in the window sides
        box("bolt", (0.13, 0.06, 0.65), FAB("weave", ["#35b39a", "#e8884a"][k], "#f3e4c4", scale=18), R, loc=(x, -d / 2 - 0.12, 1.22))
    box("mullv", (0.05, 0.07, 1.0), toon("#f3e4c4", rim=0.1), R, loc=(sx, -d / 2 - 0.12, 1.2))
    box("sill", (1.9, 0.25, 0.08), ST("#a8909a", "#86707c", scale=3), R, loc=(sx, -d / 2 - 0.1, 0.52))
    # striped awning
    zb, zf = 2.75, 2.35
    yb, yf = -d / 2, -d / 2 - 0.7
    aw = tex_toon("stripes", "#2f9a8a", "#f3e4c4", scale=3.0, plane="xy", bump=0.5, rim=0.4, ao=0.2)
    ax0, ax1 = -2.0, -0.1
    mesh_obj("awning", [(ax0, yb, zb), (ax1, yb, zb), (ax1, yf, zf), (ax0, yf, zf)], [(0, 1, 2, 3)], aw, R, smooth=False)
    n = 8
    for i in range(n):
        x0 = ax0 + i * (ax1 - ax0) / n
        x1 = x0 + (ax1 - ax0) / n
        mesh_obj("val", [(x0, yf, zf), (x1, yf, zf), ((x0 + x1) / 2, yf - 0.02, zf - 0.22)], [(0, 2, 1)],
                 toon("#2f9a8a" if i % 2 == 0 else "#f3e4c4", rim=0.4), R, smooth=False)
    for x in (ax0 + 0.05, ax1 - 0.05):
        link_cyl("aps", (x, yf, zf - 0.2), (x, yf, 0.0), 0.04, tm, R, seg=5)
    door(R, (1.35, -d / 2, 0.0), w=0.9, h=1.8, color="#2f7d8f", frame="#f3e4c4", window_=True)
    lantern2(R, (0.75, -d / 2, 2.0), color="#ffb4d0")
    for x in (-1.1, 1.1):
        window(R, (x, -d / 2, 3.05), w=0.75, h=0.6, frame="#f3e4c4", shutter="#8a4a72", flowers=True, curtain="#f3e4c4", light="#ffd0e0")
    # giant button + thread sign
    sp = pivot("sign", (1.95, -d / 2 - 0.05, 2.45), R)
    link_cyl("arm", (0, 0, 0.3), (0.0, -0.75, 0.3), 0.03, tm, sp, seg=5)
    link_cyl("ch", (0, -0.75, 0.3), (0, -0.75, 0.05), 0.012, toon("leather_d", rim=0), sp, seg=4)
    bt = pivot("btn", (0, -0.75, -0.35), sp)
    frustum("disc", 0.4, 0.4, 0.09, toon("#e8b04a", rim=0.6), bt, rot=(RAD(90), 0, 0), seg=26)
    frustum("in", 0.28, 0.28, 0.03, toon("#f2c868", rim=0.6), bt, loc=(0, -0.08, 0), rot=(RAD(90), 0, 0), seg=26)
    for (hx, hz) in ((-0.09, 0.09), (0.09, 0.09), (-0.09, -0.09), (0.09, -0.09)):
        frustum("hole", 0.045, 0.045, 0.04, toon("#2a1c34", rim=0), bt, loc=(hx, -0.1, hz), rot=(RAD(90), 0, 0), seg=8)
    tube("cross", [(-0.09, -0.12, 0.09), (0.09, -0.12, -0.09)], 0.012, toon("#c44b3f", rim=0.3), bt)
    tube("cross2", [(0.09, -0.12, 0.09), (-0.09, -0.12, -0.09)], 0.012, toon("#c44b3f", rim=0.3), bt)
    # fabric bolts leaning at the wall + hanging bunting
    for k, (x, c) in enumerate(((2.25, "#c44b3f"), (2.5, "#4f7ad8"), (2.75, "#e8b04a"))):
        frustum("bolt", 0.1, 0.1, 1.1, FAB("weave", c, "#f3e4c4", scale=16), R, loc=(x, -d / 2 - 0.45 + k * 0.05, 0.05), rot=(0, RAD(8 + k * 3), 0), seg=10)
    for i in range(7):
        x = -1.9 + i * 0.5
        mesh_obj("flag", [(x, -d / 2 - 0.05, 2.95 - 0.06 * math.sin(i)), (x + 0.28, -d / 2 - 0.05, 2.95 - 0.06 * math.sin(i + 1)),
                          (x + 0.14, -d / 2 - 0.05, 2.65)], [(0, 2, 1)], toon(["#c44b3f", "#e8b04a", "#2f9a8a", "#f3e4c4"][i % 4], rim=0.3), R, smooth=False)
    plant_pot(R, (0.3, -d / 2 - 0.9, 0), 0.2, 0.3, kind="flower", seed=2, pot="#8a4a72")
    bush(R, (-2.5, -0.9, 0), r=0.32, seed=8, fcols=("#ffb4d0", "white"))
    box("chim", (0.5, 0.5, 1.6), BR("#8a6a78", "#745a66", scale=3, soot=0.7), R, loc=(1.2, 0.6, rz + 0.3), base=True)
    truth_extras(R, cob=[(-1.9, -d / 2 - 0.1, 2.0, 0.5)], threads=[(0.0, -d / 2 - 0.3, wh + 0.2), (1.6, -d / 2 - 0.3, wh)],
                 dead=[(0.3, -d / 2 - 0.9, 0.3, 0.5)])
    return dict(smoke=[(1.2, 0.6, rz + 2.05)])


# =============================================================== school: yellow hall, bell cupola, portico, hopscotch
def school():
    R = pivot("school")
    w, d, wh = 6.2, 3.0, 2.9
    yel = PL("#e6c47c", "#d6ad62", wear=0.55, moss=0.1)
    box("found", (w + 0.16, d + 0.16, 0.3), ST("#a89c90", "#85787c", scale=2.4), R, base=True)
    box("walls", (w, d, wh - 0.3), yel, R, loc=(0, 0, 0.3), base=True)
    box("brick", (w + 0.06, d + 0.06, 0.8), BR("#b6603f", "#9c4e34", scale=2.6, wear=0.6), R, loc=(0, 0, 0.3), base=True)
    box("cband", (w + 0.1, d + 0.1, 0.1), toon("#f3ead0", rim=0.2), R, loc=(0, 0, 1.12))
    box("eaveb", (w + 0.1, d + 0.1, 0.18), toon("#f3ead0", rim=0.2), R, loc=(0, 0, wh - 0.18))
    rz, rh = wh - 0.05, 1.3
    slate = tilesm("#6f86aa", "#5c7396", scale=3.6)
    sloped_roof("roof", w, d, rh, 0.45, slate, R, loc=(0, 0, rz), ends=True)
    ridge_cap(R, w + 0.94, rz + rh, toon("#3f5070", rim=0.4), r=0.1)
    eave_trim(R, w, d, 0.45, rz + 0.02, toon("#3f5070", rim=0.3), r=0.08)
    # portico (centre)
    for x in (-0.85, 0.85):
        frustum("col", 0.16, 0.14, 2.3, PL("#f3ead0", "#e0d4b4", wear=0.3), R, loc=(x, -d / 2 - 0.85, 0.12), seg=12)
        frustum("colb", 0.22, 0.22, 0.12, toon("#f3ead0", rim=0.2), R, loc=(x, -d / 2 - 0.85, 0.12), seg=12)
        frustum("colc", 0.22, 0.22, 0.12, toon("#f3ead0", rim=0.2), R, loc=(x, -d / 2 - 0.85, 2.3), seg=12)
    box("arch", (2.4, 0.26, 0.26), toon("#f3ead0", rim=0.2), R, loc=(0, -d / 2 - 0.85, 2.55))
    sloped_roof("proof", 2.4, 1.1, 0.7, 0.15, slate, R, loc=(0, -d / 2 - 0.45, 2.6), ends=True, ridge_x=False)
    gable_wall(R, 2.4, 0.66, 2.62, -d / 2 - 1.01, toon("#f3ead0", rim=0.2))
    ellipsoid("pdisc", 0.17, glow("#ffc66a", 3), R, loc=(0, -d / 2 - 1.04, 2.95), scale=(1, 0.3, 1), seg=10, rings=8)
    door(R, (0, -d / 2, 0.3), w=1.2, h=1.9, color="#7a4a2a", frame="#f3ead0", step=False)
    for k in range(4):
        box("st", (2.8 + k * 0.3, 0.4, 0.1), ST("#c2bdb4", "#a7a49e", scale=3, bump=0.6), R, loc=(0, -d / 2 - 1.4 - k * 0.3, 0.05 + (0.1 * (3 - k)) * 0.0))
    for x in (-2.35, -1.45, 1.45, 2.35):
        arch_window(R, (x, -d / 2, 1.95), w=0.7, h=0.95, frame="#f3ead0", light="#ffe0a0")
    # bell cupola
    cz = rz + rh - 0.2
    box("cb", (1.1, 1.1, 0.4), toon("#f3ead0", rim=0.2), R, loc=(0, 0, cz), base=True)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box("cp", (0.12, 0.12, 0.8), toon("#f3ead0", rim=0.2), R, loc=(sx * 0.46, sy * 0.46, cz + 0.4), base=True)
    frustum("cbell", 0.2, 0.08, 0.35, toon("#d9a53a", rim=0.6), R, loc=(0, 0, cz + 0.55), seg=12, caps=(False, True))
    hip_roof("cr", 1.4, 1.4, 0.75, slate, R, loc=(0, 0, cz + 1.2), ridge_frac=0.0)
    ellipsoid("cfin", 0.07, toon("gold", rim=0.6), R, loc=(0, 0, cz + 1.98), seg=8, rings=6)
    # flag
    fx = 3.55
    frustum("pole", 0.04, 0.03, 4.2, WDT(), R, loc=(fx, -1.9, 0), seg=6)
    mesh_obj("flag", [(fx, -1.9, 4.1), (fx + 0.9, -1.9, 4.0), (fx + 0.9, -1.9, 3.5), (fx, -1.9, 3.5)], [(0, 1, 2, 3)],
             tex_toon("stripes", "#4f7ad8", "#f3e4c4", scale=5, plane="xz", bump=0.3, rim=0.4), R, smooth=False)
    ellipsoid("pb", 0.07, toon("gold", rim=0.6), R, loc=(fx, -1.9, 4.2), seg=8, rings=6)
    # chalkboard easel
    ep = pivot("easel", (-3.0, -2.4, 0), R)
    for x in (-0.5, 0.5):
        link_cyl("leg", (x, 0.15, 0), (x * 0.9, -0.1, 1.5), 0.04, WDT(), ep, seg=5)
    link_cyl("rear", (0, 0.45, 0), (0, 0.1, 1.5), 0.04, WDT(), ep, seg=5)
    box("bd", (1.2, 0.06, 0.9), toon("#2f4a3f", rim=0.3), ep, loc=(0, -0.1, 1.0))
    box("bf", (1.3, 0.05, 1.0), WDT(), ep, loc=(0, -0.07, 1.0))
    for (x, z, ln) in ((-0.3, 1.2, 0.5), (0.1, 1.0, 0.7), (-0.2, 0.8, 0.4)):
        box("ch", (ln, 0.02, 0.025), toon("#e8e4d8", rim=0), ep, loc=(x, -0.14, z))
    ellipsoid("sun", 0.1, toon("#e8c868", rim=0), ep, loc=(0.38, -0.14, 1.22), scale=(1, 0.2, 1), seg=8, rings=6)
    # hopscotch squares
    for i, (x, y) in enumerate([(2.0, -2.9), (2.0, -3.3), (1.6, -3.7), (2.4, -3.7), (2.0, -4.1), (2.0, -4.5)]):
        box("hop", (0.38, 0.38, 0.015), toon(["#e8884a", "#4f7ad8", "#e8b04a"][i % 3], rim=0.1), R, loc=(x, y, 0.01))
    bm = WD("#a06a3e", "#85502c", scale=3, bump=0.5)
    box("bench", (1.2, 0.35, 0.09), bm, R, loc=(-1.5, -3.4, 0.45))
    for x in (-1.95, -1.05):
        box("bl", (0.09, 0.3, 0.45), bm, R, loc=(x, -3.4, 0.22))
    bush(R, (-3.5, -1.0, 0), r=0.4, seed=3)
    bush(R, (3.3, -0.8, 0), r=0.38, col="leaf2", seed=5)
    plant_pot(R, (1.5, -d / 2 - 1.0, 0), 0.2, 0.3, kind="flower", seed=7)
    box("chim", (0.55, 0.55, 1.3), BR("#9a5a40", "#84483a", scale=3, soot=0.8), R, loc=(2.3, 0.5, rz + 0.3), base=True)
    truth_extras(R, cob=[(-2.9, -d / 2 - 0.1, 2.4, 0.5)], threads=[(-1.0, -d / 2 - 0.4, wh + 0.2), (2.2, -d / 2 - 0.4, wh + 0.1)],
                 dead=[(1.5, -d / 2 - 1.0, 0, 0.5)], holes=[(-1.5, -0.7, dict(wh=wh, rh=rh, d=d, ov=0.45, s=0.65, rz0=wh - 0.05))])
    return dict(smoke=[(2.3, 0.5, rz + 1.8)])


# =============================================================== fisher: tarred plank shack, nets, drying fish, boat
def net(parent, x0, x1, y, ztop, drop, col="#c9b98e", n=9, rows=5):
    m = toon(col, rim=0.2)
    pts = {}
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        sag = 0.14 * math.sin(math.pi * i / n)
        for j in range(rows + 1):
            z = ztop - sag - drop * j / rows * (1.0 - 0.15 * abs(math.sin(i)))
            pts[(i, j)] = (x + 0.02 * math.sin(j * 1.7 + i), y, z)
        link_cyl("nv", pts[(i, 0)], pts[(i, rows)], 0.014, m, parent, seg=3)
    for j in range(1, rows + 1):
        for i in range(n):
            link_cyl("nh", pts[(i, j)], pts[(i + 1, j)], 0.014, m, parent, seg=3)


def fish(parent, loc, c="#b9c6d6", s=1.0):
    p = pivot("fish", loc, parent)
    ellipsoid("fb", 0.1 * s, toon(c, rim=0.5), p, loc=(0, 0, -0.2 * s), scale=(0.7, 0.4, 2.2), seg=8, rings=6)
    mesh_obj("ft", [(0, 0, -0.42 * s), (-0.1 * s, 0, -0.6 * s), (0.1 * s, 0, -0.6 * s)], [(0, 2, 1)], toon(c, rim=0.3), p, smooth=False)
    return p


def fisher():
    R = pivot("fisher")
    w, d, wh = 3.2, 2.5, 2.3
    planks = WD("#5f8a98", "#4e7684", scale=3.0, along="v", bump=0.8, wear=0.9)
    box("found", (w + 0.1, d + 0.1, 0.3), ST("#8f8a88", "#6f6870", scale=2.6, moss=0.8), R, base=True)
    box("walls", (w, d, wh - 0.3), planks, R, loc=(0, 0, 0.3), base=True)
    for x in (-w / 2, w / 2):
        box("cpost", (0.16, 0.12, wh - 0.3), WDT("#4a3a30", "#3a2c24"), R, loc=(x, -d / 2 - 0.01, 0.3), base=True)
    box("btm", (w, 0.1, 0.16), WDT("#4a3a30", "#3a2c24"), R, loc=(0, -d / 2 - 0.02, wh - 0.1))
    rz = wh - 0.05
    tar = tilesm("#5a4a44", "#463a36", scale=3.0, wear=0.8)
    sloped_roof("roof", w, d, 1.0, 0.45, tar, R, loc=(0, 0, rz), ends=True)
    ridge_cap(R, w + 0.94, rz + 1.0, toon("#2e2622", rim=0.3), r=0.09)
    frustum("pipe", 0.1, 0.1, 1.4, toon("#3a3640", rim=0.4), R, loc=(-0.7, 0.4, rz + 0.5), seg=8)
    frustum("pcap", 0.17, 0.1, 0.12, toon("#3a3640", rim=0.4), R, loc=(-0.7, 0.4, rz + 1.8), seg=8)
    door(R, (-0.6, -d / 2, 0.0), w=0.8, h=1.65, color="#c44b3f", frame="#e8d6b0", arch=False, step=True)
    lantern2(R, (0.05, -d / 2, 1.9), color="#ffd070")
    # porthole
    ph = pivot("porthole", (0.85, -d / 2 - 0.02, 1.35), R)
    frustum("ring", 0.36, 0.36, 0.1, toon("#b88a3a", rim=0.6), ph, rot=(RAD(90), 0, 0), seg=20)
    frustum("gl", 0.27, 0.27, 0.06, glow("#ffd89a", 3.2), ph, loc=(0, -0.09, 0), rot=(RAD(90), 0, 0), seg=20)
    box("pm", (0.54, 0.03, 0.04), toon("#b88a3a", rim=0.5), ph, loc=(0, -0.16, 0))
    # life ring
    lr = pivot("lring", (1.2, -d / 2 - 0.04, 0.8), R)
    frustum("lr", 0.3, 0.3, 0.07, tex_toon("stripes", "#c44b3f", "#f6f0e6", scale=5, plane="xz", bump=0.2, rim=0.4), lr, rot=(RAD(90), 0, 0), seg=24)
    frustum("lh", 0.14, 0.14, 0.09, toon("#5f8a98", rim=0), lr, loc=(0, -0.01, 0), rot=(RAD(90), 0, 0), seg=14)
    # buoys on the wall
    for i, c in enumerate(("#c44b3f", "#f6f0e6", "#e8884a")):
        ellipsoid("buoy", 0.14, toon(c, rim=0.5), R, loc=(-1.45 + i * 0.0, -d / 2 - 0.2 - i * 0.02, 1.9 - i * 0.38), seg=10, rings=8)
    # drying net between poles (right)
    for x in (1.9, 3.6):
        frustum("pole", 0.05, 0.05, 2.5, WDT(), R, loc=(x, -1.5, 0), seg=6)
    net(R, 1.95, 3.55, -1.5, 2.35, 1.4)
    for i in range(7):
        ellipsoid("flt", 0.05, toon("#c44b3f" if i % 2 else "#f6f0e6", rim=0.4), R, loc=(2.0 + i * 0.26, -1.55, 2.35), seg=6, rings=4)
    # fish rack (left)
    for x in (-3.5, -1.9):
        link_cyl("rk", (x, -1.0, 0), (x, -1.0, 1.9), 0.05, WDT(), R, seg=5)
    box("rkb", (1.7, 0.08, 0.08), WDT(), R, loc=(-2.7, -1.0, 1.9))
    for i in range(6):
        link_cyl("fs", (-3.35 + i * 0.28, -1.0, 1.9), (-3.35 + i * 0.28, -1.0, 1.75), 0.01, toon("#d9c9a8", rim=0), R, seg=3)
        fish(R, (-3.35 + i * 0.28, -1.02, 1.75), ["#b9c6d6", "#a8b8cc"][i % 2], 1.0)
    # upturned rowboat
    bp = pivot("boat", (-0.6, -2.55, 0), R, rot=(0, 0, RAD(8)))
    ellipsoid("hull", 0.8, WD("#8a5a30", "#704826", scale=3, along="u", bump=0.8), bp, loc=(0, 0, 0.18), scale=(1.5, 0.62, 0.55), seg=18, rings=10)
    box("keel", (2.2, 0.07, 0.07), WDT(), bp, loc=(0, 0, 0.5))
    frustum("band", 0.0, 0.0, 0.0, toon("#c44b3f", rim=0), bp) if False else None
    for pot_i, (x, y) in enumerate(((1.4, -2.3), (1.9, -2.5))):
        frustum("pot", 0.3, 0.3, 0.35, FAB("weave", "#a07a46", "#7a5a30", scale=10), R, loc=(x, y, 0), seg=10)
        ellipsoid("pdome", 0.3, FAB("weave", "#a07a46", "#7a5a30", scale=10), R, loc=(x, y, 0.35), scale=(1, 1, 0.5), seg=10, rings=6)
    crate(R, (-2.2, -2.2, 0), 0.5, RAD(10), col="#8a6238")
    for i in range(3):
        fish(R, (-2.35 + i * 0.12, -2.2, 0.62 - 0.1), "#b9c6d6", 0.6)
    tube("rope", [(2.6, -2.7, 0.03), (2.9, -2.9, 0.03), (3.2, -2.7, 0.03), (3.0, -2.5, 0.03), (2.7, -2.6, 0.08)], 0.04, toon("#c9b98e", rim=0.2), R)
    bush(R, (-1.9, -0.2, 0), r=0.3, col="leaf3", flowers=False, seed=4)
    truth_extras(R, cob=[(-1.0, -d / 2 - 0.1, 1.9, 0.45)], threads=[(0.4, -d / 2 - 0.3, wh + 0.2), (-0.4, -d / 2 - 0.3, wh)],
                 holes=[(0.5, -0.5, dict(wh=wh, rh=1.0, d=d, ov=0.45, s=0.6, rz0=wh - 0.05))])
    return dict(smoke=[(-0.7, 0.4, rz + 2.0)])


# =============================================================== workshop: front-gable barn, big cog, open doors with forge glow
def workshop():
    R = pivot("workshop")
    w, d, wh = 5.0, 3.6, 2.6
    boards = WD("#7a5a44", "#5f4434", scale=2.6, along="v", bump=0.9, wear=0.7)
    iron = toon("#3a3640", rim=0.4)
    box("found", (w + 0.16, d + 0.16, 0.3), ST("#8a8088", "#6c6470", scale=2.4, moss=0.3, soot=0.4), R, base=True)
    box("walls", (w, d, wh - 0.3), boards, R, loc=(0, 0, 0.3), base=True)
    for x in np_range(-w / 2 + 0.1, w / 2 + 0.01, 1.2):
        box("rib", (0.12, 0.07, wh - 0.3), iron, R, loc=(x, -d / 2 - 0.02, 0.3), base=True)
    for z in (0.8, 2.1):
        box("strap", (w, 0.06, 0.1), iron, R, loc=(0, -d / 2 - 0.03, z))
    rh, ov = 1.9, 0.35
    rz = wh - 0.05
    gable_wall(R, w + 0.04, rh + 0.05, rz, -d / 2 - 0.01, boards)
    cor = tex_toon("stripes", "#b8794a", "#9c6238", scale=7.0, plane="xy", bump=0.9, wear=0.6, rim=0.35, ao=0.3)
    sloped_roof("roof", w, d, rh, ov, cor, R, loc=(0, 0, rz), ends=False, ridge_x=False)
    for s in (-1, 1):
        link_cyl("rake", (s * (w / 2 + ov), -d / 2 - ov, rz), (0, -d / 2 - ov, rz + rh), 0.07, toon("#5a3a26", rim=0.3), R, seg=5)
    frustum("rcap", 0.1, 0.1, d + 2 * ov, toon("#5a3a26", rim=0.3), R, loc=(0, -d / 2 - ov, rz + rh), rot=(RAD(-90), 0, 0), seg=8)
    # gears on the gable
    cogm = tex_toon("plain", "#c9944a", "#a9783a", scale=4, bump=0.3, rim=0.8, ao=0.2)
    cog(R, (0.0, -d / 2 - 0.12, rz + 0.8), 0.78, 12, cogm)
    cog(R, (0.95, -d / 2 - 0.12, rz + 0.45), 0.42, 8, tex_toon("plain", "#9a7a50", "#7a5a38", scale=4, bump=0.3, rim=0.8))
    cog(R, (-0.85, -d / 2 - 0.12, rz + 0.5), 0.32, 8, tex_toon("plain", "#b0b0b8", "#8a8a98", scale=4, bump=0.3, rim=0.8))
    # big doors, open
    dw, dh = 2.3, 1.95
    box("dframe", (dw + 0.3, 0.14, dh + 0.2), WDT("#4a3a30", "#3a2c24"), R, loc=(0, -d / 2 - 0.03, 0.3 + (dh + 0.2) / 2))
    box("dark", (dw, 0.06, dh), toon("#1c1420", rim=0), R, loc=(0, -d / 2 - 0.1, 0.3 + dh / 2))
    box("fg", (dw - 0.3, 0.05, dh - 0.5), glow("#ff8a30", 3.2), R, loc=(0, -d / 2 - 0.13, 0.3 + dh / 2 - 0.1))
    an = pivot("anvil", (0.2, -d / 2 - 0.45, 0.3), R)
    box("av1", (0.7, 0.3, 0.3), toon("#2a2630", rim=0.4), an, loc=(0, 0, 0.35))
    box("av2", (0.9, 0.3, 0.14), toon("#2a2630", rim=0.4), an, loc=(0, 0, 0.58))
    frustum("avh", 0.1, 0.03, 0.4, toon("#2a2630", rim=0.4), an, loc=(0.45, 0, 0.58), rot=(0, RAD(90), 0), seg=6)
    box("av3", (0.5, 0.4, 0.2), toon("#2a2630", rim=0.4), an, loc=(0, 0, 0.1))
    ellipsoid("fhalo", 1.4, glow("#ff9a38", 1.0, alpha=0.4, soft=True), R, loc=(0, -d / 2 - 0.5, 0.7), scale=(1.2, 0.3, 0.8), seg=14, rings=8)
    for s in (-1, 1):
        box("leaf", (0.8, 0.07, dh), boards, R, loc=(s * (dw / 2 + 0.4), -d / 2 - 0.35, 0.3 + dh / 2), rot=(0, 0, s * RAD(-55)))
        box("lstrap", (0.8, 0.08, 0.1), iron, R, loc=(s * (dw / 2 + 0.4), -d / 2 - 0.35, 0.3 + dh * 0.75), rot=(0, 0, s * RAD(-55)))
    # windows with gear sign
    for x in (-2.0, 2.0):
        window(R, (x, -d / 2, 1.5), w=0.5, h=0.6, frame="#3a3640", shutter=None, flowers=False, curtain=None, light="#ffb868")
    # pipes + chimney
    for x in (-2.3,):
        frustum("pp", 0.12, 0.12, 4.9, toon("#7a7a84", rim=0.5), R, loc=(x, 1.0, 0.3), seg=10)
        frustum("ppc", 0.22, 0.14, 0.2, toon("#5a5a64", rim=0.5), R, loc=(x, 1.0, 5.15), seg=10)
    for z in (1.0, 2.6, 4.0):
        frustum("pb", 0.16, 0.16, 0.08, toon("#4a4a54", rim=0.4), R, loc=(-2.3, 1.0, z), seg=10)
    link_cyl("elbow", (-2.3, 1.0, 1.4), (-2.3, -d / 2 - 0.1, 1.4), 0.07, toon("#7a7a84", rim=0.5), R, seg=8)
    # workbench + gear pile + wheel
    bm = WD("#a06a3e", "#85502c", scale=3, bump=0.6)
    box("bench", (1.5, 0.6, 0.1), bm, R, loc=(-2.2, -2.4, 0.9))
    for x in (-2.85, -1.55):
        box("bl", (0.1, 0.5, 0.9), bm, R, loc=(x, -2.4, 0.45))
    box("vise", (0.2, 0.2, 0.2), iron, R, loc=(-2.7, -2.4, 1.05))
    box("plank", (0.9, 0.3, 0.05), WD("#c9a870", "#a98850", scale=3), R, loc=(-2.0, -2.4, 0.98))
    for i, (x, y, r) in enumerate([(2.2, -2.5, 0.45), (2.75, -2.3, 0.3), (2.0, -3.0, 0.3)]):
        cp = pivot("gp", (x, y, 0.05 + i * 0.08), R, rot=(RAD(-90), 0, 0))
        cog(cp, (0, 0, 0), r, 10, tex_toon("plain", ["#c9944a", "#9a7a50", "#b0b0b8"][i], "#6a5a48", scale=4, bump=0.3, rim=0.8), thick=0.12)
    wp = pivot("wheel", (0.5, -3.0, 0.45), R, rot=(RAD(-4), 0, 0))
    for rr in (0.45, 0.38):
        frustum("rim", rr, rr, 0.06, WD("#8a5a30", "#704826", scale=4, along="v"), wp, loc=(0, 0.03, 0), rot=(RAD(90), 0, 0), seg=18, caps=(False, False))
    for k in range(6):
        a = k * math.pi / 3
        link_cyl("sp", (0, 0, 0), (math.cos(a) * 0.4, 0, math.sin(a) * 0.4), 0.03, WDT(), wp, seg=4)
    barrel(R, (-3.2, -1.2, 0), 0.3, 0.6, col="#7a6a5a")
    for i in range(4):
        box("pl", (1.4, 0.25, 0.08), WD("#c9a870", "#a98850", scale=3), R, loc=(3.0, -1.0 - 0.0, 0.05 + i * 0.1), rot=(0, 0, RAD(8 * (i - 1.5))))
    lantern2(R, (1.55, -d / 2, 2.2), color="#ffd070")
    truth_extras(R, cob=[(-1.5, -d / 2 - 0.1, 2.4, 0.5)], threads=[(-0.8, -d / 2 - 0.4, rz + 1.2), (1.0, -d / 2 - 0.4, rz + 0.9)],
                 holes=[(-0.9, 0.0, dict(wh=wh, rh=rh, d=d, ov=ov, s=0.6, rz0=wh - 0.05))])
    return dict(smoke=[(-2.3, 1.0, 5.5)])


# =============================================================== library: wine brick, corner turret, rose window, spool shelf window
def library():
    R = pivot("library")
    w, d, wh = 3.8, 3.4, 3.9
    brick = BR("#8f4a5a", "#7a3e4e", scale=2.2, wear=0.6, moss=0.15)
    cream = PL("#efe3c8", "#dccdaa", wear=0.3)
    box("found", (w + 0.2, d + 0.2, 0.4), ST("#a89c9c", "#867a82", scale=2.4, moss=0.4), R, base=True)
    box("walls", (w, d, wh - 0.4), brick, R, loc=(0, 0, 0.4), base=True)
    for z in (2.1, wh - 0.25):
        box("band", (w + 0.1, d + 0.1, 0.16), cream, R, loc=(0, 0, z))
    for sx in (-1, 1):
        box("quoin", (0.3, 0.3, wh - 0.4), cream, R, loc=(sx * (w / 2 - 0.05), -d / 2 + 0.05, 0.4), base=True)
    rz = wh - 0.1
    plum = tilesm("#5a4680", "#463570", scale=3.0)
    hip_roof("roof", w + 0.6, d + 0.6, 1.9, plum, R, loc=(0, 0, rz), ridge_frac=0.35)
    box("reave", (w + 0.64, d + 0.64, 0.1), toon("#322458", rim=0.3), R, loc=(0, 0, rz + 0.02))
    frustum("fin", 0.04, 0.02, 0.8, toon("gold", rim=0.5), R, loc=(0, 0, rz + 1.9), seg=5)
    ellipsoid("finb", 0.1, glow("#ffc66a", 4), R, loc=(0, 0, rz + 2.0), seg=8, rings=6)
    # turret
    tp = pivot("turret", (-w / 2 - 0.1, -d / 2 + 0.2, 0), R)
    frustum("tw", 0.85, 0.8, wh + 0.9, ST("#b0a498", "#8c8088", scale=2.4, wear=0.7, moss=0.3), tp, seg=20)
    frustum("tband", 0.9, 0.9, 0.14, cream, tp, loc=(0, 0, 2.1), seg=20)
    frustum("tcone", 1.05, 0.0, 1.9, plum, tp, loc=(0, 0, wh + 0.8), seg=20, caps=(False, False))
    ellipsoid("tf", 0.09, toon("gold", rim=0.6), tp, loc=(0, 0, wh + 2.7), seg=8, rings=6)
    for z in (1.5, 3.1):
        pw = pivot("tw", (0, -0.82, z), tp)
        box("tf", (0.34, 0.08, 0.7), toon("#efe3c8", rim=0.1), pw)
        box("tg", (0.24, 0.05, 0.6), glow("#ffd89a", 3), pw, loc=(0, -0.05, 0))
    # entrance
    door(R, (-0.3, -d / 2, 0.4), w=1.1, h=2.0, color="#3a2a50", frame="#efe3c8", step=False)
    for x in (-1.15, 0.55):
        frustum("pc", 0.12, 0.1, 2.2, cream, R, loc=(x, -d / 2 - 0.55, 0.14), seg=10)
    box("pl", (2.0, 0.35, 0.18), cream, R, loc=(-0.3, -d / 2 - 0.55, 2.35))
    for k in range(3):
        box("st", (2.3 + k * 0.35, 0.4, 0.12), ST("#c2bdb4", "#a7a49e", scale=3, bump=0.6), R, loc=(-0.3, -d / 2 - 0.6 - k * 0.32, 0.06))
    # rose window
    rw = pivot("rose", (-0.3, -d / 2 - 0.02, 3.1), R)
    frustum("rr", 0.5, 0.5, 0.1, cream, rw, rot=(RAD(90), 0, 0), seg=24)
    frustum("rg", 0.4, 0.4, 0.06, glow("#ffd89a" if not EL.TRUTH else "#35d3b0", 1.8), rw, loc=(0, -0.08, 0), rot=(RAD(90), 0, 0), seg=24)
    for k in range(6):
        a = k * math.pi / 6
        box("rs", (0.8, 0.03, 0.05), toon("#5a3a2a", rim=0), rw, loc=(0, -0.12, 0), rot=(0, a, 0))
    # big window with a spool wall
    wp = arch_window(R, (1.1, -d / 2, 1.75), w=0.95, h=1.35, frame="#efe3c8", light="#ffd89a", bars=False)
    cols = ["#e8884a", "#4f7ad8", "#e8b04a", "#c44b3f", "#a07ad8", "#35b39a"]
    for r_ in range(5):
        for c_ in range(5):
            frustum("sp", 0.07, 0.07, 0.1, toon(cols[(r_ * 2 + c_) % 6], rim=0.5), wp, loc=(-0.38 + c_ * 0.19, -0.1, -0.5 + r_ * 0.27), rot=(RAD(90), 0, 0), seg=8)
    arch_window(R, (1.1, -d / 2, 3.1), w=0.7, h=0.6, frame="#efe3c8", light="#ffe0a0")
    # book sign
    sp = pivot("sign", (1.9, -d / 2 - 0.05, 2.9), R)
    link_cyl("arm", (0, 0, 0.0), (0, -0.7, 0.0), 0.03, WDT(), sp, seg=5)
    bk = pivot("bk", (0, -0.7, -0.5), sp)
    for s in (-1, 1):
        box("pg", (0.42, 0.05, 0.55), toon("#f3e4c4", rim=0.3), bk, loc=(s * 0.22, 0, 0), rot=(0, s * RAD(-9), 0))
        box("cv", (0.46, 0.04, 0.6), toon("#8a3a4a", rim=0.4), bk, loc=(s * 0.23, 0.04, 0), rot=(0, s * RAD(-9), 0))
        for z in (-0.12, 0.05, 0.2):
            box("tx", (0.28, 0.01, 0.015), toon("#6a6a8a", rim=0), bk, loc=(s * 0.22, -0.03, z))
    box("rib", (0.04, 0.02, 0.5), toon("#35d3b0", rim=0.2), bk, loc=(0.0, -0.045, -0.2))
    for i, c in enumerate(cols):   # spool pile on the steps
        spool(R, (-1.9 + (i % 3) * 0.3, -d / 2 - 1.25 + (i // 3) * 0.3, 0.1), 0.1, 0.2, c)
    for i in range(3):
        book(R, (1.9, -2.3, 0.04 + i * 0.07), (0.34, 0.24, 0.06), ["wine", "indigo", "forest"][i], rot=0.2 * i)
    lantern2(R, (0.5, -d / 2, 2.6), color="#ffd070") if False else None
    plant_pot(R, (1.5, -2.5, 0), 0.22, 0.34, kind="fern", seed=2, pot="#6a5a9a")
    bush(R, (2.5, -0.6, 0), r=0.38, seed=9, fcols=("#c79ae8", "white"))
    box("chim", (0.5, 0.5, 1.2), BR("#8a5a60", "#74484e", scale=3, soot=0.7), R, loc=(1.1, 0.7, rz + 0.5), base=True)
    truth_extras(R, cob=[(-1.1, -d / 2 - 0.1, 2.0, 0.5)], threads=[(0.6, -d / 2 - 0.4, wh + 0.3), (1.6, -d / 2 - 0.4, 3.4)],
                 dead=[(1.5, -2.5, 0, 0.55)])
    return dict(smoke=[(1.1, 0.7, rz + 1.95)])


# =============================================================== observatory: domed roof with a slit and a brass telescope
def observatory():
    R = pivot("obs")
    r = 2.0
    wh = 3.6
    plast = PL("#e4dcf0", "#cdc4e0", wear=0.5, moss=0.2)
    frustum("plinth", 2.35, 2.2, 0.55, ST("#8a90a8", "#6c7290", scale=2.2, moss=0.6), R, seg=28)
    frustum("wall", 2.0, 1.85, wh, plast, R, loc=(0, 0, 0.5), seg=28)
    frustum("band", 1.98, 1.98, 0.16, ST("#8a90a8", "#6c7290", scale=2.4), R, loc=(0, 0, 1.3), seg=28, caps=(False, False))
    frustum("ring", 1.92, 1.92, 0.2, toon("#b88a3a", rim=0.5), R, loc=(0, 0, 3.0), seg=28, caps=(False, False))
    # balcony
    bz = 2.0
    frustum("bal", 2.4, 2.4, 0.12, WD("#8a5a30", "#704826", scale=3, plane="xy"), R, loc=(0, 0, bz), seg=28)
    for i in range(30):
        a = 2 * math.pi * i / 30
        if math.sin(a) > 0.5:
            continue
        frustum("bp", 0.03, 0.03, 0.5, WDT(), R, loc=(math.cos(a) * 2.35, math.sin(a) * 2.35, bz + 0.12), seg=5)
    frustum("rail", 2.37, 2.37, 0.06, WDT(), R, loc=(0, 0, bz + 0.6), seg=28, caps=(False, False))
    # door + windows on the curved wall
    door(R, (0, -2.0, 0.3), w=0.95, h=1.55, color="#3a4a8a", frame="#e8e0f0", step=True)
    for ang, z, ww in ((-48, 2.9, 0.4), (48, 2.9, 0.4), (-60, 1.6, 0.4), (60, 1.6, 0.4)):
        a = math.radians(ang)
        rr = 1.9
        wp = pivot("win", (math.sin(a) * rr, -math.cos(a) * rr, z), R, rot=(0, 0, -a))
        box("wf", (ww + 0.14, 0.1, ww + 0.2), toon("#e8e0f0", rim=0.2), wp)
        box("wp", (ww, 0.05, ww + 0.05), glow("#ffd89a", 3.0), wp, loc=(0, -0.06, 0))
        box("wm", (0.04, 0.06, ww + 0.05), toon("#e8e0f0", rim=0.2), wp, loc=(0, -0.08, 0))
    for k, a_ in enumerate((-25, 0, 25, 0)):   # gold stars painted on the wall band
        aa = math.radians(a_)
        if k == 3:
            continue
        ellipsoid("star", 0.12, glow("#ffd56a", 3.5), R, loc=(math.sin(aa) * 1.95, -math.cos(aa) * 1.95, 3.5 - (k % 2) * 0.2), scale=(1, 0.25, 1), rot=(0, 0, -aa), seg=5, rings=3)
    # dome
    dz = 0.5 + wh
    frustum("dtrim", 2.12, 2.12, 0.18, toon("#b88a3a", rim=0.5), R, loc=(0, 0, dz - 0.02), seg=28)
    Rd = 2.05
    ellipsoid("dome", Rd, tex_toon("plain", "#7388c4", "#5c70aa", scale=2.0, bump=0.2, rim=0.8, ao=0.3, wear=0.4), R, loc=(0, 0, dz), scale=(1, 1, 0.85), seg=32, rings=20)
    for k in range(6):
        ph = k * math.pi / 6
        pts = [(math.cos(t) * math.cos(ph) * Rd * 1.012, math.cos(t) * math.sin(ph) * Rd * 1.012, dz + math.sin(t) * 0.85 * Rd * 1.012)
               for t in [math.radians(a) for a in range(0, 181, 12)]]
        tube("rib", pts, 0.035, toon("#b88a3a", rim=0.5), R)
    # the slit
    Rs = Rd * 1.016
    left, right = [], []
    for ai in range(6, 87, 6):
        t = math.radians(ai)
        for x, tgt in ((-0.27, left), (0.27, right)):
            yy = -math.sqrt(max(0.0, (Rs * math.cos(t)) ** 2 - x * x))
            tgt.append((x, yy, dz + 0.85 * Rs * math.sin(t)))
    n = len(left)
    verts = left + right
    faces = [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)]
    mesh_obj("slit", verts, faces, toon("#0e1026", rim=0), R, smooth=False)
    mesh_obj("slitg", [(x * 0.35, y - 0.012, z) for (x, y, z) in left] + [(x * 0.35, y - 0.012, z) for (x, y, z) in right],
             faces, glow("#6f8aff", 1.4), R, smooth=False)
    # telescope poking out of the slit
    link_cyl("tel", (0, -1.2, dz + 0.9), (0, -2.7, dz + 1.9), 0.2, toon("#b88a3a", rim=0.7), R, seg=14, r2=0.3)
    link_cyl("tel2", (0, -2.7, dz + 1.9), (0, -3.0, dz + 2.13), 0.31, toon("#2e2a40", rim=0.5), R, seg=14, r2=0.31)
    ellipsoid("lens", 0.28, glow("#9fb4ff", 2.6), R, loc=(0, -3.01, dz + 2.14), scale=(1, 0.3, 1), seg=10, rings=6)
    for t in (0.35, 0.65):
        frustum("tband", 0.27, 0.27, 0.07, toon("#7a5a20", rim=0.5), R, loc=(0, -1.2 - 1.5 * t, dz + 0.9 + 1.0 * t), rot=(RAD(-56), 0, 0), seg=14)
    link_cyl("eye", (0, -1.25, dz + 0.9), (0, -0.8, dz + 0.6), 0.1, toon("#2e2a40", rim=0.5), R, seg=8)
    frustum("fin", 0.04, 0.02, 0.5, toon("gold", rim=0.5), R, loc=(0, 0, dz + 0.85 * Rd), seg=6)
    ellipsoid("finb", 0.09, glow("#ffd56a", 5), R, loc=(0, 0, dz + 0.85 * Rd + 0.55), seg=8, rings=6)
    # annex (right)
    ax, ay = 3.7, -0.2
    box("afound", (2.1, 1.9, 0.3), ST("#8a90a8", "#6c7290", scale=2.4), R, loc=(ax, ay, 0), base=True)
    box("awalls", (1.9, 1.7, 1.5), PL("#e4dcf0", "#cdc4e0", wear=0.5), R, loc=(ax, ay, 0.3), base=True)
    sloped_roof("aroof", 1.9, 1.7, 0.7, 0.3, tilesm("#5fa090", "#4a8a7c", scale=4.0), R, loc=(ax, ay, 1.75), ends=True)
    window(R, (ax - 0.4, ay - 0.85, 1.1), w=0.45, h=0.55, frame="#e8e0f0", shutter="#3a4a8a", flowers=False, curtain=None, light="#ffd89a")
    door(R, (ax + 0.45, ay - 0.85, 0.3), w=0.6, h=1.2, color="#3a4a8a", frame="#e8e0f0", arch=False, step=False, knob=False)
    box("chim", (0.4, 0.4, 0.9), BR("#8a7a8a", "#6a5a70", scale=3, soot=0.8), R, loc=(ax + 0.5, ay + 0.4, 2.0), base=True)
    # sundial, bench, charts
    frustum("sd", 0.22, 0.28, 0.6, ST("#a89c9c", "#867a82", scale=3), R, loc=(-3.0, -2.2, 0), seg=8)
    frustum("sdp", 0.4, 0.4, 0.06, toon("#b88a3a", rim=0.6), R, loc=(-3.0, -2.2, 0.6), seg=16)
    mesh_obj("gn", [(-3.0, -2.2, 0.66), (-2.8, -2.2, 0.66), (-3.0, -2.2, 0.95)], [(0, 1, 2)], toon("#7a5a20", rim=0.5), R, smooth=False)
    bm = ST("#b0a498", "#8c8088", scale=3, bump=0.6)
    box("bench", (1.2, 0.4, 0.1), bm, R, loc=(2.2, -2.7, 0.45))
    for x in (1.7, 2.7):
        box("bl", (0.12, 0.34, 0.45), bm, R, loc=(x, -2.7, 0.22))
    bush(R, (-2.9, -0.4, 0), r=0.4, seed=11, fcols=("#c79ae8", "white"))
    big_lantern(R, (1.4, -2.2, 0), 0.8, color="#9fb4ff", glow_s=6)
    truth_extras(R, cob=[(-0.8, -2.05, 1.9, 0.5)], threads=[(1.2, -2.0, 3.5), (-1.4, -1.9, 3.2)],
                 dead=[(-2.9, -0.4, 0, 0.6)])
    return dict(smoke=[(ax + 0.5, ay + 0.4, 2.95)])


BUILDERS = {"inn": inn, "bell_tower": bell_tower, "tailor": tailor, "school": school, "fisher": fisher,
            "workshop": workshop, "library": library, "observatory": observatory}

if __name__ == "__main__":
    try:
        import buildings_d
        BUILDERS.update(buildings_d.BUILDERS)
    except ImportError:
        pass
    run_main(BUILDERS)
