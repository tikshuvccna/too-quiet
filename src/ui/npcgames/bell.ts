import { el } from '../dom';
import { makeStage } from './canvasKit';
import type { GameMount, NpcGameDef } from './framework';

/** Bell rhythm: ring each bell exactly when it swings through the middle mark. Same swing, same order, every try. */
interface Cfg { bells: number[]; rings: number; need: number }
const CFG: Record<'easy' | 'medium' | 'hard', Cfg> = {
  easy: { bells: [2.4], rings: 8, need: 5 },
  medium: { bells: [2.2, 3.0], rings: 12, need: 10 },
  hard: { bells: [2.0, 2.6, 3.4], rings: 16, need: 12 },
};
const COLORS = ['#ffd36b', '#7ad6ff', '#ff9f7a'];

const mount: GameMount = (host, level, run) => {
  const cfg = CFG[level];
  const slow = run.calm ? 1.3 : 1;
  const window_ = run.calm ? 1.3 : 1;
  const stage = makeStage(host);
  const status = el('div', 'npcg-status', '');
  const buttons = cfg.bells.map((_, i) => {
    const b = el('button', 'btn primary npcg-big', cfg.bells.length > 1 ? `פעמון ${i + 1}` : 'צלצלו!');
    b.type = 'button';
    b.addEventListener('pointerdown', (e) => { e.preventDefault(); ring(i); });
    return b;
  });
  host.append(el('div', 'npcg-row', '', buttons), status);

  let t = 0;
  let rings = 0;
  let good = 0;
  let over = false;
  const flash: Array<{ text: string; at: number; x: number; col: string }> = [];
  // angle of bell i: sin(2*pi*t/period); crossing the middle happens when sin = 0
  const phase = (i: number): number => (t * slow) / (cfg.bells[i] as number);
  const dist = (i: number): number => {
    const p = phase(i) * 2; // zero crossings every half period
    return Math.abs(p - Math.round(p)) * ((cfg.bells[i] as number) / slow / 2); // seconds to the nearest crossing
  };

  function ring(i: number): void {
    if (over) return;
    const d = dist(i);
    rings++;
    let text = 'מאוחר';
    let col = '#ff8aa0';
    if (d < 0.1 * window_) { text = 'מדויק!'; col = '#5cf0d0'; good++; }
    else if (d < 0.22 * window_) { text = 'כמעט'; col = '#ffd36b'; good++; }
    flash.push({ text, at: t, x: ((i + 0.5) / cfg.bells.length), col });
    if (rings >= cfg.rings) {
      over = true;
      window.setTimeout(() => run.finish({ passed: good >= cfg.need, summary: `${good} צלצולים טובים מתוך ${cfg.rings} (צריך ${cfg.need})` }), 700);
    }
  }

  const nearest = (): number => cfg.bells.reduce((best, _, i) => (dist(i) < dist(best) ? i : best), 0);

  const onKey = (e: KeyboardEvent): void => {
    if (e.key === ' ' || e.key === 'ArrowDown' || e.key === 'Enter') { e.preventDefault(); ring(nearest()); return; }
    const n = Number(e.key);
    if (n >= 1 && n <= cfg.bells.length) ring(n - 1);
  };
  document.addEventListener('keydown', onKey);
  stage.canvas.addEventListener('pointerdown', (e) => {
    const r = stage.canvas.getBoundingClientRect();
    ring(Math.min(cfg.bells.length - 1, Math.floor(((e.clientX - r.left) / r.width) * cfg.bells.length)));
  });

  stage.loop((dt) => {
    t += dt;
    const { c, size } = stage;
    const g = c.createLinearGradient(0, 0, 0, size.h);
    g.addColorStop(0, '#2a2468'); g.addColorStop(1, '#6a5aa8');
    c.fillStyle = g;
    c.fillRect(0, 0, size.w, size.h);
    cfg.bells.forEach((_, i) => {
      const cx = ((i + 0.5) / cfg.bells.length) * size.w;
      const ang = Math.sin(phase(i) * Math.PI * 2) * 0.7;
      const len = size.h * 0.55;
      // beam and middle mark
      c.fillStyle = '#5a3d22';
      c.fillRect(cx - 70, 20, 140, 16);
      c.strokeStyle = 'rgba(92,240,208,.9)';
      c.lineWidth = 4;
      c.setLineDash([8, 8]);
      c.beginPath(); c.moveTo(cx, 40); c.lineTo(cx, 40 + len + 70); c.stroke();
      c.setLineDash([]);
      c.save();
      c.translate(cx, 36);
      c.rotate(ang);
      c.strokeStyle = '#c9a56a';
      c.lineWidth = 5;
      c.beginPath(); c.moveTo(0, 0); c.lineTo(0, len); c.stroke();
      // bell body
      c.translate(0, len);
      c.fillStyle = COLORS[i % COLORS.length] as string;
      c.strokeStyle = '#6d4a10';
      c.lineWidth = 3;
      c.beginPath();
      c.moveTo(-10, -26); c.bezierCurveTo(-14, -8, -22, 10, -40, 24); c.bezierCurveTo(-56, 34, -62, 44, -60, 50); c.lineTo(60, 50); c.bezierCurveTo(62, 44, 56, 34, 40, 24); c.bezierCurveTo(22, 10, 14, -8, 10, -26); c.closePath();
      c.fill(); c.stroke();
      c.fillStyle = '#6d4a10';
      c.beginPath(); c.arc(0, 56, 9, 0, 7); c.fill();
      c.restore();
    });
    for (let k = flash.length - 1; k >= 0; k--) {
      const f = flash[k] as (typeof flash)[number];
      const age = t - f.at;
      if (age > 1) { flash.splice(k, 1); continue; }
      c.globalAlpha = 1 - age;
      c.fillStyle = f.col;
      c.font = 'bold 30px sans-serif';
      c.textAlign = 'center';
      c.fillText(f.text, f.x * size.w, size.h * 0.2 - age * 30);
      c.globalAlpha = 1;
    }
    status.textContent = `צלצול ${Math.min(rings + 1, cfg.rings)} מתוך ${cfg.rings}  ·  טובים: ${good}`;
  });

  return () => {
    document.removeEventListener('keydown', onKey);
    stage.destroy();
  };
};

export const BELL_GAME: NpcGameDef = {
  id: 'bell_rhythm',
  title: 'קצב הפעמון',
  rules: 'הפעמון מתנדנד. צלצלו בדיוק ברגע שהוא עובר את הסימן האמצעי.',
  controls: 'רווח, חץ למטה או לחיצה על הפעמון. עם כמה פעמונים: המקשים 1, 2, 3.',
  mount,
  rewards: {
    easy: { coins: 8 },
    medium: { coins: 12, food: { key: 'food_bread', name: 'פירורי לחם', n: 3 } },
    hard: { coins: 20, keepsake: { flag: 'cosmetic.bell_scarf', name: 'צעיף פעמונים' } },
  },
};
