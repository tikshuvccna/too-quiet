export const SAVE_KEY = 'too-quiet.save.v1';
export const SAVE_VERSION = 1;

import type { QualitySetting } from './quality';

export type Look = 'girl' | 'boy';

export interface LessonProgress {
  done: boolean;
  checks: Record<string, boolean>;
  quizBest: number;
  quizPassed: boolean;
  games: Record<string, { points: number; passed: boolean }>;
}

export interface SaveData {
  v: number;
  started: boolean;
  look: Look;
  name: string;
  flags: Record<string, boolean>;
  collected: Record<string, boolean>;
  evidence: Record<string, 'natural' | 'hand'>;
  fixed: Record<string, boolean>;
  lessons: Record<string, LessonProgress>;
  power: number;
  coins: number;
  /** Stackable items such as creature food. */
  inv: Record<string, number>;
  playSeconds: number;
  settings: { subtitles: boolean; sound: boolean; quality: QualitySetting; showFps: boolean };
}

export function emptySave(): SaveData {
  return {
    v: SAVE_VERSION, started: false, look: 'girl', name: '', flags: {}, collected: {}, evidence: {}, fixed: {},
    lessons: {}, power: 0, coins: 0, inv: {}, playSeconds: 0, settings: { subtitles: true, sound: false, quality: 'auto', showFps: false },
  };
}

export function emptyLesson(): LessonProgress {
  return { done: false, checks: {}, quizBest: 0, quizPassed: false, games: {} };
}

interface StoreLike {
  getItem(k: string): string | null;
  setItem(k: string, v: string): void;
  removeItem(k: string): void;
}

/** Merge unknown stored data over the defaults so older saves keep working when fields are added. */
export function normalize(raw: unknown): SaveData {
  const base = emptySave();
  if (!raw || typeof raw !== 'object') return base;
  const r = raw as Partial<SaveData>;
  return {
    ...base,
    ...r,
    v: SAVE_VERSION,
    settings: { ...base.settings, ...(r.settings ?? {}) },
    flags: { ...(r.flags ?? {}) },
    collected: { ...(r.collected ?? {}) },
    evidence: { ...(r.evidence ?? {}) },
    fixed: { ...(r.fixed ?? {}) },
    lessons: { ...(r.lessons ?? {}) },
  };
}

export class SaveStore {
  data: SaveData = emptySave();

  constructor(private readonly store: StoreLike | null = safeLocalStorage()) {}

  load(): SaveData {
    try {
      const j = this.store?.getItem(SAVE_KEY);
      this.data = j ? normalize(JSON.parse(j)) : emptySave();
    } catch {
      this.data = emptySave();
    }
    return this.data;
  }

  save(): void {
    try {
      this.store?.setItem(SAVE_KEY, JSON.stringify(this.data));
    } catch {
      /* private mode or full storage: the game still runs, progress is just not kept */
    }
  }

  reset(): void {
    try {
      this.store?.removeItem(SAVE_KEY);
    } catch {
      /* ignore */
    }
    this.data = emptySave();
  }

  lesson(id: string): LessonProgress {
    return (this.data.lessons[id] ??= emptyLesson());
  }

  setFlag(name: string): void {
    this.data.flags[name] = true;
    this.save();
  }

  hasFlag(name: string): boolean {
    return !!this.data.flags[name];
  }

  /** Power grows with each completed lesson: it decides which faults the needle can mend. */
  recomputePower(): number {
    this.data.power = Object.values(this.data.lessons).filter((l) => l.done).length;
    return this.data.power;
  }
}

function safeLocalStorage(): StoreLike | null {
  try {
    return typeof localStorage === 'undefined' ? null : localStorage;
  } catch {
    return null;
  }
}
