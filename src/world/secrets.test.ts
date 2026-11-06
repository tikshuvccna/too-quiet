import { describe, expect, it } from 'vitest';
import { HOUSES, ITEMS_IN_OBJECT } from '../content';
import { SaveStore } from '../core/save';
import { SECRETS, clueFlag, cluesIn, grantReward, hintFor, parseTarget, press, progressOf, resetProgress, solvedFlag, step, targetId } from './secrets';
import { inSea, regionAt } from './regions';

const mem = (): SaveStore => new SaveStore({ getItem: () => null, setItem: () => undefined, removeItem: () => undefined });

describe('secrets data', () => {
  it('has at least five puzzles, in different styles', () => {
    expect(SECRETS.length).toBeGreaterThanOrEqual(5);
    expect(new Set(SECRETS.map((s) => s.style)).size).toBe(SECRETS.length);
  });
  it('each order is a permutation of its nodes', () => {
    for (const s of SECRETS) expect([...s.order].sort()).toEqual(s.nodes.map((n) => n.id).sort());
  });
  it('each clue lies in a different house, on a plain object', () => {
    const houses = SECRETS.map((s) => s.clue.house);
    expect(new Set(houses).size).toBe(houses.length);
    for (const s of SECRETS) {
      const h = HOUSES.find((x) => x.id === s.clue.house);
      expect(h, s.id).toBeDefined();
      expect(h?.objects.some((o) => o.id === s.clue.object), s.id).toBe(true);
      expect(ITEMS_IN_OBJECT[`${s.clue.house}:${s.clue.object}`], s.id).toBeUndefined();
      expect(cluesIn(s.clue.house, s.clue.object)).toContain(s);
    }
  });
  it('positions are on land, inside their region, and not in the locked tower region', () => {
    for (const s of SECRETS) {
      for (const n of s.nodes) {
        expect(inSea(n.x, n.y), `${s.id}/${n.id}`).toBe(false);
        const r = regionAt(n.x, n.y);
        expect(r?.id, `${s.id}/${n.id}`).toBe(s.region);
        expect(r?.lockedUntil).toBeUndefined();
      }
    }
  });
  it('rewards are 30-60 coins with a unique keepsake', () => {
    for (const s of SECRETS) {
      expect(s.reward.coins).toBeGreaterThanOrEqual(30);
      expect(s.reward.coins).toBeLessThanOrEqual(60);
      expect(s.reward.keepsake?.flag).toMatch(/^keepsake\./);
    }
    expect(new Set(SECRETS.map((s) => s.reward.keepsake?.flag)).size).toBe(SECRETS.length);
  });
  it('the moor scroll has one riddle line per stone, and no emoji anywhere', () => {
    const m = SECRETS.find((s) => s.id === 'moor_stones')!;
    expect(m.clue.lines.length).toBe(m.order.length);
    expect(/[\u{1F300}-\u{1FAFF}]/u.test(JSON.stringify(SECRETS))).toBe(false);
  });
});

describe('sequence logic', () => {
  it('step: right, wrong resets, solved', () => {
    expect(step(['a', 'b'], [], 'a')).toEqual({ result: 'ok', pressed: ['a'] });
    expect(step(['a', 'b'], ['a'], 'a')).toEqual({ result: 'wrong', pressed: [] });
    expect(step(['a', 'b'], ['a'], 'b')).toEqual({ result: 'solved', pressed: ['a', 'b'] });
  });
  it('press keeps progress per puzzle and resets after a mistake', () => {
    resetProgress();
    const d = SECRETS[0]!;
    expect(press(d, d.order[0]!)).toBe('ok');
    expect(progressOf(d.id).length).toBe(1);
    expect(press(d, d.order[0]!)).toBe('wrong');
    expect(progressOf(d.id).length).toBe(0);
    let r = 'ok';
    for (const id of d.order) r = press(d, id);
    expect(r).toBe('solved');
    expect(progressOf(d.id).length).toBe(0);
  });
  it('target ids round-trip', () => {
    expect(parseTarget(targetId('x', 'y'))).toEqual({ secretId: 'x', nodeId: 'y' });
    expect(parseTarget('npc:a')).toBeNull();
  });
  it('reward is paid once and the hint shows only after the clue', () => {
    const s = mem();
    const d = SECRETS[0]!;
    expect(hintFor(s)).toBeNull();
    s.setFlag(clueFlag(d.id));
    expect(hintFor(s)).toBe(d.hintAfterClue);
    expect(grantReward(s, d)).not.toBeNull();
    const c = s.data.coins;
    expect(grantReward(s, d)).toBeNull();
    expect(s.data.coins).toBe(c);
    expect(s.hasFlag(solvedFlag(d.id))).toBe(true);
    expect(hintFor(s)).toBeNull();
  });
});
