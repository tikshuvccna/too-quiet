import type Phaser from 'phaser';

const CELL = 320;

/** Hides static objects that are far from the camera, so thousands of trees cost nothing. */
export class Culler {
  private readonly cells = new Map<string, Phaser.GameObjects.GameObject[]>();
  private active = new Set<string>();
  private clock = 0;
  private shadows = true;
  private readonly shadowObjs = new Set<Phaser.GameObjects.GameObject>();

  /** Soft ground shadows can be switched off on weak devices. */
  setShadows(on: boolean): void {
    this.shadows = on;
    this.active = new Set();
  }

  add(obj: Phaser.GameObjects.Image, x: number, y: number, shadow = false): void {
    if (shadow) this.shadowObjs.add(obj);
    const k = `${Math.floor(x / CELL)},${Math.floor(y / CELL)}`;
    const list = this.cells.get(k);
    if (list) list.push(obj);
    else this.cells.set(k, [obj]);
    obj.setVisible(false);
  }

  /** Call every frame; refreshes a few times per second. `force` for the first call. */
  update(dtMs: number, view: Phaser.Geom.Rectangle, force = false): void {
    this.clock += dtMs;
    if (!force && this.clock < 180) return;
    this.clock = 0;
    const m = 240;
    const x0 = Math.floor((view.x - m) / CELL);
    const x1 = Math.floor((view.right + m) / CELL);
    const y0 = Math.floor((view.y - m) / CELL);
    const y1 = Math.floor((view.bottom + m + 200) / CELL);
    const next = new Set<string>();
    for (let cy = y0; cy <= y1; cy++) for (let cx = x0; cx <= x1; cx++) next.add(`${cx},${cy}`);
    for (const k of this.active) if (!next.has(k)) this.set(k, false);
    for (const k of next) if (!this.active.has(k)) this.set(k, true);
    this.active = next;
  }

  private set(k: string, on: boolean): void {
    const list = this.cells.get(k);
    if (!list) return;
    for (const o of list) (o as Phaser.GameObjects.Image).setVisible(on && (this.shadows || !this.shadowObjs.has(o)));
  }
}
