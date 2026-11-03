"""Buildings c-f: print house, bakery, mill (+ sails sprite), Weavers' tower. Imported by buildings.py."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env_blocks import *  # noqa
import env_lib as EL
from buildings import ridge_cap, eave_trim, roof_z_at


def np_range(a, b, s):
    out = []
    while a < b:
        out.append(a)
        a += s
    return out


def roof_hole(parent, x, y, wh, rh, d, ov, s=0.55, rz0=None):
    """Truth: missing tiles - dark patch with bare rafters on the front slope (ridge along X)."""
    D = d / 2 + ov
    ang = math.atan2(rh, D)
    z = (rz0 if rz0 is not None else wh) + rh * (1 - abs(y) / D) + 0.02
    p = pivot("hole", (x, y, z), parent, rot=(-ang if y < 0 else ang, 0, 0))
    box("dark", (s, s * 0.8, 0.03), toon("#0e0f18", rim=0), p)
    for i in (-1, 0, 1):
        box("raf", (0.05, s * 0.9, 0.05), toon("#5a4a3c", rim=0), p, loc=(i * s * 0.3, 0, 0.04))


def sagging_threads(parent, pts, seed=1):
    for i, p0 in enumerate(pts):
        snapped_thread(parent, p0, length=0.7 + 0.2 * (i % 3), sway=0.12, seed=seed + i, cut=(i % 2 == 0))


def bead_cloud(parent, n, rfun, zrange, rad=0.045, seed=3,
               colors=("#e8884a", "#4f7ad8", "#e8b04a", "#c44b3f", "#a07ad8", "#f3e4c4"), front_only=True):
    """n tiny beads (spools seen from afar) on a cylinder surface: one mesh, one material per colour."""
    rnd = random.Random(seed)
    mats = [toon(c, rim=0.5) for c in colors]
    bm = bmesh.new()
    me = bpy.data.meshes.new("beads")
    for i in range(n):
        z = rnd.uniform(*zrange)
        a = rnd.uniform(math.pi * 0.95, math.pi * 2.05) if front_only else rnd.uniform(0, 6.28)
        r = rfun(z)
        c = Vector((math.cos(a) * r, math.sin(a) * r, z))
        res = bmesh.ops.create_uvsphere(bm, u_segments=6, v_segments=4, radius=rad * rnd.uniform(0.8, 1.3))
        mi = rnd.randrange(len(mats))
        bmesh.ops.translate(bm, vec=c, verts=res["verts"])
        for f in {f for v in res["verts"] for f in v.link_faces}:
            f.material_index = mi
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    ob = bpy.data.objects.new("beads", me)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = parent
    return ob


# =============================================================== (c) print house
def print_house():
    R = pivot("C")
    w, d = 3.8, 3.2
    plaster = PL("#c9a495", "#b8938a", wear=0.6, moss=0.2)
    tm = WDT("#4a3040", "#3c2434")
    box("found", (w + 0.16, d + 0.16, 0.32), ST("#8f8590", "#756a7c", scale=2.4, moss=0.4), R, base=True)
    ow = 2.3
    gh = 2.3
    for s in (-1, 1):
        box("wing", ((w - ow) / 2, d, gh - 0.32), plaster, R, loc=(s * (ow / 2 + (w - ow) / 4), 0, 0.32), base=True)
    box("back", (w, 0.2, gh - 0.32), PL("#2e2038", "#251a2e", wear=0.2), R, loc=(0, d / 2 - 0.1, 0.32), base=True)
    box("floor", (w, d, 0.04), WD("#7a5638", "#6a4830", plane="xy", scale=2.2), R, loc=(0, 0, 0.32), base=True)
    box("lintel", (ow + 0.4, d, 0.4), tm, R, loc=(0, 0, gh - 0.4), base=True)
    box("interior_glow", (ow, 0.05, gh - 0.8), glow("#ff9a4a", 1.0), R, loc=(0, d / 2 - 0.22, 0.4), base=True)
    for x in (-ow / 2 - 0.1, ow / 2 + 0.1):
        box("jamb", (0.2, 0.15, gh - 0.3), tm, R, loc=(x, -d / 2, 0.32), base=True)
    uz = gh
    box("up", (w + 0.5, d + 0.3, 1.5), plaster, R, loc=(0, -0.05, uz), base=True)
    for x in (-w / 2 - 0.15, 0, w / 2 + 0.15):
        box("upost", (0.14, 0.07, 1.5), tm, R, loc=(x, -d / 2 - 0.22, uz), base=True)
    box("ubeam", (w + 0.6, 0.12, 0.16), tm, R, loc=(0, -d / 2 - 0.2, uz + 0.02))
    for x in (-1.0, 1.0):
        link_cyl("brace", (x * 0.35, -d / 2 - 0.2, uz + 0.1), (x * 0.9, -d / 2 - 0.2, uz + 1.35), 0.05, tm, R, seg=5)
    rh = 1.3
    rz = uz + 1.5
    rm = tex_toon("tiles", "#34478a", "#2a3a78", scale=3.2, plane="xy", bump=1.0, wear=0.4, moss=0.2)
    sloped_roof("roof", w + 0.5, d + 0.3, rh, 0.35, rm, R, loc=(0, -0.05, rz), ridge_x=False, ends=False)
    gw = pivot("gable", (0, -d / 2 - 0.2, rz), R)
    GW = (w + 0.5) / 2
    mesh_obj("gtri", [(-GW, 0, 0), (GW, 0, 0), (0, 0, rh)], [(0, 2, 1)], PL("#b8938a", "#a98279", wear=0.5), gw, smooth=False)
    link_cyl("g1", (-GW, -0.04, 0.02), (0, -0.04, rh - 0.05), 0.06, tm, gw, seg=5)
    link_cyl("g2", (GW, -0.04, 0.02), (0, -0.04, rh - 0.05), 0.06, tm, gw, seg=5)
    box("hdoor", (0.6, 0.05, 0.7), glow("#ffb868", 2.4), gw, loc=(0, -0.05, 0.55))
    box("hfr", (0.74, 0.06, 0.84), tm, gw, loc=(0, -0.03, 0.55))
    link_cyl("hbeam", (0, -0.05, 1.2), (0, -0.85, 1.25), 0.05, tm, gw, seg=5)
    link_cyl("rope", (0, -0.8, 1.2), (0, -0.8, 0.75), 0.012, toon("#d9c9a8", rim=0), gw, seg=4)
    box("bundle", (0.3, 0.2, 0.2), PL("#efe6cc", "#e0d4b0", wear=0.1), gw, loc=(0, -0.8, 0.65))
    for x in (-1.15, 1.15):
        window(R, (x, -d / 2 - 0.22, uz + 0.75), w=0.7, h=0.7, frame="#d8c8b8", shutter="#4a3a7a", flowers=False,
               curtain="#a080c0", light="#ffd89a")
    # the screw press
    pr = pivot("press", (0, -0.35, 0.34), R)
    pw = WD("#c48a50", "#a87238", scale=3, along="v")
    for x in (-0.6, 0.6):
        box("post", (0.16, 0.2, 1.55), pw, pr, loc=(x, 0, 0), base=True)
    box("topb", (1.5, 0.28, 0.2), WD("#8a5a30", "#704826", scale=3), pr, loc=(0, 0, 1.45), base=True)
    frustum("screw", 0.09, 0.09, 1.1, WD("#6a4220", "#583518", scale=5, along="v"), pr, loc=(0, 0, 0.55), seg=10)
    for z in np_range(0.65, 1.4, 0.1):
        frustum("thr", 0.12, 0.12, 0.03, toon("#4a2e16", rim=0.2), pr, loc=(0, 0, z), seg=10)
    link_cyl("bar", (-0.85, 0, 1.0), (0.85, 0, 1.2), 0.04, toon("#3a2a22", rim=0.3), pr, seg=6)
    for s in (-1, 1):
        ellipsoid("wt", 0.1, toon("#3a2a22", rim=0.4), pr, loc=(s * 0.85, 0, 1.0 + (0.1 if s > 0 else 0)), seg=8, rings=6)
    box("platen", (0.9, 0.7, 0.1), WD("#a06a3e", "#85502c", scale=4), pr, loc=(0, 0, 0.42), base=True)
    box("bed", (1.3, 0.8, 0.12), WD("#7a5030", "#6a4426", scale=3), pr, loc=(0, 0, 0.0), base=True)
    box("sheet", (0.8, 0.6, 0.015), tex_toon("paper", "#f3e8cc", "#2a2a60", scale=4, plane="xy", bump=0.1), pr, loc=(0, 0, 0.13), base=True)
    for i, (x, y) in enumerate([(-0.85, -0.3), (-0.85, -0.3), (0.95, -0.4)]):
        box("pile", (0.5, 0.4, 0.35), tex_toon("paper", "#f1e6c8", "#2a2a60", scale=4, plane="xz", bump=0.2), R,
            loc=(x, y, 0.34 + (0.35 if i == 1 else 0)), base=True)
    barrel(R, (2.5, -1.9, 0), 0.3, 0.6, col="#4a4a8a")
    barrel(R, (2.95, -1.7, 0), 0.26, 0.5, col="#3a3a7a")
    ellipsoid("ink", 0.2, glow("#4f7ad8", 3, alpha=0.8, soft=True), R, loc=(2.5, -1.9, 0.62), seg=10, rings=6)
    for x, y in ((-3.5, -2.3), (-0.8, -2.3)):
        frustum("pole", 0.05, 0.05, 2.2, WDT(), R, loc=(x, y, 0), seg=6)
    ln = [(-3.5 + 2.7 * t / 10, -2.3, 2.1 - 0.1 * math.sin(math.pi * t / 10)) for t in range(11)]
    tube("line", ln, 0.012, toon("#d9c9a8", rim=0.2), R)
    for i in range(6):
        x = -3.35 + i * 0.45
        box("sheet", (0.34, 0.02, 0.5), tex_toon("paper", "#f3e8cc", "#2a3a8a", scale=3.2, plane="xz", bump=0.1), R,
            loc=(x, -2.32, 1.78 + 0.02 * (i % 2)), rot=(0, RAD((i % 3 - 1) * 6), 0))
        box("clip", (0.04, 0.04, 0.05), toon("wood_d", rim=0), R, loc=(x, -2.33, 2.05))
    sp = pivot("sign", (-1.45, -d / 2 - 0.2, 2.0), R)
    link_cyl("arm", (0, 0, 0.2), (0, -0.55, 0.2), 0.03, tm, sp, seg=5)
    box("board", (0.55, 0.05, 0.5), tex_toon("paper", "#f3e8cc", "#2a3a8a", scale=3, plane="xz", bump=0.2), sp, loc=(0, -0.58, -0.08))
    box("bfr", (0.62, 0.04, 0.57), tm, sp, loc=(0, -0.56, -0.08))
    crate(R, (-2.2, -1.9, 0), 0.5, RAD(10), col="#7a5638")
    plant_pot(R, (1.55, -2.0, 0), 0.2, 0.3, seed=3, kind="flower", pot="#6a5a9a")
    box("chim", (0.6, 0.6, 1.2), BR("#8a6a60", "#74564e", scale=3, soot=0.8), R, loc=(-1.0, 0.7, rz + 0.4), base=True)
    if EL.TRUTH:
        cobweb(R, (-ow / 2 + 0.05, -d / 2 - 0.2, gh - 0.4), 0.5)
        sagging_threads(R, [(-1.5, -d / 2 - 0.5, uz + 1.2), (1.6, -d / 2 - 0.5, uz + 1.2)], seed=4)
        dead_plant(R, (1.55, -2.0, 0.3), 0.5, seed=3)
    return dict(cell=(448, 512), anchor=(224, 400), smoke=[(-1.0, 0.7, rz + 1.65)])


# =============================================================== (d) bakery
def bakery():
    R = pivot("D")
    w, d, wh, rh, ov = 3.9, 3.0, 2.6, 0.8, 0.5
    brick = BR("#c2603f", "#a94f35", scale=2.2, wear=0.6, moss=0.25)
    box("found", (w + 0.14, d + 0.14, 0.3), ST("#9a8f88", "#7c7480", scale=2.4), R, base=True)
    box("walls", (w, d, wh - 0.3), brick, R, loc=(0, 0, 0.3), base=True)
    wtm = WDT("#5a3a26", "#4a2e1e")
    box("beam", (w, 0.08, 0.14), wtm, R, loc=(0, -d / 2 - 0.02, wh - 0.1))
    roof = tex_toon("tiles", "#d0703c", "#b85a2c", scale=3.4, plane="xy", bump=1.0, wear=0.4, moss=0.3)
    sloped_roof("roof", w, d, rh, ov, roof, R, loc=(0, 0, wh - 0.05), ends=True)
    ridge_cap(R, w + 2 * ov, wh - 0.05 + rh, toon("#9a4630", rim=0.4), r=0.1)
    eave_trim(R, w, d, ov, wh - 0.03, toon("#9a4630", rim=0.3), r=0.08)
    box("cfr", (1.6, 0.1, 1.05), toon("#f3e4c4", rim=0.2), R, loc=(-0.95, -d / 2 - 0.02, 1.15))
    box("cpane", (1.4, 0.05, 0.85), glow("#ffa850", 3.4), R, loc=(-0.95, -d / 2 - 0.09, 1.15))
    box("counter", (1.9, 0.5, 0.1), WD("#a06a3e", "#85502c", scale=3), R, loc=(-0.95, -d / 2 - 0.3, 0.62))
    for i, x in enumerate((-1.45, -1.05, -0.65, -0.3)):
        ellipsoid("loaf", 0.14, toon(["#c98a3c", "#b87a30", "#d9a050", "#a86a28"][i], rim=0.5), R, loc=(x, -d / 2 - 0.3, 0.78), scale=(1.5, 0.8, 0.7), seg=10, rings=6)
    zb, zf = 2.2, 1.7
    yb, yf = -d / 2, -d / 2 - 1.05
    aw = tex_toon("stripes", "#c44b3f", "#f3e4c4", scale=3.2, plane="xy", bump=0.5, rim=0.4, ao=0.2)
    ax0, ax1 = -2.0, 0.1
    mesh_obj("awning", [(ax0, yb, zb), (ax1, yb, zb), (ax1, yf, zf), (ax0, yf, zf)], [(0, 1, 2, 3)], aw, R, smooth=False)
    for i in range(7):
        x0 = ax0 + i * (ax1 - ax0) / 7
        x1 = x0 + (ax1 - ax0) / 7
        mesh_obj("val", [(x0, yf, zf), (x1, yf, zf), ((x0 + x1) / 2, yf - 0.02, zf - 0.22)], [(0, 2, 1)],
                 toon("#c44b3f" if i % 2 == 0 else "#f3e4c4", rim=0.4), R, smooth=False)
    for x in (ax0 + 0.05, ax1 - 0.05):
        link_cyl("aps", (x, yf, zf - 0.2), (x, yf, 0.0), 0.04, wtm, R, seg=5)
    door(R, (0.95, -d / 2, 0.0), w=0.9, h=1.75, color="#6a8a5a", frame="#f3e4c4", window_=True)
    lantern2(R, (1.8, -d / 2, 1.95))
    ox, oy = 2.75, 0.35
    ellipsoid("dome", 1.25, BR("#b45a3a", "#97452e", scale=2.4, wear=0.7, soot=0.6), R, loc=(ox, oy, 0.4), scale=(1.0, 1.0, 0.95), seg=22, rings=12)
    box("ovbase", (2.3, 2.1, 0.45), ST("#9a8f88", "#7c7480", scale=2.4, soot=0.5), R, loc=(ox, oy, 0), base=True)
    frustum("flue", 0.38, 0.26, 3.0, BR("#b45a3a", "#97452e", scale=3, soot=0.9, wear=0.8), R, loc=(ox, oy + 0.1, 1.2), seg=8)
    frustum("flue2", 0.32, 0.32, 0.18, ST("#8c848a", "#6c6470", scale=3), R, loc=(ox, oy + 0.1, 4.2), seg=8)
    mouth = pivot("mouth", (ox, oy - 1.2, 0.55), R)
    box("mfr", (0.76, 0.1, 0.4), toon("#3a2a22", rim=0), mouth, loc=(0, 0.1, 0.2))
    frustum("march", 0.38, 0.38, 0.12, toon("#3a2a22", rim=0), mouth, loc=(0, 0.1, 0.4), rot=(RAD(90), 0, 0), seg=16)
    frustum("mfire", 0.3, 0.3, 0.06, glow("#ff8a28", 6), mouth, loc=(0, 0.04, 0.4), rot=(RAD(90), 0, 0), seg=16)
    box("mfire2", (0.6, 0.06, 0.4), glow("#ff8a28", 6), mouth, loc=(0, 0.04, 0.2))
    ellipsoid("mhalo", 0.7, glow("#ff9a38", 1.2, alpha=0.5, soft=True), mouth, loc=(0, -0.15, 0.35), scale=(1, 0.3, 0.8), seg=14, rings=8)
    sp = pivot("sign", (-2.1, -d / 2 - 0.05, 2.15), R)
    link_cyl("arm", (0, 0, 0), (0, -0.6, 0), 0.03, wtm, sp, seg=5)
    link_cyl("ch", (0, -0.6, 0), (0, -0.6, -0.15), 0.012, toon("leather_d", rim=0), sp, seg=4)
    ellipsoid("loaf", 0.3, tex_toon("plain", "#d9a050", "#b87a30", scale=6, bump=0.6, wear=0.2, rim=0.5, ao=0.2), sp, loc=(0, -0.6, -0.45), scale=(1.35, 0.35, 0.8), seg=16, rings=10)
    for k in range(3):
        box("score", (0.1, 0.04, 0.03), toon("#f0d9a8", rim=0.3), sp, loc=(-0.2 + k * 0.2, -0.64, -0.4 + (0.03 if k == 1 else 0)), rot=(0, RAD(35), 0))
    for i, (x, y, rot) in enumerate([(-2.35, -1.7, 20), (-2.05, -1.95, -10), (-2.3, -2.25, 5)]):
        s2 = pivot("sack", (x, y, 0), R, rot=(0, 0, RAD(rot)))
        ellipsoid("sk", 0.3, tex_toon("weave", "#efe4cc", "#d9c9a8", scale=18, plane="xz", bump=0.9, rim=0.4, ao=0.3), s2, loc=(0, 0, 0.3), scale=(1, 0.75, 1.0), seg=12, rings=8)
        frustum("tie", 0.1, 0.06, 0.12, toon("#efe4cc", rim=0.3), s2, loc=(0, 0, 0.55), seg=8)
        box("lab", (0.2, 0.02, 0.12), toon("#c44b3f", rim=0), s2, loc=(0, -0.23, 0.32))
    frustum("basket", 0.35, 0.3, 0.32, FAB("weave", "#b07a46", "#8a5a30", scale=14), R, loc=(0.2, -2.05, 0), seg=14)
    for i, a in enumerate((0, 1.6, 3.2, 4.8)):
        ellipsoid("loaf", 0.12, toon("#c98a3c", rim=0.5), R, loc=(0.2 + math.cos(a) * 0.15, -2.05 + math.sin(a) * 0.12, 0.4), scale=(1.4, 0.8, 0.8), rot=(0, 0, a), seg=8, rings=6)
    crate(R, (1.3, -1.9, 0), 0.5, RAD(-8), col="#a06a3e")
    bush(R, (-2.7, -0.5, 0), r=0.32, col="leaf2", seed=5, fcols=("#ffd86a", "white"))
    if EL.TRUTH:
        roof_hole(R, -1.0, -0.6, wh - 0.05, rh, d, ov, s=0.6, rz0=wh - 0.05)
        cobweb(R, (-1.75, -d / 2 - 0.1, 1.55), 0.45)
        sagging_threads(R, [(-0.6, -d / 2 - 0.3, wh + 0.3), (0.6, -d / 2 - 0.3, wh + 0.2)], seed=7)
        dead_plant(R, (-2.7, -0.5, 0), 0.6, seed=2)
    return dict(cell=(448, 512), anchor=(224, 380), smoke=[(ox, oy + 0.1, 4.4)])


# =============================================================== (e) mill and sails
def mill():
    R = pivot("E")
    stone = ST("#a39a92", "#8a8088", scale=2.2, wear=0.8, moss=0.7)
    frustum("plinth", 1.9, 1.75, 0.6, ST("#8a8088", "#6f6874", scale=2.4, moss=0.9), R, seg=20)
    frustum("tower", 1.6, 1.12, 3.6, stone, R, loc=(0, 0, 0.55), seg=20)
    frustum("band", 1.18, 1.1, 0.7, PL("#e8d6b8", "#d6c0a0", wear=0.5), R, loc=(0, 0, 3.0), seg=20)
    cap = pivot("cap", (0, 0, 4.05), R)
    wood = WD("#7a5030", "#6a4426", scale=3, along="v")
    frustum("capb", 1.18, 1.1, 0.3, wood, cap, seg=20)
    shingle = tex_toon("tiles", "#7a5a40", "#5a4230", scale=4, plane="xy", bump=1.0, wear=0.5, moss=0.3)
    frustum("capr", 1.35, 0.1, 1.5, shingle, cap, loc=(0, 0, 0.3), seg=20, caps=(False, False))
    ellipsoid("fin", 0.1, toon("gold", rim=0.5), cap, loc=(0, 0, 1.85), seg=8, rings=6)
    hub = (0, -1.35, 3.95)
    link_cyl("axle", (0, -0.9, 3.95), hub, 0.13, toon("#3a2a22", rim=0.4), R, seg=10)
    ellipsoid("hubb", 0.22, toon("#5a3a26", rim=0.5), R, loc=hub, seg=12, rings=8)
    door(R, (0, -1.58, 0.28), w=0.95, h=1.55, color="#6a4a8a", frame="#e8d6b8", step=False)
    box("step", (1.5, 0.7, 0.12), ST(scale=3, bump=0.6), R, loc=(0, -1.95, 0.06))
    for ang, z, ww in ((-35, 2.3, 0.5), (35, 2.3, 0.5), (0, 3.35, 0.45)):
        a = math.radians(ang)
        r = 1.42 - (z - 0.55) * (0.48 / 3.6)
        x, y = math.sin(a) * r, -math.cos(a) * r
        wp = pivot("win", (x, y, z), R, rot=(0, 0, -a))
        box("wf", (ww + 0.14, 0.1, ww + 0.2), toon("#e8d6b8", rim=0.2), wp)
        box("wp", (ww, 0.05, ww + 0.05), glow("window", 3.2), wp, loc=(0, -0.06, 0))
        box("wm", (0.04, 0.06, ww + 0.05), toon("#e8d6b8", rim=0.2), wp, loc=(0, -0.08, 0))
    wx, wy, wz, wr = 2.25, -1.1, 1.25, 1.1
    wh_ = pivot("wheel", (wx, wy, wz), R)
    ww = WD("#8a5a30", "#704826", scale=4, along="v")
    for rim_y in (-0.16, 0.16):
        frustum("rim", wr, wr, 0.06, ww, wh_, loc=(0, rim_y, 0), rot=(RAD(90), 0, 0), seg=24, caps=(False, False))
        frustum("rim2", wr * 0.9, wr * 0.9, 0.05, ww, wh_, loc=(0, rim_y, 0), rot=(RAD(90), 0, 0), seg=24, caps=(False, False))
    for k in range(8):
        a = k * math.pi / 4
        link_cyl("spoke", (0, -0.12, 0), (math.cos(a) * wr, -0.12, math.sin(a) * wr), 0.045, ww, wh_, seg=5)
        pa = (math.cos(a) * wr * 0.95, 0, math.sin(a) * wr * 0.95)
        box("pad", (0.1, 0.4, 0.28), ww, wh_, loc=pa, rot=(0, -a, 0))
    frustum("wax", 0.16, 0.16, 0.5, toon("#3a2a22", rim=0.4), wh_, loc=(0, -0.3, 0), rot=(RAD(90), 0, 0), seg=10)
    box("pit", (2.6, 0.9, 0.5), ST("#8a8088", "#6f6874", scale=3, moss=0.9), R, loc=(wx, wy + 0.2, 0), base=True)
    box("water", (2.0, 0.8, 0.03), glow("#6fd8d0", 0.9, alpha=0.5), R, loc=(wx + 0.3, wy + 0.2, 0.52))
    box("flume", (1.4, 0.3, 0.12), wood, R, loc=(wx - 0.9, wy - 0.05, wz + wr + 0.2))
    for fx in (wx - 1.5, wx - 0.3):
        link_cyl("fl", (fx, wy - 0.05, wz + wr + 0.15), (fx, wy - 0.05, 0.0), 0.05, wood, R, seg=5)
    ellipsoid("splash", 0.4, glow("#bff4f0", 2, alpha=0.8, soft=True), R, loc=(wx, wy - 0.4, 0.45), scale=(1.4, 0.4, 0.6), seg=10, rings=6)
    for i, (x, y) in enumerate([(-1.55, -1.9), (-1.2, -2.2), (-1.8, -2.35)]):
        s = pivot("sack", (x, y, 0), R, rot=(0, 0, RAD(i * 25)))
        ellipsoid("sk", 0.3, tex_toon("weave", "#efe4cc", "#d9c9a8", scale=18, plane="xz", bump=0.9, rim=0.4, ao=0.3), s, loc=(0, 0, 0.3), scale=(1, 0.75, 1.0), seg=12, rings=8)
        frustum("tie", 0.1, 0.06, 0.12, toon("#efe4cc", rim=0.3), s, loc=(0, 0, 0.55), seg=8)
    barrel(R, (-2.35, -1.2, 0), 0.3, 0.6)
    bush(R, (-2.6, -0.2, 0), r=0.4, seed=8, fcols=("#c79ae8", "white"))
    lantern2(R, (0.85, -1.62, 1.8))
    if EL.TRUTH:
        cobweb(R, (-0.3, -1.64, 1.85), 0.4)
        sagging_threads(R, [(0.0, -1.4, 4.0), (-0.5, -1.2, 3.6)], seed=9)
    anchor = (256, 470)
    hp = project(*hub, anchor)
    return dict(cell=(512, 576), anchor=anchor, smoke=[], extra={"hub": [round(hp[0], 1), round(hp[1], 1)]})


def mill_sails():
    """Four lattice blades, hub at the exact cell centre, tilted to face the camera so rotation in 2D looks right."""
    R = pivot("S")
    wood = WD("#7a5030", "#6a4426", scale=3, along="v", bump=0.6)
    dark = WDT("#4a2e1e", "#3c2418")
    cloth = tex_toon("weave", "#efe4cc", "#d9c9a8", scale=16, plane="xz", bump=0.8, rim=0.3, ao=0.2, wear=0.0)
    L = 2.5
    for k in range(4):
        a = k * math.pi / 2
        arm = pivot("arm", (0, 0, 0), R, rot=(0, a, 0))
        box("stock", (0.14, 0.1, L), wood, arm, loc=(0, 0, L / 2 + 0.2))
        box("rail1", (0.07, 0.07, L - 0.5), dark, arm, loc=(0.22, 0, 0.55 + (L - 0.5) / 2))
        box("rail2", (0.07, 0.07, L - 0.5), dark, arm, loc=(0.78, 0, 0.55 + (L - 0.5) / 2))
        box("tipbar", (0.63, 0.07, 0.07), dark, arm, loc=(0.5, 0, L + 0.07))
        for j in range(8):
            box("slat", (0.58, 0.05, 0.045), dark, arm, loc=(0.5, 0.01, 0.6 + j * (L - 0.7) / 7))
        if not EL.TRUTH or k != 1:
            box("canvas", (0.5, 0.03, (L - 0.7) * 0.55), cloth, arm, loc=(0.5, -0.02, 0.6 + (L - 0.7) * 0.28))
    ellipsoid("hub", 0.24, toon("#5a3a26", rim=0.5), R, seg=12, rings=8, scale=(1, 0.8, 1))
    ellipsoid("cap", 0.1, toon("gold", rim=0.6), R, loc=(0, -0.2, 0), seg=8, rings=6)
    R.rotation_euler = (math.radians(-ELEVATION_DEG), 0, 0)
    return dict(cell=(352, 352), anchor=(176, 176))


# =============================================================== (f) the Weavers' tower
def tower():
    R = pivot("F")
    h = 7.0
    rr = lambda z: 1.55 - (z - 0.7) * 0.045
    frustum("plinth", 2.3, 2.05, 0.7, ST("#8a90a8", "#6c7290", scale=2.2, moss=0.6), R, seg=28)
    frustum("shaft", 1.55, 1.25, h, ST("#8b95b8", "#7480a4", scale=2.2, wear=0.7, moss=0.3, bump=1.0), R, loc=(0, 0, 0.7), seg=28)
    for z in (2.2, 3.6, 5.0):
        frustum("band", rr(z) + 0.05, rr(z) + 0.05, 0.14, PL("#d8d4e4", "#bcb8d0", wear=0.3), R, loc=(0, 0, z), seg=28, caps=(False, False))
    cols = ["#e8884a", "#4f7ad8", "#e8b04a", "#c44b3f", "#a07ad8", "#f3e4c4", "#35b39a"]
    for tier, z in enumerate((1.5, 2.9, 4.3)):
        frustum("ledge", rr(z) + 0.28, rr(z) + 0.28, 0.07, WD("#8a5a30", "#704826", scale=4), R, loc=(0, 0, z), seg=28)
        n = 34
        for i in range(n):
            a = 2 * math.pi * i / n
            if math.sin(a) > 0.55:
                continue
            rad = rr(z) + 0.16
            spool(R, (math.cos(a) * rad, math.sin(a) * rad, z + 0.07), 0.07, 0.2, cols[(i + tier) % 7], glowing=(i % 7 == 0))
    bead_cloud(R, 1400, lambda z: rr(z) + 0.1, (0.9, 5.2), rad=0.04, seed=5)
    for s in range(1 if EL.TRUTH else 3):
        pts = []
        for i in range(61 if EL.TRUTH else 121):
            t = i / 120
            z = 0.9 + t * (2.6 if EL.TRUTH else 5.4)
            a = s * 2.094 + t * (2.0 if EL.TRUTH else 4.0) * math.pi * 2
            pts.append((math.cos(a) * (rr(z) + 0.18), math.sin(a) * (rr(z) + 0.18), z))
        tube("thread", pts, 0.028, glow("#35d3b0", 5.0), R)
        tube("halo", pts, 0.08, glow("#35d3b0", 1.5, alpha=0.18), R, res=2)
    bz = 5.5
    frustum("bal", 2.05, 2.05, 0.14, WD("#8a5a30", "#704826", scale=3, plane="xy"), R, loc=(0, 0, bz), seg=28)
    for i in range(28):
        a = 2 * math.pi * i / 28
        if math.sin(a) > 0.5:
            continue
        frustum("bp", 0.035, 0.035, 0.5, WDT(), R, loc=(math.cos(a) * 2.0, math.sin(a) * 2.0, bz + 0.14), seg=5)
    frustum("rail", 2.02, 2.02, 0.06, WDT(), R, loc=(0, 0, bz + 0.62), seg=28, caps=(False, False))
    for k in range(10):
        frustum("lan", 0.03, 0.03, 0.04, glow("#ffc66a", 5), R, loc=(math.cos(k * 0.6 + 3.3) * 2.02, math.sin(k * 0.6 + 3.3) * 2.02, bz + 0.64), seg=5)
    dp = pivot("door", (0, -2.02, 0.7), R)
    box("df", (1.3, 0.12, 1.9), toon("#4a4a6a", rim=0.2), dp, loc=(0, 0, 0.95))
    box("dl", (1.0, 0.1, 1.7), glow("#ff9a48", 1.7), dp, loc=(0, -0.05, 0.85))
    frustum("da", 0.5, 0.5, 0.1, glow("#ff9a48", 1.7), dp, loc=(0, -0.05, 1.7), rot=(RAD(90), 0, 0), seg=16)
    frustum("daf", 0.68, 0.68, 0.12, toon("#4a4a6a", rim=0.2), dp, loc=(0, 0.02, 1.7), rot=(RAD(90), 0, 0), seg=16)
    for k in range(3):
        box("step", (1.8 - k * 0.1, 0.5, 0.12), ST(scale=3, bump=0.5), R, loc=(0, -2.4 - k * 0.38, 0.06 - 0.0 * k))
    wz = 6.45
    wp = pivot("cw", (0.45, -rr(wz) + 0.02, wz), R, rot=(0, RAD(12), 0))
    box("wf", (0.8, 0.12, 1.1), toon("#3a3a5a", rim=0.2), wp)
    box("wg", (0.62, 0.06, 0.92), glow("#ffc66a", 2.8), wp, loc=(0, -0.07, 0))
    sil = toon("#241a3a", rim=0.0)
    frustum("robe", 0.2, 0.1, 0.5, sil, wp, loc=(0, -0.1, -0.44), seg=8)
    ellipsoid("head", 0.1, sil, wp, loc=(0, -0.1, 0.18), seg=8, rings=6)
    ellipsoid("cover", 0.12, sil, wp, loc=(0, -0.09, 0.12), scale=(1, 0.9, 1.1), seg=8, rings=6)
    wp2 = pivot("rw", (-0.8, -rr(4.0) + 0.0, 3.95), R)
    frustum("rf", 0.3, 0.3, 0.1, toon("#3a3a5a", rim=0.2), wp2, rot=(RAD(90), 0, 0), seg=16)
    frustum("rg", 0.24, 0.24, 0.1, glow("#ffc66a", 2.8), wp2, loc=(0, -0.05, 0), rot=(RAD(90), 0, 0), seg=16)
    rz = 0.7 + h
    rm = tex_toon("tiles", "#2f4a8a", "#27407a", scale=3.0, plane="xy", bump=1.0, wear=0.5, moss=0.2)
    frustum("roof", 1.95, 0.0, 2.6, rm, R, loc=(0, 0, rz - 0.05), seg=28, caps=(False, False))
    frustum("eave", 1.95, 1.95, 0.1, toon("#1f2f66", rim=0.3), R, loc=(0, 0, rz - 0.08), seg=28)
    spool(R, (0, 0, rz + 2.5), 0.22, 0.5, "#35d3b0", glowing=True)
    ellipsoid("fhalo", 0.7, glow("#35d3b0", 2.5, alpha=0.5, soft=True), R, loc=(0, 0, rz + 2.75), seg=12, rings=8)
    if EL.TRUTH:
        sagging_threads(R, [(-1.7, -1.5, 5.4), (1.9, -0.8, 5.4), (0.5, -2.0, 5.4)], seed=11)
    return dict(cell=(576, 832), anchor=(288, 690), smoke=[])


# ----------------------------------------------------------- truth-only outdoor props (same cell/anchor as props.png)
def tree_round():
    R = pivot("T1")
    bark = tex_toon("wood", "#6d4a33", "#59392a", scale=4, plane="xz", along="v", bump=1.0, moss=0.5)
    frustum("trunk", 0.3, 0.17, 1.6, bark, R, seg=10)
    for a in (0, 120, 240):
        ellipsoid("root", 0.14, bark, R, loc=(math.cos(RAD(a)) * 0.22, math.sin(RAD(a)) * 0.22, 0.08), scale=(1.4, 1, 0.7), seg=8, rings=6)
    rnd = random.Random(5)
    def branch(p, d, L, r, depth):
        e = (p[0] + d[0] * L, p[1] + d[1] * L, p[2] + d[2] * L)
        link_cyl("br", p, e, r, bark, R, seg=5, r2=r * 0.6)
        if depth > 0:
            for k in range(2):
                nd = Vector((d[0] + rnd.uniform(-.7, .7), d[1] + rnd.uniform(-.4, .4), d[2] * 0.8 + rnd.uniform(0.05, .5))).normalized()
                branch(e, nd, L * 0.72, r * 0.6, depth - 1)
        elif rnd.random() < 0.5:
            ellipsoid("lf", 0.07, toon("#7a6a4a", rim=0.2), R, loc=e, scale=(1, 0.5, 1.4), seg=6, rings=4)
    for a in (-0.7, 0.2, 0.9):
        branch((0, 0, 1.4), Vector((math.sin(a), rnd.uniform(-.3, .3), 0.9)).normalized(), 0.8, 0.09, 2)
    for i in range(7):   # dead leaves on the ground
        ellipsoid("dl", 0.07, toon("#7a6a4a", rim=0.1), R, loc=(rnd.uniform(-.9, .9), rnd.uniform(-.7, .4), 0.02), scale=(1, 0.6, 0.15), seg=6, rings=4)
    snapped_thread(R, (-0.5, -0.1, 2.3), 1.0, 0.1, seed=3, cut=True)
    return dict(cell=(192, 256), anchor=(96, 226))


def tree_pine():
    R = pivot("T2")
    bark = tex_toon("wood", "#6d4a33", "#59392a", scale=4, plane="xz", along="v", bump=1.0)
    frustum("trunk", 0.2, 0.06, 3.4, bark, R, seg=8)
    for i, (rr, z) in enumerate([(0.8, 0.8), (0.62, 1.4), (0.45, 2.0)]):
        frustum("tier", rr, 0.03, 0.6, toon("#5a5a3a", rim=0.3), R, loc=(0, 0, z), seg=7, caps=(False, False), scale=(1, 1, 1))
    for k in range(5):
        a = k * 1.3
        link_cyl("stub", (0, 0, 1.0 + k * 0.4), (math.cos(a) * 0.5, math.sin(a) * 0.4, 0.8 + k * 0.4), 0.025, bark, R, seg=4)
    snapped_thread(R, (0.0, -0.1, 3.0), 1.2, 0.1, seed=4, cut=False)
    return dict(cell=(160, 288), anchor=(80, 258))


def lamppost():
    R = pivot("L")
    frustum("base", 0.16, 0.12, 0.3, ST("#6a6270", "#544c5c", scale=3), R, seg=8)
    frustum("pole", 0.045, 0.045, 2.4, toon("#3a3640", rim=0.4), R, loc=(0, 0, 0.2), seg=8)
    box("cage", (0.3, 0.3, 0.4), toon("#2a2630", rim=0.3), R, loc=(0, 0, 2.5), base=True)
    box("glass", (0.22, 0.22, 0.34), glow("#ffc66a", 1.5), R, loc=(0, 0, 2.53), base=True)
    frustum("cap", 0.26, 0.02, 0.2, toon("#2a2630", rim=0.3), R, loc=(0, 0, 2.9), seg=4, rot=(0, 0, RAD(45)))
    snapped_thread(R, (0.15, -0.1, 2.4), 1.2, 0.08, seed=6, cut=True)
    return dict(cell=(112, 192), anchor=(56, 172))


TRUTH_ONLY = ("tree_round", "tree_pine", "lamppost")
BUILDERS = {"tree_round": tree_round, "tree_pine": tree_pine, "lamppost": lamppost, "print_house": print_house, "bakery": bakery, "mill": mill, "mill_sails": mill_sails, "tower": tower}
