import Phaser from 'phaser';
import { HOUSES, HOUSE_FOR_BUILDING } from '../content';
import { bus } from '../core/bus';
import { createActor, updateActor, type Actor } from '../game/actors';
import { CTX_KEY, type GameContext } from '../game/context';
import { TruthFx, truthLevel } from '../game/truthFx';

interface RoomObject {
  id: string;
  interactive: boolean;
  nameHe: string;
  frame: string;
  frameTruth: string;
  place: { x: number; y: number };
  wall: boolean;
  sortY: number;
  footprintPx: [number, number] | null;
}

interface RoomLayout {
  shellSize: [number, number];
  floorPolygonPx: Array<[number, number]>;
  objects: RoomObject[];
}

interface AtlasMeta { frames: Record<string, { anchor?: { x: number; y: number } }> }

function pointInPolygon(x: number, y: number, poly: Array<[number, number]>): boolean {
  let inside = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i] as [number, number];
    const [xj, yj] = poly[j] as [number, number];
    if (yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
}

/**
 * Dollhouse cutaway built from the Blender room: a shell image, one sprite per object (so each can glow
 * when the player stands near it), and a "truth" shell and truth objects cross-faded in by the needle.
 */
export class HouseScene extends Phaser.Scene {
  private ctx!: GameContext;
  private buildingId = '';
  private contentId = '';
  private player!: Actor;
  private px = 0;
  private py = 0;
  private layout!: RoomLayout;
  private keys!: Record<string, Phaser.Input.Keyboard.Key>;
  private offs: Array<() => void> = [];
  private last: string | null = null;
  private fx!: TruthFx;
  private sight = false;
  private truthImgs: Phaser.GameObjects.Image[] = [];
  private glows = new Map<string, Phaser.FX.Glow>();
  private scaleK = 1;
  private ox = 0;
  private oy = 0;
  private blockers: Array<[number, number, number, number]> = [];
  /** Hebrew object names come from the bundled story content, never from a fetched file. */
  private names = new Map<string, string>();

  constructor() {
    super('House');
  }

  init(data: { houseId: string }): void {
    this.buildingId = data.houseId;
    this.contentId = HOUSE_FOR_BUILDING[data.houseId] ?? '';
  }

  preload(): void {
    const id = this.contentId;
    const base = `${import.meta.env.BASE_URL}assets/interiors/${id}`;
    this.load.image(`shell:${id}`, `${base}/shell.png`);
    this.load.image(`shellT:${id}`, `${base}/shell_truth.png`);
    this.load.atlas(`objs:${id}`, `${base}/objects.png`, `${base}/objects.json`);
    this.load.atlas(`objsT:${id}`, `${base}/objects_truth.png`, `${base}/objects_truth.json`);
    this.load.json(`layout:${id}`, `${base}/layout.json`);
    this.load.json(`objmeta:${id}`, `${base}/objects.json`);
  }

  create(): void {
    this.ctx = this.registry.get(CTX_KEY) as GameContext;
    const id = this.contentId;
    const def = HOUSES.find((h) => h.id === id);
    if (!def) return;
    this.layout = this.cache.json.get(`layout:${id}`) as RoomLayout;
    const meta = this.cache.json.get(`objmeta:${id}`) as AtlasMeta;
    this.cameras.main.setBackgroundColor(0x0b0c1c);
    this.truthImgs = [];
    this.names = new Map(def.objects.map((o) => [o.id, o.name]));
    this.glows.clear();
    this.blockers = [];
    this.sight = false;

    const [sw, sh] = this.layout.shellSize;
    const W = this.scale.width;
    const H = this.scale.height;
    this.scaleK = Phaser.Math.Clamp(Math.min((W - 24) / sw, (H - 150) / sh), 0.5, 1.5);
    this.ox = (W - sw * this.scaleK) / 2;
    this.oy = (H - sh * this.scaleK) / 2 + 28;
    const k = this.scaleK;

    this.add.image(this.ox, this.oy, `shell:${id}`).setOrigin(0).setScale(k).setDepth(0);
    this.truthImgs.push(this.add.image(this.ox, this.oy, `shellT:${id}`).setOrigin(0).setScale(k).setDepth(1).setAlpha(0).setVisible(false));

    for (const o of this.layout.objects) {
      const a = meta.frames[o.frame]?.anchor ?? { x: 0.5, y: 0.9 };
      const x = this.ox + o.place.x * k;
      const y = this.oy + o.place.y * k;
      const depth = 10 + o.sortY * k;
      const img = this.add.image(x, y, `objs:${id}`, o.frame).setOrigin(a.x, a.y).setScale(k).setDepth(depth);
      this.truthImgs.push(this.add.image(x, y, `objsT:${id}`, o.frameTruth).setOrigin(a.x, a.y).setScale(k).setDepth(depth + 0.2).setAlpha(0).setVisible(false));
      if (o.interactive && img.postFX) this.glows.set(o.id, img.postFX.addGlow(0xffd27a, 0, 0, false, 0.1, 10));
      if (!o.wall && o.footprintPx) this.blockers.push([o.place.x - o.footprintPx[0] / 2, o.place.y - o.footprintPx[1], o.footprintPx[0], o.footprintPx[1]]);
    }

    this.add.text(W / 2, this.oy - 34, def.name, { fontFamily: 'Segoe UI, Arial', fontSize: '26px', color: '#ffd27a', rtl: true, stroke: '#0b0c1c', strokeThickness: 5 }).setOrigin(0.5).setDepth(5000);
    const door = this.add.text(this.ox + (sw / 2) * k, this.oy + (sh - 6) * k, 'יציאה', { fontFamily: 'Segoe UI, Arial', fontSize: '18px', color: '#ffd27a', rtl: true, stroke: '#0b0c1c', strokeThickness: 4 }).setOrigin(0.5, 0).setDepth(5000);
    this.tweens.add({ targets: door, y: door.y + 6, duration: 700, yoyo: true, repeat: -1, ease: 'sine.inOut' });

    const char = this.ctx.save.data.look === 'boy' ? 'apprentice_boy' : 'apprentice_girl';
    this.px = sw / 2;
    this.py = 548;
    this.player = createActor(this, char, this.ox + this.px * k, this.oy + this.py * k, undefined, k);
    this.placePlayer(0, 0);
    this.keys = (this.input.keyboard?.addKeys('W,A,S,D,UP,DOWN,LEFT,RIGHT') ?? {}) as Record<string, Phaser.Input.Keyboard.Key>;

    this.fx = new TruthFx(this.cameras.main);
    this.offs.push(
      bus.on('interact:use', ({ id: use }) => this.onUse(use)),
      bus.on('sight:toggle', ({ on }) => (this.sight = on)),
      bus.on('truth:flash', ({ ms }) => this.fx.flash(ms)),
    );
    this.events.once('shutdown', () => {
      this.offs.forEach((o) => o());
      this.offs = [];
      bus.emit('interact:available', null);
    });
    if (this.ctx.hud.isSightOn) this.sight = true;
    this.ctx.hud.setVisible(true);
    this.ctx.joystick.setVisible(true);
    this.last = null;
    bus.emit('interact:available', null);
    bus.emit('house:entered', { houseId: this.contentId });
  }

  private placePlayer(vx: number, vy: number): void {
    const k = this.scaleK;
    updateActor(this.player, this.ox + this.px * k, this.oy + this.py * k, vx, vy);
    this.player.sprite.setScale(k);
    this.player.sprite.setDepth(10 + this.py * k);
    this.player.shadow.setDepth(10 + this.py * k - 1);
  }

  private onUse(id: string): void {
    if (this.ctx.modal || !this.scene.isActive()) return;
    if (id === 'exit') bus.emit('world:exit-house', { houseId: this.buildingId });
  }

  private walkable(x: number, y: number): boolean {
    if (!pointInPolygon(x, y, this.layout.floorPolygonPx)) return false;
    for (const [bx, by, bw, bh] of this.blockers) {
      if (x > bx - 10 && x < bx + bw + 10 && y > by - 4 && y < by + bh + 4) return false;
    }
    return true;
  }

  update(_t: number, dtMs: number): void {
    if (!this.player || !this.layout) return;
    const dt = Math.min(dtMs, 50) / 1000;
    const c = this.ctx;
    if (!c.modal) c.session.tick(dt);
    c.hud.setTimer(c.session.remaining, c.session.phase !== 'free');
    c.hud.setCoins(c.save.data.coins);

    let vx = 0;
    let vy = 0;
    if (!c.modal) {
      const k = this.keys;
      vx = (k.D?.isDown || k.RIGHT?.isDown ? 1 : 0) - (k.A?.isDown || k.LEFT?.isDown ? 1 : 0) + c.joystick.vector.x;
      vy = (k.S?.isDown || k.DOWN?.isDown ? 1 : 0) - (k.W?.isDown || k.UP?.isDown ? 1 : 0) + c.joystick.vector.y;
      const len = Math.hypot(vx, vy);
      if (len > 1) {
        vx /= len;
        vy /= len;
      }
    }
    const speed = 190;
    const nx = this.px + vx * speed * dt;
    const ny = this.py + vy * speed * dt;
    if (this.walkable(nx, this.py)) this.px = nx;
    if (this.walkable(this.px, ny)) this.py = ny;
    this.placePlayer(vx, vy);

    // the truth: same grade as the village, plus cross-faded truth art
    this.fx.set(this.sight ? truthLevel(c.save.data.power) : 0);
    this.fx.update(dtMs);
    const tv = this.fx.value;
    for (const t of this.truthImgs) t.setVisible(tv > 0.03).setAlpha(Math.min(1, tv * 1.25));

    let best: { id: string; label: string; d: number } | null = null;
    for (const o of this.layout.objects) {
      if (!o.interactive) continue;
      const d = Math.hypot(o.place.x - this.px, o.place.y - this.py + 20);
      const near = d < 95;
      const glow = this.glows.get(o.id);
      if (glow) glow.outerStrength = near ? 3 + Math.sin(this.time.now / 180) : 0;
      if (near && (!best || d < best.d)) best = { id: `obj:${this.contentId}:${o.id}`, label: this.names.get(o.id) ?? o.nameHe, d };
    }
    const [sw, sh] = this.layout.shellSize;
    const atDoor = this.py > sh * 0.84 && Math.abs(this.px - sw / 2) < 120;
    const pick = best ?? (atDoor ? { id: 'exit', label: 'לצאת מהבית' } : null);
    const id = pick?.id ?? null;
    if (id !== this.last) {
      this.last = id;
      bus.emit('interact:available', pick ? { id: pick.id, label: pick.label } : null);
    }
  }
}
