import Phaser from 'phaser';
import { bus } from '../core/bus';
import { CTX_KEY, type GameContext } from '../game/context';

export interface HouseObject { id: string; x: number; y: number; label: string; color: number; w: number; h: number }

/** Placeholder rooms until the houses.json content arrives. Dollhouse cutaway: back walls, floor, open front. */
export const ROOMS: Record<string, { title: string; floor: number; wall: number; objects: HouseObject[] }> = {
  'house-grandma': {
    title: 'הבית של סבתא',
    floor: 0x8a6a4c,
    wall: 0xc9a98b,
    objects: [
      { id: 'table', x: 460, y: 360, label: 'לבדוק את השולחן', color: 0x7a4f35, w: 110, h: 60 },
      { id: 'desk', x: 700, y: 310, label: 'לבדוק את המכתבים', color: 0x5b3a2a, w: 90, h: 70 },
    ],
  },
  'house-clinic': {
    title: 'המרפאה',
    floor: 0xb9c2c0,
    wall: 0xdfe6e0,
    objects: [
      { id: 'cabinet', x: 440, y: 300, label: 'לבדוק את ארון התיקים', color: 0x6b7a8a, w: 90, h: 90 },
      { id: 'bench', x: 720, y: 380, label: 'לבדוק את הספסל', color: 0x7a5a3a, w: 130, h: 40 },
    ],
  },
  'house-bakery': {
    title: 'המאפייה',
    floor: 0xa88860,
    wall: 0xe0c08a,
    objects: [
      { id: 'oven', x: 450, y: 300, label: 'לבדוק את התנור', color: 0x5a3a30, w: 110, h: 90 },
      { id: 'flour', x: 730, y: 370, label: 'לבדוק את שקי הקמח', color: 0xe8e0cc, w: 90, h: 60 },
    ],
  },
};

export class HouseScene extends Phaser.Scene {
  private ctx!: GameContext;
  private houseId = '';
  private player!: Phaser.GameObjects.Image;
  private keys!: Record<string, Phaser.Input.Keyboard.Key>;
  private offs: Array<() => void> = [];
  private last: string | null = null;
  private objs: Array<HouseObject & { sprite: Phaser.GameObjects.GameObject }> = [];

  constructor() {
    super('House');
  }

  init(data: { houseId: string }): void {
    this.houseId = data.houseId;
  }

  create(): void {
    this.ctx = this.registry.get(CTX_KEY) as GameContext;
    const room = ROOMS[this.houseId] ?? ROOMS['house-grandma'];
    if (!room) return;
    this.cameras.main.setBackgroundColor(0x0d0f1f);
    const cx = this.scale.width / 2;
    const cy = this.scale.height / 2;
    const W = 720;
    const H = 420;
    const ox = cx - W / 2;
    const oy = cy - H / 2 + 20;
    const g = this.add.graphics();
    // back wall
    g.fillStyle(room.wall, 1); g.fillRect(ox, oy - 150, W, 150);
    g.fillStyle(0x000000, 0.18); g.fillRect(ox, oy - 150, W, 12);
    // left side wall (oblique)
    g.fillStyle(room.wall, 1); g.fillPoints([new Phaser.Geom.Point(ox - 70, oy - 80), new Phaser.Geom.Point(ox, oy - 150), new Phaser.Geom.Point(ox, oy), new Phaser.Geom.Point(ox - 70, oy + 70)], true);
    g.fillStyle(0x000000, 0.22); g.fillPoints([new Phaser.Geom.Point(ox - 70, oy - 80), new Phaser.Geom.Point(ox, oy - 150), new Phaser.Geom.Point(ox, oy), new Phaser.Geom.Point(ox - 70, oy + 70)], true);
    // floor
    g.fillStyle(room.floor, 1); g.fillRect(ox, oy, W, H);
    g.lineStyle(2, 0x000000, 0.12);
    for (let x = ox; x <= ox + W; x += 60) g.lineBetween(x, oy, x, oy + H);
    for (let y = oy; y <= oy + H; y += 60) g.lineBetween(ox, y, ox + W, y);
    g.lineStyle(6, 0x2a1a14, 1); g.strokeRect(ox, oy, W, H);
    // window glow
    g.fillStyle(0xffe3a0, 0.9); g.fillRoundedRect(ox + W / 2 - 50, oy - 120, 100, 80, 8);
    g.lineStyle(4, 0x3a2a35, 1); g.strokeRoundedRect(ox + W / 2 - 50, oy - 120, 100, 80, 8);
    this.add.text(cx, oy - 175, room.title, { fontFamily: 'Segoe UI, Arial', fontSize: '26px', color: '#ffcf6b', rtl: true }).setOrigin(0.5);
    // exit door mat
    g.fillStyle(0x5b3a2a, 1); g.fillRoundedRect(cx - 40, oy + H - 18, 80, 28, 6);
    this.add.text(cx, oy + H + 28, 'דלת יציאה', { fontFamily: 'Segoe UI, Arial', fontSize: '16px', color: '#a9b0d6', rtl: true }).setOrigin(0.5);

    this.objs = [];
    for (const o of room.objects) {
      const r = this.add.rectangle(ox + o.x - 400 + W / 2 - 0, oy + o.y - 280, o.w, o.h, o.color).setStrokeStyle(3, 0x2a1a14);
      this.add.ellipse(r.x, r.y + o.h / 2, o.w * 1.05, 14, 0x000000, 0.25).setDepth(r.depth - 1);
      this.objs.push({ ...o, x: r.x, y: r.y, sprite: r });
    }

    const key = this.ctx.save.data.look === 'boy' ? 'player_boy_ph' : 'player_ph';
    this.player = this.add.image(cx, oy + H - 70, key).setOrigin(0.5, 1);
    this.keys = (this.input.keyboard?.addKeys('W,A,S,D,UP,DOWN,LEFT,RIGHT') ?? {}) as Record<string, Phaser.Input.Keyboard.Key>;

    const bounds = { x1: ox + 30, x2: ox + W - 30, y1: oy + 80, y2: oy + H - 4 };
    this.registry.set('houseBounds', bounds);
    this.offs.push(bus.on('interact:use', ({ id }) => this.onUse(id)));
    this.events.once('shutdown', () => {
      this.offs.forEach((o) => o());
      this.offs = [];
      bus.emit('interact:available', null);
    });
    this.ctx.hud.setVisible(true);
    this.ctx.joystick.setVisible(true);
    bus.emit('interact:available', null);
  }

  private onUse(id: string): void {
    if (this.ctx.modal || !this.scene.isActive()) return;
    if (id === 'exit') bus.emit('world:exit-house', { houseId: this.houseId });
  }

  update(_t: number, dtMs: number): void {
    const dt = Math.min(dtMs, 50) / 1000;
    const c = this.ctx;
    if (!c.modal) c.session.tick(dt);
    c.hud.setTimer(c.session.remaining, c.session.phase !== 'free');
    c.hud.setCoins(c.save.data.coins);
    const b = this.registry.get('houseBounds') as { x1: number; x2: number; y1: number; y2: number };
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
    this.player.x = Phaser.Math.Clamp(this.player.x + vx * 170 * dt, b.x1, b.x2);
    this.player.y = Phaser.Math.Clamp(this.player.y + vy * 170 * dt, b.y1, b.y2);
    if (vx !== 0) this.player.setFlipX(vx < 0);
    this.player.setDepth(this.player.y + 1000);

    let best: { id: string; label: string } | null = null;
    let bd = 95;
    for (const o of this.objs) {
      const d = Math.hypot(o.x - this.player.x, o.y - this.player.y);
      if (d < bd) { bd = d; best = { id: `obj:${this.houseId}:${o.id}`, label: o.label }; }
    }
    if (!best && this.player.y > b.y2 - 110 && Math.abs(this.player.x - this.scale.width / 2) < 120) best = { id: 'exit', label: 'לצאת מהבית' };
    const id = best?.id ?? null;
    if (id !== this.last) {
      this.last = id;
      bus.emit('interact:available', best);
    }
  }
}
