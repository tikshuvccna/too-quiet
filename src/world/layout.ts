/** Hearth village (כפר האח): the demo area. All coordinates are world pixels. */
export const WORLD = { w: 2600, h: 1900 } as const;

export interface BuildingDef {
  id: string;
  kind: 'cottage_a' | 'cottage_b' | 'cottage_c' | 'tower';
  x: number; // bottom-centre of the sprite
  y: number;
  door: { x: number; y: number };
  label: string;
}

export interface NpcDef { id: string; x: number; y: number; speaker: string; label: string }
export interface PickupDef { id: string; x: number; y: number; kind: 'card' | 'page' | 'curio' }

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

export const BUILDINGS: BuildingDef[] = [
  { id: 'house-grandma', kind: 'cottage_a', x: 760, y: 880, door: { x: 760, y: 892 }, label: 'כניסה לבית' },
  { id: 'house-clinic', kind: 'cottage_b', x: 1280, y: 760, door: { x: 1280, y: 772 }, label: 'כניסה למרפאה' },
  { id: 'house-bakery', kind: 'cottage_c', x: 1780, y: 900, door: { x: 1780, y: 912 }, label: 'כניסה למאפייה' },
  { id: 'tower', kind: 'tower', x: 2180, y: 560, door: { x: 2180, y: 574 }, label: 'מגדל האורגים' },
];

export const NPCS: NpcDef[] = [
  { id: 'baker', x: 1700, y: 990, speaker: 'baker', label: 'לדבר עם הנחתום' },
  { id: 'villager1', x: 1040, y: 1010, speaker: 'villager1', label: 'לדבר' },
  { id: 'child', x: 1440, y: 1130, speaker: 'child', label: 'לדבר עם הילד' },
  { id: 'hubGrandpa', x: 1250, y: 1330, speaker: 'hubGrandpa', label: 'לדבר עם סבא הד' },
  { id: 'dvora', x: 2120, y: 650, speaker: 'dvora', label: 'לדבר עם דבורה' },
];

export const PICKUPS: PickupDef[] = [
  { id: 'card-network', x: 520, y: 1180, kind: 'card' },
  { id: 'card-host', x: 980, y: 540, kind: 'card' },
  { id: 'card-medium', x: 1560, y: 520, kind: 'card' },
  { id: 'page-1', x: 330, y: 760, kind: 'page' },
  { id: 'curio-1', x: 1960, y: 1240, kind: 'curio' },
  { id: 'curio-2', x: 640, y: 1500, kind: 'curio' },
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

/** Footprints (world px) that block walking: [x, y, w, h]. */
export const WALLS: Array<[number, number, number, number]> = [
  [660, 800, 200, 82], [1170, 690, 220, 72], [1670, 820, 220, 82], [2100, 440, 160, 120],
];

/** Where the player stands after arriving by thread storm (in front of the tower door). */
export const TOWER_SPAWN = { x: 2180, y: 640 };
export const START_SPAWN = { x: 1280, y: 1000 };
