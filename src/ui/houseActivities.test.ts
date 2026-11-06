import { describe, expect, it } from 'vitest';
import { HOUSES } from '../content';
import { SaveStore } from '../core/save';
import {
  ACTIVITIES, findFor, fixedShuffle, grantActivity, grantFind, neighbours, orderStart, orderTap,
  pairsFlip, pairsClose, pairsStart, sortCheck, toggleSolved, toggleStart, togglePress,
} from './houseActivitiesLogic';

const mem = (): SaveStore => new SaveStore({ getItem: () => null, setItem: () => undefined, removeItem: () => undefined });

describe('house activities data', () => {
  it('has one valid activity for every house', () => {
    for (const h of HOUSES) expect(ACTIVITIES[h.id], h.id).toBeDefined();
    expect(Object.keys(ACTIVITIES).length).toBe(HOUSES.length);
  });
  it('is well formed per type', () => {
    for (const [id, a] of Object.entries(ACTIVITIES)) {
      expect(a.prompt.length, id).toBeGreaterThan(5);
      if (a.type === 'order') expect(a.items.length).toBeGreaterThanOrEqual(3);
      if (a.type === 'pairs') expect(new Set(a.pairs.flat()).size, id).toBe(a.pairs.length * 2);
      if (a.type === 'toggle') {
        const l = toggleStart(a.rows, a.cols, a.presses);
        expect(toggleSolved(l), id).toBe(false);
        let s = l;
        for (const p of a.presses) s = togglePress(s, a.rows, a.cols, p);
        expect(toggleSolved(s), id).toBe(true);
      }
      if (a.type === 'sort') {
        for (const [, b] of a.items) expect(b).toBeLessThan(a.baskets.length);
        for (let b = 0; b < a.baskets.length; b++) expect(a.items.some(([, x]) => x === b), id).toBe(true);
      }
    }
  });
  it('uses no emoji and no page references', () => {
    const txt = JSON.stringify(ACTIVITIES);
    expect(/[\u{1F300}-\u{1FAFF}]/u.test(txt)).toBe(false);
    expect(txt.includes('עמוד')).toBe(false);
  });
});

describe('activity logic', () => {
  it('order: wrong tap resets, right sequence finishes', () => {
    const s = orderStart(3);
    expect(orderTap(s, 0)).toBe('ok');
    expect(orderTap(s, 2)).toBe('wrong');
    expect(s.next).toBe(0);
    expect(orderTap(s, 0)).toBe('ok');
    expect(orderTap(s, 1)).toBe('ok');
    expect(orderTap(s, 2)).toBe('done');
  });
  it('shuffle is fixed and never the identity', () => {
    for (let n = 2; n < 9; n++) {
      const a = fixedShuffle(n, `x${n}`);
      expect(a).toEqual(fixedShuffle(n, `x${n}`));
      expect([...a].sort((p, q) => p - q)).toEqual(Array.from({ length: n }, (_, i) => i));
      expect(a.every((v, i) => v === i)).toBe(false);
    }
  });
  it('pairs: match, miss and done', () => {
    const s = pairsStart([['a', 'A'], ['b', 'B']], 'seed');
    const find = (t: string): number => s.cards.findIndex((c) => c.text === t);
    expect(pairsFlip(s, find('a'))).toBe('first');
    expect(pairsFlip(s, find('B'))).toBe('miss');
    expect(pairsFlip(s, find('A'))).toBe('ignore');
    pairsClose(s);
    pairsFlip(s, find('a'));
    expect(pairsFlip(s, find('A'))).toBe('match');
    pairsFlip(s, find('b'));
    expect(pairsFlip(s, find('B'))).toBe('done');
  });
  it('toggle neighbours stay inside the board', () => {
    expect(neighbours(3, 3, 0).sort()).toEqual([0, 1, 3]);
    expect(neighbours(3, 3, 4).length).toBe(5);
    expect(neighbours(2, 3, 5).sort()).toEqual([2, 4, 5]);
  });
  it('sort check', () => {
    expect(sortCheck([['x', 1]], 0, 1)).toBe(true);
    expect(sortCheck([['x', 1]], 0, 0)).toBe(false);
  });
  it('rewards are paid once', () => {
    const s = mem();
    const a = ACTIVITIES.inn!;
    expect(grantActivity(s, 'inn', a)).not.toBeNull();
    const coins = s.data.coins;
    expect(grantActivity(s, 'inn', a)).toBeNull();
    expect(s.data.coins).toBe(coins);
    expect(s.hasFlag('act.inn.done')).toBe(true);
  });
});

describe('finds in objects', () => {
  it('are deterministic, small and paid once', () => {
    const kinds = new Set<string>();
    for (const h of HOUSES) {
      for (const o of h.objects) {
        const a = findFor(h.id, o.id);
        expect(a).toEqual(findFor(h.id, o.id));
        kinds.add(a.find.kind);
        if (a.find.kind === 'coins') {
          expect(a.find.n).toBeGreaterThanOrEqual(2);
          expect(a.find.n).toBeLessThanOrEqual(6);
        }
      }
    }
    expect(kinds.size).toBe(2);
    const s = mem();
    expect(grantFind(s, 'inn', 'i_key')).not.toBeNull();
    const snap = JSON.stringify([s.data.coins, s.data.inv]);
    expect(grantFind(s, 'inn', 'i_key')).toBeNull();
    expect(JSON.stringify([s.data.coins, s.data.inv])).toBe(snap);
  });
});
