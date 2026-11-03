import Phaser from 'phaser';
import type { Actor } from '../game/actors';
import { BUILDINGS, type BuildingDef, type NpcDef } from './layout';

interface NpcRef { actor: Actor; def: NpcDef; baseTint: number | undefined }

function hash(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function lerpColor(a: number, b: number, t: number): number {
  const ca = Phaser.Display.Color.IntegerToColor(a);
  const cb = Phaser.Display.Color.IntegerToColor(b);
  const c = Phaser.Display.Color.Interpolate.ColorWithColor(ca, cb, 100, Math.round(t * 100));
  return Phaser.Display.Color.GetColor(c.r, c.g, c.b);
}

/**
 * The cold face of the valley, drawn on top of the cheerful one while the needle looks:
 * cracks in the walls, snapped threads hanging from the eaves, drifting fog, villagers on strings.
 * (Blender "truth" sprites will replace the cracks later; the strings and fog stay.)
 */
export class TruthLayer {
  private readonly buildingFx: Array<{ g: Phaser.GameObjects.Graphics; b: BuildingDef }> = [];
  private readonly fog: Phaser.GameObjects.Image[] = [];
  private readonly strings: Phaser.GameObjects.Graphics;
  private lastTreeTruth = -1;
  private twitch = 0;

  constructor(
    private readonly scene: Phaser.Scene,
    private readonly npcs: NpcRef[],
    private readonly trees: Phaser.GameObjects.Image[],
    private readonly anchor: { x: number; y: number },
  ) {
    for (const b of BUILDINGS) this.buildingFx.push({ g: this.drawBuilding(b), b });
    for (let i = 0; i < 9; i++) {
      const f = scene.add.image(300 + i * 270, 500 + (i % 3) * 480, 'blob').setScale(15, 7).setTint(0xaebbe0).setAlpha(0).setDepth(3900);
      this.fog.push(f);
    }
    this.strings = scene.add.graphics().setDepth(3950).setBlendMode(Phaser.BlendModes.ADD);
  }

  private drawBuilding(b: BuildingDef): Phaser.GameObjects.Graphics {
    const g = this.scene.add.graphics().setDepth(b.y + 2).setAlpha(0).setVisible(false);
    let seed = hash(b.id) || 1;
    const rnd = (): number => (seed = (seed * 16807) % 2147483647) / 2147483647;
    const w = b.scale * 100;
    const h = b.scale * 110;
    // cracks in the walls
    for (let c = 0; c < 5; c++) {
      let x = b.x - w + rnd() * w * 2;
      let y = b.y - h + rnd() * (h - 18);
      let a = rnd() * Math.PI * 2;
      g.lineStyle(2.4, 0x07070f, 0.85);
      g.beginPath();
      g.moveTo(x, y);
      for (let s = 0; s < 6; s++) {
        a += (rnd() - 0.5) * 1.5;
        x += Math.cos(a) * (10 + rnd() * 9);
        y += Math.sin(a) * (10 + rnd() * 9) * 0.8;
        g.lineTo(x, y);
      }
      g.strokePath();
    }
    // snapped threads hanging from the eaves
    for (const side of [-1, 1]) {
      const sx = b.x + side * w * 1.05;
      const sy = b.y - h * 1.28;
      g.lineStyle(2.2, 0x5cf0d0, 0.55);
      g.beginPath();
      g.moveTo(sx, sy);
      const len = 55 + rnd() * 70;
      for (let i = 1; i <= 10; i++) {
        const t = i / 10;
        g.lineTo(sx + side * Math.sin(t * 3) * 8, sy + t * len);
      }
      g.strokePath();
      g.fillStyle(0xaef7e6, 0.7);
      g.fillCircle(sx + side * Math.sin(3) * 8, sy + len, 3);
    }
    return g;
  }

  update(timeMs: number, truth: number, playerDist?: (x: number, y: number) => number): void {
    const on = truth > 0.04;
    const t = timeMs / 1000;
    for (const { g, b } of this.buildingFx) {
      g.setVisible(on).setAlpha(Math.min(1, truth * 1.3));
      void b;
    }
    this.fog.forEach((f, i) => {
      f.setAlpha(0.2 * truth).setVisible(on);
      f.x += Math.sin(t * 0.2 + i) * 0.25;
    });

    // villagers: ashen, twitching, hung on strings that run up to the tower
    this.twitch = Math.sin(t * 3.1) > 0.92 ? (Math.random() - 0.5) * 3 : this.twitch * 0.8;
    this.strings.clear();
    for (const n of this.npcs) {
      const a = n.actor;
      const tint = n.baseTint === undefined ? 0xffffff : n.baseTint;
      if (truth > 0.04) a.sprite.setTint(lerpColor(tint, 0x7e89a8, Math.min(1, truth * 0.85)));
      else if (n.baseTint !== undefined) a.sprite.setTint(n.baseTint);
      else a.sprite.clearTint();
      if (truth > 0.3) a.sprite.x = n.def.x + this.twitch;
      else a.sprite.x = n.def.x;
      if (!on || n.def.id === 'dvora') continue;
      const hx = n.def.x;
      const hy = n.def.y - 100 * (n.def.scale ?? 1);
      this.strings.lineStyle(1.6, 0xbfeaff, 0.5 * truth);
      // a small control bar above the head, like a puppeteer's cross
      this.strings.lineStyle(3, 0xdff6ff, 0.75 * truth);
      this.strings.lineBetween(hx - 12, hy - 14, hx + 12, hy - 14);
      this.strings.lineStyle(1.6, 0xbfeaff, 0.5 * truth);
      this.strings.lineBetween(hx - 9, hy - 14, hx - 3, hy);
      this.strings.lineBetween(hx + 9, hy - 14, hx + 3, hy);
      for (let s = -1; s <= 1; s++) {
        const sway = Math.sin(t * 0.9 + n.def.x * 0.01 + s) * 14;
        const tx = hx + s * 26 + (this.anchor.x - hx) * 0.12 + sway;
        const ty = hy - 900;
        this.strings.beginPath();
        this.strings.moveTo(hx + s * 9, hy - 14);
        const mx = (hx + tx) / 2 + sway * 0.6;
        const my = (hy - 14 + ty) / 2;
        const steps = 14;
        for (let i = 1; i <= steps; i++) {
          const u = i / steps;
          const x = (1 - u) * (1 - u) * (hx + s * 9) + 2 * (1 - u) * u * mx + u * u * tx;
          const y = (1 - u) * (1 - u) * (hy - 14) + 2 * (1 - u) * u * my + u * u * ty;
          this.strings.lineTo(x, y);
        }
        this.strings.strokePath();
      }
      this.strings.fillStyle(0xdff6ff, 0.7 * truth);
      this.strings.fillCircle(hx, hy, 3);
    }

    // trees wither (only retint when the value moved enough, there are many)
    if (Math.abs(truth - this.lastTreeTruth) > 0.04) {
      this.lastTreeTruth = truth;
      const col = lerpColor(0xffffff, 0x8a8c7a, Math.min(1, truth));
      for (const tr of this.trees) tr.setTint(col);
    }
    void playerDist;
  }
}
