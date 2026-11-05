import { WORLD_CREATURES, WORLD_ITEMS, WORLD_NPC_INFO } from '../content/world';
import type { CreatureMode, CreatureSpawn } from './creatures';
import type { NpcDef, PickupDef } from './layout';
import { REGIONS, inSea, regionAt } from './regions';

/** Buildings of the big valley (see specs/connected-valley/02_world_manifest.md). Art comes from buildings2a/2b. */
export interface WorldBuilding {
  id: string;
  atlas: 'buildings2a' | 'buildings2b';
  x: number;
  y: number;
  door: { x: number; y: number };
  name: string;
  /** Blocked footprint as a share of the sprite width. */
  footW?: number;
}

export const WORLD_BUILDINGS: WorldBuilding[] = [
  { id: 'inn', atlas: 'buildings2a', x: 3050, y: 620, door: { x: 3040, y: 690 }, name: 'אכסניית הפנס' },
  { id: 'bell_tower', atlas: 'buildings2a', x: 3700, y: 420, door: { x: 3700, y: 486 }, name: 'מגדל הפעמון', footW: 0.5 },
  { id: 'tailor', atlas: 'buildings2a', x: 3560, y: 820, door: { x: 3556, y: 886 }, name: 'חנות החייט' },
  { id: 'school', atlas: 'buildings2a', x: 2850, y: 1020, door: { x: 2846, y: 1086 }, name: 'בית הספר' },
  { id: 'fisher', atlas: 'buildings2a', x: 3150, y: 1960, door: { x: 3146, y: 2026 }, name: 'בית הדייג' },
  { id: 'workshop', atlas: 'buildings2a', x: 3700, y: 1650, door: { x: 3696, y: 1716 }, name: 'בית המלאכה' },
  { id: 'library', atlas: 'buildings2a', x: 3800, y: 2350, door: { x: 3796, y: 2416 }, name: 'ספריית הסלילים' },
  { id: 'observatory', atlas: 'buildings2a', x: 5300, y: 420, door: { x: 5296, y: 486 }, name: 'מצפה הכוכבים' },
  { id: 'stories', atlas: 'buildings2b', x: 4700, y: 980, door: { x: 4696, y: 1046 }, name: 'אולם הסיפורים' },
  { id: 'farm', atlas: 'buildings2b', x: 1150, y: 2250, door: { x: 1146, y: 2316 }, name: 'החווה' },
  { id: 'shepherd', atlas: 'buildings2b', x: 1900, y: 2500, door: { x: 1896, y: 2566 }, name: 'צריף הרועה' },
  { id: 'herbs', atlas: 'buildings2b', x: 400, y: 2550, door: { x: 396, y: 2616 }, name: 'גן העשבים' },
  { id: 'fairy', atlas: 'buildings2b', x: 1000, y: 3500, door: { x: 996, y: 3566 }, name: 'בית העץ של הפיות', footW: 0.4 },
  { id: 'guild', atlas: 'buildings2b', x: 2500, y: 3250, door: { x: 2496, y: 3316 }, name: 'אולם הגילדה' },
  { id: 'lighthouse', atlas: 'buildings2b', x: 4300, y: 3470, door: { x: 4300, y: 3540 }, name: 'המגדלור', footW: 0.35 },
  { id: 'great_tower', atlas: 'buildings2b', x: 5200, y: 2200, door: { x: 5200, y: 2290 }, name: 'הצריח הגדול', footW: 0.4 },
];

/** Each world NPC has their own sheet: speaker key in camelCase -> w_snake_case. */
const sheetFor = (speaker: string): string => `w_${speaker.replace(/([A-Z])/g, '_$1').toLowerCase()}`;

/** Where villagers without a house stand. */
const VILLAGER_SPOT: Record<string, { x: number; y: number }> = {
  bellBoy: { x: 3380, y: 790 }, cakeLady: { x: 3230, y: 640 }, boatKid: { x: 3080, y: 1830 }, fireflyGirl: { x: 4950, y: 760 },
  dyer: { x: 620, y: 2300 }, spoolWoman: { x: 1500, y: 2480 }, bridgeBuilder: { x: 1200, y: 3300 }, dockHand: { x: 4800, y: 3470 },
};

export const WORLD_NPCS: NpcDef[] = WORLD_NPC_INFO.map((n) => {
  const b = n.house ? WORLD_BUILDINGS.find((x) => x.id === n.house) : undefined;
  const spot = b ? { x: b.door.x + 70, y: b.door.y + 24 } : (VILLAGER_SPOT[n.speaker] ?? { x: 3300, y: 800 });
  return { id: n.id, x: spot.x, y: spot.y, speaker: n.speaker, label: n.label, char: `npc_${sheetFor(n.speaker)}` };
});

export interface WorldProp { frame: string; x: number; y: number; scale?: number; block?: number }

function ring(frame: string, cx: number, cy: number, rx: number, ry: number, n: number, scale = 1, block = 0): WorldProp[] {
  return Array.from({ length: n }, (_, i) => {
    const a = (i / n) * Math.PI * 2;
    return { frame, x: cx + Math.cos(a) * rx, y: cy + Math.sin(a) * ry, scale, block };
  });
}

/** Landmarks and scenery from props2: hand-placed, plus a few seeded scatters. */
export const WORLD_PROPS: WorldProp[] = [
  // market square
  { frame: 'fountain', x: 3240, y: 560, scale: 1, block: 46 },
  { frame: 'market_stall_b', x: 3140, y: 760, scale: 1, block: 44 },
  { frame: 'market_stall_c', x: 3440, y: 740, scale: 1, block: 44 },
  { frame: 'market_stall_d', x: 3380, y: 600, scale: 1, block: 44 },
  { frame: 'lantern_post_b', x: 3180, y: 690 }, { frame: 'lantern_post_b', x: 3400, y: 690 }, { frame: 'lantern_post_b', x: 2900, y: 810 },
  { frame: 'signpost_b', x: 3280, y: 830 }, { frame: 'signpost_b', x: 2640, y: 960 },
  { frame: 'barrel', x: 3000, y: 700, block: 24 }, { frame: 'crate_stack', x: 3640, y: 900, block: 28 },
  // moor: standing stones, a stone circle, rocks
  { frame: 'stone_circle', x: 5000, y: 930, scale: 1.1, block: 90 },
  ...ring('standing_stone', 5000, 930, 330, 170, 11, 1, 18),
  ...ring('standing_stone', 5560, 1100, 170, 100, 6, 1, 18),
  { frame: 'rock_a', x: 4400, y: 300, block: 30 }, { frame: 'rock_b', x: 4600, y: 1250, block: 30 }, { frame: 'rock_a', x: 5800, y: 520, block: 30 },
  { frame: 'rock_b', x: 5200, y: 1300, block: 30 }, { frame: 'rock_a', x: 4300, y: 760, block: 30 },
  // mill valley
  { frame: 'reeds', x: 1740, y: 1560 }, { frame: 'reeds', x: 1700, y: 1760 }, { frame: 'reeds', x: 1790, y: 2010 },
  { frame: 'boat', x: 3000, y: 1980, block: 34 }, { frame: 'barrel', x: 3240, y: 2030, block: 24 }, { frame: 'crate_stack', x: 3770, y: 1720, block: 28 },
  { frame: 'rock_a', x: 3900, y: 1500, block: 30 }, { frame: 'rock_b', x: 2800, y: 2200, block: 30 },
  // orchard
  { frame: 'haystack', x: 1300, y: 2400, block: 40 }, { frame: 'hay_bale', x: 1050, y: 2330, block: 26 }, { frame: 'hay_bale', x: 1230, y: 2380, block: 26 },
  { frame: 'scarecrow', x: 600, y: 2200, block: 20 }, { frame: 'scarecrow', x: 1700, y: 2300, block: 20 },
  { frame: 'flower_bush', x: 330, y: 2620 }, { frame: 'flower_bush', x: 470, y: 2640 }, { frame: 'flower_bush', x: 1860, y: 2610 },
  { frame: 'hay_bale', x: 1990, y: 2560, block: 26 }, { frame: 'signpost_b', x: 900, y: 2760 },
  // whisper woods
  { frame: 'fairy_door_tree', x: 600, y: 3300, scale: 1.1, block: 40 }, { frame: 'fairy_door_tree', x: 1350, y: 3800, scale: 1.1, block: 40 },
  { frame: 'giant_tree_hollow', x: 300, y: 3700, block: 70 }, { frame: 'giant_tree_hollow', x: 1500, y: 3250, block: 70 },
  ...ring('mushroom_ring', 800, 3700, 230, 110, 4, 1, 0),
  { frame: 'rock_a', x: 1600, y: 3600, block: 30 },
  // coast: harbour, reeds at the stream mouth, rocks
  { frame: 'dock_segment', x: 4760, y: 3560 }, { frame: 'dock_segment', x: 4850, y: 3560 }, { frame: 'dock_segment', x: 4940, y: 3560 },
  { frame: 'boat', x: 4700, y: 3600, block: 34 }, { frame: 'boat', x: 5050, y: 3600, block: 34 },
  { frame: 'reeds', x: 2330, y: 3520 }, { frame: 'reeds', x: 2420, y: 3560 }, { frame: 'reeds', x: 2480, y: 3510 },
  { frame: 'barrel', x: 4860, y: 3490, block: 24 }, { frame: 'crate_stack', x: 4960, y: 3500, block: 28 },
  { frame: 'rock_a', x: 3300, y: 3560, block: 30 }, { frame: 'rock_b', x: 5600, y: 3520, block: 30 }, { frame: 'rock_a', x: 3900, y: 3520, block: 30 },
  // gate of the great tower (locked until the end): a line of stones and fence
  ...Array.from({ length: 6 }, (_, i): WorldProp => ({ frame: 'standing_stone', x: 4170, y: 2040 + i * 80, block: 18 })),
  { frame: 'signpost_b', x: 4140, y: 2250 },
];

/** Where a card, diary page or curiosity lies: near its house, or at a fixed spot in its region. */
const CURIO_SPOT: Record<string, { x: number; y: number }> = {
  market: { x: 3500, y: 520 }, moor: { x: 4800, y: 400 }, orchard: { x: 700, y: 2050 },
  hearth: { x: 1560, y: 760 }, mill: { x: 3050, y: 2300 }, woods: { x: 700, y: 3600 }, coast: { x: 3400, y: 3300 },
};

export const WORLD_PICKUPS: PickupDef[] = (() => {
  const perHouse = new Map<string, number>();
  const seen = new Map<string, number>();
  return WORLD_ITEMS.filter((it) => !it.objectId).map((it): PickupDef => {
    const b = it.houseId ? WORLD_BUILDINGS.find((x) => x.id === it.houseId) : undefined;
    let x: number;
    let y: number;
    if (b) {
      const i = perHouse.get(b.id) ?? 0;
      perHouse.set(b.id, i + 1);
      x = b.door.x - 120 + i * 90;
      y = b.door.y + 60 + (i % 2) * 30;
    } else {
      const base = CURIO_SPOT[it.region] ?? { x: 3000, y: 1500 };
      const i = seen.get(it.region) ?? 0;
      seen.set(it.region, i + 1);
      x = base.x + i * 130;
      y = base.y + (i % 2) * 60;
    }
    return { id: it.id, x, y, kind: it.kind };
  });
})();

export function regionName(x: number, y: number): string {
  return regionAt(x, y)?.name ?? REGIONS[0]?.name ?? '';
}

export function validSpot(x: number, y: number): boolean {
  return !inSea(x, y);
}

/** Where the new creatures live: free spots near the roads of their region, in the order of the content file. */
const SPOTS: Record<string, Array<{ x: number; y: number }>> = {
  hearth: [{ x: 1500, y: 1250 }, { x: 900, y: 1250 }],
  market: [{ x: 3500, y: 500 }, { x: 3000, y: 950 }, { x: 3800, y: 1000 }],
  moor: [{ x: 4600, y: 600 }, { x: 5400, y: 700 }, { x: 4900, y: 1250 }],
  mill: [{ x: 3350, y: 2000 }, { x: 3100, y: 2300 }, { x: 3900, y: 1900 }, { x: 3000, y: 1700 }],
  orchard: [{ x: 500, y: 2300 }, { x: 1500, y: 2600 }, { x: 2100, y: 2200 }, { x: 900, y: 2650 }],
  woods: [{ x: 700, y: 3400 }, { x: 1200, y: 3700 }, { x: 1400, y: 3350 }],
  coast: [{ x: 3200, y: 3250 }, { x: 4000, y: 3250 }, { x: 4700, y: 3350 }, { x: 5400, y: 3300 }],
};
const FLIERS = new Set(['count_butterfly', 'handshake_dove']);
const SITTERS = new Set(['address_turtle', 'queue_squirrel', 'bit_rabbit']);

export const WORLD_CREATURE_SPAWNS: CreatureSpawn[] = (() => {
  const used = new Map<string, number>();
  return Object.entries(WORLD_CREATURES).map(([name, c]): CreatureSpawn => {
    const info = c as { region: string; timeOfDay: string; legendary: boolean };
    const i = used.get(info.region) ?? 0;
    used.set(info.region, i + 1);
    const list = SPOTS[info.region] ?? [{ x: 3300, y: 800 }];
    const spot = list[i % list.length] as { x: number; y: number };
    const night = info.timeOfDay === 'night';
    const mode: CreatureMode = info.legendary ? 'static' : FLIERS.has(name) ? (night ? 'night-fly' : 'fly') : SITTERS.has(name) ? 'sit' : night ? 'night-wander' : 'wander';
    return { key: `wc_${name}`, x: spot.x + (info.legendary ? 0 : 60), y: spot.y, mode, radius: mode === 'fly' || mode === 'night-fly' ? 220 : 90, legendary: info.legendary };
  });
})();
