import linesJson from '../../content/he/lines.json';
import scenesJson from '../../content/he/scenes.json';
import housesJson from '../../content/he/houses.json';
import collectiblesJson from '../../content/he/collectibles.json';

export interface LineDef { speaker: string; text: string; textF?: string }

export type SceneStep =
  | { line: string }
  | { flag: string }
  | { cutscene: string }
  | { choice: { prompt: string; options: Array<{ text: string; goto: string }> } };

export interface SceneDef { title: string; where: string; steps: SceneStep[]; next?: string }

export interface HouseObjectDef { id: string; name: string; text: string }

export interface HouseDef {
  id: string;
  name: string;
  owner: string;
  look: string;
  mystery: string;
  networkNeed: { story: string };
  objects: HouseObjectDef[];
  threadSightClue: string;
}

export interface ConceptCard { id: string; name: string; nameEn: string; concept: string; where: string }
export interface DiaryPage { id: string; order: number; text: string; where: string }
export interface Curiosity { id: string; name: string; description: string; where: string }

export interface CollectibleSet { conceptCards: ConceptCard[]; diaryPages: DiaryPage[]; curiosities: Curiosity[] }

export const LINES = linesJson as unknown as Record<string, LineDef>;
export const SCENES = scenesJson as unknown as Record<string, SceneDef>;
export const HOUSES = (housesJson as unknown as { houses: HouseDef[] }).houses;
export const COLLECTIBLES = collectiblesJson as unknown as CollectibleSet;

/** Names shown on the subtitle box. Narrator has no name box. */
export const SPEAKER_NAMES: Record<string, string> = {
  narrator: '',
  player: 'אני',
  dvora: 'דבורה האורגת',
  baker: 'הנחתום',
  miller: 'הטוחן',
  grandma: 'סבתא שושנה',
  clinicDoctor: 'רופאת הכפר',
  child: 'הילד',
  villager1: 'תושב',
  villager2: 'תושבת',
  villager3: 'תושב',
  hubGrandpa: 'סבא הד',
};

/** Which layout building opens which house file. */
export const HOUSE_FOR_BUILDING: Record<string, string> = {
  'house-grandma': 'house_grandma',
  'house-clinic': 'house_clinic',
  'house-print': 'house_print',
};

/**
 * Collectibles hidden inside houses, found by inspecting a given object.
 * (The content files give a place in words; this ties each one to an object.)
 */
export const ITEMS_IN_OBJECT: Record<string, string[]> = {
  'house_grandma:g_tablet': ['card_host_use', 'card_p2p'],
  'house_grandma:g_cookies': ['card_stream'],
  'house_grandma:g_scarf': ['diary_1'],
  'house_clinic:c_password': ['card_auth'],
  'house_clinic:c_notes': ['card_server'],
  'house_print:p_box': ['card_soho'],
  'house_print:p_pc_yoel': ['card_share_files'],
  'house_print:p_printer': ['card_share_equipment'],
  'house_print:p_stack': ['diary_3'],
  'house_print:p_cal': ['cur_hourglass'],
};

export interface ItemInfo { id: string; kind: 'card' | 'diary' | 'curio'; title: string; text: string }

export function allItems(): ItemInfo[] {
  return [
    ...COLLECTIBLES.conceptCards.map((c): ItemInfo => ({ id: c.id, kind: 'card', title: c.name, text: c.concept })),
    ...COLLECTIBLES.diaryPages.map((d): ItemInfo => ({ id: d.id, kind: 'diary', title: `דף יומן ${d.order}`, text: d.text })),
    ...COLLECTIBLES.curiosities.map((c): ItemInfo => ({ id: c.id, kind: 'curio', title: c.name, text: c.description })),
  ];
}

export function itemById(id: string): ItemInfo | undefined {
  return allItems().find((i) => i.id === id);
}

export function lineOf(id: string): LineDef {
  const l = LINES[id];
  if (!l) throw new Error(`missing line ${id}`);
  return l;
}
