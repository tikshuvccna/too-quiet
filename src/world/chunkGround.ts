import Phaser from 'phaser';
import { REGIONS, SEA, STREAM } from './regions';
import { WORLD } from './layout';
import { drawRoads } from './roads';

const CHUNK = 1024;

/**
 * The ground is baked into 1024 px render textures that exist only near the camera.
 * A 6200x4000 world would otherwise need one huge texture or thousands of draw commands every frame.
 */
export class ChunkGround {
  private readonly chunks = new Map<string, Phaser.GameObjects.RenderTexture>();
  private readonly roadG: Phaser.GameObjects.Graphics;
  private readonly scratch: Phaser.GameObjects.Graphics;

  constructor(private readonly scene: Phaser.Scene) {
    // never added to the display list: only used as a stamp
    this.roadG = scene.make.graphics({}, false);
    this.scratch = scene.make.graphics({}, false);
    this.paintStatic(this.roadG);
  }

  /** Water, shore, roads and the plaza in world coordinates. */
  private paintStatic(g: Phaser.GameObjects.Graphics): void {
    const poly = (pts: Array<[number, number]>, col: number, a = 1): void => {
      g.fillStyle(col, a);
      g.beginPath();
      pts.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y)));
      g.closePath();
      g.fillPath();
    };
    const stroke = (pts: Array<[number, number]>, w: number, col: number): void => {
      g.lineStyle(w, col, 1);
      const sp = new Phaser.Curves.Spline(pts.map(([x, y]) => new Phaser.Math.Vector2(x, y)));
      const dense = sp.getSpacedPoints(Math.ceil(sp.getLength() / 24));
      g.beginPath();
      dense.forEach((p, i) => (i ? g.lineTo(p.x, p.y) : g.moveTo(p.x, p.y)));
      g.strokePath();
    };
    // sea with a sandy shore
    const shore = SEA.map(([x, y]) => [x, y - 46] as [number, number]);
    poly([...shore.slice(0, -2), [6200, 4000], [1700, 4000]].map((p) => p as [number, number]), 0xe9d9a4);
    poly(SEA, 0x2a6f93);
    g.lineStyle(6, 0xbfe6f2, 0.6);
    g.beginPath();
    SEA.slice(0, -2).forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y)));
    g.strokePath();
    stroke(STREAM, 84, 0x2c5a72);
    stroke(STREAM, 66, 0x3f86a6);
    stroke(STREAM, 22, 0x7fc4de);
    drawRoads(g);
    // wooden bridge over the stream on the south-east road
    const ang = Math.atan2(1382 - 1292, 2060 - 1968);
    g.save();
    g.translateCanvas(1968, 1292);
    g.rotateCanvas(ang);
    g.fillStyle(0x3a2a1a, 1);
    g.fillRect(-75, -35, 150, 70);
    g.fillStyle(0x8a6a46, 1);
    g.fillRect(-70, -30, 140, 60);
    g.fillStyle(0x4a331f, 1);
    for (let i = -6; i <= 6; i++) g.fillRect(i * 10 - 1.5, -29, 3, 58);
    g.restore();
  }

  private key(cx: number, cy: number): string {
    return `${cx},${cy}`;
  }

  private build(cx: number, cy: number): void {
    const ox = cx * CHUNK;
    const oy = cy * CHUNK;
    const rt = this.scene.add.renderTexture(ox, oy, CHUNK, CHUNK).setOrigin(0).setDepth(-1000);
    for (let y = 0; y < CHUNK; y += 128) for (let x = 0; x < CHUNK; x += 128) rt.draw('grass', x, y);
    // soft-edged colour wash per region
    for (const r of REGIONS) {
      if (r.tintAlpha <= 0) continue;
      const [rx, ry, rw, rh] = r.rect;
      const steps = 16;
      for (let k = 0; k <= steps; k++) {
        const inf = k * 20 - 160; // from 160 px inside the region to 160 px outside: the colour ramps up smoothly
        const x0 = rx - inf - ox;
        const y0 = ry - inf - oy;
        if (x0 > CHUNK || y0 > CHUNK || x0 + rw + 2 * inf < 0 || y0 + rh + 2 * inf < 0 || rw + 2 * inf <= 0 || rh + 2 * inf <= 0) continue;
        rt.fill(r.tint, (r.tintAlpha * 1.6) / steps, x0, y0, rw + 2 * inf, rh + 2 * inf);
      }
    }
    // roads, water and the plaza
    rt.draw(this.roadG, -ox, -oy);
    // flowers and tufts, deterministic per chunk
    let s = 11 + cx * 977 + cy * 131;
    const rnd = (): number => ((s = (s * 16807) % 2147483647) / 2147483647);
    const g = this.scratch;
    g.clear();
    for (let i = 0; i < 160; i++) {
      g.fillStyle([0xffe9a8, 0xffb3c6, 0xd6c8ff, 0xffffff][Math.floor(rnd() * 4)] as number, 0.85);
      g.fillCircle(rnd() * CHUNK, rnd() * CHUNK, 2 + rnd() * 2);
    }
    rt.draw(g, 0, 0);
    this.chunks.set(this.key(cx, cy), rt);
  }

  /** Create chunks near the view (at most `budget` per call), drop far ones. Pass a big budget at start-up. */
  update(view: Phaser.Geom.Rectangle, budget = 1): void {
    const margin = 260;
    const x0 = Math.max(0, Math.floor((view.x - margin) / CHUNK));
    const y0 = Math.max(0, Math.floor((view.y - margin) / CHUNK));
    const x1 = Math.min(Math.ceil(WORLD.w / CHUNK) - 1, Math.floor((view.right + margin) / CHUNK));
    const y1 = Math.min(Math.ceil(WORLD.h / CHUNK) - 1, Math.floor((view.bottom + margin) / CHUNK));
    let made = 0;
    for (let cy = y0; cy <= y1 && made < budget; cy++) {
      for (let cx = x0; cx <= x1 && made < budget; cx++) {
        if (!this.chunks.has(this.key(cx, cy))) {
          this.build(cx, cy);
          made++;
        }
      }
    }
    for (const [k, rt] of this.chunks) {
      const [cx, cy] = k.split(',').map(Number) as [number, number];
      if (cx < x0 - 1 || cx > x1 + 1 || cy < y0 - 1 || cy > y1 + 1) {
        rt.destroy();
        this.chunks.delete(k);
      }
    }
  }

  destroy(): void {
    this.chunks.forEach((rt) => rt.destroy());
    this.chunks.clear();
    this.roadG.destroy();
    this.scratch.destroy();
  }
}
