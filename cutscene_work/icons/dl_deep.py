import sys, pathlib; sys.path.insert(0, r"E:\yt-tikshuv\tools\flow")
from playwright.sync_api import sync_playwright
import flowgen, flow_download as fd
proj=open(r"E:\yt-tikshuv\flow-project.txt").read().strip()
out=pathlib.Path(r"E:\Tikshuv Games\too-quiet\cutscene_work\icons\dl3")
def collect(page):
    seen, items, stable = set(), [], 0
    while stable < 10:
        before=len(items)
        for it in page.evaluate(fd.JS_COLLECT, fd.MIN_SIDE):
            if it["src"] not in seen: seen.add(it["src"]); items.append(it)
        page.mouse.move(800,450); page.mouse.wheel(0,700); page.wait_for_timeout(2200)
        stable = stable+1 if len(items)==before else 0
        if len(items)>=130: break
    items.sort(key=lambda it:(round(it["top"]),it["left"]))
    return items
with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(user_data_dir=str(flowgen.PROFILE_DIR),headless=False,viewport={"width":1440,"height":900},accept_downloads=True,args=["--disable-blink-features=AutomationControlled"])
    p=ctx.pages[0] if ctx.pages else ctx.new_page()
    p.goto(proj+"?hl=en"); p.wait_for_timeout(8000)
    items=collect(p); print("collected",len(items))
    fd.save_all(p, items[:110], out)
    ctx.close()
