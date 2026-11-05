import { describe, expect, it } from 'vitest';
import { SaveStore } from '../core/save';
import { SKINS, baseChar, charKey, equippedSkin } from './skins';
import { buy, equipSkin, SHOP_ITEMS } from '../ui/shop';

const fresh = (look: 'girl' | 'boy', coins = 0): SaveStore => {
  const s = new SaveStore(null);
  s.load();
  s.data.look = look;
  s.data.coins = coins;
  return s;
};

describe('outfits', () => {
  it('has ten for each look, with unique ids', () => {
    expect(SKINS.filter((k) => k.look === 'girl')).toHaveLength(10);
    expect(SKINS.filter((k) => k.look === 'boy')).toHaveLength(10);
    expect(new Set(SKINS.map((k) => k.id)).size).toBe(20);
  });

  it('wears the original clothes until one is bought', () => {
    const s = fresh('girl', 500);
    expect(charKey(s)).toBe('apprentice_girl');
    const item = SHOP_ITEMS.find((i) => i.id === 'skin_girl_amber')!;
    expect(buy(s, item)).toBe(true);
    expect(charKey(s)).toBe('skin_girl_amber');
    equipSkin(s, null);
    expect(equippedSkin(s)).toBeUndefined();
    expect(charKey(s)).toBe(baseChar('girl'));
  });

  it('never shows a girl outfit on a boy', () => {
    const s = fresh('boy', 500);
    s.setFlag('equip.skin_girl_amber');
    expect(charKey(s)).toBe('apprentice_boy');
  });
});
