import { describe, expect, it } from 'vitest';
import { SaveStore } from '../core/save';
import { perksOf } from '../game/perks';
import { SHOP_ITEMS, buy, equippedAura, owns } from './shop';

const fresh = (coins: number): SaveStore => {
  const s = new SaveStore(null);
  s.load();
  s.data.coins = coins;
  return s;
};
const item = (id: string) => SHOP_ITEMS.find((i) => i.id === id)!;

describe('shop', () => {
  it('sells at least 15 things, with unique ids', () => {
    const sold = SHOP_ITEMS.filter((i) => i.price > 0);
    expect(sold.length).toBeGreaterThanOrEqual(15);
    expect(new Set(SHOP_ITEMS.map((i) => i.id)).size).toBe(SHOP_ITEMS.length);
  });

  it('charges once for a perk and refuses when poor', () => {
    const s = fresh(60);
    expect(buy(s, item('light_sandals'))).toBe(true);
    expect(s.data.coins).toBe(10);
    expect(buy(s, item('light_sandals'))).toBe(false);
    expect(buy(s, item('eagle_glasses'))).toBe(false);
  });

  it('every new perk changes what the game does', () => {
    const s = fresh(1000);
    const base = perksOf(s);
    for (const id of ['light_sandals', 'long_breath', 'long_stick', 'eagle_glasses', 'thread_lens', 'lucky_purse']) expect(buy(s, item(id))).toBe(true);
    const p = perksOf(s);
    expect(p.speed).toBeGreaterThan(base.speed);
    expect(p.timeBonus).toBe(base.timeBonus + 45);
    expect(p.reach).toBeGreaterThan(base.reach);
    expect(p.glintMul).toBeGreaterThan(base.glintMul);
    expect(p.faultRadius).toBe(base.faultRadius + 120);
    expect(p.coinMul).toBeGreaterThan(base.coinMul);
  });

  it('food can be bought again and again and fills the inventory', () => {
    const s = fresh(100);
    expect(buy(s, item('food_honey'))).toBe(true);
    expect(buy(s, item('food_honey'))).toBe(true);
    expect(s.data.inv.food_honey).toBe(6);
    expect(s.data.coins).toBe(60);
    expect(owns(s, 'food_honey')).toBe(false);
  });

  it('a bought aura is worn at once', () => {
    const s = fresh(50);
    buy(s, item('aura_sky'));
    expect(equippedAura(s)?.id).toBe('aura_sky');
  });
});
