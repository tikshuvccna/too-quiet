/** Rules of the firefly game: a glowing pattern is shown, the player repeats it. Pure functions, no DOM. */
import { seeded } from './canvasKit';

export type FlyLevel = 'easy' | 'medium' | 'hard';
export interface FlyCfg {
  flies: number;
  /** Pattern length of each round; the game has one round per entry. */
  rounds: number[];
  /** How many wrong taps are forgiven over the whole game. */
  allowedMisses: number;
  /** Seconds each firefly glows while the pattern is shown. */
  stepSec: number;
}

export const FLY_CFG: Record<FlyLevel, FlyCfg> = {
  easy: { flies: 4, rounds: [2, 3, 4], allowedMisses: 4, stepSec: 0.8 },
  medium: { flies: 6, rounds: [3, 4, 5], allowedMisses: 3, stepSec: 0.65 },
  hard: { flies: 6, rounds: [4, 5, 6, 7], allowedMisses: 2, stepSec: 0.5 },
};

/** The same seed always gives the same pattern; a firefly never glows twice in a row. */
export function makeSequence(seed: number, flies: number, length: number): number[] {
  const rnd = seeded(seed);
  const out: number[] = [];
  for (let i = 0; i < length; i++) {
    let v = Math.floor(rnd() * flies);
    if (i > 0 && v === out[i - 1]) v = (v + 1 + Math.floor(rnd() * (flies - 1))) % flies;
    out.push(v);
  }
  return out;
}

export type TapResult = 'ok' | 'done' | 'wrong';

/** `progress` is how many fireflies of the pattern were already tapped correctly. */
export function judgeTap(seq: readonly number[], progress: number, tap: number): TapResult {
  if (seq[progress] !== tap) return 'wrong';
  return progress + 1 >= seq.length ? 'done' : 'ok';
}

export function passed(misses: number, cfg: FlyCfg, calm: boolean): boolean {
  return misses <= cfg.allowedMisses + (calm ? 2 : 0);
}
