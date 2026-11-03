import Phaser from 'phaser';
import { HOUSES, HOUSE_FOR_BUILDING } from '../content';
import { bus } from '../core/bus';
import { createActor, updateActor, type Actor } from '../game/actors';
import { CTX_KEY, type GameContext } from '../game/context';

interface Palette { floor: number; wall: number; accent: number }

const PALETTES: Record<string, Palette> = {
  house_grandma: { floor: 0x8a6a4c, wall: 0xc9a98b, accent: 0x7a4f35 },
  house_clinic: { floor: 0xa9b4b2, wall: 0xdfe6e0, accent: 0x5b7a8a },
  house_print: { floor: 0x7e6a58, wall: 0xcdbfd8, accent: 0x5a4a6a },
};

interface Placed { id: string; name: string; x: number; y: number; w: number; h: number }

/** Dollhouse cutaway: back walls, floor, open front. Objects come from houses.json. */
export class HouseScene extends Phaser.Scene {
  private ctx!: GameContext;
  private buildingId = '';
  private contentId = '';
  private player!: Actor;
  private px = 0;
  private py = 0;
  private bounds = { x1: 0, x2: 0, y1: 0, y2: 0 };
  private doorX = 0;
  private keys!: Record<string, Phaser.Input.Keyboard.Key>;
  private offs: Array<() => void> = [];
  private last: string | null = null;
  private objs: Placed[] = [];

  constructor() {
    super('House');
  }

  init(data: { houseId: string }): void {
    this.buildingId = data.houseId;
    this.contentId = HOUSE_FOR_BUILDING[data.houseId] ?? '';
  }

  create(): void {
    this.ctx = this.registry.get(CTX_KEY) as GameContext;
    const def = HOUSES.find((h) => h.id === this.contentId);
    if (!def) return;
    const pal = PALETTES[def.id] ?? PALETTES.house_grandma!;
    this.cameras.main.setBackgroundColor(0x0d0f1f);
    const cx = this.scale.width / 2;
    const cy = this.scale.height / 2;
    const W = Math.min(760, this.scale.width - 80);
    const H = Math.min(430, this.scale.height - 250);
    const ox = cx - W / 2;
    const oy = cy - H / 2 + 36;
    const g = this.add.graphics();
    // back wall with a window
    g.fillStyle(pal.wall, 1);
    g.fillRect(ox, oy - 140, W, 140);
    g.fillStyle(0x000000, 0.16);
    g.fillRect(ox, oy - 140, W, 10);
    g.fillStyle(0xffe3a0, 0.95);
    g.fillRoundedRect(cx - 52, oy - 112, 104, 76, 8);
    g.lineStyle(4, 0x3a2a35, 1);
    g.strokeRoundedRect(cx - 52, oy - 112, 104, 76, 8);
    g.lineBetween(cx, oy - 112, cx, oy - 36);
    // left wall (oblique)
    const left = [new Phaser.Geom.Point(ox - 64, oy - 76), new Phaser.Geom.Point(ox, oy - 140), new Phaser.Geom.Point(ox, oy), new Phaser.Geom.Point(ox - 64, oy + 64)];
    g.fillStyle(pal.wall, 1);
    g.fillPoints(left, true);
    g.fillStyle(0x000000, 0.24);
    g.fillPoints(left, true);
    // floor
    g.fillStyle(pal.floor, 1);
    g.fillRect(ox, oy, W, H);
    g.lineStyle(2, 0x000000, 0.12);
    for (let x = ox; x <= ox + W; x += 60) g.lineBetween(x, oy, x, oy + H);
    for (let y = oy; y <= oy + H; y += 60) g.lineBetween(ox, y, ox + W, y);
    g.lineStyle(6, 0x2a1a14, 1);
    g.strokeRect(ox, oy, W, H);
    this.add.text(cx, oy - 175, def.name, { fontFamily: 'Segoe UI, Arial', fontSize: '26px', color: '#ffcf6b', rtl: true }).setOrigin(0.5);
    // door mat
    this.doorX = cx;
    g.fillStyle(0x5b3a2a, 1);
    g.fillRoundedRect(cx - 44, oy + H - 16, 88, 28, 6);
    this.add.text(cx, oy + H + 30, 'דלת יציאה', { fontFamily: 'Segoe UI, Arial', fontSize: '16px', color: '#a9b0d6', rtl: true }).setOrigin(0.5);

    this.objs = [];
    const cols = [0.17, 0.5, 0.83];
    def.objects.forEach((o, i) => {
      const x = ox + W * (cols[i % 3] as number);
      const y = oy + (i < 3 ? 62 : 190) + (i % 2) * 22;
      const w = 118;
      const h = 56;
      this.add.ellipse(x, y + h / 2 + 4, w * 1.05, 16, 0x000000, 0.25).setDepth(y);
      this.add.rectangle(x, y, w, h, pal.accent).setStrokeStyle(3, 0x2a1a14).setDepth(y + 1);
      this.add.text(x, y, o.name, { fontFamily: 'Segoe UI, Arial', fontSize: '14px', color: '#f3ecdc', align: 'center', wordWrap: { width: w - 10 }, rtl: true }).setOrigin(0.5).setDepth(y + 2);
      this.objs.push({ id: o.id, name: o.name, x, y, w, h });
    });

    this.bounds = { x1: ox + 30, x2: ox + W - 30, y1: oy + 70, y2: oy + H - 2 };
    const char = this.ctx.save.data.look === 'boy' ? 'apprentice_boy' : 'apprentice_girl';
    this.px = cx;
    this.py = oy + H - 40;
    this.player = createActor(this, char, this.px, this.py, undefined, 1.5);
    updateActor(this.player, this.px, this.py, 0, 0);
    this.player.sprite.setDepth(2000 + this.py);
    this.keys = (this.input.keyboard?.addKeys('W,A,S,D,UP,DOWN,LEFT,RIGHT') ?? {}) as Record<string, Phaser.Input.Keyboard.Key>;

    this.offs.push(bus.on('interact:use', ({ id }) => this.onUse(id)));
    this.events.once('shutdown', () => {
      this.offs.forEach((o) => o());
      this.offs = [];
      bus.emit('interact:available', null);
    });
    this.ctx.hud.setVisible(true);
    this.ctx.joystick.setVisible(true);
    this.last = null;
    bus.emit('interact:available', null);
    bus.emit('house:entered', { houseId: this.contentId });
  }

  private onUse(id: string): void {
    if (this.ctx.modal || !this.scene.isActive()) return;
    if (id === 'exit') bus.emit('world:exit-house', { houseId: this.buildingId });
  }

  update(_t: number, dtMs: number): void {
    if (!this.player) return;
    const dt = Math.min(dtMs, 50) / 1000;
    const c = this.ctx;
    if (!c.modal) c.session.tick(dt);
    c.hud.setTimer(c.session.remaining, c.session.phase !== 'free');
    c.hud.setCoins(c.save.data.coins);
    const b = this.bounds;
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
    this.px = Phaser.Math.Clamp(this.px + vx * 170 * dt, b.x1, b.x2);
    this.py = Phaser.Math.Clamp(this.py + vy * 170 * dt, b.y1, b.y2);
    updateActor(this.player, this.px, this.py, vx, vy);
    this.player.sprite.setDepth(2000 + this.py);

    let best: { id: string; label: string } | null = null;
    let bd = 105;
    for (const o of this.objs) {
      const d = Math.hypot(o.x - this.px, o.y + 30 - this.py);
      if (d < bd) {
        bd = d;
        best = { id: `obj:${this.contentId}:${o.id}`, label: o.name };
      }
    }
    if (!best && this.py > b.y2 - 110 && Math.abs(this.px - this.doorX) < 130) best = { id: 'exit', label: 'לצאת מהבית' };
    const id = best?.id ?? null;
    if (id !== this.last) {
      this.last = id;
      bus.emit('interact:available', best);
    }
  }
}
