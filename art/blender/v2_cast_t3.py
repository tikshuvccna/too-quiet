"""Tranche 3 villagers (NPC sheets only). Registered into v2_cast_npc.CAST on import."""
import math

from mathutils import Vector

from v2lib import *
from v2_parts import Human
from v2_cast import SKIN
import v2_cast_npc as N
from v2_cast_npc import beard, soft_cap, CREAM


def watering_can(hand):
    m = mat("#6a8a9a", metal=True)
    wp = pivot("can", (0.0, -0.06, -0.12), hand)
    cyl("canb", 0.07, 0.065, 0.12, m, wp, loc=(0, 0, -0.06))
    tube("spout", [Vector((0, -0.06, -0.02)), Vector((0, -0.14, 0.04)), Vector((0, -0.2, 0.08))], [0.014, 0.012, 0.02], m, wp, seg=8, sub=2)
    tube("canh", [Vector((0, 0.05, 0.05)), Vector((0, 0.0, 0.1)), Vector((0, -0.05, 0.05))], [0.009], m, wp, seg=6, sub=3)


def books(hand):
    bp = pivot("books", (0.0, -0.08, 0.02), hand, rot=(0.2, 0, 0.1))
    for k, c in enumerate(("#a94a3a", "#2f5a7a", "#e8b04a")):
        box("book", (0.16 - 0.01 * k, 0.05, 0.05), mat(c, pat='leather', var=0.2), bp, loc=(0.005 * k, 0, 0.052 * k), bevel=0.008)


def lamp_pole(hand):
    m = mat("#6b4326", pat='wood', var=0.2)
    lp = pivot("pole", (0, -0.02, -0.03), hand)
    tube("polep", [Vector((0, 0, -0.5)), Vector((0, 0, 0.5)), Vector((0, -0.03, 1.0))], [0.014], m, lp, seg=8, sub=2)
    ellipsoid("flame", 0.035, glow("#ffc66a", 4), lp, loc=(0, -0.04, 1.04), scale=(0.8, 0.8, 1.4), seg=10, rings=8)
    cyl("cup", 0.03, 0.04, 0.04, mat("#c9a040", metal=True), lp, loc=(0, -0.03, 0.98))


def clay_pot(hand):
    m = mat("#c0683a", pat='noise', P=dict(scale=20), var=0.15)
    pp = pivot("pot", (0.0, -0.1, -0.02), hand)
    loft("potb", [(0, 0.05, 0.05), (0.06, 0.1, 0.1), (0.14, 0.08, 0.08), (0.18, 0.05, 0.05), (0.2, 0.06, 0.06)], m, pp, seg=28,
         cap_bot=True)
    loft("stripe", [(0.07, 0.102, 0.102), (0.09, 0.101, 0.101)], mat("#f3e4c4", kind='soft'), pp, seg=28, line=False)


def cane(hand):
    m = mat("#6b4326", pat='wood', var=0.2)
    cp = pivot("cane", (0, -0.02, -0.03), hand)
    tube("canep", [Vector((0, 0, -0.62)), Vector((0, 0, 0.02)), Vector((0, -0.04, 0.07)), Vector((0, -0.09, 0.04))], [0.016], m, cp,
         seg=8, sub=3)


def messenger():
    sp = dict(skin=SKIN['b'], R=0.24, iris="#3a2a1a", brow_col="#2a1a10", lip="#9a4a40", blush_amt=0.4, H=1.0, W=0.92,
              head=dict(jaw=0.32, nose=0.09, chin=0.06), eye_h=0.14, flick=0.3)
    h = Human(sp)
    h.legs("#2f4a6a", shoe="#3a2418", boots=True)
    h.coat_skirt("#c44b3f", length=0.22, flare=0.6)
    h.torso("#c44b3f", collar=CREAM, belt="#5e3a22", buttons=("#e8b04a", 3))
    h.arms("#c44b3f", cuff="#e8b04a")
    bag = h.satchel(color="#8a5a36", side=1, z=0.05)
    bag.scale = (1.5, 1.5, 1.5)
    for k in range(3):
        box("letter", (0.012, 0.1, 0.07), mat("#fff4d6", kind='soft'), bag, loc=(0.0, -0.05 + 0.04 * k, 0.1), rot=(0, 0, 0.2 * k))
    h.head()
    h.hair_cap("#2a1a10", hairline=0.45, sides=-0.2, fringe=(5, 0.2))
    h.flat_cap("#2f4a6a", color2="#e8b04a", tilt=-0.08, z=0.46, pat='plaid')
    h.flags = dict(kind='legs', stride=1.1)
    return h


def gardener():
    sp = dict(skin=SKIN['e'], R=0.245, iris="#4a6a3a", brow_col="#6a4a3a", lip="#b0605a", blush_amt=0.55, H=0.95, W=1.12,
              head=dict(jaw=0.26, cheek=0.08, nose=0.09), eye_h=0.13, flick=0.5)
    h = Human(sp)
    h.feet_only(shoe="#4a3a20")
    h.skirt("#8a6a9a", pat='flowers', color2="#f3e4c4", P=dict(nu=24, fv=30, rad=0.25), hem="#4f9a4f", flare=1.0)
    h.apron("#6cb257", pat='weave', length=0.4, width=0.75, pocket="#4f9a4f")
    h.torso("#f3e4c4", collar="#8a6a9a")
    h.arms("#f3e4c4", cuff="#8a6a9a")
    watering_can(h.P['handR'])
    h.head()
    h.headscarf("#4f9a4f", color2="#e8b04a", pat='dots', P=dict(nu=20, fv=28, rad=0.14), z_front=0.5)
    h.wide_hat("#e1b865", "#4f9a4f", crown_h=0.45, brim=1.75, tilt=-0.1, bow=False, z=0.62, flower=["#f6f0e6", "#c88ad8"])
    h.flags = dict(kind='dress', stride=0.9, hold='R')
    return h


def teacher():
    sp = dict(skin=SKIN['a'], R=0.24, iris="#3a4a6a", brow_col="#3a2418", lip="#a05058", blush_amt=0.35, H=1.08, W=0.9,
              head=dict(jaw=0.34, nose=0.1, chin=0.05), eye_h=0.13, flick=0.7)
    h = Human(sp)
    h.feet_only(shoe="#2a1a14")
    h.skirt("#2f4a6a", pat='plaid', color2="#3e5a7a", P=dict(nu=20, fv=16, thr=0.82), hem="#2a3a52", flare=0.8, folds=14)
    h.torso("#e8dcc4", pat='vstripes', color2="#d0c0a0", P=dict(nu=30, fv=60, thr=0.85), collar="#2f4a6a")
    h.arms("#e8dcc4", cuff="#2f4a6a")
    books(h.P['handL'])
    h.head()
    h.headscarf("#a94a62", color2="#e8b04a", pat='vstripes', P=dict(nu=30, fv=30, thr=0.85), z_front=0.52)
    h.flags = dict(kind='dress', stride=0.85, hold='L')
    return h


def lamplighter():
    sp = dict(skin=SKIN['f'], R=0.24, iris="#2a1a10", brow_col="#d8d0c8", lip="#8a4040", blush_amt=0.3, H=1.06, W=0.9,
              head=dict(jaw=0.34, nose=0.13, chin=0.05, tall=1.05), eye_h=0.11, wrinkles=True, lash_w=0.04, flick=0.1)
    h = Human(sp)
    h.legs("#3a3040", shoe="#1a1418", boots=True)
    h.coat_skirt("#3e3466", length=0.4, flare=0.6)
    h.torso("#3e3466", collar="#e8dcc4", buttons=("#e8b04a", 4))
    h.arms("#3e3466", cuff="#2a2448")
    lamp_pole(h.P['handR'])
    h.head()
    beard(h, "#e8e2dc", length=0.3, width=0.7, mustache=True, mk=0.8)
    h.wide_hat("#2a2448", "#e8b04a", crown_h=0.95, brim=1.4, tilt=-0.06, pat='leather', P=dict(scale=18), bow=False, droop=0.02,
               z=0.55, crown_r=1.0)
    h.flags = dict(kind='legs', stride=0.8, hold='R')
    return h


def potter():
    sp = dict(skin=SKIN['d'], R=0.25, iris="#3a2a1a", brow_col="#2a1a10", lip="#9a4a40", blush_amt=0.45, H=0.96, W=1.2,
              head=dict(jaw=0.24, cheek=0.08, nose=0.12), eye_h=0.12, flick=0.2)
    h = Human(sp)
    h.legs("#6a5a48", shoe="#3a2418")
    h.torso("#d8c8a8", collar="#f3e4c4", belly=0.04)
    h.apron("#a8704a", pat='flour', color2="#d8a080", P=dict(scale=5, thr=0.6), parent=h.P['upper'], top_z=0.05, length=0.42,
            width=0.9, bib=True)
    h.arms("#d8c8a8", cuff="#a8704a")
    clay_pot(h.P['handL'])
    h.head()
    h.hair_cap("#1a1010", hairline=0.5, sides=-0.15, fringe=(4, 0.12))
    soft_cap(h, "#a8704a", z=0.55, puff=1.15, tilt=-0.1, side=-0.1)
    h.flags = dict(kind='legs', stride=0.8, hold='L')
    return h


def elder_cane():
    sp = dict(skin=SKIN['g'], R=0.235, iris="#5a6a7a", brow_col="#e0dcd8", lip="#a06060", blush_amt=0.4, H=1.02, W=0.88,
              head=dict(jaw=0.36, nose=0.13, chin=0.05, tall=1.05), eye_h=0.11, wrinkles=True, lash_w=0.04, flick=0.2)
    h = Human(sp)
    h.feet_only(shoe="#2a1a14")
    h.skirt("#4a4a5a", pat='weave', hem="#a94a62", hem2="#e8b04a", flare=0.8, folds=12)
    h.torso("#4a4a5a", collar=CREAM)
    up = h.P['upper']
    th = h.torso_h
    sm = mat("#a94a62", pat='knit', color2="#e8b04a", P=dict(nu=40, fv=55, stripe=10), var=0.2, bump=0.5)
    loft("shawl", [(th * 1.02, 0.1, 0.09), (th * 0.92, 0.22, 0.18), (th * 0.55, 0.24, 0.2)], sm, up, seg=48,
         folds=lambda a, t: 1 + 0.04 * t * math.sin(6 * a))
    h.arms("#4a4a5a", cuff=CREAM)
    cane(h.P['handR'])
    h.head()
    h.headscarf("#3e3466", color2="#c9b48a", pat='flowers', P=dict(nu=20, fv=26, rad=0.28), z_front=0.52)
    h.flags = dict(kind='dress', stride=0.55, elder=True, stoop=0.2, hold='R')
    return h


CAST = dict(messenger=messenger, gardener=gardener, teacher=teacher, lamplighter=lamplighter, potter=potter,
            elder_cane=elder_cane)
