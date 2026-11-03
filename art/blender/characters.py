"""Model + render the three characters.

blender -b --python characters.py -- <apprentice_girl|apprentice_boy|dvora|all> <rawdir> [quick]

Writes raw (supersampled, un-outlined) frames:  <rawdir>/<char>/<anim>_<DIR>_<i>.png
art/pack.py then outlines, downsamples and packs them into sheets + Phaser JSON.
All characters are posed procedurally per frame (pivot empties), no stored actions.
Modesty: every human has hat/cap, long sleeves, long dress / long trousers, high neckline.
No weapons: the only held items are a glowing sewing needle and (Dvora) a ball of yarn.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from common import *

CELL = 128
FACE_Y = -1  # characters face -Y


# ------------------------------------------------------------ shared parts
def face(head, skin, y=-0.205, z=0.2, spread=0.082, eye=0.03, blush=True, brows=False, dark="#2a1a24"):
    dm = toon(dark, rim=0)
    for s in (-1, 1):
        e = ellipsoid("eye", eye, dm, head, loc=(s * spread, y, z), scale=(0.8, 0.55, 1.15), seg=10, rings=8)
        ellipsoid("eyehl", eye * 0.28, glow("#ffffff", 3), head, loc=(s * spread - 0.008, y - 0.012, z + 0.012), seg=6, rings=4)
        if blush:
            ellipsoid("cheek", 0.036, toon("#e98f86", rim=0), head, loc=(s * (spread + 0.045), y + 0.012, z - 0.05),
                      scale=(1, 0.35, 0.7), seg=8, rings=6)
        if brows:
            link_cyl("brow", (s * (spread + 0.03), y - 0.002, z + 0.065), (s * (spread - 0.03), y - 0.002, z + 0.075),
                     0.009, toon("#bdb4b8", rim=0), head, seg=5)
    ellipsoid("nose", 0.025, toon(skin, shade=(0.62, 0.5, 0.62), rim=0), head, loc=(0, y - 0.012, z - 0.05), scale=(1, 0.8, 0.9), seg=8, rings=6)
    link_cyl("mouth", (-0.03, y + 0.004, z - 0.098), (0.03, y + 0.004, z - 0.098), 0.007, toon("#9a4a4a", rim=0), head, seg=5)


def needle_rig(hand, glow_mats):
    """Glowing weaver's needle held in the hand pivot (hand origin = palm)."""
    n = pivot("needle", (0, -0.02, -0.03), hand, rot=(math.radians(12), 0, 0))
    link_cyl("shaft", (0, 0, -0.08), (0, 0, 0.34), 0.012, toon("#f6e6b8", rim=0.2), n, seg=6)
    ellipsoid("eye_of_needle", 0.018, glow("#35d3b0", 6), n, loc=(0, 0, -0.08), scale=(1, 0.5, 1.6), seg=8, rings=6)
    tip = ellipsoid("tip", 0.034, glow("#7fffe0", 8), n, loc=(0, 0, 0.35), seg=10, rings=8)
    halo_m = glow("#35d3b0", 3.0, alpha=0.9, soft=True)
    halo = ellipsoid("halo", 0.12, halo_m, n, loc=(0, 0, 0.35), seg=12, rings=8)
    ld = bpy.data.lights.new("needle_light", 'POINT')
    ld.color = srgb("#35d3b0")
    ld.energy = 12
    ld.shadow_soft_size = 0.1
    lo = bpy.data.objects.new("needle_light", ld)
    bpy.context.scene.collection.objects.link(lo)
    lo.parent = n
    lo.location = (0, -0.05, 0.34)
    glow_mats.append(halo)
    return n, ld


def satchel(body, strap_from, strap_to, side=1, leather="leather"):
    lm, ld = toon(leather), toon("leather_d")
    hip = (side * 0.27, 0.02, -0.14)
    box("bag", (0.2, 0.1, 0.17), lm, body, loc=hip, bevel=0.012)
    box("flap", (0.205, 0.108, 0.07), ld, body, loc=(hip[0], hip[1], hip[2] + 0.052), bevel=0.01)
    ellipsoid("buckle", 0.018, toon("gold", rim=0), body, loc=(hip[0], hip[1] - 0.056, hip[2] + 0.03), scale=(1, .5, 1), seg=8, rings=6)
    link_cyl("strap", strap_from, (hip[0] - 0.02 * side, hip[1], hip[2] + 0.085), 0.015, ld, body, seg=6)
    # strap on the back too
    link_cyl("strap_b", (strap_from[0], strap_from[1] + 0.03, strap_from[2]), (hip[0] - 0.02 * side, hip[1] + 0.05, hip[2] + 0.085), 0.013, ld, body, seg=6)


def hand(parent, skin, r=0.055):
    return ellipsoid("hand", r, toon(skin, rim=0.15), parent, loc=(0, 0, 0), seg=10, rings=8)


def arm(name, parent, shoulder, length, r_top, r_bot, sleeve, cuff, skin):
    p = pivot(name, shoulder, parent)
    frustum("sleeve", r_top, r_bot, -length, toon(sleeve), p, caps=(False, True), seg=10)
    frustum("cuff", r_bot * 1.12, r_bot * 1.12, -0.04, toon(cuff, rim=0), p, loc=(0, 0, -length + 0.03), caps=(False, False), seg=10)
    ellipsoid("shoulder", r_top * 1.05, toon(sleeve), p, seg=10, rings=8)
    h = pivot(name + "_hand", (0, 0, -length - 0.01), p)
    hand(h, skin)
    return p, h


# ------------------------------------------------------------ apprentice girl
def build_girl():
    skin = "skin_a"
    R = {}
    root = pivot("root")
    body = pivot("body", parent=root)
    R['root'], R['body'] = root, body
    # long dress
    sk = pivot("skirt", (0, 0, 0.7), body)
    frustum("dress", 0.17, 0.39, -0.64, toon("wine"), sk, caps=(False, False), seg=20)
    # hem trim + bottom band + apron
    frustum("hem", 0.395, 0.385, -0.05, toon("gold", rim=0.1), sk, loc=(0, 0, -0.58), caps=(False, False), seg=20)
    R['skirt'] = sk
    # shoes (peek out of hem when walking)
    R['shoeL'] = pivot("shoeL", (0.1, 0, 0.06), body)
    R['shoeR'] = pivot("shoeR", (-0.1, 0, 0.06), body)
    for p in (R['shoeL'], R['shoeR']):
        ellipsoid("shoe", 0.075, toon("leather_d"), p, scale=(0.9, 1.45, 0.65), seg=12, rings=8)
    # torso: blouse bodice
    up = pivot("upper", (0, 0, 0.66), body)
    R['upper'] = up
    frustum("bodice", 0.2, 0.165, 0.34, toon("wine"), up, seg=14)
    frustum("collar", 0.125, 0.115, 0.06, toon("cream"), up, loc=(0, 0, 0.32), seg=14)
    frustum("belt", 0.205, 0.205, 0.05, toon("gold", rim=0.1), up, loc=(0, 0, 0.0), caps=(False, False), seg=14)
    satchel(up, (-0.15, -0.02, 0.33), None, side=1)
    # arms
    R['armL'], hL = arm("armL", up, (0.205, 0, 0.3), 0.36, 0.07, 0.058, "cream", "gold", skin)
    R['armR'], hR = arm("armR", up, (-0.205, 0, 0.3), 0.36, 0.07, 0.058, "cream", "gold", skin)
    # head
    hd = pivot("head", (0, 0, 0.4), up)
    R['head'] = hd
    hd.scale = (1.1, 1.1, 1.1)
    ellipsoid("skull", 0.235, toon(skin, rim=0.3), hd, loc=(0, 0, 0.2), scale=(1, 0.96, 0.98))
    ellipsoid("hair", 0.245, toon("brown_hair"), hd, loc=(0, 0.045, 0.215), scale=(1.0, 0.98, 0.96))
    ellipsoid("fringe", 0.2, toon("brown_hair"), hd, loc=(0, -0.085, 0.305), scale=(1.05, 0.6, 0.55))
    face(hd, skin)
    # braid (hangs down the back)
    for i, (z, r) in enumerate([(0.05, 0.065), (-0.04, 0.06), (-0.12, 0.055), (-0.2, 0.048)]):
        ellipsoid("braid", r, toon("brown_hair"), hd, loc=(0, 0.2 + i * 0.012, z), seg=10, rings=8)
    ellipsoid("bow", 0.035, toon("gold", rim=0), hd, loc=(0, 0.23, -0.25), scale=(1.4, .7, .9), seg=8, rings=6)
    # soft pointed apprentice hat with gold band
    hat = pivot("hat", (0, 0.015, 0.35), hd, rot=(math.radians(-16), 0, 0))
    frustum("brim", 0.33, 0.22, 0.045, toon("indigo"), hat, loc=(0, 0, -0.01), seg=24)
    frustum("crown", 0.21, 0.12, 0.18, toon("indigo"), hat, loc=(0, 0, 0.03), seg=20)
    frustum("tipcone", 0.12, 0.02, 0.16, toon("indigo"), hat, loc=(0, 0.0, 0.2), rot=(math.radians(-14), 0, 0), seg=14)
    ellipsoid("tipball", 0.032, toon("gold", rim=0), hat, loc=(0, -0.05, 0.35), seg=8, rings=6)
    frustum("band", 0.212, 0.2, 0.06, toon("gold", rim=0.1), hat, loc=(0, 0, 0.05), caps=(False, False), seg=20)
    # needle in right hand (-X side), arm held forward
    gm = []
    R['needle'], R['needle_light'] = needle_rig(hR, gm)
    R['glow_mats'] = gm
    R['hands'] = (hL, hR)
    R['kind'] = 'dress'
    R['stride'] = 1.0
    R['hold_R'] = True
    return R


# ------------------------------------------------------------ apprentice boy
def build_boy():
    skin = "skin_b"
    R = {}
    root = pivot("root")
    body = pivot("body", parent=root)
    R['root'], R['body'] = root, body
    # legs: long trousers
    for nm, sx in (("legL", 1), ("legR", -1)):
        p = pivot(nm, (sx * 0.1, 0, 0.62), body)
        frustum("trouser", 0.088, 0.075, -0.5, toon("#5b4a6a"), p, caps=(False, True), seg=10)
        frustum("cuff", 0.083, 0.083, -0.05, toon("#3f3350", rim=0), p, loc=(0, 0, -0.5), caps=(False, False), seg=10)
        ellipsoid("boot", 0.085, toon("leather_d"), p, loc=(0, -0.045, -0.555), scale=(0.9, 1.4, 0.7), seg=12, rings=8)
        ellipsoid("knee", 0.09, toon("#5b4a6a"), p, seg=10, rings=8)
        R[nm] = p
    up = pivot("upper", (0, 0, 0.6), body)
    R['upper'] = up
    # tunic reaching mid-thigh, long
    frustum("tunic_skirt", 0.19, 0.225, -0.22, toon("forest"), up, caps=(False, False), seg=16)
    frustum("tunic", 0.19, 0.17, 0.4, toon("forest"), up, seg=16)
    frustum("collar", 0.125, 0.115, 0.07, toon("cream"), up, loc=(0, 0, 0.37), seg=14)
    frustum("belt", 0.197, 0.197, 0.055, toon("gold", rim=0.1), up, loc=(0, 0, 0.02), caps=(False, False), seg=16)
    box("buckle", (0.06, 0.02, 0.06), toon("gold", rim=0), up, loc=(0, -0.2, 0.05))
    satchel(up, (-0.15, -0.02, 0.36), None, side=1)
    R['armL'], hL = arm("armL", up, (0.21, 0, 0.34), 0.38, 0.075, 0.062, "forest", "gold", skin)
    R['armR'], hR = arm("armR", up, (-0.21, 0, 0.34), 0.38, 0.075, 0.062, "forest", "gold", skin)
    hd = pivot("head", (0, 0, 0.43), up)
    R['head'] = hd
    hd.scale = (1.1, 1.1, 1.1)
    ellipsoid("skull", 0.235, toon(skin, rim=0.3), hd, loc=(0, 0, 0.2), scale=(1, 0.96, 0.98))
    ellipsoid("hair", 0.245, toon("dark_hair"), hd, loc=(0, 0.04, 0.215), scale=(1.0, 0.98, 0.96))
    ellipsoid("fringe", 0.2, toon("dark_hair"), hd, loc=(0, -0.09, 0.3), scale=(1.05, 0.6, 0.5))
    face(hd, skin, dark="#241818")
    # flat cap
    cap = pivot("cap", (0, 0.01, 0.33), hd, rot=(math.radians(-10), 0, 0))
    ellipsoid("capdome", 0.265, toon("ochre"), cap, loc=(0, 0, 0.02), scale=(1, 1.02, 0.62))
    frustum("capband", 0.255, 0.255, 0.05, toon("#a8702c"), cap, loc=(0, 0, -0.04), caps=(False, False), seg=20)
    frustum("visor", 0.14, 0.12, 0.025, toon("#a8702c"), cap, loc=(0, -0.2, -0.015), rot=(0, 0, 0), seg=14, scale=(1.1, 1.0, 1))
    ellipsoid("button", 0.03, toon("gold", rim=0), cap, loc=(0, 0, 0.17), seg=8, rings=6)
    gm = []
    R['needle'], R['needle_light'] = needle_rig(hR, gm)
    R['glow_mats'] = gm
    R['kind'] = 'legs'
    R['stride'] = 1.0
    return R


# ------------------------------------------------------------ Dvora
def build_dvora():
    skin = "skin_c"
    R = {}
    root = pivot("root")
    body = pivot("body", parent=root)
    R['root'], R['body'] = root, body
    sk = pivot("skirt", (0, 0, 0.62), body)
    frustum("dress", 0.17, 0.37, -0.57, toon("plum"), sk, caps=(False, False), seg=20)
    frustum("hem", 0.375, 0.365, -0.07, toon("#c98a4a", rim=0.1), sk, loc=(0, 0, -0.52), caps=(False, False), seg=20)
    frustum("hem2", 0.372, 0.362, -0.025, toon("#f0d9a0", rim=0.1), sk, loc=(0, 0, -0.43), caps=(False, False), seg=20)
    R['skirt'] = sk
    R['shoeL'] = pivot("shoeL", (0.09, 0, 0.05), body)
    R['shoeR'] = pivot("shoeR", (-0.09, 0, 0.05), body)
    for p in (R['shoeL'], R['shoeR']):
        ellipsoid("shoe", 0.07, toon("leather_d"), p, scale=(0.9, 1.4, 0.65), seg=12, rings=8)
    up = pivot("upper", (0, 0, 0.58), body, rot=(math.radians(8), 0, 0))   # slight stoop
    R['upper'] = up
    frustum("bodice", 0.2, 0.17, 0.32, toon("plum"), up, seg=14)
    frustum("collar", 0.13, 0.12, 0.05, toon("cream"), up, loc=(0, 0, 0.3), seg=14)
    # shawl: draped shoulders with fringe
    frustum("shawl", 0.27, 0.175, 0.3, toon("ochre"), up, loc=(0, 0.01, 0.07), caps=(False, False), seg=20)
    frustum("shawl_top", 0.2, 0.15, 0.04, toon("ochre"), up, loc=(0, 0.0, 0.34), caps=(False, True), seg=16)
    frustum("fringe", 0.277, 0.267, 0.06, toon("#f0d9a0", rim=0.1), up, loc=(0, 0.01, 0.03), caps=(False, False), seg=24)
    frustum("shawl_stripe", 0.24, 0.23, 0.025, toon("#8a3f55", rim=0), up, loc=(0, 0.01, 0.13), caps=(False, False), seg=24)
    ellipsoid("brooch", 0.03, toon("gold", rim=0), up, loc=(0, -0.2, 0.28), seg=8, rings=6)
    R['armL'], hL = arm("armL", up, (0.215, 0, 0.27), 0.33, 0.07, 0.056, "plum", "cream", skin)
    R['armR'], hR = arm("armR", up, (-0.215, 0, 0.27), 0.33, 0.07, 0.056, "plum", "cream", skin)
    # yarn ball in left hand
    ellipsoid("yarn", 0.085, toon("teal", rim=0.2), hL, loc=(0.02, -0.06, 0.0), seg=12, rings=8)
    ellipsoid("yarn2", 0.088, toon("#23a08a", rim=0), hL, loc=(0.02, -0.06, 0.0), scale=(1, 1, .25), seg=12, rings=8)
    hd = pivot("head", (0, -0.01, 0.38), up, rot=(math.radians(-6), 0, 0))
    R['head'] = hd
    hd.scale = (1.12, 1.12, 1.12)
    ellipsoid("skull", 0.225, toon(skin, rim=0.3), hd, loc=(0, 0, 0.2), scale=(1, 0.96, 0.98))
    ellipsoid("hair", 0.232, toon("gray_hair"), hd, loc=(0, 0.05, 0.22), scale=(1.0, 0.98, 0.95))
    ellipsoid("fringe", 0.2, toon("gray_hair"), hd, loc=(0, -0.08, 0.29), scale=(1.05, 0.6, 0.45))
    ellipsoid("bun", 0.1, toon("gray_hair"), hd, loc=(0, 0.22, 0.12), seg=12, rings=8)
    face(hd, skin, brows=True, blush=True, dark="#2a1a24")
    # little round glasses (gold) for character
    for s in (-1, 1):
        frustum("lens", 0.052, 0.052, 0.008, toon("gold", rim=0), hd, loc=(s * 0.082, -0.206, 0.2), rot=(math.radians(90), 0, 0), caps=(False, False), seg=14)
    link_cyl("bridge", (-0.03, -0.208, 0.205), (0.03, -0.208, 0.205), 0.006, toon("gold", rim=0), hd, seg=5)
    # wide brim straw hat with violet ribbon and flower
    hat = pivot("hat", (0, 0.02, 0.33), hd, rot=(math.radians(-20), 0, 0))
    frustum("brim", 0.4, 0.24, 0.05, toon("straw"), hat, loc=(0, 0, -0.03), seg=28)
    frustum("brim_edge", 0.4, 0.4, 0.012, toon("#b98a3c"), hat, loc=(0, 0, -0.03), caps=(False, False), seg=28)
    frustum("crown", 0.24, 0.17, 0.2, toon("straw"), hat, loc=(0, 0, 0.02), seg=20)
    ellipsoid("crowntop", 0.17, toon("straw"), hat, loc=(0, 0, 0.215), scale=(1, 1, 0.3), seg=16, rings=8)
    frustum("ribbon", 0.243, 0.225, 0.07, toon("#7a4a8a", rim=0), hat, loc=(0, 0, 0.04), caps=(False, False), seg=20)
    for i, a in enumerate((20, 60, 100)):
        ellipsoid("flower", 0.03, toon(["red", "gold", "white"][i], rim=0), hat,
                  loc=(math.cos(math.radians(a - 150)) * 0.24, math.sin(math.radians(a - 150)) * 0.24, 0.08), seg=8, rings=6)
    R['glow_mats'] = []
    R['kind'] = 'dress'
    R['stride'] = 0.62
    R['elder'] = True
    R['needle_light'] = None
    return R


# ------------------------------------------------------------ posing
def pose(R, anim, i, n):
    """Set pivot rotations/locations for frame i of n. All angles radians."""
    ph = 2 * math.pi * i / n
    S = R['stride']
    body, up, head = R['body'], R['upper'], R['head']
    for k in ('armL', 'armR'):
        R[k].rotation_euler = (0, 0, 0)
    R['body'].location = (0, 0, 0)
    R['body'].scale = (1, 1, 1)
    hold = R.get('hold_R', False) or R.get('needle') is not None
    stoop = 0.14 if R.get('elder') else 0.0
    if anim == 'idle':
        breathe = math.sin(ph)
        body.scale = (1, 1, 1 + 0.012 * breathe)
        R['head'].rotation_euler = (R['head_rest'][0] + 0.03 * math.sin(ph + 0.8), 0.02 * math.sin(ph), 0)
        R['armL'].rotation_euler = (0.04 * breathe + (0 if not R.get('elder') else -0.7), 0.0, 0.05)
        R['armR'].rotation_euler = ((-0.55 if R.get('needle') else 0.0) + 0.03 * breathe, 0.0, -0.05)
        if 'skirt' in R:
            R['skirt'].rotation_euler = (0.015 * math.sin(ph), 0.01 * math.sin(ph + 1), 0)
        for k in ('shoeL', 'shoeR', 'legL', 'legR'):
            if k in R:
                R[k].rotation_euler = (0, 0, 0)
                if k.startswith('shoe'):
                    R[k].location = (R[k].location[0], 0, R[k].location[2])
        up.rotation_euler = (0.14 if R.get('elder') else 0.0, 0, 0)
    else:
        s, c = math.sin(ph), math.cos(ph)
        bob = abs(s) * 0.035 * (0.7 if R.get('elder') else 1)
        body.location = (0, 0, bob)
        body.rotation_euler = (0, 0, 0.05 * s * S)
        R['head'].rotation_euler = (R['head_rest'][0], 0.03 * c, 0.04 * -s)
        up.rotation_euler = ((0.14 if R.get('elder') else 0.05), 0.03 * c, 0.0)
        R['armL'].rotation_euler = ((-0.75 * s if not R.get('elder') else -0.7 - 0.2 * s) * S, 0, 0.05)
        R['armR'].rotation_euler = (((-0.55 + 0.14 * s) if R.get('needle') else 0.75 * s * S), 0, -0.05)
        if R['kind'] == 'legs':
            R['legL'].rotation_euler = (0.78 * s * S, 0, 0)
            R['legR'].rotation_euler = (-0.78 * s * S, 0, 0)
        else:
            R['skirt'].rotation_euler = (0.03 * s * 0, 0.06 * s * S, 0.0)
            for k, sign in (('shoeL', 1), ('shoeR', -1)):
                y = -0.2 * sign * s * S - 0.0
                lift = max(0.0, sign * c) * 0.05 * S
                R[k].location = (R[k].location[0], y - 0.12 * S, 0.06 + lift)
                R[k].rotation_euler = (0.0, 0, 0)
    if R.get('needle_light') is not None:
        pulse = 1.0 + 0.25 * math.sin(ph if anim == 'idle' else ph * 2)
        R['needle_light'].energy = 12 * pulse
        for m in R['glow_mats']:
            for nd in m.active_material.node_tree.nodes:
                if nd.type == 'MIX_SHADER':
                    pass


# ------------------------------------------------------------ main
def main():
    a = script_args()
    which, rawdir = a[0], a[1]
    quick = len(a) > 2 and a[2] == 'quick'
    builders = dict(apprentice_girl=build_girl, apprentice_boy=build_boy, dvora=build_dvora)
    names = list(builders) if which == 'all' else [which]
    import time
    for nm in names:
        t0 = time.time()
        reset_scene()
        setup_render(samples=16)
        setup_world_and_lights()
        setup_camera(CELL, CELL, anchor=(CELL / 2, 110))
        R = builders[nm]()
        R['head_rest'] = tuple(R['head'].rotation_euler)
        os.makedirs(os.path.join(rawdir, nm), exist_ok=True)
        count = 0
        for anim, n in (('idle', 4), ('walk', 8)):
            for dname, deg in DIRECTIONS:
                if quick and dname not in ('S', 'E', 'NW'):
                    continue
                for i in range(n):
                    if quick and i not in (0, 2):
                        continue
                    pose(R, anim, i, n)
                    R['root'].rotation_euler = (0, 0, math.radians(deg))
                    bpy.context.view_layer.update()
                    render_to(os.path.join(rawdir, nm, f"{anim}_{dname}_{i}.png"))
                    count += 1
        print(f"CHAR {nm}: {count} frames in {time.time() - t0:.1f}s")


main()
