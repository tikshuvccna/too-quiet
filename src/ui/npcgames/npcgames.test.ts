import { describe, expect, it } from 'vitest';
import { BRIDGE_CFG, allConnected, bridgeState, budgetOf, minimumCost, totalCost, type BridgeLevel } from './bridge.logic';
import { CAKE_CFG, countRight, isComplete, makePattern, type CakeLevel } from './cake.logic';
import { FLY_CFG, judgeTap, makeSequence, passed, type FlyLevel } from './fireflies.logic';

const LEVELS = ['easy', 'medium', 'hard'] as const;

describe('fireflies', () => {
  it('patterns are repeatable, in range, and never repeat a firefly twice in a row', () => {
    for (const l of LEVELS as readonly FlyLevel[]) {
      const cfg = FLY_CFG[l];
      for (const len of cfg.rounds) {
        const a = makeSequence(len * 7, cfg.flies, len);
        expect(a).toEqual(makeSequence(len * 7, cfg.flies, len));
        expect(a).toHaveLength(len);
        a.forEach((v, i) => {
          expect(v).toBeGreaterThanOrEqual(0);
          expect(v).toBeLessThan(cfg.flies);
          if (i) expect(v).not.toBe(a[i - 1]);
        });
      }
    }
  });
  it('judges taps in order', () => {
    const seq = [2, 0, 1];
    expect(judgeTap(seq, 0, 2)).toBe('ok');
    expect(judgeTap(seq, 1, 1)).toBe('wrong');
    expect(judgeTap(seq, 2, 1)).toBe('done');
  });
  it('misses are forgiven up to the limit, calm adds more', () => {
    expect(passed(FLY_CFG.hard.allowedMisses, FLY_CFG.hard, false)).toBe(true);
    expect(passed(FLY_CFG.hard.allowedMisses + 1, FLY_CFG.hard, false)).toBe(false);
    expect(passed(FLY_CFG.hard.allowedMisses + 1, FLY_CFG.hard, true)).toBe(true);
  });
});

describe('cake', () => {
  it('patterns are repeatable and use every kind', () => {
    for (const l of LEVELS as readonly CakeLevel[]) {
      const c = CAKE_CFG[l];
      const p = makePattern(11, c.slots, c.kinds);
      expect(p).toEqual(makePattern(11, c.slots, c.kinds));
      expect(new Set(p).size).toBe(c.kinds);
    }
  });
  it('counts right slots', () => {
    expect(countRight([0, 1, 2], [0, null, 2])).toBe(2);
    expect(isComplete([0, 1], [0, 1])).toBe(true);
    expect(isComplete([0, 1], [1, 0])).toBe(false);
  });
});

describe('bridge', () => {
  it('every level is solvable within its budget and has spare links to leave out', () => {
    for (const l of LEVELS as readonly BridgeLevel[]) {
      const cfg = BRIDGE_CFG[l];
      const all = new Set(cfg.edges.map((_, i) => i));
      expect(allConnected(cfg.nodes.length, cfg.edges, all)).toBe(true);
      const min = minimumCost(cfg.nodes.length, cfg.edges);
      expect(budgetOf(cfg, false)).toBeGreaterThanOrEqual(min);
      expect(totalCost(cfg.edges, all)).toBeGreaterThan(budgetOf(cfg, false));
    }
  });
  it('reports open, over and done', () => {
    const cfg = BRIDGE_CFG.easy;
    const budget = budgetOf(cfg, false);
    expect(bridgeState(cfg, new Set(), budget)).toBe('open');
    expect(bridgeState(cfg, new Set([0, 3, 5, 1]), budget)).toBe('done');
    expect(bridgeState(cfg, new Set(cfg.edges.map((_, i) => i)), budget)).toBe('over');
  });
  it('hard has no slack', () => {
    const cfg = BRIDGE_CFG.hard;
    expect(budgetOf(cfg, false)).toBe(minimumCost(cfg.nodes.length, cfg.edges));
  });
});
