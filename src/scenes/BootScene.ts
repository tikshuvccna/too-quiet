import Phaser from 'phaser';
import { NPCS } from '../world/layout';

export const CHARS = ['apprentice_girl', 'apprentice_boy', 'dvora'] as const;
export type CharKey = (typeof CHARS)[number];

/** Villager sheets of the starting village (idle only, 5 directions, frame 3 is a blink). The rest load with their region. */
export const NPC_SHEETS: string[] = [...new Set(NPCS.map((n) => n.char.replace(/^npc_/, '')))];
export const NPC_DIRS = ['S', 'SE', 'E', 'SW', 'W'] as const;

/** Creatures of the starting village. The creatures of the big world load with their region. */
export const CREATURE_KEYS = [
  'ant_swarm', 'cloud_sheep', 'echo_parrot', 'gargar_cat', 'glow_worm', 'lantern_moth', 'librarian_owl', 'paper_crane',
  'slow_snail', 'spinner_spider', 'spool_hedgehog', 'trail_fox',
] as const;
export const LEGENDARY_KEYS = ['thread_serpent', 'cloud_whale', 'echo_giant'] as const;

interface AnimDef { frames: string[]; frameRate: number; repeat: number }

type Draw = (c: CanvasRenderingContext2D, w: number, h: number) => void;

function makeTexture(scene: Phaser.Scene, key: string, w: number, h: number, draw: Draw): void {
  if (scene.textures.exists(key)) return;
  const t = scene.textures.createCanvas(key, w, h);
  if (!t) return;
  draw(t.getContext(), w, h);
  t.refresh();
}

const drawGrass: Draw = (c, w, h) => {
  c.fillStyle = '#3d6b4a';
  c.fillRect(0, 0, w, h);
  let s = 7;
  const r = (): number => (s = (s * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < 260; i++) {
    c.fillStyle = r() < 0.5 ? 'rgba(80,140,90,.35)' : 'rgba(30,70,50,.3)';
    c.fillRect(r() * w, r() * h, 2 + r() * 3, 2 + r() * 5);
  }
};

const drawDot = (col: string): Draw => (c, w, h) => {
  c.shadowColor = col;
  c.shadowBlur = 12;
  c.fillStyle = col;
  c.beginPath();
  c.arc(w / 2, h / 2, Math.min(w, h) / 4, 0, 7);
  c.fill();
};

const drawShadow: Draw = (c, w, h) => {
  const g = c.createRadialGradient(w / 2, h / 2, 2, w / 2, h / 2, w / 2);
  g.addColorStop(0, 'rgba(0,0,0,.45)');
  g.addColorStop(1, 'rgba(0,0,0,0)');
  c.fillStyle = g;
  c.fillRect(0, 0, w, h);
};

/** Villagers: breathing and a blink on the last frame. Safe to call again. */
export function makeNpcAnims(scene: Phaser.Scene, k: string): void {
  for (const d of NPC_DIRS) {
    const key = `npc_${k}:idle_${d}`;
    if (scene.anims.exists(key)) continue;
    const seq = [0, 1, 2, 1, 0, 0, 0, 0, 3].map((i) => ({ key: `npc_${k}`, frame: `idle_${d}_${i}` }));
    scene.anims.create({ key, frames: seq, frameRate: 4, repeat: -1 });
  }
}

/** Creature animations from the atlas json that was loaded under `cr_<k>:anims`. */
export function makeCreatureAnims(scene: Phaser.Scene, k: string): void {
  const data = scene.cache.json.get(`cr_${k}:anims`) as { anims?: Record<string, AnimDef> } | undefined;
  for (const [name, a] of Object.entries(data?.anims ?? {})) {
    const key = `cr_${k}:${name}`;
    if (scene.anims.exists(key)) continue;
    const frames = name === 'idle' ? [...a.frames, ...a.frames.slice(1, -1).reverse()] : a.frames;
    scene.anims.create({ key, frames: frames.map((f) => ({ key: `cr_${k}`, frame: f })), frameRate: a.frameRate, repeat: -1 });
  }
}

export class BootScene extends Phaser.Scene {
  constructor() {
    super('Boot');
  }

  preload(): void {
    const base = import.meta.env.BASE_URL;
    for (const k of CHARS) {
      this.load.atlas(k, `${base}assets/characters_v2/${k}.png`, `${base}assets/characters_v2/${k}.json`);
      this.load.json(`${k}:anims`, `${base}assets/characters_v2/${k}.json`);
    }
    for (const k of NPC_SHEETS) this.load.atlas(`npc_${k}`, `${base}assets/characters_v2/npcs/${k}.png`, `${base}assets/characters_v2/npcs/${k}.json`);
    for (const k of [...CREATURE_KEYS, ...LEGENDARY_KEYS]) {
      this.load.atlas(`cr_${k}`, `${base}assets/creatures/${k}.png`, `${base}assets/creatures/${k}.json`);
      this.load.json(`cr_${k}:anims`, `${base}assets/creatures/${k}.json`);
    }
    this.load.atlas('the_head', `${base}assets/creatures/the_head.png`, `${base}assets/creatures/the_head.json`);
    this.load.atlas('props', `${base}assets/props/props.png`, `${base}assets/props/props.json`);
    this.load.atlas('buildings', `${base}assets/buildings/buildings.png`, `${base}assets/buildings/buildings.json`);
    this.load.json('buildings:meta', `${base}assets/buildings/buildings.json`);
    this.load.atlas('buildings_truth', `${base}assets/buildings/buildings_truth.png`, `${base}assets/buildings/buildings_truth.json`);
    this.load.atlas('fx', `${base}assets/fx/fx.png`, `${base}assets/fx/fx.json`);
  }

  create(): void {
    makeTexture(this, 'grass', 128, 128, drawGrass);
    makeTexture(this, 'dot_gold', 24, 24, drawDot('#ffcf6b'));
    makeTexture(this, 'dot_teal', 24, 24, drawDot('#5cf0d0'));
    makeTexture(this, 'dot_pink', 24, 24, drawDot('#ff9ad0'));
    makeTexture(this, 'blob', 64, 32, drawShadow);
    for (const k of CHARS) {
      const data = this.cache.json.get(`${k}:anims`) as { anims?: Record<string, AnimDef> } | undefined;
      for (const [name, a] of Object.entries(data?.anims ?? {})) {
        const key = `${k}:${name}`;
        if (this.anims.exists(key)) continue;
        this.anims.create({ key, frames: a.frames.map((f) => ({ key: k, frame: f })), frameRate: a.frameRate, repeat: a.repeat });
      }
    }
    for (const k of NPC_SHEETS) makeNpcAnims(this, k);
    for (const k of [...CREATURE_KEYS, ...LEGENDARY_KEYS]) makeCreatureAnims(this, k);
    for (const [name, frames] of [['benevolent', ['the_head_benevolent_0', 'the_head_benevolent_1']], ['truth', ['the_head_truth_0', 'the_head_truth_1']]] as const) {
      this.anims.create({ key: `the_head:${name}`, frames: frames.map((f) => ({ key: 'the_head', frame: f })), frameRate: 0.5, repeat: -1, yoyo: true });
    }
    this.scene.start('World');
  }
}
