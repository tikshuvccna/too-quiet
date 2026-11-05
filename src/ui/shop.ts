import type { SaveStore } from '../core/save';
import { el } from './dom';
import { SKINS } from '../game/skins';
import { createOverlay } from './learning/overlay';

export interface ShopItem {
  id: string;
  name: string;
  desc: string;
  price: number;
  kind: 'aura' | 'perk' | 'food' | 'skin';
  /** Outfits only: the look (girl or boy) that can wear it. */
  look?: 'girl' | 'boy';
  /** Glow colour for auras. */
  color?: number;
  /** A flag that gives the item for free (a mini-game prize). Items with price 0 only show once owned. */
  rewardFlag?: string;
  /** Food for the creatures: bought again and again, a pack adds `n` of `key` to the inventory. */
  food?: { key: string; n: number };
}

/** Everything here has a visible or felt effect in the game. Prices are fixed. */
export const SHOP_ITEMS: ShopItem[] = [
  { id: 'aura_gold', name: 'הילה זהובה', desc: 'זוהר חם סביב הדמות.', price: 40, kind: 'aura', color: 0xffd36b },
  { id: 'aura_teal', name: 'הילה תכלת', desc: 'זוהר כמו חוט שמתעורר.', price: 40, kind: 'aura', color: 0x5cf0d0 },
  { id: 'aura_rose', name: 'הילה ורודה', desc: 'זוהר רך של שקיעה.', price: 40, kind: 'aura', color: 0xff9ad0 },
  { id: 'aura_blue', name: 'גלימת התכלת', desc: 'פרס משחקון: זוהר כחול.', price: 0, kind: 'aura', color: 0x5aa8ff, rewardFlag: 'cosmetic.cloak_blue' },
  { id: 'aura_violet', name: 'גלימת הסגול', desc: 'פרס משחקון: זוהר סגול.', price: 0, kind: 'aura', color: 0xb58cff, rewardFlag: 'cosmetic.cloak_violet' },
  { id: 'aura_rose2', name: 'גלימת הוורד', desc: 'פרס משחקון: זוהר ורדרד.', price: 0, kind: 'aura', color: 0xffa3c4, rewardFlag: 'cosmetic.cloak_rose' },
  { id: 'aura_head', name: 'גלימת הראש', desc: 'פרס על הבנת הרשת כולה: אור בוקר.', price: 0, kind: 'aura', color: 0xfff2b8, rewardFlag: 'cosmetic.cloak_head' },
  { id: 'aura_white', name: 'גלימת הלבן', desc: 'פרס משחקון: זוהר נקי.', price: 0, kind: 'aura', color: 0xffffff, rewardFlag: 'cosmetic.cloak_white' },
  { id: 'aura_green', name: 'הילה ירוקה', desc: 'זוהר של עלים ראשונים באביב.', price: 40, kind: 'aura', color: 0x7ff08c },
  { id: 'aura_orange', name: 'הילה כתומה', desc: 'זוהר של אש קטנה בתנור.', price: 40, kind: 'aura', color: 0xffa04d },
  { id: 'aura_sky', name: 'הילה שמיימית', desc: 'זוהר בהיר כמו שמיים אחרי גשם.', price: 50, kind: 'aura', color: 0x9fd8ff },
  { id: 'aura_red', name: 'הילה אדומה', desc: 'זוהר של הסליל העקשן.', price: 50, kind: 'aura', color: 0xff6b6b },
  { id: 'boots', name: 'נעלי דרך', desc: 'הולכים מהר יותר, 12 אחוז.', price: 60, kind: 'perk' },
  { id: 'light_sandals', name: 'סנדלי אור', desc: 'עוד קצת מהירות, 8 אחוז. אפשר לשלב עם נעלי דרך.', price: 50, kind: 'perk' },
  { id: 'extra_time', name: 'מחט ארוכת נשימה', desc: 'עוד דקה בין קפיצה למגדל.', price: 80, kind: 'perk' },
  { id: 'long_breath', name: 'נשימה עמוקה', desc: 'עוד 45 שניות בין קפיצה למגדל.', price: 120, kind: 'perk' },
  { id: 'long_stick', name: 'מקל הליכה ארוך', desc: 'אפשר להגיע לדברים וליצורים מרחוק יותר, 20 אחוז.', price: 70, kind: 'perk' },
  { id: 'eagle_glasses', name: 'משקפי עיט', desc: 'רואים נצנוץ של חיפוש בעצים מרחוק יותר.', price: 70, kind: 'perk' },
  { id: 'thread_lens', name: 'עדשת חוט', desc: 'המחט מראה שמות של תקלות מרחוק יותר.', price: 90, kind: 'perk' },
  { id: 'lucky_purse', name: 'כיס מזל', desc: 'כל מטבע שתמצאו או תזכו בו שווה 25 אחוז יותר.', price: 100, kind: 'perk' },
  { id: 'food_bread', name: 'לחם טרי (3)', desc: 'אוכל ליצורים: שלוש חתיכות מהמאפייה.', price: 15, kind: 'food', food: { key: 'food_bread', n: 3 } },
  { id: 'food_berries', name: 'פירות יער (3)', desc: 'אוכל ליצורים: שלוש חפנות.', price: 15, kind: 'food', food: { key: 'food_berries', n: 3 } },
  { id: 'food_grains', name: 'גרגירי דגן (3)', desc: 'אוכל ליצורים: שלוש כפות.', price: 15, kind: 'food', food: { key: 'food_grains', n: 3 } },
  { id: 'food_honey', name: 'דבש (3)', desc: 'אוכל ליצורים: שלוש כפיות, היצורים אוהבים.', price: 20, kind: 'food', food: { key: 'food_honey', n: 3 } },
  ...SKINS.map((k): ShopItem => ({ id: k.id, name: `לבוש: ${k.name}`, desc: k.look === 'girl' ? 'שמלה, כיסוי ראש וצבעים חדשים לדמות.' : 'מעיל, כיסוי ראש וצבעים חדשים לדמות.', price: k.price, kind: 'skin', look: k.look })),
];

export const ownedFlag = (id: string): string => `shop.${id}`;
export const owns = (save: SaveStore, id: string): boolean => {
  const it = SHOP_ITEMS.find((i) => i.id === id);
  if (it?.kind === 'food') return false;
  return save.hasFlag(ownedFlag(id)) || !!(it?.rewardFlag && save.hasFlag(it.rewardFlag)) || (id === 'aura_gold' && save.hasFlag('cosmetic.cloak_gold'));
};
export const equippedAura = (save: SaveStore): ShopItem | undefined => SHOP_ITEMS.find((i) => i.kind === 'aura' && save.hasFlag(`equip.${i.id}`));

export function buy(save: SaveStore, item: ShopItem): boolean {
  if (owns(save, item.id) || save.data.coins < item.price) return false;
  save.data.coins -= item.price;
  if (item.food) save.data.inv[item.food.key] = (save.data.inv[item.food.key] ?? 0) + item.food.n;
  else save.setFlag(ownedFlag(item.id));
  if (item.kind === 'aura') equip(save, item.id);
  if (item.kind === 'skin') equipSkin(save, item.id);
  save.save();
  return true;
}

/** One aura at a time; passing null takes it off. */
export function equip(save: SaveStore, id: string | null): void {
  for (const i of SHOP_ITEMS) if (i.kind === 'aura') delete save.data.flags[`equip.${i.id}`];
  if (id) save.setFlag(`equip.${id}`);
  save.save();
}

/** One outfit at a time; passing null puts the original clothes back. */
export function equipSkin(save: SaveStore, id: string | null): void {
  for (const k of SKINS) delete save.data.flags[`equip.${k.id}`];
  if (id) save.setFlag(`equip.${id}`);
  save.save();
}

export function openShop(save: SaveStore, opts: { onChange(): void }): Promise<void> {
  return new Promise((resolve) => {
    const ov = createOverlay('lrn-mini npcg', null);
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
      const card = (it: ShopItem): HTMLElement => {
        const have = owns(save, it.id);
        const on = save.hasFlag(`equip.${it.id}`);
        const b = el('button', `btn ${have ? '' : 'primary'}`, '');
        b.type = 'button';
        if (!have) {
          b.textContent = `לקנות ב-${it.price}`;
          b.disabled = save.data.coins < it.price;
          b.addEventListener('click', () => { if (buy(save, it)) { opts.onChange(); render(); } });
        } else if (it.kind === 'aura' || it.kind === 'skin') {
          b.textContent = on ? 'להסיר' : 'ללבוש';
          b.addEventListener('click', () => { if (it.kind === 'skin') equipSkin(save, on ? null : it.id); else equip(save, on ? null : it.id); opts.onChange(); render(); });
        } else {
          b.textContent = 'כבר שלכם ✓';
          b.disabled = true;
        }
        const ico = el('img', 'shop-ico') as HTMLImageElement;
        ico.src = `${import.meta.env.BASE_URL}assets/shop/${it.id}.png`;
        ico.alt = '';
        ico.loading = 'lazy';
        ico.addEventListener('error', () => ico.remove());
        return el('section', `lrn-level ${have ? 'passed' : ''}`, '', [ico, el('h2', '', it.name), el('p', '', it.desc), b]);
      };
      const visible = SHOP_ITEMS.filter((it) => (it.price > 0 || owns(save, it.id)) && (!it.look || it.look === save.data.look));
      const group = (kind: ShopItem['kind'], title: string): HTMLElement[] => {
        const items = visible.filter((it) => it.kind === kind);
        return items.length ? [el('h3', 'lrn-sub', title), el('div', 'lrn-levels', '', items.map(card))] : [];
      };
      const food = Object.entries(save.data.inv).filter(([, n]) => n > 0);
      body.replaceChildren(
        el('p', 'lrn-story', 'מטבעות מגיעים ממשחקוני הצד, מחיפוש בעצים ומחידונים. הכול כאן קבוע ולא מגרילים.'),
        ...group('skin', 'לבושים'),
        ...group('perk', 'עזרים'),
        ...group('aura', 'הילות'),
        ...group('food', 'אוכל ליצורים'),
        el('p', 'lrn-sub', food.length ? `אוכל ליצורים אצלכם: ${food.map(([k, n]) => `${k.replace('food_', '')} x${n}`).join(', ')}` : 'עוד אין לכם אוכל ליצורים: מצאו אותו בעצים ובמשחקוני הצד.'),
      );
    }
    render();
  });
}
