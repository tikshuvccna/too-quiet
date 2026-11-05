"""World NPC sheets (23 villagers from content/he/world/npcs_world.json), v2 storybook-toon style.

blender -b --python art/blender/w_npcs.py -- <key[,key...]|all> <ABSOLUTE rawdir> [quick]
Writes <rawdir>/npcs/<key>/idle_<DIR>_<i>.png (SSAA 4, un-outlined); art/pack_w_npcs.py finishes them.
Specs live in w_npc_specs.py; this file holds the extra parts/props and the same render parameters as
v2_render.py (do_sprite in npc mode: idle 4 frames, dirs S SE E SW W, frame 3 = blink, anchor (64,110)).
"""
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector

from v2lib import *
from v2lib import STATE, TAU, mat, glow, pivot, ellipsoid, blob, loft, tube, box, cyl, add_lines, reset, render_setup, \
    world_and_lights, sprite_camera, render_to, args
from v2_parts import Human, darker, lighter
from v2_cast import SKIN, pose
import v2_cast_npc as N
from v2_cast_t3 import books as t3_books
from w_npc_specs import SPECS, ORDER

NPC_DIRS = [("S", 0), ("SE", 45), ("E", 90), ("SW", 315), ("W", 270)]   # same as v2_render.NPC_DIRS
WOOD = "#8a5a36"


# ====================================================================== helpers
def grip(h, side, name, loc=(0, 0, 0)):
    """Pivot in a hand whose axes are world-upright in the idle pose (cancels the forearm tilt)."""
    held = h.flags.get('hold') in (side, 'LR')
    return pivot(name, loc, h.P['hand' + side], rot=(1.25 if held else 0.15, 0, 0))


def ring_pts(c, rad, plane='xz', n=14, rz=None):
    rz = rad if rz is None else rz
    pts = []
    for i in range(n + 1):
        a = TAU * i / n
        if plane == 'xz':
            pts.append(Vector((c[0] + rad * math.cos(a), c[1], c[2] + rz * math.sin(a))))
        elif plane == 'yz':
            pts.append(Vector((c[0], c[1] + rad * math.cos(a), c[2] + rz * math.sin(a))))
        else:
            pts.append(Vector((c[0] + rad * math.cos(a), c[1] + rz * math.sin(a), c[2])))
    return pts


def on_skirt(h, a, t, k=1.06):
    """Point on the skirt surface (skirt pivot space): angle a (-pi/2 = front), t 0 waist .. 1 hem."""
    W, H = h.W, h.H
    flare = h.spec.get('skirt', {}).get('flare', 1.0)
    L = h.waist_z - 0.035 * H
    r = 0.185 * W + 0.17 * flare * W * (t ** 0.9)
    return Vector((r * math.cos(a) * k, 0.86 * r * math.sin(a) * k, -L * t))


def spool(parent, loc, c, rot=(0, 0, 0), s=1.0):
    sp = pivot("spool", loc, parent, rot=rot)
    cyl("thr", 0.032 * s, 0.032 * s, 0.06 * s, mat(c, pat='spiral', color2=darker(c, 0.75), P=dict(nu=10, fv=200)), sp,
        loc=(0, 0, -0.03 * s))
    for z in (-0.035, 0.03):
        cyl("flange", 0.04 * s, 0.04 * s, 0.008 * s, mat("#a06a3e", pat='wood'), sp, loc=(0, 0, z * s))
    return sp


# ====================================================================== headwear
def beanie(h, color, color2=None, z=0.4, pompom=None, tall=1.0, cuff=True):
    R = h.R
    hat = pivot("hat", (0, 0.02 * R, z * R), h.P['head'], rot=(-0.08, 0, 0))
    km = mat(color, pat='knit', P=dict(nu=44, fv=70), var=0.25, bump=0.6)
    blob("beanie", R * 1.08, km, hat, loc=(0, 0, 0.0), scale=(1.0, 1.02, 0.95 * tall),
         deform=lambda p: Vector((p.x, p.y, p.z if p.z > 0 else p.z * 0.12)), seg=48, rings=24)
    if cuff:
        cm = mat(color2 or darker(color, 0.85), pat='knit', P=dict(nu=60, fv=20), var=0.3, bump=0.7)
        loft("bcuff", [(-0.14 * R, R * 1.1, R * 1.12), (0.04 * R, R * 1.13, R * 1.15), (0.2 * R, R * 1.1, R * 1.12)], cm, hat,
             seg=48)
    if pompom:
        blob("pompom", R * 0.34, mat(pompom, pat='wool', P=dict(scale=90), var=0.3, bump=0.8), hat,
             loc=(0, 0.02 * R, 1.0 * R * tall), seg=24, rings=16)
    h.P['hat'] = hat
    return hat


def stocking_cap(h, color, color2, z=0.42):
    """Long knit cap whose tip flops down the back (with a tassel): reads from the side and back too."""
    R = h.R
    hat = beanie(h, color, color2, z=z, tall=1.1)
    km = mat(color, pat='knit', P=dict(nu=30, fv=70), var=0.25, bump=0.6)
    tube("sock", [Vector((0, 0.05 * R, 0.7 * R)), Vector((0.05 * R, 0.35 * R, 1.15 * R)), Vector((0.12 * R, 0.85 * R, 1.15 * R)),
                  Vector((0.18 * R, 1.15 * R, 0.75 * R)), Vector((0.2 * R, 1.2 * R, 0.45 * R))],
         [0.6 * R, 0.45 * R, 0.3 * R, 0.18 * R, 0.1 * R], km, hat, seg=16, sub=4)
    blob("tassel", R * 0.2, mat(color2, pat='wool', P=dict(scale=90), var=0.3), hat, loc=(0.2 * R, 1.2 * R, 0.33 * R),
         scale=(1, 1, 1.3), seg=16, rings=12)
    return hat


def pillbox(h, color, band, z=0.66):
    R = h.R
    hat = pivot("hat", (0, 0.1 * R, z * R), h.P['head'], rot=(-0.28, 0, 0))
    m = mat(color, pat='weave', P=dict(nu=60, fv=90), var=0.15)
    loft("pill", [(-0.05 * R, 0.8 * R, 0.8 * R), (0.2 * R, 0.82 * R, 0.82 * R), (0.32 * R, 0.76 * R, 0.76 * R),
                  (0.36 * R, 0.5 * R, 0.5 * R), (0.37 * R, 0.0, 0.0)], m, hat, seg=40)
    loft("pband", [(-0.06 * R, 0.82 * R, 0.82 * R), (0.04 * R, 0.83 * R, 0.83 * R)], mat(band, pat='weave'), hat, seg=40)
    h.P['hat'] = hat
    return hat


def captain_cap(h, top, band, visor, cord):
    R = h.R
    hat = pivot("hat", (0, -0.02 * R, 0.58 * R), h.P['head'], rot=(-0.06, 0, 0))
    bm = mat(band, pat='weave', P=dict(nu=40, fv=60))
    loft("cband", [(-0.06 * R, 1.04 * R, 1.06 * R), (0.24 * R, 1.06 * R, 1.08 * R)], bm, hat, seg=48)
    tm = mat(top, pat='weave', P=dict(nu=40, fv=60), var=0.1)
    loft("ctop", [(0.22 * R, 1.06 * R, 1.08 * R, 0, -0.02 * R), (0.3 * R, 1.26 * R, 1.24 * R, 0, -0.08 * R),
                  (0.38 * R, 1.28 * R, 1.26 * R, 0, -0.1 * R), (0.44 * R, 1.0 * R, 1.0 * R, 0, -0.08 * R),
                  (0.46 * R, 0.0, 0.0, 0, -0.06 * R)], tm, hat, seg=48)
    blob("cvisor", R, mat(visor, pat='leather', P=dict(scale=30), var=0.1), hat, loc=(0, -R * 0.95, -0.04 * R),
         scale=(0.74, 0.46, 0.07), deform=lambda p: Vector((p.x, min(p.y, 0.25), p.z)), rot=(-0.18, 0, 0), seg=32, rings=12)
    gm = mat(cord, metal=True)
    tube("ccord", [Vector((-0.7 * R, -0.82 * R, 0.02 * R)), Vector((0, -1.1 * R, 0.04 * R)), Vector((0.7 * R, -0.82 * R, 0.02 * R))],
         [0.05 * R], gm, hat, seg=8, sub=4)
    ellipsoid("cbadge", 0.13 * R, gm, hat, loc=(0, -1.08 * R, 0.14 * R), scale=(1, 0.4, 0.9), seg=12, rings=8)
    h.P['hat'] = hat
    return hat


HEADWEAR = dict(
    headscarf=lambda h, **kw: h.headscarf(**kw),
    wide_hat=lambda h, **kw: h.wide_hat(**kw),
    flat_cap=lambda h, **kw: h.flat_cap(**kw),
    beanie=beanie, stocking_cap=stocking_cap, pillbox=pillbox, captain_cap=captain_cap,
)


# ====================================================================== head extras
def glasses(h, color="#3a2a20"):
    R = h.R
    hp = h.P['head']
    m = mat(color, metal=True, line=False)
    for s in (-1, 1):
        tube("lensrim", ring_pts((s * 0.36 * R, -0.97 * R, 0.04 * R), 0.2 * R, 'xz', 16, 0.17 * R), [0.045 * R], m, hp, seg=6,
             sub=2, line=False)
        ellipsoid("lens", 0.19 * R, glow("#e8f4ff", 0.5, alpha=0.18), hp, loc=(s * 0.36 * R, -0.97 * R, 0.04 * R),
                  scale=(1, 0.08, 0.86), seg=12, rings=8)
        tube("temple", [Vector((s * 0.56 * R, -0.95 * R, 0.06 * R)), Vector((s * 0.88 * R, -0.5 * R, 0.08 * R)),
                        Vector((s * 0.98 * R, 0.0, 0.05 * R))], [0.035 * R], m, hp, seg=5, sub=3, line=False)
    tube("bridge", [Vector((-0.16 * R, -0.99 * R, 0.08 * R)), Vector((0, -1.04 * R, 0.12 * R)), Vector((0.16 * R, -0.99 * R, 0.08 * R))],
         [0.035 * R], m, hp, seg=5, sub=3, line=False)


def feather(h, color, color2):
    R = h.R
    hat = h.P['hat']
    a = math.radians(160)        # left-back side of the crown
    cx, cy = math.cos(a) * 1.0 * R, math.sin(a) * 1.0 * R + 0.25 * R
    pts = [Vector((cx, cy, 0.1 * R)), Vector((cx * 1.15, cy + 0.15 * R, 0.6 * R)), Vector((cx * 1.25, cy + 0.45 * R, 1.05 * R)),
           Vector((cx * 1.2, cy + 0.85 * R, 1.25 * R))]
    tube("feather", pts, [0.03 * R, 0.17 * R, 0.14 * R, 0.02 * R], mat(color, pat='vstripes', color2=lighter(color, 0.3),
                                                                      P=dict(nu=30, fv=30, thr=0.6)), hat, seg=10, flat=0.3)
    tube("feather2", [p + Vector((0.06 * R, 0.02 * R, 0)) for p in pts[:3]], [0.02 * R, 0.1 * R, 0.02 * R],
         mat(color2, kind='soft'), hat, seg=8, flat=0.3)


def hat_bell(h):
    R = h.R
    hat = h.P['hat']
    a = math.radians(-35)
    x, y = math.cos(a) * 1.4 * R, math.sin(a) * 1.4 * R
    tube("bellcord", [Vector((x, y, -0.12 * R)), Vector((x, y, -0.4 * R))], [0.025 * R], mat("#c8a040", pat='weave'), hat,
         seg=5, sub=1)
    gm = mat("#f0c040", metal=True)
    loft("hbell", [(-0.4 * R, 0.06 * R, 0.06 * R), (-0.5 * R, 0.13 * R, 0.13 * R), (-0.62 * R, 0.17 * R, 0.17 * R),
                   (-0.66 * R, 0.18 * R, 0.18 * R)], gm, hat, loc=(x, y, 0), seg=20, cap_bot=False)
    ellipsoid("hbelltop", 0.08 * R, gm, hat, loc=(x, y, -0.42 * R), seg=10, rings=6)
    ellipsoid("hbellclap", 0.05 * R, gm, hat, loc=(x, y, -0.68 * R), seg=8, rings=6)


HEAD_EXTRAS = dict(glasses=glasses, feather=feather, hat_bell=lambda h: hat_bell(h))


# ====================================================================== body extras
def tape(h):
    """Tailor's measuring tape draped round the neck, both ends hanging in front (tick marks = stripes)."""
    up, th, W = h.P['upper'], h.torso_h, h.W
    m = mat("#ecc84a", pat='stripes', color2="#3a2a20", P=dict(nu=8, fv=110, thr=0.86, weave=False), var=0.0, kind='soft')
    for s in (-1, 1):
        pts = [Vector((s * 0.065 * W, -0.168 * W, th * 0.3 - (0.05 if s > 0 else 0))), Vector((s * 0.075 * W, -0.165 * W, th * 0.6)),
               Vector((s * 0.085 * W, -0.13 * W, th * 0.9)), Vector((s * 0.1 * W, -0.04 * W, th * 1.02)),
               Vector((s * 0.06 * W, 0.08 * W, th * 1.02)), Vector((0, 0.1 * W, th * 1.0))]
        tube("tape", pts, [0.028], m, up, seg=8, sub=4, flat=0.22)
        ellipsoid("tapeend", 0.016, mat("#c9a040", metal=True), up, loc=pts[0] + Vector((0, -0.004, -0.01)), scale=(1.6, 0.5, 0.8),
                  seg=8, rings=6)


def pincushion(h, side='L'):
    el = h.P['elbow' + side]
    fa = 0.18 * h.H
    sx = 1 if side == 'L' else -1
    p = pivot("pincush", (sx * 0.045 * h.W, -0.01, -fa + 0.07), el)
    loft("pcband", [(-0.012, 0.058 * h.W, 0.056 * h.W), (0.012, 0.058 * h.W, 0.056 * h.W)], mat("#3a2a20", pat='leather'), p,
         loc=(-sx * 0.045 * h.W, 0.01, 0), seg=16)
    ellipsoid("cushion", 0.042, mat("#c43a4a", pat='weave', P=dict(nu=12, fv=60)), p, scale=(0.75, 1, 0.85), seg=14, rings=10)
    for k, c in enumerate(("#f0c040", "#4a78c8", "#f6f2ea", "#35b090", "#f0c040")):
        a = k * 1.3
        d = Vector((math.cos(a) * 0.4, math.sin(a) * 0.6, 0.75)).normalized()
        tube("pin", [d * 0.03, d * 0.06], [0.003], mat("#d8d8e0", metal=True), p, seg=4, sub=1, line=False)
        ellipsoid("pinhead", 0.008, mat(c, kind='soft', line=False), p, loc=d * 0.062, seg=6, rings=4)


def chalk_pocket(h):
    sk = h.P['skirt']
    a, t = -math.pi / 2 - 0.55, 0.22
    loc = on_skirt(h, a, t, 1.07)
    rz = a - math.pi / 2
    ellipsoid("pocket", 0.06 * h.W, mat("#5a3454", pat='weave', P=dict(nu=10, fv=90)), sk, loc=loc, rot=(0, 0, rz),
              scale=(1.0, 0.3, 0.85), seg=16, rings=8)
    cyl("chalk", 0.011, 0.011, 0.07, mat("#fbfbf6", kind='soft'), sk, loc=loc + Vector((0.01, -0.005, 0.0)),
        rot=(0.15, -0.25, 0), seg=10)
    cyl("chalk2", 0.01, 0.01, 0.06, mat("#f0d0e0", kind='soft'), sk, loc=loc + Vector((-0.012, -0.003, -0.005)),
        rot=(0.1, 0.2, 0), seg=10)


def scarf_neck(h, **kw):
    N.scarf_neck(h, **kw)


def long_scarf(h, color, color2):
    """Theatrical striped scarf: wrapped low on the collar, two long tails (kept clear of the short beard)."""
    up, th = h.P['upper'], h.torso_h
    m = mat(color, pat='stripes', color2=color2, P=dict(nu=30, fv=26, thr=0.5), var=0.15, bump=0.4)
    loft("lscarf", [(th * 0.84, 0.125, 0.115), (th * 0.94, 0.122, 0.11), (th * 1.03, 0.1, 0.092)], m, up, seg=32,
         folds=lambda a, t: 1 + 0.07 * math.sin(6 * a + t * 3))
    for s, dz in ((1, 0.0), (-1, 0.08)):
        tube("ltail", [Vector((s * 0.05, -0.12, th * 0.9)), Vector((s * 0.08, -0.17, th * 0.55)),
                       Vector((s * 0.09 + 0.02, -0.19, th * 0.1 + dz)), Vector((s * 0.1 + 0.03, -0.2, -0.08 + dz))],
             [0.04, 0.045, 0.045, 0.04], m, up, seg=10, flat=0.3)
        for k in range(3):   # fringe
            tube("lfr", [Vector((s * 0.1 + 0.03 + 0.02 * (k - 1), -0.2, -0.08 + dz)),
                         Vector((s * 0.1 + 0.03 + 0.025 * (k - 1), -0.2, -0.13 + dz))], [0.008], mat(color2, kind='soft'), up,
                 seg=4, sub=1, line=False)


def suspenders(h, color):
    N.suspenders(h, color)


def shawl(h, color, color2):
    up, th = h.P['upper'], h.torso_h
    sm = mat(color, pat='knit', color2=color2, P=dict(nu=40, fv=55, stripe=10), var=0.2, bump=0.5)
    loft("shawl", [(th * 1.02, 0.1, 0.09), (th * 0.92, 0.215 * h.W, 0.18 * h.W), (th * 0.58, 0.235 * h.W, 0.2 * h.W)], sm, up,
         seg=48, folds=lambda a, t: 1 + 0.04 * t * math.sin(6 * a))
    ellipsoid("shawlpin", 0.024, mat("#e8b04a", metal=True), up, loc=(0, -0.2 * h.W, th * 0.72), scale=(1, 0.5, 1), seg=10,
              rings=6)


def spyglass(h):
    """Leather strap across the body + brass spyglass at the left hip."""
    up, th, W, H = h.P['upper'], h.torso_h, h.W, h.H
    side = 1
    x = side * 0.21 * W
    z = 0.06 * H
    sm = mat("#6b4326", pat='leather', var=0.15)
    pts = [Vector((x, -0.04, z + 0.04)), Vector((-side * 0.05 * W, -0.165 * W - 0.012, th * 0.55)),
           Vector((-side * 0.14 * W, -0.11 * W, th * 0.92)), Vector((-side * 0.16 * W, 0.04, th * 0.98)),
           Vector((-side * 0.04 * W, 0.16 * W + 0.01, th * 0.6)), Vector((x * 0.95, 0.06, z + 0.04))]
    tube("sstrap", pts, [0.01], sm, up, seg=6, sub=4, flat=0.4)
    sg = pivot("spyglass", (x + 0.02, -0.02, z), up, rot=(0.0, 1.1, 0.35))
    bm = mat("#d8a840", metal=True)
    cyl("sg1", 0.034, 0.034, 0.12, bm, sg, loc=(0, 0, -0.12), seg=16)
    cyl("sg2", 0.03, 0.03, 0.1, mat("#5a3a22", pat='leather'), sg, loc=(0, 0, 0.0), seg=16)
    cyl("sg3", 0.024, 0.024, 0.09, bm, sg, loc=(0, 0, 0.1), seg=16)
    cyl("sgring", 0.038, 0.038, 0.016, bm, sg, loc=(0, 0, -0.125), seg=16)
    ellipsoid("sglens", 0.03, glow("#bfe8ff", 1.2), sg, loc=(0, 0, -0.128), scale=(1, 1, 0.2), seg=10, rings=6)


def leaf_collar(h):
    up, th, W = h.P['upper'], h.torso_h, h.W
    cols = ("#4f8a2a", "#7ab83a", "#9ac84a")
    for k in range(14):
        a = TAU * k / 14 + 0.1
        ellipsoid("leaf", 0.07, mat(cols[k % 3], kind='cloth', pat='vstripes', color2=darker(cols[k % 3], 0.75),
                                     P=dict(nu=2, fv=10, thr=0.93)), up,
                  loc=(0.16 * W * math.cos(a), 0.13 * W * math.sin(a), th * 0.93), scale=(1.0, 0.55, 0.14),
                  rot=(0, 0.55, a), seg=14, rings=8)


def mantle(h, color, trim):
    up, th, W = h.P['upper'], h.torso_h, h.W
    m = mat(color, pat='weave', P=dict(nu=40, fv=50), var=0.14)
    loft("mantle", [(th * 1.04, 0.1 * W, 0.09 * W), (th * 0.92, 0.2 * W, 0.17 * W), (th * 0.72, 0.265 * W, 0.225 * W),
                    (th * 0.6, 0.275 * W, 0.235 * W)], m, up, seg=56, folds=lambda a, t: 1 + 0.04 * t * math.sin(7 * a))
    loft("mtrim", [(th * 0.585, 0.277 * W, 0.237 * W), (th * 0.63, 0.279 * W, 0.239 * W)], mat(trim, metal=True), up, seg=56,
         folds=lambda a, t: 1 + 0.04 * math.sin(7 * a))


def sash(h, color, color2):
    up, th, W = h.P['upper'], h.torso_h, h.W
    m = mat(color, pat='vstripes', color2=color2, P=dict(nu=3, fv=30, thr=0.6), var=0.1)
    pts = [Vector((0.13 * W, 0.0, th * 1.02)), Vector((0.07 * W, -0.21 * W, th * 0.86)), Vector((-0.05 * W, -0.255 * W, th * 0.52)),
           Vector((-0.17 * W, -0.19 * W, th * 0.16)), Vector((-0.23 * W, 0.0, th * 0.06)), Vector((-0.12 * W, 0.2 * W, th * 0.4)),
           Vector((0.08 * W, 0.17 * W, th * 0.86)), Vector((0.13 * W, 0.0, th * 1.02))]
    tube("sash", pts, [0.042], m, up, seg=10, sub=4, flat=0.25)
    gm = mat("#e8c050", metal=True)
    cyl("medal", 0.045, 0.045, 0.014, gm, up, loc=(0.0, -0.262 * W, th * 0.6), rot=(math.pi / 2, 0, 0), seg=20)
    ellipsoid("medalc", 0.022, mat("#a83a3a", kind='soft'), up, loc=(0.0, -0.272 * W, th * 0.6), scale=(1, 0.4, 1), seg=10,
              rings=6)


def double_buttons(h, color):
    up, th, W = h.P['upper'], h.torso_h, h.W
    bm = mat(color, metal=True, line=False)
    for s in (-1, 1):
        for i in range(3):
            t = 0.3 + 0.24 * i
            ellipsoid("dbtn", 0.02, bm, up, loc=(s * 0.075 * W, -0.152 * W - 0.008, th * t), scale=(1, 0.5, 1), seg=10, rings=6)
    # lapels
    lm = mat(darker(h.spec['torso']['color'], 0.8), pat='weave')
    for s in (-1, 1):
        tube("lapel", [Vector((s * 0.03 * W, -0.165 * W, th * 0.85)), Vector((s * 0.1 * W, -0.15 * W, th * 0.9)),
                       Vector((s * 0.095 * W, -0.1 * W, th * 1.0))], [0.03], lm, up, seg=6, sub=3, flat=0.3)


def seagull(h):
    up, th, W = h.P['upper'], h.torso_h, h.W
    g = pivot("gull", (0.16 * W, 0.01, th * 0.76 + 0.075), up, rot=(0, 0, 0.35))
    wm = mat("#fbfaf6", kind='soft', rim=0.5)
    gm = mat("#9aa4b4", kind='cloth')
    km = mat("#2a2a30", kind='soft')
    om = mat("#f0a030", kind='soft')
    ellipsoid("gbody", 0.058, wm, g, loc=(0, 0.0, 0.05), scale=(0.78, 1.35, 0.8), rot=(-0.2, 0, 0), seg=18, rings=12)
    ellipsoid("ghead", 0.04, wm, g, loc=(0, -0.07, 0.105), seg=14, rings=10)
    tube("gbeak", [Vector((0, -0.1, 0.103)), Vector((0, -0.145, 0.095))], [0.012, 0.006], om, g, seg=8, sub=1)
    for s in (-1, 1):
        ellipsoid("geye", 0.008, km, g, loc=(s * 0.026, -0.093, 0.115), seg=6, rings=4, line=False)
        ellipsoid("gwing", 0.06, gm, g, loc=(s * 0.042, 0.02, 0.06), scale=(0.25, 1.25, 0.55), rot=(-0.25, 0, -s * 0.12),
                  seg=14, rings=8)
        ellipsoid("gtip", 0.03, km, g, loc=(s * 0.04, 0.09, 0.045), scale=(0.3, 1.3, 0.5), rot=(-0.3, 0, 0), seg=10, rings=6)
        ellipsoid("gfoot", 0.012, om, g, loc=(s * 0.018, -0.01, 0.0), scale=(1, 1.6, 0.5), seg=6, rings=4)
    ellipsoid("gtail", 0.03, wm, g, loc=(0, 0.085, 0.04), scale=(0.7, 1.2, 0.35), rot=(-0.3, 0, 0), seg=10, rings=6)


def flute_belt(h):
    up, th, W = h.P['upper'], h.torso_h, h.W
    fp = pivot("flute", (-0.12 * W, -0.175 * W, 0.04), up, rot=(0.15, -0.6, 0.0))
    fm = mat("#c89a5a", pat='wood', var=0.2)
    cyl("fbody", 0.015, 0.014, 0.28, fm, fp, loc=(0, 0, -0.12), seg=10)
    for k in range(4):
        ellipsoid("fhole", 0.006, mat("#2a1a14", kind='flat'), fp, loc=(0, -0.014, -0.04 + 0.045 * k), scale=(1, 0.4, 1),
                  seg=6, rings=4, line=False)
    tube("fcord", [Vector((0.0, 0.0, 0.14)), Vector((0.02, -0.01, 0.17)), Vector((0.05, 0.0, 0.15))], [0.006],
         mat("#c44b3f", pat='weave'), fp, seg=5, sub=3, line=False)


def dye_stains(h):
    sk = h.P['skirt']
    cols = ("#c43a5a", "#e8b030", "#3a6ac8", "#7a3a9a", "#3a9a5a", "#e8703a")
    spots = [(-1.9, 0.25, 0.07), (-1.3, 0.55, 0.09), (-2.2, 0.75, 0.06), (-1.6, 0.85, 0.08), (-0.9, 0.35, 0.06),
             (-2.5, 0.5, 0.07), (-1.15, 0.8, 0.05), (-0.6, 0.65, 0.07), (-2.8, 0.3, 0.05), (0.4, 0.6, 0.07), (1.6, 0.45, 0.07),
             (2.6, 0.7, 0.06)]
    for k, (a, t, s) in enumerate(spots):
        loc = on_skirt(h, a, t, 1.065)
        m = mat(cols[k % len(cols)], kind='soft', rim=0.2, line=False)
        ellipsoid("dye", s, m, sk, loc=loc, rot=(0, 0, a - math.pi / 2), scale=(1.0, 0.12, 0.75 + 0.3 * math.sin(k)), seg=14,
                  rings=8, line=False)
        loc2 = on_skirt(h, a + 0.12, t + 0.06, 1.065)
        ellipsoid("dyedrop", s * 0.35, m, sk, loc=loc2, rot=(0, 0, a - math.pi / 2), scale=(1, 0.15, 1), seg=8, rings=6,
                  line=False)


def spool_cord(h):
    up, W = h.P['upper'], h.W
    cp = pivot("scord", (0.19 * W, -0.06 * W, 0.0), up)
    tube("cord", [Vector((0, 0, 0.02)), Vector((0.01, -0.01, -0.06)), Vector((0.0, -0.01, -0.2))], [0.007],
         mat("#8a5a36", pat='weave'), cp, seg=5, sub=3, line=False)
    for k, c in enumerate(("#35d3b0", "#c44b3f", "#e8b04a")):
        spool(cp, (0.0, -0.012, -0.07 - 0.065 * k), c, rot=(0, 0, 0.3 * k), s=0.85)


def planks(h):
    """Three boards balanced on the right shoulder (the right hand steadies them, see carry pose)."""
    up, th, W = h.P['upper'], h.torso_h, h.W
    pp = pivot("planks", (-0.15 * W, 0.0, th * 0.76 + 0.105), up, rot=(0.22, 0.12, 0))
    for k, (c, dx) in enumerate((("#c89a5a", 0.0), ("#a87a3e", -0.03), ("#b98a4a", 0.02))):
        box("plank", (0.1, 1.05, 0.032), mat(c, pat='wood', P=dict(nu=2), var=0.25), pp, loc=(dx, 0.08 - 0.06 * k, 0.034 * k),
            bevel=0.008)


def rope_bandolier(h):
    """A coil of rope worn over the left shoulder and under the right arm."""
    up, th, W = h.P['upper'], h.torso_h, h.W
    rm = mat("#c9a870", pat='spiral', color2="#a8885a", P=dict(nu=4, fv=120), var=0.2)
    top = Vector((0.12 * W, 0.0, th * 1.0 + 0.03))
    bot = Vector((-0.24 * W, 0.0, th * 0.1))
    c = (top + bot) / 2
    d = (top - bot) / 2
    for k, sc in enumerate((1.0, 1.05, 1.1)):
        pts = []
        for i in range(17):
            a = TAU * i / 16
            p = c + d * math.cos(a) * (1 + 0.03 * k) + Vector((0, -0.215 * W * sc * math.sin(a), 0))
            pts.append(p)
        tube("ropeb", pts, [0.022], rm, up, seg=8, sub=3)


BODY = dict(tape=tape, pincushion=pincushion, chalk_pocket=chalk_pocket, scarf_neck=scarf_neck, long_scarf=long_scarf,
            suspenders=suspenders, shawl=shawl, spyglass=spyglass, leaf_collar=leaf_collar, mantle=mantle, sash=sash,
            double_buttons=double_buttons, seagull=seagull, flute_belt=flute_belt, dye_stains=dye_stains,
            spool_cord=spool_cord, planks=planks, rope_bandolier=rope_bandolier)


# ====================================================================== hand props
def teapot(h, side='L'):
    p = grip(h, side, "teapot")
    m = mat("#c8743a", metal=True)
    blob("tbody", 0.075, m, p, loc=(0, -0.05, -0.08), scale=(1, 1, 0.82), seg=24, rings=16)
    loft("tstripe", [(-0.004, 0.077, 0.077), (0.016, 0.076, 0.076)], mat("#f3e4c4", kind='soft'), p, loc=(0, -0.05, -0.08), seg=24,
         line=False)
    cyl("tlid", 0.04, 0.03, 0.02, m, p, loc=(0, -0.05, -0.02), seg=16)
    ellipsoid("tknob", 0.014, mat("#3a2418", pat='wood'), p, loc=(0, -0.05, 0.005), seg=8, rings=6)
    tube("tspout", [Vector((0, -0.11, -0.1)), Vector((0, -0.15, -0.07)), Vector((0, -0.17, -0.03))], [0.02, 0.013, 0.01], m, p,
         seg=10, sub=3)
    tube("thandle", [Vector((0, 0.0, -0.04)), Vector((0, 0.04, -0.06)), Vector((0, 0.03, -0.11)), Vector((0, 0.01, -0.12))],
         [0.012], m, p, seg=8, sub=3)


def oil_can(h, side='R'):
    p = grip(h, side, "oilcan")
    m = mat("#6a7a6a", metal=True)
    cyl("ocbody", 0.055, 0.055, 0.08, m, p, loc=(0, -0.04, -0.13), seg=20)
    loft("occone", [(0, 0.055, 0.055), (0.05, 0.02, 0.02), (0.06, 0.012, 0.012)], m, p, loc=(0, -0.04, -0.05), seg=20)
    tube("ocspout", [Vector((0, -0.04, 0.0)), Vector((0, -0.1, 0.06)), Vector((0, -0.18, 0.11))], [0.009, 0.006, 0.004],
         mat("#c9a040", metal=True), p, seg=8, sub=2)
    tube("ochandle", [Vector((0, 0.01, -0.06)), Vector((0, 0.05, -0.08)), Vector((0, 0.03, -0.12))], [0.01], m, p, seg=6, sub=3)
    ellipsoid("ocdrip", 0.012, mat("#3a3020", kind='soft'), p, loc=(0, -0.04, -0.135), scale=(1.6, 1.6, 0.3), seg=8, rings=6)


def slate(h, side='L'):
    p = grip(h, side, "slate", (0, -0.03, 0.02))
    sp = pivot("slatep", (0.04, -0.03, 0.02), p, rot=(0.15, 0, -0.35))
    box("sframe", (0.24, 0.022, 0.18), mat("#a06a3e", pat='wood', var=0.2), sp, bevel=0.01)
    box("sboard", (0.205, 0.026, 0.145), mat("#2e3e38", kind='soft', rim=0.2), sp, loc=(0, -0.002, 0))
    wm = mat("#f2f2ea", kind='soft', rim=0, line=False)
    dots = [(-0.06, 0.03), (0.0, -0.035), (0.065, 0.03), (0.0, 0.045)]
    for (x, z) in dots:
        ellipsoid("sdot", 0.012, wm, sp, loc=(x, -0.016, z), scale=(1, 0.3, 1), seg=8, rings=6, line=False)
    for a, b in ((0, 1), (1, 2), (0, 3), (3, 2)):
        tube("sline", [Vector((dots[a][0], -0.016, dots[a][1])), Vector((dots[b][0], -0.016, dots[b][1]))], [0.003], wm, sp,
             seg=4, sub=1, line=False)


def rope_coil(h, side='R'):
    p = grip(h, side, "ropecoil")
    rm = mat("#c9a870", pat='spiral', color2="#a8885a", P=dict(nu=4, fv=120), var=0.2)
    sx = 1 if side == 'L' else -1
    for k in range(3):
        c = (sx * (0.03 + 0.012 * k), -0.03 + 0.012 * k, -0.12 - 0.01 * k)
        tube("coil", ring_pts(c, 0.085 - 0.004 * k, 'xz', 14, 0.1), [0.018], rm, p, seg=8, sub=3)
    tube("ropeend", [Vector((sx * 0.06, -0.03, -0.22)), Vector((sx * 0.08, -0.05, -0.3)), Vector((sx * 0.06, -0.04, -0.36))],
         [0.016], rm, p, seg=8, sub=3)


def gear(h, side='R'):
    p = grip(h, side, "gear", (0, -0.04, 0.02))
    gp = pivot("gearp", (0, -0.02, 0.03), p, rot=(math.pi / 2, 0, 0.2))
    m = mat("#c9a040", metal=True)
    cyl("gdisc", 0.075, 0.075, 0.026, m, gp, loc=(0, 0, -0.013), seg=32)
    for k in range(10):
        a = TAU * k / 10
        box("gtooth", (0.03, 0.026, 0.026), m, gp, loc=(math.cos(a) * 0.085, math.sin(a) * 0.085, 0), rot=(0, 0, a), bevel=0.004)
    cyl("ghole", 0.022, 0.022, 0.03, mat("#3a2a18", kind='flat'), gp, loc=(0, 0, -0.015), seg=16, line=False)


def books(h, side='L'):
    t3_books(h.P['hand' + side])


def notebook(h, side='L', color="#2f62b0"):
    p = grip(h, side, "notebook", (0, -0.02, 0.0))
    np_ = pivot("nbp", (0.02, -0.03, 0.02), p, rot=(0.25, 0, -0.3))
    box("nbcover", (0.15, 0.03, 0.2), mat(color, pat='leather', var=0.2), np_, bevel=0.008)
    box("nbpages", (0.135, 0.034, 0.185), mat("#fbf4e0", kind='soft'), np_, loc=(0.008, 0, 0))
    box("nbband", (0.012, 0.036, 0.205), mat("#e8b04a", kind='soft'), np_, loc=(0.05, 0, 0))


def hay_fork(h, side='R'):
    p = grip(h, side, "hayfork", (0, -0.01, 0.0))
    wm = mat("#a87a48", pat='wood', P=dict(nu=4), var=0.25)
    tm = mat("#c89a5a", pat='wood', P=dict(nu=4), var=0.2)
    tube("hfpole", [Vector((0, 0, -0.55)), Vector((0, -0.01, 0.2)), Vector((0, -0.02, 0.62))], [0.018], wm, p, seg=8, sub=2)
    tube("hfbar", [Vector((-0.08, -0.02, 0.63)), Vector((0, -0.025, 0.62)), Vector((0.08, -0.02, 0.63))], [0.016], tm, p, seg=8,
         sub=2)
    for x in (-0.07, 0.0, 0.07):
        tube("hftine", [Vector((x, -0.02, 0.63)), Vector((x * 1.05, -0.03, 0.73)), Vector((x * 1.1, -0.06, 0.82))],
             [0.014, 0.012, 0.011], tm, p, seg=8, sub=3)


def staff(h, side='R'):
    p = grip(h, side, "staff")
    wm = mat("#7a5232", pat='wood', P=dict(nu=5), var=0.25)
    tube("staffp", [Vector((0, 0, -0.58)), Vector((0, 0.0, 0.1)), Vector((0, -0.01, 0.62))], [0.02, 0.018, 0.019], wm, p, seg=8,
         sub=3)
    blob("staffknob", 0.03, wm, p, loc=(0, -0.01, 0.64), scale=(1, 1, 1.2), seg=12, rings=8)
    tube("staffwrap", [Vector((0, -0.0, 0.0)), Vector((0, 0.0, 0.08))], [0.024], mat("#c44b3f", pat='weave'), p, seg=8, sub=1)


def herb_basket(h, side='L'):
    p = grip(h, side, "hbasket")

    def contents(b, r, depth):
        N.herbs(b, (-0.04, 0.0, depth * 0.4))
        N.herbs(b, (0.04, 0.02, depth * 0.3))
        for k, c in enumerate(("#c88ad8", "#f0d050", "#e87a8a")):
            a = TAU * k / 3 + 0.5
            ellipsoid("bloom", 0.025, mat(c, kind='soft'), b, loc=(math.cos(a) * r * 0.55, math.sin(a) * r * 0.55, depth * 1.05),
                      seg=8, rings=6)
    N.basket(h, p, (0.0, -0.05, -0.14), r=0.11, depth=0.1, contents=contents)
    tube("bhandle", [Vector((-0.1, -0.05, -0.04)), Vector((0, -0.05, 0.04)), Vector((0.1, -0.05, -0.04))], [0.012],
         mat("#b98a4a", pat='weave', P=dict(nu=36, fv=90)), p, seg=6, sub=3)


def acorn_lamp(h, side='R'):
    p = grip(h, side, "acorn")
    tube("acord", [Vector((0, -0.02, 0.0)), Vector((0, -0.03, -0.05))], [0.006], mat("#5a3a20", pat='weave'), p, seg=4, sub=1,
         line=False)
    cap = mat("#7a5230", pat='knit', P=dict(nu=20, fv=150), var=0.3, bump=0.6)
    blob("acap", 0.04, cap, p, loc=(0, -0.03, -0.065), scale=(1, 1, 0.6), deform=lambda q: Vector((q.x, q.y, max(q.z, -0.2))),
         seg=16, rings=10)
    ellipsoid("abody", 0.034, glow("#d8f070", 3.5), p, loc=(0, -0.03, -0.1), scale=(1, 1, 1.25), seg=14, rings=10)
    ellipsoid("ahalo", 0.09, glow("#c8f070", 1.4, alpha=0.5, soft=True), p, loc=(0, -0.03, -0.1), seg=12, rings=8)
    h.glow_light(p, (0, -0.1, -0.1), "#d8f070", 4, 0.05)


def hand_bell(h, side='R'):
    N.hand_bell(h, h.P['hand' + side])


def cake(h, side='L'):
    p = grip(h, side, "cake", (0.02, -0.04, 0.0))
    cyl("plate", 0.13, 0.12, 0.014, mat("#f6f2ea", kind='soft'), p, loc=(0, -0.03, 0.0), seg=28)
    sp = mat("#f0c8d8", pat='noise', P=dict(scale=30), var=0.08)
    cyl("tier1", 0.095, 0.095, 0.06, mat("#e8b8c8", kind='cloth'), p, loc=(0, -0.03, 0.014), seg=28)
    loft("drip", [(0.06, 0.098, 0.098), (0.075, 0.099, 0.099)], mat("#fffaf2", kind='soft'), p, loc=(0, -0.03, 0.014), seg=28,
         folds=lambda a, t: 1 + 0.02 * math.sin(9 * a))
    cyl("tier2", 0.065, 0.065, 0.05, sp, p, loc=(0, -0.03, 0.084), seg=28)
    cyl("icing", 0.068, 0.066, 0.012, mat("#fffaf2", kind='soft'), p, loc=(0, -0.03, 0.13), seg=28)
    ellipsoid("cherry", 0.022, mat("#d02a3a", kind='soft', rim=0.6), p, loc=(0, -0.03, 0.162), seg=12, rings=8)
    tube("stem", [Vector((0, -0.03, 0.18)), Vector((0.01, -0.025, 0.2))], [0.004], mat("#4a7a2a", kind='soft'), p, seg=4, sub=1,
         line=False)
    for k in range(8):
        a = TAU * k / 8
        ellipsoid("cream", 0.014, mat("#fffaf2", kind='soft'), p, loc=(math.cos(a) * 0.08, -0.03 + math.sin(a) * 0.08, 0.08),
                  seg=8, rings=6)


def paper_boat(h, side='R'):
    p = grip(h, side, "boat", (0, -0.04, 0.0))
    bp = pivot("boatp", (0, -0.03, 0.03), p, rot=(0, 0, math.pi / 2 - 0.4))
    s = 1.3
    A, B = Vector((0, -0.11, 0.045)) * s, Vector((0, 0.11, 0.045)) * s
    C, D = Vector((0.045, 0, 0.045)) * s, Vector((-0.045, 0, 0.045)) * s
    E, F = Vector((0, -0.05, -0.02)) * s, Vector((0, 0.05, -0.02)) * s
    pm = mat("#fbfaf2", kind='soft', rim=0.5)
    mesh_obj("hull", [A, B, C, D, E, F], [(0, 4, 2), (4, 5, 2), (5, 1, 2), (0, 3, 4), (4, 3, 5), (5, 3, 1)], pm, bp, smooth=False)
    T = Vector((0, 0, 0.14)) * s
    for dx in (-0.01, 0.01):
        mesh_obj("sail", [Vector((dx, -0.055, 0.045)) * s, Vector((dx, 0.055, 0.045)) * s, T + Vector((dx * 0.2, 0, 0))],
                 [(0, 1, 2)], mat("#f4f0e4", kind='soft'), bp, smooth=False)


def firefly_jar(h, side='L'):
    p = grip(h, side, "jar", (0, -0.04, 0.0))
    jp = pivot("jarp", (0, -0.03, -0.02), p)
    loft("jglass", [(0.0, 0.05, 0.05), (0.01, 0.06, 0.06), (0.11, 0.06, 0.06), (0.13, 0.045, 0.045), (0.14, 0.045, 0.045)],
         glow("#cfe8ff", 0.7, alpha=0.32, soft=True), jp, seg=24, cap_bot=True, line=False)
    loft("jrim", [(0.0, 0.051, 0.051), (0.012, 0.061, 0.061)], mat("#9ab8c8", kind='soft', line=False), jp, seg=24, line=False)
    cyl("jlid", 0.05, 0.048, 0.03, mat("#8a5a36", pat='wood'), jp, loc=(0, 0, 0.14), seg=16)
    tube("jstring", [Vector((-0.045, 0, 0.15)), Vector((0, 0, 0.2)), Vector((0.045, 0, 0.15))], [0.005], mat("#c9a870"), jp, seg=4,
         sub=3, line=False)
    for k, (x, y, z) in enumerate(((0.02, -0.01, 0.04), (-0.025, 0.01, 0.07), (0.01, 0.02, 0.1), (-0.01, -0.02, 0.09),
                                   (0.03, 0.0, 0.08))):
        ellipsoid("fly", 0.011, glow("#e8ff70", 6), jp, loc=(x, y, z), seg=8, rings=6)
    ellipsoid("jhalo", 0.12, glow("#d8ff80", 1.3, alpha=0.45, soft=True), jp, loc=(0, 0, 0.07), seg=14, rings=10)
    h.glow_light(jp, (0, -0.08, 0.07), "#d8ff70", 6, 0.05)


def skeins(h, side='L'):
    el = h.P['elbow' + side]
    fa = 0.18 * h.H
    held = h.flags.get('hold') in (side, 'LR')
    sp = pivot("skeins", (0, 0, -fa * 0.55), el, rot=(1.25 if held else 0.15, 0, 0))
    fdir = Vector((0, -0.95, -0.32))
    for k, c in enumerate(("#c43a5a", "#e8b030", "#3a9a5a")):
        m = mat(c, pat='spiral', color2=darker(c, 0.7), P=dict(nu=6, fv=160), var=0.25, bump=0.6)
        cen = fdir * (0.04 * (k - 1)) + Vector((0.0, 0, -0.03))
        tube("skein", ring_pts(cen, 0.06, 'xz', 14, 0.09), [0.024], m, sp, seg=8, sub=3)


def spool_basket(h):
    up, W = h.P['upper'], h.W
    N.basket(h, up, (0.0, -0.26 * min(1.0, h.H), -0.08), r=0.13, depth=0.11, contents=N.spools)


PROPS = dict(teapot=teapot, oil_can=oil_can, slate=slate, rope_coil=rope_coil, gear=gear, books=books, notebook=notebook,
             hay_fork=hay_fork, staff=staff, herb_basket=herb_basket, acorn_lamp=acorn_lamp, hand_bell=hand_bell, cake=cake,
             paper_boat=paper_boat, firefly_jar=firefly_jar, skeins=skeins, spool_basket=lambda h, **kw: spool_basket(h))


# ====================================================================== poses
def gesture_pose(side):
    def pf(h, anim, i, n):
        P = h.P
        ph = TAU * i / n
        sx = 1 if side == 'L' else -1
        P['arm' + side].rotation_euler = (-0.95 - 0.04 * math.sin(ph), 0, sx * 0.55)
        P['elbow' + side].rotation_euler = (-0.75 + 0.05 * math.sin(ph), 0, 0)
    return pf


def carry_pose(side):
    def pf(h, anim, i, n):
        P = h.P
        sx = 1 if side == 'L' else -1
        P['arm' + side].rotation_euler = (-0.35, 0, sx * 0.22)
        P['elbow' + side].rotation_euler = (-2.35, 0, 0)
    return pf


# ====================================================================== builder
def _skin(v):
    return SKIN[v] if len(v) == 1 else v


def build_npc(key):
    S = SPECS[key]
    sp = dict(S['sp'])
    sp['skin'] = _skin(sp['skin'])
    h = Human(sp)
    h.spec = S
    h.flags = dict(S['flags'])
    if 'legs' in S:
        h.legs(**S['legs'])
    else:
        h.feet_only(**S.get('feet', {}))
    if 'skirt' in S:
        h.skirt(**S['skirt'])
    if 'coat' in S:
        h.coat_skirt(**S['coat'])
    aprons = [S[k] for k in ('apron', 'apron2') if k in S]
    for a in aprons:
        if a.get('on') != 'upper':
            h.apron(**{k: v for k, v in a.items() if k != 'on'})
    h.torso(**S['torso'])
    for a in aprons:
        if a.get('on') == 'upper':
            h.apron(parent=h.P['upper'], **{k: v for k, v in a.items() if k != 'on'})
    h.arms(**S['arms'])
    for nm, kw in S.get('body_extras', []):
        BODY[nm](h, **kw)
    for nm, kw in S.get('props', []):
        PROPS[nm](h, **kw)
    h.head()
    if 'hair' in S:
        h.hair_cap(**S['hair'])
    for b in S.get('braids', []):
        h.braid(b['pts'], b['r'], S['hair']['color'], tie=b.get('tie'))
    if 'beard' in S:
        bd = dict(S['beard'])
        N.beard(h, bd.pop('color'), **bd)
    for nm, kw in S.get('head_wear', []):
        HEADWEAR[nm](h, **kw)
    for nm, kw in S.get('head_extras', []):
        HEAD_EXTRAS[nm](h, **kw)
    F = h.flags
    if F.get('gesture'):
        F['pose_fn'] = gesture_pose(F['gesture'])
    if F.get('carry'):
        F['pose_fn'] = carry_pose(F['carry'])
    if 'sprite_expr' in S:
        h.sprite_expr = S['sprite_expr']
    if 'hat_tilt' in S:
        h.sprite_hat_tilt = S['hat_tilt']
    return h


# ====================================================================== render (= v2_render.do_sprite, npc mode)
def render_npc(key, rawdir, quick=False):
    reset()
    STATE['truth'] = False
    STATE['line_t'] = 0.011
    render_setup(samples=32)
    world_and_lights('day')
    h = build_npc(key)
    h.name = key
    hat = h.P['hat'] if ('hat' in h.P and h.P['hat'].type == 'EMPTY') else None
    hat_x0 = hat.rotation_euler.x if hat else 0.0
    tilt = getattr(h, 'sprite_hat_tilt', -0.22)
    h.flags.setdefault('head_pitch', -0.16)
    add_lines()
    od = os.path.join(rawdir, 'npcs', key)
    os.makedirs(od, exist_ok=True)
    sprite_camera(128, 128, (64, 110), ssaa=4)
    bpy.context.scene.eevee.taa_render_samples = 24
    expr = getattr(h, 'sprite_expr', 'neutral')
    h.face.build(expr)
    open_objs = list(h.face.fp.objs)
    h.face.fp.objs = []
    h.face.build(expr, closed=True)
    closed_objs = list(h.face.fp.objs)
    count = 0
    for dname, deg in NPC_DIRS:
        for i in range(4):
            if quick and i != 0:
                continue
            pose(h, 'idle', i, 4)
            blink = i == 3
            for o in open_objs:
                o.hide_render = blink
            for o in closed_objs:
                o.hide_render = not blink
            h.P['root'].rotation_euler = (0, 0, math.radians(deg))
            if hat:
                hat.rotation_euler.x = hat_x0 + tilt * math.cos(math.radians(deg))
            bpy.context.view_layer.update()
            render_to(os.path.join(od, f"idle_{dname}_{i}.png"))
            count += 1
    return count


def main():
    a = args()
    which, rawdir = a[0], a[1]
    quick = len(a) > 2 and a[2] == 'quick'
    names = ORDER if which == 'all' else which.split(',')
    T = time.time()
    for nm in names:
        t0 = time.time()
        n = render_npc(nm, rawdir, quick)
        print(f"DONE npc {nm}: {n} frames {time.time() - t0:.1f}s", flush=True)
    print(f"ALL DONE {len(names)} npcs {time.time() - T:.1f}s", flush=True)


main()
