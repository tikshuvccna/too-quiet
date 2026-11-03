import Phaser from 'phaser';
import type { Actor } from '../game/actors';
import type { NpcDef } from './layout';

interface NpcRef { actor: Actor; def: NpcDef; baseTint: number | undefined }

function lerpColor(a: number, b: number, t: number): number {
  const ca = Phaser.Display.Color.IntegerToColor(a);
  const cb = Phaser.Display.Color.IntegerToColor(b);
  const c = Phaser.Display.Color.Interpolate.ColorWithColor(ca, cb, 100, Math.round(t * 100));
  return Phaser.Display.Color.GetColor(c.r, c.g, c.b);
}

export interface Swappable { img: Phaser.GameObjects.Image; frame: string; atlas: string }

/**
 * The cold face of the valley, on top of the cheerful one while the needle looks: drifting fog,
 * villagers ashen and hung on strings, and the withered "truth" sprites for trees and lamps.
 * (Buildings and rooms carry their own truth art; the world scene cross-fades them.)
 */
export class TruthLayer {
  private readonly fog: Phaser.GameObjects.Image[] = [];
  private readonly strings: Phaser.GameObjects.Graphics;
  private swapped = false;
  private twitch = 0;

  constructor(
    scene: Phaser.Scene,
    private readonly npcs: NpcRef[],
    private readonly swaps: Swappable[],
    private readonly anchor: { x: number; y: number },
  ) {
    for (let i = 0; i < 9; i++) {
      const f = scene.add.image(300 + i * 270, 500 + (i % 3) * 480, 'blob').setScale(15, 7).setTint(0xaebbe0).setAlpha(0).setDepth(3900);
      this.fog.push(f);
    }
    this.strings = scene.add.graphics().setDepth(3950).setBlendMode(Phaser.BlendModes.ADD);
  }

  update(timeMs: number, truth: number): void {
    const on = truth > 0.04;
    const t = timeMs / 1000;
    this.fog.forEach((f, i) => {
      f.setAlpha(0.2 * truth).setVisible(on);
      f.x += Math.sin(t * 0.2 + i) * 0.25;
    });

    // villagers: ashen, twitching, hung on strings that run up to the Head
    this.twitch = Math.sin(t * 3.1) > 0.92 ? (Math.random() - 0.5) * 3 : this.twitch * 0.8;
    this.strings.clear();
    for (const n of this.npcs) {
      const a = n.actor;
      const tint = n.baseTint === undefined ? 0xffffff : n.baseTint;
      if (truth > 0.04) a.sprite.setTint(lerpColor(tint, 0x7e89a8, Math.min(1, truth * 0.85)));
      else if (n.baseTint !== undefined) a.sprite.setTint(n.baseTint);
      else a.sprite.clearTint();
      a.sprite.x = truth > 0.3 ? n.def.x + this.twitch : n.def.x;
      // the puppet strings appear only once the truth is clear enough (after the first lesson)
      if (truth < 0.5 || n.def.id === 'dvora') continue;
      const hx = n.def.x;
      const hy = n.def.y - 100 * (n.def.scale ?? 1);
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

    // trees and lamps swap to their withered versions past half way (many sprites: only on crossing)
    const want = truth > 0.5;
    if (want !== this.swapped) {
      this.swapped = want;
      for (const s of this.swaps) {
        if (want) s.img.setTexture('buildings_truth', `${s.frame}_truth`);
        else s.img.setTexture(s.atlas, s.frame);
      }
    }
  }
}
