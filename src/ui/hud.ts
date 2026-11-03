import { bus } from '../core/bus';
import { el, mmss, uiRoot } from './dom';

export class Hud {
  private readonly bar = el('div', 'hud');
  private readonly timer = el('div', 'pill');
  private readonly coins = el('div', 'pill');
  private readonly objective = el('div', 'pill objective');
  private readonly sight = el('button', 'btn', 'ראיית חוטים (Q)');
  private readonly cards = el('button', 'btn', 'אוסף');
  private readonly interact = el('button', 'btn primary interact');
  private readonly toasts = el('div', 'toast-box');
  private sightOn = false;
  private current: { id: string } | null = null;
  onCollection: () => void = () => {};

  constructor() {
    this.bar.append(this.timer, this.coins, el('div', 'spacer'), this.cards, this.sight);
    uiRoot().append(this.bar, this.objective, this.interact, this.toasts);
    this.sight.addEventListener('click', () => this.toggleSight());
    this.cards.addEventListener('click', () => this.onCollection());
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

  setObjective(text: string): void {
    this.objective.textContent = text;
    this.objective.style.display = text ? '' : 'none';
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

  setCoins(n: number): void {
    this.coins.textContent = `מטבעות ${n}`;
  }

  toast(msg: string, kind: '' | 'good' | 'clue' = '', ms = 3600): void {
    const t = el('div', `toast ${kind}`, msg);
    this.toasts.append(t);
    window.setTimeout(() => t.remove(), ms);
    while (this.toasts.childElementCount > 3) this.toasts.firstElementChild?.remove();
  }
}
