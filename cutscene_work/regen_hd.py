"""Regenerate the clips that cannot be found in Flow's list any more: send the prompt, wait for the new top tile,
then download the 360p original (cutscene_work/<id>.mp4) and the free 720p upscale (hd/<id>.mp4)."""
import pathlib, sys, time
sys.path.insert(0, r"E:\yt-tikshuv\tools\flow")
from playwright.sync_api import sync_playwright
import flowgen, flow_video as fv
proj = open(r"E:\yt-tikshuv\flow-project.txt").read().strip()
W = pathlib.Path(r"E:\Tikshuv Games\too-quiet\cutscene_work")
HD = W / "hd"
ids = sys.argv[1:]
with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(user_data_dir=str(flowgen.PROFILE_DIR), headless=False,
        viewport={"width": 1440, "height": 900}, accept_downloads=True, args=["--disable-blink-features=AutomationControlled"])
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    for cid in ids:
        if (HD / f"{cid}.mp4").exists():
            continue
        prompt = " ".join(l.strip() for l in (W / f"{cid}.txt").read_text(encoding="utf-8").splitlines() if l.strip())
        before = fv.top_video_id(page, proj)
        assert flowgen.open_flow(page, proj)
        assert fv.setup(page, 8, "360p", 1, "16:9")
        box = page.locator(flowgen.PROMPT_BOX).first
        box.click(); page.keyboard.press("End"); page.keyboard.insert_text(prompt); page.wait_for_timeout(1000)
        page.locator(flowgen.SUBMIT_BTN).first.click()
        print(time.strftime("%H:%M:%S"), "sent", cid, flush=True)
        page.wait_for_timeout(20000)
        vid = None
        t0 = time.time()
        while time.time() - t0 < 480:
            page.wait_for_timeout(25000)
            now = fv.top_video_id(page, proj)
            if now and now != before:
                vid = now
                break
        if not vid:
            print("NO NEW CLIP", cid, flush=True)
            continue
        page.wait_for_timeout(5000)
        fv.download_video(page, proj, vid, str(W / f"{cid}.mp4"))
        fv.download_video(page, proj, vid, str(HD / f"{cid}.mp4"), upscale=True)
        print("OK", cid, vid, flush=True)
    ctx.close()
