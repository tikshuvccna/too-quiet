import { describe, expect, it } from 'vitest';
import { PROBLEMS, objectiveFor, problemForNpc, stageOf, type Probe } from './problems';

function probe(flags: string[], lessons: string[], scenes = true): Probe {
  const f = new Set(flags);
  const l = new Set(lessons);
  return { has: (x) => f.has(x), lessonDone: (x) => l.has(x), hasScene: () => scenes };
}

describe('problems 2-5', () => {
  const p2 = PROBLEMS[0]!;

  it('walk through problem 2: locked, chaos, learn, fix, done', () => {
    expect(stageOf(p2, probe([], []))).toBe('locked');
    expect(stageOf(p2, probe(['p1_complete'], []))).toBe('chaos');
    expect(stageOf(p2, probe(['p1_complete', 'p2_seen'], []))).toBe('learn');
    expect(stageOf(p2, probe(['p1_complete', 'p2_seen'], ['lesson02']))).toBe('fix');
    expect(stageOf(p2, probe(['p1_complete', 'p2_seen', 'p2_complete'], ['lesson02']))).toBe('done');
  });

  it('a problem whose scenes are not written yet stays locked', () => {
    expect(stageOf(p2, probe(['p1_complete'], [], false))).toBe('locked');
  });

  it('problems come one after the other', () => {
    expect(stageOf(PROBLEMS[1]!, probe(['p1_complete'], []))).toBe('locked');
    expect(stageOf(PROBLEMS[1]!, probe(['p1_complete', 'p2_complete'], []))).toBe('chaos');
  });

  it('tells the player what to do next', () => {
    expect(objectiveFor(probe(['p1_complete'], []))).toContain('בעיה חדשה');
    expect(objectiveFor(probe(['p1_complete', 'p2_seen'], []))).toContain('שיעור 2');
    expect(objectiveFor(probe(['p1_complete', 'p2_seen'], ['lesson02']))).toContain('לתקן');
    expect(objectiveFor(probe(['p1_complete', 'p2_complete', 'p3_complete', 'p4_complete', 'p5_complete'], []))).toBeNull();
  });

  it('each problem has its own NPC', () => {
    expect(new Set(PROBLEMS.map((p) => p.npc)).size).toBe(PROBLEMS.length);
    expect(problemForNpc('npc_innkeeper')?.n).toBe(2);
    expect(problemForNpc('npc_tailor')).toBeUndefined();
  });
});
