import { el } from '../dom';
import { CAKE_CFG, DECOR, countRight, isComplete, makePattern } from './cake.logic';
import type { GameMount, NpcGameDef } from './framework';

/** Cake decoration with Mrs Dalia: copy the decorations of the sample cake onto yours. Hard levels hide the sample after a few seconds. */
const mount: GameMount = (host, level, run) => {
  const cfg = CAKE_CFG[level];
  const showSec = cfg.showSec === null ? null : cfg.showSec * (run.calm ? 1.5 : 1);
  const pattern = makePattern(40 + cfg.slots, cfg.slots, cfg.kinds);
  const placed: Array<number | null> = Array(cfg.slots).fill(null);
  let selected = 0;
  let peeks = cfg.peeks + (run.calm ? 1 : 0);
  let checksLeft = cfg.checks === null ? Infinity : cfg.checks + (run.calm ? 1 : 0);
  let hidden = false;
  let done = false;
  const timers: number[] = [];
  const later = (fn: () => void, sec: number): void => { timers.push(window.setTimeout(fn, sec * 1000)); };

  const refCells = pattern.map((p) => el('span', 'cake-slot ref', DECOR[p]));
  const myCells = pattern.map((_, i) => {
    const b = el('button', 'cake-slot', '');
    b.type = 'button';
    b.setAttribute('aria-label', `מקום ${i + 1}`);
    b.addEventListener('pointerdown', (e) => { e.preventDefault(); put(i); });
    return b;
  });
  const palette = DECOR.slice(0, cfg.kinds).map((d, i) => {
    const b = el('button', 'btn cake-pick', d);
    b.type = 'button';
    b.setAttribute('aria-label', `קישוט ${i + 1}`);
    b.addEventListener('pointerdown', (e) => { e.preventDefault(); selected = i; paintPalette(); });
    return b;
  });
  const refBox = el('div', 'cake-box', '', refCells);
  const myBox = el('div', 'cake-box mine', '', myCells);
  refBox.style.setProperty('--cols', String(Math.min(4, cfg.slots)));
  myBox.style.setProperty('--cols', String(Math.min(4, cfg.slots)));
  const peek = el('button', 'btn', 'הציצו שוב');
  const check = el('button', 'btn primary', 'בדקו');
  peek.type = 'button';
  check.type = 'button';
  const timer = el('div', 'npcg-status', '');
  const msg = el('div', 'npcg-status', '');
  const sample = el('div', 'cake-col', '', [el('div', 'lrn-sub', 'העוגה לדוגמה'), refBox]);
  const mine = el('div', 'cake-col', '', [el('div', 'lrn-sub', 'העוגה שלכם'), myBox]);

  function paintPalette(): void { palette.forEach((b, i) => b.classList.toggle('on', i === selected)); }
  function paint(): void {
    myCells.forEach((c, i) => { c.textContent = placed[i] === null ? '' : (DECOR[placed[i] as number] as string); });
    refBox.classList.toggle('veiled', hidden);
    peek.hidden = cfg.showSec === null;
    peek.disabled = peeks <= 0 || !hidden;
    peek.textContent = `הציצו שוב (${peeks})`;
  }
  function veil(on: boolean): void { hidden = on; paint(); }
  function put(i: number): void {
    if (done) return;
    placed[i] = placed[i] === selected ? null : selected;
    msg.textContent = '';
    paint();
  }
  function startShow(): void {
    if (showSec === null) { timer.textContent = ''; return; }
    let left = Math.ceil(showSec);
    const tick = (): void => {
      timer.textContent = left > 0 ? `זכרו את העוגה: ${left}` : '';
      if (left-- > 0) later(tick, 1); else { veil(true); msg.textContent = 'העוגה הוסתרה. אפשר להציץ שוב.'; }
    };
    tick();
  }
  peek.addEventListener('click', () => {
    if (peeks <= 0 || !hidden) return;
    peeks--;
    veil(false);
    later(() => veil(true), 3);
  });
  check.addEventListener('click', () => {
    if (done) return;
    if (placed.includes(null)) { msg.textContent = 'עוד יש מקומות ריקים על העוגה.'; return; }
    if (isComplete(pattern, placed)) {
      done = true;
      veil(false);
      msg.textContent = 'העוגה מושלמת!';
      later(() => run.finish({ passed: true, summary: 'קישטתם את העוגה בדיוק כמו הדוגמה' }), 700);
      return;
    }
    checksLeft--;
    const right = countRight(pattern, placed);
    if (checksLeft <= 0) {
      done = true;
      msg.textContent = `${right} מתוך ${cfg.slots} במקום`;
      later(() => run.finish({ passed: false, summary: `${right} מתוך ${cfg.slots} קישוטים במקום הנכון` }), 900);
      return;
    }
    msg.textContent = `${right} מתוך ${cfg.slots} במקום הנכון${cfg.checks === null ? '' : `. נשארו ${checksLeft} בדיקות`}`;
  });

  host.append(el('div', 'npcg-split', '', [
    el('div', 'cake-cols', '', [sample, mine]),
    el('div', 'npcg-side', '', [
      el('div', 'npcg-row cake-palette', '', palette),
      el('div', 'npcg-row', '', [peek, check]),
      timer, msg,
    ]),
  ]));
  paintPalette();
  paint();
  startShow();
  return () => {
    done = true;
    timers.forEach((t) => window.clearTimeout(t));
  };
};

export const CAKE_GAME: NpcGameDef = {
  id: 'cake_decor',
  title: 'קישוט עוגה',
  rules: 'העתיקו את הקישוטים מהעוגה לדוגמה אל העוגה שלכם, כל קישוט במקומו. בשלבים הגבוהים הדוגמה נעלמת, וצריך לזכור.',
  controls: 'בוחרים קישוט למטה, ואז נוגעים במקום על העוגה. נגיעה חוזרת מורידה אותו.',
  mount,
  rewards: {
    easy: { coins: 8 },
    medium: { coins: 12, food: { key: 'food_honey', name: 'טיפות דבש', n: 1 } },
    hard: { coins: 20, keepsake: { flag: 'cosmetic.cake_hat', name: 'כובע קונדיטור' } },
  },
};
