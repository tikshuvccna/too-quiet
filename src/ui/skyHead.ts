import { el, uiRoot } from './dom';

/** The Head: a vast face in the clouds, seen only while the truth shows through. Two frames (a slow blink). */
export class SkyHead {
  private readonly node = el('div', 'sky-head');
  private blinking = false;
  private timer: number;
  /** Fired once, the first time the Head is clearly visible. */
  onSeen: () => void = () => {};
  private seenFor = 0;
  private seen = false;

  constructor() {
    const url = `${import.meta.env.BASE_URL}assets/creatures/the_head.png`;
    Object.assign(this.node.style, { backgroundImage: `url(${url})`, backgroundSize: '200% 200%', backgroundPosition: '0% 100%' });
    uiRoot().prepend(this.node);
    this.timer = window.setInterval(() => {
      this.blinking = true;
      this.paint();
      window.setTimeout(() => {
        this.blinking = false;
        this.paint();
      }, 450);
    }, 7000);
  }

  private paint(): void {
    this.node.style.backgroundPosition = this.blinking ? '100% 100%' : '0% 100%';
  }

  /** v: how much of the truth is showing, 0..1. Called every frame by the world scene. */
  setTruth(v: number, dtSec: number): void {
    const o = Math.max(0, Math.min(0.62, (v - 0.35) * 1.15));
    this.node.style.opacity = String(o);
    if (o > 0.45 && !this.seen) {
      this.seenFor += dtSec;
      if (this.seenFor > 1.5) {
        this.seen = true;
        this.onSeen();
      }
    }
  }

  destroy(): void {
    window.clearInterval(this.timer);
    this.node.remove();
  }
}
