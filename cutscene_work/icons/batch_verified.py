import sys, time; sys.path.insert(0, r"E:\yt-tikshuv\tools\flow")
from playwright.sync_api import sync_playwright
import flowgen
proj=open(r"E:\yt-tikshuv\flow-project.txt").read().strip()
D=r"E:\Tikshuv Games\too-quiet\cutscene_work\icons"
prompts=[l.strip() for l in open(D+r"\prompts.txt",encoding="utf-8") if l.strip()]
names=[l.strip() for l in open(D+r"\prompts.names",encoding="utf-8") if l.strip()]
START=int(sys.argv[1]) if len(sys.argv)>1 else 0
prompts=prompts[START:]; names=names[START:]
log=open(D+r"\verified.log","a",encoding="utf-8")
def L(m): 
    s=time.strftime("%H:%M:%S ")+m; print(s,flush=True); log.write(s+"\n"); log.flush()
cnt=lambda p: p.locator("main img, img").count()
with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(user_data_dir=str(flowgen.PROFILE_DIR),headless=True,viewport={"width":1440,"height":900},args=["--disable-blink-features=AutomationControlled"])
    p=ctx.pages[0] if ctx.pages else ctx.new_page()
    flowgen.open_flow(p, proj)
    assert flowgen.ensure_image_mode(p) and flowgen.set_aspect(p,"1:1")
    for i,(n,t) in enumerate(zip(names,prompts),1):
        for attempt in (1,2):
            before=cnt(p)
            flowgen.submit_one(p,t)
            ok=False; t0=time.time(); last=before; stable=0
            while time.time()-t0<150:
                p.wait_for_timeout(3000); c=cnt(p)
                if c>before:
                    stable = stable+1 if c==last else 0
                    if stable>=3: ok=True; break
                last=c
            L(f"{i}/24 {n} attempt {attempt}: imgs {before}->{cnt(p)} {'OK' if ok else 'NO NEW IMAGES'}")
            if ok: break
            if "flow.google.com/project" not in p.url: L("SIGNED OUT - stopping"); ctx.close(); sys.exit(2)
    L("DONE")
    ctx.close()
