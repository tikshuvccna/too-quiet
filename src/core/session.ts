/**
 * Free-roaming session cap. The valley gives the player a few minutes to roam, warns 2 minutes before the cap, and
 * then the cloud sends storms: a 10 second storm, a minute to reach the next lesson, a second storm, another minute,
 * and the third time the player is carried to the lesson's door. Reaching the lesson holds the clock (`safe`).
 */
export type SessionPhase = 'free' | 'warning' | 'storm' | 'grace' | 'teleport';

export interface SessionOptions {
  capSeconds?: number;
  /** Seconds of roaming after which the warning starts (default: 2 minutes before the cap). */
  warnAtSeconds?: number;
  stormSeconds?: number;
  graceSeconds?: number;
  /** How many storms before the player is carried to the lesson (the next trigger teleports). */
  maxStorms?: number;
  onWarning?: () => void;
  /** Called with 60 and 30 when that many seconds are left before the first storm. */
  onNotice?: (left: number) => void;
  onStorm?: (n: number) => void;
  onStormEnd?: () => void;
  onTeleport?: () => void;
}

export const DEFAULT_CAP_SECONDS = 420;
export const WARN_LEAD_SECONDS = 120;
export const NOTICES = [60, 30];

export class Session {
  private readonly baseCap: number;
  private readonly baseWarn: number;
  /** Extra seconds bought in the shop. */
  bonus = 0;
  get cap(): number { return this.baseCap + this.bonus; }
  get warnAt(): number { return Math.min(this.baseWarn + this.bonus, this.cap - 1); }
  elapsed = 0;
  phase: SessionPhase = 'free';
  /** The player stands at the lesson: nothing counts down and no storm runs. */
  safe = false;
  stormCount = 0;
  private stormLeft = 0;
  private graceLeft = 0;
  private paused = false;
  private noticed = new Set<number>();

  constructor(private readonly opts: SessionOptions = {}) {
    this.baseCap = opts.capSeconds ?? DEFAULT_CAP_SECONDS;
    this.baseWarn = Math.max(0, Math.min(opts.warnAtSeconds ?? this.baseCap - WARN_LEAD_SECONDS, this.baseCap - 1));
  }

  private get stormSeconds(): number { return this.opts.stormSeconds ?? 10; }
  private get graceSeconds(): number { return this.opts.graceSeconds ?? 60; }
  private get maxStorms(): number { return this.opts.maxStorms ?? 2; }

  /** Seconds until the next thing happens (the first storm, the next storm, or the teleport). */
  get remaining(): number {
    if (this.phase === 'free' || this.phase === 'warning') return Math.max(0, this.cap - this.elapsed);
    if (this.phase === 'grace') return Math.max(0, this.graceLeft);
    return 0;
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

  private startStorm(n: number): void {
    this.phase = 'storm';
    this.stormCount = n;
    this.stormLeft = this.stormSeconds;
    this.opts.onStorm?.(n);
  }

  /** Call every frame with the real delta in seconds. Time only counts while roaming. */
  tick(dt: number): void {
    if (this.paused || this.safe || this.phase === 'teleport') return;
    if (this.phase === 'free' || this.phase === 'warning') {
      this.elapsed += dt;
      if (this.phase === 'free' && this.elapsed >= this.warnAt) {
        this.phase = 'warning';
        this.opts.onWarning?.();
      }
      if (this.phase === 'warning') {
        for (const n of NOTICES) {
          if (this.cap - this.elapsed <= n && !this.noticed.has(n) && this.cap - this.elapsed > 0) {
            this.noticed.add(n);
            this.opts.onNotice?.(n);
          }
        }
        if (this.elapsed >= this.cap) this.startStorm(1);
      }
      return;
    }
    if (this.phase === 'storm') {
      this.stormLeft -= dt;
      if (this.stormLeft <= 0) {
        this.phase = 'grace';
        this.graceLeft = this.graceSeconds;
        this.opts.onStormEnd?.();
      }
      return;
    }
    this.graceLeft -= dt;
    if (this.graceLeft <= 0) {
      if (this.stormCount < this.maxStorms) this.startStorm(this.stormCount + 1);
      else {
        this.phase = 'teleport';
        this.opts.onTeleport?.();
      }
    }
  }

  /** Start a fresh roaming session (after a lesson or a teleport). */
  restart(): void {
    this.elapsed = 0;
    this.phase = 'free';
    this.paused = false;
    this.safe = false;
    this.stormCount = 0;
    this.stormLeft = 0;
    this.graceLeft = 0;
    this.noticed.clear();
  }
}
