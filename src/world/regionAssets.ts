import { WORLD_BUILDINGS, WORLD_CREATURE_SPAWNS, WORLD_NPCS, WORLD_PROPS } from './worldMap';
import { REGIONS, regionAt, type RegionDef } from './regions';

export interface AtlasLoad { key: string; png: string; json: string }
export interface JsonLoad { key: string; url: string }

export interface RegionLoad {
  atlases: AtlasLoad[];
  jsons: JsonLoad[];
  /** Sheet names (without the npc_ prefix) and creature keys whose animations must be created after loading. */
  npcSheets: string[];
  creatures: string[];
}

const BUILDING_ATLASES = ['buildings2a', 'buildings2b'] as const;

/** Everything one region needs on top of the core assets: its buildings, scenery, villagers and creatures. */
export function loadsForRegion(id: string, base: string): RegionLoad {
  const out: RegionLoad = { atlases: [], jsons: [], npcSheets: [], creatures: [] };
  const inRegion = (x: number, y: number): boolean => regionAt(x, y)?.id === id;
  const atlasSet = new Set<string>();
  for (const b of WORLD_BUILDINGS) if (inRegion(b.x, b.y)) atlasSet.add(b.atlas);
  for (const a of BUILDING_ATLASES) {
    if (!atlasSet.has(a)) continue;
    out.atlases.push({ key: a, png: `${base}assets/buildings/${a}.png`, json: `${base}assets/buildings/${a}.json` });
    out.atlases.push({ key: `${a}_truth`, png: `${base}assets/buildings/${a}_truth.png`, json: `${base}assets/buildings/${a}_truth.json` });
    out.jsons.push({ key: `${a}:meta`, url: `${base}assets/buildings/${a}.json` });
  }
  if (WORLD_PROPS.some((p) => inRegion(p.x, p.y))) {
    out.atlases.push({ key: 'props2', png: `${base}assets/props/props2.png`, json: `${base}assets/props/props2.json` });
    out.atlases.push({ key: 'props2_truth', png: `${base}assets/props/props2_truth.png`, json: `${base}assets/props/props2_truth.json` });
    out.jsons.push({ key: 'props2:meta', url: `${base}assets/props/props2.json` });
  }
  for (const n of WORLD_NPCS) {
    if (!inRegion(n.x, n.y)) continue;
    const sheet = n.char.replace(/^npc_/, '');
    out.npcSheets.push(sheet);
    out.atlases.push({ key: n.char, png: `${base}assets/characters_v2/npcs/${sheet}.png`, json: `${base}assets/characters_v2/npcs/${sheet}.json` });
  }
  for (const c of WORLD_CREATURE_SPAWNS) {
    if (!inRegion(c.x, c.y)) continue;
    out.creatures.push(c.key);
    out.atlases.push({ key: `cr_${c.key}`, png: `${base}assets/creatures/${c.key}.png`, json: `${base}assets/creatures/${c.key}.json` });
    out.jsons.push({ key: `cr_${c.key}:anims`, url: `${base}assets/creatures/${c.key}.json` });
  }
  return out;
}

/** Distance from a point to a region's rectangle (0 inside it). */
export function distanceToRegion(r: RegionDef, x: number, y: number): number {
  const [rx, ry, rw, rh] = r.rect;
  const dx = Math.max(rx - x, 0, x - (rx + rw));
  const dy = Math.max(ry - y, 0, y - (ry + rh));
  return Math.hypot(dx, dy);
}

export const ALL_REGION_IDS = REGIONS.map((r) => r.id);
