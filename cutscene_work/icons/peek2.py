import sys; sys.path.insert(0, r"E:\yt-tikshuv\tools\flow")
from playwright.sync_api import sync_playwright
import flowgen
proj=open(r"E:\yt-tikshuv\flow-project.txt").read().strip()
with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(user_data_dir=str(flowgen.PROFILE_DIR),headless=True,viewport={"width":1440,"height":900},args=["--disable-blink-features=AutomationControlled"])
    p=ctx.pages[0] if ctx.pages else ctx.new_page()
    p.goto(proj+"?hl=en"); p.wait_for_timeout(10000)
    p.screenshot(path=r"E:\Tikshuv Games\.playwright-mcp\peek2.png")
    print(p.locator("img").count())
    ctx.close()
