import { el } from '../dom';
import { makeStage, seeded } from './canvasKit';
import type { GameMount, NpcGameDef } from './framework';

/** Paper boat race: steer left and right, bump a rock and you slow down, catch leaves for a boost, beat Gideon to the line. */
interface Cfg { rocks: number; length: number; gideon: number; wiggle: number }
const CFG: Record<'easy' | 'medium' | 'hard', Cfg> = {
  easy: { rocks: 6, length: 3200, gideon: 44, wiggle: 0 },
  medium: { rocks: 10, length: 3200, gideon: 38, wiggle: 0.5 },
  hard: { rocks: 14, length: 3200, gideon: 34, wiggle: 1 },
};
const SPEED = 110;

const mount: GameMount = (host, level, run) => {
  const cfg = CFG[level];
  const calm = run.calm;
  const stage = makeStage(host);
  const status = el('div', 'npcg-status', '');
  const left = el('button', 'btn primary npcg-big', '◀ שמאלה');
  const right = el('button', 'btn primary npcg-big', 'ימינה ▶');
  left.type = 'button';
  right.type = 'button';
  host.append(el('div', 'npcg-row', '', [right, left]), status);

  const rnd = seeded(500 + cfg.rocks);
  const rocks = Array.from({ length: cfg.rocks }, (_, i) => ({ y: 360 + (i / cfg.rocks) * (cfg.length - 520) + rnd() * 80, x: 0.12 + rnd() * 0.76, hit: false }));
  const leaves = Array.from({ length: 8 }, (_, i) => ({ y: 250 + (i / 8) * (cfg.length - 400) + rnd() * 120, x: 0.1 + rnd() * 0.8, got: false }));
  let x = 0.5;
  let dir = 0;
  let y = 0; // distance travelled
  let slow = 0;
  let boost = 0;
  let t = 0;
  let over = false;
  const hold = (b: HTMLElement, d: number): void => {
    b.addEventListener('pointerdown', (e) => { e.preventDefault(); dir = d; });
    b.addEventListener('pointerup', () => { if (dir === d) dir = 0; });
    b.addEventListener('pointerleave', () => { if (dir === d) dir = 0; });
  };
  hold(left, -1);
  hold(right, 1);
  const kd = (e: KeyboardEvent): void => { if (e.key === 'ArrowLeft' || e.key === 'a') dir = -1; if (e.key === 'ArrowRight' || e.key === 'd') dir = 1; };
  const ku = (e: KeyboardEvent): void => { if (['ArrowLeft', 'a'].includes(e.key) && dir === -1) dir = 0; if (['ArrowRight', 'd'].includes(e.key) && dir === 1) dir = 0; };
  document.addEventListener('keydown', kd);
  document.addEventListener('keyup', ku);
  stage.canvas.addEventListener('pointerdown', (e) => {
    const r = stage.canvas.getBoundingClientRect();
    dir = e.clientX - r.left < r.width / 2 ? -1 : 1;
  });
  window.addEventListener('pointerup', () => { dir = 0; });

  const gideonSpeed = cfg.length / cfg.gideon;

  stage.loop((dt) => {
    const { c, size } = stage;
    if (!over) {
      t += dt;
      const current = Math.sin(t * 0.8) * 0.045 * cfg.wiggle;
      x = Math.max(0.06, Math.min(0.94, x + (dir * 0.55 + current) * dt));
      slow = Math.max(0, slow - dt);
      boost = Math.max(0, boost - dt);
      const base = calm ? SPEED * 0.92 : SPEED;
      const sp = base * (slow > 0 ? 0.45 : 1) * (boost > 0 ? 1.35 : 1);
      y += sp * dt;
      for (const r of rocks) {
        if (!r.hit && Math.abs(r.y - (y + 140)) < 24 && Math.abs(r.x - x) < (calm ? 0.07 : 0.095)) { r.hit = true; slow = 1.1; }
      }
      for (const l of leaves) if (!l.got && Math.abs(l.y - (y + 140)) < 26 && Math.abs(l.x - x) < 0.09) { l.got = true; boost = 1.3; }
      if (y >= cfg.length) {
        over = true;
        const mine = t;
        const win = mine < cfg.gideon;
        window.setTimeout(() => run.finish({ passed: win, summary: `הגעתם ב-${mine.toFixed(1)} שניות, גדעון ב-${cfg.gideon}` }), 500);
      }
      if (t > cfg.gideon + 6) {
        over = true;
        window.setTimeout(() => run.finish({ passed: false, summary: 'גדעון הגיע קודם' }), 300);
      }
    }
    const g = c.createLinearGradient(0, 0, size.w, 0);
    g.addColorStop(0, '#2c5a72'); g.addColorStop(0.5, '#3f86a6'); g.addColorStop(1, '#2c5a72');
    c.fillStyle = g;
    c.fillRect(0, 0, size.w, size.h);
    // ripples scrolling past
    c.strokeStyle = 'rgba(200,240,255,.25)';
    c.lineWidth = 2;
    for (let i = 0; i < 14; i++) {
      const ry = ((i * 97 - y * 1.1) % (size.h + 40) + size.h + 40) % (size.h + 40) - 20;
      const rx = ((i * 211) % 100) / 100 * size.w;
      c.beginPath(); c.ellipse(rx, ry, 18, 4, 0, 0, 7); c.stroke();
    }
    const screenY = (worldY: number): number => size.h - 140 - (worldY - y - 140) * 1;
    for (const r of rocks) {
      const sy = screenY(r.y);
      if (sy < -40 || sy > size.h + 40) continue;
      c.fillStyle = r.hit ? '#7d8190' : '#5d6272';
      c.strokeStyle = '#2b2d38';
      c.lineWidth = 3;
      c.beginPath(); c.ellipse(r.x * size.w, sy, 30, 20, 0, 0, 7); c.fill(); c.stroke();
    }
    for (const l of leaves) {
      const sy = screenY(l.y);
      if (l.got || sy < -30 || sy > size.h + 30) continue;
      c.fillStyle = '#7bd05b';
      c.strokeStyle = '#2d6a22';
      c.beginPath(); c.ellipse(l.x * size.w, sy, 16, 8, 0.6, 0, 7); c.fill(); c.stroke();
    }
    // finish line
    const fy = screenY(cfg.length + 140);
    if (fy > -20 && fy < size.h + 20) {
      for (let i = 0; i < 16; i++) { c.fillStyle = i % 2 ? '#fff' : '#222'; c.fillRect((i / 16) * size.w, fy, size.w / 16, 14); }
    }
    // my boat and Gideon's (a small red one at the edge, shown as a marker)
    const bx = x * size.w;
    c.save();
    c.translate(bx, size.h - 140);
    c.rotate(dir * 0.18);
    c.fillStyle = '#fff4d6';
    c.strokeStyle = '#6d4a10';
    c.lineWidth = 2;
    c.beginPath(); c.moveTo(-22, -6); c.lineTo(22, -6); c.lineTo(12, 22); c.lineTo(-12, 22); c.closePath(); c.fill(); c.stroke();
    c.beginPath(); c.moveTo(0, -34); c.lineTo(14, -6); c.lineTo(-14, -6); c.closePath(); c.fill(); c.stroke();
    c.restore();
    const gy = Math.min(1, (t * gideonSpeed) / cfg.length);
    c.fillStyle = 'rgba(8,9,24,.55)';
    c.fillRect(size.w - 22, 10, 12, size.h - 20);
    c.fillStyle = '#ffd36b';
    c.fillRect(size.w - 24, size.h - 10 - (y / cfg.length) * (size.h - 20) - 4, 16, 8);
    c.fillStyle = '#ff7a59';
    c.fillRect(size.w - 24, size.h - 10 - gy * (size.h - 20) - 4, 16, 8);
    status.textContent = `זמן: ${t.toFixed(1)}  ·  גדעון ב-${cfg.gideon}  ·  ${slow > 0 ? 'פגעתם באבן!' : boost > 0 ? 'עלה מאיץ!' : 'שטים'}`;
  });

  return () => {
    document.removeEventListener('keydown', kd);
    document.removeEventListener('keyup', ku);
    stage.destroy();
  };
};

export const BOATS_GAME: NpcGameDef = {
  id: 'paper_boats',
  title: 'מרוץ סירות נייר',
  rules: 'הנחל זורם למטה. כוונו את הסירה בין האבנים, תפסו עלים להאצה, והגיעו לקו הסיום לפני גדעון.',
  controls: 'חצים ימינה ושמאלה, או לחיצה בצד ימין או שמאל של המסך.',
  mount,
  rewards: {
    easy: { coins: 8 },
    medium: { coins: 12, food: { key: 'food_water_jar', name: 'כדי מי נחל', n: 1 } },
    hard: { coins: 20, keepsake: { flag: 'decor.small_bench', name: 'ספסל קטן לבית' } },
  },
};
