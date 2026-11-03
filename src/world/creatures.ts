import Phaser from 'phaser';
import { nightness } from './atmosphere';

export type CreatureMode = 'sit' | 'wander' | 'fly' | 'night-fly' | 'night-wander' | 'static';

export interface CreatureSpawn {
  key: string;
  x: number;
  y: number;
  mode: CreatureMode;
  radius?: number;
  legendary?: boolean;
}

/** Where the creatures live. Small ones roam a little; legendary ones stay put. */
export const CREATURE_SPAWNS: CreatureSpawn[] = [
  { key: 'gargar_cat', x: 706, y: 958, mode: 'sit' },
  { key: 'paper_crane', x: 1250, y: 930, mode: 'fly', radius: 280 },
  { key: 'echo_parrot', x: 1196, y: 1318, mode: 'sit' },
  { key: 'librarian_owl', x: 1372, y: 842, mode: 'sit' },
  { key: 'cloud_sheep', x: 980, y: 1440, mode: 'wander', radius: 130 },
  { key: 'trail_fox', x: 1262, y: 1580, mode: 'wander', radius: 220 },
  { key: 'slow_snail', x: 1790, y: 1340, mode: 'wander', radius: 50 },
  { key: 'spool_hedgehog', x: 640, y: 1410, mode: 'wander', radius: 90 },
  { key: 'ant_swarm', x: 1870, y: 1010, mode: 'wander', radius: 45 },
  { key: 'spinner_spider', x: 2040, y: 700, mode: 'sit' },
  { key: 'lantern_moth', x: 1320, y: 990, mode: 'night-fly', radius: 260 },
  { key: 'glow_worm', x: 1090, y: 920, mode: 'night-wander', radius: 110 },
  { key: 'thread_serpent', x: 2360, y: 700, mode: 'static', legendary: true },
  { key: 'echo_giant', x: 1160, y: 400, mode: 'static', legendary: true },
];

const WORLD_SCALE = 0.667;

class Creature {
  readonly sprite: Phaser.GameObjects.Sprite;
  readonly shadow: Phaser.GameObjects.Image;
  baseX: number;
  baseY: number;
  private tx: number;
  private ty: number;
  private wait = Math.random() * 3;
  private facing: 'S' | 'SE' | 'E' | 'N' = 'S';
  private moving = false;

  constructor(private readonly scene: Phaser.Scene, readonly spawn: CreatureSpawn) {
    const key = `cr_${spawn.key}`;
    const legend = !!spawn.legendary;
    this.shadow = scene.add.image(spawn.x, spawn.y, 'blob').setScale(legend ? 4 : 1.1).setAlpha(0.8);
    this.sprite = scene.add.sprite(spawn.x, spawn.y, key, legend ? 'idle_0' : 'idle_S_0').setOrigin(0.5, legend ? 0.9375 : 0.859375);
    if (!legend) this.sprite.setScale(WORLD_SCALE);
    this.sprite.play(legend ? `${key}:idle` : `${key}:idle_S`);
    this.baseX = spawn.x;
    this.baseY = spawn.y;
    this.tx = spawn.x;
    this.ty = spawn.y;
  }

  private anim(name: 'idle' | 'walk', dir: 'S' | 'SE' | 'E' | 'N', flip: boolean): void {
    const key = `cr_${this.spawn.key}:${name}_${dir}`;
    if (this.sprite.anims.currentAnim?.key !== key) this.sprite.play(key, true);
    this.sprite.setFlipX(flip);
  }

  update(dt: number, tod: number): void {
    const s = this.spawn;
    const night = nightness(tod);
    const flier = s.mode === 'fly' || s.mode === 'night-fly';
    const nocturnal = s.mode.startsWith('night');
    const vis = nocturnal ? night : 1;
    this.sprite.setVisible(vis > 0.05).setAlpha(vis);
    this.shadow.setVisible(vis > 0.05).setAlpha(0.8 * vis);
    const bob = flier ? Math.sin(this.scene.time.now / 260 + s.x) * 5 - 34 : 0;
    if (s.mode === 'sit' || s.mode === 'static') {
      this.sprite.setDepth(s.y);
      this.shadow.setPosition(s.x, s.y - 2).setDepth(s.y - 1);
      return;
    }
    // wander: pick a nearby point now and then, walk there slowly
    this.wait -= dt;
    const px = this.baseX;
    const py = this.baseY;
    if (this.wait <= 0 && !this.moving) {
      const r = s.radius ?? 80;
      this.tx = s.x + (Math.random() - 0.5) * 2 * r;
      this.ty = s.y + (Math.random() - 0.5) * r;
      this.moving = true;
    }
    if (this.moving) {
      const dx = this.tx - px;
      const dy = this.ty - py;
      const d = Math.hypot(dx, dy);
      const speed = flier ? 62 : 28;
      if (d < 3) {
        this.moving = false;
        this.wait = 2 + Math.random() * 4;
        this.anim('idle', this.facing, this.sprite.flipX);
      } else {
        this.baseX = px + (dx / d) * speed * dt;
        this.baseY = py + (dy / d) * speed * dt;
        const flip = dx < 0;
        const dir = Math.abs(dy) > Math.abs(dx) * 1.3 ? (dy > 0 ? 'S' : 'N') : 'E';
        this.facing = dir;
        this.anim('walk', dir, flip);
      }
    }
    this.sprite.setPosition(this.baseX, this.baseY + bob).setDepth(this.baseY);
    this.shadow.setPosition(this.baseX, this.baseY - 2).setDepth(this.baseY - 1);
  }
}

export interface CreatureTarget { key: string; x: number; y: number; legendary: boolean }

/** The small living things of the valley and the three legends. */
export class CreatureManager {
  private readonly list: Creature[];

  constructor(scene: Phaser.Scene) {
    this.list = CREATURE_SPAWNS.map((s) => new Creature(scene, s));
  }

  update(dtMs: number, tod: number): void {
    const dt = Math.min(dtMs, 50) / 1000;
    for (const c of this.list) c.update(dt, tod);
  }

  /** Creatures the player could meet right now (not hidden by the time of day). */
  targets(tod: number): CreatureTarget[] {
    return this.list
      .filter((c) => !c.spawn.mode.startsWith('night') || nightness(tod) > 0.3)
      .map((c) => ({ key: c.spawn.key, x: c.baseX, y: c.baseY, legendary: !!c.spawn.legendary }));
  }
}
