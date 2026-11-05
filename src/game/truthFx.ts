import Phaser from 'phaser';

/** How much of the "truth" the needle can show, by the number of lessons learned. */
export function truthLevel(power: number): number {
  if (power <= 0) return 0.3; // before the first lesson the needle only hints
  return Math.min(1, 0.8 + 0.1 * (power - 1));
}

/**
 * The valley has two faces. TruthFx grades the whole camera from the cheerful facade (0) to the cold,
 * dim truth (1): desaturated, darker, vignetted, with a nervous flicker when it changes.
 */
export class TruthFx {
  value = 0;
  private target = 0;
  private flashLeft = 0;
  private flickerClock = 0;
  /** Low quality turns the full-screen colour grading off. */
  enabled = true;
  private readonly cm: Phaser.FX.ColorMatrix | null;
  private readonly vig: Phaser.FX.Vignette | null;

  constructor(cam: Phaser.Cameras.Scene2D.Camera) {
    const fx = cam.postFX;
    fx?.clear();
    this.cm = fx ? fx.addColorMatrix() : null;
    this.vig = fx ? fx.addVignette(0.5, 0.5, 1, 0.2) : null;
    this.apply(0);
  }

  set(target: number): void {
    this.target = target;
  }

  /** A short involuntary glimpse of the truth (used when someone says "everything is fine"). */
  flash(ms: number): void {
    this.flashLeft = ms / 1000;
  }

  get active(): boolean {
    return this.value > 0.04;
  }

  update(dtMs: number): void {
    const dt = dtMs / 1000;
    let goal = this.target;
    if (this.flashLeft > 0) {
      this.flashLeft -= dt;
      this.flickerClock += dt;
      // flicker: the truth shows through in uneven pulses
      const on = Math.sin(this.flickerClock * 40) > -0.15 && this.flashLeft > 0.08;
      goal = Math.max(goal, on ? 0.95 : 0.15);
      this.value += (goal - this.value) * Math.min(1, dt * 30);
    } else {
      this.value += (goal - this.value) * Math.min(1, dt * 4);
    }
    this.apply(this.value);
  }

  private apply(v: number): void {
    if (!this.cm || !this.vig) return;
    if (!this.enabled) {
      this.cm.active = false;
      this.vig.active = false;
      return;
    }
    // the facade needs no post-processing at all: skip two full-screen passes (matters on phones)
    const active = v > 0.01;
    this.cm.active = active;
    this.vig.active = active;
    const m = this.cm;
    m.reset();
    if (v > 0.01) {
      m.saturate(-0.72 * v, true);
      m.brightness(1 - 0.38 * v, true);
      m.hue(-18 * v, true);
    }
    this.vig.radius = 1 - 0.48 * v;
    this.vig.strength = 0.12 + 0.5 * v;
  }
}
