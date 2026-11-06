import './houseActivities.css';
import type { SaveStore } from '../core/save';
import { audio } from '../audio/audio';
import { perksOf } from '../game/perks';
import { el } from './dom';
import { createOverlay } from './learning/overlay';
import {
  ACTIVITIES, doneFlag, fixedShuffle, grantActivity, orderStart, orderTap, pairsClose, pairsFlip, pairsStart, sortCheck,
  toggleSolved, toggleStart, togglePress,
  type Activity, type OrderAct, type PairsAct, type SortAct, type ToggleAct,
} from './houseActivitiesLogic';

type Finish = () => void;

function btn(cls: string, text: string, on: () => void): HTMLButtonElement {
  const b = el('button', cls, text);
  b.type = 'button';
  b.addEventListener('click', on);
  return b;
}

function shake(b: HTMLElement): void {
  b.classList.remove('hx-shake');
  void b.offsetWidth;
  b.classList.add('hx-shake');
}

function mountOrder(host: HTMLElement, a: OrderAct, status: HTMLElement, finish: Finish): void {
  const st = orderStart(a.items.length);
  const shown = fixedShuffle(a.items.length, `order:${a.title}`);
  const grid = el('div', 'hx-grid hx-col');
  const buttons: HTMLButtonElement[] = [];
  for (const idx of shown) {
    const b = btn('btn hx-item', a.items[idx] as string, () => {
      const r = orderTap(st, idx);
      if (r === 'wrong') {
        audio.sfx('fail');
        status.textContent = 'לא בסדר הזה. מתחילים שוב, בלי עונש.';
        buttons.forEach((x) => { x.disabled = false; x.classList.remove('hx-on'); x.dataset.n = ''; });
        shake(b);
        return;
      }
      audio.sfx('pop');
      b.disabled = true;
      b.classList.add('hx-on');
      b.dataset.n = String(idx + 1);
      status.textContent = `${st.next} מתוך ${st.total}`;
      if (r === 'done') finish();
    });
    buttons.push(b);
    grid.append(b);
  }
  host.append(grid);
}

function mountPairs(host: HTMLElement, a: PairsAct, status: HTMLElement, finish: Finish): void {
  const st = pairsStart(a.pairs, `pairs:${a.title}`);
  const grid = el('div', 'hx-grid hx-cards');
  const buttons = st.cards.map((c, i) => {
    const b = btn('btn hx-card', '?', () => {
      const r = pairsFlip(st, i);
      if (r === 'ignore') return;
      audio.sfx('pop');
      paint();
      if (r === 'miss') {
        audio.sfx('fail');
        window.setTimeout(() => { pairsClose(st); paint(); }, 900);
      } else if (r === 'match') audio.sfx('success');
      else if (r === 'done') finish();
      status.textContent = `${st.matched.size} מתוך ${a.pairs.length} זוגות`;
    });
    b.dataset.c = String(c.pair);
    return b;
  });
  function paint(): void {
    buttons.forEach((b, i) => {
      const c = st.cards[i] as { pair: number; text: string };
      const up = st.open.includes(i) || st.matched.has(c.pair);
      b.textContent = up ? c.text : '?';
      b.classList.toggle('hx-on', st.matched.has(c.pair));
      b.classList.toggle('hx-up', up);
    });
  }
  grid.append(...buttons);
  host.append(grid);
}

function mountToggle(host: HTMLElement, a: ToggleAct, status: HTMLElement, finish: Finish): void {
  let lamps = toggleStart(a.rows, a.cols, a.presses);
  const grid = el('div', 'hx-grid hx-lamps');
  grid.style.gridTemplateColumns = `repeat(${a.cols}, minmax(0, 76px))`;
  const buttons = lamps.map((_, i) => btn('btn hx-lamp', '', () => {
    lamps = togglePress(lamps, a.rows, a.cols, i);
    audio.sfx('click');
    paint();
    if (toggleSolved(lamps)) finish();
  }));
  buttons.forEach((b, i) => b.setAttribute('aria-label', `${a.noun} ${i + 1}`));
  function paint(): void {
    buttons.forEach((b, i) => b.classList.toggle('hx-lit', lamps[i]));
    status.textContent = `${lamps.filter(Boolean).length} מתוך ${lamps.length} דולקים`;
  }
  grid.append(...buttons);
  host.append(grid);
  paint();
}

function mountSort(host: HTMLElement, a: SortAct, status: HTMLElement, finish: Finish): void {
  const pending = a.items.map((_, i) => i);
  let current = 0;
  const chip = el('div', 'hx-chip', '');
  const counts = a.baskets.map(() => 0);
  const baskets = a.baskets.map((name, bi) => {
    const b = btn('btn hx-basket', '', () => {
      if (!pending.length) return;
      const item = pending[current] as number;
      if (sortCheck(a.items, item, bi)) {
        audio.sfx('pop');
        counts[bi] = (counts[bi] ?? 0) + 1;
        pending.splice(current, 1);
        current = 0;
        status.textContent = `${a.items.length - pending.length} מתוך ${a.items.length}`;
        paint();
        if (!pending.length) finish();
      } else {
        audio.sfx('fail');
        status.textContent = 'לא כאן. נסו סל אחר.';
        shake(chip);
      }
    });
    b.dataset.name = name;
    return b;
  });
  const next = btn('btn hx-skip', 'פריט אחר', () => {
    if (pending.length > 1) { current = (current + 1) % pending.length; paint(); }
  });
  function paint(): void {
    chip.textContent = pending.length ? (a.items[pending[current] as number] as [string, number])[0] : '';
    baskets.forEach((b, i) => { b.textContent = `${a.baskets[i]} (${counts[i]})`; });
  }
  host.append(el('div', 'hx-sorthead', '', [chip, next]), el('div', 'hx-baskets', '', baskets));
  paint();
}

/** Opens one house activity. Resolves true when the player finished it (the first reward is paid then). */
export function openActivity(houseId: string, save: SaveStore): Promise<boolean> {
  const found: Activity | undefined = ACTIVITIES[houseId];
  if (!found) return Promise.resolve(false);
  const a: Activity = found;
  return new Promise((resolve) => {
    const ov = createOverlay('hx-act');
    const closeBtn = el('button', 'lrn-x', '×');
    closeBtn.type = 'button';
    closeBtn.setAttribute('aria-label', 'סגירה');
    const status = el('p', 'hx-status', ' ');
    const body = el('main', 'lrn-body hx-body');
    ov.root.append(el('header', 'lrn-head', '', [el('div', 'lrn-head-main', '', [el('h1', 'lrn-title', a.title)]), closeBtn]), body);
    let won = false;
    let closed = false;
    const close = (): void => {
      if (closed) return;
      closed = true;
      document.removeEventListener('keydown', onKey, true);
      ov.destroy();
      resolve(won);
    };
    const onKey = (e: KeyboardEvent): void => { if (e.key === 'Escape') { e.preventDefault(); close(); } };
    document.addEventListener('keydown', onKey, true);
    closeBtn.addEventListener('click', close);

    const finish: Finish = () => {
      if (won) return;
      won = true;
      audio.sfx('success');
      const first = !save.hasFlag(doneFlag(houseId));
      const paid = grantActivity(save, houseId, a, perksOf(save).coinMul);
      const again = btn('btn', 'שוב', start);
      const done = btn('btn primary', 'סגירה', close);
      body.replaceChildren(el('section', 'hx-result', '', [
        el('h2', '', 'מצוין!'),
        el('p', 'hx-learn', a.learn),
        el('p', 'hx-prize', paid && first ? `פרס: ${paid}` : 'הפרס כבר התקבל.'),
        el('div', 'hx-row', '', [again, done]),
      ]));
      if (paid) audio.sfx('prize');
      done.focus();
    };

    function start(): void {
      won = false;
      status.textContent = ' ';
      const board = el('div', 'hx-board');
      body.replaceChildren(el('p', 'hx-prompt', a.prompt), board, status, el('p', 'lrn-sub', 'בלי עונש. אפשר לטעות ולנסות שוב.'));
      if (a.type === 'order') mountOrder(board, a, status, finish);
      else if (a.type === 'pairs') mountPairs(board, a, status, finish);
      else if (a.type === 'toggle') mountToggle(board, a, status, finish);
      else mountSort(board, a, status, finish);
    }
    start();
  });
}
