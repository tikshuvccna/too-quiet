/** The big valley: regions tile the whole map. Hearth village keeps its original coordinates in the north-west corner. */

export interface RegionDef {
  id: string;
  name: string;
  /** [x, y, w, h] in world px. */
  rect: [number, number, number, number];
  /** Ground colour wash laid over the grass. */
  tint: number;
  tintAlpha: number;
  /** Trees per million square px (outside clearings). */
  trees: number;
  treeStyle: 'mixed' | 'pine' | 'round' | 'rows';
  /** Story flag that must be set before the region can be entered. */
  lockedUntil?: string;
}

export const REGIONS: RegionDef[] = [
  { id: 'hearth', name: 'כפר האח', rect: [0, 0, 2600, 1900], tint: 0x000000, tintAlpha: 0, trees: 26, treeStyle: 'mixed' },
  { id: 'market', name: 'שורת השוק וגבעת הפעמון', rect: [2600, 0, 1600, 1400], tint: 0xd9b46a, tintAlpha: 0.22, trees: 10, treeStyle: 'round' },
  { id: 'moor', name: 'מישור אבני ההד', rect: [4200, 0, 2000, 1500], tint: 0x7a7fa0, tintAlpha: 0.36, trees: 3, treeStyle: 'pine' },
  { id: 'mill', name: 'עמק הטחנה והנחל', rect: [2600, 1400, 1600, 1600], tint: 0x2fa58a, tintAlpha: 0.2, trees: 16, treeStyle: 'mixed' },
  { id: 'tower', name: 'הצריח הגדול', rect: [4200, 1500, 2000, 1500], tint: 0x3a3350, tintAlpha: 0.5, trees: 4, treeStyle: 'pine', lockedUntil: 'final_unlocked' },
  { id: 'orchard', name: 'המטע ושדות הסלילים', rect: [0, 1900, 2600, 1100], tint: 0xc4dc5a, tintAlpha: 0.24, trees: 22, treeStyle: 'rows' },
  { id: 'woods', name: 'יער הלחישות', rect: [0, 3000, 1700, 1000], tint: 0x0b3d2c, tintAlpha: 0.42, trees: 70, treeStyle: 'pine' },
  { id: 'coast', name: 'החוף והמגדלור', rect: [1700, 3000, 4500, 1000], tint: 0xe6d6a0, tintAlpha: 0.3, trees: 5, treeStyle: 'round' },
];

export function regionAt(x: number, y: number): RegionDef | undefined {
  return REGIONS.find((r) => x >= r.rect[0] && x < r.rect[0] + r.rect[2] && y >= r.rect[1] && y < r.rect[1] + r.rect[3]);
}

/** Sea outline along the southern coast. Walking into it is blocked. */
export const SEA: Array<[number, number]> = [
  [1700, 3760], [2300, 3640], [2900, 3700], [3600, 3610], [4300, 3680], [5000, 3580], [5600, 3640], [6200, 3560], [6200, 4000], [1700, 4000],
];

export function inSea(x: number, y: number): boolean {
  let inside = false;
  for (let i = 0, j = SEA.length - 1; i < SEA.length; j = i++) {
    const [xi, yi] = SEA[i] as [number, number];
    const [xj, yj] = SEA[j] as [number, number];
    if (yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
}

/** Stream: from the hills in the east of the village, through the bridge, to the sea. */
export const STREAM: Array<[number, number]> = [
  [2300, 1080], [2140, 1190], [1968, 1292], [1830, 1380], [1740, 1520], [1700, 1780], [1780, 2050], [1950, 2350], [2150, 2750], [2330, 3200], [2400, 3680],
];
