/** Rules of cake decoration: copy a shown pattern of decorations onto the cake. Pure functions, no DOM. */
import { seeded } from './canvasKit';

export type CakeLevel = 'easy' | 'medium' | 'hard';
export interface CakeCfg {
  slots: number;
  kinds: number;
  /** Seconds the pattern is visible before it is hidden; null means it stays. */
  showSec: number | null;
  /** How many times the player may look again (3 seconds each). */
  peeks: number;
  /** How many checks the player gets; null means unlimited. */
  checks: number | null;
}

export const CAKE_CFG: Record<CakeLevel, CakeCfg> = {
  easy: { slots: 4, kinds: 3, showSec: null, peeks: 0, checks: null },
  medium: { slots: 6, kinds: 4, showSec: 8, peeks: 2, checks: null },
  hard: { slots: 8, kinds: 4, showSec: 5, peeks: 1, checks: 3 },
};

/** Decorations by index. */
export const DECOR = ['🍓', '🍒', '⭐', '🌸'];

/** Same seed, same cake. Every kind appears at least once so the pattern is never trivial. */
export function makePattern(seed: number, slots: number, kinds: number): number[] {
  const rnd = seeded(seed);
  const out = Array.from({ length: slots }, (_, i) => (i < kinds ? i : Math.floor(rnd() * kinds)));
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [out[i], out[j]] = [out[j] as number, out[i] as number];
  }
  return out;
}

/** How many slots hold the right decoration. Empty slots are null. */
export function countRight(pattern: readonly number[], placed: ReadonlyArray<number | null>): number {
  let n = 0;
  for (let i = 0; i < pattern.length; i++) if (placed[i] === pattern[i]) n++;
  return n;
}

export const isComplete = (pattern: readonly number[], placed: ReadonlyArray<number | null>): boolean =>
  countRight(pattern, placed) === pattern.length;
