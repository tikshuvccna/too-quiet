/** Dialogue portraits: 512px busts with expressions, loaded lazily one character at a time. */
export interface PortraitSheet {
  w: number;
  h: number;
  frames: Record<string, { x: number; y: number; w: number; h: number }>;
}

/** Atlas JSON nests each rectangle under `frame`; the UI only needs the rectangle. */
export function flatten(frames: Record<string, { frame: { x: number; y: number; w: number; h: number } }>): PortraitSheet['frames'] {
  return Object.fromEntries(Object.entries(frames).map(([k, v]) => [k, v.frame]));
}

const BASE = (): string => `${import.meta.env.BASE_URL}assets/portraits/`;
const sheets = new Map<string, Promise<PortraitSheet | null>>();

export function loadPortrait(name: string): Promise<PortraitSheet | null> {
  let p = sheets.get(name);
  if (!p) {
    p = fetch(`${BASE()}${name}.json`)
      .then((r) => (r.ok ? r.json() : null))
      .then((j: { frames: Record<string, { frame: { x: number; y: number; w: number; h: number } }>; meta: { size: { w: number; h: number } } } | null) =>
        j ? { w: j.meta.size.w, h: j.meta.size.h, frames: flatten(j.frames) } : null)
      .catch(() => null);
    sheets.set(name, p);
  }
  return p;
}

/** Which portrait sheet speaks for a line's speaker (null: no portrait, e.g. the narrator). */
export function portraitFor(speaker: string, look: 'girl' | 'boy'): string | null {
  switch (speaker) {
    case 'dvora': return 'dvora';
    case 'grandma': return 'shoshana';
    case 'clinicDoctor': return 'miriam';
    case 'baker': return 'hillel';
    case 'miller': return 'miller';
    case 'child': return 'asaf';
    case 'hubGrandpa': return 'hed';
    case 'player': return look === 'girl' ? 'apprentice_girl' : 'apprentice_boy';
    default: return null;
  }
}

const MOOD_BY_SPEAKER: Record<string, string> = { baker: 'worried', grandma: 'happy', hubGrandpa: 'happy', clinicDoctor: 'neutral' };

/** A simple, deterministic mood for a line (voice acting will refine this later). */
export function moodFor(speaker: string, text: string): string {
  const base = MOOD_BY_SPEAKER[speaker] ?? 'neutral';
  if (speaker === 'player') return text.includes('?') ? 'surprised' : 'neutral';
  if (speaker === 'child' && text.includes('?')) return 'surprised';
  if (speaker === 'dvora') return text.includes('?') ? 'surprised' : 'neutral';
  return base;
}

export function frameStyle(sheet: PortraitSheet, name: string, frame: string, size: number): { backgroundImage: string; backgroundSize: string; backgroundPosition: string } | null {
  const f = sheet.frames[`${name}_${frame}`];
  if (!f) return null;
  const k = size / f.w;
  return {
    backgroundImage: `url(${BASE()}${name}.png)`,
    backgroundSize: `${sheet.w * k}px ${sheet.h * k}px`,
    backgroundPosition: `-${f.x * k}px -${f.y * k}px`,
  };
}
