import type { Check, LessonStep } from './types';
import { hashString, mulberry32, shuffleOptions } from './util';

/** Resume at the first step whose check has not been answered. A finished lesson reopens at the start. */
export function resumeIndex(steps: readonly LessonStep[], checks: Record<string, boolean>, done: boolean): number {
  if (done) return 0;
  const i = steps.findIndex((s) => !checks[s.id]);
  return i === -1 ? Math.max(0, steps.length - 1) : i;
}

/** "Next" is blocked until this step's comprehension check was answered correctly. */
export function canAdvance(step: LessonStep, checks: Record<string, boolean>): boolean {
  return !!checks[step.id];
}

export function isLast(index: number, total: number): boolean {
  return index >= total - 1;
}

export function clampStep(index: number, total: number): number {
  return Math.min(Math.max(0, index), Math.max(0, total - 1));
}

/** Stable per-step shuffle: the content lists the right answer second almost every time, so show it in a seeded random place. */
export function checkForDisplay(step: LessonStep): Check {
  const sh = shuffleOptions(step.check.options, step.check.correct, mulberry32(hashString(step.id)));
  return { ...step.check, options: sh.options, correct: sh.correct };
}

/** Dot state for the progress bar. */
export function dotState(i: number, current: number, checks: Record<string, boolean>, steps: readonly LessonStep[]): 'done' | 'current' | 'todo' {
  if (i === current) return 'current';
  const s = steps[i];
  return s && checks[s.id] ? 'done' : 'todo';
}
