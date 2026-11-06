import { describe, expect, it } from 'vitest';
import { HOUSE_INFO, bookFlag, inspectedFlag, layersOf, type BookProbe } from './houseBook';

const probe = (flags: string[]): BookProbe => ({
  has: (f) => flags.includes(f),
  count: (pre) => flags.filter((f) => f.startsWith(pre)).length,
});
const get = (id: string) => HOUSE_INFO.find((h) => h.id === id)!;

describe('house book', () => {
  it('has a card for every building, with all texts', () => {
    expect(HOUSE_INFO.length).toBe(22);
    expect(new Set(HOUSE_INFO.map((h) => h.id)).size).toBe(22);
    for (const h of HOUSE_INFO) {
      expect(h.history.length).toBeGreaterThanOrEqual(2);
      expect(h.history.length).toBeLessThanOrEqual(3);
      expect(h.important.length).toBeGreaterThan(5);
      expect(h.topic).toMatch(/שיעור/);
      expect(h.problem.length).toBeGreaterThan(5);
    }
  });
  it('is hidden until the house is entered', () => {
    expect(layersOf(get('inn'), probe([]))).toEqual({ l1: false, l2: false, l3: false });
    expect(layersOf(get('inn'), probe([bookFlag('inn')]))).toEqual({ l1: true, l2: false, l3: false });
  });
  it('history needs two inspected objects or the owner', () => {
    const f = [bookFlag('school'), inspectedFlag('school', 's_board')];
    expect(layersOf(get('school'), probe(f)).l2).toBe(false);
    expect(layersOf(get('school'), probe([...f, inspectedFlag('school', 's_globe')])).l2).toBe(true);
    expect(layersOf(get('school'), probe([bookFlag('school'), 'met_npc_teacher']))).toEqual({ l1: true, l2: true, l3: true });
  });
  it('story houses show the problem only after their story step', () => {
    expect(layersOf(get('inn'), probe([bookFlag('inn'), 'met_npc_innkeeper'])).l3).toBe(false);
    expect(layersOf(get('inn'), probe([bookFlag('inn'), 'p2_seen'])).l3).toBe(true);
    expect(layersOf(get('house_clinic'), probe([bookFlag('house_clinic'), 'fix_clinic_done'])).l3).toBe(true);
  });
  it('the great tower comes from the story flags', () => {
    expect(layersOf(get('great_tower'), probe(['fix_clinic_done'])).l1).toBe(true);
    expect(layersOf(get('great_tower'), probe(['p5_complete', 'p2_seen'])).l3).toBe(true);
  });
});
