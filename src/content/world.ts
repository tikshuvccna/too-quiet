import linesJson from '../../content/he/world/lines_world.json';
import speakersJson from '../../content/he/world/speakers_world.json';
import npcsJson from '../../content/he/world/npcs_world.json';
import collectiblesJson from '../../content/he/world/collectibles_world.json';
import creaturesJson from '../../content/he/world/creatures_world.json';
import housesJson from '../../content/he/world/houses_world.json';

export interface WorldLine { speaker: string; text: string; textF?: string; conv?: 'a' | 'b' }

export interface WorldNpcInfo {
  id: string;
  role: string;
  house: string | null;
  region: string;
  speaker: string;
  label: string;
  miniGame: string | null;
}

export interface WorldItem {
  id: string;
  kind: 'card' | 'diary' | 'curio';
  title: string;
  text: string;
  region: string;
  houseId: string | null;
  objectId: string | null;
}

export const WORLD_HOUSES = (housesJson as unknown as { houses: Array<{ id: string; name: string; owner: string; look: string; mystery: string; networkNeed: { story: string }; objects: Array<{ id: string; name: string; text: string }>; threadSightClue: string }> }).houses;

export const WORLD_LINES = linesJson as unknown as Record<string, WorldLine>;
export const WORLD_SPEAKERS = speakersJson as unknown as Record<string, string>;
export const WORLD_NPC_INFO = (npcsJson as unknown as { npcs: WorldNpcInfo[] }).npcs;
export const WORLD_CREATURES = (creaturesJson as unknown as { creatures: Record<string, unknown> }).creatures;

interface RawCollectibles {
  conceptCards: Array<{ id: string; name: string; concept: string; region: string; houseId: string | null; objectId?: string }>;
  diaryPages: Array<{ id: string; order: number; text: string; region: string; houseId: string | null; objectId?: string }>;
  curiosities: Array<{ id: string; name: string; description: string; region: string; houseId: string | null; objectId?: string }>;
}
const raw = collectiblesJson as unknown as RawCollectibles;

export const WORLD_ITEMS: WorldItem[] = [
  ...raw.conceptCards.map((c): WorldItem => ({ id: c.id, kind: 'card', title: c.name, text: c.concept, region: c.region, houseId: c.houseId, objectId: c.objectId ?? null })),
  ...raw.diaryPages.map((d): WorldItem => ({ id: d.id, kind: 'diary', title: `דף יומן ${d.order}`, text: d.text, region: d.region, houseId: d.houseId, objectId: d.objectId ?? null })),
  ...raw.curiosities.map((c): WorldItem => ({ id: c.id, kind: 'curio', title: c.name, text: c.description, region: c.region, houseId: c.houseId, objectId: c.objectId ?? null })),
];

/**
 * What an owner says. Owners get their own lines plus the player's replies from the same house;
 * villagers only their own. First visit plays conversation "a"; later visits play "b" when it exists.
 */
export function conversationFor(npc: WorldNpcInfo, visit: 'first' | 'later'): string[] {
  const key = npc.house ?? npc.region;
  const own = Object.entries(WORLD_LINES).filter(([id, l]) => id.startsWith(`w1.${key}.`) && (l.speaker === npc.speaker || (npc.house !== null && l.speaker === 'player')));
  const want = visit === 'later' && own.some(([, l]) => l.conv === 'b') ? 'b' : 'a';
  return own.filter(([, l]) => (l.conv ?? 'a') === want).map(([id]) => id);
}
