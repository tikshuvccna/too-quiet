import { el } from '../dom';

export interface Stage {
  canvas: HTMLCanvasElement;
  c: CanvasRenderingContext2D;
  /** CSS pixel size, updated on resize. */
  size: { w: number; h: number };
  /** Starts the frame loop; the callback gets seconds since the last frame (clamped). */
  loop(step: (dt: number, t: number) => void): void;
  destroy(): void;
}

/** A canvas filling the host, scaled for the screen density, with a frame loop and clean teardown. */
export function makeStage(host: HTMLElement, aspectHeight = 'min(68vh, 560px)'): Stage {
  const wrap = el('div', 'npcg-canvas-wrap');
  wrap.style.height = aspectHeight;
  const canvas = el('canvas', 'npcg-canvas');
  wrap.append(canvas);
  host.append(wrap);
  const c = canvas.getContext('2d') as CanvasRenderingContext2D;
  const size = { w: 0, h: 0 };
  const dpr = Math.min(2, window.devicePixelRatio || 1);
  const fit = (): void => {
    size.w = wrap.clientWidth;
    size.h = wrap.clientHeight;
    canvas.width = Math.round(size.w * dpr);
    canvas.height = Math.round(size.h * dpr);
    c.setTransform(dpr, 0, 0, dpr, 0, 0);
  };
  fit();
  const ro = new ResizeObserver(fit);
  ro.observe(wrap);
  let raf = 0;
  let alive = true;
  return {
    canvas, c, size,
    loop(step) {
      let prev = performance.now();
      let t = 0;
      const frame = (now: number): void => {
        if (!alive) return;
        raf = requestAnimationFrame(frame);
        const dt = Math.min(0.1, (now - prev) / 1000);
        prev = now;
        t += dt;
        c.setTransform(dpr, 0, 0, dpr, 0, 0);
        step(dt, t);
      };
      raf = requestAnimationFrame(frame);
    },
    destroy() {
      alive = false;
      cancelAnimationFrame(raf);
      ro.disconnect();
      wrap.remove();
    },
  };
}

/** Deterministic random numbers: the same level always plays the same way. */
export function seeded(seed: number): () => number {
  let s = seed >>> 0 || 1;
  return () => {
    s = (Math.imul(s, 1664525) + 1013904223) >>> 0;
    return s / 4294967296;
  };
}
