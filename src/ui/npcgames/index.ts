import { BELL_GAME } from './bell';
import { BOATS_GAME } from './boats';
import { BRIDGE_GAME } from './bridge';
import { CAKE_GAME } from './cake';
import { DYE_GAME } from './dye';
import { FIREFLIES_GAME } from './fireflies';
import { FISHING_GAME } from './fishing';
import type { NpcGameDef } from './framework';
import { SPOOLS_GAME } from './spools';

export { openNpcGame } from './framework';

/** Which NPC offers which little game. */
export const NPC_GAMES: Record<string, NpcGameDef> = {
  npc_bellBoy: BELL_GAME,
  npc_fisher: FISHING_GAME,
  npc_boatKid: BOATS_GAME,
  npc_spoolWoman: SPOOLS_GAME,
  npc_dyer: DYE_GAME,
  npc_fireflyGirl: FIREFLIES_GAME,
  npc_cakeLady: CAKE_GAME,
  npc_bridgeBuilder: BRIDGE_GAME,
};
