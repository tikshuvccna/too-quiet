import { bus } from '../core/bus';
import { el, uiRoot } from './dom';
import { hintBadge } from './hintBadge';
import { frameStyle, loadPortrait, moodFor, portraitFor, type PortraitSheet } from './portraits';

export interface Line {
  id?: string;
  speaker: string;
  text: string;
  /** Shows the gold "רמז" badge: this line points at something to find, solve or learn. */
  hint?: boolean;
}

export interface Choice {
  text: string;
  value: string;
}

export interface VoicePlayer {
  play(lineId: string): void;
  stop(): void;
}

/** Subtitle box with a speaker portrait. Click, tap, Space or Enter advances. Lines may carry an id for a voice recording. */
export class DialogueUI {
  private readonly box = el('div', 'dialogue');
  private readonly portrait = el('div', 'portrait');
  private readonly who = el('div', 'who');
  private readonly txt = el('div', 'txt');
  private readonly choices = el('div', 'choices');
  private readonly hint = el('div', 'hint', 'לחצו להמשך');
  private readonly badge = hintBadge();
  private resolve: (() => void) | null = null;
  private typing: number | null = null;
  private full = '';
  private open = false;
  private current: { name: string; mood: string; sheet: PortraitSheet } | null = null;
  private truthUntil = 0;
  private blinkTimer: number | null = null;
  subtitles = true;
  voice: VoicePlayer | null = null;
  names: Record<string, string> = {};
  look: 'girl' | 'boy' = 'girl';
  /** Portrait sheet of the outfit the player wears (e.g. skin_girl_sea); the original look is used when it is missing. */
  playerSheet: string | null = null;

  constructor() {
    this.badge.hidden = true;
    this.box.append(this.portrait, this.who, this.txt, this.choices, this.hint, this.badge);
    uiRoot().append(this.box);
    this.box.addEventListener('pointerdown', () => this.advance());
    window.addEventListener('keydown', (e) => {
      if (!this.open || this.choices.childElementCount) return;
      if (e.key === ' ' || e.key === 'Enter') {
        e.preventDefault();
        this.advance();
      }
    });
    // when the truth flickers through, the speaker's face changes with it
    bus.on('truth:flash', ({ ms }) => {
      this.truthUntil = performance.now() + ms;
      this.paintPortrait();
      window.setTimeout(() => this.paintPortrait(), ms + 30);
    });
  }

  get isOpen(): boolean {
    return this.open;
  }

  /** Plays lines one after another; resolves when the last one is dismissed. */
  async say(lines: Line[]): Promise<void> {
    for (const l of lines) await this.showLine(l);
    this.close();
  }

  async choose(prompt: Line | null, options: Choice[]): Promise<string> {
    if (prompt) this.fillLine(prompt, false);
    else this.fillLine({ speaker: '', text: '' }, false);
    this.hint.style.display = 'none';
    this.choices.replaceChildren();
    return new Promise((res) => {
      for (const o of options) {
        const b = el('button', 'btn', o.text);
        b.addEventListener('pointerdown', (e) => e.stopPropagation());
        b.addEventListener('click', () => {
          this.choices.replaceChildren();
          this.hint.style.display = '';
          res(o.value);
        });
        this.choices.append(b);
      }
    });
  }

  close(): void {
    this.open = false;
    this.voice?.stop();
    this.box.classList.remove('show', 'has-portrait', 'is-hint');
    if (this.blinkTimer !== null) window.clearInterval(this.blinkTimer);
    this.blinkTimer = null;
  }

  private showLine(l: Line): Promise<void> {
    this.fillLine(l, true);
    return new Promise((res) => {
      this.resolve = res;
    });
  }

  private fillLine(l: Line, typewriter: boolean): void {
    this.open = true;
    this.box.classList.add('show');
    this.box.classList.toggle('is-hint', !!l.hint);
    this.badge.hidden = !l.hint;
    this.who.textContent = this.names[l.speaker] ?? l.speaker;
    this.who.style.display = l.speaker ? '' : 'none';
    this.full = l.text;
    void this.setPortrait(l);
    if (l.id) this.voice?.play(l.id);
    if (this.typing !== null) clearInterval(this.typing);
    this.typing = null;
    if (!typewriter || !this.subtitles) {
      this.txt.textContent = this.subtitles ? l.text : '';
      return;
    }
    let i = 0;
    this.txt.textContent = '';
    this.typing = window.setInterval(() => {
      i += 2;
      this.txt.textContent = this.full.slice(0, i);
      if (i >= this.full.length && this.typing !== null) {
        clearInterval(this.typing);
        this.typing = null;
      }
    }, 22);
  }

  private async setPortrait(l: Line): Promise<void> {
    let name = portraitFor(l.speaker, this.look);
    if (!name) {
      this.current = null;
      this.box.classList.remove('has-portrait');
      return;
    }
    let sheet: PortraitSheet | null = null;
    if (l.speaker === 'player' && this.playerSheet) {
      sheet = await loadPortrait(this.playerSheet);
      if (sheet) name = this.playerSheet;
    }
    sheet ??= await loadPortrait(name);
    if (!sheet || !this.open) {
      this.box.classList.remove('has-portrait');
      return;
    }
    this.current = { name, mood: moodFor(l.speaker, l.text), sheet };
    this.box.classList.add('has-portrait');
    this.paintPortrait();
    if (this.blinkTimer === null) {
      this.blinkTimer = window.setInterval(() => {
        if (!this.current || performance.now() < this.truthUntil) return;
        this.paintPortrait('blink');
        window.setTimeout(() => this.paintPortrait(), 130);
      }, 3800);
    }
  }

  private paintPortrait(override?: string): void {
    const c = this.current;
    if (!c) return;
    const size = this.portrait.clientWidth || 150;
    const truth = performance.now() < this.truthUntil && c.sheet.frames[`${c.name}_truth`];
    const frame = override ?? (truth ? 'truth' : c.mood);
    const s = frameStyle(c.sheet, c.name, frame, size) ?? frameStyle(c.sheet, c.name, 'neutral', size);
    if (s) Object.assign(this.portrait.style, s);
  }

  private advance(): void {
    if (!this.resolve) return;
    if (this.typing !== null) {
      clearInterval(this.typing);
      this.typing = null;
      this.txt.textContent = this.full;
      return;
    }
    const r = this.resolve;
    this.resolve = null;
    r();
  }
}
