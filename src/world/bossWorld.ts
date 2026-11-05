import Phaser from 'phaser';
import { el, uiRoot } from '../ui/dom';
import { DAMAGE, MAX_HP, PHASES, PHASE_SEQUENCE, PHASE_TOPIC, difficulty, phaseOf, type FaultType } from '../ui/learning/bossLogic';
import type { GameContext } from '../game/context';

/** Knots of the thread-web the Head attacks, in village coordinates (they hang over the roofs, like the thread-sight threads). */
const KNOTS: Record<string, [number, number]> = {
  a: [760, 760], b: [1280, 600], c: [1780, 740], d: [2180, 430], e: [560, 1230], f: [1250, 1230], g: [2140, 1290], h: [1280, 1010],
};
const THREADS: Array<[string, string]> = [
  ['a', 'b'], ['b', 'c'], ['c', 'd'], ['a', 'e'], ['e', 'f'], ['f', 'g'], ['b', 'h'], ['h', 'f'], ['c', 'g'], ['a', 'h'], ['h', 'c'],
];
const SPOT_T = [0.3, 0.5, 0.7];

interface Fault { id: string; type: FaultType; phase: number; thread: number; t: number; x: number; y: number; progress: number; mark: Phaser.GameObjects.Text | null }
interface Stream { x0: number; y0: number; dx: number; dy: number; telegraph: number; travelled: number; bits: number }
interface Shot { x0: number; y0: number; x1: number; y1: number; travelled: number; len: number; dmg: number; count: number }

export interface BossOptions {
  ctx: GameContext;
  /** True when a spot of the village can be stood on. */
  isFree(x: number, y: number): boolean;
  onEnd(r: { won: boolean }): void;
}

/**
 * The fight with the Head, in the village itself. The Head floats over the roofs and cuts the threads of the web
 * (seen with the needle's thread-sight), sends streams of bits at the apprentice, and every thread the apprentice mends
 * (by standing on the cut, or by solving a task from the lessons) sends bits back that take strength from it.
 */
export class BossWorld {
  private readonly scene: Phaser.Scene;
  private readonly g: Phaser.GameObjects.Graphics;
  private readonly head: Phaser.GameObjects.Sprite;
  private readonly hud: HTMLElement;
  private readonly heartsEl: HTMLElement;
  private readonly calmFill: HTMLElement;
  private readonly labelEl: HTMLElement;
  private readonly faults = new Map<string, Fault>();
  private streams: Stream[] = [];
  private shots: Shot[] = [];
  private lives = 5;
  private hp = MAX_HP;
  private phase = 0;
  private faultsDone = 0;
  private seq = 0;
  private time = 0;
  private spawnClock = 3;
  private streamClock = 4;
  private invuln = 0;
  private banner = 0;
  private countdown = 2.2;
  private ended = false;
  private taskOpen = false;
  private nextId = 1;
  private panel: HTMLElement | null = null;
  private hx = 1280;
  private hy = 360;

  constructor(scene: Phaser.Scene, private readonly o: BossOptions) {
    this.scene = scene;
    this.g = scene.add.graphics().setDepth(4520);
    this.head = scene.add.sprite(this.hx, this.hy, 'the_head', 'the_head_truth_0').setDepth(4400).setScale(0.55).setAlpha(0.95);
    if (scene.anims.exists('the_head:truth')) this.head.play('the_head:truth');
    this.heartsEl = el('div', 'bosshud-hearts');
    this.calmFill = el('i', 'boss-calm-fill');
    this.labelEl = el('div', 'bosshud-label');
    this.hud = el('div', 'bosshud', '', [this.labelEl, el('div', 'boss-calm', '', [this.calmFill]), this.heartsEl]);
    uiRoot().append(this.hud);
    document.body.classList.add('boss');
    o.ctx.session.pause();
    this.paint();
  }

  // ---- public ----
  get active(): boolean {
    return !this.ended;
  }

  targets(): Array<{ id: string; x: number; y: number; label: string; range: number }> {
    const out: Array<{ id: string; x: number; y: number; label: string; range: number }> = [];
    for (const f of this.faults.values()) {
      if (f.type === 'choice') out.push({ id: `bossfault:${f.id}`, x: f.x, y: f.y, label: 'לתקן את החוט: פותרים משימה', range: 100 });
    }
    return out;
  }

  use(id: string): void {
    const f = this.faults.get(id.replace('bossfault:', ''));
    if (f && f.type === 'choice' && !this.taskOpen) void this.openTask(f);
  }

  update(dtMs: number, px: number, py: number): void {
    const dt = Math.min(dtMs, 50) / 1000;
    this.time += dt;
    if (this.invuln > 0) this.invuln -= dt;
    if (this.banner > 0) this.banner -= dt;
    if (this.ended) { this.draw(px, py); return; }
    if (this.countdown > 0) {
      this.countdown -= dt;
      this.moveHead(dt, null);
      this.draw(px, py);
      return;
    }
    if (this.taskOpen) { this.draw(px, py); return; }
    const d = difficulty(this.phase);

    // the Head cuts threads
    this.spawnClock -= dt;
    if (this.spawnClock <= 0 && this.faults.size < d.maxFaults && this.faultsDone < PHASE_SEQUENCE.length) {
      this.spawnFault(px, py);
      this.spawnClock = d.faultEvery;
    }
    // streams of bits aimed where the apprentice stands
    this.streamClock -= dt;
    if (this.streamClock <= 0) {
      this.streamClock = d.streamEvery;
      const dx = px - this.hx;
      const dy = py - 22 - (this.hy + 60);
      const len = Math.hypot(dx, dy) || 1;
      this.streams.push({ x0: this.hx, y0: this.hy + 60, dx: dx / len, dy: dy / len, telegraph: 1.2, travelled: 0, bits: d.bits });
    }
    for (const s of this.streams) {
      if (s.telegraph > 0) { s.telegraph -= dt; continue; }
      s.travelled += (360 + this.phase * 70) * dt * 1.2;
      for (let i = 0; i < s.bits; i++) {
        const dist = s.travelled - i * 54;
        if (dist < 0) continue;
        const bx = s.x0 + s.dx * dist;
        const by = s.y0 + s.dy * dist;
        if (Math.hypot(bx - px, by - (py - 22)) < 26) this.hurt(px, py);
      }
    }
    this.streams = this.streams.filter((s) => s.telegraph > 0 || s.travelled - s.bits * 54 < 1900);

    // mending a plain cut: stand on it
    for (const f of this.faults.values()) {
      if (f.type !== 'simple') continue;
      if (Math.hypot(f.x - px, f.y - py) < 70) {
        f.progress += dt / 1.3;
        if (f.progress >= 1) this.mend(f);
      } else f.progress = Math.max(0, f.progress - dt * 0.6);
    }

    // our bits flying up to the Head
    for (const s of this.shots) s.travelled += 640 * dt;
    for (const s of this.shots.filter((x) => x.travelled >= x.len)) this.land(s);
    this.shots = this.shots.filter((x) => x.travelled < x.len);

    this.moveHead(dt, this.oldestFault());
    this.draw(px, py);
  }

  destroy(): void {
    this.panel?.remove();
    this.hud.remove();
    document.body.classList.remove('boss');
    this.g.destroy();
    this.head.destroy();
    for (const f of this.faults.values()) f.mark?.destroy();
    this.faults.clear();
    this.o.ctx.session.resume();
  }

  // ---- fight ----
  private paint(): void {
    this.heartsEl.replaceChildren(...Array.from({ length: 5 }, (_, i) => el('span', `lrn-heart${i < this.lives ? '' : ' lost'}`, '♥')));
    this.calmFill.style.width = `${((MAX_HP - this.hp) / MAX_HP) * 100}%`;
    this.labelEl.textContent = `הראש · שלב ${this.phase + 1} מתוך ${PHASES}: ${PHASE_TOPIC[this.phase] ?? ''}`;
  }

  private oldestFault(): Fault | null {
    let best: Fault | null = null;
    for (const f of this.faults.values()) if (!best || f.progress < best.progress) best = f;
    return best;
  }

  private moveHead(dt: number, over: Fault | null): void {
    const tx = over ? over.x : 1280 + Math.cos(this.time * 0.35) * 520;
    const ty = (over ? over.y : 560 + Math.sin(this.time * 0.5) * 80) - 330;
    this.hx += (tx - this.hx) * Math.min(1, dt * 1.4);
    this.hy += (ty - this.hy) * Math.min(1, dt * 1.4);
    this.head.setPosition(this.hx, this.hy + Math.sin(this.time * 1.6) * 8);
    const calm = this.hp <= MAX_HP * 0.5;
    const anim = calm ? 'the_head:benevolent' : 'the_head:truth';
    if (this.scene.anims.exists(anim) && this.head.anims.currentAnim?.key !== anim) this.head.play(anim);
  }

  private spawnFault(px: number, py: number): void {
    const choices: Array<{ thread: number; t: number; x: number; y: number }> = [];
    THREADS.forEach(([a, b], ti) => {
      const [ax, ay] = KNOTS[a] as [number, number];
      const [bx, by] = KNOTS[b] as [number, number];
      for (const t of SPOT_T) {
        const x = ax + (bx - ax) * t;
        const y = ay + (by - ay) * t + 70; // the apprentice stands under the thread, on the ground
        const near = [...this.faults.values()].some((f) => Math.hypot(f.x - x, f.y - y) < 260);
        if (!near && this.o.isFree(x, y) && Math.hypot(x - px, y - py) > 320) choices.push({ thread: ti, t, x, y });
      }
    });
    const pick = choices[Math.floor(Math.random() * choices.length)];
    if (!pick) return;
    const type = PHASE_SEQUENCE[this.seq % PHASE_SEQUENCE.length] as FaultType;
    this.seq++;
    this.faultsDone++;
    const mark = type === 'choice'
      ? this.scene.add.text(pick.x, pick.y - 56, '?', { fontFamily: 'Segoe UI, Arial', fontSize: '30px', color: '#ffd36b', fontStyle: 'bold', stroke: '#2b2150', strokeThickness: 5 }).setOrigin(0.5).setDepth(4600)
      : null;
    const id = `f${this.nextId++}`;
    this.faults.set(id, { id, type, phase: this.phase, ...pick, progress: 0, mark });
    this.float(pick.x, pick.y - 90, 'נותק!', '#ff6b7d');
  }

  private mend(f: Fault): void {
    this.faults.delete(f.id);
    f.mark?.destroy();
    const dmg = DAMAGE[f.type];
    const len = Math.hypot(this.hx - f.x, this.hy - f.y);
    this.shots.push({ x0: f.x, y0: f.y - 60, x1: this.hx, y1: this.hy, travelled: 0, len, dmg, count: f.type === 'choice' ? 9 : 4 });
    this.float(f.x, f.y - 90, f.type === 'choice' ? 'נכון!' : 'תוקן!', '#5cf0d0');
  }

  private land(s: Shot): void {
    this.hp = Math.max(0, this.hp - s.dmg);
    this.scene.cameras.main.shake(180, 0.004);
    this.head.setTint(0xffffff);
    this.scene.time.delayedCall(120, () => this.head.clearTint());
    this.float(this.hx, this.hy + 90, `-${s.dmg}`, '#ffd36b');
    const before = this.phase;
    this.phase = phaseOf(this.hp);
    if (this.phase !== before) { this.banner = 3; this.faultsDone = 0; this.seq = 0; }
    this.paint();
    if (this.hp <= 0) this.finish(true);
  }

  private hurt(px: number, py: number): void {
    if (this.invuln > 0 || this.ended) return;
    this.lives--;
    this.invuln = 1.4;
    this.scene.cameras.main.shake(160, 0.006);
    this.float(px, py - 70, 'זרם ביטים!', '#ff6b7d');
    this.paint();
    if (this.lives <= 0) this.finish(false);
  }

  private finish(won: boolean): void {
    if (this.ended) return;
    this.ended = true;
    this.panel?.remove();
    this.panel = null;
    this.taskOpen = false;
    this.o.ctx.modal = false;
    if (won) {
      this.scene.tweens.add({ targets: this.head, y: this.hy - 260, alpha: 0, duration: 2600, ease: 'sine.in' });
    }
    this.scene.time.delayedCall(won ? 2800 : 600, () => this.o.onEnd({ won }));
  }

  private float(x: number, y: number, text: string, color: string): void {
    const t = this.scene.add.text(x, y, text, { fontFamily: 'Segoe UI, Arial', fontSize: '22px', color, fontStyle: 'bold', stroke: '#0b0c1c', strokeThickness: 5, rtl: true }).setOrigin(0.5).setDepth(4700);
    this.scene.tweens.add({ targets: t, y: y - 44, alpha: 0, duration: 1200, onComplete: () => t.destroy() });
  }

  // ---- a task from the lessons ----
  private async openTask(f: Fault): Promise<void> {
    this.taskOpen = true;
    this.o.ctx.modal = true;
    const { loadBundle } = await import('../ui/learning');
    const b = loadBundle(`lesson0${f.phase + 1}`);
    if (!b) { this.taskOpen = false; this.o.ctx.modal = false; this.mend(f); return; }
    const level = f.phase < 2 ? 'easy' : 'medium';
    const count = b.game.levels[level].count;
    const index = Math.floor(Math.random() * count);
    const host = el('section', 'lrn-wire');
    const feedback = el('div', 'lrn-wire-msg', '');
    const bar = el('div', 'lrn-row');
    const card = el('div', 'boss-panel-card bosstask-card', '', [
      el('span', 'lrn-banner-n', `תקלה שדורשת החלטה · שיעור ${f.phase + 1}: ${PHASE_TOPIC[f.phase] ?? ''}`),
      host, feedback, bar,
    ]);
    const panel = el('div', 'bosstask', '', [card]);
    uiRoot().append(panel);
    this.panel = panel;
    let cleanup: (() => void) | null = null;
    let settled = false;
    const api = {
      timeLimit: null,
      elapsed: () => 0,
      onTimeout: () => {},
      setBusy: () => {},
      isPaused: () => false,
      flash: () => {},
      resolve: (ok: boolean, text: string) => {
        if (settled) return;
        settled = true;
        feedback.className = `lrn-wire-msg ${ok ? 'good' : 'warn'}`;
        feedback.textContent = `${ok ? 'נכון! ' : 'לא הפעם. '}${text}`;
        const go = el('button', 'btn primary', ok ? 'לתקן את החוט' : 'להמשיך');
        go.type = 'button';
        go.addEventListener('click', () => {
          cleanup?.();
          panel.remove();
          this.panel = null;
          this.taskOpen = false;
          this.o.ctx.modal = false;
          if (this.ended) return;
          if (ok) this.mend(f);
          else this.hurt(f.x, f.y);
        });
        bar.replaceChildren(go);
        go.focus();
      },
    };
    cleanup = b.game.mountRound(level, index, host, api as never);
  }

  // ---- drawing ----
  private draw(px: number, py: number): void {
    const g = this.g;
    g.clear();
    const t = this.time;
    // the web
    THREADS.forEach(([a, b], ti) => {
      const [ax, ay] = KNOTS[a] as [number, number];
      const [bx, by] = KNOTS[b] as [number, number];
      const cuts = [...this.faults.values()].filter((f) => f.thread === ti).map((f) => f.t);
      g.lineStyle(5, 0x5cf0d0, 0.9);
      const steps = 34;
      let pen = false;
      g.beginPath();
      for (let i = 0; i <= steps; i++) {
        const u = i / steps;
        if (cuts.some((c) => Math.abs(u - c) < 0.045)) { if (pen) g.strokePath(); g.beginPath(); pen = false; continue; }
        const wave = Math.sin(u * Math.PI * 3 + t * 2) * 6 * Math.sin(u * Math.PI);
        const len = Math.hypot(bx - ax, by - ay) || 1;
        const x = ax + (bx - ax) * u + (-(by - ay) / len) * wave;
        const y = ay + (by - ay) * u + ((bx - ax) / len) * wave;
        if (!pen) { g.moveTo(x, y); pen = true; } else g.lineTo(x, y);
      }
      g.strokePath();
    });
    for (const k of Object.values(KNOTS)) { g.fillStyle(0xffd36b, 1); g.fillCircle(k[0], k[1], 9); }
    // faults
    for (const f of this.faults.values()) {
      const [ax, ay] = KNOTS[(THREADS[f.thread] as [string, string])[0]] as [number, number];
      const [bx, by] = KNOTS[(THREADS[f.thread] as [string, string])[1]] as [number, number];
      const cx = ax + (bx - ax) * f.t;
      const cy = ay + (by - ay) * f.t;
      const pulse = 1 + Math.sin(t * 9) * 0.15;
      g.lineStyle(4, 0xff6b7d, 1);
      g.strokeCircle(cx, cy, 20 * pulse);
      g.lineBetween(cx - 9, cy - 9, cx + 9, cy + 9);
      g.lineBetween(cx + 9, cy - 9, cx - 9, cy + 9);
      // a line down to where the apprentice has to stand, and the ring of the mending
      g.lineStyle(2, 0xff6b7d, 0.6);
      g.lineBetween(cx, cy + 20, f.x, f.y - 8);
      g.fillStyle(0xff6b7d, 0.25);
      g.fillCircle(f.x, f.y, 44 * pulse);
      g.lineStyle(4, 0xff6b7d, 0.9);
      g.strokeCircle(f.x, f.y, 44 * pulse);
      if (f.progress > 0) { g.lineStyle(7, 0x5cf0d0, 1); g.beginPath(); g.arc(f.x, f.y, 44, -Math.PI / 2, -Math.PI / 2 + f.progress * Math.PI * 2); g.strokePath(); }
      f.mark?.setPosition(f.x, f.y - 62 + Math.sin(t * 5) * 3);
    }
    // streams of bits: warning line, then the bits
    for (const s of this.streams) {
      if (s.telegraph > 0) {
        g.lineStyle(8, 0xff4d63, 0.25 + 0.35 * Math.abs(Math.sin(t * 16)));
        g.lineBetween(s.x0, s.y0, s.x0 + s.dx * 1900, s.y0 + s.dy * 1900);
        continue;
      }
      for (let i = 0; i < s.bits; i++) {
        const dist = s.travelled - i * 54;
        if (dist < 0 || dist > 1900) continue;
        const bx = s.x0 + s.dx * dist;
        const by = s.y0 + s.dy * dist;
        g.fillStyle(0xff4d63, 1);
        g.fillRoundedRect(bx - 12, by - 12, 24, 24, 5);
        g.lineStyle(2, 0xffffff, 1);
        g.strokeRoundedRect(bx - 12, by - 12, 24, 24, 5);
        g.fillStyle(0xffffff, 1);
        if ((i + Math.floor(t * 5)) % 2) g.fillRect(bx - 2, by - 7, 4, 14); else g.strokeCircle(bx, by, 6);
      }
    }
    // our bits
    for (const s of this.shots) {
      const dx = (s.x1 - s.x0) / (s.len || 1);
      const dy = (s.y1 - s.y0) / (s.len || 1);
      for (let i = 0; i < s.count; i++) {
        const dist = s.travelled - i * 40;
        if (dist < 0 || dist > s.len) continue;
        g.fillStyle(0x5cf0d0, 1);
        g.fillRoundedRect(s.x0 + dx * dist - 11, s.y0 + dy * dist - 11, 22, 22, 5);
        g.lineStyle(2, 0xffffff, 1);
        g.strokeRoundedRect(s.x0 + dx * dist - 11, s.y0 + dy * dist - 11, 22, 22, 5);
      }
    }
    if (this.invuln > 0 && Math.floor(t * 14) % 2 === 0) { g.lineStyle(3, 0xff6b7d, 0.9); g.strokeCircle(px, py - 22, 34); }
    if (this.countdown > 0 || this.banner > 0) this.labelEl.classList.add('pulse'); else this.labelEl.classList.remove('pulse');
  }
}
