"""World-2 interior objects, part C: shepherd, herbs, fairy, guild, lighthouse."""
import math
import random

from iw2_lib import *  # noqa
from iw2_objs_a import fire, steam, mug, plate, b_stairs, b_rope_coil
from iw2_objs_b import clock_face, BRASS


# ==================================================================== SHEPHERD
def sh_window(R):
    w, h = 1.4, 1.5
    fm = WD("#6a4a30", "#54382a", scale=3, bump=0.8)
    # view: dusk sky, a green hill with a bare finger-shaped patch
    box("sk", (w, 0.05, h), glow("#ffb080" if not T() else "#4a5a82", 1.3 if not T() else 0.7), R, loc=(0, -0.08, h / 2 + 0.05))
    box("sk2", (w, 0.052, h * 0.4), glow("#8a5a9a" if not T() else "#33406a", 1.1 if not T() else 0.6), R, loc=(0, -0.085, h * 0.8 + 0.05))
    ellipsoid("hl", 1.0, toon("#4f8a4f" if not T() else "#4a5a44", rim=0.2), R, loc=(0.1, -0.1, 0.1), scale=(1.1, 0.06, 0.5), seg=16, rings=8)
    ellipsoid("hl2", 0.7, toon("#3a7a42" if not T() else "#3e4e3e", rim=0.2), R, loc=(-0.5, -0.11, 0.1), scale=(1.2, 0.06, 0.45), seg=14, rings=8)
    # the bare patch: elongated rounded finger with a knuckle line
    pc = "#d8c89a" if not T() else "#7a7a84"
    ellipsoid("pa", 0.1, toon(pc, rim=0), R, loc=(0.3, -0.13, 0.38), scale=(0.7, 0.05, 2.0), rot=(0, RAD(-12), 0), seg=10, rings=8)
    ellipsoid("pa2", 0.07, toon(pc, rim=0), R, loc=(0.38, -0.131, 0.58), scale=(0.7, 0.05, 1.3), rot=(0, RAD(-12), 0), seg=8, rings=6)
    link_cyl("kn", (0.24, -0.14, 0.32), (0.34, -0.14, 0.34), 0.005, toon("#a89870", rim=0), R, seg=3)
    # frame, mullions, sill, shutters
    for s in (-1, 1):
        box("fv", (0.14, 0.12, h + 0.2), fm, R, loc=(s * (w / 2 + 0.05), -0.06, h / 2 + 0.05))
    box("ft", (w + 0.3, 0.12, 0.14), fm, R, loc=(0, -0.06, h + 0.1))
    box("fb", (w + 0.5, 0.3, 0.1), fm, R, loc=(0, -0.12, -0.05))
    box("mv", (0.05, 0.08, h), fm, R, loc=(0, -0.14, h / 2 + 0.05))
    box("mh", (w, 0.08, 0.05), fm, R, loc=(0, -0.14, h * 0.55))
    if T():
        tthread(R, [(0.3, -0.16, 0.4), (0.33, -0.16, 1.0), (0.5, -0.2, 1.8), (0.9, -0.3, 2.8)], 0.012, 3.2)
        halo(R, (0.34, -0.15, 0.5), 0.45, 0.25)
        crack_fx(R, (-0.4, -0.15, h), 0.7)
    else:
        flower_box(R, (0, -0.28, -0.0), 1.2, seed=4)
    return {}


def sh_names(R):
    box("bd", (2.2, 0.08, 0.9), WD("#6a4a30", "#54382a", scale=3), R, loc=(0, -0.04, 0.45))
    box("bd2", (2.0, 0.05, 0.7), WD("#8a6a48", "#6a4a30", scale=3, along="v"), R, loc=(0, -0.09, 0.45))
    # 8 hooks with round name tags (carved dots) and a slack thread each
    for k in range(8):
        x = -0.88 + k * 0.25
        ellipsoid("hk", 0.03, toon("gold", rim=0.5), R, loc=(x, -0.12, 0.72), seg=6, rings=4)
        if k == 7:
            tube("fr", [(x, -0.12, 0.72), (x + 0.02, -0.14, 0.5)], 0.008, toon("#d9c9a8", rim=0) if not T() else glow(TEAL, 2.8), R)
            continue
        tube("st", [(x, -0.12, 0.72), (x, -0.13, 0.58)], 0.008, toon("#d9c9a8", rim=0), R)
        frustum("tg", 0.085, 0.085, 0.02, WD(["#d9b05a", "#c9a06a", "#e8d6a0"][k % 3], "#a88a5a", scale=5), R, loc=(x, -0.14, 0.5), rot=(RAD(90), 0, 0), seg=14)
        for j in range((k % 3) + 1):
            ellipsoid("dt", 0.016, toon("#3a2a22", rim=0), R, loc=(x - 0.03 + j * 0.03, -0.17, 0.5), seg=5, rings=4)
        # slack thread dangling from each tag
        sc = glow(TEAL, 2.8) if T() else toon("#c9b48a", rim=0)
        tube("sl", [(x, -0.15, 0.42), (x + 0.04 * math.sin(k), -0.16, 0.3), (x - 0.02, -0.17, 0.18 + 0.02 * (k % 3))], 0.008, sc, R)
    if T():
        halo(R, (0, -0.2, 0.4), 1.1, 0.12)
        cobweb(R, (-1.05, -0.1, 0.9), 0.3)
    return {}


def sh_flute(R):
    # wooden flute hanging on two pegs with a ribbon
    box("pg", (0.06, 0.12, 0.06), toon("wood_d", rim=0), R, loc=(-0.45, -0.06, 0.1))
    box("pg", (0.06, 0.12, 0.06), toon("wood_d", rim=0), R, loc=(0.45, -0.06, 0.1))
    link_cyl("fl", (-0.6, -0.14, 0.05), (0.6, -0.14, 0.1), 0.04, tex_toon("wood", "#c9a06a", "#a8804a", scale=8, plane="xz", bump=0.5, rim=0.5), R, seg=10)
    for k in range(6):
        ellipsoid("ho", 0.015, toon("#2a1e1a", rim=0), R, loc=(-0.15 + k * 0.12, -0.185, 0.07 + k * 0.004), seg=5, rings=4)
    ellipsoid("mp", 0.03, toon("#a06a3e", rim=0.5), R, loc=(-0.55, -0.15, 0.06), seg=6, rings=4)
    tube("rb", [(-0.6, -0.14, 0.05), (-0.7, -0.16, -0.25), (-0.62, -0.17, -0.5)], 0.03, toon("#4f7ad8", rim=0.3), R)
    tube("rb2", [(0.6, -0.14, 0.1), (0.7, -0.16, -0.2), (0.64, -0.17, -0.42)], 0.03, toon("#c44b3f", rim=0.3), R)
    if T():
        # blue sound-waves leave the flute and sink into the thread
        for k, rr in enumerate((0.2, 0.32, 0.44, 0.56)):
            pts = [(math.cos(t) * rr * 0.6, -0.2 - 0.04 * k, math.sin(t) * rr + 0.4) for t in [-1.1 + i * 0.28 for i in range(9)]]
            tube("wv", [(p[0] + 0.55, p[1], p[2] - 0.35) for p in pts], 0.012, glow(BLUE, 3.4 - k * 0.5), R)
        tthread(R, [(0.5, -0.2, 0.1), (0.9, -0.3, 0.5), (1.4, -0.3, 1.0), (1.9, -0.3, 1.2)], 0.01, 2.8)
        halo(R, (0.9, -0.3, 0.4), 0.7, 0.15, BLUE)
    return {}


def sh_bed(R):
    wd = WD("#8a6a48", "#6a4a30", scale=3, bump=0.8)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box("lg", (0.1, 0.1, 0.3), WDT(), R, loc=(sx * 1.0, sy * 0.42, 0), base=True)
    box("fr", (2.2, 0.95, 0.12), wd, R, loc=(0, 0, 0.3))
    box("hd", (0.1, 0.95, 0.55), wd, R, loc=(-1.1, 0, 0.3), base=True)
    box("ft", (0.1, 0.95, 0.35), wd, R, loc=(1.1, 0, 0.3), base=True)
    box("st", (2.0, 0.82, 0.18), tex_toon("thatch", "#d2a24e", "#b38238", scale=6, plane="xy", bump=1.0), R, loc=(0, 0, 0.42), bevel=0.05)
    box("bl", (1.2, 0.84, 0.08), FAB("stripes", "#f3e4c4", "#c9b48a", scale=5, plane="xy", bump=0.9), R, loc=(0.4, 0, 0.56), bevel=0.03)
    ellipsoid("pi", 0.3, FAB("weave", "#f3f0e4", "#dfd8c4", scale=14), R, loc=(-0.72, 0, 0.62), scale=(1.0, 1.4, 0.45), seg=12, rings=8)
    if T():
        # three little lines on the pillow, all pointing up
        for k in range(3):
            tthread(R, [(-0.8 + k * 0.1, -0.1, 0.68), (-0.78 + k * 0.1, -0.1, 0.9), (-0.7 + k * 0.1, -0.1, 1.3)], 0.01, 3.2)
        halo(R, (-0.7, -0.1, 0.8), 0.5, 0.2)
        cobweb(R, (-1.0, 0.4, 0.9), 0.35)
    return {}


def sh_blanket(R):
    chest(R, (0, 0, 0), 1.3, 0.7, 0.55, "#7a4a2a", "#3a2a22")
    # a folded wool blanket on top with a glowing knot
    box("bl", (1.0, 0.55, 0.14), FAB("stripes", "#c44b3f", "#f3e4c4", scale=5, plane="xy", bump=1.0), R, loc=(0, 0, 0.6), bevel=0.04, rot=(0, 0, RAD(3)))
    box("bl2", (0.95, 0.5, 0.1), FAB("knit", "#4f7ad8", "#f3e4c4", scale=12, plane="xy"), R, loc=(0.05, 0, 0.72), bevel=0.04)
    if T():
        weaver_knot(R, (0.3, -0.3, 0.7), 0.07)
    else:
        ellipsoid("kn", 0.05, glow("#fff3c8", 1.0), R, loc=(0.3, -0.3, 0.7), seg=8, rings=6)
        for s in (-1, 1):
            tube("tl", [(0.3, -0.3, 0.7), (0.35 + s * 0.1, -0.35, 0.6), (0.4 + s * 0.12, -0.4, 0.5)], 0.015, toon("#f3e4c4", rim=0.2), R)
    if T():
        tthread(R, [(0.3, -0.3, 0.75), (0.3, -0.32, 1.5), (0.4, -0.3, 2.6), (0.6, -0.3, 3.8)], 0.01, 3.0)
        halo(R, (0.3, -0.3, 0.7), 0.4, 0.3)
        cobweb(R, (-0.6, 0.2, 0.9), 0.3)
    return {}


def sh_stove(R):
    iron = toon("#2a2a30", rim=0.6)
    frustum("bd", 0.32, 0.32, 0.8, iron, R, loc=(0, 0, 0.14), seg=14)
    for k in range(3):
        a = k * 2.094 + 0.5
        link_cyl("lg", (math.cos(a) * 0.2, math.sin(a) * 0.2, 0.14), (math.cos(a) * 0.3, math.sin(a) * 0.3, 0.0), 0.03, iron, R, seg=5)
    frustum("pipe", 0.07, 0.07, 1.8, iron, R, loc=(0, 0, 0.9), seg=8)
    box("dr", (0.22, 0.02, 0.25), glow("#ff8a2a", 3) if not T() else toon("#1a1a20", rim=0), R, loc=(0, -0.32, 0.45))
    ellipsoid("pt", 0.16, toon("#4a5a6a", rim=0.7), R, loc=(0, 0, 1.08), scale=(1, 1, 0.8), seg=10, rings=8)
    if not T():
        steam(R, (0, 0, 1.25), 3, 0.5)
    else:
        cobweb(R, (0.25, 0.1, 1.9), 0.3)


def sh_wool_bales(R):
    for k, (x, y, z) in enumerate(((-0.35, 0.0, 0.0), (0.3, 0.05, 0.0), (-0.05, 0.0, 0.52))):
        box("bl", (0.62, 0.5, 0.5), FAB("knit", "#f6f0e6" if not T() else "#bfc2cc", "#e6dcc6", scale=9, bump=1.2, plane="xz"), R, loc=(x, y, z), base=True, bevel=0.12)
        for zz in (0.15, 0.38):
            box("bd", (0.66, 0.54, 0.035), toon("#8a5a30", rim=0.3), R, loc=(x, y, z + zz))
    ellipsoid("tuft", 0.14, FAB("knit", "#f6f0e6", "#e6dcc6", scale=9, bump=1.2), R, loc=(0.35, -0.3, 0.1), scale=(1.4, 1, 0.5), seg=8, rings=6)
    if T():
        cobweb(R, (-0.5, 0.2, 1.0), 0.3)


def sh_staff_rack(R):
    frustum("ft", 0.28, 0.28, 0.07, WDT(), R, seg=10)
    for k, (dx, a) in enumerate(((-0.15, 10), (0.1, -8))):
        p = pivot("stf", (dx, 0, 0.05), R, rot=(0, RAD(a), 0))
        link_cyl("st", (0, 0, 0), (0, 0, 2.0), 0.035, WD("#8a5a30", "#6a4220", scale=6, along="v"), p, seg=6)
        tube("cr", [(0, 0, 2.0), (0.05, 0, 2.22), (0.22, 0, 2.28), (0.3, 0, 2.12)], 0.035, WD("#8a5a30", "#6a4220", scale=6), p)
    box("bd", (0.5, 0.3, 0.05), WDT(), R, loc=(0, 0, 0.45))
    if T():
        cobweb(R, (0.0, 0.0, 2.0), 0.4)


def sh_table(R):
    table(R, (0, 0, 0), 1.2, 0.8, 0.8, "#a68a62", "#6a4a30")
    frustum("bw", 0.14, 0.09, 0.1, toon("#c0693f", rim=0.4), R, loc=(-0.2, 0.0, 0.84), seg=12)
    frustum("lf", 0.12, 0.12, 0.08, toon("#c98a3c", rim=0.4), R, loc=(0.1, 0.1, 0.84), seg=8)
    candle(R, (0.4, -0.1, 0.84), 0.16, not T())
    stool_round(R, (0.0, -0.75, 0.0), 0.25, 0.46)
    if T():
        cobweb(R, (-0.5, 0.3, 0.9), 0.3)


def sh_hay(R):
    tx = tex_toon("thatch", "#d2a24e", "#b38238", scale=6, plane="xy", bump=1.0)
    ellipsoid("hy", 0.7, tx, R, loc=(0, 0, 0.1), scale=(1.1, 0.85, 0.7), seg=12, rings=8)
    ellipsoid("hy2", 0.45, tx, R, loc=(0.35, -0.2, 0.2), scale=(1, 0.9, 0.7), seg=10, rings=6)
    frustum("bk", 0.16, 0.12, 0.26, WD("#8a5a30", "#6a4220", scale=5, along="v"), R, loc=(-0.65, -0.4, 0), seg=10)
    tube("hd", [(-0.8, -0.4, 0.25), (-0.65, -0.4, 0.5), (-0.5, -0.4, 0.25)], 0.012, toon("#3a3a44", rim=0.5), R)
    if T():
        cobweb(R, (-0.3, 0.1, 0.8), 0.3)


# ==================================================================== HERBS
def arch_door(R, w, h, col, open_=False, rich=False, frame="#f3f0e4"):
    fm = ST("#b9b0a2", "#9a9288", plane="xz", scale=3, bump=0.8, wear=0.4)
    box("fl", (w + 0.3, 0.12, h - w / 2), fm, R, loc=(0, -0.03, 0), base=True)
    frustum("fa", (w + 0.3) / 2, (w + 0.3) / 2, 0.12, fm, R, loc=(0, 0.03, h - w / 2), rot=(RAD(90), 0, 0), seg=20)
    # dark opening
    box("op", (w - 0.1, 0.03, h - w / 2), toon("#1a1620" if not open_ else "#e8d890", rim=0), R, loc=(0, -0.1, 0), base=True)
    frustum("oa", (w - 0.1) / 2, (w - 0.1) / 2, 0.03, toon("#1a1620" if not open_ else "#e8d890", rim=0), R, loc=(0, -0.07, h - w / 2), rot=(RAD(90), 0, 0), seg=18)
    dm = WD(col, col, scale=3, along="v", bump=0.8)
    if not open_:
        box("lf", (w - 0.14, 0.08, h - w / 2), dm, R, loc=(0, -0.17, 0), base=True)
        frustum("la", (w - 0.14) / 2, (w - 0.14) / 2, 0.08, dm, R, loc=(0, -0.13, h - w / 2), rot=(RAD(90), 0, 0), seg=18)
        for z in (0.4, 1.3):
            box("hg", (w - 0.14, 0.04, 0.07), toon("#2a2a30", rim=0.6), R, loc=(0, -0.23, z))
    else:
        # leaf swung open to the left: seen edge-on as a slim plank with a perspective skew
        box("lf", (0.08, 0.7, h - w / 2), dm, R, loc=(-w / 2 - 0.1, -0.5, 0), base=True, rot=(0, 0, RAD(-25)))
        glw = glow("#fff0b0" if not T() else "#4a5a6a", 1.2 if not T() else 0.4, alpha=0.8)
        box("lt", (w - 0.2, 0.03, h - w / 2 - 0.2), glw, R, loc=(0, -0.115, 0.1), base=True)
    return fm


def h_room1(R):
    arch_door(R, 1.5, 2.6, "#4f9a7a", open_=True)
    ellipsoid("kn", 0.04, toon("gold", rim=0.5), R, loc=(0.6, -0.3, 1.1), seg=6, rings=4)
    box("pl", (0.5, 0.03, 0.2), toon("#f6efe0", rim=0.2), R, loc=(0, -0.2, 2.95))
    for k in range(3):
        ellipsoid("dt", 0.02, toon("#3a2a22", rim=0), R, loc=(-0.1 + k * 0.1, -0.22, 2.95), seg=5, rings=4)
    if T():
        # many open threads fan out from the threshold in every direction
        for k in range(11):
            a = -1.4 + k * 0.28
            tthread(R, [(0.0, -0.1, 1.0), (math.sin(a) * 0.7, -0.4, 1.0 + math.cos(a) * 0.9), (math.sin(a) * 1.4, -0.7, 1.0 + math.cos(a) * 1.6)], 0.008, 2.8)
        halo(R, (0, -0.2, 1.2), 1.1, 0.14)
        cobweb(R, (-0.8, -0.2, 2.6), 0.4)
    return {}


def h_room2(R):
    arch_door(R, 1.5, 2.6, "#7a4a2a")
    box("lk", (0.2, 0.06, 0.26), toon("#b9b0a2", rim=0.8), R, loc=(0.45, -0.24, 1.1))
    ellipsoid("kh", 0.03, toon("#1a1620", rim=0), R, loc=(0.45, -0.28, 1.08), scale=(1, 0.3, 1.4), seg=5, rings=4)
    # key on a hook beside the door
    box("hk", (0.06, 0.1, 0.06), toon("wood_d", rim=0), R, loc=(1.0, -0.1, 1.6))
    key_obj(R, (1.0, -0.16, 1.5), "gold", 0.34)
    # cabinet beside it
    box("cb", (0.6, 0.3, 1.1), WD("#6a4630", "#553622", scale=3), R, loc=(1.6, -0.15, 0.0), base=True)
    box("cd", (0.5, 0.03, 0.9), WD("#7a5638", "#6a4830", scale=4), R, loc=(1.6, -0.31, 0.1), base=True)
    ellipsoid("ck", 0.03, toon("gold", rim=0.5), R, loc=(1.45, -0.34, 0.6), seg=5, rings=4)
    box("pl", (0.5, 0.03, 0.2), toon("#f6efe0", rim=0.2), R, loc=(0, -0.2, 2.95))
    if T():
        # blue thread: key -> lock -> cabinet
        tthread(R, [(1.0, -0.2, 1.5), (0.8, -0.3, 1.2), (0.45, -0.3, 1.1)], 0.012, 3.4)
        tthread(R, [(0.45, -0.3, 1.1), (0.7, -0.33, 0.6), (1.3, -0.36, 0.55), (1.45, -0.36, 0.6)], 0.012, 3.4)
        halo(R, (0.9, -0.3, 1.0), 0.8, 0.18)
        cobweb(R, (-0.8, -0.2, 2.6), 0.4)
    return {}


def h_room3(R):
    arch_door(R, 1.5, 2.6, "#2f4a7a")
    # big ornate handle + gold boss + plaque
    ellipsoid("bs", 0.1, toon("gold", rim=0.7), R, loc=(0.45, -0.25, 1.2), scale=(1, 0.4, 1), seg=10, rings=6)
    link_cyl("hd", (0.45, -0.28, 1.0), (0.45, -0.28, 1.4), 0.03, toon("gold", rim=0.7), R, seg=6)
    for s in (-1, 1):
        ellipsoid("rv", 0.04, toon("gold", rim=0.7), R, loc=(s * 0.4, -0.2, 2.1), scale=(1, 0.4, 1), seg=6, rings=4)
    box("pl", (0.7, 0.04, 0.25), toon("gold", rim=0.6), R, loc=(0, -0.2, 2.95))
    for k in range(2):
        ellipsoid("st", 0.05, toon("#c44b3f", rim=0.4), R, loc=(-0.15 + k * 0.3, -0.23, 2.95), scale=(1, 0.3, 1), seg=6, rings=4)
    if T():
        # a doubled thread is knotted round the handle (replaced by someone)
        for dz in (0.0, 0.05):
            tthread(R, [(0.45, -0.33, 1.4 + dz), (0.55, -0.35, 1.2), (0.45, -0.33, 1.0 + dz), (0.35, -0.35, 1.2), (0.45, -0.33, 1.4 + dz)], 0.012, 3.4)
        tthread(R, [(0.45, -0.33, 1.4), (0.5, -0.4, 2.0), (0.6, -0.4, 3.2)], 0.012, 3.0)
        halo(R, (0.45, -0.33, 1.2), 0.45, 0.28)
        cobweb(R, (-0.8, -0.2, 2.6), 0.4)
    return {}


def h_pot(R):
    p = pot_clay(R, (0, 0, 0), 0.42, 0.5, "#c0693f")
    frustum("so", 0.38, 0.38, 0.03, toon("#3a2a20", rim=0), R, loc=(0, 0, 0.5), seg=14)
    rnd = random.Random(5)
    for k in range(14):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.05, 0.3)
        x, y = math.cos(a) * r, math.sin(a) * r * 0.8
        hh = rnd.uniform(0.25, 0.55)
        link_cyl("sm", (x, y, 0.5), (x * 1.1, y * 1.1, 0.5 + hh), 0.01, toon("#2f6b48" if not T() else "#5a4c3c", rim=0), R, seg=3)
        if T():
            ellipsoid("fl", 0.055, toon("#1a1a22", rim=0.2), R, loc=(x * 1.1, y * 1.1, 0.5 + hh), seg=8, rings=5)
        else:
            ellipsoid("fl", 0.055, toon("#6a9af8", rim=0.3), R, loc=(x * 1.1, y * 1.1, 0.5 + hh), seg=8, rings=5)
            ellipsoid("ct", 0.02, toon("#ffe08a", rim=0), R, loc=(x * 1.1, y * 1.1 - 0.04, 0.5 + hh + 0.01), seg=5, rings=4)
        ellipsoid("lf", 0.07, toon("leaf1" if not T() else "#4a4236", rim=0.3), R, loc=(x, y, 0.55 + hh * 0.4), scale=(1, 0.4, 1.3), rot=(0, 0, a), seg=6, rings=4)
    if T():
        # a blue thread under the soil, the folded paper wrapped in it
        box("pp", (0.2, 0.14, 0.04), toon("#e8d8b0", rim=0), R, loc=(0.2, -0.38, 0.46), rot=(0, 0, RAD(20)))
        tthread(R, [(0.12, -0.34, 0.5), (0.2, -0.4, 0.47), (0.3, -0.4, 0.44), (0.35, -0.34, 0.48)], 0.012, 3.4)
        tthread(R, [(0.2, -0.38, 0.45), (0.25, -0.45, 0.45)], 0.01, 3.4)
        halo(R, (0.2, -0.38, 0.5), 0.5, 0.3)
        cobweb(R, (-0.4, 0.0, 0.9), 0.3)
    return {}


def h_labels(R):
    stool_round(R, (0, 0, 0), 0.34, 0.5, "#8a5a30")
    box("tr", (0.8, 0.5, 0.1), WD("#9a6a3e", "#7a4e2a", scale=4), R, loc=(0, 0, 0.56))
    box("in", (0.72, 0.42, 0.02), toon("#3a2a20", rim=0), R, loc=(0, 0, 0.62))
    for k in range(9):
        x = -0.3 + (k % 5) * 0.15
        y = -0.12 + (k // 5) * 0.2
        blank = (k == 4)
        link_cyl("sk", (x, y, 0.62), (x + 0.02, y, 0.95), 0.012, WD("#c9a06a", "#a8804a", scale=6), R, seg=4)
        c = glow(TEAL, 3.4) if (blank and T()) else toon("#f6efe0", rim=0.3)
        box("lb", (0.1, 0.012, 0.12), c, R, loc=(x + 0.02, y - 0.02, 0.98 + (0.02 if blank else 0)), rot=(0, 0, RAD(k * 5 - 12)))
        if not blank:
            box("tx", (0.06, 0.012, 0.012), toon("#3a2a22", rim=0), R, loc=(x + 0.02, y - 0.03, 0.99), rot=(0, 0, RAD(k * 5 - 12)))
    if T():
        halo(R, (0.0, -0.1, 1.0), 0.5, 0.25)
        cobweb(R, (0.35, 0.2, 1.1), 0.25)
    return {}


def h_herb_rack(R):
    wd = WDT()
    for s in (-1, 1):
        link_cyl("lg", (s * 1.1, -0.1, 0), (s * 1.1, 0.0, 2.0), 0.05, wd, R, seg=5)
        link_cyl("lg", (s * 1.1, 0.1, 0), (s * 1.1, 0.0, 2.0), 0.05, wd, R, seg=5)
    for z in (1.95, 1.2):
        link_cyl("bar", (-1.15, 0, z), (1.15, 0, z), 0.04, wd, R, seg=6)
    cols = ["#6f9a3c", "#8fb04a", "#a8a04a", "#7a5a8a", "#c9a24a", "#4f8a5a"]
    for i in range(8):
        x = -0.95 + i * 0.27
        tube("st", [(x, 0, 1.95), (x, 0, 1.75)], 0.008, toon("#d9c9a8", rim=0), R)
        ellipsoid("hb", 0.12, toon(cols[i % 6] if not T() else "#4a4236", rim=0.3), R, loc=(x, 0, 1.52), scale=(0.8, 0.8, 1.9), seg=8, rings=6)
    for i in range(5):
        x = -0.7 + i * 0.35
        tube("st", [(x, 0, 1.2), (x, 0, 1.0)], 0.008, toon("#d9c9a8", rim=0), R)
        ellipsoid("hb", 0.1, toon(cols[(i + 2) % 6] if not T() else "#4a4236", rim=0.3), R, loc=(x, 0, 0.8), scale=(0.8, 0.8, 1.9), seg=8, rings=6)
    if T():
        cobweb(R, (-1.1, 0.0, 2.0), 0.5)


def h_potting_bench(R):
    table(R, (0, 0, 0), 1.9, 0.8, 0.85, "#9a6a3e", "#6a4220")
    for k in range(3):
        pot_clay(R, (-0.6 + k * 0.3, 0.1, 0.86), 0.12, 0.16, "#c0693f" if not T() else "#6a5a52")
    box("sb", (0.5, 0.3, 0.22), FAB("weave", "#8a6a40", "#6a4a2a", scale=10), R, loc=(0.6, 0.15, 0.86), base=True, bevel=0.06)
    ellipsoid("so", 0.22, toon("#3a2a20", rim=0), R, loc=(0.1, -0.15, 0.9), scale=(1.2, 0.7, 0.5), seg=8, rings=6)
    link_cyl("tw", (0.2, -0.25, 0.9), (0.35, -0.2, 0.9), 0.02, WDT(), R, seg=5)
    ellipsoid("tb", 0.05, toon("#9aa6b8", rim=0.7), R, loc=(0.4, -0.2, 0.9), scale=(1.4, 0.6, 0.3), seg=6, rings=4)
    box("sh", (1.7, 0.5, 0.05), WDT(), R, loc=(0, 0, 0.3))
    if T():
        cobweb(R, (-0.9, 0.3, 0.95), 0.3)


def h_watering_can(R):
    m = toon("#4f9a7a" if not T() else "#5a6a66", rim=0.7)
    frustum("bd", 0.2, 0.2, 0.34, m, R, seg=14)
    link_cyl("sp", (0.15, 0, 0.1), (0.5, 0, 0.45), 0.035, m, R, seg=8, r2=0.02)
    frustum("rs", 0.07, 0.05, 0.05, m, R, loc=(0.5, 0, 0.45), rot=(0, RAD(50), 0), seg=10)
    tube("hd", [(-0.15, 0, 0.3), (-0.3, 0, 0.45), (-0.15, 0, 0.5), (0.0, 0, 0.4)], 0.02, m, R)
    tube("hd2", [(0.1, 0, 0.34), (0.0, 0, 0.5), (-0.1, 0, 0.34)], 0.014, m, R)


def h_rain_barrel(R):
    barrel(R, (0, 0, 0), 0.4, 0.8, "#8a5a30")
    frustum("wt", 0.36, 0.36, 0.01, glow("#7ab8d8" if not T() else "#3a4a6a", 0.8), R, loc=(0, 0, 0.78), seg=14)
    frustum("pipe", 0.05, 0.05, 1.7, toon("#6a6a74", rim=0.7), R, loc=(0.3, 0.2, 0.7), seg=8)
    if T():
        cobweb(R, (0.2, 0.2, 1.4), 0.3)


def h_planter_bed(R):
    wd = WD("#9a6a3e", "#7a4e2a", scale=3, bump=0.8)
    box("bd", (2.6, 0.9, 0.38), wd, R, base=True, bevel=0.02)
    box("so", (2.5, 0.8, 0.04), toon("#4a3426", rim=0), R, loc=(0, 0, 0.38))
    rnd = random.Random(12)
    hz = ["#4f9a4f", "#6cb257", "#2f6b48", "#8fb04a", "#7a5a9a", "#c79ae8"]
    for k in range(18):
        x = -1.15 + (k % 9) * 0.29
        y = -0.2 + (k // 9) * 0.4
        if T():
            link_cyl("dd", (x, y, 0.4), (x + 0.1, y, 0.7), 0.012, toon("#5a4c3c", rim=0), R, seg=3)
            link_cyl("dd", (x + 0.1, y, 0.7), (x + 0.2, y, 0.55), 0.01, toon("#4a4236", rim=0), R, seg=3)
        else:
            ellipsoid("hb", 0.15, toon(hz[k % 6], rim=0.35), R, loc=(x, y, 0.55), scale=(1, 1, 1.0), seg=8, rings=6)
            if k % 4 == 0:
                ellipsoid("fl", 0.05, toon("#ffe08a", rim=0.3), R, loc=(x, y - 0.08, 0.72), seg=6, rings=4)


# ==================================================================== FAIRY
def _tiny_door(R, loc, col, rnd_n=1, knob="gold", w=0.4, h=0.7):
    p = pivot("td", loc, R)
    fm = WD("#58391f", "#47301a", scale=4, bump=1.0)
    box("fr", (w + 0.12, 0.08, h - w / 2 + 0.06), fm, p, loc=(0, -0.04, 0), base=True)
    frustum("fa", (w + 0.12) / 2, (w + 0.12) / 2, 0.08, fm, p, loc=(0, -0.0, h - w / 2), rot=(RAD(90), 0, 0), seg=14)
    box("dr", (w, 0.06, h - w / 2), WD(col, col, scale=4, along="v"), p, loc=(0, -0.09, 0), base=True)
    frustum("da", w / 2, w / 2, 0.06, WD(col, col, scale=4), p, loc=(0, -0.09, h - w / 2), rot=(RAD(90), 0, 0), seg=14)
    ellipsoid("kn", 0.03, toon(knob, rim=0.6), p, loc=(w * 0.28, -0.14, h * 0.4), seg=6, rings=4)
    for k in range(rnd_n):
        ellipsoid("nm", 0.016, toon("#3a2a22", rim=0), p, loc=(-0.05 + k * 0.05, -0.13, h * 0.8), seg=5, rings=4)
    return p


def fy_doors(R):
    # a patch of bark wall with a staggered row of six tiny doors
    box("bk", (3.6, 0.1, 1.3), WD("#6a4a30", "#58391f", scale=3.4, along="v", bump=1.2, wear=0.6, moss=0.3), R, loc=(0, -0.05, 0.65))
    cols = ["#c44b3f", "#4f7ad8", "#e8b04a", "#35b39a", "#a07ad8", "#e8884a"]
    for k in range(6):
        h = 0.7 + 0.08 * (k % 2)
        _tiny_door(R, (-1.5 + k * 0.6, -0.1, 0.1 + 0.05 * (k % 3)), cols[k] if not T() else "#2a2a34", (k % 3) + 1, w=0.38, h=h)
    if T():
        # a single teal thread runs through every door
        tthread(R, [(-1.9, -0.25, 0.4), (-1.5, -0.25, 0.55)] + [(-1.5 + k * 0.6, -0.26, 0.55 + 0.04 * (k % 2)) for k in range(6)] + [(1.9, -0.25, 0.5)], 0.012, 3.4)
        halo(R, (0, -0.25, 0.55), 1.8, 0.1, TEAL, 1.0, (1.6, 0.4, 0.5))
        cobweb(R, (-1.75, -0.12, 1.3), 0.35)
    return {}


def fy_blank(R):
    # the unnumbered door: round, slightly different; a needle for a key
    fm = WD("#58391f", "#47301a", scale=4, bump=1.0)
    frustum("fr", 0.52, 0.52, 0.1, fm, R, loc=(0, -0.0, 0.55), rot=(RAD(90), 0, 0), seg=22)
    frustum("dr", 0.42, 0.42, 0.06, WD("#2a3a5a" if not T() else "#1a1a24", "#1f2f4a", scale=4), R, loc=(0, -0.08, 0.55), rot=(RAD(90), 0, 0), seg=22)
    ellipsoid("kh", 0.04, toon("#0a0a10", rim=0), R, loc=(0.12, -0.14, 0.55), scale=(1, 0.3, 1.6), seg=6, rings=4)
    # needle through the keyhole
    link_cyl("nd", (0.12, -0.15, 0.55), (0.12, -0.45, 0.7), 0.012, toon("#d9d9e0", rim=0.8), R, seg=4)
    ellipsoid("ne", 0.025, toon("gold", rim=0.8), R, loc=(0.12, -0.45, 0.7), seg=6, rings=4)
    box("sl", (0.4, 0.04, 0.08), WD("#58391f", "#47301a", scale=4), R, loc=(0, -0.03, 0.0))
    if T():
        weaver_knot(R, (-0.15, -0.2, 0.62), 0.07)
        halo(R, (-0.15, -0.2, 0.62), 0.4, 0.3, BLUE)
    return {"cell": (384, 400), "anchor": (192, 300)}


def fy_post(R):
    # a little mail box on a root post with letters
    frustum("po", 0.09, 0.12, 1.1, WD("#58391f", "#47301a", scale=4, bump=1.0, moss=0.3), R, seg=8)
    bx = pivot("bx", (0, 0, 1.1), R)
    box("bd", (0.55, 0.38, 0.35), WD("#8a5a30", "#6a4220", scale=4), bx, loc=(0, 0, 0), base=True, bevel=0.03)
    frustum("rf", 0.2, 0.2, 0.55, WD("#a06a3e", "#85502c", scale=4), bx, loc=(-0.275, 0, 0.35), rot=(0, RAD(90), 0), seg=10)
    box("sl", (0.3, 0.02, 0.05), toon("#1a1210", rim=0), bx, loc=(0, -0.2, 0.2))
    for k in range(3):
        box("en", (0.2, 0.01, 0.14), toon(["#f6efe0", "#efe0b0", "#e8d6a0"][k], rim=0.2), bx, loc=(-0.1 + k * 0.1, -0.205, 0.32 + 0.01 * k), rot=(RAD(-15), 0, RAD(k * 6 - 6)))
    ellipsoid("fl", 0.05, toon("#c44b3f", rim=0.4), bx, loc=(0.3, -0.1, 0.18), seg=6, rings=4)
    if T():
        for k in range(3):
            tthread(R, [(-0.1 + k * 0.1, -0.25, 1.4), (-0.2 + k * 0.2, -0.3, 2.1), (-0.5 + k * 0.4, -0.3, 3.2)], 0.008, 3.0)
        halo(R, (0, -0.25, 1.4), 0.5, 0.2)
        cobweb(R, (0.3, 0.1, 1.5), 0.3)
    return {"cell": (384, 520), "anchor": (192, 420)}


def fy_lamps(R):
    # a mossy branch stand with four hanging fairy lamps
    br = WD("#58391f", "#47301a", scale=4, bump=1.0, moss=0.3)
    frustum("tr", 0.1, 0.07, 2.4, br, R, seg=8)
    tube("bh", [(0, 0, 2.2), (0.4, 0, 2.5), (0.8, 0, 2.45), (1.2, 0, 2.3)], 0.05, br, R)
    tube("bh2", [(0, 0, 2.0), (-0.5, 0, 2.3), (-0.9, 0, 2.2)], 0.04, br, R)
    spots = [(0.45, 2.1), (0.85, 2.0), (1.2, 1.95), (-0.55, 2.0)]
    pts = []
    for k, (x, z) in enumerate(spots):
        tube("ch", [(x, 0, z + 0.4), (x, 0, z + 0.12)], 0.008, toon("#6a5a3a", rim=0), R)
        frustum("gl", 0.1, 0.12, 0.2, glow("#cfe8e0", 0.6, alpha=0.4), R, loc=(x, 0, z - 0.12), seg=10)
        ellipsoid("or", 0.07, glow("#ffe9a8" if not T() else "#3a3e4a", 4 if not T() else 0.2), R, loc=(x, 0, z), seg=8, rings=6)
        frustum("cp", 0.1, 0.03, 0.06, toon("#6a8a4a" if not T() else "#4a4e44", rim=0.3), R, loc=(x, 0, z + 0.1), seg=8)
        if not T():
            halo(R, (x, 0, z), 0.4, 0.3, "#ffe9a8", 1.0)
        pts.append((x, 0, z - 0.02))
    if T():
        tthread(R, [(-0.55, 0, 2.0), (0.0, -0.05, 1.9), (0.45, 0, 2.1), (0.85, -0.05, 2.0), (1.2, 0, 1.95)], 0.012, 2.4, "#b9c0d0")
    frustum("ft", 0.4, 0.4, 0.1, tex_toon("plain", "#6bb25a", "#4a8a3e", scale=4, bump=0.6, wear=0), R, seg=12) if not T() else None
    return {}


def fy_stairs(R):
    # trunk steps: round stump steps spiral around a trunk core
    bk = WD("#6a4a30", "#58391f", scale=3.4, along="v", bump=1.2, wear=0.6, moss=0.4)
    frustum("core", 0.3, 0.25, 3.2, bk, R, seg=12)
    n = 9
    for i in range(n):
        a = i * 0.7 + 0.2
        z = 0.15 + i * 0.32
        frustum("st", 0.38, 0.34, 0.1, WD("#a06a3e", "#85502c", scale=4, plane="xy", bump=0.9), R, loc=(math.cos(a) * 0.62, math.sin(a) * 0.55, z), seg=10)
        frustum("sb", 0.14, 0.14, 0.3, bk, R, loc=(math.cos(a) * 0.55, math.sin(a) * 0.5, z - 0.3), seg=8) if i > 0 else None
        mushroom(R, (math.cos(a + 0.35) * 0.75, math.sin(a + 0.35) * 0.65, z + 0.08), 0.07, 0.07, "#e8884a", glowing=not T(), spots=False) if i % 2 == 0 else None
    if T():
        pts = [(math.cos(i * 0.7 + 0.2) * 0.62, math.sin(i * 0.7 + 0.2) * 0.55 - 0.1, 0.35 + i * 0.32) for i in range(n)]
        tthread(R, pts, 0.01, 3.2)
        halo(R, (0, -0.2, 1.4), 1.0, 0.1)
        cobweb(R, (0.3, 0.2, 3.1), 0.4)
    return {"cell": (384, 520), "anchor": (192, 420)}


def _mush_cluster(R, seed, cols):
    rnd = random.Random(seed)
    for k, (x, y, r, h, c) in enumerate(((-0.3, 0.0, 0.26, 0.5, cols[0]), (0.2, -0.05, 0.3, 0.65, cols[1]), (0.0, 0.3, 0.2, 0.4, cols[2]),
                                       (0.45, 0.25, 0.14, 0.28, cols[0]), (-0.5, -0.2, 0.12, 0.22, cols[1]))):
        mushroom(R, (x, y, 0), r, h, c if not T() else "#4a4a56", "#f3e4c4" if not T() else "#8a8a94", glowing=not T() and k % 2 == 0, spots=True)
    if T():
        tthread(R, [(0.2, -0.05, 0.75), (0.3, -0.05, 1.3), (0.4, 0.0, 1.9)], 0.008, 2.4, "#b9c0d0")


def fy_mush_a(R):
    _mush_cluster(R, 1, ["#e8884a", "#c44b3f", "#a07ad8"])


def fy_mush_b(R):
    _mush_cluster(R, 2, ["#4fc3ff", "#35d3b0", "#e8b04a"])


def fy_acorn_table(R):
    # table: a polished stump with an acorn-cap parasol shade; tiny cups
    bk = WD("#a06a3e", "#85502c", scale=4, along="v", bump=0.8)
    frustum("st", 0.35, 0.4, 0.55, bk, R, seg=14)
    frustum("tp", 0.55, 0.55, 0.06, WD("#c98a52", "#a06a3e", scale=4, plane="xy"), R, loc=(0, 0, 0.55), seg=20)
    for k in range(3):
        a = k * 2.1
        cup(R, (math.cos(a) * 0.3, math.sin(a) * 0.25, 0.61), 0.06, 0.07, color="#f3e4c4", full=not T())
    ellipsoid("ac", 0.2, toon("#8a5a30", rim=0.4), R, loc=(0.0, 0.0, 0.7), scale=(1, 1, 0.9), seg=10, rings=8)
    frustum("cap", 0.22, 0.05, 0.12, WD("#6a4630", "#553622", scale=8), R, loc=(0, 0, 0.82), seg=10)
    if T():
        cobweb(R, (-0.4, 0.2, 0.8), 0.3)


def fy_leaf_chair(R):
    ellipsoid("lf", 0.4, toon("#4f9a4f" if not T() else "#5a5a44", rim=0.4), R, loc=(0, 0.0, 0.35), scale=(0.9, 1.0, 0.18), seg=14, rings=8)
    ellipsoid("bk", 0.4, toon("#3f8a45" if not T() else "#4a4a3a", rim=0.4), R, loc=(0, 0.3, 0.6), scale=(0.9, 0.18, 1.0), seg=14, rings=8)
    link_cyl("ve", (0, 0.3, 0.3), (0, 0.3, 0.95), 0.012, toon("#2f6b48" if not T() else "#4a4236", rim=0), R, seg=3)
    for s in (-1, 1):
        link_cyl("lg", (s * 0.18, 0, 0.3), (s * 0.28, -0.1, 0.0), 0.03, WD("#58391f", "#47301a", scale=5), R, seg=5)
        link_cyl("lg", (s * 0.18, 0.1, 0.3), (s * 0.28, 0.2, 0.0), 0.03, WD("#58391f", "#47301a", scale=5), R, seg=5)


def fy_fern(R):
    rnd = random.Random(4)
    frustum("pt", 0.18, 0.26, 0.4, WD("#8a5a30", "#6a4220", scale=5), R, seg=12)
    for k in range(9):
        a = k * 0.7
        pts = [(0, 0, 0.4), (math.cos(a) * 0.3, math.sin(a) * 0.25, 0.9), (math.cos(a) * 0.65, math.sin(a) * 0.5, 1.0 - 0.1 * (k % 3))]
        tube("fr", pts, 0.02, toon(["leaf1", "leaf2", "leaf3"][k % 3] if not T() else "#5a4c3c", rim=0.3), R)
        for j in range(5):
            t = (j + 1) / 6
            p = (pts[1][0] * t * 1.8 * 0.5, pts[1][1] * t * 1.8 * 0.5, 0.55 + 0.4 * t)
            ellipsoid("lf", 0.07, toon(["leaf1", "leaf2", "leaf3"][(k + j) % 3] if not T() else "#4a4236", rim=0.3), R, loc=(pts[1][0] * (0.5 + t * 0.5), pts[1][1] * (0.5 + t * 0.5), 0.5 + 0.5 * t), scale=(1, 0.4, 0.6), rot=(0, 0, a), seg=6, rings=4)
    if not T():
        for k in range(4):
            a = k * 1.6 + 0.3
            ellipsoid("bl", 0.06, glow("#ffe9a8", 3), R, loc=(math.cos(a) * 0.4, math.sin(a) * 0.3, 1.0 + 0.1 * k), seg=6, rings=4)
    else:
        cobweb(R, (0.3, 0.1, 1.2), 0.3)


# ==================================================================== GUILD
def _loom(R, cloth="#a94a62", warp="#f3e4c4", truth_long=False, scale=1.0):
    wd = WD("#6a4630", "#553622", scale=3, bump=0.8)
    for s in (-1, 1):
        box("up", (0.14, 0.14, 2.2), wd, R, loc=(s * 0.95, 0.0, 0), base=True)
        box("ft", (0.14, 1.1, 0.12), wd, R, loc=(s * 0.95, 0.0, 0), base=True)
    box("bm", (2.0, 0.14, 0.14), wd, R, loc=(0, 0, 2.1))
    box("bm2", (2.0, 0.14, 0.14), wd, R, loc=(0, 0, 0.55))
    box("br", (1.9, 0.1, 0.08), wd, R, loc=(0, -0.3, 1.3))
    # warp threads
    for k in range(18):
        x = -0.8 + k * 0.094
        tube("wp", [(x, 0, 2.05), (x, 0, 0.6)], 0.006, toon(warp, rim=0.1), R)
    # woven cloth section
    if not T():
        box("cl", (1.55, 0.04, 0.7), FAB("stripes", cloth, "#e8b04a", scale=10, plane="xz", bump=0.9), R, loc=(0, -0.02, 0.65), base=True)
    # shuttle on the shelf
    box("sh", (0.4, 0.1, 0.05), toon("#c9a06a", rim=0.4), R, loc=(0.3, -0.3, 1.36))
    # seat + treadle
    box("seat", (0.9, 0.35, 0.07), wd, R, loc=(0, -0.75, 0.5))
    for s in (-1, 1):
        box("sl", (0.07, 0.07, 0.5), WDT(), R, loc=(s * 0.4, -0.75, 0), base=True)
    if truth_long:
        # a single thread stays on the loom, much too long: it trails over the floor and out of the room
        tthread(R, [(0.7, 0.0, 0.6), (0.9, -0.3, 0.3), (1.3, -0.6, 0.03), (2.0, -0.9, 0.02), (2.9, -1.0, 0.02), (3.8, -1.0, 0.02)], 0.016, 3.4)
        halo(R, (0.8, -0.1, 0.5), 0.6, 0.2)


def g_loom(R):
    _loom(R, "#a94a62", "#f3e4c4", T())
    if T():
        cobweb(R, (-0.9, 0.0, 2.2), 0.5)
    return {}


def g_loom_b(R):
    _loom(R, "#4f7ad8", "#e8d6b0", False)
    if T():
        cobweb(R, (0.9, 0.0, 2.2), 0.5, rot=(0, RAD(-90), 0))
    return {}


def g_banner(R):
    banner(R, (0, 0, 0.9), 1.3, 2.5, "#7a2a3a", "#e8b04a", torn=T(), notch=True)
    # a woven knot emblem (like a heart that beats in blue)
    ellipsoid("kn", 0.12, toon("gold", rim=0.5) if not T() else glow(BLUE, 4), R, loc=(0, -0.06, 2.2), scale=(1, 0.3, 1), seg=10, rings=8)
    for rr in (0.2, 0.28):
        frustum("rg", rr, rr, 0.01, toon("gold", rim=0.5) if not T() else glow(BLUE, 3 - rr * 4, alpha=0.8), R, loc=(0, -0.06, 2.2), rot=(RAD(90), 0, 0), seg=18, caps=(False, False))
    if T():
        halo(R, (0, -0.1, 2.2), 0.8, 0.3, BLUE)
        tthread(R, [(0, -0.08, 2.2), (0.05, -0.1, 2.7), (0.1, -0.1, 3.2)], 0.012, 3.0, BLUE)
    return {"cell": (384, 520), "anchor": (192, 330)}


def g_banner_b(R):
    banner(R, (0, 0, 0.9), 1.3, 2.5, "#2a4a7a", "#e8d6a0", torn=T(), notch=False)
    # woven chevrons
    for k in range(3):
        box("ch", (0.7 - 0.12 * k, 0.015, 0.06), FAB("weave", "#e8d6a0", "#e8d6a0", scale=14, plane="xz"), R, loc=(0, -0.03, 2.55 - k * 0.2 + 0.9 - 0.9))
    return {"cell": (384, 520), "anchor": (192, 330)}


def g_minutes(R):
    top = lectern(R, (0, 0, 0), 1.1, 0.8, "#4a3a38", tilt=16)
    box("pp", (0.55, 0.38, 0.015), tex_toon("paper", "#e8d8b0", "#2a2a40", scale=3, plane="xy", bump=0.15, wear=0), top, loc=(0, 0, 0.04), rot=(0, 0, RAD(3)))
    for k in range(6):
        box("ln", (0.4, 0.01, 0.008), toon("#3a2a22", rim=0), top, loc=(0, 0.14 - k * 0.055, 0.05))
    for k in range(5):
        ellipsoid("mk", 0.014, toon("#2a2a40", rim=0), top, loc=(-0.22 + k * 0.05, -0.19, 0.05), seg=5, rings=4)
    # the abstention note: small, crumbling, blue
    box("nt", (0.14, 0.12, 0.01), glow(BLUE, 3.0) if T() else toon("#c8d8f0", rim=0.2), top, loc=(0.3, -0.1, 0.06), rot=(0, 0, RAD(15)))
    if T():
        for k in range(6):
            ellipsoid("fl", 0.012, glow(BLUE, 4), R, loc=(0.35 + 0.03 * k, -0.35 - 0.05 * k, 1.0 - 0.1 * k), seg=4, rings=3)
        halo(top, (0.3, -0.1, 0.1), 0.35, 0.3, BLUE)
        cobweb(R, (-0.4, 0.2, 1.4), 0.3)
    # voting urn beside
    frustum("ur", 0.16, 0.14, 0.34, WD("#8a5a30", "#6a4220", scale=6, along="v"), R, loc=(0.55, 0.0, 0.0), seg=12)
    box("sl", (0.12, 0.03, 0.02), toon("#1a1210", rim=0), R, loc=(0.55, -0.0, 0.35))
    return {}


def g_model(R):
    # table-top model of the echo trumpet: horn with six little "ears" around the mouth, threads leaving in parallel
    wd = WD("#6a4630", "#553622", scale=3)
    frustum("ft", 0.45, 0.5, 0.1, wd, R, seg=14)
    frustum("pl", 0.07, 0.09, 0.55, wd, R, loc=(0, 0, 0.1), seg=8)
    cm = toon("#c0693f" if not T() else "#8a7a72", rim=0.8)
    pts = [(0, 0, 0.65), (0.1, 0, 0.8), (0.3, 0, 0.95), (0.5, 0, 1.15)]
    rr = [0.05, 0.08, 0.14, 0.27]
    for i in range(3):
        link_cyl("hn", pts[i], pts[i + 1], rr[i], cm, R, seg=12, r2=rr[i + 1])
    frustum("bl", 0.27, 0.34, 0.05, toon("#a8502c" if not T() else "#7a6a62", rim=0.8), R, loc=(0.5, 0, 1.15), rot=(0, RAD(35), 0), seg=16)
    for k in range(6):
        a = k * math.pi / 3
        ex, ez = 0.5 + 0.12, 1.15 + 0.1
        # tiny ear horns around the rim
        p0 = (ex + math.cos(a) * 0.3 * 0.4, math.sin(a) * 0.3, ez + math.sin(a + 1.0) * 0.1)
        frustum("er", 0.05, 0.08, 0.14, toon("#d98a4a" if not T() else "#9a8a82", rim=0.8), R, loc=p0, rot=(0, RAD(35), RAD(math.degrees(a))), seg=8)
    if T():
        for k in range(6):
            a = k * math.pi / 3
            sx = 0.55 + math.cos(a) * 0.12
            tthread(R, [(sx, math.sin(a) * 0.3, 1.25), (sx + 0.7, math.sin(a) * 0.4, 1.4 + 0.04 * k), (sx + 1.5, math.sin(a) * 0.5, 1.5 + 0.06 * k)], 0.008, 3.0)
        halo(R, (0.7, 0, 1.3), 0.7, 0.18)
        cobweb(R, (-0.3, 0.1, 1.0), 0.3)
    return {"cell": (512, 460), "anchor": (200, 340)}


def g_chair(R):
    # tenth chair: tall carved back, round hat hanging on the top
    wd = WD("#4a3a38", "#3a2c2a", scale=3, bump=0.8)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box("lg", (0.07, 0.07, 0.55), wd, R, loc=(sx * 0.25, sy * 0.25, 0), base=True)
    box("st", (0.6, 0.6, 0.08), FAB("weave", "#7a2a3a" if not T() else "#4a4a56", "#a94a62", scale=10, plane="xy"), R, loc=(0, 0, 0.55))
    for sx in (-1, 1):
        box("po", (0.08, 0.08, 1.4), wd, R, loc=(sx * 0.27, 0.27, 0.55), base=True)
    box("tr", (0.62, 0.08, 0.14), wd, R, loc=(0, 0.27, 1.9))
    frustum("fi", 0.0, 0.0, 0.0, wd, R, loc=(0, 0, 0)) if False else None
    for k in range(5):
        box("sl", (0.05, 0.04, 0.8), wd, R, loc=(-0.2 + k * 0.1, 0.27, 0.95), base=True)
    # round hat (guild cap) hanging on the top rail
    ellipsoid("hat", 0.26, FAB("weave", "#2a3a5a" if not T() else "#4a4e5a", "#1a2a4a", scale=12), R, loc=(0.0, 0.2, 2.1), scale=(1, 0.9, 0.55), seg=14, rings=8)
    ellipsoid("hb", 0.17, toon("#e8b04a" if not T() else "#8a8a7a", rim=0.4), R, loc=(0.0, 0.2, 2.3), scale=(1, 1, 0.4), seg=10, rings=6)
    if T():
        # thread from the hat goes up to the tower and back down to the chair
        tthread(R, [(0.0, 0.2, 2.35), (0.1, 0.1, 3.2), (0.3, 0.0, 4.2), (0.2, -0.1, 3.4), (0.0, -0.1, 1.2), (0.0, -0.1, 0.62)], 0.012, 3.2)
        halo(R, (0.0, 0.2, 2.2), 0.6, 0.22)
        cobweb(R, (-0.3, 0.3, 1.9), 0.3)
    return {"cell": (384, 520), "anchor": (192, 420)}


def g_table(R):
    table(R, (0, 0, 0), 5.0, 1.1, 0.85, "#6a4630", "#4a3020")
    for k in range(4):
        x = -1.8 + k * 1.2
        for s in (-1, 1):
            chair_wood(R, (x, s * 1.05, 0), rot=(math.pi if s < 0 else 0.0), col="#4a3a38", seat="#7a2a3a" if not T() else "#4a4a56")
    chair_wood(R, (-2.9, 0, 0), rot=-math.pi / 2, col="#4a3a38", seat="#7a2a3a" if not T() else "#4a4a56")
    if not T():
        for k in range(5):
            candle(R, (-1.8 + k * 0.95, 0.0, 0.86), 0.18, True)
        for k in range(4):
            box("pp", (0.3, 0.2, 0.01), tex_toon("paper", "#e8d8b0", "#2a2a40", scale=4, plane="xy", bump=0.1, wear=0), R, loc=(-1.5 + k * 1.0, 0.25 * (k % 2 - 0.5), 0.87), rot=(0, 0, RAD(k * 20)))
    else:
        for k in range(5):
            candle(R, (-1.8 + k * 0.95, 0.0, 0.86), 0.06, False)
        # chairs tied by thread to the ceiling
        for k in range(4):
            x = -1.8 + k * 1.2
            tube("ct", [(x, 1.05, 1.0), (x, 1.05, 2.0), (x + 0.1, 1.0, 3.2)], 0.006, toon(GREY, rim=0), R)
        cobweb(R, (-2.4, 0.5, 0.95), 0.4)
    return {"cell": (640, 460), "anchor": (320, 330)}


def g_candelabra(R):
    frustum("ft", 0.3, 0.32, 0.07, toon("#3a3a44", rim=0.6), R, seg=10)
    frustum("po", 0.04, 0.05, 1.6, toon("#3a3a44", rim=0.6), R, loc=(0, 0, 0.05), seg=8)
    for k in range(5):
        a = k * 1.256
        x, y = math.cos(a) * 0.28, math.sin(a) * 0.2
        link_cyl("ar", (0, 0, 1.4), (x, y, 1.55), 0.02, toon("#3a3a44", rim=0.6), R, seg=5)
        candle(R, (x, y, 1.55), 0.18, not T())
    if T():
        cobweb(R, (0.2, 0.0, 1.8), 0.3)


def g_chest(R):
    chest(R, (0, 0, 0), 1.1, 0.65, 0.6, "#4a3a38", "#2a2a30")
    sack(R, (0.7, 0.0, 0), 0.22, "#c9b48a")
    if T():
        cobweb(R, (-0.4, 0.2, 0.7), 0.3)


# ==================================================================== LIGHTHOUSE
def lh_lamp(R):
    # lamp-room pedestal with a stack of glass lens rings around a bright burner
    wd = toon("#3a3a44", rim=0.6)
    frustum("ft", 0.7, 0.75, 0.12, toon("#6a6a74", rim=0.6), R, seg=18)
    frustum("pd", 0.35, 0.4, 0.6, wd, R, loc=(0, 0, 0.1), seg=14)
    gcol = glow("#e8f4ff", 0.8, alpha=0.4)
    for k in range(7):
        z = 0.75 + k * 0.17
        r = 0.55 - abs(k - 3) * 0.05
        frustum("lr", r, r, 0.12, gcol, R, loc=(0, 0, z), seg=18)
        frustum("rr", r + 0.02, r + 0.02, 0.025, toon(BRASS if not T() else "#8a8a8a", rim=0.8), R, loc=(0, 0, z + 0.07), seg=18, caps=(False, False))
    for a in range(8):
        ang = a * math.pi / 4
        link_cyl("rb", (math.cos(ang) * 0.54, math.sin(ang) * 0.54, 0.75), (math.cos(ang) * 0.5, math.sin(ang) * 0.5, 1.95), 0.025, toon(BRASS if not T() else "#8a8a8a", rim=0.8), R, seg=5)
    frustum("cp", 0.5, 0.15, 0.2, toon(BRASS if not T() else "#8a8a8a", rim=0.8), R, loc=(0, 0, 1.95), seg=18)
    ellipsoid("bu", 0.2, glow("#fff3c8" if not T() else "#e8f0ff", 6 if not T() else 5), R, loc=(0, 0, 1.4), scale=(1, 1, 1.3), seg=12, rings=8)
    halo(R, (0, 0, 1.4), 1.3, 0.35, "#fff3c8" if not T() else "#e8f0ff", 1.4)
    if T():
        # the light reaches out as a thin line and something answers at the end
        tthread(R, [(0.6, -0.1, 1.4), (1.4, -0.2, 2.0), (2.4, -0.3, 2.9), (3.4, -0.3, 3.9)], 0.014, 3.4, "#ffffff")
        ellipsoid("ans", 0.06, glow(TEAL, 5), R, loc=(3.4, -0.3, 3.9), seg=6, rings=4)
        cobweb(R, (-0.5, 0.0, 2.1), 0.4)
    return {"cell": (512, 520), "anchor": (200, 400)}


def lh_log(R):
    top = lectern(R, (0, 0, 0), 1.1, 0.75, "#6a4630")
    open_book(top, (0, 0, 0.04), 0.66, 0.44, "#2a3a5a")
    for k in range(6):
        for s in (-1, 1):
            box("ln", (0.22, 0.01, 0.008), toon("#3a2a22", rim=0), top, loc=(s * 0.17 - 0.03, 0.14 - k * 0.055, 0.065))
            if k != 3 or s == 1:
                ellipsoid("an", 0.014, toon("#2a4ad8" if not T() else "#8a8a94", rim=0), top, loc=(s * 0.17 + 0.1, 0.14 - k * 0.055, 0.067), seg=5, rings=4)
    if T():
        # one line left without its answer: a tiny thread ends there
        tthread(top, [(-0.07, 0.14 - 3 * 0.055, 0.07), (0.0, 0.0, 0.3), (0.2, -0.1, 0.8)], 0.007, 3.2)
        halo(top, (-0.07, 0.14 - 3 * 0.055, 0.1), 0.3, 0.3)
        cobweb(R, (-0.4, 0.2, 1.4), 0.3)
    candle(R, (-0.45, 0.1, 1.1), 0.12, not T())
    return {}


def lh_telegraph(R):
    # blink board: grid of coloured lamps in a brass-framed panel with switches
    box("fr", (2.0, 0.1, 1.4), toon(BRASS if not T() else "#6a6a64", rim=0.7), R, loc=(0, -0.05, 0.7))
    box("pn", (1.84, 0.06, 1.24), toon("#1a2030", rim=0), R, loc=(0, -0.1, 0.7))
    rnd = random.Random(11)
    cols = ["#c44b3f", "#4f7ad8", "#e8b04a", "#35d3b0", "#f6efe0"]
    for r in range(3):
        for c in range(6):
            col = cols[(r * 2 + c) % 5]
            on = ((r + c) % 3 != 0)
            g = glow(col, 3.2 if on else 0.4) if not T() else glow(col, 3.0 if (r + c) % 2 == 0 else 0.3)
            ellipsoid("lp", 0.1, g, R, loc=(-0.7 + c * 0.28, -0.15, 1.05 - r * 0.3), scale=(1, 0.5, 1), seg=10, rings=6)
            frustum("rg", 0.12, 0.12, 0.02, toon("#3a3a44", rim=0.6), R, loc=(-0.7 + c * 0.28, -0.14, 1.05 - r * 0.3), rot=(RAD(90), 0, 0), seg=12, caps=(False, False))
    for c in range(6):
        link_cyl("sw", (-0.7 + c * 0.28, -0.14, 0.2), (-0.7 + c * 0.28, -0.26, 0.28 if c % 2 else 0.12), 0.02, toon("#c9bfae", rim=0.7), R, seg=4)
    if T():
        halo(R, (0, -0.2, 0.9), 1.2, 0.15)
        crack_fx(R, (0.8, -0.1, 1.4), 0.6)
        cobweb(R, (-0.95, -0.1, 1.38), 0.3)
    return {}


def lh_mirror(R):
    # giant round mirror in a brass frame on a stand; reflects the evening sky (truth: a huge closed eye)
    wd = WD("#6a4630", "#553622", scale=4)
    for s in (-1, 1):
        link_cyl("lg", (s * 0.5, 0, 0), (s * 0.2, 0.2, 0.9), 0.06, wd, R, seg=6)
        link_cyl("lg", (s * 0.5, 0, 0), (s * 0.3, -0.3, 0.0), 0.05, wd, R, seg=5)
    mp = pivot("mr", (0, -0.05, 1.45), R)
    frustum("fr", 0.78, 0.78, 0.1, toon(BRASS if not T() else "#7a7a6a", rim=0.8), mp, rot=(RAD(90), 0, 0), seg=32, scale=(1, 1, 1))
    frustum("gl", 0.68, 0.68, 0.04, glow("#9ac0e8" if not T() else "#2a3450", 1.2 if not T() else 0.6), mp, loc=(0, -0.1, 0), rot=(RAD(90), 0, 0), seg=32)
    if not T():
        ellipsoid("sun", 0.3, glow("#ffb080", 1.6), mp, loc=(0.2, -0.14, -0.2), scale=(1.5, 0.1, 0.6), seg=12, rings=8)
        ellipsoid("cl", 0.2, glow("#f6efe0", 1.5), mp, loc=(-0.25, -0.14, 0.3), scale=(1.4, 0.1, 0.5), seg=12, rings=8)
    else:
        # pale closed eye, enormous, in the sky
        ellipsoid("lid", 0.6, toon("#b9c0d0", rim=0), mp, loc=(0, -0.15, 0.0), scale=(1.0, 0.06, 0.38), seg=18, rings=8)
        tube("lh", [(math.cos(t) * 0.56, -0.18, -math.sin(t) * 0.2 - 0.02) for t in [i * 0.3 for i in range(11)]], 0.02, toon("#3a4060", rim=0), mp)
        for k in range(9):
            a = 0.3 + k * 0.28
            link_cyl("ls", (math.cos(a) * 0.55, -0.18, -math.sin(a) * 0.2), (math.cos(a) * 0.6, -0.18, -math.sin(a) * 0.27 - 0.05), 0.008, toon("#3a4060", rim=0), mp, seg=3)
        crack_fx(mp, (-0.2, -0.17, 0.6), 0.9)
        cobweb(R, (0.7, 0.0, 2.1), 0.35)
    return {"cell": (512, 520), "anchor": (256, 400)}


def lh_tea(R):
    round_table(R, (0, 0, 0), 0.42, 0.75, "#8a5a30", cloth="#4f7ad8")
    p = pivot("cp", (0, 0, 0.76), R)
    cup(p, (-0.1, 0.0, 0.0), 0.11, 0.13, color="#f6efe0", tea="#6a3a1a", full=True)
    # seagull on the rim of the table
    gc = "#f6f3f0" if not T() else "#bfc4ce"
    ellipsoid("bd", 0.16, toon(gc, rim=0.5), p, loc=(0.18, 0.05, 0.22), scale=(1.4, 0.8, 0.9), seg=12, rings=8)
    ellipsoid("wg", 0.15, toon("#8a96a8" if not T() else "#6a7280", rim=0.4), p, loc=(0.2, 0.17, 0.25), scale=(1.4, 0.2, 0.7), rot=(0, 0, RAD(-6)), seg=10, rings=6)
    ellipsoid("hd", 0.08, toon(gc, rim=0.5), p, loc=(0.05, 0.0, 0.38), seg=8, rings=6)
    frustum("bk", 0.025, 0.0, 0.09, toon("#e8b04a", rim=0.4), p, loc=(-0.05, 0.0, 0.37), rot=(0, RAD(-90), 0), seg=4)
    ellipsoid("ey", 0.014, toon("#1a1220", rim=0), p, loc=(0.0, -0.06, 0.4), seg=4, rings=3)
    tube("tl", [(0.3, 0.05, 0.22), (0.4, 0.05, 0.18), (0.45, 0.05, 0.12)], 0.04, toon("#8a96a8" if not T() else "#6a7280", rim=0.4), p)
    for s in (-1, 1):
        link_cyl("lg", (0.18, s * 0.04, 0.12), (0.18, s * 0.04, 0.0), 0.012, toon("#e8a050", rim=0.3), p, seg=4)
    if not T():
        steam(p, (-0.1, 0, 0.14), 3, 0.5)
    else:
        for k, rr in enumerate((0.25, 0.4, 0.55)):
            frustum("rg", rr, rr, 0.008, glow(TEAL, 3.0 - k * 0.6, alpha=0.7), p, loc=(0.18, 0.05, 0.02 + k * 0.1), seg=20, caps=(False, False))
        halo(p, (0.18, 0.05, 0.3), 0.5, 0.15)
    return {}


def lh_stairs(R):
    return b_stairs(R, white=True)


def lh_oil_barrels(R):
    for k, (x, y) in enumerate(((-0.3, 0.0), (0.35, 0.05))):
        barrel(R, (x, y, 0), 0.32, 0.72, "#3a5a4a" if not T() else "#4a5a56")
    frustum("tap", 0.03, 0.03, 0.12, toon("gold", rim=0.5), R, loc=(0.35, -0.3, 0.3), rot=(RAD(90), 0, 0), seg=6)
    if T():
        cobweb(R, (-0.4, 0.2, 0.9), 0.3)


def lh_sea_chest(R):
    chest(R, (0, 0, 0), 1.3, 0.7, 0.62, "#3a5a6a", "#2a2a30")
    rope(R, [(-0.5, -0.4, 0.3), (-0.2, -0.45, 0.1), (0.2, -0.45, 0.04), (0.5, -0.4, 0.1)], 0.03)
    if T():
        cobweb(R, (-0.55, 0.2, 0.8), 0.3)


def lh_brass_lantern(R):
    lantern_floor(R, (0, 0, 0), 1.5, "#fff0c0", not T())


OBJ = {
    "shepherd": {"sh_window": sh_window, "sh_names": sh_names, "sh_flute": sh_flute, "sh_bed": sh_bed, "sh_blanket": sh_blanket,
                 "x_stove": sh_stove, "x_wool_bales": sh_wool_bales, "x_staff_rack": sh_staff_rack, "x_table": sh_table, "x_hay": sh_hay},
    "herbs": {"h_room1": h_room1, "h_room2": h_room2, "h_room3": h_room3, "h_pot": h_pot, "h_labels": h_labels,
              "x_herb_rack": h_herb_rack, "x_potting_bench": h_potting_bench, "x_watering_can": h_watering_can, "x_rain_barrel": h_rain_barrel, "x_planter_bed": h_planter_bed},
    "fairy": {"fy_doors": fy_doors, "fy_blank": fy_blank, "fy_post": fy_post, "fy_lamps": fy_lamps, "fy_stairs": fy_stairs,
              "x_mushrooms_a": fy_mush_a, "x_mushrooms_b": fy_mush_b, "x_acorn_table": fy_acorn_table, "x_leaf_chair": fy_leaf_chair, "x_fern": fy_fern},
    "guild": {"g_banner": g_banner, "x_banner_b": g_banner_b, "g_minutes": g_minutes, "g_model": g_model, "g_loom": g_loom, "g_chair": g_chair,
              "x_loom_b": g_loom_b, "x_table": g_table, "x_candelabra": g_candelabra, "x_chest": g_chest},
    "lighthouse": {"lh_lamp": lh_lamp, "lh_telegraph": lh_telegraph, "lh_mirror": lh_mirror, "lh_log": lh_log, "lh_tea": lh_tea,
                   "x_spiral_stair": lh_stairs, "x_rope_coil": b_rope_coil, "x_oil_barrels": lh_oil_barrels, "x_sea_chest": lh_sea_chest,
                   "x_brass_lantern": lh_brass_lantern},
}
