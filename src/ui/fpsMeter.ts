import { el, uiRoot } from './dom';

/** A tiny frames-per-second badge, shown only when switched on in the settings. */
export class FpsMeter {
  private readonly node = el('div', 'fps-badge');

  constructor() {
    this.node.style.display = 'none';
    uiRoot().append(this.node);
  }

  show(on: boolean): void {
    this.node.style.display = on ? '' : 'none';
  }

  set(fps: number, level: string): void {
    if (this.node.style.display === 'none') return;
    this.node.textContent = `${Math.round(fps)} FPS · ${level}`;
    this.node.classList.toggle('bad', fps < 24);
  }
}
