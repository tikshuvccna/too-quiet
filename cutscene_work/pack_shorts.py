"""Compress the channel Shorts (E:/yt-tikshuv/episodes) to 540x960 and write public/assets/shorts/<id>.mp4, <id>.jpg and
content/he/shorts.json with Hebrew title, YouTube link and length. Idempotent."""
import glob, json, os, subprocess
EP = r"E:\yt-tikshuv\episodes"
OUT = r"E:\Tikshuv Games\too-quiet\public\assets\shorts"
os.makedirs(OUT, exist_ok=True)
# id -> (episode folder, topic key)
PICK = {
 'sh_lan_wan': '003-lan-wan-v2', 'sh_client_server': '015-client-server-p2p', 'sh_host_end_media': '016-host-end-intermediary-media',
 'sh_topologies': '017-topologies', 'sh_pt_intro': '018-packet-tracer-intro', 'sh_pt_demo': '019-packet-tracer-demo',
 'sh_internet_home': '020-internet-home-connection', 'sh_hub_switch_router': '008-hub-switch-router', 'sh_hub_vs_switch': '009-hub-vs-switch',
 'sh_router': '010-router', 'sh_ip_address': '006-ip-address', 'sh_mac_address': '007-mac-address', 'sh_protocol_tcpip': '011-protocol-tcpip',
 'sh_ip_a': '013-ip-address-a', 'sh_ip_b': '014-ip-address-b',
}
data = []
for sid, ep in PICK.items():
    src = (glob.glob(os.path.join(EP, ep, 'output', 'final*.mp4')) or glob.glob(os.path.join(EP, ep, '*', 'final*.mp4')))[0]
    dst = os.path.join(OUT, sid + '.mp4')
    if not os.path.exists(dst):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf', 'scale=540:960', '-c:v', 'libx264', '-crf', '30', '-preset', 'medium',
                        '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '64k', '-movflags', '+faststart', dst], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '2', '-i', src, '-frames:v', '1', '-vf', 'scale=270:480', '-q:v', '4',
                        os.path.join(OUT, sid + '.jpg')], check=True)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', dst], capture_output=True, text=True).stdout)
    meta = {}
    mp = os.path.join(EP, ep, 'upload', 'meta.json')
    if os.path.exists(mp):
        meta = json.load(open(mp, encoding='utf-8'))
    link = ''
    lp = os.path.join(EP, ep, 'upload', 'link.txt')
    if os.path.exists(lp):
        link = open(lp, encoding='utf-8').read().strip().splitlines()[0]
    data.append({'id': sid, 'episode': ep, 'title': meta.get('title', ''), 'youtube': link, 'seconds': round(dur), 'mb': round(os.path.getsize(dst) / 1e6, 1)})
    print(sid, round(os.path.getsize(dst) / 1e6, 1), 'MB', round(dur), 's', meta.get('title', '')[:50], flush=True)
json.dump(data, open(r"E:\Tikshuv Games\too-quiet\cutscene_work\shorts_meta.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('done', sum(d['mb'] for d in data), 'MB total')
