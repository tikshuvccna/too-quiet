import sys, time; sys.path.insert(0, r"E:\yt-tikshuv\tools\flow")
from playwright.sync_api import sync_playwright
import flowgen
proj=open(r"E:\yt-tikshuv\flow-project.txt").read().strip()
with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(user_data_dir=str(flowgen.PROFILE_DIR),headless=False,viewport={"width":1440,"height":900},args=["--disable-blink-features=AutomationControlled"])
    p=ctx.pages[0] if ctx.pages else ctx.new_page()
    p.goto(flowgen.en(proj)); p.wait_for_selector(flowgen.PROMPT_BOX,timeout=45000); p.wait_for_timeout(4000)
    def state(tag):
        return p.evaluate("""()=>{const v=document.querySelectorAll('img[alt="Generated video thumbnail"]').length;
          const all=document.querySelectorAll('img').length; const badges=document.querySelectorAll('.resolution-badge').length;
          const sc=[...document.querySelectorAll('*')].filter(e=>e.scrollHeight>e.clientHeight+50&&getComputedStyle(e).overflowY!=='visible').map(e=>[e.tagName,Math.round(e.scrollTop),e.scrollHeight]).slice(0,3);
          return {videoThumbs:v, imgs:all, badges, scrollers:sc}}""")
    print("ALL MEDIA start", state('all'), flush=True)
    last=0
    for i in range(40):
        p.mouse.move(800,450); p.mouse.wheel(0,900); p.wait_for_timeout(1500)
        s=state('all')
        if i%4==0 or s['videoThumbs']!=last: print(f"scroll {i}: videoThumbs={s['videoThumbs']} imgs={s['imgs']} scrollers={s['scrollers']}", flush=True)
        last=s['videoThumbs']
    p.screenshot(path=r"E:\Tikshuv Games\.playwright-mcp\diag_all.png")
    # the Videos tab
    p.goto(flowgen.en(proj)); p.wait_for_selector(flowgen.PROMPT_BOX,timeout=45000); p.wait_for_timeout(3000)
    p.get_by_text("Videos",exact=True).first.click(); p.wait_for_timeout(4000)
    print("VIDEOS TAB start", state('v'), flush=True)
    last=0
    for i in range(40):
        p.mouse.move(800,450); p.mouse.wheel(0,900); p.wait_for_timeout(1500)
        s=state('v')
        if i%4==0 or s['videoThumbs']!=last: print(f"vscroll {i}: videoThumbs={s['videoThumbs']} imgs={s['imgs']}", flush=True)
        last=s['videoThumbs']
    p.screenshot(path=r"E:\Tikshuv Games\.playwright-mcp\diag_videos.png")
    ctx.close()
