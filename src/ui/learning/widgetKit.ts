import { el } from '../dom';

const SVG_NS = 'http://www.w3.org/2000/svg';

export function reducedMotion(): boolean {
  return typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches === true;
}

export function svg<K extends keyof SVGElementTagNameMap>(tag: K, attrs: Record<string, string | number> = {}, kids: (Node | null)[] = []): SVGElementTagNameMap[K] {
  const e = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, String(v));
  for (const k of kids) if (k) e.append(k);
  return e;
}

export function setPos(g: SVGElement, x: number, y: number): void {
  g.setAttribute('transform', `translate(${x.toFixed(2)} ${y.toFixed(2)})`);
}

export const lerp = (a: number, b: number, t: number): number => a + (b - a) * t;

/** Owns every animation frame a widget starts, so that cleanup stops them all. */
export class Runner {
  private alive = true;
  private frames = new Set<number>();

  /** Resolves when done. After dispose() it never resolves, so no code runs on a removed widget. */
  tween(ms: number, step: (p: number) => void): Promise<void> {
    const dur = reducedMotion() ? 1 : Math.max(1, ms);
    return new Promise((resolve) => {
      const t0 = performance.now();
      const tick = (now: number): void => {
        if (!this.alive) return;
        const p = Math.min(1, (now - t0) / dur);
        step(p);
        if (p >= 1) resolve();
        else this.frames.add(requestAnimationFrame(tick));
      };
      this.frames.add(requestAnimationFrame(tick));
    });
  }

  /** Per-frame loop until fn returns false. */
  loop(fn: (dt: number) => boolean): void {
    let last = performance.now();
    const tick = (now: number): void => {
      if (!this.alive) return;
      const dt = Math.min(0.1, (now - last) / 1000);
      last = now;
      if (fn(dt)) this.frames.add(requestAnimationFrame(tick));
    };
    this.frames.add(requestAnimationFrame(tick));
  }

  wait(ms: number): Promise<void> {
    return new Promise((resolve) => {
      const id = window.setTimeout(() => { if (this.alive) resolve(); }, reducedMotion() ? 0 : ms);
      this.timers.push(id);
    });
  }

  private timers: number[] = [];

  dispose(): void {
    this.alive = false;
    for (const f of this.frames) cancelAnimationFrame(f);
    for (const t of this.timers) clearTimeout(t);
    this.frames.clear();
  }

  get running(): boolean { return this.alive; }
}

/** A small envelope the messenger carries. Origin is its centre. */
export function envelope(failed = false): SVGGElement {
  return svg('g', { class: `lw-env${failed ? ' lw-env-x' : ''}` }, [
    svg('rect', { x: -5, y: -3.4, width: 10, height: 6.8, rx: 1.2 }),
    svg('polyline', { points: '-5,-3.4 0,0.6 5,-3.4', fill: 'none' }),
    failed ? svg('path', { d: 'M-2.4 -2.4L2.4 2.4M2.4 -2.4L-2.4 2.4', class: 'lw-x' }) : null,
  ]);
}

/** A row of goal chips that tick as the learner tries things. */
export function checklist(labels: string[]): { root: HTMLElement; tick(i: number): void; count(): number; all(): boolean } {
  const chips = labels.map((l) => el('span', 'lw-chip', l));
  const root = el('div', 'lw-chips', '', chips);
  return {
    root,
    tick: (i) => chips[i]?.classList.add('on'),
    count: () => chips.filter((c) => c.classList.contains('on')).length,
    all: () => chips.every((c) => c.classList.contains('on')),
  };
}

export function bannerEl(text: string): HTMLElement {
  return el('div', 'lw-banner', text);
}

/** Replace children of an element by text. */
export function say(target: HTMLElement, text: string, tone: '' | 'good' | 'warn' = ''): void {
  target.textContent = text;
  target.className = `${target.className.split(' ').filter((c) => !c.startsWith('tone-')).join(' ')}${tone ? ` tone-${tone}` : ''}`;
}

export function node(x: number, y: number): { left: string; top: string } {
  return { left: `${x * 100}%`, top: `${y * 100}%` };
}

export interface WidgetApi { done(): void }
export type Mount<S> = (host: HTMLElement, spec: S, api: WidgetApi) => () => void;

export function ringPositions(n: number, cx: number, cy: number, rx: number, ry: number): { x: number; y: number }[] {
  return Array.from({ length: n }, (_, k) => {
    const a = ((-90 + (360 / n) * k) * Math.PI) / 180;
    return { x: cx + rx * Math.cos(a), y: cy + ry * Math.sin(a) };
  });
}
