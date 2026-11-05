import { describe, expect, it } from 'vitest';
import { bossRounds } from './bossGame';

describe('the Head', () => {
  it('asks three questions from every lesson, none of them an ordering question', () => {
    const rounds = bossRounds();
    expect(rounds).toHaveLength(15);
    for (const n of [1, 2, 3, 4, 5]) expect(rounds.filter((r) => r.lessonNo === n)).toHaveLength(3);
    for (const r of rounds) {
      expect(r.q.type === 'mcq' || r.q.type === 'tf').toBe(true);
      expect(r.q.correct).toBeLessThan(r.q.options.length);
    }
    expect(new Set(rounds.map((r) => `${r.lessonNo}:${r.q.id}`)).size).toBe(15);
  });
});
