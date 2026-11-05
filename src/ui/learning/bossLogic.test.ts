import { describe, expect, it } from 'vitest';
import { DAMAGE, MAX_HP, PHASES, PHASE_HP, PHASE_SEQUENCE, buildArena, difficulty, phaseOf, walk } from './bossLogic';

describe('the thread map', () => {
  const arena = buildArena();
  it('every link has a middle node, and the village gate reaches every house and lantern', () => {
    expect(arena.nodes.filter((n) => n.kind === 'mid')).toHaveLength(15);
    for (const n of arena.nodes.filter((x) => x.kind === 'house' || x.kind === 'hub')) {
      expect(walk(arena.adj, arena.start, n.id, new Set()), n.id).not.toBeNull();
    }
  });
  it('the walk never goes through the Head, and a cut blocks the way but can still be reached', () => {
    const p = walk(arena.adj, 'S', 'hA', new Set())!;
    expect(p).not.toContain('H');
    const cut = new Set(['hB~h3']);
    const around = walk(arena.adj, 'S', 'hB', cut)!;
    expect(around).not.toContain('hB~h3');
    expect(walk(arena.adj, 'S', 'hB~h3', cut)).not.toBeNull();
  });
  it('streams can come from the Head down to any reachable node', () => {
    expect(walk(arena.adj, 'H', 'h1', new Set(), true)).not.toBeNull();
  });
});

describe('phases and damage', () => {
  it('a full phase of faults takes exactly the strength of one phase', () => {
    const total = PHASE_SEQUENCE.reduce((sum, t) => sum + DAMAGE[t], 0);
    expect(total).toBe(PHASE_HP);
    expect(PHASES * PHASE_HP).toBe(MAX_HP);
  });
  it('the phase follows the Head strength and the fight gets harder', () => {
    expect(phaseOf(MAX_HP)).toBe(0);
    expect(phaseOf(MAX_HP - PHASE_HP)).toBe(1);
    expect(phaseOf(1)).toBe(PHASES - 1);
    expect(phaseOf(0)).toBe(PHASES - 1);
    expect(difficulty(4).streamEvery).toBeLessThan(difficulty(0).streamEvery);
    expect(difficulty(4).maxFaults).toBeGreaterThan(difficulty(0).maxFaults);
  });
});
