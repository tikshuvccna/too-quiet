import { el } from './dom';

/** A tiny frames-per-second badge, shown only when switched on in the settings. */
export class FpsMeter {
  private readonly node = el('div', 'pill fps-badge');

  /** The badge lives in the HUD row, so it can never cover another control. */
  constructor(parent: HTMLElement) {
    this.node.style.display = 'none';
    parent.append(this.node);
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
