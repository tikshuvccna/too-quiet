"""THE HEAD: the great face that peeks from the clouds (puppeteer). 1024x512 sprites.

blender -b --python v2_head.py -- <rawdir>
Writes <rawdir>/head/the_head_<benevolent|truth>_<0|1>.png (frame 1 = slow half-blink). SSAA 2.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector

from v2lib import *


def build(truth):
    reset()
    STATE['truth'] = truth
    STATE['line_t'] = 0.0
    STATE['lines'] = False
    render_setup(samples=48)
    world_and_lights('truth' if truth else 'day')
    rnd = random.Random(11)
    face_c = "#f2e8f4" if not truth else "#c8d2dc"
    cloud = mat(face_c, pat='noise', P=dict(scale=1.6), kind='soft', var=0.1, bump=0.25, rim=0.9)
    cloud2 = mat("#e4dcf0" if not truth else "#aab8c6", pat='noise', P=dict(scale=2.2), kind='soft', var=0.12, bump=0.3, rim=0.9)
    root = pivot("root")
    # vast head (only brow, eyes, upper cheeks show above the cloud bank)
    hd = pivot("head", (0, 0, 2.3), root)
    blob("dome", 3.0, cloud, hd, scale=(1.2, 0.8, 1.0),
         deform=lambda p: Vector((p.x, p.y - 0.12 * math.exp(-((p.z - 0.15) ** 2) / 0.02) * (1 - p.x * p.x), p.z)), seg=64, rings=40)
    for s in (-1, 1):
        blob("browlump", 1.0, cloud, hd, loc=(s * 1.15, -2.2, 1.05), scale=(1.3, 0.5, 0.42), rot=(0, s * 0.07, 0), seg=30, rings=18)
    blob("nose", 0.5, cloud, hd, loc=(0, -2.45, -0.6), scale=(0.9, 0.8, 1.6), seg=28, rings=18)
    eyes = []
    for s in (-1, 1):
        e = pivot("eye", (s * 1.15, -2.25, 0.35), hd)
        sock = ellipsoid("socket", 0.62, mat("#8a80a8" if not truth else "#3a4452", kind='soft', rim=0.2), e,
                         loc=(0, 0.12, 0), scale=(1.15, 0.5, 0.8), seg=28, rings=18)
        ellipsoid("sclera", 0.5, mat("#fffaf0" if not truth else "#1e2830", kind='soft', rim=0.3), e, loc=(0, -0.08, 0),
                  scale=(1.15, 0.5, 0.78), seg=28, rings=18)
        if truth:
            ellipsoid("iris", 0.22, glow("#45e0c8", 2.2), e, loc=(0, -0.3, -0.03), scale=(1, 0.35, 1), seg=20, rings=12)
            ellipsoid("ihalo", 0.5, glow("#45e0c8", 1.2, alpha=0.18, soft=True), e, loc=(0, -0.35, -0.03), seg=16, rings=10)
        else:
            ellipsoid("iris", 0.3, mat("#6a7ad0", kind='soft', rim=0), e, loc=(0, -0.28, -0.04), scale=(1, 0.35, 1), seg=24, rings=14)
            ellipsoid("iris2", 0.22, mat("#9ab0f0", kind='soft', rim=0), e, loc=(0, -0.31, -0.08), scale=(1, 0.3, 1), seg=20, rings=12)
            ellipsoid("pupil", 0.13, mat("#1a1430", kind='flat', rim=0), e, loc=(0, -0.35, -0.03), scale=(1, 0.3, 1), seg=16, rings=10)
            ellipsoid("hl", 0.07, glow("#ffffff", 1.2), e, loc=(-0.12, -0.4, 0.1), seg=10, rings=6)
            ellipsoid("hl2", 0.035, glow("#ffffff", 1.2), e, loc=(0.1, -0.39, -0.12), seg=8, rings=4)
        # heavy, calm upper lid (rotates down for the half-blink)
        lid = pivot("lid", (0, 0.0, 0.0), e)
        blob("lidshell", 0.56, cloud2, lid, scale=(1.18, 0.56, 0.82),
             deform=lambda p: Vector((p.x, p.y, max(p.z, 0.05 + 0.15 * p.x * p.x))), seg=28, rings=18)
        eyes.append(lid)
    # cloud bank hides everything below the cheeks
    for k in range(26):
        x = rnd.uniform(-4.8, 4.8)
        r = rnd.uniform(0.6, 1.1)
        blob("bank", r, cloud2 if k % 3 else cloud, root, loc=(x, -2.4 - rnd.uniform(0, 0.8), 0.9 + rnd.uniform(-0.4, 0.5)),
             scale=(1.3, 0.9, 0.8), seg=24, rings=16)
    # hands at both sides, fingertips down, strings of light
    th = glow("#fff2c0" if not truth else "#7ff3e0", 2.4 if not truth else 3.0)
    for s in (-1, 1):
        hp = pivot("hand", (s * 3.3, -3.6, 2.2), root, rot=(0.25, s * 0.2, 0))
        blob("palm", 0.7, cloud, hp, scale=(0.9, 0.5, 0.75), seg=26, rings=16)
        for f in range(4):
            fx = -0.45 + f * 0.3
            tip = Vector((fx * 0.9, -0.15, -1.15 - 0.12 * (1.5 - abs(f - 1.5))))
            tube("finger", [Vector((fx, -0.1, -0.3)), Vector((fx * 0.95, -0.15, -0.75)), tip], [0.16, 0.14, 0.11], cloud, hp, seg=14, sub=3)
            # the string: falls to the bottom of the frame
            tube("string", [tip, tip + Vector((0.02 * f, 0, -1.5)), tip + Vector((-0.05, 0, -3.2))], [0.018], th, hp, seg=5, sub=3)
            ellipsoid("spark", 0.05, th, hp, loc=tip + Vector((0, 0, -0.1)), seg=8, rings=6)
    if truth:   # threads woven through the face itself
        for k in range(7):
            x = -2.6 + k * 0.85
            tube("facethread", [Vector((x, -2.6, 3.8)), Vector((x + 0.2, -2.9, 2.4)), Vector((x - 0.1, -2.8, 0.6))], [0.025],
                 glow("#7ff3e0", 1.4), root, seg=5, sub=3)
    return eyes


def main():
    rawdir = args()[0]
    od = os.path.join(rawdir, "head")
    os.makedirs(od, exist_ok=True)
    for truth in (False, True):
        lids = build(truth)
        cam = portrait_camera(Vector((0, 0, 2.55)), dist=30, res=2048, elev=4, yaw=0, ortho_scale=12.6)
        sc = bpy.context.scene
        sc.render.resolution_x, sc.render.resolution_y = 2048, 1024
        for fr, ang in ((0, 0.0), (1, 0.55)):
            for lid in lids:
                lid.rotation_euler = (ang, 0, 0)
            render_to(os.path.join(od, f"the_head_{'truth' if truth else 'benevolent'}_{fr}.png"))
        print("HEAD", truth)


main()
