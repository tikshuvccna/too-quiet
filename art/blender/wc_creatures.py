"""World creatures (wc_): 12 small + 2 legendary, from content/he/world/creatures_world.json.

blender -b --python wc_creatures.py -- <name[,name]|all|small|legend> <ABSOLUTE rawdir>
Same rig, camera, frame naming and layout as v2_creatures.py (reuses its helpers):
<rawdir>/creatures/wc_<key>/<anim>_<DIR>_<i>.png (SSAA 4), wc_<key>_codex.png, meta.json.
Rules: cute, readable, non-violent, no readable text (numbers are drawn as pips and tablets).
"""
import json
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector

from v2lib import *
from v2_parts import darker, lighter
from v2_creatures import C, eye, closed_eye, smile, blush, leg4, walk4, build, codex, CPPU, CDIRS


# ---------------------------------------------------------------- helpers
def V(*a):
    return Vector(a)


def npivot(name, loc, parent, normal):
    p = pivot(name, loc, parent)
    p.rotation_mode = 'QUATERNION'
    p.rotation_quaternion = Vector(normal).normalized().to_track_quat('Z', 'Y')
    return p


def ring_pts(c, rx, ry, n=28, axis_b=(0, 1, 0)):
    """Closed loop around centre c: cos*x + sin*axis_b."""
    bx = Vector(axis_b)
    return [Vector(c) + Vector((rx * math.cos(TAU * k / n), 0, 0)) + bx * (ry * math.sin(TAU * k / n)) for k in range(n + 1)]


def star4(name, parent, loc, r, m):
    v = [(0, -0.01, 0), (0, 0.01, 0)]
    out = []
    for k in range(8):
        a = TAU * k / 8
        rr = r if k % 2 == 0 else r * 0.32
        out.append((rr * math.cos(a), 0, rr * math.sin(a)))
    v += out
    f = []
    for k in range(8):
        f.append((0, 2 + k, 2 + (k + 1) % 8))
        f.append((1, 2 + (k + 1) % 8, 2 + k))
    return mesh_obj(name, v, f, m, parent, loc=loc, smooth=False, line=False)


def set_hide(objs, hidden):
    for o in objs:
        o.hide_render = hidden
        for ch in o.children_recursive:
            ch.hide_render = hidden


# ================================================================ 1 address turtle (IP address)
def address_turtle():
    c = C("wc_address_turtle")
    b = pivot("b", parent=c.body)
    skin = mat("#9ccc6a", pat='skin', kind='skin', var=0.06, rim=0.6)
    shellm = mat("#3f8a5a", pat='patches', color2="#2e6a48", P=dict(scale=9, thr=0.5, sharp=5), var=0.2, bump=0.5, rim=0.7)
    scute = mat("#6cb878", pat='noise', P=dict(scale=40), var=0.15, rim=0.7)
    cream = mat("#f0e2b0", kind='soft', rim=0.5)
    gold = mat("#f2c24e", metal=True, rim=0.9)
    bz = 0.12
    SC = V(0, 0.03, bz + 0.08)
    RX, RY, RZ = 0.25, 0.28, 0.2
    shell = pivot("shell", parent=b)
    blob("dome", 1.0, shellm, shell, loc=SC, scale=(RX, RY, RZ), deform=lambda p: Vector((p.x, p.y, max(p.z, -0.2))),
         seg=40, rings=26)
    tube("rim", ring_pts((SC.x, SC.y, SC.z - 0.04), RX * 0.99, RY * 0.99, n=32), [0.034], cream, shell, seg=10, sub=1)

    def surf(d):
        d = d.normalized()
        pos = SC + Vector((d.x * RX, d.y * RY, d.z * RZ))
        nrm = Vector((d.x / RX, d.y / RY, d.z / RZ))
        return pos, nrm
    # scutes (skip the front, where the address sits)
    for k in range(6):
        az = math.radians(30 + 60 * k)
        if abs(math.degrees(az) - 270) < 40:
            continue
        el = math.radians(30)
        pos, nrm = surf(V(math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
        p = npivot("sc", pos, shell, nrm)
        ellipsoid("scute", 0.075, scute, p, scale=(1, 1, 0.22), seg=16, rings=8)
    pos, nrm = surf(V(0, 0.45, 0.9))
    p = npivot("sc", pos, shell, nrm)
    ellipsoid("scute", 0.085, scute, p, scale=(1, 1, 0.2), seg=16, rings=8)
    # the address: four gold tablets with three glowing dots between them (no digits)
    dotm = glow("#fff0a0", 2.6)
    us = [-0.42, -0.14, 0.14, 0.42]
    for j, u in enumerate(us):
        pos, nrm = surf(V(u, -0.62, 0.78))
        p = npivot("tab", pos + nrm.normalized() * 0.008, shell, nrm)
        box("tablet", (0.058, 0.04, 0.016), gold, p, bevel=0.006)
        box("groove", (0.034, 0.008, 0.004), mat("#a87a2a", kind='flat', line=False), p, loc=(0, 0.0, 0.009))
        if j < 3:
            pos2, nrm2 = surf(V((u + us[j + 1]) / 2, -0.66, 0.74))
            ellipsoid("dot", 0.011, dotm, shell, loc=pos2 + nrm2.normalized() * 0.01, seg=8, rings=6)
    # head
    hd = pivot("h", (0, -0.27, bz + 0.07), b)
    tube("neck", [V(0, 0.13, -0.04), V(0, 0.06, -0.01), V(0, 0.0, 0.02)], [0.055, 0.05], skin, hd, seg=12, sub=2)
    blob("head", 0.095, skin, hd, loc=(0, -0.02, 0.05), scale=(1.0, 1.1, 0.92), seg=24, rings=16)
    for s in (-1, 1):
        eye(hd, (s * 0.046, -0.088, 0.08), 0.032, iris="#3a2a1a", rot=(0, 0, -s * 0.35))
        blush(hd, (s * 0.062, -0.1, 0.025), 0.016)
    smile(hd, (0, -0.12, 0.03), 0.024)
    L = leg4(b, bz, dict(FL=(0.16, -0.13), FR=(-0.16, -0.13), BL=(0.16, 0.18), BR=(-0.16, 0.18)), 0.05, skin)
    tube("tail", [V(0, 0.3, bz), V(0, 0.36, bz - 0.03), V(0, 0.4, bz - 0.05)], [0.03, 0.02, 0.006], skin, b, seg=8, sub=2)

    def pose(anim, i, n):
        ph = TAU * i / n
        if anim == 'walk':
            walk4(L, ph, 0.45)
            b.location.z = 0.012 * abs(math.cos(ph))
            b.rotation_euler = (0, 0.04 * math.sin(ph), 0)
            hd.location.y = -0.27 - 0.02 * math.sin(ph)
            hd.rotation_euler = (0, 0, 0)
        else:
            walk4(L, 0, 0)
            b.location.z = 0
            b.rotation_euler = (0, 0, 0)
            hd.location.y = -0.27 - 0.015 * math.sin(ph)
            hd.rotation_euler = (0, 0, 0.15 * math.sin(ph))
        shell.scale = (1, 1, 1 + 0.015 * math.sin(ph))
    c.pose = pose
    c.meta = dict(move="walks")
    return c


# ================================================================ 2 bit rabbit (bit: two states)
def bit_rabbit():
    c = C("wc_bit_rabbit")
    b = pivot("b", parent=c.body)
    fur = mat("#f7f3ee", pat='fur', P=dict(scale=80), kind='soft', var=0.12, rim=0.6)
    pink = mat("#f4a8b8", kind='soft', rim=0.3)
    blob("rbody", 0.15, fur, b, loc=(0, 0.06, 0.16), scale=(0.95, 1.1, 1.0), seg=28, rings=18)
    blob("rchest", 0.1, fur, b, loc=(0, -0.05, 0.21), scale=(0.9, 0.8, 1.0), seg=20, rings=14)
    hd = pivot("h", (0, -0.08, 0.37), b)
    blob("rhead", 0.12, fur, hd, scale=(1.05, 0.95, 0.9), seg=26, rings=18)
    blob("muzzle", 0.05, fur, hd, loc=(0, -0.095, -0.04), scale=(1.2, 0.7, 0.8), seg=16, rings=10)
    ellipsoid("rnose", 0.016, pink, hd, loc=(0, -0.135, -0.015), scale=(1.3, 0.6, 0.9), seg=8, rings=6)
    for s in (-1, 1):
        eye(hd, (s * 0.058, -0.085, 0.02), 0.036, iris="#4a3a5a", rot=(0, 0, -s * 0.4))
        blush(hd, (s * 0.075, -0.095, -0.035), 0.02)
    on = glow("#7ffff0", 3.0)
    halo = glow("#9ffff4", 1.3, alpha=0.16, soft=True)
    off = mat("#69708a", kind='soft', rim=0.3)
    E = {}
    for s in (-1, 1):
        ep = pivot("ear", (s * 0.045, 0.01, 0.08), hd)
        blob("rear", 0.05, fur, ep, loc=(0, 0, 0.12), scale=(0.62, 0.32, 2.4), seg=16, rings=12)
        ellipsoid("rearin", 0.034, pink, ep, loc=(0, -0.013, 0.11), scale=(0.5, 0.2, 2.5), seg=12, rings=8)
        lit = [ellipsoid("tipon", 0.04, on, ep, loc=(0, 0, 0.2), scale=(0.85, 0.55, 1.4), seg=12, rings=8)]
        for k in range(3):
            a = math.radians(60 + 30 * k)
            lit.append(tube("ray", [V(0.05 * math.cos(a) * (1 if k != 1 else 0), 0, 0.25 + 0.05 * math.sin(a)),
                                    V(0.085 * math.cos(a) * (1 if k != 1 else 0), 0, 0.25 + 0.085 * math.sin(a))],
                            [0.008, 0.004], on, ep, seg=4, sub=1))
        dim = [ellipsoid("tipoff", 0.04, off, ep, loc=(0, 0, 0.2), scale=(0.85, 0.55, 1.4), seg=12, rings=8)]
        E[s] = (ep, lit, dim)
    for s in (-1, 1):
        blob("hind", 0.06, fur, b, loc=(s * 0.095, 0.02, 0.03), scale=(0.8, 1.6, 0.5), seg=16, rings=10)
        blob("front", 0.035, fur, b, loc=(s * 0.055, -0.12, 0.03), scale=(1, 1.3, 0.8), seg=12, rings=8)
    blob("tailpuff", 0.055, fur, b, loc=(0, 0.22, 0.16), seg=14, rings=10)

    def ears(state):
        for s, (ep, lit, dim) in E.items():
            up = (s == 1) == (state == 0)
            ep.rotation_euler = (-0.12, s * 0.16, 0) if up else (0.35, s * 1.85, 0)
            set_hide(lit, not up)
            set_hide(dim, up)

    def pose(anim, i, n):
        ph = TAU * i / n
        if anim == 'walk':
            ears(0 if i < 3 else 1)
            b.location.z = 0.09 * max(0, math.sin(ph))
            b.rotation_euler = (0.12 * math.cos(ph), 0, 0)
            hd.rotation_euler = (0, 0, 0)
        else:
            ears(0 if i < 2 else 1)
            b.location.z = 0
            b.rotation_euler = (0, 0, 0)
            b.scale = (1, 1, 1 + 0.02 * math.sin(ph))
            hd.rotation_euler = (0.05 * math.sin(ph * 2), 0, 0.1 * math.sin(ph))
    c.pose = pose
    c.meta = dict(move="hops")
    return c


# ================================================================ 3 gateway doe (default gateway)
def gateway_doe():
    c = C("wc_gateway_doe")
    b = pivot("b", parent=c.body)
    fur = mat("#b8804e", pat='fur', P=dict(scale=70), var=0.18)
    spots = mat("#b8804e", pat='dots', color2="#f6e8cc", P=dict(nu=7, fv=9, rad=0.13), var=0.15)
    cream = mat("#f6ead2", pat='fur', P=dict(scale=70), var=0.1)
    dark = mat("#3a2a26", kind='soft')
    blue = mat("#3a7ae0", kind='cloth', rim=0.6)
    gold = mat("#f2c24e", metal=True, rim=0.9)
    bz = 0.34
    blob("dbody", 0.15, spots, b, loc=(0, 0.04, bz + 0.05), scale=(0.78, 1.45, 0.82), seg=30, rings=20)
    blob("dbelly", 0.12, cream, b, loc=(0, 0.05, bz - 0.01), scale=(0.7, 1.25, 0.55), seg=22, rings=14)
    tube("dneck", [V(0, -0.13, bz + 0.08), V(0, -0.19, bz + 0.2), V(0, -0.215, bz + 0.31)], [0.066, 0.052, 0.045], fur, b,
         seg=14, sub=3)
    blob("dthroat", 0.045, cream, b, loc=(0, -0.21, bz + 0.17), scale=(0.9, 0.7, 1.5), seg=14, rings=10)
    hd = pivot("h", (0, -0.225, bz + 0.35), b)
    blob("dhead", 0.085, fur, hd, scale=(0.9, 1.05, 0.92), seg=24, rings=16)
    blob("dsnout", 0.05, cream, hd, loc=(0, -0.08, -0.03), scale=(0.75, 1.25, 0.7), seg=16, rings=10)
    ellipsoid("dnose", 0.018, dark, hd, loc=(0, -0.14, -0.012), scale=(1.2, 0.7, 0.8), seg=8, rings=6)
    EA = {}
    for s in (-1, 1):
        eye(hd, (s * 0.047, -0.062, 0.02), 0.031, iris="#3a2418", rot=(0, 0, -s * 0.45))
        blush(hd, (s * 0.058, -0.085, -0.02), 0.016)
        ep = pivot("ear", (s * 0.065, 0.02, 0.05), hd, rot=(0.1, s * 0.95, 0))
        blob("dear", 0.05, fur, ep, loc=(0, 0, 0.065), scale=(0.6, 0.28, 1.3), seg=14, rings=10)
        ellipsoid("dearin", 0.036, mat("#f0c0b0", kind='soft'), ep, loc=(0, -0.012, 0.065), scale=(0.45, 0.15, 1.15), seg=10, rings=6)
        EA[s] = ep
    L = leg4(b, bz, dict(FL=(0.06, -0.14), FR=(-0.06, -0.14), BL=(0.06, 0.2), BR=(-0.06, 0.2)), 0.03, fur, dark)
    tail = pivot("tail", (0, 0.25, bz + 0.1), b)
    blob("dtail", 0.035, cream, tail, loc=(0, 0.01, 0.0), scale=(0.8, 0.6, 1.15), seg=12, rings=8)
    # blue ribbon with a bow and a tiny golden gate pendant (the way out of the village)
    Cn = V(0, -0.175, bz + 0.16)
    nb = V(0, 0.9, 0.45)
    tube("ribbon", ring_pts(Cn, 0.06, 0.06, n=28, axis_b=nb), [0.014], blue, b, seg=6, sub=1, flat=0.5)
    B = Cn + V(0, -0.9, -0.45) * 0.062
    for s in (-1, 1):
        ellipsoid("bowloop", 0.028, blue, b, loc=B + V(s * 0.03, -0.006, 0.006), scale=(1.3, 0.45, 0.8), rot=(0, 0, s * 0.25),
                  seg=12, rings=8)
    ellipsoid("bowknot", 0.014, blue, b, loc=B + V(0, -0.012, 0), seg=8, rings=6)
    P0 = B + V(0, -0.008, -0.045)
    tube("arch", [P0 + V(-0.022, 0, -0.022), P0 + V(-0.022, 0, 0.008), P0 + V(0, 0, 0.026), P0 + V(0.022, 0, 0.008),
                  P0 + V(0.022, 0, -0.022)], [0.0065], gold, b, seg=6, sub=3)
    box("gatelight", (0.034, 0.004, 0.032), glow("#9ffff0", 2.2), b, loc=P0 + V(0, 0.002, -0.004))

    def pose(anim, i, n):
        ph = TAU * i / n
        if anim == 'walk':
            walk4(L, ph, 0.5)
            b.location.z = 0.015 * abs(math.cos(ph))
            hd.rotation_euler = (0.06 * math.sin(2 * ph), 0, 0)
        else:
            walk4(L, 0, 0)
            b.location.z = 0
            hd.rotation_euler = (0, 0, 0.18 * math.sin(ph))
        for s, ep in EA.items():
            ep.rotation_euler = (0.1 + (0.35 if (anim == 'idle' and i == 2 and s == 1) else 0), s * 0.95, 0)
        tail.rotation_euler = (0.3 * math.sin(ph * 2), 0, 0)
    c.pose = pose
    c.meta = dict(move="walks")
    return c


# ================================================================ 4 queue squirrel (queue)
def queue_squirrel():
    c = C("wc_queue_squirrel")
    b = pivot("b", parent=c.body)
    fur = mat("#c46c34", pat='fur', P=dict(scale=70), var=0.2)
    fur2 = mat("#a8562a", pat='fur', P=dict(scale=50), var=0.25, bump=0.5)
    cream = mat("#f6e2c0", pat='fur', P=dict(scale=70), var=0.1)
    dark = mat("#3a2420", kind='soft')
    wood = mat("#7a5232", pat='wood', P=dict(nu=6))
    cone = mat("#9a6034", pat='dots', color2="#5e3618", P=dict(nu=7, fv=70, rad=0.32), var=0.2, bump=0.6)
    blob("qbody", 0.12, fur, b, loc=(0, 0.03, 0.15), scale=(0.95, 0.95, 1.2), seg=26, rings=18)
    blob("qbelly", 0.09, cream, b, loc=(0, -0.04, 0.15), scale=(0.85, 0.6, 1.15), seg=20, rings=14)
    hd = pivot("h", (0, -0.03, 0.34), b)
    blob("qhead", 0.1, fur, hd, scale=(1.05, 1.0, 0.92), seg=24, rings=16)
    blob("qmuzzle", 0.045, cream, hd, loc=(0, -0.08, -0.03), scale=(1.1, 0.8, 0.8), seg=14, rings=10)
    ellipsoid("qnose", 0.014, dark, hd, loc=(0, -0.118, -0.012), scale=(1.3, 0.7, 0.9), seg=8, rings=6)
    for s in (-1, 1):
        eye(hd, (s * 0.05, -0.072, 0.02), 0.032, iris="#2a1a10", rot=(0, 0, -s * 0.4))
        blush(hd, (s * 0.065, -0.08, -0.03), 0.017)
        ep = pivot("ear", (s * 0.06, 0.0, 0.075), hd, rot=(0, s * 0.3, 0))
        blob("qear", 0.035, fur, ep, loc=(0, 0, 0.035), scale=(0.75, 0.4, 1.3),
             deform=lambda p: Vector((p.x * (1 - 0.6 * max(0, p.z)), p.y, p.z)), seg=12, rings=8)
        tube("tuft", [V(0, 0, 0.07), V(s * 0.008, 0.01, 0.105), V(s * 0.02, 0.015, 0.125)], [0.013, 0.008, 0.002], fur2, ep,
             seg=6, sub=2)
    tail = pivot("tail", (0, 0.12, 0.08), b)
    tube("qtail", [V(0, 0, 0), V(0, 0.11, 0.07), V(0, 0.18, 0.24), V(0, 0.13, 0.41), V(0, 0.03, 0.45)],
         [0.04, 0.09, 0.11, 0.095, 0.045], fur2, tail, seg=16, sub=4)
    for s in (-1, 1):
        blob("hind", 0.045, fur, b, loc=(s * 0.085, -0.02, 0.03), scale=(0.8, 1.5, 0.6), seg=14, rings=10)
        tube("arm", [V(s * 0.085, -0.04, 0.24), V(s * 0.08, -0.12, 0.2), V(s * 0.06, -0.15, 0.185)], [0.024, 0.02], fur, b,
             seg=8, sub=2)
        ellipsoid("paw", 0.02, fur, b, loc=(s * 0.058, -0.155, 0.19), seg=8, rings=6)
    # a twig held across, three pinecones waiting in a neat line on it
    tube("twig", [V(-0.17, -0.16, 0.175), V(0.0, -0.163, 0.17), V(0.17, -0.16, 0.175)], [0.011], wood, b, seg=6, sub=2)
    ellipsoid("leaf", 0.03, mat("#7ab84a", kind='soft'), b, loc=(0.19, -0.16, 0.19), scale=(1, 0.25, 0.5), rot=(0, -0.6, 0),
              seg=10, rings=6)
    cones = []
    for k, x in enumerate((-0.11, 0.0, 0.11)):
        p = pivot("pc", (x, -0.165, 0.18), b)
        blob("cone", 0.03, cone, p, loc=(0, 0, 0.032), scale=(1, 1, 1.35), seg=14, rings=10)
        tube("stem", [V(0, 0, 0.07), V(0.004, 0, 0.085)], [0.005], wood, p, seg=4, sub=1, line=False)
        cones.append(p)

    def pose(anim, i, n):
        ph = TAU * i / n
        for k, p in enumerate(cones):
            p.location.z = 0.18 + (0.03 if (anim == 'idle' and i == k + 1) else 0.0)
        if anim == 'walk':
            b.location.z = 0.06 * max(0, math.sin(ph))
            b.rotation_euler = (0.1 * math.cos(ph), 0, 0)
            tail.rotation_euler = (0.2 * math.sin(ph), 0, 0)
            hd.rotation_euler = (0, 0, 0)
        else:
            b.location.z = 0
            b.rotation_euler = (0, 0, 0)
            tail.rotation_euler = (0.05 * math.sin(ph), 0, 0.15 * math.sin(ph))
            hd.rotation_euler = (0, 0, 0.12 * math.sin(ph))
    c.pose = pose
    c.meta = dict(move="hops")
    return c


# ================================================================ 5 stream fish (bandwidth)
def _fish(parent, sc, main, belly, fin, loc=(0, 0, 0), detail=True):
    f = pivot("fish", loc, parent)
    blob("fbody", 0.13 * sc, main, f, scale=(0.62, 1.35, 0.85),
         deform=lambda p: Vector((p.x * (1 - 0.45 * max(0, p.y)), p.y, p.z * (1 - 0.35 * max(0, p.y)))), seg=28, rings=18)
    blob("fbelly", 0.11 * sc, belly, f, loc=(0, -0.025 * sc, -0.045 * sc), scale=(0.55, 1.1, 0.5), seg=20, rings=12)
    tail = pivot("ftail", (0, 0.16 * sc, 0), f)
    for sg in (-1, 1):
        blob("fluke", 0.075 * sc, fin, tail, loc=(0, 0.055 * sc, sg * 0.04 * sc), scale=(0.15, 1.0, 0.6), rot=(sg * 0.65, 0, 0),
             seg=14, rings=8)
    blob("dorsal", 0.085 * sc, fin, f, loc=(0, 0.03 * sc, 0.095 * sc), scale=(0.12, 1.0, 0.55), rot=(-0.35, 0, 0), seg=14, rings=8)
    pects = []
    for sg in (-1, 1):
        pp = pivot("pect", (sg * 0.07 * sc, -0.03 * sc, -0.03 * sc), f)
        blob("pfin", 0.065 * sc, fin, pp, loc=(sg * 0.045 * sc, 0.025 * sc, 0), scale=(1, 0.6, 0.12), rot=(0, sg * 0.4, 0),
             seg=14, rings=8)
        pects.append((pp, sg))
        if detail:
            eye(f, (sg * 0.058 * sc, -0.1 * sc, 0.03 * sc), 0.034 * sc, iris="#1a2a4a", rot=(0, 0, -sg * 0.9))
            blush(f, (sg * 0.06 * sc, -0.13 * sc, -0.02 * sc), 0.015 * sc)
        else:
            ellipsoid("e", 0.016 * sc * 2, mat("#1a2a4a", kind='flat', line=False), f, loc=(sg * 0.05 * sc, -0.11 * sc, 0.03 * sc),
                      seg=8, rings=6)
    if detail:
        smile(f, (0, -0.172 * sc, -0.012 * sc), 0.02 * sc, curve=0.5)
    return f, tail, pects


def stream_fish():
    c = C("wc_stream_fish")
    main = mat("#3a8ae0", pat='plaid', color2="#8ad4ff", P=dict(nu=16, fv=36, thr=0.8), var=0.12, kind='soft', rim=0.8)
    belly = mat("#eaf6ff", kind='soft', rim=0.5)
    fin = mat("#7fe8dc", pat='stripes', color2="#5ac8d8", P=dict(nu=4, fv=90, thr=0.6, weave=False), kind='soft', rim=0.7)
    f, tail, pects = _fish(c.body, 1.0, main, belly, fin, loc=(0, 0, 0.3))
    small = []
    for (x, y, z, ph0) in ((0.2, 0.2, 0.2, 1.2), (-0.19, 0.27, 0.16, 2.6)):
        small.append((_fish(c.body, 0.45, mat("#4a9ae8", kind='soft', rim=0.7), belly, fin, loc=(x, y, z), detail=False), z, ph0))
    # the stream under it: a soft pool, a ripple ring and drops
    ellipsoid("pool", 0.26, glow("#8fd8ff", 0.9, alpha=0.32), c.body, loc=(0, 0.06, 0.006), scale=(1, 0.75, 0.03), seg=28, rings=8)
    rip = tube("ripple", ring_pts((0, 0.06, 0.012), 0.2, 0.15, n=30), [0.006], glow("#e8fbff", 1.6, alpha=0.7), c.body, seg=5, sub=1)
    drops = [ellipsoid("drop", 0.016, glow("#dff8ff", 2.0), c.body, loc=(0.0, 0, 0), seg=8, rings=6) for _ in range(3)]

    def pose(anim, i, n):
        ph = TAU * i / n
        sp = 1 if anim == 'idle' else 2
        f.location.z = 0.3 + 0.035 * math.sin(ph)
        f.rotation_euler = ((-0.15 if anim == 'walk' else 0.0) + 0.05 * math.cos(ph), 0, 0.12 * math.sin(ph * sp))
        tail.rotation_euler = (0, 0, 0.45 * math.sin(ph * sp + 1))
        for pp, sg in pects:
            pp.rotation_euler = (0, sg * 0.3 * math.sin(ph * sp), 0)
        for (sf, st, _), z0, ph0 in small:
            sf.location.z = z0 + 0.03 * math.sin(ph + ph0)
            st.rotation_euler = (0, 0, 0.5 * math.sin(ph * sp + ph0))
        rip.scale = (1 + 0.12 * ((i % 4) / 3), 1 + 0.12 * ((i % 4) / 3), 1)
        for k, d in enumerate(drops):
            a = ph + k * TAU / 3
            d.location = (0.16 * math.cos(k * 2.1), 0.06 + 0.1 * math.sin(k * 2.1), 0.04 + 0.08 * max(0, math.sin(a)))
            d.hide_render = math.sin(a) < 0
    c.pose = pose
    c.meta = dict(move="swims", hover=0.3)
    return c


# ================================================================ 6 thunder frog (latency)
def thunder_frog():
    c = C("wc_thunder_frog")
    b = pivot("b", parent=c.body)
    green = mat("#8ccc3a", pat='dots', color2="#6aa82a", P=dict(nu=7, fv=12, rad=0.14), kind='soft', var=0.1, rim=0.7)
    pad = mat("#4a9a48", pat='stripes', color2="#3f8a3e", P=dict(nu=20, fv=1, thr=0.7, weave=False), kind='soft', rim=0.5)
    # lily leaf with a notch at the back
    leaf = pivot("leaf", parent=c.body)
    vs = [(0, 0.02, 0.022)]
    N = 30
    for k in range(N + 1):
        a = math.pi / 2 + 0.38 + (TAU - 0.76) * k / N
        vs.append((0.32 * math.cos(a), 0.02 + 0.27 * math.sin(a), 0.012))
    fs = [(0, k + 1, k + 2) for k in range(N)]
    mesh_obj("pad", vs, fs, pad, leaf, smooth=False)
    for k in range(5):
        a = math.pi / 2 + 0.9 + k * 0.95
        tube("vein", [V(0, 0.02, 0.024), V(0.26 * math.cos(a), 0.02 + 0.22 * math.sin(a), 0.016)], [0.005, 0.002],
             mat("#6ab85a", kind='flat', line=False), leaf, seg=4, sub=1)
    fr = pivot("fr", (0, 0, 0.022), b)
    blob("fbody", 0.15, green, fr, loc=(0, 0.04, 0.12), scale=(1.1, 1.0, 0.78), seg=30, rings=20)
    blob("fhead", 0.13, green, fr, loc=(0, -0.06, 0.2), scale=(1.25, 0.95, 0.68), seg=30, rings=20)
    bellyA = blob("bellyA", 0.1, mat("#ffe46a", kind='soft'), fr, loc=(0, -0.1, 0.11), scale=(1.0, 0.5, 0.75), seg=20, rings=12)
    bellyB = blob("bellyB", 0.1, mat("#ffa0b0", kind='soft'), fr, loc=(0, -0.1, 0.11), scale=(1.0, 0.5, 0.75), seg=20, rings=12)
    for s in (-1, 1):
        blob("bump", 0.055, green, fr, loc=(s * 0.085, -0.08, 0.28), seg=16, rings=10)
        eye(fr, (s * 0.085, -0.115, 0.29), 0.043, iris="#3a2a10", rot=(0, 0, -s * 0.3))
        blush(fr, (s * 0.12, -0.15, 0.18), 0.022)
        blob("thigh", 0.07, green, fr, loc=(s * 0.14, 0.08, 0.08), scale=(0.75, 1.3, 0.7), seg=18, rings=12)
        blob("foot", 0.05, mat("#a8dc5a", kind='soft'), fr, loc=(s * 0.17, -0.03, 0.01), scale=(1.0, 1.4, 0.3), seg=14, rings=8)
        tube("arm", [V(s * 0.08, -0.1, 0.13), V(s * 0.1, -0.15, 0.05), V(s * 0.1, -0.165, 0.015)], [0.022, 0.018], green, fr,
             seg=8, sub=2)
        ellipsoid("hand", 0.028, mat("#a8dc5a", kind='soft'), fr, loc=(s * 0.1, -0.175, 0.008), scale=(1.1, 1.1, 0.3), seg=10, rings=6)
    smile(fr, (0, -0.185, 0.175), 0.065, curve=0.28)
    # first the flash, a moment later the thunder rings: the gap is the latency
    bolt = [tube("bolt", [V(0.25, -0.05, 0.78), V(0.19, -0.05, 0.64), V(0.26, -0.05, 0.62), V(0.18, -0.05, 0.46)],
                 [0.026, 0.02, 0.015, 0.005], glow("#fff27a", 3.2), c.body, seg=6, sub=1)]
    for k in range(3):
        a = 0.6 + k * 2.1
        bolt.append(tube("spark", [V(0.22 + 0.07 * math.cos(a), -0.05, 0.62 + 0.07 * math.sin(a)),
                                   V(0.22 + 0.12 * math.cos(a), -0.05, 0.62 + 0.12 * math.sin(a))], [0.007, 0.003],
                         glow("#fff6b0", 2.5), c.body, seg=4, sub=1))
    rings = []
    for k in range(2):
        R = 0.07 + 0.06 * k
        rings.append(tube("thunder", [V(-0.2 + R * math.cos(a), -0.08, 0.5 + R * math.sin(a))
                                      for a in [math.pi * 0.55 + 0.9 * j / 8 * math.pi for j in range(9)]],
                          [0.01], glow("#cfe0ff", 2.2), c.body, seg=5, sub=1))

    def pose(anim, i, n):
        ph = TAU * i / n
        if anim == 'walk':
            set_hide([leaf], True)
            set_hide(bolt + rings, True)
            fr.location.z = 0.022 + 0.11 * max(0, math.sin(ph))
            fr.rotation_euler = (-0.25 * max(0, math.sin(ph)), 0, 0)
            fr.scale = (1, 1, 1 + 0.08 * math.sin(ph))
            bellyA.hide_render, bellyB.hide_render = False, True
        else:
            set_hide([leaf], False)
            fr.location.z = 0.022
            fr.rotation_euler = (0, 0, 0)
            fr.scale = (1, 1, 1 + 0.025 * math.sin(ph))
            set_hide(bolt, i != 0)
            rings[0].hide_render = i < 2
            rings[1].hide_render = i < 3
            bellyA.hide_render, bellyB.hide_render = i >= 2, i < 2
    c.pose = pose
    c.meta = dict(move="hops")
    return c


# ================================================================ 7 handshake dove (handshake)
def handshake_dove():
    c = C("wc_handshake_dove")
    b = pivot("b", parent=c.body)
    white = mat("#f8f6f4", pat='fur', P=dict(scale=90), kind='soft', var=0.08, rim=0.6)
    tip = mat("#c4c4d8", pat='stripes', color2="#a8a8c4", P=dict(nu=6, fv=70, thr=0.6, weave=False), kind='soft', rim=0.6)
    sheen = mat("#a8dcd4", pat='stripes', color2="#c8b4e8", P=dict(nu=8, fv=70, thr=0.5, weave=False), kind='soft', rim=0.6)
    pinkl = mat("#e89aa0", kind='soft')
    blob("dvbody", 0.13, white, b, loc=(0, 0.03, 0.19), scale=(0.85, 1.3, 0.9),
         deform=lambda p: Vector((p.x, p.y, p.z + 0.25 * max(0, p.y) ** 2)), seg=28, rings=18)
    blob("collar", 0.075, sheen, b, loc=(0, -0.08, 0.28), scale=(1.05, 0.85, 0.75), seg=20, rings=12)
    hd = pivot("h", (0, -0.1, 0.37), b)
    blob("dvhead", 0.085, white, hd, scale=(0.95, 1.0, 0.95), seg=24, rings=16)
    ellipsoid("beak", 0.022, pinkl, hd, loc=(0, -0.095, -0.012), scale=(0.75, 1.6, 0.75), seg=10, rings=8)
    ellipsoid("cere", 0.013, white, hd, loc=(0, -0.085, 0.006), seg=8, rings=6)
    for s in (-1, 1):
        eye(hd, (s * 0.047, -0.058, 0.018), 0.027, iris="#2a1a2a", rot=(0, 0, -s * 0.5))
        blush(hd, (s * 0.055, -0.065, -0.025), 0.015)
    # left wing folded, right wing raised in greeting
    wl = pivot("wingL", (-0.105, 0.02, 0.24), b)
    blob("fold", 0.1, white, wl, loc=(-0.005, 0.06, -0.02), scale=(0.32, 1.15, 0.7), rot=(0.3, 0, 0), seg=18, rings=12)
    blob("foldtip", 0.06, tip, wl, loc=(-0.005, 0.15, 0.0), scale=(0.3, 1.2, 0.5), rot=(0.4, 0, 0), seg=14, rings=8)
    wr = pivot("wingR", (0.1, 0.0, 0.25), b)
    blob("open", 0.1, white, wr, loc=(0.09, 0.03, 0), scale=(1.0, 0.85, 0.2),
         deform=lambda p: Vector((p.x, p.y + 0.35 * max(0, p.x), p.z)), seg=20, rings=12)
    for k in range(5):
        a = math.radians(-35 + 22 * k)
        p0 = V(0.15, 0.06, 0)
        tube("feather", [p0, p0 + V(math.cos(a) * 0.09, math.sin(a) * 0.09 + 0.02, 0), p0 + V(math.cos(a) * 0.16, math.sin(a) * 0.16 + 0.04, 0)],
             [0.026, 0.024, 0.008], white if k < 2 else tip, wr, seg=8, sub=2, flat=0.35)
    tail = pivot("tail", (0, 0.17, 0.2), b)
    blob("fan", 0.085, white, tail, loc=(0, 0.05, 0.02), scale=(0.9, 1.0, 0.15), rot=(-0.35, 0, 0), seg=18, rings=10)
    blob("fantip", 0.07, tip, tail, loc=(0, 0.1, 0.035), scale=(0.95, 0.5, 0.12), rot=(-0.35, 0, 0), seg=14, rings=8)
    F = {}
    for s in (-1, 1):
        fp = pivot("leg", (s * 0.04, -0.0, 0.08), b)
        tube("dleg", [V(0, 0, 0), V(0, -0.01, -0.075)], [0.011], pinkl, fp, seg=6, sub=1)
        for t in (-0.45, 0, 0.45):
            tube("toe", [V(0, -0.01, -0.075), V(math.sin(t) * 0.03, -0.04, -0.078)], [0.008], pinkl, fp, seg=5, sub=1, line=False)
        F[s] = fp
    cyl("ring", 0.017, 0.017, 0.016, mat("#3a7ae0", kind='soft', rim=0.6), F[1], loc=(0, -0.006, -0.05))
    # hello, hello-back, ok: three soft lights that appear one after the other
    dots = [ellipsoid("hs", 0.022, glow(cl, 2.4), c.body, loc=(0.13 + 0.09 * k, -0.12, 0.6 + 0.04 * math.sin(k * 1.4)), seg=8,
                      rings=6) for k, cl in enumerate(("#9ffff0", "#ffe08a", "#9ffff0"))]

    def pose(anim, i, n):
        ph = TAU * i / n
        if anim == 'walk':
            b.location.z = 0.01 * abs(math.sin(ph))
            hd.location.y = -0.1 - 0.03 * math.sin(ph)
            wr.rotation_euler = (0, -0.25, -0.9)
            b.rotation_euler = (0, 0.06 * math.sin(ph), 0)
            for s, fp in F.items():
                fp.location.y = 0.04 * math.sin(ph) * s
            set_hide(dots, True)
        else:
            b.location.z = 0
            hd.location.y = -0.1
            b.rotation_euler = (0, 0, 0)
            wr.rotation_euler = (0, -(0.8 + 0.25 * math.sin(ph)), 0)
            for s, fp in F.items():
                fp.location.y = 0
            for k, d in enumerate(dots):
                d.hide_render = k > i
            hd.rotation_euler = (0, 0, 0.12 * math.sin(ph))
    c.pose = pose
    c.meta = dict(move="waddles")
    return c


# ================================================================ 8 cocoon worm (encapsulation)
def cocoon_worm():
    c = C("wc_cocoon_worm")
    b = pivot("b", parent=c.body)
    larva = mat("#ffd84a", pat='skin', kind='soft', var=0.05, rim=0.7)
    layers = [("#5ac8c0", "#8ae0d8", 0.2, 0.15, 0.3), ("#f08aa8", "#f8b0c8", 0.11, 0.122, 0.28),
              ("#b89ae8", "#d0bcf4", 0.02, 0.098, 0.26)]
    wraps = []
    zc = 0.15
    for k, (c1, c2, y0, R, Lz) in enumerate(layers):
        m = mat(c1, pat='spiral', color2=c2, P=dict(nu=5, fv=28, thr=0.55), kind='soft', var=0.12, rim=0.7)
        w = pivot("wrap", (0, y0, zc), b, rot=(math.radians(90), 0, 0))
        loft("cocoon", [(0, R * 0.25, R * 0.25), (0.04, R * 0.8, R * 0.78), (Lz * 0.45, R, R * 0.97), (Lz, R * 0.92, R * 0.9)],
             m, w, seg=28, cap_bot=True)
        tube("lip", ring_pts((0, 0, Lz), R * 0.92, R * 0.9, n=28), [0.016], mat(c2, kind='soft', rim=0.6), w, seg=8, sub=1)
        wraps.append(w)
    # the larva peeking out of the innermost wrap
    hd = pivot("h", (0, -0.26, zc - 0.005), b)
    blob("lhead", 0.078, larva, hd, scale=(1.0, 0.95, 0.95), seg=24, rings=16)
    for s in (-1, 1):
        eye(hd, (s * 0.034, -0.06, 0.012), 0.028, iris="#3a2a1a", rot=(0, 0, -s * 0.35))
        blush(hd, (s * 0.05, -0.065, -0.03), 0.014)
        tube("nub", [V(s * 0.03, -0.01, 0.065), V(s * 0.045, -0.02, 0.105)], [0.01, 0.007], larva, hd, seg=6, sub=1)
        ellipsoid("nubtip", 0.014, mat("#ff9a4a", kind='soft'), hd, loc=(s * 0.046, -0.02, 0.11), seg=8, rings=6)
    smile(hd, (0, -0.077, -0.03), 0.02)
    blob("lneck", 0.07, larva, b, loc=(0, -0.2, zc - 0.01), scale=(1, 0.9, 0.95), seg=18, rings=12)
    leaf = ellipsoid("mint", 0.05, mat("#6ac05a", pat='stripes', color2="#4aa040", P=dict(nu=2, fv=60, thr=0.7, weave=False),
                                        kind='soft'), b, loc=(0.06, 0.24, zc + 0.15), scale=(1, 0.5, 0.2), rot=(0.2, 0.3, 0.5),
                     seg=12, rings=8)

    def pose(anim, i, n):
        ph = TAU * i / n
        if anim == 'walk':
            b.location.z = 0
            for k, w in enumerate(wraps):
                w.scale = (1, 1, 1 + 0.07 * math.sin(ph - k * 0.9))
                w.location.z = zc + 0.015 * max(0, math.sin(ph - k * 0.9))
            hd.location.y = -0.26 - 0.025 * math.sin(ph)
            hd.rotation_euler = (0, 0, 0)
        else:
            for k, w in enumerate(wraps):
                w.scale = (1 + 0.015 * math.sin(ph - k), 1 + 0.015 * math.sin(ph - k), 1)
                w.location.z = zc
            hd.location.y = -0.26 - 0.01 * math.sin(ph)
            hd.rotation_euler = (0.08 * math.sin(ph), 0, 0.15 * math.sin(ph))
    c.pose = pose
    c.meta = dict(move="crawls")
    return c


# ================================================================ 9 count butterfly (TTL)
def count_butterfly():
    c = C("wc_count_butterfly")
    b = pivot("b", (0, 0, 0.6), c.body)
    bodym = mat("#2a3a7a", pat='fur', P=dict(scale=90), kind='soft', var=0.15, rim=0.7)
    blob("thorax", 0.05, bodym, b, scale=(0.9, 1.1, 0.9), seg=16, rings=12)
    blob("abdomen", 0.04, bodym, b, loc=(0, 0.1, -0.01), scale=(0.75, 2.0, 0.75), seg=16, rings=12)
    hd = pivot("h", (0, -0.07, 0.015), b)
    blob("bhead", 0.045, bodym, hd, seg=16, rings=12)
    for s in (-1, 1):
        eye(hd, (s * 0.024, -0.032, 0.012), 0.021, iris="#2a2a5a", rot=(0, 0, -s * 0.5))
        tube("ant", [V(s * 0.012, -0.03, 0.035), V(s * 0.04, -0.08, 0.12), V(s * 0.07, -0.08, 0.17), V(s * 0.08, -0.05, 0.16)],
             [0.005, 0.004], bodym, hd, seg=5, sub=3, line=False)
        ellipsoid("antb", 0.014, glow("#cffaff", 2.4), hd, loc=(s * 0.08, -0.05, 0.16), seg=8, rings=6)
    blue = mat("#3a86f0", pat='patches', color2="#2a5ac8", P=dict(scale=6, thr=0.5, sharp=4), kind='soft', var=0.1, rim=0.8)
    blue2 = mat("#7ab8ff", pat='patches', color2="#5a9af0", P=dict(scale=6, thr=0.5, sharp=4), kind='soft', var=0.1, rim=0.8)
    edge = mat("#1e2a6a", kind='soft', rim=0.5)
    pip_on = glow("#d8fcff", 3.2)
    pip_off = mat("#2a4a9a", kind='soft', rim=0.2, line=False)
    W = {}
    last = []
    for s in (-1, 1):
        w = pivot("wing", (s * 0.03, 0, 0.01), b)
        blob("upE", 0.18, edge, w, loc=(s * 0.15, -0.05, 0.0), scale=(1.0, 0.78, 0.045), rot=(0, 0, s * -0.3), seg=28, rings=10)
        blob("up", 0.165, blue, w, loc=(s * 0.145, -0.05, 0.006), scale=(1.0, 0.76, 0.045), rot=(0, 0, s * -0.3), seg=28, rings=10)
        blob("loE", 0.115, edge, w, loc=(s * 0.1, 0.09, -0.002), scale=(0.9, 1.0, 0.045), rot=(0, 0, s * 0.3), seg=24, rings=10)
        blob("lo", 0.103, blue2, w, loc=(s * 0.098, 0.088, 0.004), scale=(0.9, 1.0, 0.045), rot=(0, 0, s * 0.3), seg=24, rings=10)
        tube("swallow", [V(s * 0.12, 0.17, 0.0), V(s * 0.15, 0.24, -0.005), V(s * 0.14, 0.29, -0.01)], [0.018, 0.012, 0.008], edge, w,
             seg=6, sub=2, flat=0.4)
        for k in range(4):
            pos = (s * (0.08 + 0.055 * k), -0.11 + 0.025 * k, 0.018)
            pip = ellipsoid("pip", 0.019, pip_on, w, loc=pos, scale=(1, 1, 0.35), seg=10, rings=6)
            if k == 3:
                last.append((pip, ellipsoid("pipoff", 0.019, pip_off, w, loc=pos, scale=(1, 1, 0.4), seg=10, rings=6)))
        W[s] = w
    sparkle = ellipsoid("sp", 0.07, glow("#cffaff", 1.3, alpha=0.14, soft=True), b, loc=(0, 0, 0.02), seg=12, rings=8)

    def pose(anim, i, n):
        ph = TAU * i / n
        fl = 0.7 * math.sin(ph * (1 if anim == 'idle' else 2))
        for s, w in W.items():
            w.rotation_euler = (0, -s * (0.6 * fl + 0.45), 0)
        b.location.z = 0.6 + 0.04 * math.sin(ph + 1)
        b.rotation_euler = (-0.2, 0, 0)
        for on, off in last:
            dim = anim == 'idle' and i >= 2
            on.hide_render, off.hide_render = dim, not dim
    c.pose = pose
    c.meta = dict(move="flies", hover=0.6)
    return c


# ================================================================ 10 backup lizard (redundancy)
def backup_lizard():
    c = C("wc_backup_lizard")
    b = pivot("b", parent=c.body)
    skin = mat("#6ac04a", pat='dots', color2="#a8e070", P=dict(nu=8, fv=24, rad=0.18), kind='soft', var=0.1, rim=0.7)
    belly = mat("#d8f0a0", kind='soft')
    gold = mat("#f0c040", pat='stripes', color2="#d89a28", P=dict(nu=8, fv=60, thr=0.6, weave=False), kind='soft', rim=0.8)
    blue = mat("#4a8ae8", pat='stripes', color2="#2a62c0", P=dict(nu=8, fv=60, thr=0.6, weave=False), kind='soft', rim=0.8)
    zz = 0.075
    spine = pivot("spine", parent=b)
    tube("lbody", [V(0, -0.17, zz + 0.005), V(0, -0.05, zz), V(0, 0.07, zz - 0.005), V(0, 0.16, zz - 0.015)],
         [0.06, 0.075, 0.07, 0.048], skin, spine, seg=16, sub=4, flat=1.3)
    for k in range(5):
        ellipsoid("crest", 0.016, mat("#f8e070", kind='soft', rim=0.5), spine, loc=(0, -0.12 + 0.06 * k, zz + 0.07 - 0.004 * k),
                  seg=8, rings=6)
    hd = pivot("h", (0, -0.24, zz + 0.02), b)
    blob("lhead", 0.08, skin, hd, scale=(1.0, 1.25, 0.72), seg=24, rings=16)
    blob("ljaw", 0.06, belly, hd, loc=(0, -0.03, -0.03), scale=(1.0, 1.2, 0.5), seg=16, rings=10)
    for s in (-1, 1):
        blob("ebump", 0.035, skin, hd, loc=(s * 0.048, -0.03, 0.045), seg=12, rings=8)
        eye(hd, (s * 0.05, -0.05, 0.05), 0.03, iris="#5a3a10", rot=(0, 0, -s * 0.6))
        blush(hd, (s * 0.06, -0.075, 0.0), 0.014)
    smile(hd, (0, -0.1, 0.0), 0.035, curve=0.35)
    LG = []
    for s in (-1, 1):
        for j, y in enumerate((-0.12, 0.1)):
            lp = pivot("lleg", (s * 0.07, y, zz - 0.01), b)
            tube("ll", [V(0, 0, 0), V(s * 0.07, 0, 0.01), V(s * 0.1, -0.02, -0.055)], [0.022, 0.019, 0.016], skin, lp, seg=8, sub=2)
            ellipsoid("lfoot", 0.026, skin, lp, loc=(s * 0.105, -0.035, -0.058), scale=(1.1, 1.3, 0.35), seg=10, rings=6)
            LG.append((lp, s, j))
    T = []
    for s, m in ((1, gold), (-1, blue)):
        tp = pivot("tail", (s * 0.012, 0.17, zz - 0.015), b)
        tube("ltail", [V(0, 0, 0), V(s * 0.05, 0.1, -0.02), V(s * 0.1, 0.19, -0.02), V(s * 0.08, 0.25, 0.02)],
             [0.035, 0.026, 0.016, 0.006], m, tp, seg=10, sub=4)
        T.append((tp, s))

    def pose(anim, i, n):
        ph = TAU * i / n
        if anim == 'walk':
            spine.rotation_euler = (0, 0, 0.1 * math.sin(ph))
            hd.rotation_euler = (0, 0, -0.12 * math.sin(ph))
            for lp, s, j in LG:
                lp.rotation_euler = (0, 0, 0.5 * math.sin(ph + (s > 0) * math.pi + j * math.pi))
            for tp, s in T:
                tp.rotation_euler = (0, 0, -0.3 * math.sin(ph))
        else:
            spine.rotation_euler = (0, 0, 0)
            hd.rotation_euler = (0.05 * math.sin(ph), 0, 0.15 * math.sin(ph))
            for lp, s, j in LG:
                lp.rotation_euler = (0, 0, 0)
            for tp, s in T:
                tp.rotation_euler = (0, 0, 0.25 * s * math.sin(ph))
    c.pose = pose
    c.meta = dict(move="scurries")
    return c


# ================================================================ 11 bridge beetle (collision on a shared medium)
def _beetle(parent, loc, rz, shellm, headm):
    p = pivot("beetle", loc, parent, rot=(0, 0, rz))
    blob("bshell", 0.12, shellm, p, loc=(0, 0.02, 0.085), scale=(1, 1.15, 0.78),
         deform=lambda q: Vector((q.x, q.y, max(q.z, -0.35))), seg=30, rings=20)
    tube("seam", [V(0, -0.1, 0.16), V(0, 0.03, 0.178), V(0, 0.15, 0.13)], [0.006], mat("#5a1a24", kind='flat', line=False), p,
         seg=5, sub=3)
    blob("bhead", 0.062, headm, p, loc=(0, -0.13, 0.075), scale=(1.1, 0.8, 0.85), seg=18, rings=12)
    for s in (-1, 1):
        eye(p, (s * 0.032, -0.168, 0.09), 0.025, iris="#2a1a10", rot=(0, 0, -s * 0.3))
        blush(p, (s * 0.048, -0.17, 0.058), 0.012)
        tube("bant", [V(s * 0.02, -0.15, 0.12), V(s * 0.05, -0.2, 0.2), V(s * 0.07, -0.19, 0.24)], [0.005], headm, p, seg=5, sub=2,
             line=False)
        ellipsoid("bantb", 0.015, headm, p, loc=(s * 0.07, -0.19, 0.245), seg=8, rings=6)
    legs = []
    for s in (-1, 1):
        for j, y in enumerate((-0.07, 0.0, 0.07)):
            lp = pivot("bl", (s * 0.08, y, 0.045), p)
            tube("bleg", [V(0, 0, 0), V(s * 0.05, (j - 1) * 0.02, 0.005), V(s * 0.07, (j - 1) * 0.03, -0.045)], [0.009], headm, lp,
                 seg=5, sub=2, line=False)
            legs.append((lp, s, j))
    return p, legs


def bridge_beetle():
    c = C("wc_bridge_beetle")
    shellm = mat("#d8423a", pat='dots', color2="#3a6ad8", P=dict(nu=6, fv=11, rad=0.2), kind='soft', var=0.08, rim=0.8)
    headm = mat("#2e2c48", kind='soft', rim=0.7)
    A, LA = _beetle(c.body, (-0.15, 0.0, 0), 0.35, shellm, headm)
    B, LB = _beetle(c.body, (0.15, 0.02, 0), -0.35, shellm, headm)
    spark = [star4("spark", c.body, (0, -0.16, 0.24), 0.06, glow("#fff2a0", 3.0)),
             ellipsoid("sparkhalo", 0.08, glow("#fff6c0", 1.3, alpha=0.18, soft=True), c.body, loc=(0, -0.16, 0.24), seg=10, rings=8)]

    def pose(anim, i, n):
        ph = TAU * i / n
        if anim == 'walk':
            set_hide(spark, True)
            A.location.x, B.location.x = -0.15, 0.15
            for legs, o in ((LA, 0), (LB, math.pi)):
                for lp, s, j in legs:
                    lp.rotation_euler = (0, 0, 0.45 * math.sin(2 * ph + o + j * math.pi + (s > 0) * math.pi))
            A.location.z = 0.006 * abs(math.sin(2 * ph))
            B.location.z = 0.006 * abs(math.cos(2 * ph))
        else:
            d = 0.035 * math.sin(ph)
            A.location.x, B.location.x = -0.15 + d, 0.15 - d
            A.location.z = B.location.z = 0
            for legs in (LA, LB):
                for lp, s, j in legs:
                    lp.rotation_euler = (0, 0, 0.1 * math.sin(ph + j))
            set_hide(spark, i != 1)
    c.pose = pose
    c.meta = dict(move="walks")
    return c


# ================================================================ 12 door mouse (port)
def door_mouse():
    c = C("wc_door_mouse")
    b = pivot("b", parent=c.body)
    fur = mat("#a6a4b6", pat='fur', P=dict(scale=90), kind='soft', var=0.12, rim=0.6)
    coat = mat("#2f7a72", pat='weave', kind='cloth', rim=0.6)
    coat2 = mat("#24605a", kind='cloth', rim=0.5)
    pink = mat("#f2a8b8", kind='soft', rim=0.3)
    gold = mat("#f2c24e", metal=True, rim=0.9)
    blob("coat", 0.12, coat, b, loc=(0, 0.02, 0.17), scale=(1.0, 0.92, 1.15),
         deform=lambda p: Vector((p.x * (1 + 0.18 * max(0, -p.z)), p.y * (1 + 0.18 * max(0, -p.z)), p.z)), seg=28, rings=18)
    ellipsoid("vest", 0.07, mat("#f2e6cc", kind='cloth'), b, loc=(0, -0.075, 0.18), scale=(0.62, 0.45, 1.15), seg=18, rings=12)
    for z in (0.21, 0.15):
        ellipsoid("btn", 0.011, gold, b, loc=(0, -0.11, z), seg=8, rings=6)
    tube("collar", ring_pts((0, 0.01, 0.285), 0.075, 0.07, n=24), [0.02], coat2, b, seg=8, sub=1)
    hd = pivot("h", (0, -0.02, 0.37), b)
    blob("mhead", 0.1, fur, hd, scale=(1.0, 1.05, 0.95), deform=lambda p: Vector((p.x, p.y - 0.35 * max(0, -p.y) ** 2, p.z)),
         seg=26, rings=18)
    ellipsoid("mnose", 0.018, pink, hd, loc=(0, -0.14, -0.01), seg=8, rings=6)
    EA = {}
    for s in (-1, 1):
        eye(hd, (s * 0.046, -0.078, 0.03), 0.03, iris="#2a1a2a", rot=(0, 0, -s * 0.4))
        blush(hd, (s * 0.06, -0.09, -0.02), 0.016)
        ep = pivot("ear", (s * 0.08, 0.01, 0.08), hd, rot=(0.15, s * 0.5, 0))
        ellipsoid("mear", 0.07, fur, ep, scale=(1, 0.25, 1), seg=18, rings=10)
        ellipsoid("mearin", 0.05, pink, ep, loc=(0, -0.012, 0), scale=(1, 0.2, 1), seg=14, rings=8)
        EA[s] = ep
        for k in (-1, 1):
            tube("whisk", [V(s * 0.03, -0.13, -0.015 + 0.008 * k), V(s * 0.12, -0.14, -0.01 + 0.025 * k)], [0.0025],
                 mat("#fbf4ea", kind='flat'), hd, seg=4, sub=1, line=False)
        tube("arm", [V(s * 0.1, -0.02, 0.25), V(s * 0.12, -0.06, 0.18), V(s * 0.105, -0.085, 0.14)], [0.026, 0.022], coat, b,
             seg=8, sub=2)
        ellipsoid("hand", 0.02, fur, b, loc=(s * 0.1, -0.095, 0.125), seg=8, rings=6)
    F = {}
    for s in (-1, 1):
        F[s] = blob("foot", 0.04, pink, b, loc=(s * 0.05, -0.06, 0.018), scale=(0.8, 1.5, 0.45), seg=12, rings=8)
    tail = pivot("tail", (0, 0.11, 0.06), b)
    tube("mtail", [V(0, 0, 0), V(0.05, 0.12, -0.04), V(0.12, 0.2, -0.03), V(0.15, 0.18, 0.08)], [0.013, 0.01, 0.007, 0.004], pink,
         tail, seg=6, sub=4)
    # a ring of tiny keys: many doors, one key each (ports)
    kc = V(0, -0.118, 0.255)
    tube("keyring", ring_pts(kc, 0.03, 0.03, n=18, axis_b=(0, 0, 1)), [0.0045], gold, b, seg=5, sub=1, line=False)
    for k, (cl, a) in enumerate((("#35d3b0", -0.6), ("#e8604a", 0.0), ("#f2c24e", 0.6))):
        kp = pivot("key", kc + V(math.sin(a) * 0.03, -0.006, -0.03), b, rot=(0, a * 0.6, 0))
        ellipsoid("kbow", 0.014, mat(cl, kind='soft', rim=0.6), kp, loc=(0, 0, 0.0), scale=(1, 0.4, 1), seg=10, rings=6)
        box("kshaft", (0.007, 0.006, 0.034), gold, kp, loc=(0, 0, -0.026))
        box("kbit", (0.012, 0.006, 0.006), gold, kp, loc=(0.006, 0, -0.04))

    def pose(anim, i, n):
        ph = TAU * i / n
        if anim == 'walk':
            b.rotation_euler = (0, 0.12 * math.sin(ph), 0)
            b.location.z = 0.025 * abs(math.sin(ph))
            for s, f in F.items():
                f.location.y = -0.06 + 0.05 * math.sin(ph) * s
            tail.rotation_euler = (0, 0, 0.25 * math.sin(ph))
            for s, ep in EA.items():
                ep.rotation_euler = (0.15, s * 0.5, 0)
        else:
            b.rotation_euler = (0, 0, 0)
            b.location.z = 0
            b.scale = (1, 1, 1 + 0.02 * math.sin(ph))
            for s, f in F.items():
                f.location.y = -0.06
            tail.rotation_euler = (0, 0, 0.3 * math.sin(ph))
            for s, ep in EA.items():
                ep.rotation_euler = (0.15 + (0.3 if (i == 2 and s == -1) else 0), s * 0.5, 0)
            hd.rotation_euler = (0, 0, 0.1 * math.sin(ph))
    c.pose = pose
    c.meta = dict(move="waddles")
    return c


# ================================================================ legend: glass stag (optical fiber)
def glass_stag():
    c = C("wc_glass_stag")
    fur = mat("#f4f0ea", pat='fur', P=dict(scale=30), kind='soft', var=0.12, rim=0.8)
    pale = mat("#dde6f6", pat='wool', P=dict(scale=26), kind='soft', var=0.15, bump=0.4, rim=0.8)
    hoof = mat("#a8d8e8", metal=True, rim=0.8)
    b = pivot("b", parent=c.body)
    bz = 0.95
    torso = pivot("torso", parent=b)
    blob("sbody", 0.55, fur, torso, loc=(0, 0.12, bz + 0.3), scale=(0.58, 1.3, 0.62),
         deform=lambda p: Vector((p.x, p.y, p.z * (1 + 0.12 * max(0, -p.y)))), seg=40, rings=28)
    blob("schest", 0.34, fur, torso, loc=(0, -0.42, bz + 0.34), scale=(0.88, 0.9, 1.05), seg=32, rings=20)
    blob("ruff", 0.22, pale, torso, loc=(0, -0.58, bz + 0.62), scale=(0.95, 0.7, 1.2), seg=28, rings=18)
    tube("sneck", [V(0, -0.45, bz + 0.45), V(0, -0.6, bz + 0.8), V(0, -0.7, bz + 1.08)], [0.24, 0.18, 0.15], fur, torso,
         seg=20, sub=3)
    hd = pivot("h", (0, -0.75, bz + 1.17), b)
    blob("shead", 0.2, fur, hd, scale=(0.8, 1.15, 0.85), seg=32, rings=22)
    blob("ssnout", 0.12, pale, hd, loc=(0, -0.2, -0.075), scale=(0.75, 1.2, 0.7), seg=24, rings=14)
    ellipsoid("snose", 0.04, mat("#6a7a9a", kind='soft'), hd, loc=(0, -0.33, -0.055), scale=(1.2, 0.7, 0.8), seg=10, rings=8)
    for s in (-1, 1):
        eye(hd, (s * 0.1, -0.11, 0.04), 0.05, iris="#3a7ac0", rot=(0, 0, -s * 0.75))
        blush(hd, (s * 0.11, -0.2, -0.04), 0.035)
        ep = pivot("ear", (s * 0.14, 0.05, 0.1), hd, rot=(0.25, s * 1.15, 0))
        blob("sear", 0.1, fur, ep, loc=(0, 0, 0.09), scale=(0.5, 0.25, 1.15), seg=14, rings=10)
        ellipsoid("searin", 0.07, mat("#e8c8e0", kind='soft'), ep, loc=(0, -0.02, 0.09), scale=(0.4, 0.15, 1.1), seg=10, rings=6)
    top = bz + 0.15
    for (x, y, hind) in ((0.17, -0.45, False), (-0.17, -0.45, False), (0.17, 0.62, True), (-0.17, 0.62, True)):
        lp = pivot("sleg", (x, y, top), b)
        blob("thigh", 0.2 if hind else 0.16, fur, lp, loc=(0, 0.02 if hind else 0, -0.05), scale=(0.55, 0.95, 1.35), seg=20, rings=14)
        kz = 0.05 if hind else -0.04
        tube("shank", [V(0, 0, -0.1), V(0, kz, -0.5), V(0, kz * 0.3, -0.8), V(0, -0.01, -top + 0.09)],
             [0.1, 0.06, 0.045, 0.042], fur, lp, seg=12, sub=3)
        blob("fetlock", 0.05, pale, lp, loc=(0, -0.01, -top + 0.13), scale=(1, 1, 1.1), seg=12, rings=8)
        ellipsoid("hoof", 0.058, hoof, lp, loc=(0, -0.025, -top + 0.04), scale=(1, 1.25, 0.75), seg=14, rings=8)
    blob("stail", 0.08, pale, b, loc=(0, 0.82, bz + 0.48), scale=(0.8, 0.7, 1.2), seg=14, rings=10)
    # glass antlers: a translucent shell with a bright light core, and pulses of light travelling along them
    glass = glow("#6fdcff", 1.5, alpha=0.62)
    core = glow("#eaffff", 3.5)
    branches = []
    for s in (-1, 1):
        main = [V(s * 0.1, 0.02, 0.15), V(s * 0.27, 0.08, 0.45), V(s * 0.42, 0.18, 0.78), V(s * 0.47, 0.32, 1.08), V(s * 0.41, 0.42, 1.3)]
        tines = [[V(s * 0.21, 0.05, 0.32), V(s * 0.26, -0.1, 0.46), V(s * 0.27, -0.2, 0.6)],
                 [V(s * 0.37, 0.15, 0.68), V(s * 0.55, 0.08, 0.86), V(s * 0.66, 0.07, 1.02)],
                 [V(s * 0.45, 0.27, 0.98), V(s * 0.6, 0.3, 1.14), V(s * 0.66, 0.34, 1.3)],
                 [V(s * 0.44, 0.24, 0.92), V(s * 0.32, 0.26, 1.08), V(s * 0.27, 0.3, 1.22)]]
        tube("antler", main, [0.05, 0.042, 0.033, 0.024, 0.012], glass, hd, seg=12, sub=4)
        tube("acore", main, [0.016, 0.013, 0.01, 0.007, 0.003], core, hd, seg=6, sub=4)
        branches.append(main)
        for t in tines:
            tube("tine", t, [0.03, 0.022, 0.01], glass, hd, seg=10, sub=3)
            tube("tcore", t, [0.009, 0.006, 0.003], core, hd, seg=5, sub=3)
            branches.append(t)

    def along(pts, t):
        seglen = [(pts[k + 1] - pts[k]).length for k in range(len(pts) - 1)]
        tot = sum(seglen)
        d = t * tot
        for k, sl in enumerate(seglen):
            if d <= sl or k == len(seglen) - 1:
                return pts[k].lerp(pts[k + 1], min(1, d / sl))
            d -= sl
    beadm = glow("#ffffff", 6.0)
    beadh = glow("#9ff0ff", 2.0, alpha=0.45, soft=True)
    sets = []
    for k in range(4):
        objs = []
        for br in branches:
            p = along(br, (k + 0.5) / 4)
            objs.append(ellipsoid("bead", 0.022, beadm, hd, loc=p, seg=8, rings=6))
            objs.append(ellipsoid("beadh", 0.06, beadh, hd, loc=p, seg=8, rings=6))
        sets.append(objs)
    # a few motes of old light around it
    rnd = random.Random(11)
    for k in range(9):
        ellipsoid("mote", rnd.uniform(0.012, 0.024), glow(rnd.choice(["#dffcff", "#fff4c8"]), 3.0), c.body,
                  loc=(rnd.uniform(-0.55, 0.55), rnd.uniform(-0.9, 0.8), rnd.uniform(0.4, 2.2)), seg=6, rings=4)

    def pose(anim, i, n):
        ph = TAU * i / n
        torso.scale = (1 + 0.012 * math.sin(ph), 1, 1 + 0.012 * math.sin(ph))
        hd.rotation_euler = (0.03 * math.sin(ph), 0, 0.04 * math.sin(ph))
        for k, objs in enumerate(sets):
            set_hide(objs, k != i)
    c.pose = pose
    c.meta = dict(legendary=True)
    return c


# ================================================================ legend: path oak (alternate paths)
def path_oak():
    c = C("wc_path_oak")
    bark = mat("#86603e", pat='wood', P=dict(nu=14), var=0.3, bump=0.8, rim=0.6)
    bark2 = mat("#74533a", pat='wood', P=dict(nu=10), var=0.3, bump=0.8, rim=0.6)
    moss = mat("#7a9a4a", pat='wool', P=dict(scale=30), var=0.3, bump=0.6)
    pathm = mat("#f4e2b8", pat='noise', P=dict(scale=60), kind='soft', var=0.12, rim=0.5)
    T = pivot("trunk", parent=c.body)
    loft("trunk", [(0.1, 0.6, 0.56), (0.5, 0.5, 0.47), (1.4, 0.45, 0.43), (2.05, 0.5, 0.47), (2.35, 0.62, 0.56)], bark, T, seg=40,
         cap_top=True, folds=lambda a, t: 1 + 0.045 * math.sin(9 * a + 2 * t))
    # roots = feet
    R = {}
    for k, az in enumerate((-60, -120, 20, 160, 90)):
        a = math.radians(az)
        rp = pivot("root", (0, 0, 0), T)
        tube("rootT", [V(0.4 * math.cos(a), 0.4 * math.sin(a), 0.55), V(0.72 * math.cos(a), 0.72 * math.sin(a), 0.18),
                       V(0.98 * math.cos(a), 0.98 * math.sin(a), 0.06)], [0.2, 0.14, 0.1], bark2, rp, seg=14, sub=3)
        blob("toe", 0.11, bark2, rp, loc=(1.0 * math.cos(a), 1.0 * math.sin(a), 0.06), scale=(1.2, 1.2, 0.55), seg=16, rings=10)
        R[az] = rp
    blob("mossroot", 0.22, moss, T, loc=(0.55, 0.3, 0.2), scale=(1.2, 1.0, 0.45), seg=20, rings=12)
    blob("mossroot2", 0.18, moss, T, loc=(-0.6, -0.1, 0.18), scale=(1.1, 1.0, 0.45), seg=20, rings=12)
    # calm face in the trunk
    F = pivot("face", parent=T)
    for s in (-1, 1):
        closed_eye(F, (s * 0.17, -0.47, 1.48), 0.085, color="#3a2418", up=False)
        tube("brow", [V(s * 0.08, -0.465, 1.6), V(s * 0.17, -0.47, 1.64), V(s * 0.26, -0.45, 1.6)], [0.03, 0.035, 0.02], moss, F,
             seg=8, sub=3)
        blush(F, (s * 0.25, -0.44, 1.32), 0.05)
    blob("knotnose", 0.07, bark2, F, loc=(0, -0.48, 1.36), scale=(0.9, 0.8, 1.2), seg=16, rings=10)
    smile(F, (0, -0.475, 1.2), 0.11, color="#3a2418", curve=0.35)
    # branches that are paths, each to a canopy and a village light
    leaves = ["#e8862e", "#d8542e", "#f0b840", "#c8683a", "#e89a3a", "#9ab040"]
    rnd = random.Random(4)
    clusters = []
    specs = [(-15, 1.35, 3.2), (35, 1.25, 3.55), (80, 0.95, 3.75), (115, 1.15, 3.5), (160, 1.3, 3.25), (205, 1.3, 3.05)]
    for k, (az, rr, zt) in enumerate(specs):
        a = math.radians(az)
        pts = [V(0.25 * math.cos(a), 0.25 * math.sin(a), 2.15), V(0.7 * rr * math.cos(a), 0.7 * rr * math.sin(a), 2.55 + 0.1 * (k % 2)),
               V(rr * math.cos(a), rr * math.sin(a), zt - 0.3)]
        tube("branch", pts, [0.2, 0.12, 0.07], bark, T, seg=12, sub=4)
        tube("path", [p + V(0, 0, r * 0.95) for p, r in zip(pts, (0.2, 0.12, 0.07))], [0.06, 0.045, 0.03], pathm, T, seg=8, sub=4,
             flat=1.0)
        cp = pivot("canopy", (rr * math.cos(a), rr * math.sin(a), zt), T)
        lm = mat(leaves[k % len(leaves)], pat='wool', P=dict(scale=14), kind='soft', var=0.22, bump=0.6, rim=0.8)
        lm2 = mat(lighter(leaves[k % len(leaves)], 0.18), pat='wool', P=dict(scale=14), kind='soft',
                  var=0.2, bump=0.6, rim=0.8)
        for j in range(6):
            aa = rnd.uniform(0, TAU)
            blob("leafy", rnd.uniform(0.2, 0.3), lm if j % 2 else lm2, cp,
                 loc=(0.28 * math.cos(aa), 0.25 * math.sin(aa), rnd.uniform(-0.08, 0.15)), seg=18, rings=12)
        blob("leafcore", 0.36, lm, cp, loc=(0, 0, 0.05), scale=(1.05, 1.0, 0.8), seg=24, rings=16)
        # a little village light hanging under each canopy
        tube("cord", [V(0, -0.15, -0.25), V(0, -0.2, -0.42)], [0.008], mat("#4a3a2a", kind='flat'), cp, seg=4, sub=1, line=False)
        ellipsoid("lamp", 0.045, glow("#ffd27a", 3.0), cp, loc=(0, -0.2, -0.46), seg=10, rings=8)
        ellipsoid("lamph", 0.13, glow("#ffd27a", 1.3, alpha=0.16, soft=True), cp, loc=(0, -0.2, -0.46), seg=10, rings=8)
        clusters.append((cp, k))
    blob("crown", 0.5, mat("#e89a3a", pat='wool', P=dict(scale=14), kind='soft', var=0.2, bump=0.6, rim=0.8), T,
         loc=(0, 0.35, 3.3), scale=(1.2, 1.0, 0.7), seg=28, rings=18)
    # a branch that was cut, and the new shoot that grew beside it (healed, not hurt)
    a = math.radians(-110)
    tube("stub", [V(0.38 * math.cos(a), 0.38 * math.sin(a), 1.95), V(0.62 * math.cos(a), 0.62 * math.sin(a), 2.08)], [0.12, 0.1],
         bark, T, seg=12, sub=1)
    sp = V(0.66 * math.cos(a), 0.66 * math.sin(a), 2.1)
    cyl("cut", 0.1, 0.1, 0.02, mat("#f0d8a8", pat='spiral', color2="#d8b880", P=dict(nu=1, fv=80)), T, loc=sp,
        rot=(math.radians(90) + 0.5, 0, a + math.pi / 2))
    tube("shoot", [V(0.5 * math.cos(a), 0.5 * math.sin(a), 2.05), V(0.62 * math.cos(a), 0.62 * math.sin(a), 2.3),
                   V(0.66 * math.cos(a), 0.66 * math.sin(a), 2.48)], [0.04, 0.025, 0.012], mat("#8ac04a", kind='soft'), T, seg=8, sub=3)
    for s in (-1, 1):
        ellipsoid("sleaf", 0.07, mat("#9ad85a", kind='soft', rim=0.6), T,
                  loc=(0.66 * math.cos(a) + s * 0.06, 0.66 * math.sin(a), 2.5), scale=(1, 0.4, 0.45), rot=(0, -s * 0.5, 0),
                  seg=12, rings=8)
    # falling leaves
    fall = []
    for k in range(3):
        fall.append(ellipsoid("fall", 0.05, mat(leaves[k], kind='soft', rim=0.6), c.body, loc=(0, 0, 0), scale=(1, 0.5, 0.3),
                              seg=10, rings=6))

    def pose(anim, i, n):
        ph = TAU * i / n
        T.scale = (1 + 0.008 * math.sin(ph), 1 + 0.008 * math.sin(ph), 1)
        for cp, k in clusters:
            cp.rotation_euler = (0.04 * math.sin(ph + k), 0.04 * math.cos(ph + k), 0)
        R[-60].location.z = 0.05 if i == 2 else 0.0
        for k, lf in enumerate(fall):
            t = ((i + k * 1.3) % 4) / 4
            lf.location = (-1.1 + 1.0 * k + 0.12 * math.sin(t * 6), -0.6 + 0.2 * k, 3.0 - 2.4 * t)
            lf.rotation_euler = (t * 3, t * 2, k)
    c.pose = pose
    c.meta = dict(legendary=True)
    return c


SMALL = dict(wc_address_turtle=address_turtle, wc_bit_rabbit=bit_rabbit, wc_gateway_doe=gateway_doe,
             wc_queue_squirrel=queue_squirrel, wc_stream_fish=stream_fish, wc_thunder_frog=thunder_frog,
             wc_handshake_dove=handshake_dove, wc_cocoon_worm=cocoon_worm, wc_count_butterfly=count_butterfly,
             wc_backup_lizard=backup_lizard, wc_bridge_beetle=bridge_beetle, wc_door_mouse=door_mouse)
# name: (fn, cell, anchor, ppu, yaw)
LEGEND = dict(wc_glass_stag=(glass_stag, (384, 384), (192, 360), 92.0, 40),
              wc_path_oak=(path_oak, (384, 384), (192, 338), 74.0, 0))


def main():
    a = args()
    which, rawdir = a[0], a[1]
    if which == 'all':
        names = list(SMALL) + list(LEGEND)
    elif which == 'small':
        names = list(SMALL)
    elif which == 'legend':
        names = list(LEGEND)
    else:
        names = [n if n.startswith("wc_") else "wc_" + n for n in which.split(',')]
    for nm in names:
        t0 = time.time()
        od = os.path.join(rawdir, "creatures", nm)
        os.makedirs(od, exist_ok=True)
        if nm in SMALL:
            c = build(SMALL[nm], line_t=0.008)
            add_lines()
            cam = sprite_camera(128, 128, (64, 110), ppu=CPPU, ssaa=4)
            for anim, n in (('idle', 4), ('walk', 6)):
                for dn, deg in CDIRS:
                    for i in range(n):
                        c.pose(anim, i, n)
                        c.root.rotation_euler = (0, 0, math.radians(deg))
                        bpy.context.view_layer.update()
                        render_to(os.path.join(od, f"{anim}_{dn}_{i}.png"))
            bpy.data.objects.remove(cam, do_unlink=True)
            codex(c, od, 1)
            m = dict(c.meta)
        else:
            fn, cell, anchor, ppu, yaw = LEGEND[nm]
            c = build(fn, line_t=0.016)
            add_lines()
            cam = sprite_camera(cell[0], cell[1], anchor, ppu=ppu, ssaa=3)
            for i in range(4):
                c.pose('idle', i, 4)
                c.root.rotation_euler = (0, 0, math.radians(yaw))
                bpy.context.view_layer.update()
                render_to(os.path.join(od, f"idle_S_{i}.png"))
            bpy.data.objects.remove(cam, do_unlink=True)
            codex(c, od, 1)
            m = dict(c.meta, cell=list(cell), anchor=list(anchor))
        with open(os.path.join(od, "meta.json"), "w", encoding="utf8") as f:
            json.dump(m, f, ensure_ascii=False, indent=1)
        print(f"CREATURE {nm} {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
