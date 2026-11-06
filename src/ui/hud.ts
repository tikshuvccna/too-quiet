import { bus } from '../core/bus';
import { el, isTouchDevice, mmss, uiRoot } from './dom';
import { audio } from '../audio/audio';
import { hintBadge } from './hintBadge';

export class Hud {
  private readonly bar = el('div', 'hud');
  private readonly timer = el('div', 'pill timer');
  private readonly coins = el('div', 'pill coins');
  private readonly objective = el('div', 'pill objective');
  private readonly compass = el('div', 'pill compass');
  private readonly compassArrow = el('span', 'compass-arrow');
  private readonly compassText = el('span', 'compass-text');
  private readonly sight = el('button', 'btn', isTouchDevice() ? 'ראיית חוטים' : 'ראיית חוטים (Q)');
  private readonly cards = el('button', 'btn', 'אוסף');
  private readonly gear = el('button', 'btn gear', 'הגדרות');
  private readonly help = el('button', 'btn help-btn', '?');
  private readonly interact = el('button', 'btn primary interact');
  private readonly toasts = el('div', 'toast-box');
  private sightOn = false;
  private current: { id: string } | null = null;
  onCollection: () => void = () => {};
  onSettings: () => void = () => {};
  onHelp: () => void = () => {};

  constructor() {
    this.bar.append(this.timer, this.coins, el('div', 'spacer'), this.help, this.gear, this.cards, this.sight, this.compass, this.objective);
    this.compass.append(this.compassArrow, this.compassText);
    this.compass.style.display = 'none';
    uiRoot().append(this.bar, this.interact, this.toasts);
    // toasts sit just under the HUD, whatever height it wraps to (small phones use two or three rows)
    const measure = (): void => document.documentElement.style.setProperty('--hud-h', `${Math.ceil(this.bar.getBoundingClientRect().bottom)}px`);
    if (typeof ResizeObserver !== 'undefined') new ResizeObserver(measure).observe(this.bar);
    window.addEventListener('resize', measure);
    requestAnimationFrame(measure);
    this.sight.addEventListener('click', () => this.toggleSight());
    this.cards.addEventListener('click', () => this.onCollection());
    this.help.setAttribute('aria-label', 'עזרה');
    this.help.title = 'עזרה';
    this.help.addEventListener('click', () => this.onHelp());
    this.gear.addEventListener('click', () => this.onSettings());
    this.interact.addEventListener('click', () => this.use());
    bus.on('interact:available', (a) => {
      this.current = a;
      this.interact.classList.toggle('show', !!a);
      if (a) this.interact.textContent = a.label;
    });
    window.addEventListener('keydown', (e) => {
      if (e.key === 'q' || e.key === 'Q') this.toggleSight();
      if (e.key === 'e' || e.key === 'E') this.use();
    });
  }

  /** A place in the top row for small readouts (the FPS counter). */
  get row(): HTMLElement {
    return this.bar;
  }

  setObjective(text: string): void {
    this.objective.textContent = text;
    this.objective.style.display = text ? '' : 'none';
  }

  /** An arrow toward where the next lesson is (null hides it). `angle` is radians on screen, 0 = right, clockwise. */
  setCompass(info: { angle: number; text: string } | null): void {
    this.compass.style.display = info ? '' : 'none';
    if (!info) return;
    this.compassArrow.style.transform = `rotate(${info.angle + Math.PI / 2}rad)`;
    this.compassText.textContent = info.text;
  }

  setVisible(v: boolean): void {
    this.bar.style.display = v ? '' : 'none';
    this.objective.style.visibility = v ? 'visible' : 'hidden';
    if (!v) this.interact.classList.remove('show');
  }

  private use(): void {
    if (this.current) bus.emit('interact:use', { id: this.current.id });
  }

  toggleSight(force?: boolean): void {
    this.sightOn = force ?? !this.sightOn;
    this.sight.classList.toggle('on', this.sightOn);
    bus.emit('sight:toggle', { on: this.sightOn });
  }

  get isSightOn(): boolean {
    return this.sightOn;
  }

  setTimer(remaining: number, warning: boolean): void {
    this.timer.textContent = `זמן בעולם ${mmss(remaining)}`;
    this.timer.classList.toggle('warn', warning);
  }

  private lastCoins = -1;

  setCoins(n: number): void {
    if (this.lastCoins >= 0 && n > this.lastCoins) audio.sfx('coin');
    this.lastCoins = n;
    this.coins.textContent = `מטבעות ${n}`;
  }

  /** `hint` adds the gold "רמז" badge: use it only for notes that point at something to find, solve or learn. */
  toast(msg: string, kind: '' | 'good' | 'clue' = '', ms = 3600, hint = false): void {
    const t = el('div', `toast ${kind}${hint ? ' has-hint' : ''}`);
    if (hint) t.append(hintBadge());
    t.append(el('span', 'toast-text', msg));
    this.toasts.append(t);
    window.setTimeout(() => t.remove(), ms);
    while (this.toasts.childElementCount > 3) this.toasts.firstElementChild?.remove();
  }
}
