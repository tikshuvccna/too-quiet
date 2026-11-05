import sys; sys.path.insert(0, r"E:\yt-tikshuv\tools\flow")
from playwright.sync_api import sync_playwright
import flowgen
proj=open(r"E:\yt-tikshuv\flow-project.txt").read().strip()
prompt=open(r"E:\Tikshuv Games\too-quiet\cutscene_work\icons\prompts.txt",encoding="utf-8").readline().strip()
S=r"E:\Tikshuv Games\.playwright-mcp"
with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(user_data_dir=str(flowgen.PROFILE_DIR),headless=True,viewport={"width":1440,"height":900},args=["--disable-blink-features=AutomationControlled"])
    p=ctx.pages[0] if ctx.pages else ctx.new_page()
    flowgen.open_flow(p, proj)
    print("image mode:", flowgen.ensure_image_mode(p), "aspect:", flowgen.set_aspect(p,"1:1"))
    box=p.locator(flowgen.PROMPT_BOX).first; box.click(); p.keyboard.press("Control+A"); p.keyboard.press("Delete"); p.keyboard.insert_text(prompt); p.wait_for_timeout(1000)
    p.screenshot(path=S+r"\dbg1.png")
    btn=p.locator(flowgen.SUBMIT_BTN).first
    print("submit visible/disabled:", btn.is_visible(), btn.is_disabled())
    btn.click(); p.wait_for_timeout(6000); p.screenshot(path=S+r"\dbg2.png")
    p.wait_for_timeout(30000); p.screenshot(path=S+r"\dbg3.png")
    print([l for l in p.inner_text("body").splitlines() if l.strip()][:25])
    ctx.close()
