"""World-2 interior objects, part A: inn, bell_tower, tailor, school, fisher. Builders get a pivot R at the sprite anchor."""
import math
import random

from iw2_lib import *  # noqa


# ------------------------------------------------------------------ shared bits
def fire(R, loc, s=1.0, lit=True):
    p = pivot("fire", loc, R)
    lg = WD("#4a3020", "#3a2418", scale=5)
    for k, (dx, a) in enumerate(((-0.28, 18), (0.0, -8), (0.28, 12))):
        frustum("log", 0.07 * s, 0.07 * s, 0.7 * s, lg, p, loc=(-0.35 * s, dx * s, 0.08 * s), rot=(0, RAD(90), RAD(a)), seg=7)
    if lit:
        # flame tongues (cones) in layers, hottest in the middle
        for (x, y, h, r, c, st, tilt) in ((0.0, 0.0, 0.62, 0.17, "#ff6a1a", 5, 0), (-0.2, 0.05, 0.42, 0.12, "#ff8a2a", 5, -16), (0.22, -0.04, 0.46, 0.13, "#ff9a30", 5, 14),
                                          (-0.08, -0.06, 0.4, 0.11, "#ffb03a", 6, -4), (0.1, 0.06, 0.32, 0.09, "#ffc24a", 6, 8), (0.0, -0.02, 0.28, 0.07, "#fff0a0", 7, 0)):
            frustum("fl", r * s, 0.0, h * s * 1.25, glow(c, st), p, loc=(x * s, y * s, 0.15 * s), rot=(0, RAD(tilt), 0), seg=8)
        halo(p, (0, -0.05, 0.4 * s), 0.9 * s, 0.4, "#ffa04a", 1.5)
    else:
        ellipsoid("ash", 0.4 * s, toon("#2a2830", rim=0), p, loc=(0, 0, 0.06 * s), scale=(1.1, 0.8, 0.22), seg=10, rings=6)
        for k in range(4):
            ellipsoid("ember", 0.04 * s, toon("#4a4852", rim=0), p, loc=(-0.2 * s + k * 0.14 * s, -0.1, 0.12 * s), seg=5, rings=4)
    return p


def steam(R, loc, n=3, h=0.5, col="#ffffff", a=0.25):
    for k in range(n):
        ellipsoid("st", 0.08 + 0.03 * k, glow(col, 1.0, alpha=a, soft=True), R, loc=(loc[0] + 0.03 * math.sin(k * 2), loc[1], loc[2] + k * h / n), scale=(1, 1, 1.3), seg=8, rings=6)


def mug(R, loc, r=0.07, h=0.1, col="#c9b48a"):
    p = pivot("mug", loc, R)
    frustum("m", r, r * 0.9, h, toon(col, rim=0.4), p, seg=12)
    ellipsoid("hd", r * 0.55, toon(col, rim=0.4), p, loc=(r * 1.0, 0, h * 0.5), scale=(0.5, 0.25, 1), seg=8, rings=6)
    return p


def plate(R, loc, r=0.13, col="#f3e4c4"):
    frustum("pl", r, r * 0.8, 0.02, toon(col, rim=0.4), R, loc=loc, seg=14)


def stone_block_hearth(R, w, h, d, col="#a8a09a"):
    box("hb", (w, d, h), ST(col, "#8c848a", plane="xz", scale=2.8, bump=1.0, wear=0.5), R, base=True)


# ==================================================================== INN
def i_board(R):
    box("fr", (2.35, 0.09, 1.95), WD("#5a3a24", "#4a2e1c", scale=3), R, loc=(0, -0.045, 0.98))
    box("ck", (2.15, 0.05, 1.75), tex_toon("plain", "#c49a64", "#a9824e", scale=7, plane="xz", bump=1.2, wear=0, rim=0.2), R, loc=(0, -0.09, 0.98))
    rnd = random.Random(4)
    tints = [("#f3e8cc", "#2a3a8a"), ("#efe0b0", "#4a2a2a"), ("#e8d8c0", "#2a4a3a"), ("#f6efe0", "#3a2a5a")]
    notes = []
    for i in range(10):
        x = -0.8 + (i % 4) * 0.55 + rnd.uniform(-0.08, 0.08)
        z = 1.55 - (i // 4) * 0.55 + rnd.uniform(-0.06, 0.06) - 0.02
        a, b = tints[i % 4]
        paper_sheet(R, (x, -0.125, z), (0.4, 0.48), rot=(0, RAD(rnd.uniform(-6, 6)), 0), a=a, b=b, scale=4.2)
        ellipsoid("pin", 0.032, toon(["#c44b3f", "#e8b04a", "#4f7ad8"][i % 3], rim=0.6), R, loc=(x, -0.15, z + 0.2), seg=6, rings=4)
        notes.append((x, z + 0.2))
    if T():
        # one thin teal thread ties every note and leaves towards the north (up-right)
        pts = [(n[0], -0.16, n[1]) for n in notes[:4]] + [(n[0], -0.16, n[1]) for n in notes[4:8][::-1]]
        tthread(R, pts + [(1.0, -0.17, 1.9), (1.5, -0.2, 2.5), (2.4, -0.25, 3.2)], 0.012, 3.0)
        halo(R, (0.6, -0.2, 1.6), 0.9, 0.12)
        cobweb(R, (-1.05, -0.1, 1.9), 0.4)


def i_guestbook(R):
    top = lectern(R, (0, 0, 0), 1.05, 0.72, "#7a4a2a")
    open_book(top, (0, 0, 0.04), 0.66, 0.4, "wine", lines=6)
    # signature lines: dark ink; one glowing line in truth
    for k in range(5):
        box("ink", (0.2, 0.012, 0.012), toon("#3a2a22", rim=0), top, loc=(-0.17, 0.0 - 0.1 + k * 0.05, 0.062), rot=(0, 0, 0))
    if T():
        box("sig", (0.2, 0.014, 0.014), glow(TEAL, 4), top, loc=(0.17, 0.02, 0.066))
        halo(top, (0.17, 0.0, 0.1), 0.34, 0.35)
    # quill in an inkwell
    frustum("iw", 0.05, 0.045, 0.07, toon("#1f2f66", rim=0.5), top, loc=(0.34, -0.08, 0.03), seg=8)
    link_cyl("qu", (0.34, -0.08, 0.1), (0.5, -0.04, 0.4), 0.008, toon("#f3e4c4", rim=0.3), top, seg=4)
    ellipsoid("qf", 0.05, toon("#f3e4c4", rim=0.3), top, loc=(0.44, -0.05, 0.28), scale=(0.35, 0.12, 1.8), rot=(0, RAD(-14), 0), seg=8, rings=5)
    candle(R, (-0.45, 0.1, 1.1), 0.12, not T())
    if T():
        cobweb(R, (0.3, 0.2, 1.4), 0.4)


def i_key(R):
    box("bd", (1.55, 0.09, 0.3), WD("#5a3a24", "#4a2e1c", scale=3), R, loc=(0, -0.045, 0.95))
    for k in range(6):
        x = -0.65 + k * 0.26
        ellipsoid("hk", 0.03, toon("gold", rim=0.5), R, loc=(x, -0.1, 0.9), seg=6, rings=4)
        if k == 3:
            continue
        link_cyl("rg", (x, -0.1, 0.9), (x, -0.1, 0.75), 0.008, toon("#c9bfae", rim=0.5), R, seg=3)
        key_obj(R, (x, -0.12, 0.73), "#c9bfae" if k % 2 else "gold", 0.26)
        box("tag", (0.1, 0.02, 0.12), toon("#a06a3e", rim=0.2), R, loc=(x + 0.0, -0.13, 0.5))
    # key of room 4: big wooden tag
    x = -0.65 + 3 * 0.26
    link_cyl("rg", (x, -0.1, 0.9), (x, -0.1, 0.72), 0.01, toon("gold", rim=0.5), R, seg=3)
    key_obj(R, (x, -0.13, 0.7), "gold", 0.34)
    frustum("tg", 0.1, 0.1, 0.03, WD("#d9b05a", "#b88a3a", scale=4), R, loc=(x, -0.15, 0.3), rot=(RAD(90), 0, 0), seg=14)
    box("tgm", (0.08, 0.02, 0.012), toon("#3a2a22", rim=0), R, loc=(x, -0.185, 0.3))
    box("tgm", (0.012, 0.02, 0.08), toon("#3a2a22", rim=0), R, loc=(x + 0.03, -0.185, 0.3))
    if T():
        tthread(R, [(x, -0.12, 0.9), (x + 0.05, -0.16, 1.4), (x + 0.5, -0.2, 2.0), (x + 1.0, -0.3, 2.6)], 0.012, 3.2)
        tthread(R, [(x, -0.13, 0.45), (x - 0.04, -0.14, 0.7)], 0.01, 3.0)
        halo(R, (x, -0.2, 0.6), 0.45, 0.28)


def i_rules(R):
    box("fr", (0.95, 0.07, 1.3), WD("#6a4630", "#553622", scale=3), R, loc=(0, -0.035, 0.65))
    box("pp", (0.8, 0.05, 1.15), tex_toon("paper", "#efe0b0", "#4a2a2a", scale=3.5, plane="xz", bump=0.1, wear=0), R, loc=(0, -0.075, 0.65))
    for k in range(4):
        box("hd", (0.5, 0.012, 0.045), toon("#3a2a22", rim=0), R, loc=(0, -0.105, 1.0 - k * 0.25))
        box("tx", (0.62 - 0.1 * (k % 2), 0.012, 0.025), toon("#6a5a4a", rim=0), R, loc=(0.0, -0.105, 0.93 - k * 0.25))
        ellipsoid("nm", 0.045, toon("#c44b3f", rim=0.4), R, loc=(-0.33, -0.11, 1.0 - k * 0.25), seg=6, rings=4)
    ellipsoid("seal", 0.07, toon("#a02a2a", rim=0.4), R, loc=(0.28, -0.1, 0.18), scale=(1, 0.3, 1), seg=8, rings=5)
    if T():
        tthread(R, [(-0.33, -0.12, 1.0), (0.3, -0.12, 0.95), (-0.3, -0.12, 0.76), (0.3, -0.12, 0.7), (-0.3, -0.12, 0.5), (0.3, -0.12, 0.45), (-0.3, -0.12, 0.26)], 0.01, 3.0)
        cobweb(R, (-0.46, -0.1, 1.28), 0.3)


def i_kettle(R):
    round_table(R, (0, 0, 0), 0.5, 0.78, "#a06a3e", cloth="#f3e4c4")
    p = pivot("kt", (0, 0, 0.79), R)
    ellipsoid("body", 0.2, toon("#c0693f", rim=0.7), p, loc=(0, 0, 0.2), scale=(1, 1, 0.85), seg=16, rings=10)
    frustum("lid", 0.1, 0.06, 0.05, toon("#c0693f", rim=0.7), p, loc=(0, 0, 0.35), seg=10)
    ellipsoid("kn", 0.035, toon("gold", rim=0.5), p, loc=(0, 0, 0.42), seg=6, rings=4)
    link_cyl("sp", (0.16, 0, 0.16), (0.34, 0, 0.34), 0.03, toon("#c0693f", rim=0.7), p, seg=6, r2=0.015)
    tube("hd", [(-0.17, 0, 0.3), (-0.26, 0, 0.45), (-0.05, 0, 0.5), (0.08, 0, 0.42)], 0.016, toon("leather_d", rim=0.3), p)
    mug(R, (-0.32, -0.15, 0.78), col="#f3e4c4")
    mug(R, (0.3, -0.18, 0.78), col="#4f7ad8")
    for k in range(3):
        ellipsoid("ap", 0.07, toon("#c44b3f", rim=0.5), R, loc=(0.02 + k * 0.1, -0.3, 0.84), seg=8, rings=6)
    if not T():
        steam(p, (0.34, 0, 0.42), 3, 0.55)
    else:
        for k in range(3):
            tthread(p, [(0.34, 0, 0.4), (0.2 - k * 0.12, -0.1, 0.7), (-0.2 - k * 0.2, -0.2, 0.95), (-0.8 - k * 0.2, -0.3, 1.05)], 0.008, 2.6)


def i_lost(R):
    p = pivot("lostbox", (0, 0, 0), R)
    wm = WD("#8a5a30", "#6a4220", scale=4, bump=0.8)
    box("bx", (1.2, 0.8, 0.5), wm, p, base=True, bevel=0.02)
    box("in", (1.1, 0.7, 0.04), toon("#2a1e1a", rim=0), p, loc=(0, 0, 0.5))
    for sx in (-1, 1):
        box("bd", (0.07, 0.82, 0.52), WDT(), p, loc=(sx * 0.5, 0, 0), base=True)
    # items
    ellipsoid("hat", 0.28, FAB("weave", "#4f7ad8", "#f3e4c4", scale=12), p, loc=(-0.25, -0.05, 0.62), scale=(1.1, 1.0, 0.45), seg=12, rings=8)
    frustum("hatc", 0.14, 0.12, 0.2, FAB("weave", "#4f7ad8", "#f3e4c4", scale=12), p, loc=(-0.25, -0.05, 0.6), seg=10)
    box("scarf", (0.7, 0.14, 0.06), FAB("knit", "#c44b3f", "#e8b04a", scale=14, plane="xy"), p, loc=(0.18, 0.15, 0.58), rot=(0, 0, RAD(-14)))
    ellipsoid("shoe", 0.14, toon("leather", rim=0.4), p, loc=(0.28, -0.15, 0.58), scale=(1.5, 0.8, 0.8), seg=10, rings=6)
    ellipsoid("mit", 0.09, FAB("knit", "#35b39a", "#f3e4c4", scale=14), p, loc=(-0.1, 0.2, 0.55), scale=(1, 0.6, 1.2), seg=8, rings=6)
    book(p, (0.35, 0.22, 0.54), (0.26, 0.2, 0.05), "forest", rot=0.6)
    lantern2(p, (0.5, -0.15, 0.58), "amber", 3, 0.2, hang=False) if not T() else None
    frustum("lh", 0.05, 0.05, 0.02, toon("#3a3a44", rim=0), p, loc=(0, 0, 0.1), seg=4)
    # umbrella-less: a walking stick leans against it
    link_cyl("cane", (0.62, 0.1, 0.0), (0.72, 0.18, 1.0), 0.025, WDT(), p, seg=5)
    if T():
        # doubled thread folded under the box, ends not cut
        tthread(p, [(-0.5, -0.45, 0.02), (-0.2, -0.55, 0.03), (0.2, -0.5, 0.02), (0.5, -0.45, 0.03), (0.2, -0.38, 0.02), (-0.2, -0.42, 0.03), (-0.5, -0.45, 0.02)], 0.013, 3.4)
        halo(p, (0, -0.5, 0.1), 0.6, 0.18, TEAL, 1.0, (1.6, 0.6, 0.4))
        cobweb(p, (-0.6, 0.35, 0.9), 0.4)


def i_hearth(R):
    p = R
    box("pl", (2.6, 1.0, 0.18), ST("#8c848a", "#74707a", plane="xz", scale=3, bump=1.0), p, base=True)
    box("bk", (2.2, 0.8, 1.35), ST("#a8a09a", "#8c848a", plane="xz", scale=2.6, bump=1.0, wear=0.6, soot=0.3), p, loc=(0, 0.05, 0.18), base=True)
    # firebox opening
    box("op", (1.3, 0.1, 0.95), toon("#1a1214", rim=0), p, loc=(0, -0.38, 0.34), base=True)
    frustum("arch", 0.65, 0.65, 0.1, toon("#1a1214", rim=0), p, loc=(0, -0.38, 1.27), rot=(RAD(90), 0, 0), seg=18)
    for x in (-0.8, 0.8):
        box("jb", (0.22, 0.14, 1.2), ST("#b9b0a2", "#9a9288", plane="xz", scale=3), p, loc=(x, -0.42, 0.18), base=True)
    box("lint", (1.8, 0.16, 0.2), ST("#b9b0a2", "#9a9288", plane="xz", scale=3), p, loc=(0, -0.44, 1.55))
    # chimney breast
    box("ch", (1.9, 0.7, 2.2), ST("#a8a09a", "#8c848a", plane="xz", scale=2.6, bump=1.0, wear=0.6, soot=0.35), p, loc=(0, 0.2, 1.7), base=True)
    box("mt", (2.3, 0.6, 0.1), WD("#5a3a24", "#4a2e1c", scale=3), p, loc=(0, -0.2, 1.75))
    jar(p, (-0.7, -0.2, 1.8), 0.1, 0.22, content="#d68f3a")
    candle(p, (0.6, -0.2, 1.8), 0.18, not T())
    frustum("jug", 0.1, 0.08, 0.28, toon("#4f7a8a", rim=0.5), p, loc=(0.2, -0.2, 1.8), seg=10)
    # crane + pot
    link_cyl("cr", (-0.55, -0.3, 0.2), (-0.55, -0.3, 1.2), 0.03, toon("#2a2a30", rim=0.5), p, seg=5)
    link_cyl("ca", (-0.55, -0.3, 1.2), (0.0, -0.3, 1.1), 0.03, toon("#2a2a30", rim=0.5), p, seg=5)
    link_cyl("ch2", (0.0, -0.3, 1.1), (0.0, -0.3, 0.8), 0.012, toon("#2a2a30", rim=0.5), p, seg=4)
    ellipsoid("pot", 0.17, toon("#2a2a30", rim=0.6), p, loc=(0.0, -0.3, 0.68), scale=(1, 1, 0.8), seg=12, rings=8)
    fire(p, (0, -0.28, 0.22), 1.0, not T())
    if T():
        cobweb(p, (-0.95, -0.45, 1.5), 0.45)
        cobweb(p, (0.95, -0.45, 2.2), 0.5, rot=(0, RAD(-90), 0))


def i_long_table(R):
    table(R, (0, 0, 0), 4.2, 0.95, 0.82, "#a06a3e", "#6a4220")
    bench(R, (0, -0.85, 0), 3.9, 0.4, 0.5, "#8a5a30")
    bench(R, (0, 0.85, 0), 3.9, 0.4, 0.5, "#8a5a30")
    if not T():
        for k in range(5):
            x = -1.7 + k * 0.85
            plate(R, (x, -0.22, 0.83), 0.14)
            plate(R, (x + 0.15, 0.24, 0.83), 0.14, "#e8d8b0")
            mug(R, (x - 0.15, -0.05, 0.83), col=["#c9b48a", "#4f7ad8", "#c44b3f"][k % 3])
        candle(R, (-0.4, 0, 0.83), 0.2, True)
        candle(R, (1.2, 0, 0.83), 0.2, True)
        frustum("loaf", 0.14, 0.14, 0.12, toon("#c98a3c", rim=0.4), R, loc=(0.5, 0.05, 0.83), rot=(0, RAD(90), 0), seg=8)
    else:
        mug(R, (1.4, -0.1, 0.83), col="#7a7a86")
        candle(R, (-0.4, 0, 0.83), 0.1, False)
        cobweb(R, (-2.0, 0.4, 0.95), 0.5)


def i_barrels(R):
    barrel(R, (-0.3, 0.0, 0.0), 0.34, 0.7)
    barrel(R, (0.4, -0.05, 0.0), 0.3, 0.62, "#8a5a30")
    barrel(R, (0.05, 0.3, 0.7), 0.28, 0.58, "#a06a3e")
    box("rk", (1.5, 0.12, 0.08), WDT(), R, loc=(0.05, -0.2, 0.0))
    frustum("tap", 0.03, 0.03, 0.14, toon("gold", rim=0.5), R, loc=(0.05, -0.0, 0.72), rot=(RAD(90), 0, 0), seg=6)
    if T():
        cobweb(R, (-0.5, 0.2, 1.2), 0.4)


def i_coat_rack(R):
    frustum("pole", 0.04, 0.035, 2.0, WDT(), R, seg=8)
    frustum("foot", 0.3, 0.3, 0.07, WDT(), R, seg=12)
    for k in range(5):
        a = k * 1.256 + 0.3
        link_cyl("arm", (0, 0, 1.85), (math.cos(a) * 0.3, math.sin(a) * 0.3, 1.98), 0.02, WDT(), R, seg=5)
    ellipsoid("hat", 0.3, FAB("weave", "#7a5a3a", "#5a3a24", scale=12), R, loc=(0.3, 0.05, 1.93), scale=(1.0, 1.0, 0.18), seg=14, rings=6)
    frustum("hatc", 0.13, 0.1, 0.18, FAB("weave", "#7a5a3a", "#5a3a24", scale=12), R, loc=(0.3, 0.05, 1.95), seg=10)
    box("shawl", (0.34, 0.06, 0.8), FAB("knit", "#4f7ad8", "#f3e4c4", scale=12), R, loc=(-0.25, -0.2, 1.1))
    lantern2(R, (0.1, -0.3, 1.9), "amber", 3, 0.2, hang=True) if not T() else None


def i_plant(R):
    plant_pot(R, (0, 0, 0), 0.32, 0.5, kind="fern", seed=21, leaf="leaf3", pot="#8a5a40")
    for k in range(5):
        a = k * 1.3
        ellipsoid("big", 0.2, toon(["leaf1", "leaf2", "leaf3"][k % 3], rim=0.4), R, loc=(math.cos(a) * 0.3, math.sin(a) * 0.25, 0.9 + 0.12 * k), scale=(1, 0.4, 1.6), rot=(0, 0, a), seg=10, rings=8)
    if T():
        dead_plant(R, (0, 0, 0.5), 0.9, seed=6, n=9)


# ==================================================================== BELL TOWER
def b_rope(R):
    # bell rope hanging from the ceiling: striped woollen sally grip, tail hanging
    rm = tex_toon("weave", "#c9b48a", "#8a7450", scale=40, plane="xz", bump=1.0, rim=0.3, ao=0)
    if not T():
        tube("rp", [(0, 0, 4.95), (0.02, 0, 3.6), (0, 0, 2.2)], 0.06, rm, R)
        # sally: red/white/blue striped fluffy grip
        for k in range(8):
            c = ["#c44b3f", "#f6efe0", "#4f7ad8"][k % 3]
            ellipsoid("sl", 0.095, FAB("knit", c, c, scale=14, bump=1.0), R, loc=(0, 0, 2.2 - k * 0.12), scale=(1, 1, 0.9), seg=10, rings=6)
        tube("tl", [(0, 0, 1.25), (0.02, 0, 1.0), (0.0, 0.0, 0.9)], 0.04, rm, R)
        # soft oil glints from years of hands
        for k in range(3):
            ellipsoid("oil", 0.05, glow("#ffd890", 0.8, alpha=0.5, soft=True), R, loc=(0, -0.08, 3.0 - k * 0.3), scale=(1, 0.4, 2.5), seg=6, rings=4)
    else:
        # cut: the rope ends at 3.1, a short piece dangles lower; weaver's knot at the cut
        tube("rp", [(0, 0, 4.95), (0.03, 0, 4.2), (0.0, 0, 3.15)], 0.06, rm, R)
        tube("rp2", [(0.3, -0.05, 2.5), (0.34, -0.06, 1.9), (0.3, -0.03, 1.4)], 0.04, rm, R)
        for k in range(4):
            ellipsoid("sl", 0.095, FAB("knit", "#9aa0aa", "#7a808a", scale=14, bump=1.0), R, loc=(0.3, -0.03, 1.4 - k * 0.12), scale=(1, 1, 0.9), seg=10, rings=6)
        weaver_knot(R, (0.0, -0.12, 3.05), 0.1)
        tthread(R, [(0.1, -0.1, 3.0), (0.2, -0.1, 2.8), (0.3, -0.06, 2.5)], 0.012, 3.0)
        halo(R, (0.15, -0.1, 3.0), 0.6, 0.25)
        cobweb(R, (0.25, 0.0, 4.9), 0.5)
    # floor hole ring where the rope would reach the bell room
    frustum("ring", 0.5, 0.5, 0.05, ST("#8a847c", "#6e6a6a", plane="xy", scale=4), R, seg=18)
    frustum("hole", 0.34, 0.34, 0.06, toon("#1a1620", rim=0), R, seg=18)


def b_oil(R):
    p = pivot("oil", (0, 0, 0), R)
    box("crate", (0.9, 0.6, 0.45), WD("#8a5a30", "#6a4220", scale=4), p, base=True, bevel=0.02)
    box("crt", (0.95, 0.65, 0.05), WDT(), p, loc=(0, 0, 0.45))
    # oil can: tin body with long spout
    frustum("can", 0.18, 0.18, 0.32, toon("#b9b0a2", rim=0.7), p, loc=(-0.2, 0, 0.5), seg=14)
    frustum("cap", 0.12, 0.08, 0.06, toon("#b9b0a2", rim=0.7), p, loc=(-0.2, 0, 0.82), seg=12)
    link_cyl("sp", (-0.05, 0, 0.7), (0.3, -0.05, 0.9), 0.025, toon("#b9b0a2", rim=0.7), p, seg=6, r2=0.012)
    tube("hd", [(-0.2, 0.12, 0.8), (-0.2, 0.2, 0.95), (-0.2, 0.22, 0.6)], 0.018, toon("#b9b0a2", rim=0.7), p)
    # oily rag
    box("rag", (0.34, 0.26, 0.04), FAB("weave", "#8a7a68", "#6a5a48", scale=10, plane="xy"), p, loc=(0.2, 0.1, 0.5), rot=(0, 0, RAD(25)))
    # glowing finger-smudges of oil on the crate edge and the rag
    for k in range(4):
        ellipsoid("sm", 0.045, glow("#ffd890" if not T() else TEAL, 1.2 if not T() else 3.0, alpha=0.8, soft=True), p, loc=(0.1 + k * 0.1, -0.3, 0.34 - 0.02 * k), scale=(1, 0.3, 1.8), seg=6, rings=4)
    halo(p, (0.2, -0.2, 0.55), 0.5, 0.15, "#ffd890" if not T() else TEAL, 0.8)
    if T():
        cobweb(p, (0.45, 0.25, 0.8), 0.35)


def b_notes(R):
    top = lectern(R, (0, 0, 0), 1.1, 0.7, "#6a4630")
    open_book(top, (0, 0, 0.04), 0.62, 0.42, "forest")
    # stair-stepped lines: each line starts a bit lower and further right
    for k in range(5):
        box("ln", (0.34 - 0.04 * k, 0.012, 0.012), toon("#3a2a22", rim=0), top, loc=(-0.2 + 0.05 * k, 0.12 - 0.065 * k, 0.062))
    if T():
        for k in range(4):
            tthread(top, [(-0.12 + 0.05 * k, 0.12 - 0.065 * k, 0.07), (-0.12 + 0.05 * (k + 1), 0.12 - 0.065 * (k + 1), 0.07)], 0.007, 3.0)
    ellipsoid("bm", 0.06, toon("gold", rim=0.5), top, loc=(0.36, 0.1, 0.06), scale=(1, 1, 0.4), seg=8, rings=5)
    if T():
        cobweb(R, (-0.4, 0.2, 1.35), 0.35)


def b_pigeon(R):
    # perch stand with a straw nest and a white pigeon; thread from its leg to the bell
    frustum("fo", 0.3, 0.32, 0.06, WDT(), R, seg=10)
    frustum("po", 0.045, 0.045, 1.25, WDT(), R, seg=8)
    link_cyl("pe", (-0.45, 0, 1.25), (0.45, 0, 1.25), 0.035, WDT(), R, seg=6)
    ellipsoid("nst", 0.28, tex_toon("thatch", "#d2a24e", "#b38238", scale=6, plane="xy", bump=1.0), R, loc=(0, 0, 1.3), scale=(1, 0.8, 0.3), seg=12, rings=6)
    col = "#f3f0ee" if not T() else "#c9ced8"
    gm = tex_toon("stripes", col, "#d8d8e4", scale=18, plane="xz", bump=0.4, rim=0.5, ao=0.3)
    ellipsoid("bd", 0.2, gm, R, loc=(0, 0, 1.55), scale=(1.15, 0.8, 0.95), seg=14, rings=10)
    ellipsoid("hd", 0.12, toon(col, rim=0.5), R, loc=(-0.2, -0.08, 1.78), seg=10, rings=8)
    frustum("bk", 0.04, 0.0, 0.1, toon("#e8a050", rim=0.3), R, loc=(-0.3, -0.12, 1.78), rot=(0, RAD(-90), 0), seg=4)
    ellipsoid("ey", 0.025, toon("#1a1220", rim=0), R, loc=(-0.26, -0.17, 1.82), seg=5, rings=4)
    tube("tl", [(0.22, 0.02, 1.52), (0.42, 0.04, 1.42), (0.5, 0.05, 1.32)], 0.07, toon("#e0dce4" if not T() else "#a9aebb", rim=0.4), R)
    ellipsoid("wg", 0.17, toon("#e6e2ea" if not T() else "#b4b9c6", rim=0.4), R, loc=(0.06, 0.1, 1.55), scale=(1.3, 0.25, 0.7), rot=(0, 0, RAD(-20)), seg=10, rings=6)
    # leg thread (white; glowing teal in truth) going up
    th = [(-0.06, -0.02, 1.4), (-0.2, 0.0, 2.2), (-0.3, 0.1, 3.2), (-0.2, 0.2, 4.4)]
    if T():
        tthread(R, th, 0.012, 3.2)
        halo(R, (-0.2, 0.0, 2.2), 0.7, 0.14)
    else:
        tube("lg", th[:2], 0.007, toon("#f3f0ee", rim=0), R)
    return {"cell": (384, 560), "anchor": (192, 460)}


def b_window(R):
    # arched stone window with shutters; market roofs inside; threads gather to one thick one in truth
    sm = ST("#a79e92", "#8a847c", plane="xz", scale=3, bump=1.0, wear=0.5)
    w, h = 1.5, 2.4
    box("fl", (w + 0.5, 0.2, h * 0.6), sm, R, loc=(-0.0, -0.1, h * 0.3 + 0.02))
    frustum("ar", (w + 0.5) / 2, (w + 0.5) / 2, 0.2, sm, R, loc=(0, -0.0, h * 0.6 + 0.02), rot=(RAD(90), 0, 0), seg=20)
    # inner sky
    box("sk", (w, 0.05, h * 0.6), glow("#ffb080" if not T() else "#4a5a82", 1.4 if not T() else 0.7), R, loc=(0, -0.2, h * 0.3 + 0.02))
    frustum("ska", w / 2, w / 2, 0.05, glow("#e8806a" if not T() else "#33406a", 1.2 if not T() else 0.6), R, loc=(0, -0.2, h * 0.6 + 0.02), rot=(RAD(90), 0, 0), seg=20)
    # market roofs silhouette
    for k, (x, hh, ww) in enumerate(((-0.45, 0.25, 0.4), (0.0, 0.34, 0.36), (0.45, 0.2, 0.34))):
        box("rf", (ww, 0.04, hh), toon("#2a2250" if not T() else "#10142a", rim=0), R, loc=(x, -0.235, 0.05 + hh / 2))
        frustum("rt", ww * 0.7, 0.0, 0.18, toon("#2a2250" if not T() else "#10142a", rim=0), R, loc=(x, -0.235, 0.05 + hh), rot=(RAD(90), 0, 0), seg=3)
    # sill + shutters
    box("sil", (w + 0.8, 0.45, 0.1), sm, R, loc=(0, -0.15, 0.0))
    wm = WD("#6a4a30", "#54382a", scale=3, bump=0.7)
    for s in (-1, 1):
        box("sh", (0.5, 0.05, 1.6), wm, R, loc=(s * (w / 2 + 0.55), -0.2, 1.0), rot=(0, 0, s * RAD(-8)))
    if not T():
        flower_box(R, (0, -0.4, 0.07), 1.3)
    # threads from the market gather into one thick thread rising to the spire
    if T():
        cx = 0.0
        for k, x in enumerate((-0.6, -0.3, 0.0, 0.3, 0.6)):
            tthread(R, [(x, -0.26, 0.4 + 0.1 * (k % 2)), (x * 0.6, -0.27, 0.9), (x * 0.2, -0.28, 1.4)], 0.008, 2.6)
        tthread(R, [(0, -0.28, 1.4), (0.0, -0.28, 1.9), (0.1, -0.3, 2.5), (0.2, -0.32, 3.3)], 0.035, 3.4)
        halo(R, (0, -0.3, 1.6), 0.8, 0.22)
        crack_fx(R, (0.5, -0.12, 2.2), 0.8)
    return {"cell": (384, 400), "anchor": (192, 300)}


def b_stairs(R, white=False):
    # spiral stair base: central stone column with winding steps (each step has a solid riser block under it)
    stn = ST("#c4bbae", "#a79e92", plane="xy", scale=3, bump=1.0, wear=0.4) if not white else PL("#f0ece4", "#dcd6ca", plane="xy", wear=0.3)
    dk = ST("#8a847c", "#6e6a6a", plane="xz", scale=3, bump=1.0, wear=0.6) if not white else PL("#c9c2b4", "#b4ad9e", plane="xz", wear=0.5)
    n, rise, da = 12, 0.36, 0.56
    frustum("col", 0.3, 0.26, 0.2 + n * rise + 0.3, ST("#a79e92", "#8a847c", plane="xz", scale=3, bump=1.0, wear=0.5) if not white else PL("#e8e2d6", "#d4cec0", plane="xz", wear=0.4), R, seg=14)
    for i in range(n):
        a = i * da + 0.3
        z = 0.2 + i * rise
        p = pivot("stp", (0, 0, z), R, rot=(0, 0, a))
        box("st", (1.0, 0.62, 0.12), stn, p, loc=(0.62, 0, 0))
        box("rs", (0.96, 0.5, rise - 0.08), dk, p, loc=(0.62, 0, -0.12 - (rise - 0.08) / 2 + 0.06))
    frustum("base", 1.05, 1.1, 0.2, stn, R, seg=18)
    pts = [(math.cos(i * da + 0.3) * 1.18, math.sin(i * da + 0.3) * 1.18, 0.2 + i * rise + 0.8) for i in range(n)]
    if white:
        tube("rl", pts, 0.035, toon("#c44b3f", rim=0.4), R)
    else:
        rope(R, pts, 0.03)
    for i in range(0, n, 3):
        p = pts[i]
        link_cyl("bal", (p[0], p[1], p[2] - 0.8), p, 0.02, toon("#3a3a44", rim=0.5), R, seg=4)
    if T():
        cobweb(R, (0.5, 0.4, 2.6), 0.5)
    return {"cell": (512, 560), "anchor": (256, 440)}


def b_bell_wheel(R):
    # wooden bell wheel on an A-frame with a rope winding round it
    wd = WD("#6a4630", "#553622", scale=3, bump=0.8)
    for s in (-1, 1):
        link_cyl("lg", (s * 0.7, 0, 0), (s * 0.7, 0, 1.0), 0.07, wd, R, seg=6)
        link_cyl("lg", (s * 0.7, 0.25, 0), (s * 0.7, 0, 1.0), 0.06, wd, R, seg=6)
        link_cyl("lg", (s * 0.7, -0.25, 0), (s * 0.7, 0, 1.0), 0.06, wd, R, seg=6)
    link_cyl("ax", (-0.85, 0, 1.0), (0.85, 0, 1.0), 0.05, toon("#3a3a44", rim=0.5), R, seg=8)
    wr = 0.95
    wp = pivot("wh", (0.0, -0.05, 1.0), R, rot=(0, 0, 0))
    frustum("rim", wr, wr, 0.14, wd, wp, rot=(RAD(90), 0, 0), seg=32, caps=(False, False))
    frustum("rim2", wr - 0.08, wr - 0.08, 0.14, WDT(), wp, rot=(RAD(90), 0, 0), seg=32, caps=(False, False))
    for k in range(8):
        a = k * math.pi / 4
        link_cyl("sp", (0, 0, 0), (math.cos(a) * wr, 0, math.sin(a) * wr), 0.035, wd, wp, seg=5)
    ellipsoid("hub", 0.1, toon("gold", rim=0.5), wp, scale=(1, 0.8, 1), seg=8, rings=6)
    for k in range(6):
        a = 0.3 + k * 0.22
        ellipsoid("rw", 0.05, toon("#c9b48a", rim=0.3), wp, loc=(math.cos(a) * (wr + 0.02), -0.09, math.sin(a) * (wr + 0.02)), seg=6, rings=4)
    rope(R, [(0.0 - wr * 0.3, -0.1, 1.0 + wr), (-wr * 0.9, -0.1, 1.0 + wr * 0.4), (-wr * 1.05, -0.1, 0.5), (-wr * 1.05, -0.1, 0.05)], 0.035)
    if T():
        for a in (0.9, 3.4):
            crack_fx(wp, (math.cos(a) * 0.5, -0.12, math.sin(a) * 0.5), 0.4)
        cobweb(R, (-0.7, 0.0, 1.9), 0.4)
    return {"cell": (384, 400), "anchor": (192, 300)}


def b_rope_coil(R):
    rm = tex_toon("weave", "#c9b48a", "#8a7450", scale=40, plane="xz", bump=1.0, rim=0.3, ao=0)
    for k in range(4):
        frustum("lp", 0.45 - k * 0.04, 0.45 - k * 0.04, 0.09, rm, R, loc=(0, 0, k * 0.09), seg=24)
    frustum("lc", 0.25, 0.25, 0.32, toon("#5a3a24", rim=0.2), R, seg=10) if False else None
    tube("end", [(0.4, -0.2, 0.3), (0.7, -0.4, 0.04), (1.1, -0.3, 0.025)], 0.035, rm, R)
    if T():
        cobweb(R, (-0.3, 0.2, 0.6), 0.3)


def b_crate_pile(R):
    crate(R, (-0.2, 0.0, 0.0), 0.6, 0.1, "#9a6a3e")
    crate(R, (0.5, -0.1, 0.0), 0.5, -0.2, "#8a5a30")
    crate(R, (0.1, 0.0, 0.6), 0.5, 0.3, "#a8723e")
    sack(R, (-0.75, -0.25, 0), 0.26)
    if T():
        cobweb(R, (-0.3, 0.2, 1.1), 0.4)


def b_lantern(R):
    lantern_floor(R, (0, 0, 0), 1.7, "amber", not T())


# ==================================================================== TAILOR
def t_shop(R):
    # giant wooden button sign on an iron bracket + a shelf with the jar of coins
    link_cyl("br", (-0.6, 0.0, 0.0), (0.0, 0.0, 0.0), 0.04, toon("#2a2a30", rim=0.5), R, seg=5)
    bt = pivot("bt", (0, -0.1, 0.0), R)
    frustum("b", 0.62, 0.62, 0.11, WD("#d9b05a", "#b88a3a", scale=3), bt, rot=(RAD(90), 0, 0), seg=28)
    frustum("b2", 0.48, 0.48, 0.05, WD("#c9a04a", "#a8802c", scale=3), bt, loc=(0, -0.09, 0), rot=(RAD(90), 0, 0), seg=28, caps=(True, True))
    for dx, dz in ((-0.14, -0.14), (0.14, -0.14), (-0.14, 0.14), (0.14, 0.14)):
        frustum("h", 0.06, 0.06, 0.08, toon("#2a1e1a", rim=0), bt, loc=(dx, -0.1, dz), rot=(RAD(90), 0, 0), seg=10)
    tube("th", [(-0.14, -0.2, -0.14), (0.14, -0.2, 0.14)], 0.014, toon("#c44b3f", rim=0.2), bt)
    tube("th", [(0.14, -0.2, -0.14), (-0.14, -0.2, 0.14)], 0.014, toon("#c44b3f", rim=0.2), bt)
    for s in (-1, 1):
        link_cyl("ch", (s * 0.25, 0, 0.58), (s * 0.12, 0, 1.0), 0.012, toon("#2a2a30", rim=0.5), R, seg=3)
    # jar of coins on a small wall shelf below
    box("sh", (1.0, 0.3, 0.07), WD("#6a4630", "#553622", scale=3), R, loc=(0.0, -0.15, -1.5))
    jar(R, (0.0, -0.15, -1.46), 0.22, 0.42, content="#e8b04a", lid="leather_d", gl=True)
    for k in range(5):
        frustum("co", 0.06, 0.06, 0.012, glow("#ffd86a", 3.0), R, loc=(0.0 + (k - 2) * 0.1, -0.4, -1.45 + 0.01 * k), rot=(RAD(80), 0, 0), seg=10)
    if T():
        for k in range(5):
            tthread(R, [(0.0 + (k - 2) * 0.05, -0.15, -1.1), (0.0 + (k - 2) * 0.06, -0.15, -0.6), (0.0 + (k - 2) * 0.08, -0.12, 0.0)], 0.006, 2.6, "#ffd86a")
        halo(R, (0, -0.2, -1.2), 0.45, 0.25, "#ffd86a", 1.0)
    return {"cell": (384, 400), "anchor": (192, 300)}


def t_list(R):
    # clip-board with a long order scroll
    box("bd", (0.75, 0.05, 1.15), WD("#6a4630", "#553622", scale=3), R, loc=(0, -0.025, 0.58))
    box("pp", (0.6, 0.03, 0.95), tex_toon("paper", "#f3e8cc", "#3a2a22", scale=3.2, plane="xz", bump=0.1, wear=0), R, loc=(0, -0.06, 0.58))
    for k in range(7):
        box("nm", (0.2, 0.012, 0.03), toon("#3a2a22", rim=0), R, loc=(-0.12 + 0.01 * (k % 3), -0.08, 0.95 - k * 0.12))
        box("sz", (0.13, 0.012, 0.03), toon("#8a3a2e" if k % 2 else "#2a3a8a", rim=0), R, loc=(0.18, -0.08, 0.95 - k * 0.12))
    box("clip", (0.3, 0.06, 0.09), toon("#b9b0a2", rim=0.7), R, loc=(0, -0.09, 1.12))
    ellipsoid("pin", 0.04, toon("#c44b3f", rim=0.5), R, loc=(0, -0.13, 1.2), seg=6, rings=4)
    tube("hg", [(-0.28, -0.04, 1.14), (0, -0.04, 1.4), (0.28, -0.04, 1.14)], 0.008, toon("#d9c9a8", rim=0), R)
    if T():
        tthread(R, [(0.3, -0.1, 0.35), (0.5, -0.12, 0.9), (0.9, -0.15, 1.6), (1.4, -0.2, 2.4)], 0.014, 2.6, "#b9c0d0")
        tthread(R, [(-0.2, -0.1, 0.85), (-0.1, -0.1, 0.8), (0.1, -0.1, 0.9), (0.3, -0.1, 0.35)], 0.008, 2.6, "#b9c0d0")
        cobweb(R, (-0.38, -0.08, 1.14), 0.3)


def t_threads(R):
    # sewing-thread box: wooden tray on a stool with pairs of spools
    stool_round(R, (0, 0, 0), 0.34, 0.48, "#8a5a30")
    box("tr", (0.9, 0.55, 0.12), WD("#9a6a3e", "#7a4e2a", scale=4), R, loc=(0, 0, 0.58), bevel=0.01)
    box("in", (0.8, 0.45, 0.02), toon("#3a2a22", rim=0), R, loc=(0, 0, 0.64))
    cols = ["#c44b3f", "#4f7ad8", "#e8b04a", "#35b39a", "#a07ad8", "#f3e4c4"]
    for i in range(6):
        for j in range(2):
            c = cols[i]
            spool(R, (-0.33 + i * 0.132, -0.1 + j * 0.2, 0.64), 0.055, 0.17, c, False)
    if T():
        tthread(R, [(-0.33, -0.1, 0.85), (-0.1, -0.1, 0.9), (0.2, 0.0, 0.92), (0.4, 0.1, 0.85)], 0.008, 3.0, GREY if False else "#ffffff")
        for i in range(6):
            tthread(R, [(-0.33 + i * 0.132, -0.1, 0.72), (-0.33 + i * 0.132, 0.1, 0.72)], 0.004, 2.5, "#ffffff")
    return {}


def t_mannequin(R):
    # dress form on a wooden tripod stand: padded torso, measuring tape, a loop at the collar
    wd = WD("#8a5a30", "#704826", scale=4)
    frustum("pole", 0.04, 0.04, 1.3, wd, R, loc=(0, 0, 0.1), seg=8)
    for k in range(3):
        a = k * 2.094 + 0.4
        link_cyl("lg", (0, 0, 0.5), (math.cos(a) * 0.4, math.sin(a) * 0.4, 0.0), 0.035, wd, R, seg=5)
    fm = FAB("weave", "#e8d6b0" if not T() else "#b0b0b8", "#c9b48a", scale=22, plane="xz", bump=0.9)
    ellipsoid("bust", 0.3, fm, R, loc=(0, 0, 1.45), scale=(1.1, 0.7, 1.25), seg=16, rings=12)
    ellipsoid("wst", 0.24, fm, R, loc=(0, 0, 1.1), scale=(1.0, 0.65, 0.9), seg=14, rings=10)
    ellipsoid("hip", 0.3, fm, R, loc=(0, 0, 0.85), scale=(1.05, 0.7, 0.55), seg=14, rings=8)
    frustum("nk", 0.1, 0.12, 0.12, fm, R, loc=(0, 0, 1.72), seg=10)
    frustum("cap", 0.1, 0.1, 0.1, toon("gold", rim=0.5), R, loc=(0, 0, 1.84), seg=10)
    ellipsoid("kn", 0.05, toon("gold", rim=0.5), R, loc=(0, 0, 1.97), seg=8, rings=6)
    # pins + tape round the waist
    tube("tp", [(math.cos(t) * 0.255, math.sin(t) * 0.17, 1.08) for t in [i * 0.4 for i in range(17)]], 0.02, toon("#f2d36a", rim=0.3), R)
    for k in range(6):
        ellipsoid("pin", 0.02, toon(["#c44b3f", "#4f7ad8", "#e8b04a"][k % 3], rim=0.5), R, loc=(-0.22 + k * 0.09, -0.19, 1.5 - (k % 2) * 0.1), seg=5, rings=4)
    if T():
        # a small loop at the collar, as if for a thread
        tthread(R, [(0.0, -0.08, 1.78), (0.1, -0.12, 1.9), (0.12, -0.12, 2.05), (0.04, -0.1, 2.1), (-0.02, -0.09, 1.95), (0.0, -0.08, 1.78)], 0.012, 3.4)
        tthread(R, [(0.1, -0.1, 2.0), (0.3, -0.1, 2.6), (0.5, -0.1, 3.4)], 0.008, 2.6)
        halo(R, (0.05, -0.1, 1.95), 0.3, 0.3)
    return {}


def t_basket(R):
    # wicker basket with a folded coat, hanging from a rope that runs up to the ceiling
    wm = FAB("weave", "#b07a46", "#8a5a30", scale=14, bump=1.0)
    frustum("bk", 0.42, 0.34, 0.4, wm, R, loc=(0, 0, 0.3), seg=18)
    frustum("rm", 0.43, 0.43, 0.05, toon("#8a5a30", rim=0.3), R, loc=(0, 0, 0.66), seg=18)
    box("coat", (0.55, 0.38, 0.14), FAB("weave", "#4f6a8a" if not T() else "#6a7280", "#2a3a5a", scale=12, plane="xy"), R, loc=(0, 0, 0.7), rot=(0, 0, RAD(8)))
    box("cl", (0.3, 0.3, 0.1), FAB("weave", "#3a2a22", "#5a3a24", scale=12, plane="xy"), R, loc=(0.05, 0, 0.82), rot=(0, 0, RAD(-10)))
    for s in (-1, 1):
        link_cyl("ha", (s * 0.4, 0, 0.66), (s * 0.1, 0, 1.4), 0.015, toon("#c9b48a", rim=0.2), R, seg=4)
    rope(R, [(0.0, 0, 1.4), (0.0, 0, 3.0), (0.0, 0.0, 5.2)], 0.035)
    ellipsoid("kn", 0.05, toon("#c9b48a", rim=0.2), R, loc=(0, 0, 1.4), seg=6, rings=4)
    if T():
        tthread(R, [(0.03, -0.03, 1.5), (0.06, -0.03, 3.2), (0.0, 0.0, 5.2)], 0.01, 3.0, "#b9c0d0")
        cobweb(R, (0.3, 0.1, 0.9), 0.3)


def t_cloth_shelf(R):
    shelf_unit(R, (0, 0, 0), 2.7, 2.4, 0.5, 3, "#8a5a30")
    cols = [("#c44b3f", "#f3e4c4"), ("#4f7ad8", "#f3e4c4"), ("#e8b04a", "#c44b3f"), ("#35b39a", "#f3e4c4"), ("#a07ad8", "#f3e4c4"), ("#2f7d6f", "#e8b04a")]
    for lv in range(3):
        z0 = 0.06 + lv * 0.78
        # folded cloth stacks along the shelf
        for i in range(5):
            c = cols[(i + lv * 2) % 6]
            k = "stripes" if (i + lv) % 2 == 0 else "weave"
            for j in range(4):
                box("fold", (0.44, 0.4, 0.07), FAB(k, c[0], c[1], scale=10, plane="xy", bump=0.8), R, loc=(-1.05 + i * 0.5, 0.0, z0 + 0.0 + j * 0.07), base=True, rot=(0, 0, RAD(((i + j) % 3 - 1) * 2)))
    for i, c in enumerate(cols):
        cloth_roll(R, (-1.0 + i * 0.4, 0.0, 2.42 + 0.0), 0.34, 0.13, c[0], c[1], "weave", axis="z")
    if T():
        cobweb(R, (-1.3, -0.2, 2.4), 0.5)
        tthread(R, [(0.9, -0.3, 1.0), (1.0, -0.3, 1.6), (1.1, -0.3, 2.2)], 0.008, 2.6, "#b9c0d0")


def t_cutting_table(R):
    table(R, (0, 0, 0), 2.1, 1.0, 0.85, "#c98a52", "#85502c")
    box("clo", (1.6, 0.8, 0.03), FAB("weave", "#c44b3f" if not T() else "#8a8a94", "#f3e4c4", scale=10, plane="xy", bump=0.7), R, loc=(0, 0, 0.87), base=True, rot=(0, 0, RAD(4)))
    # chalk pattern lines + tape + chalk
    link_cyl("pt", (-0.6, -0.1, 0.9), (0.4, 0.15, 0.9), 0.008, toon("#f6efe0", rim=0), R, seg=3)
    link_cyl("pt", (-0.6, 0.2, 0.9), (0.5, -0.2, 0.9), 0.008, toon("#f6efe0", rim=0), R, seg=3)
    box("tape", (0.9, 0.06, 0.012), toon("#f2d36a", rim=0.3), R, loc=(0.2, 0.38, 0.9), rot=(0, 0, RAD(-4)))
    box("chk", (0.07, 0.02, 0.02), toon("#f6efe0", rim=0.2), R, loc=(0.7, -0.2, 0.9))
    for i in range(4):
        pin = ellipsoid("pn", 0.02, toon("#c44b3f", rim=0.5), R, loc=(-0.8 + i * 0.2, -0.3, 0.9), seg=5, rings=4)
    spool(R, (0.8, 0.3, 0.87), 0.06, 0.12, "#4f7ad8")
    for k in range(2):
        box("dr", (0.6, 0.02, 0.2), WD("#b8844e", "#8a5a30", scale=4), R, loc=(-0.45 + k * 0.9, -0.5, 0.45))
        ellipsoid("kn", 0.03, toon("gold", rim=0.5), R, loc=(-0.45 + k * 0.9, -0.52, 0.45), seg=6, rings=4)
    if T():
        cobweb(R, (-0.9, 0.4, 0.95), 0.4)


def t_sewing(R):
    # treadle sewing machine
    iron = toon("#2a2a30", rim=0.6)
    for s in (-1, 1):
        box("lg", (0.07, 0.5, 0.75), iron, R, loc=(s * 0.4, 0, 0), base=True)
        frustum("ft", 0.14, 0.14, 0.03, iron, R, loc=(s * 0.4, 0, 0), seg=10)
    box("trd", (0.7, 0.4, 0.04), iron, R, loc=(0, 0, 0.14), rot=(RAD(6), 0, 0))
    ellipsoid("whl", 0.2, iron, R, loc=(0.35, 0.2, 0.55), scale=(0.2, 1, 1), seg=14, rings=10)
    box("top", (1.05, 0.5, 0.06), WD("#c98a52", "#85502c", scale=3, plane="xy"), R, loc=(0, 0, 0.78))
    box("mb", (0.6, 0.2, 0.09), toon("#1c1c24", rim=0.7), R, loc=(0, 0.05, 0.84))
    box("ar", (0.12, 0.2, 0.34), toon("#1c1c24", rim=0.7), R, loc=(-0.26, 0.05, 0.92))
    box("hd", (0.5, 0.2, 0.1), toon("#1c1c24", rim=0.7), R, loc=(-0.02, 0.05, 1.2))
    link_cyl("nd", (-0.26, -0.06, 1.12), (-0.26, -0.06, 0.88), 0.01, toon("#d9d9e0", rim=0.7), R, seg=4)
    spool(R, (0.14, 0.05, 1.28), 0.05, 0.1, "#c44b3f")
    box("clo", (0.4, 0.3, 0.02), FAB("weave", "#4f7ad8", "#f3e4c4", scale=12, plane="xy"), R, loc=(-0.2, -0.15, 0.82))
    if T():
        tthread(R, [(-0.26, -0.06, 0.9), (-0.3, -0.1, 0.84), (-0.1, -0.2, 0.84)], 0.006, 3.0)
        cobweb(R, (0.4, 0.2, 1.3), 0.3)


def t_mirror(R):
    # tall standing mirror on a swivel frame: dusk-lit glass; black in truth
    wd = WD("#8a5a30", "#704826", scale=4, bump=0.8)
    for s in (-1, 1):
        link_cyl("lg", (s * 0.5, 0, 0), (s * 0.5, 0, 2.2), 0.06, wd, R, seg=6)
        link_cyl("ft", (s * 0.5, -0.4, 0), (s * 0.5, 0.4, 0), 0.05, wd, R, seg=5)
    link_cyl("tp", (-0.55, 0, 2.2), (0.55, 0, 2.2), 0.07, wd, R, seg=6)
    link_cyl("bt", (-0.55, 0, 0.45), (0.55, 0, 0.45), 0.06, wd, R, seg=6)
    frustum("fr", 0.46, 0.46, 0.08, toon("gold", rim=0.6), R, loc=(0, -0.02, 1.34), rot=(RAD(90), 0, 0), seg=24, scale=(1, 1, 1)) if False else None
    ellipsoid("kn", 0.08, toon("gold", rim=0.6), R, loc=(-0.55, 0, 2.3), seg=8, rings=6)
    ellipsoid("kn", 0.08, toon("gold", rim=0.6), R, loc=(0.55, 0, 2.3), seg=8, rings=6)
    if not T():
        box("gl", (0.9, 0.03, 1.7), glow("#a8c8e0", 1.4), R, loc=(0, -0.03, 1.32))
        box("sh", (0.2, 0.031, 1.7), glow("#e8f4ff", 1.8, alpha=0.5), R, loc=(-0.25, -0.05, 1.32), rot=(0, RAD(10), 0))
    else:
        box("gl", (0.9, 0.03, 1.7), toon("#05060c", rim=0.8), R, loc=(0, -0.03, 1.32))
        crack_fx(R, (0.2, -0.06, 2.1), 1.0)
        cobweb(R, (-0.4, -0.05, 2.15), 0.35)
    return {}


def t_hat_stand(R):
    frustum("pole", 0.035, 0.03, 1.6, WDT(), R, seg=8)
    frustum("foot", 0.26, 0.26, 0.06, WDT(), R, seg=12)
    for k, (z, c) in enumerate(((1.15, "#4f7ad8"), (1.4, "#c44b3f"), (1.62, "#e8b04a"))):
        ellipsoid("h", 0.22 - 0.02 * k, FAB("weave", c, "#f3e4c4", scale=12), R, loc=(0, 0, z), scale=(1, 1, 0.55), seg=12, rings=8)
        link_cyl("br", (0, 0, z), (0.18, 0.0, z - 0.04), 0.015, toon("#d9c9a8", rim=0), R, seg=3)
    if T():
        cobweb(R, (0.2, 0.0, 1.7), 0.3)


# ==================================================================== SCHOOL
def s_board(R):
    box("fr", (3.5, 0.1, 2.0), WD("#8a5a30", "#704826", scale=3), R, loc=(0, -0.05, 1.0))
    box("bd", (3.3, 0.06, 1.8), toon("#2f4a3e", rim=0.15), R, loc=(0, -0.1, 1.0))
    box("tr", (3.3, 0.14, 0.05), WD("#8a5a30", "#704826", scale=3), R, loc=(0, -0.14, 0.03))
    for k in range(3):
        box("ch", (0.12, 0.05, 0.03), toon("#f6efe0", rim=0.2), R, loc=(-0.6 + k * 0.2, -0.18, 0.08))
    box("er", (0.22, 0.08, 0.06), FAB("weave", "#3a3a44", "#2a2a30", scale=12), R, loc=(1.2, -0.18, 0.1))
    # chalk drawings: a loop (cloud), dots, a house, arrows
    cl = toon("#f6efe0", rim=0) if not T() else toon("#c9ced8", rim=0)
    if not T():
        for k in range(5):
            tube("c", [(-1.2 + k * 0.4, -0.14, 1.5), (-1.0 + k * 0.4, -0.14, 1.45)], 0.01, cl, R)
        tube("cloud", [(math.cos(t) * 0.35 + 0.9, -0.14, math.sin(t) * 0.22 + 1.3) for t in [i * 0.4 for i in range(17)]], 0.011, cl, R)
        for k in range(4):
            box("dot", (0.05, 0.02, 0.05), cl, R, loc=(-1.2 + k * 0.28, -0.14, 0.9))
        tube("ar", [(-1.2, -0.14, 0.55), (-0.2, -0.14, 0.55)], 0.011, cl, R)
        tube("ar2", [(-0.3, -0.14, 0.62), (-0.2, -0.14, 0.55), (-0.3, -0.14, 0.48)], 0.011, cl, R)
        box("hs", (0.34, 0.02, 0.26), cl, R, loc=(0.4, -0.14, 0.55)) if False else None
    else:
        # chalk lines climb off the board, up the wall to the ceiling, like threads
        for k in range(5):
            x = -1.2 + k * 0.6
            tube("cl", [(x, -0.14, 1.2), (x + 0.05 * math.sin(k), -0.14, 1.7), (x + 0.1, -0.14, 1.95)], 0.012, cl, R)
            tthread(R, [(x + 0.1, -0.12, 2.0), (x + 0.15, -0.1, 2.6), (x + 0.2, -0.1, 3.4)], 0.01, 2.6, "#b9c0d0")
        tthread(R, [(0.0, -0.14, 1.0), (0.0, -0.14, 1.8)], 0.014, 3.2)
        halo(R, (0, -0.14, 1.6), 1.2, 0.1)
        cobweb(R, (-1.7, -0.1, 1.95), 0.4)
    return {"cell": (512, 520), "anchor": (256, 400)}


def s_drawings(R):
    # clothesline with clipped drawings of the cloud with two eyes and fingers
    tube("ln", [(-1.15, -0.04, 0.0), (0, -0.04, -0.18), (1.15, -0.04, 0.0)], 0.01, toon("#d9c9a8", rim=0), R)
    pc = [("#f6efe0", "#4f7ad8"), ("#efe0b0", "#c44b3f"), ("#f6efe0", "#35b39a"), ("#efe8d0", "#a07ad8")]
    for k in range(4):
        x = -0.85 + k * 0.57
        z = -0.18 * (1 - ((x / 1.15) ** 2)) - 0.05
        p = pivot("dr", (x, -0.07, z - 0.28), R, rot=(0, RAD((k % 2) * 6 - 3), 0))
        a, b = pc[k]
        box("pp", (0.48, 0.015, 0.56), tex_toon("paper", a, b, scale=4, plane="xz", bump=0.1, wear=0), p)
        box("sky", (0.4, 0.015, 0.48), toon("#9ad0f0" if not T() else "#7a8a9a", rim=0), p, loc=(0, -0.012, 0))
        for dx, dz, rr in ((0, 0.04, 0.17), (-0.12, -0.0, 0.11), (0.12, -0.01, 0.12)):
            ellipsoid("cl", rr, toon("#ffffff" if not T() else "#cfd4de", rim=0), p, loc=(dx, -0.03, dz), scale=(1, 0.15, 0.8), seg=10, rings=6)
        for s in (-1, 1):
            ellipsoid("ey", 0.04, toon("#ffffff", rim=0), p, loc=(s * 0.06, -0.05, 0.05), scale=(1, 0.2, 1.2), seg=8, rings=6)
            ellipsoid("pu", 0.02, toon("#1a1220" if not T() else TEAL, rim=0) if not T() else glow(TEAL, 3.0), p, loc=(s * 0.06, -0.06, 0.05), seg=6, rings=4)
        for f in range(2):
            tube("fg", [(-0.05 + f * 0.1, -0.05, -0.09), (-0.05 + f * 0.1, -0.05, -0.2)], 0.012, toon("#ffffff" if not T() else "#cfd4de", rim=0), p)
        box("cl", (0.06, 0.03, 0.08), toon("#e8b04a", rim=0.4), p, loc=(0, 0.0, 0.3))
    if T():
        for k in range(4):
            x = -0.85 + k * 0.57
            tthread(R, [(x, -0.1, -0.6), (x + 0.1, -0.1, -1.0), (x + 0.2, -0.1, -1.6)], 0.006, 2.6, "#b9c0d0")
    return {"cell": (400, 300), "anchor": (200, 160)}


def s_notes(R):
    table(R, (0, 0, 0), 1.9, 0.95, 0.85, "#c98a52", "#85502c")
    for k in range(2):
        box("dr", (0.5, 0.02, 0.18), WD("#b8844e", "#8a5a30", scale=4), R, loc=(-0.5 + k * 1.0, -0.48, 0.58))
        ellipsoid("kn", 0.03, toon("gold", rim=0.5), R, loc=(-0.5 + k * 1.0, -0.5, 0.58), seg=6, rings=4)
    # stack of coloured envelopes
    cols = ["#e8b04a", "#4f7ad8", "#c44b3f", "#35b39a", "#a07ad8", "#e8884a", "#f3e4c4", "#4f9a7a"]
    for i in range(8):
        c = cols[i % 8]
        e = box("env", (0.5, 0.34, 0.025), glow(c, 1.4 if not T() else 2.4) if T() else toon(c, rim=0.3), R, loc=(0.35 + (i % 2) * 0.02, 0.0 + (i % 3 - 1) * 0.01, 0.87 + i * 0.027), rot=(0, 0, RAD(i * 7 - 20)), base=False)
        box("fl", (0.5, 0.01, 0.01), toon("#00000030"[:7] if False else "#2a2230", rim=0), R, loc=(0.35, -0.0, 0.875 + i * 0.027), rot=(0, 0, RAD(i * 7 - 20))) if False else None
    for i in range(3):
        ellipsoid("sl", 0.04, toon("#a02a2a", rim=0.4), R, loc=(0.38, -0.03, 1.1 + i * 0.0), scale=(1, 1, 0.3), seg=6, rings=4) if i == 0 else None
    # bell, inkwell and a book
    frustum("bl", 0.07, 0.03, 0.1, toon("gold", rim=0.7), R, loc=(-0.6, 0.15, 0.87), seg=10)
    book(R, (-0.55, -0.15, 0.87), (0.4, 0.3, 0.08), "forest", rot=0.2)
    book(R, (-0.55, -0.15, 0.95), (0.34, 0.26, 0.06), "wine", rot=-0.1)
    chair_wood(R, (0, 0.95, 0), rot=0.0, col="#8a5a30", seat="#4f7ad8")
    if T():
        cobweb(R, (-0.9, 0.4, 0.95), 0.4)
        halo(R, (0.35, 0, 1.0), 0.5, 0.2)


def s_globe(R):
    # globe of the valley on a wooden stand
    wd = WD("#8a5a30", "#704826", scale=4, bump=0.8)
    frustum("ft", 0.3, 0.32, 0.07, wd, R, seg=14)
    frustum("st", 0.06, 0.07, 0.6, wd, R, loc=(0, 0, 0.05), seg=8)
    gp = pivot("gl", (0, 0, 1.0), R, rot=(RAD(-23), 0, RAD(20)))
    ellipsoid("sea", 0.46, toon("#4f8ad8" if not T() else "#4a5a7a", rim=0.5), gp, seg=24, rings=16)
    rnd = random.Random(3)
    for k in range(7):
        a, b = rnd.uniform(0, 6.28), rnd.uniform(-1.0, 1.0)
        ellipsoid("ld", 0.17 + rnd.random() * 0.08, toon(["#6cb257", "#c9b48a", "#4f9a4f", "#8a6a50"][k % 4], rim=0.4), gp,
                  loc=(math.cos(a) * math.cos(b) * 0.4, math.sin(a) * math.cos(b) * 0.4, math.sin(b) * 0.4), scale=(1, 1, 0.5), seg=10, rings=6)
    frustum("ring", 0.52, 0.52, 0.03, toon("gold", rim=0.7), R, loc=(0, 0, 1.0), rot=(RAD(90 - 23), 0, 0), seg=28, caps=(False, False)) if False else None
    # brass meridian
    pts = [(math.sin(t) * 0.52, 0.0, 1.0 + math.cos(t) * 0.52) for t in [i * 0.2 - 1.6 for i in range(17)]]
    pts = [(math.sin(t) * 0.52, 0.0, 1.0 + math.cos(t) * 0.52) for t in [i * 0.4 - 3.14 + 0.4 for i in range(15)]]
    tube("mer", pts, 0.025, toon("gold", rim=0.7), R)
    if T():
        # short cut threads sprouting at the globe's edge
        for k in range(5):
            a = 0.5 + k * 0.7
            x, z = math.cos(a) * 0.48, 1.0 + math.sin(a) * 0.48
            tthread(R, [(x, -0.2, z), (x * 1.15, -0.22, z + 0.05 * k), (x * 1.3, -0.22, z + 0.02)], 0.01, 3.2)
        halo(R, (0, -0.3, 1.0), 0.7, 0.15)
        cobweb(R, (0.2, 0.0, 1.62), 0.3)


def s_bench(R):
    # last bench: schoolbench with desk, glowing carving on the plank
    bw, bd = 2.0, 0.7
    wd = WD("#9a6238", "#7a4a2a", scale=3, bump=0.7)
    for s in (-1, 1):
        box("lg", (0.07, 0.85, 0.75), WDT(), R, loc=(s * (bw / 2 - 0.1), 0.0, 0), base=True)
    box("dk", (bw, 0.5, 0.06), wd, R, loc=(0, 0.25, 0.78), rot=(RAD(-8), 0, 0))
    box("sl", (bw, 0.05, 0.08), WDT(), R, loc=(0, -0.0, 0.8))
    box("st", (bw, 0.3, 0.06), wd, R, loc=(0, -0.45, 0.45))
    box("bk", (bw, 0.05, 0.3), wd, R, loc=(0, -0.58, 0.7)) if False else None
    for s in (-1, 1):
        box("ink", (0.05, 0.05, 0.03), toon("#1f2f66", rim=0.5), R, loc=(s * 0.8, 0.45, 0.84))
    book(R, (-0.4, 0.3, 0.83), (0.34, 0.24, 0.05), "wine", rot=0.2)
    # carving: three marks + glowing line
    carve = glow(TEAL, 3.2) if T() else toon("#4a2e1c", rim=0)
    for k in range(3):
        box("ca", (0.12, 0.02, 0.012), carve, R, loc=(0.4 + k * 0.17, 0.26, 0.835), rot=(RAD(-8), 0, RAD(k * 8 - 8)))
    box("ca2", (0.5, 0.02, 0.012), carve, R, loc=(0.6, 0.38, 0.84), rot=(RAD(-8), 0, 0))
    if T():
        halo(R, (0.6, 0.3, 0.9), 0.5, 0.25)
    return {}


def s_desks_a(R):
    for k in range(2):
        s_bench_unit(R, (-0.55 + k * 1.1, 0, 0))
    return {}


def s_bench_unit(R, loc, w=1.0):
    wd = WD("#9a6238", "#7a4a2a", scale=3, bump=0.7)
    p = pivot("du", loc, R)
    for s in (-1, 1):
        box("lg", (0.06, 0.8, 0.75), WDT(), p, loc=(s * (w / 2 - 0.06), 0.0, 0), base=True)
    box("dk", (w, 0.45, 0.05), wd, p, loc=(0, 0.2, 0.78), rot=(RAD(-8), 0, 0))
    box("st", (w, 0.26, 0.05), wd, p, loc=(0, -0.28, 0.44))
    if not T():
        book(p, (0.0, 0.2, 0.81), (0.3, 0.22, 0.04), "#4f7ad8", rot=0.1)
        box("ink", (0.04, 0.04, 0.03), toon("#1f2f66", rim=0.5), p, loc=(w * 0.36, 0.35, 0.82))
    else:
        cobweb(p, (-w * 0.4, 0.3, 0.9), 0.25)


def s_desks_b(R):
    for k in range(2):
        s_bench_unit(R, (-0.55 + k * 1.1, 0, 0))
    if T():
        tthread(R, [(-0.5, 0.2, 0.9), (-0.45, 0.2, 2.0), (-0.4, 0.2, 3.4)], 0.005, 2.0, "#b9c0d0")
    return {}


def s_bookcase(R):
    shelf_unit(R, (0, 0, 0), 1.6, 2.2, 0.45, 3, "#8a5a30")
    books_row(R, (-0.7, 0, 0.12), 11, 0.5, seed=7)
    books_row(R, (-0.7, 0, 0.85), 10, 0.5, seed=8)
    books_row(R, (-0.7, 0, 1.6), 9, 0.46, seed=9)
    frustum("gl", 0.1, 0.1, 0.2, toon("#4f7ad8", rim=0.5), R, loc=(0.5, 0, 0.82), seg=8) if False else None
    if T():
        cobweb(R, (-0.7, -0.2, 2.2), 0.4)


def s_stove(R):
    iron = toon("#2a2a30", rim=0.6)
    frustum("bd", 0.3, 0.3, 0.75, iron, R, loc=(0, 0, 0.12), seg=14)
    for s in (-1, 1):
        box("ft", (0.08, 0.08, 0.14), iron, R, loc=(s * 0.2, 0, 0), base=True)
    frustum("pipe", 0.07, 0.07, 1.8, iron, R, loc=(0, 0, 0.85), seg=8)
    box("dr", (0.2, 0.02, 0.25), glow("#ff8a2a", 3) if not T() else toon("#1a1a20", rim=0), R, loc=(0, -0.3, 0.4))
    frustum("lid", 0.32, 0.32, 0.04, iron, R, loc=(0, 0, 0.87), seg=14)
    if T():
        cobweb(R, (0.25, 0.1, 1.9), 0.3)


def s_easel(R):
    wd = WD("#a06a3e", "#85502c", scale=4)
    for s in (-1, 1):
        link_cyl("lg", (s * 0.4, 0, 0), (s * 0.12, 0.12, 1.55), 0.035, wd, R, seg=5)
    link_cyl("lg", (0, 0.45, 0), (0, 0.12, 1.55), 0.035, wd, R, seg=5)
    box("sh", (0.9, 0.12, 0.05), wd, R, loc=(0, -0.1, 0.55))
    box("pp", (0.7, 0.03, 0.9), tex_toon("paper", "#f6efe0", "#4f7ad8", scale=3, plane="xz", bump=0.1, wear=0), R, loc=(0, -0.12, 1.05), rot=(RAD(-8), 0, 0))
    ellipsoid("cl", 0.18, toon("#ffffff" if not T() else "#cfd4de", rim=0), R, loc=(0, -0.15, 1.15), scale=(1.4, 0.15, 0.8), seg=10, rings=6)
    for s in (-1, 1):
        ellipsoid("ey", 0.035, toon("#1a1220", rim=0), R, loc=(s * 0.07, -0.17, 1.17), scale=(1, 0.2, 1.2), seg=6, rings=4)
    for i, c in enumerate(("#c44b3f", "#4f7ad8", "#e8b04a")):
        frustum("pt", 0.03, 0.03, 0.05, toon(c, rim=0.3), R, loc=(-0.3 + i * 0.15, -0.1, 0.57), seg=8)


# ==================================================================== FISHER
def f_net(R):
    # fishing net hung from a pole, sagging in a swag; nodes glow, every thread joins several others
    pole_z = 3.7
    link_cyl("pole", (-1.7, -0.08, pole_z), (1.7, -0.08, pole_z), 0.05, WD("#6a4630", "#553622", scale=3), R, seg=6)
    ncol, nrow = 14, 12
    nodes = {}
    for j in range(nrow + 1):
        for i in range(ncol + 1):
            u = i / ncol
            x = -1.6 + 3.2 * u
            z = pole_z - 0.1 - j * 0.28 * (1 - 0.35 * math.sin(math.pi * u) * (j / nrow))
            x += 0.06 * math.sin(j * 1.3 + i) if j > 0 else 0
            nodes[(i, j)] = (x, -0.1 - 0.08 * math.sin(math.pi * u), z + 0.35 * (j / nrow) * math.sin(math.pi * u) * 0.0)
    th = toon("#c9b48a" if not T() else "#8a8a94", rim=0)
    for j in range(nrow + 1):
        for i in range(ncol + 1):
            for di, dj in ((1, 1), (-1, 1)):
                a, b = nodes[(i, j)], nodes.get((i + di, j + 1))
                if b and (i + j) % 2 == 0:
                    link_cyl("n", a, b, 0.008, th, R, seg=3)
    gm = glow(TEAL, 3.0) if T() else None
    for (i, j), p in nodes.items():
        if (i + j) % 2 == 0 and j % 2 == 0 and gm:
            ellipsoid("nd", 0.03, gm, R, loc=p, seg=5, rings=4)
    # floats
    for i in range(0, ncol + 1, 2):
        ellipsoid("fl", 0.07, toon("#c44b3f" if i % 4 == 0 else "#f6efe0", rim=0.4), R, loc=(nodes[(i, 0)][0], -0.14, pole_z - 0.1), seg=8, rings=6)
    for i in range(1, ncol, 3):
        ellipsoid("lw", 0.045, toon("#6a6a74", rim=0.6), R, loc=(nodes[(i, nrow)][0], nodes[(i, nrow)][1], nodes[(i, nrow)][2] - 0.05), seg=6, rings=4)
    if T():
        # torn holes (gaps): dark spots + cobweb look
        for hx, hz in ((-0.4, 2.6), (0.7, 1.9)):
            ellipsoid("hole", 0.28, toon("#05060c", rim=0), R, loc=(hx, -0.16, hz), scale=(1, 0.1, 1.1), seg=10, rings=6)
        halo(R, (0.0, -0.2, 2.2), 1.6, 0.1)
    return {"cell": (512, 520), "anchor": (256, 340)}


def f_map(R):
    # sea map on a frame; erased line still glows and leads to a far village
    box("fr", (1.7, 0.07, 1.25), WD("#5a3a24", "#4a2e1c", scale=3), R, loc=(0, -0.035, 0.62))
    box("mp", (1.55, 0.05, 1.1), tex_toon("paper", "#e8d8b0", "#4a6a8a", scale=2.6, plane="xz", bump=0.1, wear=0), R, loc=(0, -0.07, 0.62))
    # coast + sea blobs
    ellipsoid("se", 0.3, toon("#7ab8d8" if not T() else "#5a6a7a", rim=0), R, loc=(0.1, -0.095, 0.38), scale=(2.3, 0.04, 1.3), seg=14, rings=8)
    ellipsoid("ld", 0.3, toon("#c9b48a" if not T() else "#8a8a7a", rim=0), R, loc=(-0.45, -0.1, 0.5), scale=(1.2, 0.05, 1.1), seg=12, rings=6)
    ellipsoid("ld", 0.17, toon("#c9b48a" if not T() else "#8a8a7a", rim=0), R, loc=(0.5, -0.1, 0.92), scale=(1.2, 0.05, 0.9), seg=10, rings=6)
    for k in range(4):
        tube("wv", [(0.2 + k * 0.18, -0.12, 0.75 - k * 0.04), (0.28 + k * 0.18, -0.12, 0.8 - k * 0.04), (0.36 + k * 0.18, -0.12, 0.75 - k * 0.04)], 0.007, toon("#4a6a8a", rim=0), R)
    # compass rose
    for k in range(4):
        a = k * math.pi / 2
        box("cr", (0.03, 0.02, 0.2), toon("#8a3a2e", rim=0), R, loc=(-0.6, -0.12, 0.95), rot=(0, a, 0))
    # route: dashed dark line; an erased section glows
    pts = [(-0.45, 0.4), (-0.15, 0.5), (0.1, 0.45), (0.35, 0.7), (0.55, 0.95)]
    for (x0, z0), (x1, z1) in zip(pts[:2], pts[1:3]):
        link_cyl("rt", (x0, -0.12, z0), (x1, -0.12, z1), 0.01, toon("#8a3a2e", rim=0), R, seg=3)
    gm = glow(TEAL, 3.0) if T() else toon("#d8c8a0", rim=0)
    for (x0, z0), (x1, z1) in zip(pts[2:], pts[3:]):
        link_cyl("er", (x0, -0.125, z0), (x1, -0.125, z1), 0.014, gm, R, seg=4)
    ellipsoid("vil", 0.04, toon("#8a3a2e", rim=0.3), R, loc=(0.55, -0.13, 0.95), seg=6, rings=4)
    if T():
        halo(R, (0.35, -0.2, 0.8), 0.8, 0.2)
        cobweb(R, (-0.8, -0.08, 1.24), 0.35)
    return {}


def f_lamp(R):
    # fisher's storm lantern hung from a post by the door; light draws a thread out to the sea
    frustum("po", 0.05, 0.05, 2.0, WDT(), R, seg=8)
    frustum("ft", 0.3, 0.3, 0.07, WDT(), R, seg=10)
    link_cyl("ar", (0, 0, 1.95), (0.45, 0, 1.95), 0.035, WDT(), R, seg=6)
    link_cyl("br", (0, 0, 1.55), (0.38, 0, 1.92), 0.025, WDT(), R, seg=5)
    link_cyl("ch", (0.45, 0, 1.95), (0.45, 0, 1.78), 0.01, toon("#2a2a30", rim=0.5), R, seg=3)
    p = pivot("lt", (0.45, 0, 1.45), R)
    frustum("bs", 0.1, 0.12, 0.05, toon("#3a3a44", rim=0.5), p, seg=8)
    frustum("gl", 0.1, 0.1, 0.22, glow("#ffd070", 5 if not T() else 1.0), p, loc=(0, 0, 0.05), seg=8)
    for a in (0, 1.57, 3.14, 4.7):
        link_cyl("rb", (math.cos(a) * 0.105, math.sin(a) * 0.105, 0.05), (math.cos(a) * 0.105, math.sin(a) * 0.105, 0.27), 0.01, toon("#3a3a44", rim=0.5), p, seg=3)
    frustum("tp", 0.12, 0.03, 0.08, toon("#3a3a44", rim=0.5), p, loc=(0, 0, 0.27), seg=8)
    ellipsoid("hl", 0.55, glow("#ffd070", 1.4, alpha=0.3, soft=True), p, loc=(0, 0, 0.15), seg=10, rings=6)
    if T():
        # the light reaches out as a thread and stops half way
        tthread(R, [(0.5, -0.1, 1.55), (0.9, -0.3, 1.5), (1.4, -0.5, 1.4), (1.9, -0.7, 1.35)], 0.014, 3.2)
        ellipsoid("end", 0.04, glow(TEAL, 5), R, loc=(1.9, -0.7, 1.35), seg=6, rings=4)
    else:
        tube("rp", [(0.1, 0, 0.9), (0.2, -0.2, 0.5), (0.1, -0.35, 0.05)], 0.02, toon("#c9b48a", rim=0.2), R)
    return {"cell": (512, 520), "anchor": (200, 410)}


def f_log(R):
    barrel(R, (0, 0, 0), 0.4, 0.8, "#8a5a30")
    lid = frustum("tp", 0.44, 0.44, 0.05, WD("#6a4630", "#553622", scale=4, plane="xy"), R, loc=(0, 0, 0.8), seg=18)
    open_book(R, (0, 0, 0.86), 0.58, 0.4, "#2a4a6a", rot=(0, 0, RAD(8)))
    frustum("ik", 0.04, 0.04, 0.06, toon("#1f2f66", rim=0.5), R, loc=(0.32, 0.15, 0.85), seg=8)
    link_cyl("pn", (0.3, 0.1, 0.94), (0.2, -0.1, 0.88), 0.01, toon("#3a2a22", rim=0), R, seg=4)
    for k in range(5):
        box("ln", (0.18, 0.01, 0.01), toon("#3a2a22", rim=0), R, loc=(-0.15, -0.1 + k * 0.05, 0.9), rot=(0, 0, RAD(8)))
    if T():
        # last page tied by a thread to the jetty (out of the door / left)
        tthread(R, [(0.15, 0.0, 0.92), (0.05, -0.2, 0.8), (-0.5, -0.5, 0.4), (-1.2, -0.7, 0.05)], 0.012, 3.2)
        cobweb(R, (-0.4, 0.3, 1.0), 0.3)
    return {}


def f_boat(R):
    # small clinker-built dinghy resting on trestles, tied with a rope
    hull = WD("#8a5a30", "#6a4220", scale=3, bump=1.0, wear=0.6)
    hull_out = WD("#3a6a8a" if not T() else "#4a5a68", "#2e5470", scale=3, bump=0.9, wear=0.6)
    L, W = 3.4, 1.15
    segs = 14
    rows = 6
    # hull as a lofted shell: rows go from left gunwale (j=0) around the keel to right gunwale
    v = []
    for i in range(segs + 1):
        t = i / segs
        x = -L / 2 + L * t
        half = W / 2 * (math.sin(math.pi * (0.03 + 0.94 * t)) ** 0.6)
        gun = 0.85 + 0.25 * (abs(2 * t - 1) ** 2)
        keel = 0.32 + 0.1 * (abs(2 * t - 1) ** 2)
        for j in range(rows + 1):
            a = math.pi * j / rows
            yy = -half * math.cos(a)
            zz = keel + (gun - keel) * (1 - math.sin(a)) ** 1.0 if False else gun - (gun - keel) * math.sin(a)
            v.append((x, yy, zz))
    f = []
    for i in range(segs):
        for j in range(rows):
            a = i * (rows + 1) + j
            f.append((a, a + rows + 1, a + rows + 2, a + 1))
    mesh_obj("hull", v, f, hull_out, R, smooth=True)
    # inner (visible) planking: same shape slightly smaller, flipped faces
    vi = [(x, y * 0.93, z + 0.02 if True else z) for (x, y, z) in v]
    fi = [tuple(reversed(ff)) for ff in f]
    mesh_obj("inner", vi, fi, hull, R, smooth=True)
    # gunwale rails
    for s in (-1, 1):
        pts = []
        for i in range(segs + 1):
            t = i / segs
            x = -L / 2 + L * t
            half = W / 2 * (math.sin(math.pi * (0.03 + 0.94 * t)) ** 0.6)
            pts.append((x, s * half, 0.85 + 0.25 * (abs(2 * t - 1) ** 2)))
        tube("gw", pts, 0.04, WDT(), R)
    box("th1", (0.1, W * 0.75, 0.05), hull, R, loc=(-0.5, 0, 0.62))
    box("th2", (0.1, W * 0.85, 0.05), hull, R, loc=(0.5, 0, 0.62))
    # trestles
    for x in (-1.0, 1.0):
        for s in (-1, 1):
            link_cyl("tr", (x, s * 0.15, 0.4), (x, s * 0.5, 0.0), 0.05, WDT(), R, seg=5)
    # oars
    link_cyl("oar", (-0.2, 0.1, 0.68), (1.0, 0.4, 1.0), 0.025, WDT(), R, seg=5)
    ellipsoid("bl", 0.12, WD("#c9b48a", "#a8884a", scale=4), R, loc=(1.1, 0.45, 1.05), scale=(2.0, 0.4, 0.6), seg=8, rings=6)
    # bow rope tied to a post
    ellipsoid("cl", 0.06, toon("#c9b48a", rim=0.2), R, loc=(L / 2 + 0.05, 0, 1.1), seg=6, rings=4)
    rope(R, [(L / 2 + 0.05, 0, 1.1), (L / 2 + 0.3, -0.2, 0.7), (L / 2 + 0.5, -0.3, 0.3), (L / 2 + 0.6, -0.3, 0.05)], 0.035)
    if T():
        ellipsoid("wat", 0.5, glow("#3a4a6a", 0.4, alpha=0.9), R, loc=(0, 0, 0.62), scale=(2.8, 1.0, 0.02), seg=14, rings=4)
        weaver_knot(R, (L / 2 + 0.38, -0.3, 0.75), 0.1)
        halo(R, (L / 2 + 0.38, -0.3, 0.75), 0.5, 0.2)
    return {"cell": (640, 420), "anchor": (320, 310)}


def f_barrels(R):
    barrel(R, (-0.3, 0.0, 0.0), 0.34, 0.7)
    barrel(R, (0.4, 0.05, 0.0), 0.3, 0.62, "#8a5a30")
    crate(R, (0.0, 0.0, 0.7), 0.4, 0.2, "#9a6a3e") if False else None
    rope(R, [(-0.3, -0.34, 0.5), (0.1, -0.4, 0.4), (0.4, -0.3, 0.45)], 0.02)
    if T():
        cobweb(R, (-0.4, 0.2, 0.9), 0.3)


def f_fish_rack(R):
    wd = WDT()
    for s in (-1, 1):
        link_cyl("lg", (s * 1.0, -0.1, 0), (s * 1.0, 0, 1.8), 0.05, wd, R, seg=5)
        link_cyl("lg", (s * 1.0, 0.1, 0), (s * 1.0, 0, 1.8), 0.05, wd, R, seg=5)
    link_cyl("bar", (-1.05, 0, 1.75), (1.05, 0, 1.75), 0.04, wd, R, seg=6)
    link_cyl("bar", (-1.05, 0, 1.2), (1.05, 0, 1.2), 0.03, wd, R, seg=6)
    for i in range(7):
        x = -0.85 + i * 0.28
        z = 1.75
        fc = ["#9aa6b8", "#b4a89a", "#8a9aa8"][i % 3] if not T() else "#6a6e78"
        tube("st", [(x, 0, z), (x, 0, z - 0.2)], 0.008, toon("#d9c9a8", rim=0), R)
        ellipsoid("fs", 0.1, toon(fc, rim=0.5), R, loc=(x, 0, z - 0.45), scale=(0.5, 0.25, 1.9), seg=10, rings=8)
        frustum("tl", 0.06, 0.0, 0.12, toon(fc, rim=0.5), R, loc=(x, 0, z - 0.76), rot=(RAD(180), 0, 0), seg=3)
        ellipsoid("ey", 0.02, toon("#1a1220", rim=0), R, loc=(x, -0.05, z - 0.28), seg=5, rings=4)
    for i in range(4):
        x = -0.7 + i * 0.45
        ellipsoid("fs2", 0.09, toon("#b4a89a" if not T() else "#6a6e78", rim=0.5), R, loc=(x, 0, 1.2 - 0.3), scale=(0.5, 0.25, 1.9), seg=10, rings=8)
        tube("st", [(x, 0, 1.2), (x, 0, 1.0)], 0.008, toon("#d9c9a8", rim=0), R)
    if T():
        cobweb(R, (-1.0, 0.0, 1.8), 0.5)


def f_rods(R):
    frustum("ft", 0.3, 0.3, 0.07, WDT(), R, seg=10)
    box("bk", (0.5, 0.06, 0.5), WDT(), R, loc=(0, 0.1, 0.5), base=True)
    for i in range(4):
        a = -0.3 + i * 0.2
        link_cyl("rd", (-0.2 + i * 0.14, 0.0, 0.2), (-0.2 + i * 0.14 + a * 0.9, 0.05, 2.3), 0.016, WD("#c9b48a", "#a8884a", scale=5), R, seg=4, r2=0.007)
    frustum("rl", 0.08, 0.08, 0.05, toon("#3a3a44", rim=0.6), R, loc=(-0.1, -0.05, 0.9), rot=(RAD(90), 0, 0), seg=10)
    if T():
        cobweb(R, (0.0, 0.0, 2.2), 0.4)


def f_buoys(R):
    cols = ["#c44b3f", "#f6efe0", "#e8b04a", "#4f7ad8"]
    for k, (x, y, r) in enumerate(((-0.3, 0.0, 0.26), (0.25, 0.05, 0.22), (0.0, -0.28, 0.2), (0.45, -0.3, 0.17))):
        ellipsoid("by", r, FAB("stripes", cols[k], cols[(k + 1) % 4], scale=7, plane="xz", bump=0.5), R, loc=(x, y, r * 0.95), seg=14, rings=10)
        ellipsoid("rg", r * 0.22, toon("#3a3a44", rim=0.6), R, loc=(x, y, r * 1.9), scale=(1, 0.3, 1), seg=8, rings=5)
    rope(R, [(-0.3, 0.0, 0.5), (0.1, -0.4, 0.1), (0.5, -0.5, 0.02)], 0.025)
    if T():
        cobweb(R, (-0.3, 0.1, 0.55), 0.25)


def f_bucket(R):
    frustum("bk", 0.28, 0.22, 0.4, WD("#8a5a30", "#6a4220", scale=5, along="v"), R, seg=12)
    for z in (0.08, 0.28):
        frustum("bn", 0.285 - z * 0.1, 0.285 - z * 0.1, 0.04, toon("#3a3a44", rim=0.5), R, loc=(0, 0, z), caps=(False, False), seg=12)
    tube("hd", [(-0.27, 0, 0.4), (0, 0, 0.78), (0.27, 0, 0.4)], 0.015, toon("#3a3a44", rim=0.5), R)
    frustum("wt", 0.24, 0.24, 0.01, glow("#7ab8d8" if not T() else "#3a4a6a", 0.8), R, loc=(0, 0, 0.35), seg=12)
    for k in range(2):
        ellipsoid("sc", 0.05, toon("#b4a89a", rim=0.5), R, loc=(-0.1 + k * 0.15, -0.05 * k, 0.4), scale=(0.5, 0.2, 1.7), rot=(0, 0, k), seg=6, rings=5)


OBJ = {
    "inn": {"i_board": i_board, "i_guestbook": i_guestbook, "i_key": i_key, "i_rules": i_rules, "i_kettle": i_kettle, "i_lost": i_lost,
            "x_hearth": i_hearth, "x_long_table": i_long_table, "x_barrels": i_barrels, "x_coat_rack": i_coat_rack, "x_plant": i_plant},
    "bell_tower": {"b_window": b_window, "b_rope": b_rope, "b_notes": b_notes, "b_pigeon": b_pigeon, "b_oil": b_oil, "x_stairs": b_stairs,
                   "x_bell_wheel": b_bell_wheel, "x_rope_coil": b_rope_coil, "x_crate_pile": b_crate_pile, "x_lantern": b_lantern},
    "tailor": {"t_shop": t_shop, "t_list": t_list, "t_threads": t_threads, "t_mannequin": t_mannequin, "t_basket": t_basket,
               "x_cloth_shelf": t_cloth_shelf, "x_cutting_table": t_cutting_table, "x_sewing": t_sewing, "x_mirror": t_mirror,
               "x_hat_stand": t_hat_stand},
    "school": {"s_board": s_board, "s_drawings": s_drawings, "s_notes": s_notes, "s_globe": s_globe, "s_bench": s_bench,
               "x_desks_a": s_desks_a, "x_desks_b": s_desks_b, "x_bookcase": s_bookcase, "x_stove": s_stove, "x_easel": s_easel},
    "fisher": {"f_net": f_net, "f_map": f_map, "f_lamp": f_lamp, "f_log": f_log, "f_boat": f_boat, "x_barrels": f_barrels,
               "x_fish_rack": f_fish_rack, "x_rods": f_rods, "x_buoys": f_buoys, "x_bucket": f_bucket},
}
