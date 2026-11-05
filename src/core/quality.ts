import type { SaveStore } from './save';

export type Quality = 'low' | 'medium' | 'high';
export type QualitySetting = 'auto' | Quality;
export const QUALITY_ORDER: readonly Quality[] = ['low', 'medium', 'high'];
export const QUALITY_NAME: Record<Quality, string> = { low: 'נמוכה', medium: 'בינונית', high: 'גבוהה' };

/** What each level turns on. Everything here is purely visual: gameplay is identical at every level. */
export interface Profile {
  /** Frame cap: 30 on weak phones halves the work and the battery use. */
  targetFps: number;
  /** Full-screen colour grading and vignette for the "truth" face. Off: the cold art variants still show. */
  postFx: boolean;
  /** Soft glows around the player and objects. */
  glow: boolean;
  clouds: number;
  rays: boolean;
  motes: number;
  /** Soft ground shadows under trees and props. */
  shadows: boolean;
  smoke: boolean;
}

export const PROFILES: Record<Quality, Profile> = {
  low: { targetFps: 30, postFx: false, glow: false, clouds: 2, rays: false, motes: 6, shadows: false, smoke: false },
  medium: { targetFps: 60, postFx: true, glow: false, clouds: 4, rays: true, motes: 20, shadows: true, smoke: true },
  high: { targetFps: 60, postFx: true, glow: true, clouds: 7, rays: true, motes: 46, shadows: true, smoke: true },
};

interface NavigatorHints { deviceMemory?: number; hardwareConcurrency?: number; userAgent: string }

/** A guess from what the browser tells us. Weak phones and school Chromebooks land lower; the FPS watcher corrects it. */
export function detectQuality(nav: NavigatorHints = navigator as unknown as NavigatorHints, coarsePointer = typeof matchMedia !== 'undefined' && matchMedia('(pointer: coarse)').matches, dpr = typeof devicePixelRatio === 'number' ? devicePixelRatio : 1): Quality {
  const mem = nav.deviceMemory ?? 4;
  const cores = nav.hardwareConcurrency ?? 4;
  let score = 0;
  score += mem >= 8 ? 2 : mem >= 4 ? 1 : mem <= 2 ? -2 : 0;
  score += cores >= 8 ? 2 : cores >= 4 ? 1 : cores <= 2 ? -2 : 0;
  if (coarsePointer) score -= 1;
  if (/CrOS/.test(nav.userAgent)) score -= 1;
  if (dpr >= 3) score -= 1;
  return score >= 3 ? 'high' : score >= 0 ? 'medium' : 'low';
}

type Listener = () => void;

/**
 * The quality the game runs at. The setting is "auto" (recommended, from the device) or a fixed level.
 * In auto mode, a few seconds of low frame rate step the level down by one; a fixed level is never changed.
 */
export class QualityManager {
  private recommended: Quality;
  private current: Quality;
  private slow = 0;
  private listeners: Listener[] = [];
  /** Called when the level was lowered automatically (to tell the player). */
  onAutoLowered: (to: Quality) => void = () => {};

  constructor(private readonly save: SaveStore, recommended: Quality = detectQuality()) {
    this.recommended = recommended;
    this.current = this.resolve();
  }

  private resolve(): Quality {
    const s = this.save.data.settings.quality;
    return s === 'auto' ? this.recommended : s;
  }

  get setting(): QualitySetting {
    return this.save.data.settings.quality;
  }

  get level(): Quality {
    return this.current;
  }

  get profile(): Profile {
    return PROFILES[this.current];
  }

  get recommendedLevel(): Quality {
    return this.recommended;
  }

  set(setting: QualitySetting): void {
    this.save.data.settings.quality = setting;
    this.save.save();
    this.slow = 0;
    this.current = this.resolve();
    this.listeners.forEach((l) => l());
  }

  onChange(cb: Listener): () => void {
    this.listeners.push(cb);
    return () => { this.listeners = this.listeners.filter((l) => l !== cb); };
  }

  /** Feed the measured frames per second about once a second while the world is running. */
  sample(fps: number): void {
    if (this.setting !== 'auto') return;
    const floor = this.current === 'high' ? 40 : 24;
    this.slow = fps > 0 && fps < floor ? this.slow + 1 : 0;
    if (this.slow >= 6 && this.current !== 'low') {
      const lower = QUALITY_ORDER[QUALITY_ORDER.indexOf(this.current) - 1] as Quality;
      this.recommended = lower;
      this.current = lower;
      this.slow = 0;
      this.listeners.forEach((l) => l());
      this.onAutoLowered(lower);
    }
  }
}
