import type { Level, MiniLevel, MiniTask } from './types';
import { shuffleOptions, type Rng } from './util';

export const BASE_POINTS: Record<Level, number> = { easy: 100, medium: 150, hard: 200 };
/** Share of tasks that must be right. 70 percent as asked; the content file says 8 of 10 for hard. */
export const PASS_FRACTION: Record<Level, number> = { easy: 0.7, medium: 0.7, hard: 0.8 };
export const LIFE_BONUS = 25;
export const MAX_STREAK_STEPS = 5;

export interface Rules { level: Level; lives: number; timeLimit: number | null; total: number }

export function rulesFor(level: Level, lv: MiniLevel): Rules {
  return { level, lives: lv.lives, timeLimit: lv.timeLimitPerTaskSec, total: lv.tasks.length };
}

export function passMin(level: Level, total: number): number {
  return Math.ceil(PASS_FRACTION[level] * total - 1e-9);
}

export interface GameState {
  index: number;
  lives: number;
  streak: number;
  bestStreak: number;
  correct: number;
  points: number;
  lostLife: boolean;
  over: boolean;
  finished: boolean;
}

export function newGame(r: Rules): GameState {
  return { index: 0, lives: r.lives, streak: 0, bestStreak: 0, correct: 0, points: 0, lostLife: false, over: false, finished: false };
}

/** Speed bonus only exists on timed levels, up to half the base points. A streak adds 10 percent per step, capped. */
export function scoreTask(level: Level, streakBefore: number, secondsUsed: number, timeLimit: number | null): { base: number; speed: number; streak: number; total: number } {
  const base = BASE_POINTS[level];
  const speed = timeLimit ? Math.round(base * 0.5 * Math.max(0, 1 - secondsUsed / timeLimit)) : 0;
  const streak = Math.round(base * 0.1 * Math.min(streakBefore, MAX_STREAK_STEPS));
  return { base, speed, streak, total: base + speed + streak };
}

export function answerTask(s: GameState, r: Rules, isCorrect: boolean, secondsUsed: number): { state: GameState; gained: number } {
  if (s.over || s.finished) return { state: s, gained: 0 };
  const index = s.index + 1;
  let gained = 0;
  let { lives, streak, bestStreak, correct, lostLife } = s;
  if (isCorrect) {
    gained = scoreTask(r.level, streak, secondsUsed, r.timeLimit).total;
    streak += 1;
    bestStreak = Math.max(bestStreak, streak);
    correct += 1;
  } else {
    lives -= 1;
    streak = 0;
    lostLife = true;
  }
  const finished = index >= r.total;
  const over = !finished && lives <= 0;
  return { state: { index, lives, streak, bestStreak, correct, points: s.points + gained, lostLife, over, finished }, gained };
}

export interface Summary { points: number; passed: boolean; flawless: boolean; lifeBonus: number }

export function summarize(s: GameState, r: Rules): Summary {
  const passed = s.finished && !s.over && s.correct >= passMin(r.level, r.total);
  const lifeBonus = s.finished ? Math.max(0, s.lives) * LIFE_BONUS : 0;
  return { points: s.points + lifeBonus, passed, flawless: s.finished && !s.lostLife, lifeBonus };
}

/** Keep only the best points, and a pass stays a pass. */
export function mergeBest(prev: { points: number; passed: boolean } | undefined, points: number, passed: boolean): { points: number; passed: boolean } {
  return { points: Math.max(prev?.points ?? 0, points), passed: !!prev?.passed || passed };
}

/** Long hard-level options sit in a fixed slot in the content: show them in a stable random order. */
export function prepareTask(task: MiniTask, level: Level, rng: Rng): MiniTask {
  if (level !== 'hard') return task;
  const sh = shuffleOptions(task.options, task.correct, rng);
  return { ...task, options: sh.options, correct: sh.correct };
}
