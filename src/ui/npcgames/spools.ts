import { el } from '../dom';
import { makeStage, seeded } from './canvasKit';
import type { GameMount, NpcGameDef } from './framework';

/** Spool sorting with Mrs Lea: coloured spools slide down the belt, send each one to the basket of its colour. */
interface Cfg { colors: Array<{ name: string; fill: string }>; count: number; fall: number }
const BASE = [
  { name: 'אדום', fill: '#e0524f' }, { name: 'כחול', fill: '#4f8fe0' }, { name: 'ירוק', fill: '#5fbf5a' }, { name: 'צהוב', fill: '#f0c840' },
];
const CFG: Record<'easy' | 'medium' | 'hard', Cfg> = {
  easy: { colors: BASE.slice(0, 3), count: 12, fall: 6 },
  medium: { colors: BASE, count: 16, fall: 5 },
  // similar shades: a darker and a lighter pair
  hard: { colors: [{ name: 'כתום', fill: '#e8843c' }, { name: 'אדום', fill: '#d64a4a' }, { name: 'תכלת', fill: '#59b6e0' }, { name: 'כחול', fill: '#4a74d0' }], count: 20, fall: 4.5 },
};

const mount: GameMount = (host, level, run) => {
  const cfg = CFG[level];
  const fall = cfg.fall * (run.calm ? 1.4 : 1);
  const stage = makeStage(host, 'min(52vh, 420px)');
  const status = el('div', 'npcg-status', '');
  const rnd = seeded(900 + cfg.count);
  const order = Array.from({ length: cfg.count }, (_, i) => i % cfg.colors.length);
  for (let i = order.length - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [order[i], order[j]] = [order[j] as number, order[i] as number];
  }
  const baskets = cfg.colors.map((col, i) => {
    const b = el('button', 'btn npcg-big npcg-basket', `${i + 1}. ${col.name}`);
    b.type = 'button';
    b.style.borderColor = col.fill;
    b.addEventListener('pointerdown', (e) => { e.preventDefault(); pick(i); });
    return b;
  });
  host.append(el('div', 'npcg-row', '', baskets), status);

  let idx = 0;
  let sorted = 0;
  let mistakes = 0;
  let y = 0;
  let total = 0;
  let over = false;
  let flash = 0;
  let flashOk = true;

  function pick(i: number): void {
    if (over) return;
    if (i === order[idx]) { sorted++; idx++; y = 0; flash = 0.35; flashOk = true; }
    else { mistakes++; y = 0; flash = 0.35; flashOk = false; }
    if (sorted >= cfg.count) {
      over = true;
      window.setTimeout(() => run.finish({ passed: true, summary: `מיינתם ${sorted} סלילים, ${mistakes} טעויות` }), 500);
    }
  }
  const kd = (e: KeyboardEvent): void => {
    const n = Number(e.key);
    if (n >= 1 && n <= cfg.colors.length) pick(n - 1);
  };
  document.addEventListener('keydown', kd);

  stage.loop((dt) => {
    if (!over) {
      total += dt;
      y += dt / fall;
      flash = Math.max(0, flash - dt);
      if (y >= 1) { mistakes++; y = 0; flashOk = false; flash = 0.35; } // an unsorted spool returns to the top
      if (total > 120) { over = true; window.setTimeout(() => run.finish({ passed: false, summary: `מיינתם ${sorted} מתוך ${cfg.count}` }), 300); }
    }
    const { c, size } = stage;
    c.fillStyle = flash > 0 ? (flashOk ? '#2f6a4a' : '#7a3340') : '#3a2f52';
    c.fillRect(0, 0, size.w, size.h);
    c.fillStyle = '#2a2240';
    c.fillRect(size.w / 2 - 70, 0, 140, size.h);
    c.strokeStyle = 'rgba(255,255,255,.12)';
    for (let k = 0; k < 12; k++) c.strokeRect(size.w / 2 - 70, ((k * 40 + y * 200) % size.h), 140, 4);
    const next = order[idx + 1];
    if (next !== undefined) {
      c.fillStyle = (cfg.colors[next] as { fill: string }).fill;
      c.globalAlpha = 0.4;
      c.fillRect(size.w / 2 + 90, 20, 36, 36);
      c.globalAlpha = 1;
    }
    const cur = order[idx];
    if (cur !== undefined) {
      const sy = 40 + y * (size.h - 120);
      const col = (cfg.colors[cur] as { fill: string }).fill;
      c.fillStyle = '#d8c8a0';
      c.fillRect(size.w / 2 - 36, sy - 40, 72, 10);
      c.fillRect(size.w / 2 - 36, sy + 30, 72, 10);
      c.fillStyle = col;
      c.strokeStyle = '#1a1230';
      c.lineWidth = 3;
      c.beginPath(); c.roundRect(size.w / 2 - 30, sy - 32, 60, 64, 10); c.fill(); c.stroke();
      c.strokeStyle = 'rgba(255,255,255,.35)';
      for (let k = 0; k < 4; k++) { c.beginPath(); c.moveTo(size.w / 2 - 30, sy - 20 + k * 14); c.lineTo(size.w / 2 + 30, sy - 12 + k * 14); c.stroke(); }
    }
    status.textContent = `סלילים: ${sorted} מתוך ${cfg.count}  ·  טעויות: ${mistakes}`;
  });

  return () => {
    document.removeEventListener('keydown', kd);
    stage.destroy();
  };
};

export const SPOOLS_GAME: NpcGameDef = {
  id: 'spool_sort',
  title: 'מיון סלילים',
  rules: 'סלילים צבעוניים גולשים על הסרט. שלחו כל אחד לסל בצבע שלו לפני שיגיע לקצה.',
  controls: 'לחיצה על הסל, או המקשים 1 עד 4.',
  mount,
  rewards: {
    easy: { coins: 8 },
    medium: { coins: 12, keepsake: { flag: 'decor.wool_rug', name: 'שטיח צמר לבית' } },
    hard: { coins: 18, food: { key: 'food_grains', name: 'גרגירים', n: 3 }, keepsake: { flag: 'cosmetic.wool_gloves', name: 'כפפות צמר' } },
  },
};
