import Phaser from 'phaser';
import { bus } from '../core/bus';
import { createActor, setIdleFacing, updateActor, type Actor } from '../game/actors';
import { TruthFx, truthLevel } from '../game/truthFx';
import { ROADS } from '../world/roads';
import { ChunkGround } from '../world/chunkGround';
import { Culler } from '../world/culler';
import { REGIONS, inSea, regionAt } from '../world/regions';
import { equippedAura } from '../ui/shop';
import { perksOf } from '../game/perks';
import { WORLD_BUILDINGS, WORLD_CREATURE_SPAWNS, WORLD_NPCS, WORLD_PICKUPS, WORLD_PROPS } from '../world/worldMap';
import { distanceToRegion, loadsForRegion, type RegionLoad } from '../world/regionAssets';
import type { CreatureSpawn } from '../world/creatures';
import { makeCreatureAnims, makeNpcAnims } from './BootScene';
import { Atmosphere } from '../world/atmosphere';
import { CreatureManager } from '../world/creatures';
import { CREATURES } from '../content';
import { TruthLayer, type Swappable } from '../world/truthLayer';
import { CTX_KEY, type GameContext } from '../game/context';
import {
  BUILDINGS, DECOR, FAULTS, NPCS, PICKUPS, SPOTS, START_SPAWN, THREADS, WORLD, wallRects,
  type FaultDef, type PickupDef, type ThreadDef,
} from '../world/layout';

const SPEED = 190;
const INTERACT_RANGE = 78;
const PLAYER_R = 16;

/** Ground-contact anchors of the prop frames (from art/pipeline props.json). */
const ANCHOR: Record<string, [number, number]> = {
  cottage_a: [0.5, 0.75], cottage_b: [0.5, 0.75], cottage_c: [0.4514, 0.7847], tree_round: [0.5, 0.8828],
  tree_pine: [0.5, 0.8958], fence: [0.5, 0.7917], signpost: [0.5, 0.8611], lamppost: [0.5, 0.8958],
  well: [0.5, 0.8542], market_stall: [0.4643, 0.875],
};

/** Regions whose assets are in the texture cache. Module level: a restarted scene keeps them. */
const readyRegions = new Set<string>();

interface Target { id: string; x: number; y: number; label: string; range?: number }

function closestOnSegment(a: { x: number; y: number }, b: { x: number; y: number }, p: { x: number; y: number }): { x: number; y: number; t: number } {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const t = Math.max(0, Math.min(1, ((p.x - a.x) * dx + (p.y - a.y) * dy) / (dx * dx + dy * dy)));
  return { x: a.x + dx * t, y: a.y + dy * t, t };
}

export class WorldScene extends Phaser.Scene {
  private ctx!: GameContext;
  private player!: Actor;
  private px = 0;
  private py = 0;
  private keys!: Record<string, Phaser.Input.Keyboard.Key>;
  private blockers: Array<{ x: number; y: number; r: number }> = [];
  private walls = wallRects();
  private readonly allNpcs = [...NPCS, ...WORLD_NPCS];
  private readonly allPickups = [...PICKUPS, ...WORLD_PICKUPS];
  private pickups = new Map<string, Phaser.GameObjects.Image>();
  private fx!: TruthFx;
  private truthLayer!: TruthLayer;
  private npcRefs: Array<{ actor: Actor; def: (typeof NPCS)[number]; baseTint: number | undefined }> = [];
  private truthSwapBuildings: Array<{ img: Phaser.GameObjects.Image }> = [];
  private swaps: Swappable[] = [];
  private truthBuildings: Phaser.GameObjects.Image[] = [];
  private atmos!: Atmosphere;
  private creatures!: CreatureManager;
  private nextFlash = 240 + Math.random() * 60;
  private sightG!: Phaser.GameObjects.Graphics;
  private sightOn = false;
  private faultLabels = new Map<string, Phaser.GameObjects.Text>();
  private dots: Phaser.GameObjects.Image[] = [];
  private offs: Array<() => void> = [];
  private spawn: { x: number; y: number } = START_SPAWN;
  private lastTarget: string | null = null;
  private pickupClock = 0;
  private ground!: ChunkGround;
  private treeCount = 0;
  private spawned = new Set<string>();
  private queued: string[] = [];
  private loadingRegion: string | null = null;
  private regionClock = 0;
  private pending: { smoke: Array<{ x: number; y: number; off: Array<{ x: number; y: number }> }>; creatures: CreatureSpawn[] } = { smoke: [], creatures: [] };
  private hiddenTrees: Array<{ id: string; x: number; y: number; glint: Phaser.GameObjects.Image }> = [];
  private culler = new Culler();
  private regionId = '';
  private roadPts: Array<[number, number]> = [];

  constructor() {
    super('World');
  }

  init(data: { spawn?: { x: number; y: number } }): void {
    this.spawn = data?.spawn ?? START_SPAWN;
  }

  create(): void {
    this.ctx = this.registry.get(CTX_KEY) as GameContext;
    this.sightOn = false;
    this.blockers = [];
    this.walls = wallRects();
    this.pickups.clear();
    this.faultLabels.clear();
    this.dots = [];
    this.npcRefs = [];
    this.swaps = [];
    this.truthBuildings = [];
    // a restarted scene is the same object: forget what the previous run created
    this.creatures = undefined as unknown as CreatureManager;
    this.atmos = undefined as unknown as Atmosphere;
    this.culler = new Culler();
    this.regionId = '';
    this.treeCount = 0;
    this.hiddenTrees = [];
    this.buildGround();
    this.buildProps();
    this.buildNpcs();
    this.spawned = new Set();
    this.queued = [];
    this.loadingRegion = null;
    this.pending = { smoke: [], creatures: [] };
    this.enqueueNear(this.spawn.x, this.spawn.y);
    for (const id of readyRegions) this.spawnRegion(id);
    this.refreshPickups();
    this.buildPlayer();
    this.buildSight();
    this.truthLayer = new TruthLayer(this, this.npcRefs, this.swaps, { x: 2180, y: 420 });
    const bmeta = (this.cache.json.get('buildings:meta') as { frames: Record<string, { anchor: { x: number; y: number }; smoke?: Array<{ x: number; y: number }>; hub?: { x: number; y: number } }> }).frames;
    this.creatures = new CreatureManager(this);
    this.creatures.addSpawns(this.pending.creatures);
    this.pending.creatures = [];
    this.refreshFriends();
    this.atmos = new Atmosphere(this, (this.registry.get('tod') as number | undefined) ?? 0.4, bmeta);
    for (const sm of this.pending.smoke) this.atmos.addSmoke(sm.x, sm.y, sm.off);
    this.pending.smoke = [];

    const cam = this.cameras.main;
    cam.setBounds(0, 0, WORLD.w, WORLD.h);
    cam.startFollow(this.player.sprite, true, 0.12, 0.12, 0, -40);
    this.fx = new TruthFx(cam);
    this.applyQuality();
    this.offs.push(this.ctx.quality.onChange(() => this.applyQuality()));
    this.applyZoom();
    this.scale.on('resize', () => this.applyZoom());
    cam.preRender();
    this.ground.update(cam.worldView, 99);
    this.culler.update(0, cam.worldView, true);

    const kb = this.input.keyboard;
    this.keys = (kb?.addKeys('W,A,S,D,UP,DOWN,LEFT,RIGHT') ?? {}) as Record<string, Phaser.Input.Keyboard.Key>;

    this.offs.push(
      bus.on('interact:use', ({ id }) => this.onUse(id)),
      bus.on('sight:toggle', ({ on }) => this.setSight(on)),
      bus.on('truth:flash', ({ ms }) => this.fx.flash(ms)),
    );
    this.events.once('shutdown', () => {
      this.registry.set('tod', this.atmos.tod);
      this.atmos.destroy();
      this.ground.destroy();
      this.offs.forEach((o) => o());
      this.offs = [];
      bus.emit('interact:available', null);
    });
    this.ctx.hud.setVisible(true);
    this.ctx.joystick.setVisible(true);
    if (this.ctx.hud.isSightOn) this.setSight(true);
  }

  private applyZoom(): void {
    const w = this.scale.width;
    const h = this.scale.height;
    this.cameras.main.setZoom(Phaser.Math.Clamp(Math.min(w / 1000, h / 640), 0.62, 1.5));
  }

  private buildGround(): void {
    this.ground = new ChunkGround(this);
    // sample the roads once: trees keep away from them
    this.roadPts = [];
    for (const r of ROADS) {
      const sp = new Phaser.Curves.Spline(r.pts.map(([x, y]) => new Phaser.Math.Vector2(x, y)));
      for (const p of sp.getSpacedPoints(Math.ceil(sp.getLength() / 40))) this.roadPts.push([p.x, p.y]);
    }
  }

  private prop(frame: string, x: number, y: number, scale = 1, tint?: number): Phaser.GameObjects.Image {
    const a = ANCHOR[frame] ?? [0.5, 0.9];
    const img = this.add.image(x, y, 'props', frame).setOrigin(a[0], a[1]).setScale(scale).setDepth(y);
    if (tint !== undefined) img.setTint(tint);
    return img;
  }

  private buildProps(): void {
    const meta = (this.cache.json.get('buildings:meta') as { frames: Record<string, { anchor: { x: number; y: number } }> }).frames;
    for (const b of BUILDINGS) {
      const a = meta[b.frame]?.anchor ?? { x: 0.5, y: 0.75 };
      this.add.image(b.x, b.y - 6, 'blob').setScale((b.foot.w / 64) * 1.5, (b.foot.h / 32) * 1.6).setAlpha(0.85).setDepth(b.y - 1);
      this.add.image(b.x, b.y, 'buildings', b.frame).setOrigin(a.x, a.y).setScale(b.scale).setDepth(b.y);
      const truth = this.add.image(b.x, b.y, 'buildings_truth', `${b.frame}_truth`).setOrigin(a.x, a.y).setScale(b.scale).setDepth(b.y + 0.5).setAlpha(0).setVisible(false);
      this.truthBuildings.push(truth);
    }
    for (const d of DECOR) {
      this.add.image(d.x, d.y - 3, 'blob').setScale((d.scale ?? 1) * 1.2).setDepth(d.y - 1);
      const di = this.prop(d.frame, d.x, d.y, d.scale ?? 1);
      if (d.frame === 'lamppost') this.swaps.push({ img: di, frame: d.frame, atlas: 'props' });
      if (d.block) this.blockers.push({ x: d.x, y: d.y - 6, r: d.block });
    }
    // trees: density per region, never on roads, buildings, the plaza or the sea
    let sd = 3;
    const r = (): number => ((sd = (sd * 16807) % 2147483647) / 2147483647);
    const nearRoad = (x: number, y: number): boolean => {
      for (const [rx, ry] of this.roadPts) if (Math.abs(rx - x) < 70 && Math.abs(ry - y) < 70) return true;
      return false;
    };
    const keepClear = (x: number, y: number): boolean =>
      BUILDINGS.some((b) => Math.abs(b.x - x) < 260 && y > b.y - 200 && y < b.y + 260) ||
      WORLD_BUILDINGS.some((b) => Math.abs(b.x - x) < 260 && y > b.y - 260 && y < b.y + 220) ||
      WORLD_PROPS.some((p) => Math.abs(p.x - x) < 90 && Math.abs(p.y - y) < 70) ||
      this.allPickups.some((p) => Math.abs(p.x - x) < 70 && Math.abs(p.y - y) < 70) ||
      this.allNpcs.some((n) => Math.abs(n.x - x) < 70 && Math.abs(n.y - y) < 70) ||
      WORLD_CREATURE_SPAWNS.some((c) => Math.abs(c.x - x) < 110 && Math.abs(c.y - y) < 90) ||
      (x > 900 && x < 1900 && y > 880 && y < 1500) || (x > 1800 && x < 2150 && y > 1000 && y < 1800) || (x > 480 && x < 1000 && y > 960 && y < 1560) ||
      inSea(x, Math.min(y + 60, 3990)) || nearRoad(x, y);
    const plant = (x: number, y: number, frame: string): void => {
      const sc = 0.75 + r() * 0.4;
      const sh = this.add.image(x, y - 2, 'blob').setScale(sc * 1.4).setDepth(y - 1);
      const tr = this.prop(frame, x, y, sc);
      this.culler.add(sh, x, y, true);
      this.culler.add(tr, x, y);
      this.swaps.push({ img: tr, frame, atlas: 'props' });
      this.blockers.push({ x, y: y - 6, r: 20 * sc });
      // every 14th tree hides something small: a fixed spot, never random
      if (this.treeCount++ % 14 === 6 && !this.ctx.save.data.collected[`tree_${this.treeCount}`]) {
        const glint = this.add.image(x + 12, y - 60 * sc, 'dot_gold').setScale(0.45).setAlpha(0).setDepth(y + 1).setBlendMode(Phaser.BlendModes.ADD);
        this.hiddenTrees.push({ id: `tree_${this.treeCount}`, x, y, glint });
      }
    };
    for (const reg of REGIONS) {
      const [rx, ry, rw, rh] = reg.rect;
      if (reg.treeStyle === 'rows') {
        // orchard: tidy rows
        for (let y = ry + 80; y < ry + rh - 60; y += 150) {
          for (let x = rx + 100; x < rx + rw - 60; x += 130) {
            if (!keepClear(x, y) && r() < 0.8) plant(x, y, 'tree_round');
          }
        }
        continue;
      }
      const n = Math.round((reg.trees * rw * rh) / 1e6);
      let placed = 0;
      for (let tries = 0; placed < n && tries < n * 6; tries++) {
        const x = rx + 60 + r() * (rw - 120);
        const y = ry + 90 + r() * (rh - 160);
        if (keepClear(x, y)) continue;
        const frame = reg.treeStyle === 'pine' ? 'tree_pine' : reg.treeStyle === 'round' ? 'tree_round' : r() < 0.65 ? 'tree_round' : 'tree_pine';
        plant(x, y, frame);
        placed++;
      }
    }
    // the edge of the world: a dense ring so nobody wonders what is beyond
    for (let i = 0; i < 520; i++) {
      const side = Math.floor(r() * 4);
      const x = side === 0 ? r() * WORLD.w : side === 1 ? WORLD.w - r() * 260 : side === 2 ? r() * WORLD.w : r() * 260;
      const y = side === 0 ? r() * 260 : side === 1 ? r() * WORLD.h : side === 2 ? WORLD.h - r() * 240 : r() * WORLD.h;
      if (keepClear(x, y)) continue;
      plant(x, Math.max(60, y), r() < 0.5 ? 'tree_pine' : 'tree_round');
    }
  }

  private buildNpcs(): void {
    for (const n of NPCS) this.addNpc(n);
  }

  private addNpc(n: (typeof NPCS)[number]): void {
    const a = createActor(this, n.char, n.x, n.y, undefined, n.scale ?? 1);
    updateActor(a, n.x, n.y, 0, 0);
    setIdleFacing(a, n.x > 1500 && n.x < 4200 ? 'SW' : 'SE');
    this.npcRefs.push({ actor: a, def: n, baseTint: undefined });
    this.blockers.push({ x: n.x, y: n.y - 4, r: 20 });
  }

  /** Start loading every region the player is close to (once each, one load at a time). */
  private enqueueNear(x: number, y: number): void {
    for (const r of REGIONS) {
      if (readyRegions.has(r.id) || this.queued.includes(r.id) || this.loadingRegion === r.id) continue;
      if (distanceToRegion(r, x, y) < 1200) this.queued.push(r.id);
    }
    this.pump();
  }

  private pump(): void {
    if (this.loadingRegion || !this.queued.length || !this.sys.isActive()) return;
    const id = this.queued.shift() as string;
    const load = loadsForRegion(id, import.meta.env.BASE_URL);
    const atlases = load.atlases.filter((a) => !this.textures.exists(a.key));
    const jsons = load.jsons.filter((j) => !this.cache.json.exists(j.key));
    if (!atlases.length && !jsons.length) {
      this.regionReady(id, load);
      this.pump();
      return;
    }
    this.loadingRegion = id;
    for (const a of atlases) this.load.atlas(a.key, a.png, a.json);
    for (const j of jsons) this.load.json(j.key, j.url);
    this.load.once(Phaser.Loader.Events.COMPLETE, () => {
      this.loadingRegion = null;
      this.regionReady(id, load);
      this.pump();
    });
    this.load.start();
  }

  private regionReady(id: string, load: RegionLoad): void {
    for (const sheet of load.npcSheets) makeNpcAnims(this, sheet);
    for (const c of load.creatures) makeCreatureAnims(this, c);
    readyRegions.add(id);
    if (this.sys.isActive()) this.spawnRegion(id);
  }

  /** Create the buildings, scenery, villagers and creatures of one region, once its assets are in. */
  private spawnRegion(id: string): void {
    if (this.spawned.has(id)) return;
    this.spawned.add(id);
    const inRegion = (x: number, y: number): boolean => regionAt(x, y)?.id === id;
    for (const wb of WORLD_BUILDINGS) {
      if (!inRegion(wb.x, wb.y)) continue;
      const meta = (this.cache.json.get(`${wb.atlas}:meta`) as { frames: Record<string, { anchor: { x: number; y: number }; frame: { w: number; h: number }; smoke?: Array<{ x: number; y: number }> }> } | undefined)?.frames[wb.id];
      if (!meta) continue;
      const foot = { w: meta.frame.w * (wb.footW ?? 0.62), h: 64 };
      this.add.image(wb.x, wb.y - 6, 'blob').setScale((foot.w / 64) * 1.5, (foot.h / 32) * 1.6).setAlpha(0.85).setDepth(wb.y - 1);
      this.add.image(wb.x, wb.y, wb.atlas, wb.id).setOrigin(meta.anchor.x, meta.anchor.y).setDepth(wb.y);
      const truth = this.add.image(wb.x, wb.y, `${wb.atlas}_truth`, `${wb.id}_truth`).setOrigin(meta.anchor.x, meta.anchor.y).setDepth(wb.y + 0.5).setAlpha(0).setVisible(false);
      this.truthBuildings.push(truth);
      this.walls.push([wb.x - foot.w / 2, wb.y - foot.h + 8, foot.w, foot.h]);
      if (meta.smoke) {
        if (this.atmos) this.atmos.addSmoke(wb.x, wb.y, meta.smoke);
        else this.pending.smoke.push({ x: wb.x, y: wb.y, off: meta.smoke });
      }
    }
    const truthProps = new Set(['fairy_door_tree', 'giant_tree_hollow', 'lantern_post_b', 'flower_bush', 'mushroom_ring', 'reeds']);
    const propMeta = (this.cache.json.get('props2:meta') as { frames: Record<string, { anchor: { x: number; y: number } }> } | undefined)?.frames;
    for (const wp of WORLD_PROPS) {
      if (!inRegion(wp.x, wp.y) || !propMeta) continue;
      const sc = wp.scale ?? 1;
      const a = propMeta[wp.frame]?.anchor ?? { x: 0.5, y: 0.9 };
      this.add.image(wp.x, wp.y - 3, 'blob').setScale(sc * 1.2).setDepth(wp.y - 1);
      const img = this.add.image(wp.x, wp.y, 'props2', wp.frame).setOrigin(a.x, a.y).setScale(sc).setDepth(wp.y);
      if (truthProps.has(wp.frame)) this.swaps.push({ img, frame: wp.frame, atlas: 'props2', truthAtlas: 'props2_truth' });
      if (wp.block) this.blockers.push({ x: wp.x, y: wp.y - 6, r: wp.block });
    }
    for (const n of WORLD_NPCS) if (inRegion(n.x, n.y) && this.textures.exists(n.char)) this.addNpc(n);
    const spawns = WORLD_CREATURE_SPAWNS.filter((c) => inRegion(c.x, c.y) && this.textures.exists(`cr_${c.key}`));
    if (this.creatures) this.creatures.addSpawns(spawns);
    else this.pending.creatures.push(...spawns);
  }

  private pickupAllowed(p: PickupDef): boolean {
    if (this.ctx.save.data.collected[p.id]) return false;
    return !p.requires || this.ctx.save.hasFlag(p.requires);
  }

  /** Spawn pickups whose story requirement has just been met. */
  private refreshPickups(): void {
    for (const p of this.allPickups) {
      if (this.pickups.has(p.id) || !this.pickupAllowed(p)) continue;
      const key = p.kind === 'card' ? 'dot_gold' : p.kind === 'diary' ? 'dot_pink' : 'dot_teal';
      const img = this.add.image(p.x, p.y - 10, key).setDepth(p.y).setScale(1.2);
      this.tweens.add({ targets: img, y: p.y - 22, duration: 900, yoyo: true, repeat: -1, ease: 'sine.inOut' });
      this.pickups.set(p.id, img);
    }
  }

  private buildPlayer(): void {
    const char = this.ctx.save.data.look === 'boy' ? 'apprentice_boy' : 'apprentice_girl';
    this.px = this.spawn.x;
    this.py = this.spawn.y;
    this.unstick();
    this.player = createActor(this, char, this.px, this.py);
    updateActor(this.player, this.px, this.py, 0, 0);
    this.applyAura();
  }

  /** The aura bought in the tailor's shop: a soft coloured glow around the player. */
  applyAura(): void {
    const fx = this.player?.sprite.postFX;
    if (!fx) return;
    fx.clear();
    const a = equippedAura(this.ctx.save);
    if (a?.color && this.ctx.quality.profile.glow) fx.addGlow(a.color, 4, 0, false, 0.1, 14);
  }

  /** Apply the picture-quality level to everything this scene owns. */
  private applyQuality(): void {
    const p = this.ctx.quality.profile;
    this.fx.enabled = p.postFx;
    this.atmos?.setQuality(p);
    this.culler.setShadows(p.shadows);
    this.culler.update(0, this.cameras.main.worldView, true);
    this.applyAura();
  }

  private buildSight(): void {
    this.sightG = this.add.graphics().setDepth(4500).setBlendMode(Phaser.BlendModes.ADD);
    for (let i = 0; i < THREADS.length * 3; i++) this.dots.push(this.add.image(0, 0, 'dot_gold').setDepth(4501).setVisible(false).setBlendMode(Phaser.BlendModes.ADD));
    for (const f of FAULTS) {
      const t = this.add.text(f.x, f.y - 44, '', { fontFamily: 'Segoe UI, Arial', fontSize: '18px', color: '#ffcf6b', align: 'center', backgroundColor: 'rgba(8,9,24,.85)', padding: { x: 8, y: 4 }, rtl: true }).setOrigin(0.5).setDepth(4600).setVisible(false);
      this.faultLabels.set(f.id, t);
    }
  }

  private setSight(on: boolean): void {
    this.sightOn = on;
    if (!on) {
      this.sightG.clear();
      this.dots.forEach((d) => d.setVisible(false));
      this.faultLabels.forEach((t) => t.setVisible(false));
    }
  }

  private isFixed(f: FaultDef): boolean {
    return !!this.ctx.save.data.fixed[f.id];
  }

  private targets(): Target[] {
    const out: Target[] = [];
    for (const b of BUILDINGS) {
      if (b.id.startsWith('house-') || b.id === 'tower') out.push({ id: `door:${b.id}`, x: b.door.x, y: b.door.y, label: b.label, range: 70 });
    }
    for (const wb of WORLD_BUILDINGS) {
      if (wb.id !== 'great_tower') out.push({ id: `door:house-${wb.id}`, x: wb.door.x, y: wb.door.y, label: `כניסה: ${wb.name}`, range: 80 });
    }
    for (const n of this.npcRefs.map((r) => r.def)) out.push({ id: `npc:${n.id}`, x: n.x, y: n.y, label: n.label });
    for (const p of this.allPickups) if (this.pickups.has(p.id)) out.push({ id: `pickup:${p.id}`, x: p.x, y: p.y, label: 'לאסוף' });
    const save = this.ctx.save;
    for (const c of this.creatures.targets(this.atmos.tod)) {
      const info = CREATURES[c.key];
      if (!info) continue;
      const met = !!save.data.collected[`creature_${c.key}`];
      out.push({ id: `creature:${c.key}`, x: c.x, y: c.y, label: met ? `להסתכל על ${info.name_he}` : c.legendary ? `להתבונן: ${info.name_he}` : `להכיר: ${info.name_he}`, range: c.legendary ? 150 : 84 });
    }
    for (const s of SPOTS) {
      if (s.id === 'bridge' && save.hasFlag('bakery_fixed') && !save.hasFlag('p1_complete')) out.push({ id: `spot:${s.id}`, x: s.x, y: s.y, label: s.label, range: s.range });
      if (s.id === 'sky') out.push({ id: `spot:${s.id}`, x: s.x, y: s.y, label: s.label, range: s.range });
    }
    for (const t of this.hiddenTrees) {
      if (!save.data.collected[t.id]) out.push({ id: `tree:${t.id}`, x: t.x, y: t.y + 14, label: 'לחפש בעץ', range: 62 });
    }
    if (this.sightOn) {
      const power = save.data.power;
      for (const f of FAULTS) {
        if (!this.isFixed(f)) out.push({ id: `fault:${f.id}`, x: f.x, y: f.y, label: power >= f.needsPower ? 'לתקן את החוט' : 'לבדוק את הכתם', range: 110 });
      }
    }
    return out;
  }

  private onUse(id: string): void {
    if (this.ctx.modal || !this.scene.isActive()) return;
    if (id.startsWith('door:house-')) {
      bus.emit('world:enter-house', { houseId: id.slice(5) });
    } else if (id.startsWith('tree:')) {
      this.searchTree(id.slice(5));
    } else if (id.startsWith('pickup:')) {
      const pid = id.slice(7);
      const img = this.pickups.get(pid);
      if (!img) return;
      this.pickups.delete(pid);
      this.ctx.save.data.collected[pid] = true;
      this.ctx.save.save();
      this.tweens.add({ targets: img, scale: 2.4, alpha: 0, duration: 260, onComplete: () => img.destroy() });
      bus.emit('interact:available', null);
      this.lastTarget = null;
      bus.emit('item:collected', { id: pid });
    } else if (id.startsWith('fault:')) {
      this.tryFix(FAULTS.find((f) => f.id === id.slice(6)));
    } else if (id.startsWith('creature:')) {
      bus.emit('creature:met', { key: id.slice(9) });
    }
  }

  /** Fixed rewards by tree number: small coins most of the time, creature food now and then. */
  private searchTree(tid: string): void {
    const t = this.hiddenTrees.find((x) => x.id === tid);
    const save = this.ctx.save;
    if (!t || save.data.collected[tid]) return;
    const n = Number(tid.slice(5));
    const table: Array<{ text: string; give: () => void }> = [
      { text: '5 מטבעות בין העלים', give: () => { save.data.coins += 5; } },
      { text: 'פירות יער ליצורים', give: () => { save.data.inv.food_berries = (save.data.inv.food_berries ?? 0) + 1; } },
      { text: '8 מטבעות בחור של הגזע', give: () => { save.data.coins += 8; } },
      { text: 'פירורי לחם ליצורים', give: () => { save.data.inv.food_bread = (save.data.inv.food_bread ?? 0) + 1; } },
      { text: '5 מטבעות בין הענפים', give: () => { save.data.coins += 5; } },
      { text: 'טיפת דבש ליצורים', give: () => { save.data.inv.food_honey = (save.data.inv.food_honey ?? 0) + 1; } },
      { text: '12 מטבעות בקן ישן', give: () => { save.data.coins += 12; } },
      { text: 'גרגירים ליצורים', give: () => { save.data.inv.food_grains = (save.data.inv.food_grains ?? 0) + 1; } },
    ];
    const prize = table[n % table.length] as { text: string; give: () => void };
    prize.give();
    save.data.collected[tid] = true;
    save.save();
    this.tweens.add({ targets: t.glint, scale: 3, alpha: 0, duration: 400, onComplete: () => t.glint.destroy() });
    this.hiddenTrees = this.hiddenTrees.filter((x) => x.id !== tid);
    this.ctx.hud.toast(`מצאתם בעץ: ${prize.text}`, 'good', 3200);
    bus.emit('interact:available', null);
    this.lastTarget = null;
  }

  private tryFix(f: FaultDef | undefined): void {
    if (!f || this.isFixed(f)) return;
    if (this.ctx.save.data.power < f.needsPower) {
      this.ctx.hud.toast('הכתם מטושטש. עוד לא למדת מספיק כדי להבין אותו.', 'clue');
      return;
    }
    this.ctx.save.data.fixed[f.id] = true;
    this.ctx.save.data.evidence[f.id] = f.evidence;
    this.ctx.save.save();
    const fx = this.add.image(f.x, f.y, 'dot_teal').setDepth(4700).setScale(1).setBlendMode(Phaser.BlendModes.ADD);
    this.tweens.add({ targets: fx, scale: 6, alpha: 0, duration: 700, onComplete: () => fx.destroy() });
    bus.emit('fault:fixed', { id: f.id, evidence: f.evidence });
  }

  /** If the spawn point sits inside a wall or next to an NPC, move to the nearest free spot so the player is never trapped. */
  private unstick(): void {
    if (!this.blocked(this.px, this.py)) return;
    for (let r = 8; r <= 240; r += 8) {
      for (let k = 0; k < 16; k++) {
        const a = (k / 16) * Math.PI * 2;
        const x = this.px + Math.cos(a) * r;
        const y = this.py + Math.sin(a) * r;
        if (!this.blocked(x, y)) {
          this.px = x;
          this.py = y;
          return;
        }
      }
    }
  }

  private blocked(x: number, y: number): boolean {
    if (x < 30 || y < 30 || x > WORLD.w - 30 || y > WORLD.h - 30) return true;
    if (inSea(x, y)) return true;
    const reg = regionAt(x, y);
    if (reg?.lockedUntil && !this.ctx.save.hasFlag(reg.lockedUntil)) return true;
    for (const [rx, ry, rw, rh] of this.walls) {
      if (x > rx - PLAYER_R && x < rx + rw + PLAYER_R && y > ry - 6 && y < ry + rh + 6) return true;
    }
    for (const t of this.blockers) if (Math.hypot(x - t.x, y - t.y) < t.r + PLAYER_R * 0.8) return true;
    return false;
  }

  update(_t: number, dtMs: number): void {
    const dt = Math.min(dtMs, 50) / 1000;
    const c = this.ctx;
    if (!c.modal) {
      c.session.tick(dt);
      c.save.data.playSeconds += dt;
    }
    c.hud.setTimer(c.session.remaining, c.session.phase !== 'free');
    c.hud.setCoins(c.save.data.coins);

    let vx = 0;
    let vy = 0;
    if (!c.modal) {
      const k = this.keys;
      vx = (k.D?.isDown || k.RIGHT?.isDown ? 1 : 0) - (k.A?.isDown || k.LEFT?.isDown ? 1 : 0);
      vy = (k.S?.isDown || k.DOWN?.isDown ? 1 : 0) - (k.W?.isDown || k.UP?.isDown ? 1 : 0);
      vx += c.joystick.vector.x;
      vy += c.joystick.vector.y;
      const len = Math.hypot(vx, vy);
      if (len > 1) {
        vx /= len;
        vy /= len;
      }
    }
    const speed = SPEED * (this.sightOn ? 0.8 : 1) * perksOf(c.save).speed;
    const nx = this.px + vx * speed * dt;
    const ny = this.py + vy * speed * dt;
    if (!this.blocked(nx, this.py)) this.px = nx;
    if (!this.blocked(this.px, ny)) this.py = ny;
    updateActor(this.player, this.px, this.py, vx, vy);

    // the two faces of the valley
    const power = c.save.data.power;
    this.fx.set(this.sightOn ? truthLevel(power) : 0);
    if (!c.modal) {
      this.nextFlash -= dt;
      if (this.nextFlash <= 0) {
        this.nextFlash = 150 + Math.random() * 120;
        this.fx.flash(450);
      }
    }
    this.fx.update(dtMs);
    this.truthLayer.update(this.time.now, this.fx.value);
    const tv = this.fx.value;
    for (const tb of this.truthBuildings) tb.setVisible(tv > 0.03).setAlpha(Math.min(1, tv * 1.25));
    this.atmos.update(dtMs, tv, this.px, this.py);
    this.creatures.update(dtMs, this.atmos.tod, this.px, this.py);
    this.ctx.head.setTruth(tv, dt);

    this.pickupClock += dt;
    if (this.pickupClock > 0.6) {
      this.pickupClock = 0;
      this.refreshPickups();
    }
    this.ground.update(this.cameras.main.worldView, 1);
    this.culler.update(dtMs, this.cameras.main.worldView);
    this.watchRegion();
    const pulse = 0.5 + Math.sin(this.time.now / 260) * 0.3;
    for (const t of this.hiddenTrees) t.glint.setAlpha(Math.hypot(t.x - this.px, t.y - this.py) < 380 * perksOf(this.ctx.save).reach ? pulse : 0);
    // real time, not game time: a slow device must not postpone loading what it is about to need
    if (this.time.now - this.regionClock > 600) {
      this.regionClock = this.time.now;
      this.enqueueNear(this.px, this.py);
    }
    if (this.queued.length && !this.loadingRegion) this.pump();
    this.updateTarget();
    if (this.sightOn) this.drawSight();
  }

  /** Name of the region on entering it (a quiet toast, never during dialogue). */
  /** Befriended creatures (fed once) follow the player. Called after feeding too. */
  refreshFriends(): void {
    const friends = Object.keys(this.ctx.save.data.collected).filter((k) => k.startsWith('friend_')).map((k) => k.slice(7));
    this.creatures.setFriends(friends);
  }

  private watchRegion(): void {
    const id = regionAt(this.px, this.py)?.id ?? '';
    if (id === this.regionId) return;
    const first = this.regionId === '';
    this.regionId = id;
    const reg = REGIONS.find((x) => x.id === id);
    if (!first && reg && !this.ctx.modal) this.ctx.hud.toast(reg.name, '', 2600);
  }

  private updateTarget(): void {
    if (this.ctx.modal) {
      if (this.lastTarget !== null) bus.emit('interact:available', null);
      this.lastTarget = null;
      return;
    }
    let best: Target | null = null;
    let bd = Infinity;
    for (const t of this.targets()) {
      const d = Math.hypot(t.x - this.px, t.y - this.py);
      if (d < (t.range ?? INTERACT_RANGE) * perksOf(this.ctx.save).reach && d < bd) {
        best = t;
        bd = d;
      }
    }
    const id = best?.id ?? null;
    if (id !== this.lastTarget) {
      this.lastTarget = id;
      bus.emit('interact:available', best ? { id: best.id, label: best.label } : null);
    }
  }

  private threadPath(th: ThreadDef, time: number): Array<{ x: number; y: number }> {
    const pts: Array<{ x: number; y: number }> = [];
    const n = 28;
    const len = Math.hypot(th.b.x - th.a.x, th.b.y - th.a.y);
    const nx = -(th.b.y - th.a.y) / len;
    const ny = (th.b.x - th.a.x) / len;
    for (let i = 0; i <= n; i++) {
      const t = i / n;
      const w = Math.sin(t * Math.PI * 3 + time * 2) * 5 * Math.sin(t * Math.PI);
      pts.push({ x: th.a.x + (th.b.x - th.a.x) * t + nx * w, y: th.a.y + (th.b.y - th.a.y) * t + ny * w });
    }
    return pts;
  }

  private drawSight(): void {
    const g = this.sightG;
    g.clear();
    const time = this.time.now / 1000;
    let di = 0;
    for (const th of THREADS) {
      const fault = th.faultId ? FAULTS.find((f) => f.id === th.faultId) : undefined;
      const broken = !!fault && !this.isFixed(fault);
      const pts = this.threadPath(th, time);
      const gapAt = broken && fault ? closestOnSegment(th.a, th.b, fault) : null;
      g.lineStyle(5, broken ? 0xff6b7d : 0x5cf0d0, 0.85);
      g.beginPath();
      let pen = false;
      for (let i = 0; i < pts.length; i++) {
        const p = pts[i] as { x: number; y: number };
        const t = i / (pts.length - 1);
        if (gapAt && Math.abs(t - gapAt.t) < 0.045) {
          if (pen) g.strokePath();
          pen = false;
          g.beginPath();
          continue;
        }
        if (!pen) {
          g.moveTo(p.x, p.y);
          pen = true;
        } else g.lineTo(p.x, p.y);
      }
      g.strokePath();
      // messengers run along healthy threads only up to the fault
      for (let k = 0; k < 3; k++) {
        const dot = this.dots[di++];
        if (!dot) break;
        let t = (time * 0.18 + k / 3 + (th.a.x % 7) / 7) % 1;
        if (gapAt) t = t * gapAt.t * 0.92;
        dot.setVisible(true).setPosition(th.a.x + (th.b.x - th.a.x) * t, th.a.y + (th.b.y - th.a.y) * t);
      }
    }
    for (; di < this.dots.length; di++) this.dots[di]?.setVisible(false);
    const power = this.ctx.save.data.power;
    for (const f of FAULTS) {
      const label = this.faultLabels.get(f.id);
      if (this.isFixed(f)) {
        label?.setVisible(false);
        continue;
      }
      const near = Math.hypot(f.x - this.px, f.y - this.py) < perksOf(this.ctx.save).faultRadius;
      const known = power >= f.needsPower;
      const pulse = 1 + Math.sin(time * 5) * 0.12;
      g.fillStyle(known ? 0xff6b7d : 0x9aa0c8, 0.5);
      g.fillCircle(f.x, f.y, 26 * pulse);
      g.lineStyle(3, known ? 0xffcf6b : 0xb8bcd8, 0.9);
      g.strokeCircle(f.x, f.y, 34 * pulse);
      if (label) {
        label.setVisible(near);
        label.setText(known ? f.label : '? כתם מטושטש\nעוד לא למדתם מספיק');
      }
    }
  }
}
