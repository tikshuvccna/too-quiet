import { el } from '../dom';
import type { GameDef, RoundApi } from './gameShell';
import type { Level, MinigameData } from './types';
import { SERVER, type Verdict, type WiringData, type WiringRound, evaluate, layout, linkKey } from './wiringLogic';
import { reducedMotion } from './widgetKit';

const DEVICE_COLORS = ['#ff9f7a', '#7ad6ff', '#c6a2ff', '#ffd36b', '#9be28a', '#ff8fb8'];

/**
 * "Valley wiring": every round describes a place and what it needs. The player decides whether it is
 * a network of equals or a server with clients, wires it with threads, and sends messengers to test it.
 */
export function wiringGame(wiring: WiringData, data: MinigameData): GameDef {
  const levelInfo = (level: Level): GameDef['levels']['easy'] => {
    const lv = wiring.levels[level];
    const meta = data.levels[level];
    return {
      count: lv.rounds.length,
      lives: meta.lives,
      timeLimit: meta.timeLimitPerTaskSec,
      blurb: `${lv.rounds.length} סיבובים. ${meta.timeLimitPerTaskSec ? `${meta.timeLimitPerTaskSec} שניות לסיבוב. ` : 'בלי הגבלת זמן. '}${lv.attempts} ניסיונות בכל סיבוב.`,
    };
  };
  return {
    title: wiring.title,
    intro: wiring.intro,
    howTo: wiring.howTo,
    levels: { easy: levelInfo('easy'), medium: levelInfo('medium'), hard: levelInfo('hard') },
    mountRound: (level, index, host, api) => mountWiringRound(wiring.levels[level].rounds[index] as WiringRound, wiring.levels[level].attempts, host, api),
  };
}

function mountWiringRound(round: WiringRound, attempts: number, host: HTMLElement, api: RoundApi): () => void {
  const canvas = el('canvas', 'lrn-canvas');
  const banner = el('div', 'lrn-wire-banner', '', [el('p', '', round.text)]);
  const msg = el('div', 'lrn-wire-msg', '');
  msg.setAttribute('aria-live', 'polite');
  const serverBtn = el('button', 'btn', 'שרת: אין');
  const clearBtn = el('button', 'btn', 'נתקו הכול');
  const sendBtn = el('button', 'btn primary', 'שלחו שליחים');
  for (const b of [serverBtn, clearBtn, sendBtn]) b.type = 'button';
  const controls = el('div', 'lrn-row lrn-wire-controls', '', [serverBtn, clearBtn, sendBtn]);
  const stage = el('div', 'lrn-wire-stage', '', [canvas]);
  host.append(banner, stage, msg, controls);

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

  const pos = layout(round.devices.length);
  const state = { server: false, links: new Set<string>() };
  let selected: number | null = null;
  let attemptsLeft = attempts;
  let t = 0;
  let busy = false;
  let done = false;
  let anim: { ok: boolean; bad: Set<string> } | null = null;
  const px = (i: number): [number, number] => (i === SERVER ? [W / 2, H * 0.52] : [pos[i]!.x * W, pos[i]!.y * H]);
  const radius = (): number => Math.max(34, Math.min(W, H) * 0.115);

  function hit(cx: number, cy: number): number | null {
    const r = stage.getBoundingClientRect();
    const x = cx - r.left;
    const y = cy - r.top;
    const R = radius();
    if (state.server) {
      const [sx, sy] = px(SERVER);
      if (Math.hypot(x - sx, y - sy) < R) return SERVER;
    }
    for (let i = 0; i < pos.length; i++) {
      const [dx, dy] = px(i);
      if (Math.hypot(x - dx, y - dy) < R) return i;
    }
    return null;
  }

  function setServer(on: boolean): void {
    state.server = on;
    if (!on) for (const k of [...state.links]) if (k.startsWith('-1-')) state.links.delete(k);
    serverBtn.textContent = on ? 'שרת: יש (הסירו)' : 'שרת: אין (הציבו)';
    serverBtn.classList.toggle('on', on);
    selected = null;
    msg.textContent = '';
  }
  setServer(false);

  canvas.addEventListener('pointerdown', (e) => {
    if (busy || done) return;
    const h = hit(e.clientX, e.clientY);
    if (h === null) { selected = null; return; }
    if (selected === null) { selected = h; return; }
    if (selected === h) { selected = null; return; }
    const key = linkKey(selected, h);
    if (state.links.has(key)) state.links.delete(key);
    else state.links.add(key);
    selected = null;
    msg.textContent = '';
  });
  serverBtn.addEventListener('click', () => { if (!busy && !done) setServer(!state.server); });
  clearBtn.addEventListener('click', () => { if (busy || done) return; state.links.clear(); selected = null; msg.textContent = ''; });

  const solutionHint = round.need === 'cs' ? ' כאן צריך שרת וכל מכשיר מחובר אליו.' : ' כאן אין שרת, וכל מכשיר מחובר לכל האחרים.';

  function finish(ok: boolean, text: string): void {
    done = true;
    controls.remove();
    api.resolve(ok, text);
  }

  function settle(v: Verdict): void {
    if (done) return;
    busy = false;
    api.setBusy(false);
    sendBtn.disabled = false;
    anim = null;
    if (v.ok) { finish(true, round.why); return; }
    attemptsLeft--;
    api.flash('bad');
    msg.className = 'lrn-wire-msg warn';
    if (attemptsLeft <= 0) { finish(false, `${v.message} ${round.why}${solutionHint}`); return; }
    msg.textContent = `${v.message} (נשארו ${attemptsLeft} ניסיונות)`;
  }

  sendBtn.addEventListener('click', () => {
    if (busy || done) return;
    const v = evaluate(round, state);
    busy = true;
    api.setBusy(true);
    sendBtn.disabled = true;
    const bad = new Set<string>();
    if (!v.ok && v.code === 'extra_links') for (const k of state.links) if (!k.startsWith('-1-')) bad.add(k);
    anim = { ok: v.ok, bad };
    window.setTimeout(() => settle(v), reducedMotion() ? 200 : 1500);
  });
  api.onTimeout(() => {
    if (done) return;
    finish(false, `הזמן נגמר. ${round.why}${solutionHint}`);
  });

  const c = canvas.getContext('2d') as CanvasRenderingContext2D;
  function house(x: number, y: number, col: string, label: string, sel: boolean, R: number): void {
    c.save();
    c.translate(x, y);
    if (sel) { c.shadowColor = '#ffd36b'; c.shadowBlur = 22; }
    c.fillStyle = col;
    c.strokeStyle = '#2b2150';
    c.lineWidth = 3;
    c.beginPath(); c.roundRect(-R * 0.6, -R * 0.35, R * 1.2, R * 0.9, 8); c.fill(); c.stroke();
    c.fillStyle = '#c85a4a';
    c.beginPath(); c.moveTo(-R * 0.75, -R * 0.35); c.lineTo(0, -R * 0.95); c.lineTo(R * 0.75, -R * 0.35); c.closePath(); c.fill(); c.stroke();
    c.shadowBlur = 0;
    c.fillStyle = '#fff6c8';
    c.fillRect(-R * 0.18, -R * 0.1, R * 0.36, R * 0.3);
    c.fillStyle = '#fff';
    c.font = `bold ${Math.max(12, R * 0.34)}px sans-serif`;
    c.textAlign = 'center';
    c.direction = 'rtl';
    c.lineWidth = 4;
    c.strokeStyle = 'rgba(8,9,24,.9)';
    c.strokeText(label, 0, R * 0.95);
    c.fillText(label, 0, R * 0.95);
    c.restore();
  }
  function crane(x: number, y: number, ang: number): void {
    c.save();
    c.translate(x, y);
    c.rotate(ang);
    c.fillStyle = '#fff4d6';
    c.strokeStyle = '#6d4a10';
    c.lineWidth = 1.5;
    c.beginPath(); c.moveTo(-8, 0); c.lineTo(0, -5); c.lineTo(8, 0); c.lineTo(0, 7); c.closePath(); c.fill(); c.stroke();
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
    g.addColorStop(0, '#2a2468'); g.addColorStop(1, '#6a5aa8');
    c.fillStyle = g;
    c.fillRect(0, 0, W, H);
    const R = radius();
    for (const k of state.links) {
      const [a, b] = k.split(/(?<=\d)-/).map(Number) as [number, number];
      const [ax, ay] = px(a);
      const [bx, by] = px(b);
      const bad = anim?.bad.has(k);
      c.strokeStyle = bad ? '#ff6b7d' : '#5cf0d0';
      c.lineWidth = 4;
      c.shadowColor = bad ? '#ff6b7d' : '#5cf0d0';
      c.shadowBlur = 10;
      c.beginPath(); c.moveTo(ax, ay); c.lineTo(bx, by); c.stroke();
      c.shadowBlur = 0;
      if (anim) {
        const p = (t * 1.4) % 1;
        const ang = Math.atan2(by - ay, bx - ax);
        crane(ax + (bx - ax) * p, ay + (by - ay) * p, ang);
        crane(bx + (ax - bx) * ((p + 0.5) % 1), by + (ay - by) * ((p + 0.5) % 1), ang + Math.PI);
      }
    }
    if (selected !== null) {
      const [sx, sy] = px(selected);
      c.strokeStyle = '#ffd36b';
      c.lineWidth = 3;
      c.setLineDash([8, 6]);
      c.beginPath(); c.arc(sx, sy, R + 8, 0, 7); c.stroke();
      c.setLineDash([]);
    }
    if (state.server) {
      const [sx, sy] = px(SERVER);
      c.save();
      c.translate(sx, sy);
      c.shadowColor = '#5cf0d0';
      c.shadowBlur = 24;
      c.fillStyle = '#3c3a78';
      c.strokeStyle = '#ffd36b';
      c.lineWidth = 3;
      c.beginPath(); c.roundRect(-R * 0.55, -R * 0.8, R * 1.1, R * 1.5, 10); c.fill(); c.stroke();
      c.shadowBlur = 0;
      for (let i = 0; i < 3; i++) { c.fillStyle = i === 0 ? '#5cf0d0' : '#ffd36b'; c.fillRect(-R * 0.38, -R * 0.6 + i * R * 0.38, R * 0.76, R * 0.22); }
      c.fillStyle = '#fff';
      c.font = `bold ${Math.max(12, R * 0.34)}px sans-serif`;
      c.textAlign = 'center';
      c.direction = 'rtl';
      c.fillText('שרת', 0, R * 1.05);
      c.restore();
    }
    round.devices.forEach((label, i) => {
      const [dx, dy] = px(i);
      house(dx, dy, DEVICE_COLORS[i % DEVICE_COLORS.length] as string, label, selected === i, R);
    });
    c.fillStyle = 'rgba(255,255,255,.75)';
    c.font = '13px sans-serif';
    c.textAlign = 'right';
    c.direction = 'rtl';
    c.fillText(`חוטים: ${state.links.size}   ·   ניסיונות: ${attemptsLeft}`, W - 12, 20);
  };
  raf = requestAnimationFrame(frame);
  return () => {
    cancelAnimationFrame(raf);
    ro.disconnect();
  };
}
