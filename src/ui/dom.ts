export function el<K extends keyof HTMLElementTagNameMap>(
  tag: K, cls = '', text = '', kids: (Node | null | false)[] = [],
): HTMLElementTagNameMap[K] {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text) e.textContent = text;
  for (const k of kids) if (k) e.append(k);
  return e;
}

export const uiRoot = (): HTMLElement => document.getElementById('ui') as HTMLElement;

export function isTouchDevice(): boolean {
  return window.matchMedia('(pointer: coarse)').matches || 'ontouchstart' in window;
}

export function mmss(sec: number): string {
  const s = Math.max(0, Math.ceil(sec));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
}
