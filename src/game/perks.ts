import type { SaveStore } from '../core/save';

/**
 * What the player has earned that changes how the game feels. Everything is a plain flag on the save,
 * set by the shop or by a mini-game prize, so it survives reloads and never depends on chance.
 */
export interface Perks {
  /** Multiplier on how far the player can reach things. */
  reach: number;
  /** Distance within which the needle shows a fault's label. */
  faultRadius: number;
  /** Extra seconds before the storm sends the player to the tower. */
  timeBonus: number;
  /** Speed multiplier. */
  speed: number;
  /** Multiplier on coins found in trees and won in side games. */
  coinMul: number;
  /** Multiplier on the distance from which tree glints show. */
  glintMul: number;
}

export function perksOf(save: SaveStore): Perks {
  const voice = save.hasFlag('power.messenger_voice');
  const needle = save.hasFlag('upgrade.needle_range');
  const has = (f: string): number => (save.hasFlag(f) ? 1 : 0);
  return {
    reach: (voice ? 1.3 : 1) * (has('perk.long_arms') ? 1.2 : 1),
    faultRadius: (needle ? 300 : 190) + has('perk.thread_sense') * 120,
    timeBonus: (save.hasFlag('shop.extra_time') ? 60 : 0) + (needle ? 30 : 0) + has('perk.long_breath_03') * 45 + has('perk.long_breath_05') * 45,
    speed: (save.hasFlag('shop.boots') ? 1.12 : 1) * (has('perk.sure_feet') ? 1.08 : 1) * (has('perk.light_steps') ? 1.08 : 1),
    coinMul: has('perk.coin_pouch') ? 1.25 : 1,
    glintMul: has('perk.keen_eyes') ? 1.5 : 1,
  };
}
