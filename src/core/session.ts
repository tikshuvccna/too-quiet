/** Free-roaming session cap: warning near the end, then a story beat that sends the player to the next lesson. */
export type SessionPhase = 'free' | 'warning' | 'storm';

export interface SessionOptions {
  capSeconds?: number;
  warnAtSeconds?: number;
  onWarning?: () => void;
  onStorm?: () => void;
}

export const DEFAULT_CAP_SECONDS = 420;
export const DEFAULT_WARN_SECONDS = 360;

export class Session {
  private readonly baseCap: number;
  private readonly baseWarn: number;
  /** Extra seconds bought in the shop. */
  bonus = 0;
  get cap(): number { return this.baseCap + this.bonus; }
  get warnAt(): number { return this.baseWarn + this.bonus; }
  elapsed = 0;
  phase: SessionPhase = 'free';
  private paused = false;

  constructor(private readonly opts: SessionOptions = {}) {
    this.baseCap = opts.capSeconds ?? DEFAULT_CAP_SECONDS;
    this.baseWarn = Math.min(opts.warnAtSeconds ?? DEFAULT_WARN_SECONDS, this.baseCap - 1);
  }

  get remaining(): number {
    return Math.max(0, this.cap - this.elapsed);
  }

  get isPaused(): boolean {
    return this.paused;
  }

  pause(): void {
    this.paused = true;
  }

  resume(): void {
    this.paused = false;
  }

  /** Call every frame with the real delta in seconds. Time only counts while roaming. */
  tick(dt: number): void {
    if (this.paused || this.phase === 'storm') return;
    this.elapsed += dt;
    if (this.phase === 'free' && this.elapsed >= this.warnAt) {
      this.phase = 'warning';
      this.opts.onWarning?.();
    }
    if (this.phase === 'warning' && this.elapsed >= this.cap) {
      this.phase = 'storm';
      this.opts.onStorm?.();
    }
  }

  /** Start a fresh roaming session (after a lesson). */
  restart(): void {
    this.elapsed = 0;
    this.phase = 'free';
    this.paused = false;
  }
}
