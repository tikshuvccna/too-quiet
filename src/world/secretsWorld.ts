import Phaser from 'phaser';
import type { SaveStore } from '../core/save';
import { SECRETS, isSolved, progressOf, targetId, type Glyph, type SecretDef, type SecretNode } from './secrets';

export interface SecretTarget { id: string; x: number; y: number; label: string; range: number }

const PREFIX: Record<SecretDef['style'], string> = {
  stones: 'לגעת באבן',
  bells: 'לצלצל',
  lamps: 'להדליק',
  mushrooms: 'לדרוך על',
  tree: 'לדפוק בעץ',
};

const toInt = (c: string): number => parseInt(c.replace('#', ''), 16);

function poly(g: Phaser.GameObjects.Graphics, pts: Array<[number, number]>, x: number, y: number, s: number, fill: boolean): void {
  g.beginPath();
  pts.forEach(([px, py], i) => (i ? g.lineTo(x + px * s, y + py * s) : g.moveTo(x + px * s, y + py * s)));
  g.closePath();
  if (fill) g.fillPath();
  else g.strokePath();
}

/** One rune or symbol on a dark plate. `lit` brightens it, `dim` mutes it (a solved puzzle). */
export function drawGlyph(g: Phaser.GameObjects.Graphics, glyph: Glyph, x: number, y: number, color: number, lit: boolean, dim: boolean, size = 1, n = 1): void {
  const a = dim ? 0.35 : lit ? 1 : 0.8;
  if (glyph !== 'bell' && glyph !== 'lamp') {
    g.fillStyle(0x0b0c1c, 0.85 * (dim ? 0.6 : 1)).fillCircle(x, y, 20);
    g.lineStyle(2, color, a).strokeCircle(x, y, 20);
    if (lit) g.fillStyle(color, 0.22).fillCircle(x, y, 26);
  }
  g.fillStyle(color, a).lineStyle(2.5, color, a);
  switch (glyph) {
    case 'sun': {
      g.fillCircle(x, y, 6);
      for (let i = 0; i < 8; i++) {
        const t = (i / 8) * Math.PI * 2;
        g.lineBetween(x + Math.cos(t) * 9, y + Math.sin(t) * 9, x + Math.cos(t) * 14, y + Math.sin(t) * 14);
      }
      break;
    }
    case 'moon':
      g.fillCircle(x - 1, y, 11);
      g.fillStyle(0x0b0c1c, 1).fillCircle(x + 5, y - 2, 9.5);
      break;
    case 'star': {
      const pts: Array<[number, number]> = [];
      for (let i = 0; i < 10; i++) {
        const t = -Math.PI / 2 + (i / 10) * Math.PI * 2;
        const r = i % 2 ? 5 : 13;
        pts.push([Math.cos(t) * r, Math.sin(t) * r]);
      }
      poly(g, pts, x, y + 1, 1, true);
      break;
    }
    case 'wave':
      for (let k = -1; k <= 1; k++) {
        g.beginPath();
        for (let i = 0; i <= 12; i++) {
          const px = x - 13 + i * (26 / 12);
          const py = y + k * 7 + Math.sin((i / 12) * Math.PI * 2) * 3;
          if (i) g.lineTo(px, py);
          else g.moveTo(px, py);
        }
        g.strokePath();
      }
      break;
    case 'leaf':
      poly(g, [[0, -13], [8, -6], [9, 3], [0, 12], [-9, 3], [-8, -6]], x, y, 1, true);
      g.lineStyle(2, 0x0b0c1c, 0.9).lineBetween(x, y - 8, x, y + 14);
      break;
    case 'flame':
      poly(g, [[0, -14], [6, -5], [9, 3], [5, 11], [0, 13], [-5, 11], [-9, 3], [-5, -4], [-2, -7]], x, y, 1, true);
      g.fillStyle(0x0b0c1c, 0.8).fillCircle(x, y + 7, 3.5);
      break;
    case 'bell': {
      const s = size;
      g.lineStyle(3, 0x6b4a22, dim ? 0.5 : 1).lineBetween(x - 34 * s, y - 62 * s, x + 34 * s, y - 62 * s);
      g.lineBetween(x, y - 62 * s, x, y - 36 * s);
      if (lit) g.fillStyle(color, 0.28).fillCircle(x, y - 14 * s, 38 * s);
      g.fillStyle(color, dim ? 0.55 : 1);
      poly(g, [[-6, -34], [6, -34], [14, -22], [18, -2], [24, 8], [-24, 8], [-18, -2], [-14, -22]], x, y, s, true);
      g.fillStyle(0x4a3010, 1).fillCircle(x, y + 12 * s, 4 * s);
      break;
    }
    case 'lamp': {
      g.lineStyle(4, 0x3a3340, dim ? 0.5 : 1).lineBetween(x, y + 6, x, y - 44);
      g.fillStyle(0x2a2630, 1).fillRect(x - 12, y - 4, 24, 10);
      if (lit) g.fillStyle(color, 0.3).fillCircle(x, y - 54, 44);
      g.fillStyle(color, lit ? 1 : dim ? 0.35 : 0.55).fillCircle(x, y - 54, 13);
      g.lineStyle(2, 0x2a2630, 1).strokeCircle(x, y - 54, 13);
      break;
    }
    case 'mushroom':
      g.fillStyle(color, lit ? 0.45 : 0.25).fillCircle(x, y - 12, 34);
      g.fillStyle(color, lit ? 1 : 0.85).fillCircle(x, y - 14, 5);
      for (let i = 0; i < 4; i++) {
        const t = (i / 4) * Math.PI * 2 + 0.4;
        g.fillCircle(x + Math.cos(t) * 20, y - 14 + Math.sin(t) * 12, 2);
      }
      break;
    case 'rings':
      g.fillStyle(0x3b2a14, dim ? 0.4 : 0.75).fillCircle(x, y - 14, 22);
      g.lineStyle(2, color, a);
      for (let i = 1; i <= n; i++) g.strokeCircle(x, y - 14, 3 + i * 4.5);
      if (lit) g.fillStyle(color, 0.25).fillCircle(x, y - 14, 30);
      break;
  }
}

/** Draws and offers the markers of the secret sequences, only when the player is near one. */
export class SecretsWorld {
  private readonly g: Phaser.GameObjects.Graphics;
  private prevLen = new Map<string, number>();
  private flash = new Map<string, { until: number; kind: 'bad' | 'good' }>();
  private drewLast = false;

  constructor(private readonly scene: Phaser.Scene, private readonly save: SaveStore) {
    this.g = scene.add.graphics().setDepth(4400);
  }

  private near(s: SecretDef, px: number, py: number): boolean {
    return Math.hypot(s.center[0] - px, s.center[1] - py) < s.showRadius;
  }

  targets(px: number, py: number): SecretTarget[] {
    const out: SecretTarget[] = [];
    for (const s of SECRETS) {
      if (isSolved(this.save, s) || !this.near(s, px, py)) continue;
      for (const n of s.nodes) {
        const name = s.style === 'stones' ? (s.nodeNames?.[n.id] ?? n.label) : s.style === 'lamps' ? n.label : n.label;
        out.push({ id: targetId(s.id, n.id), x: n.x, y: n.y + 10, label: `${PREFIX[s.style]}: ${name}`, range: 74 });
      }
    }
    return out;
  }

  update(px: number, py: number): void {
    const now = this.scene.time.now;
    const g = this.g;
    let any = false;
    for (const s of SECRETS) {
      const solved = isSolved(this.save, s);
      const near = this.near(s, px, py);
      const len = progressOf(s.id).length;
      const was = this.prevLen.get(s.id) ?? 0;
      if (was > 0 && len === 0) this.flash.set(s.id, { until: now + 700, kind: solved || was === s.order.length - 1 ? 'good' : 'bad' });
      this.prevLen.set(s.id, len);
      if (!near) continue;
      if (!any) g.clear();
      any = true;
      const pressed = new Set(progressOf(s.id));
      const fl = this.flash.get(s.id);
      const flashing = !!fl && fl.until > now;
      const pulse = 0.5 + 0.5 * Math.sin(now / 400);
      for (const n of s.nodes) this.drawNode(s, n, solved, pressed.has(n.id) || (flashing && fl?.kind === 'good'), flashing && fl?.kind === 'bad', pulse);
      if (solved && s.hatch) this.drawHatch(s.hatch[0], s.hatch[1]);
    }
    if (!any && this.drewLast) g.clear();
    this.drewLast = any;
  }

  private drawNode(s: SecretDef, n: SecretNode, solved: boolean, lit: boolean, bad: boolean, pulse: number): void {
    const color = bad ? 0xff6b6b : toInt(n.color);
    const g = this.g;
    const idle = !solved && !lit;
    const y = s.style === 'stones' ? n.y - 96 : s.style === 'mushrooms' ? n.y : n.y;
    if (s.style === 'stones') {
      // a soft glow at the foot of the stone, the symbol above it
      g.fillStyle(color, solved ? 0.08 : lit ? 0.3 : 0.1 + pulse * 0.06).fillEllipse(n.x, n.y + 6, 70, 24);
    } else if (idle) {
      g.fillStyle(color, 0.08 + pulse * 0.06).fillEllipse(n.x, n.y + 6, 56, 18);
    }
    drawGlyph(g, n.glyph, n.x, y, color, lit, solved, n.size ?? 1, n.n ?? 1);
  }

  private drawHatch(x: number, y: number): void {
    const g = this.g;
    g.fillStyle(0xffd27a, 0.18).fillEllipse(x, y + 4, 120, 50);
    g.fillStyle(0x15121c, 1).fillRect(x - 34, y - 10, 68, 26);
    g.lineStyle(3, 0xffd27a, 0.9).strokeRect(x - 34, y - 10, 68, 26);
    g.fillStyle(0x4a3418, 1).fillRect(x - 30, y - 28, 60, 14);
    g.fillStyle(0xffd27a, 1).fillCircle(x, y + 3, 4);
  }

  destroy(): void {
    this.g.destroy();
  }
}
