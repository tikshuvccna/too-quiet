"""Contact sheet for the world-2 atlases -> art/preview_world2.png (true scale on top, enlarged 2x below; facade above truth)."""
import json, os
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "public", "assets")
GREEN, DARK = (96, 120, 84, 255), (58, 66, 84, 255)


def frames_of(folder, pattern_names, truth):
    out = {}
    for fn in os.listdir(os.path.join(A, folder)):
        if fn.endswith(".json") and fn.startswith(pattern_names) and fn.endswith("_truth.json") == truth and "index" not in fn:
            js = json.load(open(os.path.join(A, folder, fn)))
            sh = Image.open(os.path.join(A, folder, js["meta"]["image"])).convert("RGBA")
            for k, f in js["frames"].items():
                r = f["frame"]
                out[k] = (sh.crop((r["x"], r["y"], r["x"] + r["w"], r["y"] + r["h"])), f["anchor"])
    return out


def row(items, bg, gap=16, scale=1):
    ims = []
    for im, an in items:
        if scale != 1:
            im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
        ims.append((im, an))
    if not ims:
        return Image.new("RGBA", (10, 10), bg)
    H = max(i.height for i, _ in ims) + 20
    base = H - 12
    W = sum(i.width + gap for i, _ in ims) + gap
    r = Image.new("RGBA", (W, H), bg)
    x = gap
    for im, an in ims:
        r.alpha_composite(im, (x, base - int(an["y"] * im.height)))
        x += im.width + gap
    return r


def groups(items, maxw, scale):
    rows, cur, w = [], [], 0
    for it in items:
        iw = int(it[0].width * scale) + 16
        if cur and w + iw > maxw:
            rows.append(cur); cur, w = [], 0
        cur.append(it); w += iw
    if cur:
        rows.append(cur)
    return rows


def main():
    order = ["inn", "bell_tower", "tailor", "school", "fisher", "workshop", "library", "observatory", "stories", "farm", "shepherd", "herbs",
             "fairy", "guild", "lighthouse", "great_tower"]
    bf, bt = frames_of("buildings", "buildings2", False), frames_of("buildings", "buildings2", True)
    pf, pt = frames_of("props", "props2", False), frames_of("props", "props2", True)

    def pair_rows(names, F, T, sfx, maxw, scale):
        out = []
        items = [(n, F[n]) for n in names if n in F]
        # group by facade widths
        rows, cur, w = [], [], 0
        for n, it in items:
            iw = int(it[0].width * scale) + 16
            if cur and w + iw > maxw:
                rows.append(cur); cur, w = [], 0
            cur.append(n); w += iw
        if cur:
            rows.append(cur)
        for r in rows:
            out.append(row([F[n] for n in r], GREEN, scale=scale))
            out.append(row([T[n + sfx] for n in r if n + sfx in T], DARK, scale=scale))
        return out

    def save(sheets, path):
        W = max(s.width for s in sheets)
        H = sum(s.height for s in sheets)
        o = Image.new("RGBA", (W, H), (30, 30, 40, 255))
        y = 0
        for s in sheets:
            o.alpha_composite(s, (0, y)); y += s.height
        o.convert("RGB").save(path, optimize=True)
        print(path, o.size)

    main_sheets = pair_rows(order, bf, bt, "_truth", 2400, 1)
    main_sheets += pair_rows(list(pf), pf, pt, "_truth", 2400, 1)
    save(main_sheets, os.path.join(ROOT, "art", "preview_world2.png"))
    save(pair_rows(order, bf, bt, "_truth", 5000, 2) + pair_rows(list(pf), pf, pt, "_truth", 5000, 2), os.path.join(ROOT, "art", "preview_world2_big.png"))


if __name__ == "__main__":
    main()
