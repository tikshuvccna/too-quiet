import { el } from '../dom';
import type { GameDef, RoundApi } from './gameShell';
import { type SimData, type SimDevice, type SimKind, type SimRound, KIND_NAME, canLink, linkId, runPings } from './simLogic';
import { reducedMotion } from './widgetKit';
import type { Level } from './types';

const KIND_ORDER: SimKind[] = ['pc', 'server', 'switch'];

/** "The planning table": a small simulator. Place devices, wire them, send pings and watch the messages travel. */
export function simGame(data: SimData): GameDef {
  const info = (level: Level): GameDef['levels']['easy'] => {
    const l = data.levels[level];
    return {
      count: l.rounds.length, lives: l.lives, timeLimit: l.timeLimitPerTaskSec,
      blurb: `${l.rounds.length} סיבובים. ${l.timeLimitPerTaskSec ? `${l.timeLimitPerTaskSec} שניות לסיבוב. ` : 'בלי הגבלת זמן. '}${l.attempts} ניסיונות בכל סיבוב.`,
    };
  };
  return {
    title: data.title,
    intro: data.intro,
    howTo: data.howTo,
    levels: { easy: info('easy'), medium: info('medium'), hard: info('hard') },
    mountRound: (level, index, host, api) => mountSim(data.levels[level].rounds[index] as SimRound, data.levels[level].attempts, host, api),
  };
}

function mountSim(round: SimRound, attempts: number, host: HTMLElement, api: RoundApi): () => void {
  const devices: SimDevice[] = round.given.map((g, i) => ({ id: `g${i}`, kind: g.kind, label: g.label, x: g.x, y: g.y, fixed: true }));
  const links = new Set<string>();
  const remaining: Partial<Record<SimKind, number>> = { ...round.tools };
  const placedCount: Record<SimKind, number> = { pc: devices.filter((d) => d.kind === 'pc').length, server: devices.filter((d) => d.kind === 'server').length, switch: devices.filter((d) => d.kind === 'switch').length };
  let tool: SimKind | null = null;
  let selected: string | null = null;
  let attemptsLeft = attempts;
  let busy = false;
  let done = false;
  let t = 0;
  let anim: { paths: string[][]; start: number } | null = null;

  const canvas = el('canvas', 'lrn-canvas');
  const stage = el('div', 'lrn-wire-stage', '', [canvas]);
  const msg = el('div', 'lrn-wire-msg', '');
  msg.setAttribute('aria-live', 'polite');
  const toolBtns = new Map<SimKind, HTMLButtonElement>();
  const tools = el('div', 'lrn-row lrn-wire-controls');
  for (const k of KIND_ORDER) {
    if (!round.tools[k]) continue;
    const b = el('button', 'btn', '');
    b.type = 'button';
    b.addEventListener('click', () => { if (busy || done) return; tool = tool === k ? null : k; selected = null; refresh(); });
    toolBtns.set(k, b);
    tools.append(b);
  }
  const del = el('button', 'btn', 'מחקו מכשיר');
  const clear = el('button', 'btn', 'נתקו הכול');
  const send = el('button', 'btn primary', 'שלחו פינג');
  for (const b of [del, clear, send]) b.type = 'button';
  const controls = el('div', 'lrn-row lrn-wire-controls', '', [del, clear, send]);
  host.append(el('div', 'lrn-wire-banner', '', [el('p', '', round.text)]), stage, msg, tools, controls);

  function refresh(): void {
    for (const [k, b] of toolBtns) {
      const left = remaining[k] ?? 0;
      b.textContent = `${tool === k ? '✓ ' : ''}הציבו ${KIND_NAME[k]} (${left})`;
      b.classList.toggle('on', tool === k);
      b.disabled = left <= 0 && tool !== k;
    }
    const sel = devices.find((d) => d.id === selected);
    del.disabled = !sel || sel.fixed;
  }

  const dpr = Math.min(2, window.devicePixelRatio || 1);
  let W = 0;
  let H = 0;
  const fit = (): void => {
    W = stage.clientWidth;
    H = stage.clientHeight;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
  };
  fit();
  const ro = new ResizeObserver(fit);
  ro.observe(stage);
  const R = (): number => Math.max(24, Math.min(W, H) * 0.075);
  const pos = (d: SimDevice): [number, number] => [d.x * W, d.y * H];

  function deviceAt(cx: number, cy: number): SimDevice | null {
    const r = stage.getBoundingClientRect();
    const x = cx - r.left;
    const y = cy - r.top;
    for (let i = devices.length - 1; i >= 0; i--) {
      const d = devices[i] as SimDevice;
      const [dx, dy] = pos(d);
      if (Math.hypot(x - dx, y - dy) < R() * 1.1) return d;
    }
    return null;
  }

  canvas.addEventListener('pointerdown', (e) => {
    if (busy || done) return;
    const hit = deviceAt(e.clientX, e.clientY);
    const r = stage.getBoundingClientRect();
    if (tool && !hit) {
      if ((remaining[tool] ?? 0) <= 0) return;
      const nx = (e.clientX - r.left) / r.width;
      const ny = (e.clientY - r.top) / r.height;
      if (ny < 0.08) return;
      placedCount[tool]++;
      const label = tool === 'switch' ? `מתג ${placedCount.switch}` : `${KIND_NAME[tool]} ${placedCount[tool]}`;
      devices.push({ id: `p${devices.length}_${Math.round(t * 1000)}`, kind: tool, label, x: Math.min(0.94, Math.max(0.06, nx)), y: Math.min(0.92, Math.max(0.1, ny)), fixed: false });
      remaining[tool] = (remaining[tool] ?? 0) - 1;
      msg.textContent = '';
      refresh();
      return;
    }
    if (!hit) { selected = null; refresh(); return; }
    tool = null;
    if (selected === null || selected === hit.id) { selected = selected === hit.id ? null : hit.id; refresh(); return; }
    const key = linkId(selected, hit.id);
    if (links.has(key)) {
      links.delete(key);
      msg.textContent = '';
    } else {
      const c = canLink(devices, links, selected, hit.id);
      if (c.ok) { links.add(key); msg.textContent = ''; } else { msg.className = 'lrn-wire-msg warn'; msg.textContent = c.message; }
    }
    selected = null;
    refresh();
  });

  del.addEventListener('click', () => {
    const i = devices.findIndex((d) => d.id === selected && !d.fixed);
    if (i < 0) return;
    const d = devices[i] as SimDevice;
    devices.splice(i, 1);
    for (const k of [...links]) if (k.split('|').includes(d.id)) links.delete(k);
    remaining[d.kind] = (remaining[d.kind] ?? 0) + 1;
    selected = null;
    refresh();
  });
  clear.addEventListener('click', () => { if (busy || done) return; links.clear(); selected = null; msg.textContent = ''; refresh(); });

  function finish(ok: boolean, text: string): void {
    done = true;
    controls.remove();
    tools.remove();
    api.resolve(ok, text);
  }

  send.addEventListener('click', () => {
    if (busy || done) return;
    const v = runPings(round, devices, links);
    busy = true;
    api.setBusy(true);
    send.disabled = true;
    const paths = v.pings.filter((p) => p.path).map((p) => p.path as string[]);
    anim = { paths, start: t };
    window.setTimeout(() => {
      if (done) return;
      busy = false;
      api.setBusy(false);
      send.disabled = false;
      anim = null;
      if (v.ok) { finish(true, round.why); return; }
      attemptsLeft--;
      api.flash('bad');
      msg.className = 'lrn-wire-msg warn';
      if (attemptsLeft <= 0) { finish(false, `${v.message} ${round.why}`); return; }
      msg.textContent = `${v.message} (נשארו ${attemptsLeft} ניסיונות)`;
    }, reducedMotion() ? 200 : 1700);
  });
  api.onTimeout(() => { if (!done) finish(false, `הזמן נגמר. ${round.why}`); });

  const c = canvas.getContext('2d') as CanvasRenderingContext2D;
  function icon(d: SimDevice, sel: boolean): void {
    const [x, y] = pos(d);
    const r = R();
    c.save();
    c.translate(x, y);
    if (sel) { c.shadowColor = '#ffd36b'; c.shadowBlur = 22; }
    c.strokeStyle = '#2b2150';
    c.lineWidth = 3;
    if (d.kind === 'pc') {
      c.fillStyle = '#7ad6ff';
      c.beginPath(); c.roundRect(-r * 0.7, -r * 0.6, r * 1.4, r * 0.95, 8); c.fill(); c.stroke();
      c.shadowBlur = 0;
      c.fillStyle = '#1a1440'; c.fillRect(-r * 0.5, -r * 0.45, r * 1.0, r * 0.65);
      c.fillStyle = '#5a6a8a'; c.fillRect(-r * 0.2, r * 0.35, r * 0.4, r * 0.2); c.fillRect(-r * 0.5, r * 0.55, r * 1.0, r * 0.12);
    } else if (d.kind === 'server') {
      c.fillStyle = '#c6a2ff';
      c.beginPath(); c.roundRect(-r * 0.5, -r * 0.75, r * 1.0, r * 1.5, 8); c.fill(); c.stroke();
      c.shadowBlur = 0;
      for (let i = 0; i < 3; i++) { c.fillStyle = i === 0 ? '#5cf0d0' : '#2b2150'; c.fillRect(-r * 0.35, -r * 0.55 + i * r * 0.4, r * 0.7, r * 0.25); }
    } else {
      c.fillStyle = '#ffd36b';
      c.beginPath(); c.roundRect(-r * 0.85, -r * 0.3, r * 1.7, r * 0.6, 8); c.fill(); c.stroke();
      c.shadowBlur = 0;
      for (let i = 0; i < 8; i++) { c.fillStyle = '#2b2150'; c.fillRect(-r * 0.7 + i * r * 0.18, -r * 0.1, r * 0.1, r * 0.2); }
    }
    c.shadowBlur = 0;
    c.fillStyle = '#fff';
    c.font = `bold ${Math.max(11, r * 0.36)}px sans-serif`;
    c.textAlign = 'center';
    c.direction = 'rtl';
    c.lineWidth = 4;
    c.strokeStyle = 'rgba(8,9,24,.9)';
    c.strokeText(d.label, 0, r * 1.1);
    c.fillText(d.label, 0, r * 1.1);
    c.restore();
  }

  let raf = 0;
  let prev = performance.now();
  const frame = (now: number): void => {
    raf = requestAnimationFrame(frame);
    t += Math.min(0.25, (now - prev) / 1000);
    prev = now;
    c.setTransform(dpr, 0, 0, dpr, 0, 0);
    const g = c.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#2a2468'); g.addColorStop(1, '#4a3d7a');
    c.fillStyle = g;
    c.fillRect(0, 0, W, H);
    // a faint table grid, so the empty space reads as a place to put things
    c.strokeStyle = 'rgba(255,255,255,.05)';
    c.lineWidth = 1;
    for (let gx = 0; gx < W; gx += 40) { c.beginPath(); c.moveTo(gx, 0); c.lineTo(gx, H); c.stroke(); }
    for (let gy = 0; gy < H; gy += 40) { c.beginPath(); c.moveTo(0, gy); c.lineTo(W, gy); c.stroke(); }
    const byId = new Map(devices.map((d) => [d.id, d]));
    for (const k of links) {
      const [a, b] = k.split('|') as [string, string];
      const da = byId.get(a);
      const db = byId.get(b);
      if (!da || !db) continue;
      const [ax, ay] = pos(da);
      const [bx, by] = pos(db);
      c.strokeStyle = '#5cf0d0';
      c.lineWidth = 4;
      c.shadowColor = '#5cf0d0';
      c.shadowBlur = 8;
      c.beginPath(); c.moveTo(ax, ay); c.lineTo(bx, by); c.stroke();
      c.shadowBlur = 0;
    }
    if (anim) {
      // simulation mode: an envelope travels along every working path
      const p = ((t - anim.start) * 0.7) % 1;
      for (const path of anim.paths) {
        const pts = path.map((id) => pos(byId.get(id) as SimDevice));
        const seg = Math.min(pts.length - 2, Math.floor(p * (pts.length - 1)));
        const local = p * (pts.length - 1) - seg;
        const [x0, y0] = pts[seg] as [number, number];
        const [x1, y1] = pts[seg + 1] as [number, number];
        const ex = x0 + (x1 - x0) * local;
        const ey = y0 + (y1 - y0) * local;
        c.fillStyle = '#fff4d6';
        c.strokeStyle = '#6d4a10';
        c.lineWidth = 2;
        c.beginPath(); c.roundRect(ex - 10, ey - 7, 20, 14, 3); c.fill(); c.stroke();
        c.beginPath(); c.moveTo(ex - 10, ey - 7); c.lineTo(ex, ey); c.lineTo(ex + 10, ey - 7); c.stroke();
      }
    }
    for (const d of devices) icon(d, d.id === selected);
    c.fillStyle = 'rgba(255,255,255,.75)';
    c.font = '13px sans-serif';
    c.textAlign = 'right';
    c.direction = 'rtl';
    c.fillText(`חוטים: ${links.size}   ·   ניסיונות: ${attemptsLeft}${tool ? `   ·   לחצו על השולחן להצבת ${KIND_NAME[tool]}` : ''}`, W - 12, 20);
  };
  raf = requestAnimationFrame(frame);
  refresh();
  return () => {
    cancelAnimationFrame(raf);
    ro.disconnect();
  };
}
