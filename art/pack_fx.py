"""Atmosphere FX sprites, generated procedurally with numpy + Pillow (stylised, soft, small files).

python art/pack_env.py fx art/_raw   ->  public/assets/fx/fx.png + fx.json  (Phaser atlas; 'anims' for smoke + star)
Sprites: cloud_1..5, smoke_0..9, sun, moon, star_0..3, godray, mote_warm, mote_white, spark_0..3, mist_1..3, leaf_green/orange/red.
"""
import json
import math
import os

import numpy as np
from PIL import Image, ImageFilter

from pack_env import OUT, shelf_pack, frame_json, trim

SS = 2   # supersample for smoother shapes


def smooth(x, a=0.0, b=1.0):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def grid(w, h):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    return x, y


def to_img(rgb, a, size=None):
    arr = np.dstack([np.clip(rgb, 0, 1), np.clip(a, 0, 1)])
    im = Image.fromarray((arr * 255).astype(np.uint8), "RGBA")
    if size:
        im = im.resize(size, Image.LANCZOS)
    return im


def hexc(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], dtype=np.float32)


def blobs_density(w, h, blobs):
    x, y = grid(w, h)
    d = np.zeros((h, w), np.float32)
    for (cx, cy, r) in blobs:
        dd = ((x - cx) ** 2 + (y - cy) ** 2) / (r * r)
        d += np.exp(-dd * 1.6)
    return d


def cloud(w, h, seed, lit="#fff1dc", mid="#f4c8c8", shade="#7a78c4"):
    """Layered stylised cloud: flat base, puffy top; lit top, violet-blue underside, rim light."""
    rnd = np.random.RandomState(seed)
    W, H = w * SS, h * SS
    blobs = []
    n = rnd.randint(7, 11)
    for i in range(n):
        t = (i + 0.5) / n
        cx = W * (0.14 + 0.72 * t + rnd.uniform(-0.03, 0.03))
        bump = math.sin(math.pi * t) ** 0.8
        r = H * (0.17 + 0.2 * bump * rnd.uniform(0.75, 1.15))
        cy = H * 0.72 - r * rnd.uniform(0.5, 0.95)
        blobs.append((cx, cy, r))
    blobs += [(W * (0.18 + 0.0833 * k), H * 0.70, H * 0.2) for k in range(10)]   # wide flat underside
    d = blobs_density(W, H, blobs)
    a = smooth(d, 0.55, 0.85)
    a[int(H * 0.80):, :] *= np.linspace(1, 0, H - int(H * 0.80))[:, None] ** 0.6       # flat bottom
    ds = np.array(Image.fromarray((np.clip(d, 0, 3) / 3 * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(H * 0.11)), np.float32) / 255 * 3
    gy, gx = np.gradient(ds)
    light = np.clip(0.42 + gy * 30 + gx * 14, 0, 1)                               # light from upper left
    yy = np.linspace(0, 1, H)[:, None]
    light = np.clip(light * 0.6 + (1 - yy) * 0.55, 0, 1)
    # three soft toon steps
    s = smooth(light, 0.25, 0.5) * 0.55 + smooth(light, 0.5, 0.7) * 0.45
    col = hexc(shade)[None, None] * (1 - s[..., None]) + hexc(mid)[None, None] * s[..., None]
    s2 = smooth(light, 0.62, 0.72)[..., None]
    col = col * (1 - s2) + hexc(lit)[None, None] * s2
    rim = smooth(a, 0.0, 0.25) * (1 - smooth(a, 0.35, 0.8))
    col = col + rim[..., None] * np.array([0.10, 0.08, 0.06], np.float32)
    return to_img(col, a * 0.97, (w, h))


def smoke_frames(n=10, size=96):
    out = []
    rnd = np.random.RandomState(7)
    base = [(rnd.uniform(-0.2, 0.2), rnd.uniform(0.0, 0.2), rnd.uniform(0.7, 1.1), rnd.uniform(-1, 1)) for _ in range(12)]
    for f in range(n):
        t = f / (n - 1)
        W = size * SS
        x, y = grid(W, W)
        d = np.zeros((W, W), np.float32)
        for (ox, oy, k, sw) in base:
            cx = W * (0.4 + 0.12 * t + ox * 1.1 * t + 0.06 * sw * math.sin(t * 4))
            cy = W * (0.82 - 0.58 * t - oy * 0.9 * t)
            r = W * (0.06 + 0.16 * t * k)
            d += np.exp(-(((x - cx) ** 2 + (y - cy) ** 2) / (r * r)) * 1.7)
        a = smooth(d, 0.3, 0.9) * (smooth(1 - t, 0.0, 0.4) ** 1.0) * 0.8 * smooth(t, 0.0, 0.08)
        dd = np.array(Image.fromarray((np.clip(d, 0, 3) / 3 * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(W * 0.07)), np.float32) / 255 * 3
        gy, gx = np.gradient(dd)
        light = np.clip(0.45 + gy * 26 + gx * 12, 0, 1)
        s = (smooth(light, 0.1, 0.9) * 0.75)[..., None]
        col = hexc("#7d789e") * (1 - s) + hexc("#d8d0e4") * s
        out.append(to_img(col, a, (size, size)))
    return out


def sun(size=256):
    W = size * SS
    x, y = grid(W, W)
    r = np.hypot(x - W / 2, y - W / 2) / (W / 2)
    halo = np.exp(-(r * 2.2) ** 2) * 0.55 + np.exp(-(r * 5) ** 2) * 0.5
    disc = 1 - smooth(r, 0.2, 0.225)
    ang = np.arctan2(y - W / 2, x - W / 2)
    rays = (0.5 + 0.5 * np.cos(ang * 12)) ** 3 * np.exp(-(r * 1.6) ** 2) * 0.25
    a = np.clip(halo + rays, 0, 1) * (1 - disc) + disc
    col = hexc("#ffc864")[None, None] * (1 - disc[..., None]) + hexc("#fff6d8")[None, None] * disc[..., None]
    col = col + rays[..., None] * 0.2
    return to_img(col, a * smooth(1 - r, 0, 0.08), (size, size))


def moon(size=160):
    W = size * SS
    x, y = grid(W, W)
    c = W / 2
    r = np.hypot(x - c, y - c) / (W / 2)
    halo = np.exp(-(r * 2.0) ** 2) * 0.5
    R0 = 0.42
    m1 = 1 - smooth(np.hypot(x - c, y - c) / (W / 2), R0 - 0.012, R0 + 0.012)
    cut = 1 - smooth(np.hypot(x - c - W * 0.16, y - c + W * 0.06) / (W / 2), R0 * 0.92 - 0.012, R0 * 0.92 + 0.012)
    cres = np.clip(m1 - cut, 0, 1)
    nz = (np.sin(x * 0.07) * np.cos(y * 0.09) * 0.5 + 0.5) * 0.12
    col = hexc("#fff3c8")[None, None] * (1 - nz[..., None]) + hexc("#e8d8a0")[None, None] * nz[..., None]
    col = col * cres[..., None] + hexc("#b8c8ff")[None, None] * (1 - cres[..., None])
    a = np.clip(halo * (1 - cres) + cres, 0, 1) * smooth(1 - r, 0, 0.1)
    return to_img(col, a, (size, size))


def star(size=48, k=1.0):
    W = size * SS
    x, y = grid(W, W)
    dx, dy = np.abs(x - W / 2) / (W / 2), np.abs(y - W / 2) / (W / 2)
    r = np.hypot(dx, dy)
    cross = np.exp(-(dx * 18 / k) ** 1) * np.exp(-(dy * 1.4) ** 2) + np.exp(-(dy * 18 / k) ** 1) * np.exp(-(dx * 1.4) ** 2)
    diag = np.exp(-(np.abs(dx - dy) * 20)) * np.exp(-(r * 2.2) ** 2) * 0.35
    core = np.exp(-(r * 6) ** 2)
    a = np.clip(cross * 0.9 * k + diag + core, 0, 1) * smooth(1 - r, 0, 0.15)
    col = hexc("#fffbe8")[None, None] * np.ones((W, W, 1), np.float32)
    col = col * (0.75 + 0.25 * core[..., None]) + hexc("#bcd4ff")[None, None] * (1 - core[..., None]) * 0.25
    return to_img(col, a, (size, size))


def godray(w=192, h=448):
    W, H = w * SS, h * SS
    x, y = grid(W, H)
    t = y / H
    half = (0.10 + 0.40 * t) * W / 2
    cx = W * (0.5 - 0.12 * t)
    dx = np.abs(x - cx) / np.maximum(half, 1)
    edge = 1 - smooth(dx, 0.55, 1.0)
    streak = 0.65 + 0.35 * np.sin(x * 0.05 + np.sin(y * 0.01) * 3) * np.sin(x * 0.021 + 1.3)
    a = edge * streak * (1 - t) ** 1.2 * smooth(t, 0.0, 0.04) * 0.55
    col = hexc("#ffe2a8")[None, None] * np.ones((H, W, 1), np.float32)
    return to_img(col, a, (w, h))


def mote(size=32, color="#ffd878"):
    W = size * SS
    x, y = grid(W, W)
    r = np.hypot(x - W / 2, y - W / 2) / (W / 2)
    a = np.exp(-(r * 3.0) ** 2) * 0.55 + np.exp(-(r * 7.0) ** 2) * 0.6
    col = hexc(color)[None, None] * np.ones((W, W, 1), np.float32)
    col = col * (1 - np.exp(-(r * 7) ** 2)[..., None]) + np.array([1, 1, 0.95], np.float32) * np.exp(-(r * 7) ** 2)[..., None]
    return to_img(col, np.clip(a, 0, 1) * smooth(1 - r, 0, 0.1), (size, size))


def spark(size=64, rot=0.0):
    """Teal drifting thread-spark: a small curled glowing thread segment with a soft halo."""
    W = size * SS
    x, y = grid(W, W)
    c = W / 2
    ca, sa = math.cos(rot), math.sin(rot)
    u = (x - c) * ca + (y - c) * sa
    v = -(x - c) * sa + (y - c) * ca
    curve = v - 0.18 * (u ** 2) / (W / 2)
    line = np.exp(-(curve / (W * 0.018)) ** 2) * smooth(1 - np.abs(u) / (W * 0.34), 0, 0.5)
    r = np.hypot(x - c, y - c) / (W / 2)
    halo = np.exp(-(r * 2.6) ** 2) * 0.5
    a = np.clip(line + halo * 0.7, 0, 1) * smooth(1 - r, 0, 0.1)
    col = hexc("#35d3b0")[None, None] * (1 - line[..., None]) + hexc("#d8fff4")[None, None] * line[..., None]
    return to_img(col, a, (size, size))


def mist(w, h, seed):
    W, H = w * SS, h * SS
    rnd = np.random.RandomState(seed)
    x, y = grid(W, H)
    d = np.zeros((H, W), np.float32)
    for i in range(6):
        cx, cy = W * rnd.uniform(0.15, 0.85), H * rnd.uniform(0.35, 0.65)
        rx, ry = W * rnd.uniform(0.14, 0.3), H * rnd.uniform(0.12, 0.28)
        d += np.exp(-(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2) * 1.5)
    nz = np.array(Image.fromarray((rnd.rand(H // 8 + 1, W // 8 + 1) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
    a = smooth(d * (0.85 + 0.3 * nz), 0.1, 1.6) * 0.5
    a *= smooth(x / W, 0, 0.1) * smooth(1 - x / W, 0, 0.1) * smooth(y / H, 0, 0.15) * smooth(1 - y / H, 0, 0.15)
    a = np.array(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(H * 0.04)), np.float32) / 255
    col = hexc("#dfe8f8")[None, None] * np.ones((H, W, 1), np.float32)
    return to_img(col, a, (w, h))


def leaf(size, color, dark, rot=0.5):
    W = size * SS
    x, y = grid(W, W)
    c = W / 2
    ca, sa = math.cos(rot), math.sin(rot)
    u = ((x - c) * ca + (y - c) * sa) / (W * 0.42)
    v = (-(x - c) * sa + (y - c) * ca) / (W * 0.42)
    half = 0.55 * np.clip(1 - u ** 2, 0, None) ** 0.8 * (1 - 0.35 * u)
    inside = (np.abs(v) < half) & (np.abs(u) < 1)
    a = inside.astype(np.float32)
    a = np.array(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255
    vein = np.exp(-(v / 0.035) ** 2) * (np.abs(u) < 0.9)
    shade = smooth(v, -0.5, 0.5)[..., None]
    col = hexc(color)[None, None] * (1 - shade * 0.35) + hexc(dark)[None, None] * shade * 0.35
    col = col * (1 - vein[..., None] * 0.35) + hexc("#f3e4a8")[None, None] * vein[..., None] * 0.35
    stem = (np.abs(v) < 0.035) & (u < -0.95) & (u > -1.25)
    a = np.maximum(a, stem.astype(np.float32))
    return to_img(col, a, (size, size))


def pack(raw):
    sprites = []
    for i in range(5):
        w, h = [(320, 144), (256, 120), (384, 160), (224, 110), (288, 136)][i]
        sprites.append((f"cloud_{i + 1}", cloud(w, h, 11 + i * 7)))
    for i, im in enumerate(smoke_frames()):
        sprites.append((f"smoke_{i}", im))
    sprites.append(("sun", sun()))
    sprites.append(("moon", moon()))
    for i, k in enumerate((0.55, 0.85, 1.0, 0.7)):
        sprites.append((f"star_{i}", star(48, k)))
    sprites.append(("godray", godray()))
    sprites.append(("mote_warm", mote(32, "#ffd878")))
    sprites.append(("mote_white", mote(32, "#dff0ff")))
    for i in range(4):
        sprites.append((f"spark_{i}", spark(64, i * 0.5 + 0.3)))
    for i, (w, h) in enumerate([(256, 96), (200, 80), (288, 104)]):
        sprites.append((f"mist_{i + 1}", mist(w, h, 3 + i)))
    for nm, c, d in (("green", "#6cb257", "#2f6b48"), ("orange", "#e0933a", "#a94a30"), ("red", "#c44b3f", "#7a2a3a")):
        sprites.append((f"leaf_{nm}", leaf(40, c, d, 0.6)))
    items = [(n, im, None) for n, im in sprites]
    sheet, pos = shelf_pack(items, 1024)
    path = os.path.join(OUT, "fx", "fx.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path, optimize=True)
    frames = {n: frame_json(n, im, pos[n], (im.width / 2, im.height / 2)) for n, im in sprites}
    frames["smoke_0"]["note"] = "emit at the chimney point; frames grow, drift up-right and fade"
    frames["godray"]["anchor"] = {"x": 0.5, "y": 0.0}
    frames["godray"]["note"] = "anchor at the top (light source end); stretch/tint/alpha in game"
    anims = {"smoke": {"frames": [f"smoke_{i}" for i in range(10)], "frameRate": 8, "repeat": 0},
             "star_twinkle": {"frames": ["star_0", "star_1", "star_2", "star_3", "star_2", "star_1"], "frameRate": 6, "repeat": -1},
             "spark_spin": {"frames": [f"spark_{i}" for i in range(4)], "frameRate": 8, "repeat": -1}}
    json.dump({"frames": frames, "anims": anims,
               "meta": {"app": "too-quiet art pipeline", "image": "fx.png", "format": "RGBA8888", "size": {"w": sheet.width, "h": sheet.height},
                        "scale": "1", "note": "All sprites anchor at centre unless stated. Use blendMode ADD for sun, mote_*, spark_*, godray, star_*; NORMAL for clouds, smoke, mist, leaves. Tint clouds for night (e.g. 0x6a78b8)."}},
              open(os.path.join(OUT, "fx", "fx.json"), "w"), indent=1)
    print(f"fx: {len(frames)} sprites, sheet {sheet.size}, {os.path.getsize(path) / 1024:.0f} KB")
