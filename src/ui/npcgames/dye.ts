import { el } from '../dom';
import type { GameMount, NpcGameDef } from './framework';

/** Wool dyeing with Mrs Yehudit: drops of red, yellow and blue mix by plain averaging. The same recipe always gives the same colour. */
type Rgb = [number, number, number];
const BOTTLES: Array<{ name: string; rgb: Rgb; css: string }> = [
  { name: 'אדום', rgb: [224, 64, 64], css: '#e04040' },
  { name: 'צהוב', rgb: [244, 208, 60], css: '#f4d03c' },
  { name: 'כחול', rgb: [60, 100, 224], css: '#3c64e0' },
];

interface Cfg { recipe: [number, number, number]; limit: number | null; tolerance: number; hint: string }
const CFG: Record<'easy' | 'medium' | 'hard', Cfg> = {
  easy: { recipe: [0, 2, 1], limit: null, tolerance: 42, hint: 'גוון ירוק' },
  medium: { recipe: [2, 1, 1], limit: null, tolerance: 38, hint: 'גוון חום' },
  hard: { recipe: [2, 0, 2], limit: 6, tolerance: 30, hint: 'סגול עדין, עד 6 טיפות' },
};

export function mix(drops: [number, number, number]): Rgb {
  const n = drops[0] + drops[1] + drops[2];
  if (n === 0) return [236, 232, 220];
  const out: Rgb = [0, 0, 0];
  drops.forEach((d, i) => { for (let k = 0; k < 3; k++) out[k] = (out[k] as number) + (BOTTLES[i] as { rgb: Rgb }).rgb[k]! * d; });
  return [Math.round(out[0] / n), Math.round(out[1] / n), Math.round(out[2] / n)];
}
const dist = (a: Rgb, b: Rgb): number => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
const css = (c: Rgb): string => `rgb(${c[0]},${c[1]},${c[2]})`;

const mount: GameMount = (host, level, run) => {
  const cfg = CFG[level];
  const tol = cfg.tolerance * (run.calm ? 1.3 : 1);
  const target = mix(cfg.recipe);
  const drops: [number, number, number] = [0, 0, 0];
  const total = (): number => drops[0] + drops[1] + drops[2];

  const bowl = el('div', 'dye-swatch');
  const goal = el('div', 'dye-swatch goal');
  goal.style.background = css(target);
  const status = el('div', 'npcg-status', '');
  const bottles = BOTTLES.map((b, i) => {
    const btn = el('button', 'btn npcg-big dye-bottle', `${i + 1}. ${b.name}`);
    btn.type = 'button';
    btn.style.borderColor = b.css;
    btn.addEventListener('click', () => add(i));
    return btn;
  });
  const dip = el('button', 'btn primary npcg-big', 'הטבילו את הצמר');
  const reset = el('button', 'btn npcg-big', 'התחילו קערה חדשה');
  dip.type = 'button';
  reset.type = 'button';
  const msg = el('div', 'npcg-status', '');

  function paint(): void {
    bowl.style.background = css(mix(drops));
    status.textContent = `טיפות: ${total()}${cfg.limit ? ` מתוך ${cfg.limit}` : ''}  ·  אדום ${drops[0]}, צהוב ${drops[1]}, כחול ${drops[2]}`;
  }
  function add(i: number): void {
    if (cfg.limit && total() >= cfg.limit) { msg.textContent = 'הקערה מלאה. התחילו קערה חדשה.'; return; }
    drops[i] = (drops[i] as number) + 1;
    msg.textContent = '';
    paint();
  }
  reset.addEventListener('click', () => { drops[0] = drops[1] = drops[2] = 0; msg.textContent = ''; paint(); });
  dip.addEventListener('click', () => {
    if (total() === 0) return;
    const d = dist(mix(drops), target);
    if (d <= tol) run.finish({ passed: true, summary: 'הצמר נצבע בדיוק בגוון המבוקש' });
    else msg.textContent = d < tol * 2 ? 'קרוב! עוד קצת התאמה.' : 'עדיין רחוק מהגוון. נסו שוב, בלי עונש.';
  });
  const kd = (e: KeyboardEvent): void => {
    const n = Number(e.key);
    if (n >= 1 && n <= 3) add(n - 1);
    if (e.key === 'Enter') { e.preventDefault(); dip.click(); }
  };
  document.addEventListener('keydown', kd);

  host.append(
    el('p', 'lrn-sub', `הגוון המבוקש: ${cfg.hint}`),
    el('div', 'dye-row', '', [el('div', '', '', [el('div', 'lrn-sub', 'המבוקש'), goal]), el('div', '', '', [el('div', 'lrn-sub', 'הקערה שלכם'), bowl])]),
    el('div', 'npcg-row', '', bottles),
    el('div', 'npcg-row', '', [reset, dip]),
    status, msg,
  );
  paint();
  return () => {
    document.removeEventListener('keydown', kd);
  };
};

export const DYE_GAME: NpcGameDef = {
  id: 'wool_dye',
  title: 'צביעת צמר',
  rules: 'ערבבו טיפות של שלושה צבעים כדי להגיע לגוון המבוקש. אותו מתכון תמיד נותן אותו גוון.',
  controls: 'לחיצה על הבקבוק, או המקשים 1, 2, 3. Enter להטבלה.',
  mount,
  rewards: {
    easy: { coins: 8 },
    medium: { coins: 12, food: { key: 'food_honey', name: 'טיפות דבש', n: 1 } },
    hard: { coins: 20, keepsake: { flag: 'cosmetic.dyed_scarf', name: 'מטפחת צבעונית' } },
  },
};
