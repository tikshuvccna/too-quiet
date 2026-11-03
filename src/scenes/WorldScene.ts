import Phaser from 'phaser';
import { bus } from '../core/bus';
import { CTX_KEY, type GameContext } from '../game/context';
import {
  BUILDINGS, FAULTS, NPCS, PICKUPS, START_SPAWN, THREADS, WALLS, WORLD, type FaultDef, type ThreadDef,
} from '../world/layout';

const SPEED = 190;
const INTERACT_RANGE = 78;
const PLAYER_R = 16;

interface Target { id: string; x: number; y: number; label: string; range?: number }

function closestOnSegment(a: { x: number; y: number }, b: { x: number; y: number }, p: { x: number; y: number }): { x: number; y: number; t: number } {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const t = Math.max(0, Math.min(1, ((p.x - a.x) * dx + (p.y - a.y) * dy) / (dx * dx + dy * dy)));
  return { x: a.x + dx * t, y: a.y + dy * t, t };
}

export class WorldScene extends Phaser.Scene {
  private ctx!: GameContext;
  private player!: Phaser.GameObjects.Image;
  private keys!: Record<string, Phaser.Input.Keyboard.Key>;
  private trees: Array<{ x: number; y: number; r: number }> = [];
  private pickups = new Map<string, Phaser.GameObjects.Image>();
  private dim!: Phaser.GameObjects.Rectangle;
  private sightG!: Phaser.GameObjects.Graphics;
  private sightOn = false;
  private faultLabels = new Map<string, Phaser.GameObjects.Text>();
  private dots: Phaser.GameObjects.Image[] = [];
  private offs: Array<() => void> = [];
  private spawn = START_SPAWN;
  private lastTarget: string | null = null;

  constructor() {
    super('World');
  }

  init(data: { spawn?: { x: number; y: number } }): void {
    this.spawn = data?.spawn ?? START_SPAWN;
  }

  create(): void {
    this.ctx = this.registry.get(CTX_KEY) as GameContext;
    this.sightOn = false;
    this.trees = [];
    this.pickups.clear();
    this.faultLabels.clear();
    this.dots = [];
    this.buildGround();
    this.buildProps();
    this.buildNpcs();
    this.buildPickups();
    this.buildPlayer();
    this.buildSight();

    const cam = this.cameras.main;
    cam.setBounds(0, 0, WORLD.w, WORLD.h);
    cam.startFollow(this.player, true, 0.12, 0.12);
    this.applyZoom();
    this.scale.on('resize', () => this.applyZoom());

    const kb = this.input.keyboard;
    this.keys = (kb?.addKeys('W,A,S,D,UP,DOWN,LEFT,RIGHT') ?? {}) as Record<string, Phaser.Input.Keyboard.Key>;

    this.offs.push(
      bus.on('interact:use', ({ id }) => this.onUse(id)),
      bus.on('sight:toggle', ({ on }) => this.setSight(on)),
    );
    this.events.once('shutdown', () => {
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
    this.cameras.main.setZoom(Phaser.Math.Clamp(Math.min(w / 1100, h / 700), 0.62, 1.5));
  }

  private buildGround(): void {
    this.add.tileSprite(0, 0, WORLD.w, WORLD.h, 'grass').setOrigin(0).setDepth(-1000);
    const g = this.add.graphics().setDepth(-900);
    const road = (pts: Array<[number, number]>, w: number): void => {
      g.lineStyle(w + 14, 0x6b5a45, 1);
      g.beginPath(); pts.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y))); g.strokePath();
      g.lineStyle(w, 0xc6aa7c, 1);
      g.beginPath(); pts.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y))); g.strokePath();
    };
    road([[760, 910], [760, 1010], [1280, 1010], [1280, 790]], 74);
    road([[1280, 1010], [1780, 1010], [1780, 930]], 74);
    road([[1280, 1010], [1250, 1380]], 74);
    road([[1780, 1010], [2100, 900], [2180, 620]], 64);
    // flowers and tufts, deterministic
    let s = 11;
    const r = (): number => ((s = (s * 16807) % 2147483647) / 2147483647);
    for (let i = 0; i < 420; i++) {
      const x = r() * WORLD.w;
      const y = r() * WORLD.h;
      g.fillStyle([0xffe9a8, 0xffb3c6, 0xd6c8ff, 0xffffff][Math.floor(r() * 4)] as number, 0.85);
      g.fillCircle(x, y, 2 + r() * 2);
    }
  }

  private buildProps(): void {
    for (const b of BUILDINGS) {
      const img = this.add.image(b.x, b.y, b.kind).setOrigin(0.5, 1).setDepth(b.y);
      void img;
    }
    // trees around the edge and a few inside, seeded
    let s = 3;
    const r = (): number => ((s = (s * 16807) % 2147483647) / 2147483647);
    const keepClear = (x: number, y: number): boolean =>
      BUILDINGS.some((b) => Math.abs(b.x - x) < 230 && y > b.y - 40 && y < b.y + 240) || (x > 900 && x < 1900 && y > 880 && y < 1500) || Math.hypot(x - 2180, y - 640) < 300;
    for (let i = 0; i < 170; i++) {
      const edge = r() < 0.7;
      const x = edge ? (r() < 0.5 ? r() * 320 : WORLD.w - r() * 320) : 160 + r() * (WORLD.w - 320);
      const y = edge && r() < 0.5 ? (r() < 0.5 ? r() * 260 : WORLD.h - r() * 260) : 160 + r() * (WORLD.h - 320);
      if (keepClear(x, y)) continue;
      const sc = 0.8 + r() * 0.5;
      this.add.image(x, y, 'tree').setOrigin(0.5, 1).setScale(sc).setDepth(y);
      this.trees.push({ x, y: y - 8, r: 18 * sc });
    }
  }

  private buildNpcs(): void {
    for (const n of NPCS) {
      const key = n.id === 'dvora' ? 'npc_dvora' : n.id === 'hubGrandpa' ? 'npc_hub' : 'npc_ph';
      const img = this.add.image(n.x, n.y, key).setOrigin(0.5, 1).setDepth(n.y);
      this.tweens.add({ targets: img, scaleY: 1.025, duration: 1100 + (n.x % 300), yoyo: true, repeat: -1, ease: 'sine.inOut' });
    }
  }

  private buildPickups(): void {
    for (const p of PICKUPS) {
      if (this.ctx.save.data.collected[p.id]) continue;
      const key = p.kind === 'card' ? 'dot_gold' : p.kind === 'page' ? 'dot_pink' : 'dot_teal';
      const img = this.add.image(p.x, p.y - 10, key).setDepth(p.y).setScale(1.2);
      this.tweens.add({ targets: img, y: p.y - 22, duration: 900, yoyo: true, repeat: -1, ease: 'sine.inOut' });
      this.pickups.set(p.id, img);
    }
  }

  private buildPlayer(): void {
    const key = this.ctx.save.data.look === 'boy' ? 'player_boy_ph' : 'player_ph';
    this.player = this.add.image(this.spawn.x, this.spawn.y, key).setOrigin(0.5, 1);
  }

  private buildSight(): void {
    this.dim = this.add.rectangle(0, 0, 8000, 6000, 0x05061a, 0).setOrigin(0).setDepth(4000);
    this.dim.setPosition(-2000, -2000);
    this.sightG = this.add.graphics().setDepth(4500).setBlendMode(Phaser.BlendModes.ADD);
    for (let i = 0; i < THREADS.length * 3; i++) this.dots.push(this.add.image(0, 0, 'dot_gold').setDepth(4501).setVisible(false).setBlendMode(Phaser.BlendModes.ADD));
    for (const f of FAULTS) {
      const t = this.add.text(f.x, f.y - 44, '', { fontFamily: 'Segoe UI, Arial', fontSize: '18px', color: '#ffcf6b', align: 'center', backgroundColor: 'rgba(8,9,24,.85)', padding: { x: 8, y: 4 }, rtl: true }).setOrigin(0.5).setDepth(4600).setVisible(false);
      this.faultLabels.set(f.id, t);
    }
  }

  private setSight(on: boolean): void {
    this.sightOn = on;
    this.tweens.add({ targets: this.dim, fillAlpha: on ? 0.58 : 0, duration: 350 });
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
    for (const b of BUILDINGS) out.push({ id: `door:${b.id}`, x: b.door.x, y: b.door.y, label: b.label, range: 70 });
    for (const n of NPCS) out.push({ id: `npc:${n.id}`, x: n.x, y: n.y, label: n.label });
    for (const p of PICKUPS) if (this.pickups.has(p.id)) out.push({ id: `pickup:${p.id}`, x: p.x, y: p.y, label: 'לאסוף' });
    if (this.sightOn) {
      const power = this.ctx.save.data.power;
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
    } else if (id.startsWith('pickup:')) {
      const pid = id.slice(7);
      const img = this.pickups.get(pid);
      if (!img) return;
      this.pickups.delete(pid);
      this.ctx.save.data.collected[pid] = true;
      this.ctx.save.save();
      this.tweens.add({ targets: img, scale: 2.4, alpha: 0, duration: 260, onComplete: () => img.destroy() });
      bus.emit('interact:available', null);
      this.events.emit('collected', pid);
    } else if (id.startsWith('fault:')) {
      this.tryFix(FAULTS.find((f) => f.id === id.slice(6)));
    }
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

  private blocked(x: number, y: number): boolean {
    if (x < 30 || y < 30 || x > WORLD.w - 30 || y > WORLD.h - 30) return true;
    for (const [rx, ry, rw, rh] of WALLS) {
      if (x > rx - PLAYER_R && x < rx + rw + PLAYER_R && y > ry - 6 && y < ry + rh + 6) return true;
    }
    for (const t of this.trees) if (Math.hypot(x - t.x, y - t.y) < t.r + PLAYER_R) return true;
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
    const speed = SPEED * (this.sightOn ? 0.8 : 1);
    const nx = this.player.x + vx * speed * dt;
    const ny = this.player.y + vy * speed * dt;
    if (!this.blocked(nx, this.player.y)) this.player.x = nx;
    if (!this.blocked(this.player.x, ny)) this.player.y = ny;
    if (vx !== 0) this.player.setFlipX(vx < 0);
    this.player.setDepth(this.player.y);
    const bob = vx !== 0 || vy !== 0 ? Math.sin(this.time.now / 70) * 2 : 0;
    this.player.setScale(1, 1 + bob * 0.01);

    this.updateTarget();
    if (this.sightOn) this.drawSight();
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
      const d = Math.hypot(t.x - this.player.x, t.y - this.player.y);
      if (d < (t.range ?? INTERACT_RANGE) && d < bd) {
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

  private threadPath(th: ThreadDef, time: number, gap?: { x: number; y: number; t: number }): Array<{ x: number; y: number }> {
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
    void gap;
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
        if (gapAt) t = (t * gapAt.t * 0.92);
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
      const near = Math.hypot(f.x - this.player.x, f.y - this.player.y) < 190;
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
