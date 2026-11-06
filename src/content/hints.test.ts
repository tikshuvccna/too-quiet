import { describe, expect, it } from 'vitest';
import { HOUSES, LINES } from './index';
import { HINTS, isHintLine, isHintObject } from './hints';
import { HELP } from '../ui/help';
import { SECRETS } from '../world/secrets';

describe('hint markers', () => {
  it('every hint line exists in the content', () => {
    for (const id of HINTS.lines) expect(LINES[id], id).toBeDefined();
  });

  it('every hint object exists in a house', () => {
    for (const key of HINTS.objects) {
      const [houseId, objId] = key.split(':') as [string, string];
      const house = HOUSES.find((h) => h.id === houseId);
      expect(house, key).toBeDefined();
      expect(house?.objects.some((o) => o.id === objId), key).toBe(true);
    }
  });

  it('has no duplicates and stays a small, meaningful set', () => {
    expect(new Set(HINTS.lines).size).toBe(HINTS.lines.length);
    expect(new Set(HINTS.objects).size).toBe(HINTS.objects.length);
    const total = HINTS.lines.length + HINTS.objects.length;
    expect(total).toBeGreaterThanOrEqual(25);
    expect(total).toBeLessThanOrEqual(60);
  });

  it('every secret clue object is a hint', () => {
    for (const s of SECRETS) expect(isHintObject(s.clue.house, s.clue.object), s.id).toBe(true);
  });

  it('lookups answer false for plain chat and missing ids', () => {
    expect(isHintLine('r1.p0.villager1.0001')).toBe(false);
    expect(isHintLine(undefined)).toBe(false);
    expect(isHintObject('library', 'nope')).toBe(false);
    expect(isHintLine(HINTS.lines[0])).toBe(true);
  });
});

describe('help content', () => {
  it('sections are short and cover the required topics', () => {
    for (const s of HELP.sections) {
      expect(s.lines.length, s.id).toBeGreaterThanOrEqual(2);
      expect(s.lines.length, s.id).toBeLessThanOrEqual(5);
      for (const l of s.lines) expect(l.split(/\s+/).length, `${s.id}: ${l}`).toBeLessThanOrEqual(22);
    }
    const ids = HELP.sections.map((s) => s.id);
    for (const need of ['move', 'goal', 'lessons', 'hint', 'collect', 'secrets', 'houses', 'housebook', 'videos', 'sound', 'saving', 'stuck']) expect(ids).toContain(need);
  });

  it('the tutorial has at most three cards with two short lines each', () => {
    expect(HELP.tutorial.cards.length).toBeLessThanOrEqual(3);
    for (const c of HELP.tutorial.cards) expect(c.lines).toHaveLength(2);
  });

  it('player text has no emoji and does not mention books or pages', () => {
    const all = JSON.stringify(HELP);
    expect(/\p{Extended_Pictographic}/u.test(all)).toBe(false);
    expect(all).not.toMatch(/ספר הלימוד|בספר|עמוד \d/);
  });
});
