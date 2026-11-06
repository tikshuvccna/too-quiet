import data from '../../content/he/world/house_activities.json';
import type { SaveStore } from '../core/save';

/** Pure logic for the small activities inside the houses and for the one-time finds in objects. */

export interface ActReward {
  coins: number;
  food?: { key: string; name: string; n: number };
  keepsake?: { flag: string; name: string };
}
interface ActCommon { spot: string; title: string; prompt: string; learn: string; done: string; reward: ActReward }
export interface OrderAct extends ActCommon { type: 'order'; items: string[] }
export interface PairsAct extends ActCommon { type: 'pairs'; pairs: Array<[string, string]> }
export interface ToggleAct extends ActCommon { type: 'toggle'; rows: number; cols: number; presses: number[]; noun: string }
export interface SortAct extends ActCommon { type: 'sort'; baskets: string[]; items: Array<[string, number]> }
export type Activity = OrderAct | PairsAct | ToggleAct | SortAct;

export const ACTIVITIES: Record<string, Activity> = (data as unknown as { activities: Record<string, Activity> }).activities;

export const doneFlag = (houseId: string): string => `act.${houseId}.done`;

/** FNV-1a: a stable hash, so "random-looking" choices are fixed for every player and every visit. */
export function hash(s: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h >>> 0;
}

/** A fixed shuffle of 0..n-1 that is never the identity (for n >= 2). */
export function fixedShuffle(n: number, seed: string): number[] {
  const a = Array.from({ length: n }, (_, i) => i);
  let h = hash(seed) || 1;
  const rnd = (): number => {
    h ^= h << 13; h >>>= 0;
    h ^= h >>> 17;
    h ^= h << 5; h >>>= 0;
    return h / 4294967296;
  };
  for (let i = n - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [a[i], a[j]] = [a[j] as number, a[i] as number];
  }
  if (n >= 2 && a.every((v, i) => v === i)) [a[0], a[1]] = [a[1] as number, a[0] as number];
  return a;
}

// ---- order ----
export interface OrderState { next: number; total: number }
export const orderStart = (total: number): OrderState => ({ next: 0, total });
/** Tap the item whose correct position is `idx`. Wrong taps reset the progress (free retry). */
export function orderTap(s: OrderState, idx: number): 'ok' | 'wrong' | 'done' {
  if (idx !== s.next) { s.next = 0; return 'wrong'; }
  s.next++;
  return s.next >= s.total ? 'done' : 'ok';
}

// ---- pairs ----
export interface Card { id: number; pair: number; text: string }
export interface PairsState { cards: Card[]; open: number[]; matched: Set<number> }
export function pairsStart(pairs: Array<[string, string]>, seed: string): PairsState {
  const cards: Card[] = pairs.flatMap((p, k) => [{ id: 0, pair: k, text: p[0] }, { id: 0, pair: k, text: p[1] }]);
  const order = fixedShuffle(cards.length, seed);
  return { cards: order.map((o, i) => ({ ...(cards[o] as Card), id: i })), open: [], matched: new Set() };
}
export function pairsFlip(s: PairsState, i: number): 'ignore' | 'first' | 'match' | 'miss' | 'done' {
  const c = s.cards[i];
  if (!c || s.matched.has(c.pair) || s.open.includes(i) || s.open.length >= 2) return 'ignore';
  s.open.push(i);
  if (s.open.length === 1) return 'first';
  const a = s.cards[s.open[0] as number] as Card;
  if (a.pair === c.pair) {
    s.matched.add(c.pair);
    s.open = [];
    return s.matched.size * 2 >= s.cards.length ? 'done' : 'match';
  }
  return 'miss';
}
export const pairsClose = (s: PairsState): void => { s.open = []; };

// ---- toggle (lights out) ----
export function neighbours(rows: number, cols: number, idx: number): number[] {
  const r = Math.floor(idx / cols);
  const c = idx % cols;
  const out = [idx];
  if (r > 0) out.push(idx - cols);
  if (r < rows - 1) out.push(idx + cols);
  if (c > 0) out.push(idx - 1);
  if (c < cols - 1) out.push(idx + 1);
  return out;
}
export function togglePress(lamps: boolean[], rows: number, cols: number, idx: number): boolean[] {
  const next = lamps.slice();
  for (const n of neighbours(rows, cols, idx)) next[n] = !next[n];
  return next;
}
/** Starts from "all lit" and applies the listed presses, so the board is always solvable (press the same cells again). */
export function toggleStart(rows: number, cols: number, presses: number[]): boolean[] {
  let l: boolean[] = Array.from({ length: rows * cols }, () => true);
  for (const p of presses) l = togglePress(l, rows, cols, p);
  return l;
}
export const toggleSolved = (l: boolean[]): boolean => l.every(Boolean);

// ---- sort ----
export const sortCheck = (items: Array<[string, number]>, item: number, basket: number): boolean => items[item]?.[1] === basket;

// ---- rewards ----
export function grantActivity(save: SaveStore, houseId: string, a: Activity, coinMul = 1): string | null {
  const flag = doneFlag(houseId);
  if (save.hasFlag(flag)) return null;
  const r = a.reward;
  const gained = Math.round(r.coins * coinMul);
  save.data.coins += gained;
  const parts = [`${gained} מטבעות`];
  if (r.food) {
    save.data.inv[r.food.key] = (save.data.inv[r.food.key] ?? 0) + r.food.n;
    parts.push(`${r.food.n} ${r.food.name} ליצורים`);
  }
  if (r.keepsake) {
    save.data.flags[r.keepsake.flag] = true;
    parts.push(r.keepsake.name);
  }
  save.data.flags[flag] = true;
  save.save();
  return parts.join(', ');
}

// ---- small finds in plain objects ----
export type Find = { kind: 'coins'; n: number } | { kind: 'food'; key: string; name: string };
const FOODS = [
  { key: 'food_berries', name: 'פירות יער' }, { key: 'food_bread', name: 'פירורי לחם' },
  { key: 'food_honey', name: 'טיפות דבש' }, { key: 'food_grains', name: 'גרגירים' },
];
const COIN_LINES = ['מתחת לחפץ נח מטבע שנשכח.', 'בתוך קפל נתקעו מטבעות.', 'משהו מצלצל בפנים: מטבעות.', 'מאחורי החפץ נשכחו כמה מטבעות.', 'על הרצפה מתחת לחפץ נוצץ מטבע.'];
const FOOD_LINES = ['נשאר כאן אוכל קטן. יצורים יאהבו אותו.', 'בפינה נחה פיסת אוכל שמורה ליצורים.', 'ממש ליד נמצא כיס עם אוכל ליצורים.'];

/** Fixed per house and object: the same find for every player, paid once. */
export function findFor(houseId: string, objId: string): { find: Find; line: string } {
  const h = hash(`${houseId}:${objId}`);
  if (h % 10 < 7) {
    const n = 2 + ((h >>> 4) % 5);
    return { find: { kind: 'coins', n }, line: `${COIN_LINES[(h >>> 8) % COIN_LINES.length]} (${n})` };
  }
  const f = FOODS[(h >>> 6) % FOODS.length] as { key: string; name: string };
  return { find: { kind: 'food', key: f.key, name: f.name }, line: `${FOOD_LINES[(h >>> 8) % FOOD_LINES.length]} (${f.name})` };
}

export const findFlag = (houseId: string, objId: string): string => `find:${houseId}:${objId}`;

/** Gives the find if not yet taken. Returns the line to show, or null. */
export function grantFind(save: SaveStore, houseId: string, objId: string, coinMul = 1): string | null {
  const key = findFlag(houseId, objId);
  if (save.data.collected[key]) return null;
  const { find, line } = findFor(houseId, objId);
  if (find.kind === 'coins') save.data.coins += Math.round(find.n * coinMul);
  else save.data.inv[find.key] = (save.data.inv[find.key] ?? 0) + 1;
  save.data.collected[key] = true;
  save.save();
  return line;
}
