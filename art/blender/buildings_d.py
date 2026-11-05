"""World-2 buildings, part 2: stories, farm, shepherd, herbs, fairy, guild, lighthouse, great_tower. Imported by buildings_c.py."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w2lib import *  # noqa
import env_lib as EL
from buildings_c import tilesm, cog


def flame(parent, loc, s=1.0, color="#ff8a28"):
    p = pivot("flame", loc, parent)
    for i, (dx, hh, rr) in enumerate([(0, 0.55, 0.14), (-0.12, 0.38, 0.1), (0.12, 0.4, 0.1)]):
        frustum("fl", rr * s, 0.0, hh * s, glow(color if i else "#ffd070", 6), p, loc=(dx * s, 0, 0), seg=7, caps=(True, False))
    ellipsoid("fh", 0.5 * s, glow(color, 1.5, alpha=0.45, soft=True), p, loc=(0, -0.05, 0.25 * s), seg=12, rings=8)
    return p


# =============================================================== stories hall: long timber hall, fire glow
def stories():
    R = pivot("stories")
    w, d, wh = 7.4, 3.3, 2.2
    logs = WD("#7a4e30", "#63402a", scale=3.4, along="u", bump=1.0, wear=0.6)
    dk = WDT("#4a2e1c", "#3a2214")
    box("found", (w + 0.2, d + 0.2, 0.3), ST("#8a8088", "#6c6470", scale=2.4, moss=0.5), R, base=True)
    box("walls", (w, d, wh - 0.3), logs, R, loc=(0, 0, 0.3), base=True)
    for sx in (-1, 1):
        frustum("corner", 0.2, 0.2, wh - 0.1, WD("#6a4326", "#5a3720", scale=4, along="v"), R, loc=(sx * w / 2, -d / 2, 0.2), seg=10)
    for k in range(5):
        z = 0.5 + k * 0.38
        for sx in (-1, 1):
            ellipsoid("le", 0.1, toon("#8a5a38", rim=0.4), R, loc=(sx * (w / 2 + 0.05), -d / 2 - 0.02, z), scale=(1, 0.8, 1), seg=8, rings=6)
    rz, rh, ov = wh - 0.05, 1.55, 0.6
    th = TH("#d2a24e", "#b38238", scale=2.2, wear=0.5, moss=0.3)
    sloped_roof("roof", w, d, rh, ov, th, R, loc=(0, 0, rz), ends=True)
    frustum("ridge", 0.2, 0.2, w + 2 * ov + 0.2, TH("#a8803a", "#8a6428", scale=3), R, loc=(-(w / 2 + ov + 0.1), 0, rz + rh), rot=(0, RAD(90), 0), seg=10)
    for sx in (-1, 1):   # crossed gable ends
        for a in (-35, 35):
            box("x", (0.1, 0.1, 1.3), dk, R, loc=(sx * (w / 2 + ov + 0.1), 0, rz + rh + 0.15), rot=(RAD(a), 0, 0))
    eave_trim(R, w, d, ov, rz + 0.02, toon("#8a6428", rim=0.3), r=0.1)
    # doorway with the fire inside
    dw, dh = 2.0, 1.75
    box("dfr", (dw + 0.5, 0.2, dh + 0.3), dk, R, loc=(0, -d / 2 - 0.03, 0.3 + (dh + 0.3) / 2))
    box("dark", (dw, 0.06, dh), toon("#1c1018", rim=0), R, loc=(0, -d / 2 - 0.14, 0.3 + dh / 2))
    box("fglow", (dw - 0.3, 0.05, dh - 0.55), glow("#ff7a20", 2.8), R, loc=(0, -d / 2 - 0.17, 0.3 + dh / 2 - 0.15))
    ellipsoid("fhalo", 1.8, glow("#ff9a38", 1.1, alpha=0.4, soft=True), R, loc=(0, -d / 2 - 0.7, 0.8), scale=(1.4, 0.3, 0.7), seg=14, rings=8)
    flame(R, (0, -d / 2 - 0.2, 0.4), 1.6)
    for x in (-0.6, 0.6):   # silhouettes of listeners
        pass
    frustum("lint", 0.14, 0.14, dw + 0.8, dk, R, loc=(-(dw / 2 + 0.4), -d / 2 - 0.12, 0.3 + dh + 0.15), rot=(0, RAD(90), 0), seg=8)
    # carved story posts flanking
    for sx in (-1, 1):
        px = sx * 1.55
        frustum("post", 0.17, 0.15, 2.4, WD("#6a4326", "#5a3720", scale=4, along="v"), R, loc=(px, -d / 2 - 0.5, 0.0), seg=10)
        for z, c in ((0.5, "#2f9a8a"), (1.0, "#c44b3f"), (1.5, "#e8b04a")):
            frustum("ring", 0.2, 0.2, 0.1, toon(c, rim=0.4), R, loc=(px, -d / 2 - 0.5, z), seg=10, caps=(False, False))
        ellipsoid("knob", 0.2, toon("#8a5a38", rim=0.4), R, loc=(px, -d / 2 - 0.5, 2.5), seg=10, rings=8)
        ellipsoid("eye", 0.045, glow("#ffd56a", 4), R, loc=(px - 0.07, -d / 2 - 0.68, 2.55), seg=6, rings=4)
        ellipsoid("eye", 0.045, glow("#ffd56a", 4), R, loc=(px + 0.07, -d / 2 - 0.68, 2.55), seg=6, rings=4)
        lantern2(R, (px + sx * 0.5, -d / 2 - 0.5, 2.1), color="#ffb04a")
    for x in (-2.6, -3.3, 2.6, 3.3):
        window(R, (x, -d / 2, 1.35), w=0.5, h=0.55, frame="#4a2e1c", shutter="#8a3a2a", flowers=False, curtain=None, light="#ffa850")
    # smoke vent on the roof
    vz = rz + rh * 0.9
    box("vent", (0.9, 0.9, 0.5), dk, R, loc=(1.0, 0.0, vz), base=True)
    hip_roof("ventr", 1.3, 1.3, 0.55, th, R, loc=(1.0, 0, vz + 0.5), ridge_frac=0.0)
    # benches, logs, fire pit
    bm = WD("#8a6238", "#6a4a2a", scale=3, bump=0.6)
    for (x, y) in ((-2.0, -2.5), (-3.2, -2.9)):
        box("bn", (1.6, 0.4, 0.1), bm, R, loc=(x, y, 0.45))
        for dx in (-0.65, 0.65):
            box("bl", (0.1, 0.34, 0.45), bm, R, loc=(x + dx, y, 0.22))
    pp = pivot("pit", (2.8, -2.7, 0), R)
    for k in range(9):
        a = k * 2 * math.pi / 9
        ellipsoid("stn", 0.17, ST("#8d8794", "#6f6874", scale=3, bump=0.8), pp, loc=(math.cos(a) * 0.55, math.sin(a) * 0.45, 0.12), scale=(1, 1, 0.8), seg=8, rings=6)
    flame(pp, (0, 0, 0.1), 1.3)
    for k in range(3):
        link_cyl("lg", (-0.25, -0.1 + k * 0.1, 0.12), (0.25, 0.0 + k * 0.1, 0.2), 0.05, toon("#4a2e1c", rim=0.2), pp, seg=5)
    for k, (x, z) in enumerate(((-3.5, 0.15), (-3.2, 0.15), (-2.95, 0.15), (-3.35, 0.38), (-3.1, 0.38), (-3.22, 0.6))):
        frustum("logend", 0.13, 0.13, 0.7, WD("#8a5a38", "#6a4326", scale=6, along="v"), R, loc=(x - 0.2, -1.8, z), rot=(RAD(-90), 0, 0), seg=10)
    plant_pot(R, (-1.2, -2.0, 0), 0.2, 0.3, kind="fern", seed=4)
    bush(R, (3.9, -1.0, 0), r=0.4, seed=6, fcols=("#ffd86a", "white"))
    truth_extras(R, cob=[(-1.8, -d / 2 - 0.2, 2.0, 0.5)], threads=[(-1.0, -d / 2 - 0.5, 2.5), (2.0, -d / 2 - 0.5, 2.4)],
                 dead=[(-1.2, -2.0, 0, 0.5)], holes=[(-2.0, -0.7, dict(wh=wh, rh=rh, d=d, ov=ov, s=0.7, rz0=wh - 0.05))])
    return dict(smoke=[(1.0, 0.0, vz + 1.2)])


# =============================================================== farm: red gambrel barn, farmhouse, silo
def farm():
    R = pivot("farm")
    # barn
    bx, by, bw, bd, bh = 1.6, 0.4, 4.0, 3.2, 2.6
    red = WD("#b04a3a", "#963c2e", scale=3, along="v", bump=0.9, wear=0.7)
    white = toon("#f3ead8", rim=0.2)
    bp = pivot("barn", (bx, by, 0), R)
    box("bf", (bw + 0.1, bd + 0.1, 0.3), ST("#8a8088", "#6c6470", scale=2.4, moss=0.5), bp, base=True)
    box("bwalls", (bw, bd, bh - 0.3), red, bp, loc=(0, 0, 0.3), base=True)
    for x in (-bw / 2 + 0.07, bw / 2 - 0.07):
        box("bpost", (0.16, 0.08, bh - 0.3), white, bp, loc=(x, -bd / 2 - 0.02, 0.3), base=True)
    box("btrim", (bw, 0.08, 0.14), white, bp, loc=(0, -bd / 2 - 0.02, bh - 0.12))
    D = bd / 2 + 0.4
    gamb = [(-D, 0), (-D * 0.64, 1.05), (0, 1.75), (D * 0.64, 1.05), (D, 0)]
    prism_roof("broof", gamb, bw + 0.8, tilesm("#6e7288", "#5a5e74", scale=3.4), bp, loc=(0, 0, bh - 0.05), caps=True)
    for (y0, z0, y1, z1) in ((-D, 0, -D * 0.64, 1.05), (-D * 0.64, 1.05, 0, 1.75)):
        pass
    link_cyl("bridge", (-bw / 2 - 0.4, 0, bh + 1.7), (bw / 2 + 0.4, 0, bh + 1.7), 0.09, toon("#4a4a60", rim=0.4), bp, seg=8)
    # big doors with X braces
    for s in (-1, 1):
        lx = s * 0.55
        box("bd", (1.1, 0.08, 1.9), WD("#c4553f", "#a8452f", scale=3, along="v"), bp, loc=(lx, -bd / 2 - 0.08, 0.3 + 0.95))
        for a in (-1, 1):
            link_cyl("x", (lx - 0.5, -bd / 2 - 0.14, 0.3 + 0.95 - a * 0.9), (lx + 0.5, -bd / 2 - 0.14, 0.3 + 0.95 + a * 0.9), 0.045, white, bp, seg=5)
        box("bfr", (1.16, 0.06, 0.08), white, bp, loc=(lx, -bd / 2 - 0.13, 0.3 + 0.1))
        box("bfr", (1.16, 0.06, 0.08), white, bp, loc=(lx, -bd / 2 - 0.13, 0.3 + 1.88))
    box("bdf", (2.4, 0.1, 2.1), white, bp, loc=(0, -bd / 2 - 0.03, 0.3 + 1.0))
    box("bdf2", (2.2, 0.1, 1.9), toon("#1c1420", rim=0), bp, loc=(0, -bd / 2 - 0.05, 0.3 + 0.95))
    # hayloft
    box("hl", (0.9, 0.06, 0.8), toon("#2a1c20", rim=0), bp, loc=(0, -bd / 2 - 0.05, bh + 0.7))
    box("hlf", (1.1, 0.06, 1.0), white, bp, loc=(0, -bd / 2 - 0.03, bh + 0.7))
    box("hl2", (0.9, 0.06, 0.8), toon("#2a1c20", rim=0), bp, loc=(0, -bd / 2 - 0.07, bh + 0.7))
    ellipsoid("hay", 0.38, TH("#e0b858", "#c8a040", scale=4), bp, loc=(0, -bd / 2 - 0.12, bh + 0.5), scale=(1.1, 0.3, 0.6), seg=10, rings=6)
    link_cyl("hb", (0, -bd / 2, bh + 1.3), (0, -bd / 2 - 0.9, bh + 1.3), 0.05, WDT(), bp, seg=5)
    ellipsoid("pulley", 0.1, toon("#3a3640", rim=0.4), bp, loc=(0, -bd / 2 - 0.9, bh + 1.25), seg=8, rings=6)
    # cupola
    box("cup", (0.7, 0.7, 0.5), white, bp, loc=(0, 0, bh + 1.6), base=True)
    hip_roof("cupr", 1.0, 1.0, 0.5, tilesm("#6e7288", "#5a5e74"), bp, loc=(0, 0, bh + 2.1), ridge_frac=0.0)
    link_cyl("wv", (0, 0, bh + 2.55), (0, 0, bh + 3.1), 0.025, toon("gold", rim=0.5), bp, seg=5)
    box("wvv", (0.5, 0.03, 0.18), toon("gold", rim=0.5), bp, loc=(0.1, 0, bh + 3.0))
    # silo
    sx_, sy_ = bx + 3.1, by + 0.5
    frustum("silo", 0.85, 0.85, 4.6, tex_toon("plain", "#aab6c2", "#8c98a6", scale=2, bump=0.2, wear=0.7, rim=0.6), R, loc=(sx_, sy_, 0), seg=20)
    for z in (0.9, 1.9, 2.9, 3.9):
        frustum("sband", 0.89, 0.89, 0.08, toon("#5a5a6a", rim=0.4), R, loc=(sx_, sy_, z), seg=20, caps=(False, False))
    ellipsoid("sdome", 0.9, toon("#b04a3a", rim=0.5), R, loc=(sx_, sy_, 4.6), scale=(1, 1, 0.65), seg=18, rings=10)
    ellipsoid("sk", 0.07, toon("gold", rim=0.6), R, loc=(sx_, sy_, 5.2), seg=8, rings=6)
    # farmhouse
    hx, hy = -2.9, -0.5
    hp = pivot("house", (hx, hy, 0), R)
    hw, hd, hwh = 2.6, 2.3, 2.1
    box("hf", (hw + 0.1, hd + 0.1, 0.28), ST("#a89c90", "#85787c", scale=2.4), hp, base=True)
    box("hwalls", (hw, hd, hwh - 0.28), PL("#f1e2bc", "#e4d0a4", wear=0.5, moss=0.2), hp, loc=(0, 0, 0.28), base=True)
    hrh = 1.4
    brown = tilesm("#7a4a3a", "#643c2e", scale=3.4)
    sloped_roof("hroof", hw, hd, hrh, 0.3, brown, hp, loc=(0, 0, hwh - 0.05), ends=True, ridge_x=False)
    gable_wall(hp, hw, hrh - 0.05, hwh - 0.05, -hd / 2 - 0.01, PL("#f1e2bc", "#e4d0a4", wear=0.5))
    sloped_roof("hroof2", hw + 0.1, hd - 0.3, 0.0, 0.0, brown, hp, loc=(0, 0, hwh), ends=False) if False else None
    ellipsoid("gl", 0.2, glow("#ffc66a", 3.2), hp, loc=(0, -hd / 2 - 0.05, hwh + 0.45), scale=(1, 0.3, 1.1), seg=8, rings=6)
    door(hp, (-0.5, -hd / 2, 0.28), w=0.8, h=1.55, color="#3a6a7a", frame="#f3ead8", step=True)
    window(hp, (0.75, -hd / 2, 1.2), w=0.6, h=0.65, frame="#f3ead8", shutter="#3a6a7a", flowers=True, curtain="#c44b3f")
    box("hchim", (0.5, 0.5, 1.5), BR("#a0583e", "#8a4632", scale=3, soot=0.8), hp, loc=(0.6, 0.5, hwh + 0.3), base=True)
    # fields, bales, fence
    soil = toon("#4a3426", rim=0)
    for i in range(3):
        y = -2.55 - i * 0.55
        box("row", (3.0, 0.3, 0.1), soil, R, loc=(-2.0, y, 0.05))
        for k in range(8):
            ellipsoid("crop", 0.12, toon(["leaf1", "leaf2", "leaf3"][(k + i) % 3], rim=0.3), R, loc=(-3.3 + k * 0.38, y, 0.22), scale=(1, 0.8, 1.2), seg=8, rings=6)
        if i == 1:
            for k in range(3):
                ellipsoid("pump", 0.15, toon("#e8842a", rim=0.5), R, loc=(-1.0 + k * 0.5, y + 0.15, 0.2), scale=(1.1, 1.1, 0.8), seg=8, rings=6)
    for k, (x, y) in enumerate(((3.0, -2.3), (3.7, -2.1), (3.35, -2.25))):
        frustum("bale", 0.36, 0.36, 0.6, TH("#e0b858", "#c8a040", scale=4, wear=0.2), R, loc=(x - 0.3, y, 0.36 + (0.55 if k == 2 else 0.0)), rot=(0, RAD(90), 0), seg=14)
        for dx in (-0.12, 0.12):
            frustum("bnd", 0.37, 0.37, 0.04, toon("#7a5a30", rim=0.2), R, loc=(x + dx - 0.3, y, 0.36 + (0.55 if k == 2 else 0.0)), rot=(0, RAD(90), 0), seg=14, caps=(False, False))
    fence_run(R, -0.6, 1.0, -2.7, n=3)
    barrel(R, (0.0, -1.9, 0), 0.3, 0.6, col="#6a8a9a")
    truth_extras(R, cob=[(-3.0, -1.5, 1.7, 0.5)], threads=[(0.4, -2.0, 3.3), (-2.4, -1.8, 2.8)],
                 dead=[(-2.0, -2.6, 0.1, 0.5), (-1.0, -2.6, 0.1, 0.5)],
                 holes=[(0.0, -0.7, dict(wh=hwh - 0.05, rh=hrh, d=hd, ov=0.3, s=0.5, rz0=0))] if False else [])
    return dict(smoke=[(hx + 0.6, hy + 0.5, hwh + 2.0)])


# =============================================================== shepherd's wagon with a sheep pen
def shepherd():
    R = pivot("shep")
    bl, bd, bz = 3.6, 1.9, 0.62
    body = WD("#4f7a5a", "#3f6a4a", scale=3.2, along="u", bump=0.9, wear=0.8)
    box("floor", (bl + 0.2, bd + 0.2, 0.14), WDT("#5a3a26", "#4a2e1e"), R, loc=(0, 0, bz - 0.07))
    box("walls", (bl, bd, 1.35), body, R, loc=(0, 0, bz), base=True)
    box("trim", (bl + 0.06, bd + 0.06, 0.1), toon("#f3ead0", rim=0.3), R, loc=(0, 0, bz + 1.3))
    box("trimb", (bl + 0.06, bd + 0.06, 0.08), toon("#c44b3f", rim=0.3), R, loc=(0, 0, bz + 0.05))
    prof = [(-math.cos(math.radians(t)) * (bd / 2 + 0.12), 0.95 * math.sin(math.radians(t))) for t in range(0, 181, 15)]
    canvas = tex_toon("weave", "#e8dcc0", "#d0c4a4", scale=14, plane="xy", bump=0.9, wear=0.5, rim=0.5, ao=0.3)
    prism_roof("roof", prof, bl + 0.35, canvas, R, loc=(0, 0, bz + 1.32))
    for x in (-1.4, -0.7, 0.0, 0.7, 1.4):
        pts = [(x, -math.cos(math.radians(t)) * (bd / 2 + 0.14), bz + 1.32 + 0.97 * math.sin(math.radians(t))) for t in range(0, 181, 15)]
        tube("hoop", pts, 0.03, toon("#3a3640", rim=0.4), R)
    # door and window on the long side
    door(R, (-0.9, -bd / 2, bz), w=0.75, h=1.2, color="#c44b3f", frame="#f3ead0", arch=False, step=False)
    window(R, (0.8, -bd / 2, bz + 0.7), w=0.6, h=0.55, frame="#f3ead0", shutter="#c44b3f", flowers=False, curtain="#f3e4c4", light="#ffd89a")
    for k in range(3):
        box("stp", (0.8, 0.28, 0.1), WD("#a06a3e", "#85502c", scale=3), R, loc=(-0.9, -bd / 2 - 0.2 - k * 0.28, bz - 0.15 - k * 0.14))
    # wheels
    for x in (-1.15, 1.15):
        wp = pivot("wheel", (x, -bd / 2 - 0.18, 0.6), R)
        iron = toon("#3a3640", rim=0.4)
        wd_ = WD("#c4553f", "#a8452f", scale=4, along="v")
        frustum("tire", 0.62, 0.62, 0.1, iron, wp, loc=(0, 0.05, 0), rot=(RAD(90), 0, 0), seg=24, caps=(False, False))
        frustum("rim", 0.56, 0.56, 0.12, wd_, wp, loc=(0, 0.06, 0), rot=(RAD(90), 0, 0), seg=24, caps=(False, False))
        for k in range(8):
            a = k * math.pi / 4
            link_cyl("sp", (0, 0, 0), (math.cos(a) * 0.56, 0, math.sin(a) * 0.56), 0.035, wd_, wp, seg=5)
        frustum("hub", 0.12, 0.12, 0.2, iron, wp, loc=(0, 0.1, 0), rot=(RAD(90), 0, 0), seg=10)
    link_cyl("tow", (-bl / 2, 0, 0.45), (-bl / 2 - 1.3, -0.15, 0.22), 0.06, WDT(), R, seg=6)
    link_cyl("prop", (-bl / 2 - 1.1, -0.15, 0.25), (-bl / 2 - 1.1, -0.15, 0.0), 0.05, WDT(), R, seg=5)
    frustum("pipe", 0.09, 0.09, 0.9, toon("#3a3640", rim=0.4), R, loc=(1.2, 0.2, bz + 1.6), seg=8)
    frustum("pcap", 0.15, 0.09, 0.12, toon("#3a3640", rim=0.4), R, loc=(1.2, 0.2, bz + 2.5), seg=8)
    lantern2(R, (-0.1, -bd / 2 - 0.0, bz + 1.35), color="#ffb04a")
    # pen with sheep
    pw = 3.6
    fence_run(R, -pw, pw, -3.4, n=9, col="#a07a4a")
    for sx in (-1, 1):
        for k in range(4):
            y = -3.4 + k * 0.62
            box("pp", (0.1, 0.1, 0.85), WD("#a07a4a", "#85602e", scale=4), R, loc=(sx * pw, y, 0.42))
        box("pr", (0.07, 2.0, 0.08), WD("#a07a4a", "#85602e", scale=4), R, loc=(sx * pw, -2.4, 0.45))
        box("pr2", (0.07, 2.0, 0.08), WD("#a07a4a", "#85602e", scale=4), R, loc=(sx * pw, -2.4, 0.75))
    for (x, y, r_, s_) in ((-2.4, -2.5, 0.3, 1.0), (-0.5, -2.8, 3.2, 1.0), (1.6, -2.4, 0.1, 1.0), (2.6, -2.9, 3.0, 0.8), (0.4, -2.2, 0.6, 0.65)):
        sheep(R, (x, y, 0), r_, s_)
    box("trough", (1.0, 0.35, 0.28), WD("#8a5a30", "#704826", scale=3), R, loc=(-1.5, -1.6, 0.18))
    box("water", (0.9, 0.28, 0.02), glow("#6fd8d0", 0.7, alpha=0.6), R, loc=(-1.5, -1.6, 0.33))
    for i in range(5):
        ellipsoid("hay", 0.26, TH("#e0b858", "#c8a040", scale=4), R, loc=(2.4 + (i % 3) * 0.2, -1.4 - (i // 3) * 0.1, 0.18 + (i // 3) * 0.2), scale=(1.3, 1, 0.7), seg=8, rings=6)
    # crook leaning at the door
    tube("crook", [(-1.85, -1.0, 0.0), (-1.8, -1.0, 1.6), (-1.7, -1.0, 1.95), (-1.5, -1.0, 2.0), (-1.4, -1.0, 1.8)], 0.035, WDT(), R)
    bush(R, (3.4, -0.2, 0), r=0.4, seed=7, fcols=("#ffd86a", "white"))
    rocks_at(R, [(-3.2, -0.2, 0.4), (-3.6, 0.3, 0.3)], seed=3)
    truth_extras(R, cob=[(-0.2, -bd / 2 - 0.1, bz + 1.1, 0.4)], threads=[(0.6, -bd / 2 - 0.3, bz + 1.8), (-1.2, -bd / 2 - 0.3, bz + 1.9)])
    return dict(smoke=[(1.2, 0.2, bz + 2.7)])


# =============================================================== herb garden: glasshouse with a gabled porch
def herbs():
    R = pivot("herbs")
    w, d = 4.6, 3.0
    bz, gh = 0.5, 1.5
    brickm = BR("#a8603f", "#8f4f34", scale=2.4, wear=0.7, moss=0.5)
    frame = toon("#f3f0e4", rim=0.25)
    box("base", (w + 0.1, d + 0.1, bz), brickm, R, base=True)
    glassm = glow("#b8f0d8", 1.3, alpha=0.42)
    box("gwall", (w, d, gh), glassm, R, loc=(0, 0, bz), base=True)
    # inside plants
    pm = [toon("leaf1", rim=0.3), toon("leaf2", rim=0.3), toon("leaf3", rim=0.3)]
    rnd = random.Random(5)
    for i in range(14):
        x = -w / 2 + 0.4 + (i % 7) * (w - 0.8) / 6
        y = -0.4 + (i // 7) * 0.9
        h = rnd.uniform(0.8, 1.5)
        ellipsoid("pl", 0.32, pm[i % 3], R, loc=(x, y, bz + h * 0.7), scale=(1, 1, h / 0.5 * 0.5), seg=8, rings=6)
        if i % 3 == 0:
            ellipsoid("fl", 0.09, toon(["red", "gold", "#c79ae8"][i % 3 if i % 3 < 3 else 0], rim=0.3), R, loc=(x + 0.1, y - 0.2, bz + h * 1.15), seg=6, rings=4)
    # frame
    for x in np_range(-w / 2, w / 2 + 0.01, 0.46):
        box("mv", (0.05, 0.05, gh), frame, R, loc=(x, -d / 2 - 0.02, bz), base=True)
    for z in (bz, bz + 0.5, bz + 1.0, bz + gh):
        box("mh", (w + 0.05, 0.05, 0.05), frame, R, loc=(0, -d / 2 - 0.02, z))
    rz = bz + gh
    rh = 1.35
    sloped_roof("roof", w, d, rh, 0.15, glassm, R, loc=(0, 0, rz), ends=True)
    sloped_roof("roofl", w, d, rh, 0.15, toon("#f3f0e4", rim=0.2), R, loc=(0, 0, rz - 0.0), ends=False) if False else None
    D = d / 2 + 0.15
    for k in range(1, 9):   # glazing bars on the front slope
        x = -w / 2 + k * w / 9
        link_cyl("bar", (x, -D, rz), (x, 0, rz + rh), 0.025, frame, R, seg=4)
    for yy in (0.3, 0.6):
        link_cyl("barh", (-w / 2 - 0.1, -D * (1 - yy), rz + rh * yy), (w / 2 + 0.1, -D * (1 - yy), rz + rh * yy), 0.025, frame, R, seg=4)
    link_cyl("ridge", (-w / 2 - 0.1, 0, rz + rh), (w / 2 + 0.1, 0, rz + rh), 0.06, frame, R, seg=6)
    for sx in (-1, 1):
        frustum("fin", 0.04, 0.02, 0.45, toon("#3a3640", rim=0.4), R, loc=(sx * (w / 2 + 0.05), 0, rz + rh), seg=5)
        ellipsoid("finb", 0.06, toon("gold", rim=0.5), R, loc=(sx * (w / 2 + 0.05), 0, rz + rh + 0.47), seg=6, rings=4)
    # gabled porch (centre front)
    pw, pd, ph = 1.7, 0.9, 1.9
    box("pbase", (pw + 0.1, pd + 0.1, bz), brickm, R, loc=(0, -d / 2 - pd / 2 + 0.2, 0), base=True)
    box("pgl", (pw, pd, ph - bz), glassm, R, loc=(0, -d / 2 - pd / 2 + 0.2, bz), base=True)
    sloped_roof("proof", pw, pd, 0.8, 0.12, glassm, R, loc=(0, -d / 2 - pd / 2 + 0.2, ph), ends=True, ridge_x=False)
    gable_wall(R, pw + 0.2, 0.75, ph, -d / 2 - pd + 0.08, glow("#c8f4e0", 1.4, alpha=0.85))
    link_cyl("pg1", (-pw / 2 - 0.1, -d / 2 - pd + 0.06, ph), (0, -d / 2 - pd + 0.06, ph + 0.8), 0.04, frame, R, seg=5)
    link_cyl("pg2", (pw / 2 + 0.1, -d / 2 - pd + 0.06, ph), (0, -d / 2 - pd + 0.06, ph + 0.8), 0.04, frame, R, seg=5)
    yp = -d / 2 - pd + 0.17
    box("dfr", (0.95, 0.1, 1.6), frame, R, loc=(0, yp, 0.8 + bz * 0.5))
    box("dgl", (0.78, 0.05, 1.45), glow("#c8f4e0", 2.0), R, loc=(0, yp - 0.06, 0.8 + bz * 0.5))
    box("dmv", (0.05, 0.07, 1.45), frame, R, loc=(0, yp - 0.1, 0.8 + bz * 0.5))
    ellipsoid("dk", 0.05, toon("gold", rim=0.5), R, loc=(0.3, yp - 0.12, 0.85), seg=6, rings=4)
    for k in range(3):
        box("st", (1.4 + k * 0.3, 0.35, 0.1), ST("#c2bdb4", "#a7a49e", scale=3, bump=0.6), R, loc=(0, -d / 2 - pd - 0.1 - k * 0.3, 0.05))
    # garden outside
    wood = WD("#9a6238", "#7d4a2a", scale=3, bump=0.5)
    soil = toon("#4a3426", rim=0)
    hz = ["#4f9a4f", "#6cb257", "#2f6b48", "#8fb04a", "#7a5a9a", "#c79ae8"]
    for bi, (bx, by, bw) in enumerate([(-2.4, -2.5, 1.7), (2.4, -2.5, 1.7)]):
        bp = pivot("bed", (bx, by, 0), R)
        box("fr", (bw, 0.8, 0.22), wood, bp, loc=(0, 0, 0.11))
        box("so", (bw - 0.1, 0.7, 0.05), soil, bp, loc=(0, 0, 0.23))
        for k in range(16):
            x = -bw / 2 + 0.15 + (k % 8) * (bw - 0.3) / 7
            y = -0.2 + (k // 8) * 0.4
            rr = 0.1 + 0.03 * ((k * 5) % 3)
            ellipsoid("h", rr, toon(hz[(k + bi * 2) % 6], rim=0.35), bp, loc=(x, y, 0.3 + rr * 0.5), scale=(1, 1, 1.2), seg=8, rings=6)
    # trellis with beans (left side)
    for x in (-3.5, -2.1):
        frustum("tp", 0.04, 0.04, 2.0, WDT(), R, loc=(x, -1.0, 0), seg=5)
    for k in range(6):
        link_cyl("tl", (-3.5 + k * 0.28, -1.0, 0.1), (-3.4 + k * 0.28, -1.0, 1.9), 0.012, toon("#d9c9a8", rim=0), R, seg=3)
    for k in range(10):
        ellipsoid("bean", 0.1, pm[k % 3], R, loc=(-3.45 + (k % 5) * 0.32, -1.02, 0.5 + (k // 5) * 0.7 + 0.1 * (k % 3)), scale=(1.2, 0.5, 1.0), seg=6, rings=4)
    # drying rack
    for x in (2.2, 3.6):
        link_cyl("dr", (x, -1.0, 0), (x, -1.0, 1.9), 0.04, WDT(), R, seg=5)
    box("drb", (1.5, 0.06, 0.06), WDT(), R, loc=(2.9, -1.0, 1.9))
    for k in range(6):
        link_cyl("ds", (2.35 + k * 0.22, -1.0, 1.9), (2.35 + k * 0.22, -1.0, 1.65), 0.01, toon("#d9c9a8", rim=0), R, seg=3)
        ellipsoid("dh", 0.08, toon(["#6f9a3c", "#a8a04a", "#7a5a8a", "#8fb04a"][k % 4], rim=0.3), R, loc=(2.35 + k * 0.22, -1.0, 1.5), scale=(0.8, 0.8, 2.0), seg=8, rings=6)
    # rain barrel + skep
    barrel(R, (-w / 2 - 0.3, 0.7, 0), 0.32, 0.7, col="#6a8a9a")
    link_cyl("dp", (-w / 2 - 0.3, 0.7, 1.8), (-w / 2 - 0.3, 0.7, 0.72), 0.05, toon("#7a7a84", rim=0.5), R, seg=6)
    link_cyl("dp2", (-w / 2 - 0.15, 0.7, rz), (-w / 2 - 0.3, 0.7, 1.8), 0.05, toon("#7a7a84", rim=0.5), R, seg=6)
    sk = pivot("skep", (0.0, -3.4, 0), R)
    box("skst", (0.5, 0.5, 0.4), wood, sk, loc=(0, 0, 0.2))
    ellipsoid("skd", 0.3, TH("#d9b45a", "#b8903a", scale=6), sk, loc=(0, 0, 0.65), scale=(1, 1, 1.15), seg=12, rings=8)
    ellipsoid("sko", 0.05, toon("#2a1c20", rim=0), sk, loc=(0, -0.28, 0.5), seg=6, rings=4)
    truth_extras(R, cob=[(-1.3, -d / 2 - 0.1, 1.9, 0.5)], threads=[(0.0, -d / 2 - 0.5, 3.0), (1.6, -d / 2 - 0.5, 2.8)],
                 dead=[(-2.4, -2.5, 0.2, 0.55), (2.4, -2.5, 0.2, 0.55)])
    if EL.TRUTH:
        for (x, z) in ((-1.4, 1.6), (0.9, 1.3), (1.7, 1.9)):   # missing / broken panes
            box("brk", (0.4, 0.04, 0.45), toon("#141a28", rim=0), R, loc=(x, -d / 2 - 0.05, z))
            link_cyl("crk", (x - 0.2, -d / 2 - 0.08, z + 0.2), (x + 0.1, -d / 2 - 0.08, z - 0.2), 0.012, toon("#9aa6b8", rim=0), R, seg=3)
    return dict(smoke=[])


# =============================================================== fairy tree: giant hollow tree with a tiny round door
def fairy():
    R = pivot("fairy")
    bark = tex_toon("wood", "#6d4a63", "#58384f", scale=4.0, plane="xz", along="v", bump=1.4, moss=0.9, wear=0.4)
    bark2 = tex_toon("wood", "#7a5a42", "#5f4430", scale=4.0, plane="xz", along="v", bump=1.4, moss=0.7, wear=0.4)
    rr = lambda z: 1.7 - 0.115 * z
    frustum("trunk", 1.7, 1.0, 6.0, bark2, R, seg=24, scale=(1, 0.95, 1))
    for k in range(7):
        a = k * 2 * math.pi / 7 + 0.3
        ellipsoid("root", 0.7, bark2, R, loc=(math.cos(a) * 1.55, math.sin(a) * 1.45, 0.18), scale=(1.5, 0.55, 0.4), rot=(0, 0, a), seg=10, rings=6)
    # hollow above the door (dark with warm glow)
    hz = 3.6
    yh = -math.sqrt(max(0.01, rr(hz) ** 2)) + 0.05
    ellipsoid("hdark", 0.55, toon("#1a1220", rim=0), R, loc=(0, yh - 0.02, hz), scale=(0.9, 0.3, 1.3), seg=14, rings=10)
    ellipsoid("hglow", 0.4, glow("#ffb868", 3.0), R, loc=(0, yh - 0.08, hz - 0.05), scale=(0.85, 0.2, 1.2), seg=12, rings=8)
    ellipsoid("hrim", 0.62, bark, R, loc=(0, yh + 0.02, hz), scale=(0.95, 0.14, 1.4), seg=14, rings=10) if False else None
    # tiny round door
    dz = 0.62
    yd = -1.62
    dp = pivot("door", (0, yd, dz), R)
    frustum("dring", 0.46, 0.46, 0.16, ST("#a8a09a", "#8c848a", scale=4, moss=0.9), dp, loc=(0, 0.08, 0), rot=(RAD(90), 0, 0), seg=22)
    frustum("dleaf", 0.36, 0.36, 0.1, WD("#3fa890", "#2f8a76", scale=4, along="v"), dp, loc=(0, -0.05, 0), rot=(RAD(90), 0, 0), seg=22)
    box("dh", (0.5, 0.04, 0.04), toon("#2a4a46", rim=0.3), dp, loc=(0, -0.17, 0.12))
    box("dh2", (0.5, 0.04, 0.04), toon("#2a4a46", rim=0.3), dp, loc=(0, -0.17, -0.12))
    ellipsoid("dk", 0.05, toon("gold", rim=0.6), dp, loc=(0.18, -0.2, 0), seg=6, rings=4)
    ellipsoid("dlight", 0.7, glow("#6fe8c8", 0.8, alpha=0.3, soft=True), dp, loc=(0, -0.25, 0), scale=(1, 0.2, 1), seg=12, rings=8)
    for k, (x, y) in enumerate(((-0.4, -2.0), (0.1, -2.35), (-0.15, -2.7))):
        ellipsoid("stp", 0.24, ST("#a8a09a", "#8c848a", scale=3, moss=0.7, bump=0.6), R, loc=(x, y, 0.03), scale=(1.2, 0.8, 0.22), seg=10, rings=5)
    # round windows on the trunk
    for (x, z) in ((-0.75, 2.0), (0.7, 2.6), (-0.5, 4.7), (0.55, 5.1)):
        yy = -math.sqrt(max(0.05, rr(z) ** 2 - x * x)) + 0.02
        wp = pivot("win", (x, yy, z), R, rot=(0, 0, math.atan2(x, -yy) * 0.0))
        frustum("wr", 0.3, 0.3, 0.12, WD("#6a4326", "#5a3720", scale=4), wp, loc=(0, 0.06, 0), rot=(RAD(90), 0, 0), seg=16)
        frustum("wg", 0.22, 0.22, 0.08, glow("#ffd070", 3.4), wp, loc=(0, -0.05, 0), rot=(RAD(90), 0, 0), seg=16)
        box("wm", (0.44, 0.04, 0.04), toon("#3a2a1a", rim=0), wp, loc=(0, -0.1, 0))
        box("wm2", (0.04, 0.04, 0.44), toon("#3a2a1a", rim=0), wp, loc=(0, -0.1, 0))
    # bracket fungi
    for (a, z, c) in ((-35, 1.3, "#ff9ac8"), (30, 1.8, "#7fe8d0"), (-60, 3.0, "#ff9ac8"), (55, 4.0, "#7fe8d0")):
        aa = math.radians(a)
        px, py = math.sin(aa) * rr(z) * 0.98, -math.cos(aa) * rr(z) * 0.98
        ellipsoid("bf", 0.28, glow(c, 1.6), R, loc=(px, py, z), scale=(1.1, 0.7, 0.22), rot=(0, 0, -aa), seg=10, rings=6)
    # branches + canopy
    rnd = random.Random(9)
    for (a, L) in ((0.4, 1.6), (2.3, 1.7), (4.2, 1.5)):
        link_cyl("br", (math.cos(a) * 0.4, math.sin(a) * 0.4, 5.2), (math.cos(a) * 1.9, math.sin(a) * 1.5, 6.6), 0.24, bark2, R, seg=8, r2=0.1)
    gm = [tex_toon("plain", "#4fa86a", "#3a8a54", scale=3, bump=0.0, wear=0, ao=0.4),
          tex_toon("plain", "#6cc27a", "#4fa86a", scale=3, bump=0.0, wear=0, ao=0.4),
          tex_toon("plain", "#2f8a6a", "#257558", scale=3, bump=0.0, wear=0, ao=0.4)]
    for i in range(26):
        a = i * 2.4
        rad = 0.3 + math.sqrt(i / 26.0) * 2.5
        x, y = math.cos(a) * rad, math.sin(a) * rad * 0.8
        z = 6.2 + (2.8 - rad) * 0.5 + rnd.uniform(-0.2, 0.6)
        rs = rnd.uniform(0.95, 1.5)
        ellipsoid("lf", rs, gm[i % 3], R, loc=(x, y, z), scale=(1, 1, 0.85), seg=12, rings=8)
    for i in range(18):   # blossoms and fireflies
        a = rnd.uniform(0, 6.28)
        rad = rnd.uniform(1.0, 2.4)
        x, y = math.cos(a) * rad, -abs(math.sin(a)) * rad * 0.8
        z = 6.0 + rnd.uniform(0.2, 2.4)
        if i % 3 == 0:
            ellipsoid("ff", 0.07, glow("#ffe890", 5), R, loc=(x, y - 0.3, z), seg=6, rings=4)
        else:
            ellipsoid("bl", 0.1, toon(["#ffb4d8", "#f6f0e6", "#ffd86a"][i % 3], rim=0.3), R, loc=(x, y - 0.3, z), seg=6, rings=4)
    # string of tiny lanterns
    pts = [(-2.2 + 3.0 * t / 8, -1.9 - 0.1, 5.4 - 0.28 * math.sin(math.pi * t / 8)) for t in range(9)]
    tube("fl_str", pts, 0.012, toon("#3a2a1a", rim=0), R)
    for k in range(1, 8, 2):
        p_ = pts[k]
        ellipsoid("fl", 0.09, glow(["#ffc66a", "#7fe8d0"][(k // 2) % 2], 6), R, loc=(p_[0], p_[1], p_[2] - 0.12), seg=8, rings=6)
        ellipsoid("flh", 0.28, glow(["#ffc66a", "#7fe8d0"][(k // 2) % 2], 1.2, alpha=0.4, soft=True), R, loc=(p_[0], p_[1], p_[2] - 0.12), seg=8, rings=6)
    # mushroom ring
    for k in range(9):
        a = k * 2 * math.pi / 9 + 0.2
        mx, my = math.cos(a) * 2.5, math.sin(a) * 2.0 - 0.6
        s_ = rnd.uniform(0.7, 1.2)
        frustum("ms", 0.05 * s_, 0.07 * s_, 0.2 * s_, toon("#efe6d0", rim=0.3), R, loc=(mx, my, 0.0), seg=6)
        ellipsoid("mc", 0.15 * s_, toon("#c44b3f", rim=0.4), R, loc=(mx, my, 0.22 * s_), scale=(1, 1, 0.65), seg=10, rings=6)
        for j in range(3):
            ellipsoid("md", 0.026 * s_, toon("#f6f0e6", rim=0), R, loc=(mx + (j - 1) * 0.06 * s_, my - 0.1 * s_, 0.3 * s_), seg=5, rings=3)
    # tiny mailbox
    box("mbp", (0.05, 0.05, 0.5), WDT(), R, loc=(0.9, -2.5, 0), base=True)
    box("mb", (0.22, 0.16, 0.16), toon("#c44b3f", rim=0.4), R, loc=(0.9, -2.5, 0.58))
    truth_extras(R, cob=[(-0.6, -1.7, 1.4, 0.4)], threads=[(0.8, -1.2, 5.2), (-0.7, -1.3, 4.9), (1.5, -0.6, 6.0)])
    return dict(smoke=[])


# =============================================================== guild hall: old grey stone, crenellated gatehouse, banners
def guild():
    R = pivot("guild")
    w, d, wh = 6.4, 3.6, 3.2
    stone = ST("#a2a0aa", "#868490", scale=1.8, wear=0.8, moss=0.45, bump=1.0)
    light = ST("#bdbac4", "#a09ea8", scale=2.2, wear=0.6, moss=0.2)
    box("found", (w + 0.25, d + 0.25, 0.4), ST("#7a7882", "#625f6c", scale=2.2, moss=0.6), R, base=True)
    box("walls", (w, d, wh - 0.4), stone, R, loc=(0, 0, 0.4), base=True)
    for x in (-w / 2, -2.0, 2.0, w / 2):
        bx = pivot("butt", (x, -d / 2 - 0.1, 0.4), R)
        box("b1", (0.5, 0.5, 1.8), light, bx, loc=(0, 0, 0), base=True)
        box("b2", (0.42, 0.4, 1.0), light, bx, loc=(0, 0.05, 1.8), base=True)
        mesh_obj("bs", [(-0.21, -0.2, 2.8), (0.21, -0.2, 2.8), (0.21, 0.25, 2.8), (-0.21, 0.25, 2.8), (-0.21, 0.25, 3.0), (0.21, 0.25, 3.0)], [(0, 1, 5, 4)], light, bx, smooth=False) if False else None
    rz, rh, ov = wh - 0.05, 1.8, 0.4
    slate = tilesm("#4a5268", "#3a4258", scale=3.0, wear=0.7)
    sloped_roof("roof", w, d, rh, ov, slate, R, loc=(0, 0, rz), ends=True)
    ridge_cap(R, w + 0.84, rz + rh, toon("#2a3044", rim=0.4), r=0.1)
    eave_trim(R, w, d, ov, rz + 0.02, toon("#2a3044", rim=0.3), r=0.08)
    # gatehouse
    gw, gd, gh = 2.6, 1.2, 4.6
    gy = -d / 2 - gd / 2 + 0.2
    gp = pivot("gate", (0, gy, 0), R)
    box("g", (gw, gd, gh - 0.4), stone, gp, loc=(0, 0, 0.4), base=True)
    box("gf", (gw + 0.2, gd + 0.2, 0.4), ST("#7a7882", "#625f6c", scale=2.2), gp, base=True)
    box("gband", (gw + 0.12, gd + 0.12, 0.16), light, gp, loc=(0, 0, gh - 0.9))
    box("gtop", (gw + 0.4, gd + 0.4, 0.2), light, gp, loc=(0, 0, gh - 0.2))
    for k in range(7):   # merlons (front + sides)
        x = -gw / 2 - 0.1 + k * (gw + 0.2) / 6
        box("mer", (0.26, 0.26, 0.38), light, gp, loc=(x, -gd / 2 - 0.1, gh + 0.2))
    for sx in (-1, 1):
        for k in range(1, 4):
            box("mer", (0.26, 0.26, 0.38), light, gp, loc=(sx * (gw / 2 + 0.1), -gd / 2 - 0.1 + k * (gd + 0.2) / 4, gh + 0.2))
    fy = -gd / 2
    door(gp, (0, fy, 0.4), w=1.3, h=2.1, color="#5a3a22", frame="#bdbac4", step=False)
    for z in (0.9, 1.8):
        box("ib", (1.3, 0.05, 0.1), toon("#2a2630", rim=0.4), gp, loc=(0, fy - 0.16, z))
    for k in range(3):
        box("st", (2.1 + k * 0.4, 0.45, 0.12), ST("#c2bdb4", "#a7a49e", scale=3, bump=0.6), R, loc=(0, -d / 2 - gd - 0.1 - k * 0.38, 0.06))
    # emblem: gold disc with a teal thread loop
    em = pivot("emb", (0, fy - 0.03, 3.3), gp)
    frustum("ed", 0.45, 0.45, 0.08, toon("#e8b04a", rim=0.6), em, rot=(RAD(90), 0, 0), seg=24)
    frustum("ed2", 0.34, 0.34, 0.04, toon("#2a3a5a", rim=0.3), em, loc=(0, -0.07, 0), rot=(RAD(90), 0, 0), seg=24)
    tube("thr", [(math.cos(t) * 0.24, -0.11, math.sin(2 * t) * 0.14) for t in [k * 0.4 for k in range(17)]], 0.025, glow("#35d3b0", 3.0), em)
    arch_window(gp, (0, fy, 3.0), w=0.0001, h=0.0001, bars=False) if False else None
    # banners
    banner(gp, (-1.0, fy - 0.12, 3.5), 0.55, 1.5, "#a8383a", "#e8b04a")
    banner(gp, (1.0, fy - 0.12, 3.5), 0.55, 1.5, "#a8383a", "#e8b04a")
    banner(R, (-2.5, -d / 2 - 0.12, 3.0), 0.8, 1.6, "#2f7a8a", "#f3e4c4")
    banner(R, (2.5, -d / 2 - 0.12, 3.0), 0.8, 1.6, "#6a3a8a", "#e8b04a")
    for x in (-2.55, 2.55):
        arch_window(R, (x, -d / 2, 1.5), w=0.5, h=0.9, frame="#bdbac4", light="#ffd89a", glow_s=2.6)
    # flag poles on the gatehouse corners
    for sx in (-1, 1):
        frustum("fp", 0.03, 0.03, 1.8, WDT(), gp, loc=(sx * (gw / 2 + 0.05), -gd / 2 - 0.1, gh + 0.3), seg=5)
        mesh_obj("pen", [(sx * (gw / 2 + 0.05), -gd / 2 - 0.1, gh + 2.0), (sx * (gw / 2 + 0.05) + sx * 0.7, -gd / 2 - 0.1, gh + 1.8),
                         (sx * (gw / 2 + 0.05), -gd / 2 - 0.1, gh + 1.55)], [(0, 1, 2)], toon("#a8383a", rim=0.4), gp, smooth=False)
    big_lantern(R, (-1.5, -d / 2 - gd - 0.1, 0.0), 0.7, glow_s=6)
    big_lantern(R, (1.5, -d / 2 - gd - 0.1, 0.0), 0.7, glow_s=6)
    for x in (-3.5, 3.5):
        frustum("urn", 0.28, 0.2, 0.55, ST("#a8a8b0", "#86868e", scale=3), R, loc=(x, -2.4, 0), seg=10)
    plant_pot(R, (-3.4, -2.6, 0), 0.0001, 0.0001, seed=1) if False else None
    bush(R, (-3.6, -2.5, 0), r=0.3, seed=3, fcols=("#c79ae8", "white"))
    bush(R, (3.6, -2.5, 0), r=0.3, col="leaf2", seed=4)
    box("chim", (0.7, 0.7, 1.6), ST("#8a8892", "#6c6a78", scale=2.6, soot=0.8), R, loc=(2.3, 0.7, rz + 0.3), base=True)
    truth_extras(R, cob=[(-1.7, -d / 2 - 0.2, 2.3, 0.55)], threads=[(1.4, -d / 2 - 1.0, 3.9), (-0.9, -d / 2 - 1.0, 3.5)],
                 dead=[(-3.6, -2.5, 0, 0.55)], holes=[(-1.2, -0.6, dict(wh=wh, rh=rh, d=d, ov=ov, s=0.7, rz0=wh - 0.05))])
    return dict(smoke=[(2.3, 0.7, rz + 2.15)])


# =============================================================== lighthouse: banded tower, gallery, strange light
def lighthouse():
    R = pivot("lh")
    rock = ST("#8a8890", "#6c6a74", scale=2.2, wear=0.7, moss=0.6, bump=1.0)
    frustum("plinth", 2.1, 1.9, 0.7, rock, R, seg=26)
    H = 8.0
    r0, r1 = 1.55, 0.95
    n = 5
    for i in range(n):
        za, zb = 0.6 + H * i / n, 0.6 + H * (i + 1) / n
        ra, rb = r0 + (r1 - r0) * i / n, r0 + (r1 - r0) * (i + 1) / n
        c = PL("#f1ede4", "#ddd8cc", wear=0.5, moss=0.2) if i % 2 == 0 else PL("#c84a3e", "#b03c32", wear=0.6)
        frustum("seg", ra, rb, zb - za + 0.02, c, R, loc=(0, 0, za), seg=26)
    rr = lambda z: r0 + (r1 - r0) * (z - 0.6) / H
    for z in (0.6 + H / n, 0.6 + 3 * H / n):
        pass
    # gallery
    gz = 0.6 + H
    frustum("gal", 1.45, 1.45, 0.14, WD("#6a5a4a", "#544638", scale=3, plane="xy"), R, loc=(0, 0, gz), seg=26)
    frustum("galb", 1.2, 1.0, 0.25, toon("#3a3a50", rim=0.4), R, loc=(0, 0, gz - 0.2), seg=26)
    for i in range(26):
        a = 2 * math.pi * i / 26
        if math.sin(a) > 0.45:
            continue
        frustum("bp", 0.03, 0.03, 0.55, toon("#2e2a30", rim=0.4), R, loc=(math.cos(a) * 1.4, math.sin(a) * 1.4, gz + 0.14), seg=5)
    frustum("rail", 1.42, 1.42, 0.06, toon("#2e2a30", rim=0.4), R, loc=(0, 0, gz + 0.68), seg=26, caps=(False, False))
    # lantern room
    lz = gz + 0.14
    frustum("lglass", 0.82, 0.82, 1.2, glow("#fff2c8", 3.6), R, loc=(0, 0, lz), seg=20)
    for k in range(10):
        a = k * 2 * math.pi / 10
        frustum("mul", 0.04, 0.04, 1.2, toon("#2e2a30", rim=0.4), R, loc=(math.cos(a) * 0.84, math.sin(a) * 0.84, lz), seg=5)
    frustum("mulh", 0.85, 0.85, 0.05, toon("#2e2a30", rim=0.4), R, loc=(0, 0, lz + 0.6), seg=20, caps=(False, False))
    ellipsoid("core", 0.38, glow("#35d3b0", 7), R, loc=(0, -0.1, lz + 0.6), seg=12, rings=8)
    ellipsoid("lens", 0.6, glow("#c8fff0", 2), R, loc=(0, -0.2, lz + 0.62), scale=(1, 0.7, 1.1), seg=12, rings=8) if False else None
    ellipsoid("halo", 1.7, glow("#8ff0d8", 1.2, alpha=0.28, soft=True), R, loc=(0, -0.3, lz + 0.6), seg=14, rings=10)
    ellipsoid("halo2", 1.0, glow("#fff0b0", 1.4, alpha=0.4, soft=True), R, loc=(0, -0.3, lz + 0.6), seg=14, rings=10)
    frustum("lroof", 1.05, 0.0, 0.5, toon("#2f3a5a", rim=0.5), R, loc=(0, 0, lz + 1.2), seg=20, caps=(False, False))
    ellipsoid("dome", 0.7, tex_toon("plain", "#2f3a5a", "#24304c", scale=3, bump=0.2, rim=0.7, ao=0.3), R, loc=(0, 0, lz + 1.2), scale=(1, 1, 0.8), seg=20, rings=10)
    frustum("rod", 0.025, 0.012, 0.8, toon("gold", rim=0.6), R, loc=(0, 0, lz + 1.7), seg=5)
    ellipsoid("rb", 0.08, toon("gold", rim=0.6), R, loc=(0, 0, lz + 1.75), seg=8, rings=6)
    # tower door and slit windows
    door(R, (0, -rr(0.7) + 0.08, 0.6), w=0.95, h=1.6, color="#2f5a7a", frame="#e8e0d4", step=True)
    for z in (2.8, 4.4, 6.0):
        wp = pivot("win", (0, -rr(z) + 0.03, z), R)
        box("wf", (0.34, 0.1, 0.8), toon("#2e2a30", rim=0.3), wp)
        box("wg", (0.22, 0.05, 0.66), glow("#ffd89a", 3.0), wp, loc=(0, -0.06, 0))
    # keeper's cottage
    cx, cy = -3.5, -0.4
    cp = pivot("cottage", (cx, cy, 0), R)
    cw, cd, cwh = 2.8, 2.2, 1.9
    box("cf", (cw + 0.1, cd + 0.1, 0.3), rock, cp, base=True)
    box("cwalls", (cw, cd, cwh - 0.3), PL("#f1ede4", "#ddd8cc", wear=0.6, moss=0.3), cp, loc=(0, 0, 0.3), base=True)
    sloped_roof("croof", cw, cd, 1.0, 0.35, tilesm("#b04b3a", "#8f3a2c", scale=3.6), cp, loc=(0, 0, cwh - 0.05), ends=True)
    ridge_cap(cp, cw + 0.74, cwh - 0.05 + 1.0, toon("#6e2a1c", rim=0.4), r=0.09)
    door(cp, (-0.5, -cd / 2, 0.3), w=0.8, h=1.5, color="#2f5a7a", frame="#e8e0d4", step=True)
    window(cp, (0.75, -cd / 2, 1.1), w=0.6, h=0.6, frame="#e8e0d4", shutter="#c84a3e", flowers=True, curtain="#f3e4c4")
    box("cchim", (0.5, 0.5, 1.2), BR("#8a6a60", "#74564e", scale=3, soot=0.8), cp, loc=(0.9, 0.4, cwh + 0.2), base=True)
    # fence run to the tower, rocks, crates, rope
    fence_run(R, -2.2, -0.2, -1.9, n=3, col="#d8d4cc")
    rocks_at(R, [(2.2, -0.5, 0.6), (2.7, 0.3, 0.8), (1.8, 0.9, 0.5), (-2.0, 1.4, 0.6), (3.2, -1.2, 0.35), (-5.2, 0.6, 0.5)], seed=4)
    crate(R, (1.6, -2.2, 0), 0.5, RAD(12), col="#8a6238")
    barrel(R, (2.2, -2.0, 0), 0.3, 0.6, col="#6a8a9a")
    lantern2(R, (cx + 0.3, cy - cd / 2 - 0.0, 1.8))
    bush(R, (-5.4, -0.9, 0), r=0.36, col="leaf3", seed=3, fcols=("white",))
    truth_extras(R, cob=[(-0.5, -rr(2.0) - 0.1, 2.2, 0.5)], threads=[(0.4, -1.5, 5.0), (-0.5, -1.4, 3.5), (1.0, -1.0, 6.5)],
                 dead=[(-5.4, -0.9, 0, 0.5)])
    return dict(smoke=[(cx + 0.9, cy + 0.4, cwh + 1.6)])


# =============================================================== the great tower: locked dark keep, spire, chained gate
def great_tower():
    R = pivot("gt")
    dark = ST("#5c5672", "#463f5c", scale=2.0, wear=0.8, moss=0.15, bump=1.1)
    dark2 = ST("#6a6482", "#524b6c", scale=2.2, wear=0.6, bump=1.0)
    trim = PL("#8a82a8", "#6e6690", wear=0.4)
    s = 5.2
    for k in range(3):
        box("pst", (s + 1.2 - k * 0.3, s + 1.2 - k * 0.3, 0.25), ST("#6a6482", "#524b6c", scale=2.4), R, loc=(0, 0, 0.125 + k * 0.25), base=False)
    box("keep", (s, s, 6.0), dark, R, loc=(0, 0, 0.75), base=True)
    for z in (2.6, 4.6):
        box("kb", (s + 0.14, s + 0.14, 0.18), trim, R, loc=(0, 0, z))
    for x in (-s / 2, s / 2):    # pilasters
        box("pil", (0.4, 0.4, 6.0), dark2, R, loc=(x, -s / 2 - 0.1, 0.75), base=True)
    box("cor", (s + 0.5, s + 0.5, 0.35), trim, R, loc=(0, 0, 6.8))
    for i in range(10):   # corbels
        box("cb", (0.3, 0.3, 0.3), dark2, R, loc=(-s / 2 + 0.3 + i * (s - 0.6) / 9, -s / 2 - 0.2, 6.5))
    ub = 3.8
    box("upper", (ub, ub, 3.0), dark, R, loc=(0, 0, 6.9), base=True)
    box("ucor", (ub + 0.4, ub + 0.4, 0.28), trim, R, loc=(0, 0, 9.9))
    # corner turrets on the lower keep
    for sx in (-1, 1):
        for sy in (-1, 1):
            tx, ty = sx * (s / 2 + 0.05), sy * (s / 2 + 0.05)
            frustum("tur", 0.62, 0.55, 7.8, dark2, R, loc=(tx, ty, 0.75), seg=14)
            frustum("tcone", 0.8, 0.0, 1.9, tilesm("#2c2742", "#221e38", scale=2.8, wear=0.8), R, loc=(tx, ty, 8.45), seg=14, caps=(False, False))
            ellipsoid("tf", 0.07, toon("#b8b4d0", rim=0.7), R, loc=(tx, ty, 10.4), seg=8, rings=6)
    # spire
    spm = tilesm("#2c2742", "#221e38", scale=2.6, wear=0.8)
    frustum("spire", 2.9, 0.0, 4.6, spm, R, loc=(0, 0, 9.85), seg=24, caps=(False, False))
    frustum("seave", 2.95, 2.95, 0.16, toon("#1c1830", rim=0.4), R, loc=(0, 0, 9.85), seg=24)
    link_cyl("ant", (0, 0, 14.3), (0, 0, 15.4), 0.04, toon("#b8b4d0", rim=0.7), R, seg=6)
    ellipsoid("orb", 0.2, glow("#b8a0ff", 4), R, loc=(0, 0, 15.5), seg=10, rings=8)
    ellipsoid("orbh", 0.7, glow("#b8a0ff", 1.2, alpha=0.3, soft=True), R, loc=(0, 0, 15.5), seg=10, rings=8)
    # the gate: tall arch, iron-banded double door, chains and a padlock
    gz = 0.75
    box("gfr", (2.5, 0.35, 3.5), dark2, R, loc=(0, -s / 2 - 0.02, gz + 1.75))
    frustum("garch", 1.25, 1.25, 0.35, dark2, R, loc=(0, -s / 2 + 0.15, gz + 3.5), rot=(RAD(90), 0, 0), seg=22)
    box("gdoor", (1.9, 0.14, 3.3), toon("#26222e", rim=0.3), R, loc=(0, -s / 2 - 0.2, gz + 1.65))
    frustum("gdarch", 0.95, 0.95, 0.14, toon("#26222e", rim=0.3), R, loc=(0, -s / 2 - 0.12, gz + 3.3), rot=(RAD(90), 0, 0), seg=18)
    for z in (0.6, 1.5, 2.4, 3.1):
        box("band", (1.9, 0.08, 0.14), toon("#4a465a", rim=0.5), R, loc=(0, -s / 2 - 0.3, gz + z))
    box("gsplit", (0.05, 0.08, 3.3), toon("#4a465a", rim=0.5), R, loc=(0, -s / 2 - 0.3, gz + 1.65))
    ch = toon("#6a6880", rim=0.6)
    for a in (-1, 1):
        n_ = 10
        for i in range(n_):
            t = i / (n_ - 1)
            x = -0.85 + 1.7 * t
            z = gz + 1.65 + a * (-1.0 + 2.0 * t) * 0.9 + 0.0
            ellipsoid("link", 0.12, ch, R, loc=(x, -s / 2 - 0.4, z), scale=(1.0, 0.35, 0.55), rot=(0, a * RAD(-30) * (1 if i % 2 else -1) + (0.8 * a), 0), seg=8, rings=5)
    pl = pivot("lock", (0, -s / 2 - 0.45, gz + 1.3), R)
    box("lb", (0.55, 0.2, 0.5), toon("#8a7a4a", rim=0.7), pl, loc=(0, 0, -0.1))
    tube("shackle", [(math.cos(t) * 0.19, 0, 0.15 + math.sin(t) * 0.26) for t in [math.pi * k / 10 for k in range(11)]], 0.045, toon("#8a8a9a", rim=0.7), pl)
    box("kh", (0.06, 0.04, 0.16), toon("#1a1620", rim=0), pl, loc=(0, -0.11, -0.08))
    ellipsoid("khc", 0.06, toon("#1a1620", rim=0), pl, loc=(0, -0.11, -0.02), scale=(1, 0.3, 1), seg=8, rings=6)
    # windows (dim violet) + oculus
    for (x, z) in ((-1.5, 3.6), (1.5, 3.6), (-1.5, 5.3), (1.5, 5.3)):
        arch_window(R, (x, -s / 2, z), w=0.34, h=0.9, frame="#8a82a8", light="#9a80e0", glow_s=2.2, bars=False)
    for x in (-1.0, 0.0, 1.0):
        arch_window(R, (x, -ub / 2, 8.0), w=0.3, h=0.8, frame="#8a82a8", light="#9a80e0", glow_s=2.0, bars=False)
    oc = pivot("oculus", (0, -s / 2 - 0.02, 5.5), R)
    frustum("or", 0.62, 0.62, 0.14, trim, oc, rot=(RAD(90), 0, 0), seg=24)
    frustum("og", 0.5, 0.5, 0.08, glow("#e8c070", 2.2), oc, loc=(0, -0.1, 0), rot=(RAD(90), 0, 0), seg=24)
    ellipsoid("oi", 0.2, toon("#1c1830", rim=0), oc, loc=(0, -0.16, 0), scale=(1, 0.3, 1.0), seg=10, rings=8)
    # braziers with cold violet flames
    for sx in (-1, 1):
        bp = pivot("brz", (sx * 2.2, -s / 2 - 1.2, 0), R)
        frustum("bst", 0.14, 0.1, 1.0, toon("#2a2630", rim=0.4), bp, seg=8)
        frustum("bwl", 0.34, 0.14, 0.3, toon("#2a2630", rim=0.4), bp, loc=(0, 0, 1.0), seg=10)
        flame(bp, (0, 0, 1.25), 1.0, color="#9a70ff")
    for k in range(4):
        box("st", (3.0 + k * 0.4, 0.5, 0.14), ST("#6a6482", "#524b6c", scale=2.4), R, loc=(0, -s / 2 - 0.5 - k * 0.4, 0.07))
    # faint teal veins climbing the stone
    for (x0, z0) in ((-2.0, 1.2), (1.9, 2.0), (-0.9, 6.9)):
        pts = [(x0 + 0.15 * math.sin(t * 1.3), -s / 2 - 0.03, z0 + t * 0.35) for t in range(10)]
        tube("vein", pts, 0.018, glow("#35d3b0", 2.4), R)
    rocks_at(R, [(-3.7, -2.2, 0.4), (3.8, -2.0, 0.45), (-4.2, 0.5, 0.5)], col="#6a6482", seed=7)
    truth_extras(R, cob=[(-1.7, -s / 2 - 0.2, 2.6, 0.6)], threads=[(1.0, -s / 2 - 0.5, 5.2), (-1.4, -s / 2 - 0.5, 4.2), (2.0, -s / 2 - 0.5, 3.0)])
    return dict(smoke=[])


BUILDERS = {"stories": stories, "farm": farm, "shepherd": shepherd, "herbs": herbs, "fairy": fairy,
            "guild": guild, "lighthouse": lighthouse, "great_tower": great_tower}
