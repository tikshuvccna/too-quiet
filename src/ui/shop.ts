import type { SaveStore } from '../core/save';
import { el } from './dom';
import { createOverlay } from './learning/overlay';

export interface ShopItem {
  id: string;
  name: string;
  desc: string;
  price: number;
  kind: 'aura' | 'perk';
  /** Glow colour for auras. */
  color?: number;
}

/** Everything here has a visible or felt effect in the game. Prices are fixed. */
export const SHOP_ITEMS: ShopItem[] = [
  { id: 'aura_gold', name: 'הילה זהובה', desc: 'זוהר חם סביב הדמות.', price: 40, kind: 'aura', color: 0xffd36b },
  { id: 'aura_teal', name: 'הילה תכלת', desc: 'זוהר כמו חוט שמתעורר.', price: 40, kind: 'aura', color: 0x5cf0d0 },
  { id: 'aura_rose', name: 'הילה ורודה', desc: 'זוהר רך של שקיעה.', price: 40, kind: 'aura', color: 0xff9ad0 },
  { id: 'boots', name: 'נעלי דרך', desc: 'הולכים מהר יותר, 12 אחוז.', price: 60, kind: 'perk' },
  { id: 'extra_time', name: 'מחט ארוכת נשימה', desc: 'עוד דקה בין קפיצה למגדל.', price: 80, kind: 'perk' },
];

export const ownedFlag = (id: string): string => `shop.${id}`;
export const owns = (save: SaveStore, id: string): boolean => save.hasFlag(ownedFlag(id)) || (id === 'aura_gold' && save.hasFlag('cosmetic.cloak_gold'));
export const equippedAura = (save: SaveStore): ShopItem | undefined => SHOP_ITEMS.find((i) => i.kind === 'aura' && save.hasFlag(`equip.${i.id}`));

export function buy(save: SaveStore, item: ShopItem): boolean {
  if (owns(save, item.id) || save.data.coins < item.price) return false;
  save.data.coins -= item.price;
  save.setFlag(ownedFlag(item.id));
  if (item.kind === 'aura') equip(save, item.id);
  save.save();
  return true;
}

/** One aura at a time; passing null takes it off. */
export function equip(save: SaveStore, id: string | null): void {
  for (const i of SHOP_ITEMS) if (i.kind === 'aura') delete save.data.flags[`equip.${i.id}`];
  if (id) save.setFlag(`equip.${id}`);
  save.save();
}

export function openShop(save: SaveStore, opts: { onChange(): void }): Promise<void> {
  return new Promise((resolve) => {
    const ov = createOverlay('lrn-mini npcg');
    const coins = el('span', 'lrn-points', '');
    const closeBtn = el('button', 'lrn-x', '×');
    closeBtn.type = 'button';
    closeBtn.setAttribute('aria-label', 'סגירה');
    const head = el('header', 'lrn-head', '', [el('div', 'lrn-head-main', '', [el('h1', 'lrn-title', 'חנות החייט'), el('div', 'lrn-hud', '', [coins, document.createTextNode(' מטבעות')])]), closeBtn]);
    const body = el('main', 'lrn-body');
    ov.root.append(head, body);
    const close = (): void => {
      document.removeEventListener('keydown', onKey, true);
      ov.destroy();
      resolve();
    };
    const onKey = (e: KeyboardEvent): void => { if (e.key === 'Escape') { e.preventDefault(); close(); } };
    closeBtn.addEventListener('click', close);
    document.addEventListener('keydown', onKey, true);

    function render(): void {
      coins.textContent = String(save.data.coins);
      const cards = SHOP_ITEMS.map((it) => {
        const have = owns(save, it.id);
        const on = save.hasFlag(`equip.${it.id}`);
        const b = el('button', `btn ${have ? '' : 'primary'}`, '');
        b.type = 'button';
        if (!have) {
          b.textContent = `לקנות ב-${it.price}`;
          b.disabled = save.data.coins < it.price;
          b.addEventListener('click', () => { if (buy(save, it)) { opts.onChange(); render(); } });
        } else if (it.kind === 'aura') {
          b.textContent = on ? 'להסיר' : 'ללבוש';
          b.addEventListener('click', () => { equip(save, on ? null : it.id); opts.onChange(); render(); });
        } else {
          b.textContent = 'כבר שלכם ✓';
          b.disabled = true;
        }
        return el('section', `lrn-level ${have ? 'passed' : ''}`, '', [el('h2', '', it.name), el('p', '', it.desc), b]);
      });
      const food = Object.entries(save.data.inv).filter(([, n]) => n > 0);
      body.replaceChildren(
        el('p', 'lrn-story', 'מטבעות מגיעים ממשחקוני הצד, מחיפוש בעצים ומחידונים. הכול כאן קבוע ולא מגרילים.'),
        el('div', 'lrn-levels', '', cards),
        el('p', 'lrn-sub', food.length ? `אוכל ליצורים אצלכם: ${food.map(([k, n]) => `${k.replace('food_', '')} x${n}`).join(', ')}` : 'עוד אין לכם אוכל ליצורים: מצאו אותו בעצים ובמשחקוני הצד.'),
      );
    }
    render();
  });
}
