import Phaser from 'phaser';
import { bus } from '../core/bus';
import { createActor, setIdleFacing, updateActor, type Actor } from '../game/actors';
import { TruthFx, truthLevel } from '../game/truthFx';
import { drawRoads } from '../world/roads';
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
  private pickups = new Map<string, Phaser.GameObjects.Image>();
  private fx!: TruthFx;
  private truthLayer!: TruthLayer;
  private npcRefs: Array<{ actor: Actor; def: (typeof NPCS)[number]; baseTint: number | undefined }> = [];
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
    this.pickups.clear();
    this.faultLabels.clear();
    this.dots = [];
    this.npcRefs = [];
    this.swaps = [];
    this.truthBuildings = [];
    this.buildGround();
    this.buildProps();
    this.buildNpcs();
    this.refreshPickups();
    this.buildPlayer();
    this.buildSight();
    this.truthLayer = new TruthLayer(this, this.npcRefs, this.swaps, { x: 2180, y: 420 });
    const bmeta = (this.cache.json.get('buildings:meta') as { frames: Record<string, { anchor: { x: number; y: number }; smoke?: Array<{ x: number; y: number }>; hub?: { x: number; y: number } }> }).frames;
    this.creatures = new CreatureManager(this);
    this.atmos = new Atmosphere(this, (this.registry.get('tod') as number | undefined) ?? 0.4, bmeta);

    const cam = this.cameras.main;
    cam.setBounds(0, 0, WORLD.w, WORLD.h);
    cam.startFollow(this.player.sprite, true, 0.12, 0.12, 0, -40);
    this.fx = new TruthFx(cam);
    this.applyZoom();
    this.scale.on('resize', () => this.applyZoom());

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
    this.add.tileSprite(0, 0, WORLD.w, WORLD.h, 'grass').setOrigin(0).setDepth(-1000);
    const g = this.add.graphics().setDepth(-900);
    const stroke = (pts: Array<[number, number]>, w: number, col: number): void => {
      g.lineStyle(w, col, 1);
      g.beginPath();
      pts.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y)));
      g.strokePath();
    };
    const road = (pts: Array<[number, number]>, w: number): void => {
      stroke(pts, w + 14, 0x6b5a45);
      stroke(pts, w, 0xc6aa7c);
    };
    // the stream crosses the south-east road at the bridge (perpendicular, so it reads as a crossing)
    const stream: Array<[number, number]> = [[2300, 1080], [2140, 1190], [1968, 1292], [1830, 1380], [1740, 1520], [1700, 1780]];
    stroke(stream, 84, 0x2c5a72);
    stroke(stream, 66, 0x3f86a6);
    stroke(stream, 22, 0x7fc4de);
    drawRoads(g);
    // wooden bridge along the road direction
    const ang = Math.atan2(1382 - 1292, 2060 - 1968);
    this.add.rectangle(1968, 1292, 150, 70, 0x3a2a1a).setRotation(ang).setDepth(-850);
    this.add.rectangle(1968, 1292, 140, 60, 0x8a6a46).setRotation(ang).setDepth(-849);
    for (let i = -6; i <= 6; i++) {
      this.add.rectangle(1968 + Math.cos(ang) * i * 10, 1292 + Math.sin(ang) * i * 10, 3, 58, 0x4a331f).setRotation(ang).setDepth(-848);
    }
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
    // trees around the edge and a few inside, seeded
    let s = 3;
    const r = (): number => ((s = (s * 16807) % 2147483647) / 2147483647);
    const keepClear = (x: number, y: number): boolean =>
      BUILDINGS.some((b) => Math.abs(b.x - x) < 260 && y > b.y - 200 && y < b.y + 260) ||
      (x > 900 && x < 1900 && y > 880 && y < 1500) || (x > 1800 && x < 2150 && y > 1000 && y < 1800) || (x > 480 && x < 1000 && y > 960 && y < 1560);
    for (let i = 0; i < 190; i++) {
      const edge = r() < 0.7;
      const x = edge ? (r() < 0.5 ? r() * 320 : WORLD.w - r() * 320) : 160 + r() * (WORLD.w - 320);
      const y = edge && r() < 0.5 ? (r() < 0.5 ? r() * 260 : WORLD.h - r() * 260) : 160 + r() * (WORLD.h - 320);
      if (keepClear(x, y)) continue;
      const sc = 0.75 + r() * 0.4;
      const frame = r() < 0.65 ? 'tree_round' : 'tree_pine';
      this.add.image(x, y - 2, 'blob').setScale(sc * 1.4).setDepth(y - 1);
      this.swaps.push({ img: this.prop(frame, x, y, sc), frame, atlas: 'props' });
      this.blockers.push({ x, y: y - 6, r: 20 * sc });
    }
  }

  private buildNpcs(): void {
    for (const n of NPCS) {
      const a = createActor(this, n.char, n.x, n.y, undefined, n.scale ?? 1);
      updateActor(a, n.x, n.y, 0, 0);
      setIdleFacing(a, n.x > 1500 ? 'SW' : 'SE');
      this.npcRefs.push({ actor: a, def: n, baseTint: undefined });
      this.blockers.push({ x: n.x, y: n.y - 4, r: 20 });
    }
  }

  private pickupAllowed(p: PickupDef): boolean {
    if (this.ctx.save.data.collected[p.id]) return false;
    return !p.requires || this.ctx.save.hasFlag(p.requires);
  }

  /** Spawn pickups whose story requirement has just been met. */
  private refreshPickups(): void {
    for (const p of PICKUPS) {
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
    this.player = createActor(this, char, this.px, this.py);
    updateActor(this.player, this.px, this.py, 0, 0);
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
    for (const n of NPCS) out.push({ id: `npc:${n.id}`, x: n.x, y: n.y, label: n.label });
    for (const p of PICKUPS) if (this.pickups.has(p.id)) out.push({ id: `pickup:${p.id}`, x: p.x, y: p.y, label: 'לאסוף' });
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
    const speed = SPEED * (this.sightOn ? 0.8 : 1);
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
    this.creatures.update(dtMs, this.atmos.tod);
    this.ctx.head.setTruth(tv, dt);

    this.pickupClock += dt;
    if (this.pickupClock > 0.6) {
      this.pickupClock = 0;
      this.refreshPickups();
    }
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
      const d = Math.hypot(t.x - this.px, t.y - this.py);
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
      const near = Math.hypot(f.x - this.px, f.y - this.py) < 190;
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
