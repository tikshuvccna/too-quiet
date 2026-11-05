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
}

export function perksOf(save: SaveStore): Perks {
  const voice = save.hasFlag('power.messenger_voice');
  const needle = save.hasFlag('upgrade.needle_range');
  return {
    reach: voice ? 1.3 : 1,
    faultRadius: needle ? 300 : 190,
    timeBonus: (save.hasFlag('shop.extra_time') ? 60 : 0) + (needle ? 30 : 0),
    speed: save.hasFlag('shop.boots') ? 1.12 : 1,
  };
}
