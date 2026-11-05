import { el } from '../dom';
import { makeStage, seeded } from './canvasKit';
import type { GameMount, NpcGameDef } from './framework';

/** Fishing with Yona: hold to lift the green zone, release to let it sink, keep the fish inside it until the meter is full. */
interface Cfg { fish: number; zone: number; speed: number; fill: number; drain: number; seconds: number }
const CFG: Record<'easy' | 'medium' | 'hard', Cfg> = {
  easy: { fish: 1, zone: 0.34, speed: 0.55, fill: 0.2, drain: 0.1, seconds: 60 },
  medium: { fish: 2, zone: 0.26, speed: 0.8, fill: 0.2, drain: 0.14, seconds: 75 },
  hard: { fish: 3, zone: 0.2, speed: 1.05, fill: 0.2, drain: 0.17, seconds: 90 },
};

const mount: GameMount = (host, level, run) => {
  const base = CFG[level];
  const cfg = run.calm ? { ...base, zone: base.zone * 1.25, speed: base.speed * 0.7, drain: base.drain * 0.7 } : base;
  const stage = makeStage(host);
  const status = el('div', 'npcg-status', '');
  const hold = el('button', 'btn primary npcg-big', 'החזיקו להרמה');
  hold.type = 'button';
  host.append(hold, status);

  const rnd = seeded(77 + cfg.fish);
  const seeds = Array.from({ length: 6 }, () => rnd() * 6.28);
  let down = false;
  const set = (v: boolean): void => { down = v; };
  hold.addEventListener('pointerdown', (e) => { e.preventDefault(); set(true); });
  window.addEventListener('pointerup', () => set(false));
  stage.canvas.addEventListener('pointerdown', () => set(true));
  const kd = (e: KeyboardEvent): void => { if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); set(true); } };
  const ku = (e: KeyboardEvent): void => { if (e.key === ' ' || e.key === 'Enter') set(false); };
  document.addEventListener('keydown', kd);
  document.addEventListener('keyup', ku);

  let zone = 0.5; // centre of the green zone, 0 bottom .. 1 top
  let zv = 0;
  let meter = 0;
  let caught = 0;
  let left = cfg.seconds;
  let t = 0;
  let over = false;
  // the fish wanders by a fixed sum of waves: same fish every try, stronger later
  const fishY = (k: number): number => {
    const sp = cfg.speed * (1 + k * 0.12);
    const a = Math.sin(t * sp * 0.9 + seeds[0]!) * 0.5 + Math.sin(t * sp * 1.7 + seeds[1]! + k) * 0.28 + Math.sin(t * sp * 0.43 + seeds[2]!) * 0.22;
    return 0.5 + Math.max(-0.5, Math.min(0.5, a)) * 0.92;
  };

  stage.loop((dt) => {
    if (!over) {
      t += dt;
      left -= dt;
      zv += (down ? 2.6 : -2.2) * dt;
      zv *= 0.96;
      zone = Math.max(cfg.zone / 2, Math.min(1 - cfg.zone / 2, zone + zv * dt));
      if (zone <= cfg.zone / 2 || zone >= 1 - cfg.zone / 2) zv = 0;
      const fy = fishY(caught);
      const inside = Math.abs(fy - zone) < cfg.zone / 2;
      meter = Math.max(0, Math.min(1, meter + (inside ? cfg.fill : -cfg.drain) * dt));
      if (meter >= 1) {
        caught++;
        meter = 0;
        if (caught >= cfg.fish) {
          over = true;
          window.setTimeout(() => run.finish({ passed: true, summary: `תפסתם ${caught} מתוך ${cfg.fish} דגים` }), 500);
        }
      }
      if (left <= 0 && !over) {
        over = true;
        window.setTimeout(() => run.finish({ passed: false, summary: `תפסתם ${caught} מתוך ${cfg.fish} דגים` }), 300);
      }
    }
    const { c, size } = stage;
    const g = c.createLinearGradient(0, 0, 0, size.h);
    g.addColorStop(0, '#7fc4de'); g.addColorStop(1, '#1d4d6b');
    c.fillStyle = g;
    c.fillRect(0, 0, size.w, size.h);
    const colX = size.w / 2 - 70;
    const colW = 140;
    const top = 30;
    const colH = size.h - 60;
    const yOf = (v: number): number => top + (1 - v) * colH;
    c.fillStyle = 'rgba(8,9,24,.45)';
    c.fillRect(colX, top, colW, colH);
    c.fillStyle = 'rgba(92,240,160,.55)';
    c.fillRect(colX, yOf(zone + cfg.zone / 2), colW, cfg.zone * colH);
    // fish
    const fy = yOf(fishY(caught));
    c.save();
    c.translate(size.w / 2, fy);
    c.fillStyle = '#ff9f7a';
    c.strokeStyle = '#6d2a1a';
    c.lineWidth = 2;
    c.beginPath(); c.ellipse(0, 0, 26, 13, 0, 0, 7); c.fill(); c.stroke();
    c.beginPath(); c.moveTo(24, 0); c.lineTo(42, -12); c.lineTo(42, 12); c.closePath(); c.fill(); c.stroke();
    c.fillStyle = '#fff'; c.beginPath(); c.arc(-14, -3, 3.5, 0, 7); c.fill();
    c.fillStyle = '#2b2150'; c.beginPath(); c.arc(-14, -3, 1.6, 0, 7); c.fill();
    c.restore();
    // meter on the side
    const mx = colX + colW + 30;
    c.fillStyle = 'rgba(8,9,24,.6)';
    c.fillRect(mx, top, 22, colH);
    c.fillStyle = '#ffd36b';
    c.fillRect(mx, top + colH * (1 - meter), 22, colH * meter);
    status.textContent = `דגים: ${caught} מתוך ${cfg.fish}  ·  זמן: ${Math.max(0, Math.ceil(left))}`;
  });

  return () => {
    document.removeEventListener('keydown', kd);
    document.removeEventListener('keyup', ku);
    stage.destroy();
  };
};

export const FISHING_GAME: NpcGameDef = {
  id: 'yona_fishing',
  title: 'דיג עם יונה',
  rules: 'הדג שוחה למעלה ולמטה. החזיקו כדי להרים את האזור הירוק, שחררו כדי להוריד, ושמרו עליו על הדג עד שהמד מתמלא.',
  controls: 'החזקת רווח או Enter. במגע: החזקת האצבע על הכפתור או על הנחל.',
  mount,
  rewards: {
    easy: { coins: 8 },
    medium: { coins: 12, food: { key: 'food_berries', name: 'פירות יער', n: 3 } },
    hard: { coins: 20, keepsake: { flag: 'cosmetic.wool_coat', name: 'מעיל צמר' } },
  },
};
