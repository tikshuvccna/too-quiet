import type { Difficulty, QuizQuestion } from './types';

export const POINTS: Record<Difficulty, number> = { easy: 10, medium: 15, hard: 20 };
export const PASS_MIN_CORRECT = 5;

/** first = right at once, retry = right on the second try, miss = wrong twice. */
export type Outcome = 'first' | 'retry' | 'miss';

/** A retry earns half the points, rounded down (15 gives 7). */
export function pointsFor(d: Difficulty, outcome: Outcome): number {
  if (outcome === 'first') return POINTS[d];
  if (outcome === 'retry') return Math.floor(POINTS[d] / 2);
  return 0;
}

export type AttemptResult = { kind: 'done'; outcome: Outcome } | { kind: 'again' };

/** attempt is 1 for the first answer, 2 for the retry. One retry per question. */
export function resolveAttempt(attempt: number, correct: boolean): AttemptResult {
  if (correct) return { kind: 'done', outcome: attempt <= 1 ? 'first' : 'retry' };
  return attempt <= 1 ? { kind: 'again' } : { kind: 'done', outcome: 'miss' };
}

export function maxScore(qs: readonly Pick<QuizQuestion, 'difficulty'>[]): number {
  return qs.reduce((s, q) => s + POINTS[q.difficulty], 0);
}

export interface Tally { score: number; max: number; correct: number; total: number; passed: boolean }

export function tally(qs: readonly Pick<QuizQuestion, 'difficulty'>[], outcomes: readonly (Outcome | undefined)[]): Tally {
  let score = 0;
  let correct = 0;
  qs.forEach((q, i) => {
    const o = outcomes[i];
    if (!o) return;
    score += pointsFor(q.difficulty, o);
    if (o !== 'miss') correct++;
  });
  return { score, max: maxScore(qs), correct, total: qs.length, passed: correct >= PASS_MIN_CORRECT };
}

/** The picked sequence lists option indices in the order the learner tapped them. */
export function isOrderCorrect(picked: readonly number[], correct: readonly number[]): boolean {
  return picked.length === correct.length && picked.every((v, i) => v === correct[i]);
}

/** Tapping an item adds it to the end; tapping a picked item removes it (the others keep their order). */
export function togglePick(picked: readonly number[], idx: number): number[] {
  return picked.includes(idx) ? picked.filter((v) => v !== idx) : [...picked, idx];
}
