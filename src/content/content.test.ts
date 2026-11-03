import { describe, expect, it } from 'vitest';
import { COLLECTIBLES, HOUSES, HOUSE_FOR_BUILDING, ITEMS_IN_OBJECT, LINES, SCENES, SPEAKER_NAMES, allItems, itemById } from './index';
import { BUILDINGS, FAULTS, NPCS, PICKUPS, THREADS, WORLD } from '../world/layout';
import { STOP_AFTER } from '../game/sceneRunner';

describe('story content', () => {
  it('every scene line exists and every jump resolves', () => {
    for (const [id, scene] of Object.entries(SCENES)) {
      for (const st of scene.steps) {
        if ('line' in st) expect(LINES[st.line], `${id}: ${st.line}`).toBeDefined();
        if ('choice' in st) for (const o of st.choice.options) expect(SCENES[o.goto], `${id} -> ${o.goto}`).toBeDefined();
      }
      if (scene.next) expect(SCENES[scene.next], `${id}.next`).toBeDefined();
    }
  });

  it('every speaker has a display name entry or is the narrator', () => {
    for (const [id, l] of Object.entries(LINES)) expect(SPEAKER_NAMES[l.speaker] !== undefined, `${id}: ${l.speaker}`).toBe(true);
  });

  it('every line is short enough to record', () => {
    for (const [id, l] of Object.entries(LINES)) expect(l.text.split(/\s+/).length, id).toBeLessThanOrEqual(25);
  });

  it('stop-after scenes exist', () => {
    for (const id of STOP_AFTER) expect(SCENES[id], id).toBeDefined();
  });

  it('the story flags the controller reads are actually set by some scene', () => {
    const set = new Set<string>();
    for (const s of Object.values(SCENES)) for (const st of s.steps) if ('flag' in st) set.add(st.flag);
    for (const f of ['start_lesson01', 'lesson01_done', 'fix_grandma_done', 'fix_clinic_done', 'fix_mill_done', 'bakery_fixed', 'p1_complete', 'clue1_clean_cut', 'storm_warned', 'needle_blur_seen', 'neighbours_asked', 'houses_unlocked']) {
      expect(set.has(f), f).toBe(true);
    }
  });
});

describe('collectibles and houses', () => {
  it('has 12 cards, 5 diary pages and 6 curiosities with unique ids', () => {
    expect(COLLECTIBLES.conceptCards).toHaveLength(12);
    expect(COLLECTIBLES.diaryPages).toHaveLength(5);
    expect(COLLECTIBLES.curiosities).toHaveLength(6);
    const ids = allItems().map((i) => i.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it('every item can be found exactly once, either in a house object or as a world pickup', () => {
    const inHouses = Object.values(ITEMS_IN_OBJECT).flat();
    const inWorld = PICKUPS.map((p) => p.id);
    const found = [...inHouses, ...inWorld];
    expect(new Set(found).size).toBe(found.length);
    for (const i of allItems()) expect(found.includes(i.id), `${i.id} is not placed anywhere`).toBe(true);
    for (const id of found) expect(itemById(id), id).toBeDefined();
  });

  it('house objects referenced by the item table exist', () => {
    for (const key of Object.keys(ITEMS_IN_OBJECT)) {
      const [houseId, objId] = key.split(':') as [string, string];
      const house = HOUSES.find((h) => h.id === houseId);
      expect(house, key).toBeDefined();
      expect(house?.objects.some((o) => o.id === objId), key).toBe(true);
    }
  });

  it('every enterable building maps to a house file', () => {
    for (const b of BUILDINGS.filter((x) => x.id.startsWith('house-'))) {
      expect(HOUSES.some((h) => h.id === HOUSE_FOR_BUILDING[b.id]), b.id).toBe(true);
    }
    expect(HOUSES).toHaveLength(3);
  });
});

describe('world layout', () => {
  it('keeps everything inside the world', () => {
    const pts = [...BUILDINGS, ...NPCS, ...PICKUPS, ...FAULTS];
    for (const p of pts) {
      expect(p.x).toBeGreaterThan(0);
      expect(p.x).toBeLessThan(WORLD.w);
      expect(p.y).toBeGreaterThan(0);
      expect(p.y).toBeLessThan(WORLD.h);
    }
  });

  it('faults referenced by threads exist, and NPC speakers have names', () => {
    for (const t of THREADS) if (t.faultId) expect(FAULTS.some((f) => f.id === t.faultId), t.id).toBe(true);
    for (const n of NPCS) expect(SPEAKER_NAMES[n.speaker], n.id).toBeDefined();
  });

  it('unique ids', () => {
    for (const list of [BUILDINGS.map((b) => b.id), NPCS.map((n) => n.id), PICKUPS.map((p) => p.id), FAULTS.map((f) => f.id)]) {
      expect(new Set(list).size).toBe(list.length);
    }
  });
});
