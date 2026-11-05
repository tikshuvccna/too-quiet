import Phaser from 'phaser';
import { BUILDINGS, DECOR, WORLD, type BuildingDef } from './layout';

/** Time of day as 0..1: 0 dawn, 0.25 noon, 0.5 dusk, 0.75 deep night. */
const SKY_KEYS: Array<[number, number]> = [
  [0.0, 0xffd9c4], [0.12, 0xffffff], [0.3, 0xffffff], [0.4, 0xffe2b8],
  [0.5, 0xe0a0a8], [0.58, 0x9a86c0], [0.7, 0x6a7cb8], [0.85, 0x7a88c4], [1.0, 0xffd9c4],
];

function lerpHex(a: number, b: number, t: number): number {
  const ca = Phaser.Display.Color.IntegerToColor(a);
  const cb = Phaser.Display.Color.IntegerToColor(b);
  const c = Phaser.Display.Color.Interpolate.ColorWithColor(ca, cb, 100, Math.round(t * 100));
  return Phaser.Display.Color.GetColor(c.r, c.g, c.b);
}

export function skyColor(t: number): number {
  const x = ((t % 1) + 1) % 1;
  for (let i = 0; i < SKY_KEYS.length - 1; i++) {
    const [t0, c0] = SKY_KEYS[i] as [number, number];
    const [t1, c1] = SKY_KEYS[i + 1] as [number, number];
    if (x >= t0 && x <= t1) return lerpHex(c0, c1, (x - t0) / (t1 - t0 || 1));
  }
  return 0xffffff;
}

/** 0 in daylight, 1 at night: drives lamps, fireflies and window glow. */
export function nightness(t: number): number {
  const x = ((t % 1) + 1) % 1;
  if (x < 0.42) return 0;
  if (x < 0.62) return (x - 0.42) / 0.2;
  if (x < 0.88) return 1;
  return Math.max(0, 1 - (x - 0.88) / 0.12);
}

interface Cloud { img: Phaser.GameObjects.Image; shadow: Phaser.GameObjects.Image; speed: number }

/** Clouds with ground shadows, god rays, motes and fireflies, chimney smoke, the windmill, and a day-night cycle. */
export class Atmosphere {
  private readonly clouds: Cloud[] = [];
  private readonly rays: Phaser.GameObjects.Image[] = [];
  private readonly motes: Array<{ img: Phaser.GameObjects.Image; ox: number; oy: number; ph: number }> = [];
  private readonly lamps: Phaser.GameObjects.Image[] = [];
  private readonly tint: Phaser.GameObjects.Rectangle;
  private readonly sails: Array<{ a: Phaser.GameObjects.Image; b: Phaser.GameObjects.Image | null }> = [];
  private readonly smokeTimers: Phaser.Time.TimerEvent[] = [];
  /** Time of day, advanced by update(). A full day is 20 real minutes. */
  tod = 0.4;

  constructor(private readonly scene: Phaser.Scene, startTod: number, meta: Record<string, { anchor: { x: number; y: number }; smoke?: Array<{ x: number; y: number }>; hub?: { x: number; y: number } }>) {
    this.tod = startTod;
    // colour grade for the time of day: a multiply layer over the world, under the truth effects
    this.tint = scene.add.rectangle(-4000, -3000, 12000, 9000, 0xffffff, 1).setOrigin(0).setScrollFactor(0).setDepth(3990).setBlendMode(Phaser.BlendModes.MULTIPLY);

    for (let i = 0; i < 7; i++) {
      const frame = `cloud_${(i % 5) + 1}`;
      const x = (i / 7) * WORLD.w + 200;
      const y = 300 + ((i * 577) % (WORLD.h - 500));
      const sc = 0.9 + (i % 3) * 0.3;
      const shadow = scene.add.image(x + 160, y + 520, 'blob').setScale(sc * 6, sc * 2.4).setAlpha(0.2).setDepth(-700);
      const img = scene.add.image(x, y, 'fx', frame).setScale(sc).setAlpha(0.8).setDepth(3800);
      this.clouds.push({ img, shadow, speed: 7 + (i % 4) * 3 });
    }
    for (let i = 0; i < 5; i++) {
      const r = scene.add.image(400 + i * 420, 700 + ((i * 331) % 900), 'fx', 'godray').setOrigin(0.5, 0).setAlpha(0.22).setDepth(3700).setBlendMode(Phaser.BlendModes.ADD).setScale(1.5);
      r.setRotation(0.5);
      this.rays.push(r);
    }
    for (let i = 0; i < 46; i++) {
      const img = scene.add.image(0, 0, 'fx', i % 3 === 0 ? 'mote_white' : 'mote_warm').setAlpha(0).setDepth(3600).setBlendMode(Phaser.BlendModes.ADD);
      this.motes.push({ img, ox: 600 + ((i * 457) % (WORLD.w - 1200)), oy: 500 + ((i * 691) % (WORLD.h - 1000)), ph: i * 1.7 });
    }
    for (const d of DECOR) {
      if (d.frame !== 'lamppost') continue;
      this.lamps.push(scene.add.image(d.x, d.y - 120, 'dot_gold').setScale(7).setAlpha(0).setDepth(3500).setBlendMode(Phaser.BlendModes.ADD));
    }
    for (const b of BUILDINGS) this.attachBuildingFx(b, meta[b.frame]);
  }

  private attachBuildingFx(b: BuildingDef, m: { smoke?: Array<{ x: number; y: number }>; hub?: { x: number; y: number } } | undefined): void {
    if (!m) return;
    for (const s of m.smoke ?? []) {
      this.smokeTimers.push(this.scene.time.addEvent({
        delay: 900 + (b.x % 400), loop: true,
        callback: () => this.puff(b.x + s.x * b.scale, b.y + s.y * b.scale),
      }));
    }
    if (m.hub) {
      const hx = b.x + m.hub.x * b.scale;
      const hy = b.y + m.hub.y * b.scale;
      const a = this.scene.add.image(hx, hy, 'buildings', 'mill_sails').setScale(b.scale).setDepth(b.y + 2);
      const bt = this.scene.add.image(hx, hy, 'buildings_truth', 'mill_sails_truth').setScale(b.scale).setDepth(b.y + 3).setAlpha(0);
      this.sails.push({ a, b: bt });
    }
  }

  /** Chimney smoke for buildings that are not in the village layout (offsets in px from the anchor). */
  addSmoke(x: number, y: number, offsets: Array<{ x: number; y: number }>): void {
    for (const s of offsets) {
      this.smokeTimers.push(this.scene.time.addEvent({ delay: 1000 + (x % 500), loop: true, callback: () => this.puff(x + s.x, y + s.y) }));
    }
  }

  private smokeOn = true;
  private motesMax = 46;
  private cloudsMax = 7;
  private raysOn = true;

  /** Fewer clouds, rays, dust and smoke on weaker devices. */
  setQuality(p: { clouds: number; rays: boolean; motes: number; smoke: boolean }): void {
    this.smokeOn = p.smoke;
    this.motesMax = p.motes;
    this.cloudsMax = p.clouds;
    this.raysOn = p.rays;
    this.clouds.forEach((c, i) => { c.img.setVisible(i < p.clouds); c.shadow.setVisible(i < p.clouds); });
    this.rays.forEach((r) => r.setVisible(p.rays));
    this.lamps.forEach((l) => l.setVisible(true));
  }

  private truthNow = 0;

  private puff(x: number, y: number): void {
    const cam = this.scene.cameras.main;
    const v = cam.worldView;
    if (!this.smokeOn || this.truthNow > 0.5 || x < v.x - 200 || x > v.right + 200 || y < v.y - 400 || y > v.bottom + 200) return;
    const p = this.scene.add.image(x, y, 'fx', `smoke_${Phaser.Math.Between(0, 9)}`).setScale(0.35).setAlpha(0.6).setDepth(y + 400);
    this.scene.tweens.add({
      targets: p, y: y - 110, x: x + 30 + Math.random() * 30, scale: 1.25, alpha: 0, duration: 3200, ease: 'sine.out',
      onComplete: () => p.destroy(),
    });
  }

  update(dtMs: number, truth: number, playerX: number, playerY: number): void {
    const dt = dtMs / 1000;
    this.truthNow = truth;
    this.tod = (this.tod + dt / 1200) % 1;
    const night = nightness(this.tod);
    // the truth is always dim and cold: pull the sky towards a flat grey-blue
    this.tint.setFillStyle(lerpHex(skyColor(this.tod), 0xb8c0d8, Math.min(1, truth * 0.8)));

    for (const [ci, c] of this.clouds.entries()) {
      if (ci >= this.cloudsMax) continue;
      c.img.x += c.speed * dt;
      if (c.img.x > WORLD.w + 500) c.img.x = -500;
      c.shadow.x = c.img.x + 160;
      c.img.setAlpha(0.34 - 0.12 * night).setTint(lerpHex(0xffffff, 0x4e5678, Math.min(1, truth * 0.9 + night * 0.5)));
      c.shadow.setAlpha(0.2 * (1 - night * 0.5));
    }
    for (const r of this.rays) if (this.raysOn) r.setAlpha(0.22 * (1 - night) * (1 - truth));
    const t = this.scene.time.now / 1000;
    for (const [mi, m] of this.motes.entries()) {
      if (mi >= this.motesMax) { m.img.setVisible(false); continue; }
      const dx = Math.sin(t * 0.25 + m.ph) * 90;
      const dy = Math.cos(t * 0.21 + m.ph * 1.3) * 70;
      m.img.setPosition(m.ox + dx, m.oy + dy);
      const near = Math.hypot(m.ox - playerX, m.oy - playerY) < 1500;
      m.img.setVisible(near);
      m.img.setAlpha(near ? (0.18 + 0.7 * night) * (0.6 + 0.4 * Math.sin(t * 2 + m.ph)) * (1 - truth * 0.6) : 0);
    }
    for (const l of this.lamps) l.setAlpha((0.15 + 0.5 * night) * (1 - truth * 0.7));
    for (const s of this.sails) {
      s.a.rotation += dt * 0.55;
      if (s.b) {
        s.b.rotation = s.a.rotation;
        s.b.setAlpha(Math.min(1, truth * 1.3));
      }
    }
  }

  destroy(): void {
    for (const t of this.smokeTimers) t.remove();
  }
}
