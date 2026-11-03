import type { SaveStore } from '../../core/save';
import minigame from '../../../content/he/minigame01.json';
import type { Level, MinigameData, Prize } from './types';

const defaultPrizes = (minigame as unknown as MinigameData).prizes;

/** Fixed coin amounts per tier (not in the content file): easy guarantees progress, hard is prestige. */
export const PRIZE_COINS: Record<Level, number> = { easy: 10, medium: 20, hard: 40 };

/** Flags written for each tier. The first one is the "already claimed" marker. */
export const PRIZE_FLAGS: Record<Level, string[]> = {
  easy: ['prize.easy', 'cosmetic.scarf_blue', 'unlock.lesson02', 'power.messenger_voice'],
  medium: ['prize.medium', 'cosmetic.hat_weaver_blue', 'upgrade.needle_range'],
  hard: ['prize.hard', 'cosmetic.cloak_gold', 'badge.network_weaver'],
};
export const FLAWLESS_FLAG = 'badge.good_evening';

export function prizeFor(level: Level, prizes: MinigameData['prizes'] = defaultPrizes): Prize {
  return prizes[level];
}

export interface PrizeOutcome { granted: boolean; coins: number; flawlessBadge: boolean }

/** Deterministic, first pass only. The hard level also has a one-time badge for a run with no lost life. */
export function applyPrize(save: SaveStore, level: Level, opts: { flawless?: boolean } = {}): PrizeOutcome {
  const flags = PRIZE_FLAGS[level];
  const marker = flags[0] as string;
  const first = !save.hasFlag(marker);
  if (first) {
    save.data.coins += PRIZE_COINS[level];
    for (const f of flags) save.data.flags[f] = true;
  }
  const badge = level === 'hard' && !!opts.flawless && !save.hasFlag(FLAWLESS_FLAG);
  if (badge) save.data.flags[FLAWLESS_FLAG] = true;
  if (first || badge) save.save();
  return { granted: first, coins: first ? PRIZE_COINS[level] : 0, flawlessBadge: badge };
}
