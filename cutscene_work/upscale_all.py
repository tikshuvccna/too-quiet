"""Download the free 720p Upscaled version of every cutscene clip from Flow into cutscene_work/hd/<id>.mp4.

Each Flow video is matched to a local clip by comparing the 360p Original download with our local file (same bytes),
so the order of the tiles does not matter. Resumable: ids are cached in hd/ids.json, finished clips are skipped."""
import hashlib, json, pathlib, sys, tempfile
sys.path.insert(0, r"E:\yt-tikshuv\tools\flow")
from playwright.sync_api import sync_playwright
import flowgen, flow_video as fv

proj = open(r"E:\yt-tikshuv\flow-project.txt").read().strip()
W = pathlib.Path(r"E:\Tikshuv Games\too-quiet\cutscene_work")
HD = W / "hd"
HD.mkdir(exist_ok=True)
local = {hashlib.md5(p.read_bytes()).hexdigest(): p.stem for p in W.glob("*.mp4")}
ids_file = HD / "ids.json"
ids = json.loads(ids_file.read_text()) if ids_file.exists() else []
log = open(HD / "upscale.log", "a", encoding="utf-8")


def L(m):
    print(m, flush=True)
    log.write(m + "\n")
    log.flush()


def open_videos(page):
    page.goto(flowgen.en(proj), wait_until="domcontentloaded")
    page.wait_for_selector(flowgen.PROMPT_BOX, timeout=45000)
    page.wait_for_timeout(3500)


def thumb_id(page, i):
    open_videos(page)
    thumbs = page.locator('img[alt="Generated video thumbnail"]')
    for _ in range(40):
        if thumbs.count() > i:
            break
        page.mouse.move(800, 450)
        page.mouse.wheel(0, 900)
        page.wait_for_timeout(1500)
    if thumbs.count() <= i:
        return None
    thumbs.nth(i).click()
    page.wait_for_url("**/edit/**", timeout=20000)
    return page.url.rstrip("/").rsplit("/", 1)[-1]


with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(user_data_dir=str(flowgen.PROFILE_DIR), headless=False,
        viewport={"width": 1440, "height": 900}, accept_downloads=True,
        args=["--disable-blink-features=AutomationControlled"])
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    # 1) collect the edit ids of the newest tiles (our 30 clips plus a few extras from failed tries)
    i = len(ids)
    while i < 100:
        v = thumb_id(page, i)
        if not v:
            break
        if v not in ids:
            ids.append(v)
        ids_file.write_text(json.dumps(ids))
        L(f"tile {i}: {v}")
        i += 1
    # 2) match each id to a local clip and fetch the upscaled copy
    done = {p.stem for p in HD.glob("*.mp4")}
    seen_local = set(done)
    for v in ids:
        if len(seen_local) >= len(local):
            break
        tmp = pathlib.Path(tempfile.gettempdir()) / f"flow_{v}.mp4"
        try:
            out = fv.download_video(page, proj, v, str(tmp), upscale=False)
        except Exception as e:  # noqa: BLE001
            L(f"{v}: original download failed {type(e).__name__}")
            continue
        if not out:
            continue
        h = hashlib.md5(pathlib.Path(out).read_bytes()).hexdigest()
        cid = local.get(h)
        pathlib.Path(out).unlink(missing_ok=True)
        if not cid:
            L(f"{v}: not one of our clips")
            continue
        if cid in seen_local:
            L(f"{v}: {cid} already done")
            continue
        try:
            res = fv.download_video(page, proj, v, str(HD / cid), upscale=True)
        except Exception as e:  # noqa: BLE001
            L(f"{cid}: upscale failed {type(e).__name__}")
            continue
        if res:
            seen_local.add(cid)
            L(f"OK {cid} <- {v}")
    L(f"DONE {len(seen_local)}/{len(local)}")
    ctx.close()
