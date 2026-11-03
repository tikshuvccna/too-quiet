/** Hearth village (כפר האח): the demo area. All coordinates are world pixels. */
import type { CharKey } from '../scenes/BootScene';

export const WORLD = { w: 2600, h: 1900 } as const;

export type BuildingFrame = 'cottage_shoshana' | 'clinic' | 'print_house' | 'bakery' | 'mill' | 'tower';

export interface BuildingDef {
  id: string;
  frame: BuildingFrame;
  /** Ground contact point (footprint centre) of the sprite. */
  x: number;
  y: number;
  scale: number;
  /** Walkable spot in front of the door. */
  door: { x: number; y: number };
  label: string;
  /** Size of the blocked footprint, in world px. */
  foot: { w: number; h: number };
}

export interface NpcDef {
  id: string;
  x: number;
  y: number;
  speaker: string;
  label: string;
  char: CharKey;
  tint?: number;
  scale?: number;
}

export interface PickupDef {
  id: string;
  x: number;
  y: number;
  kind: 'card' | 'diary' | 'curio';
  /** Only shown once this story flag is set. */
  requires?: string;
}

export type FaultType = 'cut' | 'tangled' | 'loose' | 'overloaded';

export interface FaultDef {
  id: string;
  x: number;
  y: number;
  type: FaultType;
  /** Needle power (number of finished lessons) needed to mend it. */
  needsPower: number;
  evidence: 'natural' | 'hand';
  label: string;
  note: string;
}

export interface ThreadDef { id: string; a: { x: number; y: number }; b: { x: number; y: number }; faultId?: string }

export interface DecorDef { frame: string; x: number; y: number; scale?: number; block?: number }

export interface SpotDef { id: string; x: number; y: number; label: string; range?: number }

export const BUILDINGS: BuildingDef[] = [
  { id: 'house-grandma', frame: 'cottage_shoshana', x: 760, y: 870, scale: 1, door: { x: 742, y: 936 }, label: 'כניסה לבית סבתא שושנה', foot: { w: 270, h: 70 } },
  { id: 'house-clinic', frame: 'clinic', x: 1280, y: 750, scale: 1, door: { x: 1268, y: 818 }, label: 'כניסה למרפאה', foot: { w: 290, h: 72 } },
  { id: 'house-print', frame: 'print_house', x: 560, y: 1430, scale: 1, door: { x: 556, y: 1500 }, label: 'כניסה לבית הדפוס', foot: { w: 270, h: 72 } },
  { id: 'bakery', frame: 'bakery', x: 1780, y: 890, scale: 1, door: { x: 1756, y: 956 }, label: 'המאפייה', foot: { w: 290, h: 70 } },
  { id: 'mill', frame: 'mill', x: 2180, y: 1430, scale: 1, door: { x: 2172, y: 1498 }, label: 'הטחנה', foot: { w: 200, h: 70 } },
  { id: 'tower', frame: 'tower', x: 2180, y: 560, scale: 0.9, door: { x: 2180, y: 626 }, label: 'מגדל האורגים', foot: { w: 170, h: 78 } },
];

export const NPCS: NpcDef[] = [
  { id: 'baker', x: 1700, y: 1000, speaker: 'baker', label: 'לדבר עם הנחתום', char: 'apprentice_boy', tint: 0xffd9a0 },
  { id: 'villager1', x: 1030, y: 1060, speaker: 'villager1', label: 'לדבר עם התושב', char: 'apprentice_boy', tint: 0xb8d8ff },
  { id: 'villager2', x: 1510, y: 1020, speaker: 'villager2', label: 'לדבר עם התושבת', char: 'apprentice_girl', tint: 0xd8ffd0 },
  { id: 'villager3', x: 930, y: 1190, speaker: 'villager3', label: 'לדבר עם התושב', char: 'apprentice_boy', tint: 0xffc8d8 },
  { id: 'child', x: 1450, y: 1150, speaker: 'child', label: 'לדבר עם הילד', char: 'apprentice_boy', tint: 0xfff0b0, scale: 0.72 },
  { id: 'hubGrandpa', x: 1250, y: 1330, speaker: 'hubGrandpa', label: 'לדבר עם סבא הד', char: 'dvora', tint: 0xc8d890 },
  { id: 'miller', x: 2090, y: 1500, speaker: 'miller', label: 'לדבר עם הטוחן', char: 'apprentice_boy', tint: 0xe8e0d0 },
  { id: 'dvora', x: 2110, y: 650, speaker: 'dvora', label: 'לדבר עם דבורה', char: 'dvora' },
];

export const PICKUPS: PickupDef[] = [
  { id: 'card_network', x: 1130, y: 1110, kind: 'card' },
  { id: 'card_lan_preview', x: 1060, y: 1170, kind: 'card' },
  { id: 'cur_bell', x: 1130, y: 870, kind: 'curio' },
  { id: 'card_client', x: 1740, y: 1050, kind: 'card' },
  { id: 'diary_2', x: 1880, y: 1000, kind: 'diary' },
  { id: 'cur_sock', x: 1920, y: 910, kind: 'curio' },
  { id: 'cur_spoon', x: 1680, y: 870, kind: 'curio' },
  { id: 'cur_sleep_messenger', x: 1840, y: 1050, kind: 'curio' },
  { id: 'card_live', x: 2090, y: 1420, kind: 'card' },
  { id: 'cur_red_spool', x: 2060, y: 690, kind: 'curio' },
  { id: 'diary_4', x: 1320, y: 1400, kind: 'diary' },
  { id: 'diary_5', x: 2010, y: 1330, kind: 'diary', requires: 'clue1_clean_cut' },
];

export const FAULTS: FaultDef[] = [
  { id: 'fault-root', x: 1020, y: 800, type: 'cut', needsPower: 1, evidence: 'natural', label: 'שורש עץ על החוט', note: 'שורש שגדל מעל החוט. טבעי.' },
  { id: 'fault-mice', x: 1530, y: 830, type: 'loose', needsPower: 1, evidence: 'natural', label: 'עכברים כירסמו את החוט', note: 'סימני שיניים קטנים. טבעי.' },
  { id: 'fault-knot', x: 1880, y: 740, type: 'cut', needsPower: 1, evidence: 'hand', label: 'חיתוך נקי וקשר בשני סיבובים', note: 'חיתוך חלק, וקשר שאורגים קושרים. זה לא טבעי.' },
];

export const THREADS: ThreadDef[] = [
  { id: 't1', a: { x: 760, y: 700 }, b: { x: 1280, y: 580 } },
  { id: 't2', a: { x: 1280, y: 580 }, b: { x: 1780, y: 720 }, faultId: 'fault-mice' },
  { id: 't3', a: { x: 760, y: 700 }, b: { x: 760, y: 1000 }, faultId: 'fault-root' },
  { id: 't4', a: { x: 1780, y: 720 }, b: { x: 2180, y: 420 }, faultId: 'fault-knot' },
  { id: 't5', a: { x: 1280, y: 580 }, b: { x: 1250, y: 1200 } },
];

export const DECOR: DecorDef[] = [
  { frame: 'well', x: 1400, y: 1110, scale: 1.1, block: 36 },
  { frame: 'market_stall', x: 1090, y: 1130, scale: 1.1, block: 44 },
  { frame: 'lamppost', x: 1190, y: 1000, scale: 1.1 },
  { frame: 'lamppost', x: 1380, y: 1000, scale: 1.1 },
  { frame: 'lamppost', x: 1700, y: 1000, scale: 1.1 },
  { frame: 'lamppost', x: 1280, y: 1250, scale: 1.1 },
  { frame: 'signpost', x: 1000, y: 1000, scale: 1.1 },
  { frame: 'signpost', x: 2000, y: 900, scale: 1.1 },
  { frame: 'fence', x: 640, y: 960, scale: 1.1 },
  { frame: 'fence', x: 860, y: 960, scale: 1.1 },
  { frame: 'fence', x: 1700, y: 970, scale: 1.1 },
];

/** Story spots that are not objects: the bridge over the stream where the first clue waits. */
export const SPOTS: SpotDef[] = [
  { id: 'bridge', x: 1960, y: 1290, label: 'להסתכל על החוט שעל הגשר', range: 110 },
];

/** Footprints (world px) that block walking: [x, y, w, h], from each building's ground area. */
export function wallRects(): Array<[number, number, number, number]> {
  return BUILDINGS.map((b) => [b.x - b.foot.w / 2, b.y - b.foot.h + 8, b.foot.w, b.foot.h] as [number, number, number, number]);
}

export const TOWER_SPAWN = { x: 2130, y: 640 };
export const START_SPAWN = { x: 1280, y: 1040 };
