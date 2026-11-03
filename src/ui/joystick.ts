import { el, isTouchDevice, uiRoot } from './dom';

/** Virtual joystick for touch screens. `vector` is read by the world scene every frame. */
export class Joystick {
  vector = { x: 0, y: 0 };
  private readonly root = el('div', 'joy');
  private readonly knob = el('i');
  private pointer: number | null = null;
  private readonly radius = 55;

  constructor() {
    this.root.append(this.knob);
    uiRoot().append(this.root);
    if (isTouchDevice()) this.root.classList.add('show');
    this.root.addEventListener('pointerdown', (e) => this.start(e));
    this.root.addEventListener('pointermove', (e) => this.move(e));
    for (const t of ['pointerup', 'pointercancel'] as const) this.root.addEventListener(t, (e) => this.end(e));
  }

  setVisible(v: boolean): void {
    this.root.style.visibility = v ? 'visible' : 'hidden';
    if (!v) this.reset();
  }

  private start(e: PointerEvent): void {
    this.pointer = e.pointerId;
    this.root.setPointerCapture(e.pointerId);
    this.move(e);
  }

  private move(e: PointerEvent): void {
    if (e.pointerId !== this.pointer) return;
    const r = this.root.getBoundingClientRect();
    let dx = e.clientX - (r.left + r.width / 2);
    let dy = e.clientY - (r.top + r.height / 2);
    const len = Math.hypot(dx, dy);
    if (len > this.radius) {
      dx = (dx / len) * this.radius;
      dy = (dy / len) * this.radius;
    }
    this.knob.style.transform = `translate(${dx}px, ${dy}px)`;
    const k = Math.hypot(dx, dy) / this.radius;
    this.vector = k < 0.18 ? { x: 0, y: 0 } : { x: dx / this.radius, y: dy / this.radius };
  }

  private end(e: PointerEvent): void {
    if (e.pointerId === this.pointer) this.reset();
  }

  private reset(): void {
    this.pointer = null;
    this.vector = { x: 0, y: 0 };
    this.knob.style.transform = '';
  }
}
