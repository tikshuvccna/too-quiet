import sys; sys.path.insert(0, r"E:\yt-tikshuv\tools\flow")
from playwright.sync_api import sync_playwright
import flowgen
proj=open(r"E:\yt-tikshuv\flow-project.txt").read().strip()
with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(user_data_dir=str(flowgen.PROFILE_DIR),headless=True,viewport={"width":1440,"height":900},args=["--disable-blink-features=AutomationControlled"])
    p=ctx.pages[0] if ctx.pages else ctx.new_page()
    p.goto(proj+"?hl=en"); p.wait_for_timeout(8000)
    p.get_by_text("Images", exact=True).first.click(); p.wait_for_timeout(6000)
    p.screenshot(path=r"E:\Tikshuv Games\.playwright-mcp\peek3.png")
    body=p.inner_text("body"); print([l for l in body.splitlines() if any(w in l.lower() for w in ("fail","error","blocked","policy","try again","violat"))][:8])
    ctx.close()
