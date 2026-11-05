/**
 * All the sound of the game, made in the browser (no files to download): a quiet generative score that changes with
 * the place, and small synthesized effects. Music and effects have their own volume and their own off switch.
 */
export type Mood =
  | 'menu' | 'village' | 'market' | 'mill' | 'orchard' | 'woods' | 'moor' | 'coast' | 'tower'
  | 'house' | 'lesson' | 'game' | 'truth' | 'boss';

export interface SoundSettings { musicOn: boolean; sfxOn: boolean; musicVol: number; sfxVol: number }

interface MoodDef {
  /** Semitone steps above the root that the tune walks on. */
  scale: number[];
  root: number;
  bpm: number;
  /** Chord roots (semitones) the pad cycles through, each as a triad of the scale. */
  chords: number[][];
  /** Chance that a beat plays a note. */
  density: number;
  voice: 'pluck' | 'bell' | 'soft' | 'box';
  /** Octave shift of the tune. */
  octave: number;
  pad: number;
  /** 0 none; low rumble/pulse for tension. */
  pulse?: number;
  noise?: { kind: 'wind' | 'waves'; level: number };
  /** Music that must not pull attention (lessons, tasks) is played at this share of the music volume. */
  share: number;
}

const MAJ_PENT = [0, 2, 4, 7, 9];
const MIN_PENT = [0, 3, 5, 7, 10];

export const MOODS: Record<Mood, MoodDef> = {
  menu: { scale: MAJ_PENT, root: 220, bpm: 60, chords: [[0, 4, 7], [-3, 0, 4], [-5, -1, 2], [-7, -3, 0]], density: 0.35, voice: 'bell', octave: 1, pad: 0.5, share: 1 },
  village: { scale: MAJ_PENT, root: 261.6, bpm: 72, chords: [[0, 4, 7], [-3, 0, 4], [5, 9, 12], [-5, -1, 2]], density: 0.5, voice: 'pluck', octave: 0, pad: 0.55, share: 1 },
  market: { scale: [0, 2, 4, 5, 7, 9, 10], root: 293.7, bpm: 96, chords: [[0, 4, 7], [10, 14, 17], [5, 9, 12], [0, 4, 7]], density: 0.62, voice: 'pluck', octave: 0, pad: 0.4, share: 1 },
  mill: { scale: MAJ_PENT, root: 196, bpm: 66, chords: [[0, 4, 7], [5, 9, 12], [7, 11, 14], [0, 4, 7]], density: 0.55, voice: 'soft', octave: 1, pad: 0.55, noise: { kind: 'waves', level: 0.02 }, share: 1 },
  orchard: { scale: [0, 2, 4, 6, 7, 9, 11], root: 349.2, bpm: 60, chords: [[0, 4, 7], [2, 6, 9], [4, 7, 11], [0, 4, 7]], density: 0.4, voice: 'soft', octave: 0, pad: 0.5, share: 1 },
  woods: { scale: [0, 2, 3, 5, 7, 9, 10], root: 220, bpm: 52, chords: [[0, 3, 7], [-2, 2, 5], [3, 7, 10], [0, 3, 7]], density: 0.28, voice: 'bell', octave: 1, pad: 0.6, noise: { kind: 'wind', level: 0.012 }, share: 0.9 },
  moor: { scale: MIN_PENT, root: 146.8, bpm: 46, chords: [[0, 7, 12], [-2, 5, 10], [0, 7, 12], [-4, 3, 8]], density: 0.2, voice: 'bell', octave: 1, pad: 0.7, noise: { kind: 'wind', level: 0.025 }, share: 0.85 },
  coast: { scale: [0, 2, 4, 7, 9], root: 329.6, bpm: 70, chords: [[0, 4, 7], [5, 9, 12], [-3, 0, 4], [0, 4, 7]], density: 0.4, voice: 'soft', octave: 0, pad: 0.55, noise: { kind: 'waves', level: 0.03 }, share: 1 },
  tower: { scale: [0, 1, 4, 5, 7, 8], root: 130.8, bpm: 44, chords: [[0, 7, 12], [1, 8, 13], [0, 7, 12], [-2, 5, 10]], density: 0.15, voice: 'bell', octave: 1, pad: 0.8, share: 0.8 },
  house: { scale: MAJ_PENT, root: 392, bpm: 80, chords: [[0, 4, 7], [-3, 0, 4]], density: 0.45, voice: 'box', octave: 0, pad: 0.15, share: 0.8 },
  lesson: { scale: MAJ_PENT, root: 220, bpm: 56, chords: [[0, 7, 12], [-3, 4, 9], [-5, 2, 7], [0, 7, 12]], density: 0.07, voice: 'soft', octave: 1, pad: 0.45, share: 0.4 },
  game: { scale: MAJ_PENT, root: 261.6, bpm: 104, chords: [[0, 4, 7], [-3, 0, 4], [5, 9, 12], [-5, -1, 2]], density: 0.5, voice: 'pluck', octave: 1, pad: 0.25, share: 0.6 },
  truth: { scale: [0, 1, 3, 5, 6, 8], root: 164.8, bpm: 42, chords: [[0, 6, 11], [1, 6, 10], [0, 6, 11], [-1, 5, 10]], density: 0.12, voice: 'bell', octave: 1, pad: 0.9, noise: { kind: 'wind', level: 0.03 }, share: 0.9 },
  boss: { scale: MIN_PENT, root: 146.8, bpm: 118, chords: [[0, 7, 12], [-2, 5, 10], [-4, 3, 8], [-2, 5, 10]], density: 0.55, voice: 'pluck', octave: 1, pad: 0.5, pulse: 0.5, share: 0.9 },
};

export type Sfx =
  | 'click' | 'open' | 'close' | 'pickup' | 'coin' | 'diary' | 'creature' | 'success' | 'fail' | 'hurt' | 'bit'
  | 'mend' | 'bossHit' | 'door' | 'thread' | 'prize' | 'warn' | 'fanfare' | 'pop';

const DEFAULTS: SoundSettings = { musicOn: true, sfxOn: true, musicVol: 0.5, sfxVol: 0.8 };

const mtof = (root: number, semis: number): number => root * Math.pow(2, semis / 12);

export class AudioHub {
  private ctx: AudioContext | null = null;
  private master!: GainNode;
  private musicBus!: GainNode;
  private sfxBus!: GainNode;
  private delay!: DelayNode;
  private noiseBuf: AudioBuffer | null = null;
  settings: SoundSettings = { ...DEFAULTS };
  private moodNow: Mood | null = null;
  private layer: { stop(): void; gain: GainNode } | null = null;
  // what decides the mood, strongest first
  private base: Mood = 'menu';
  private overlays: Mood[] = [];
  private sight = false;
  private boss = false;
  private held = false;

  configure(s: Partial<SoundSettings>): void {
    this.settings = { ...this.settings, ...s };
    this.applyVolumes();
  }

  /** Browsers only allow sound after a tap: call this from the first click. */
  unlock(): void {
    if (!this.ctx) this.build();
    void this.ctx?.resume();
    this.resolve();
  }

  private build(): void {
    const AC = (window.AudioContext ?? (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext);
    if (!AC) return;
    const ctx = new AC();
    this.ctx = ctx;
    this.master = ctx.createGain();
    // a gentle limiter, so layered notes and effects can never clip
    const limiter = ctx.createDynamicsCompressor();
    limiter.threshold.value = -14;
    limiter.ratio.value = 6;
    this.master.connect(limiter).connect(ctx.destination);
    this.musicBus = ctx.createGain();
    this.sfxBus = ctx.createGain();
    this.musicBus.connect(this.master);
    this.sfxBus.connect(this.master);
    // a soft echo for the music, so a few notes feel like a place
    this.delay = ctx.createDelay(1.5);
    this.delay.delayTime.value = 0.42;
    const fb = ctx.createGain();
    fb.gain.value = 0.32;
    const wet = ctx.createGain();
    wet.gain.value = 0.35;
    this.delay.connect(fb).connect(this.delay);
    this.delay.connect(wet).connect(this.musicBus);
    const len = ctx.sampleRate * 2;
    this.noiseBuf = ctx.createBuffer(1, len, ctx.sampleRate);
    const d = this.noiseBuf.getChannelData(0);
    for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
    this.applyVolumes();
  }

  private applyVolumes(): void {
    if (!this.ctx) return;
    const t = this.ctx.currentTime;
    this.musicBus.gain.setTargetAtTime(this.settings.musicOn && !this.held ? this.settings.musicVol : 0, t, 0.1);
    this.sfxBus.gain.setTargetAtTime(this.settings.sfxOn ? this.settings.sfxVol : 0, t, 0.05);
  }

  // ----- mood: who decides -----
  setBase(m: Mood): void { this.base = m; this.resolve(); }
  pushOverlay(m: Mood): () => void {
    this.overlays.push(m);
    this.resolve();
    return () => { const i = this.overlays.lastIndexOf(m); if (i >= 0) this.overlays.splice(i, 1); this.resolve(); };
  }
  setSight(on: boolean): void { this.sight = on; this.resolve(); }
  setBoss(on: boolean): void { this.boss = on; this.resolve(); }
  /** Silence the music while a video plays. */
  hold(on: boolean): void { this.held = on; this.applyVolumes(); }

  private resolve(): void {
    const top = this.overlays[this.overlays.length - 1];
    const m: Mood = this.boss ? 'boss' : top ?? (this.sight && this.base !== 'house' ? 'truth' : this.base);
    this.playMood(m);
  }

  get mood(): Mood | null { return this.moodNow; }

  // ----- the score -----
  private wanted: Mood = 'menu';

  private playMood(m: Mood): void {
    this.wanted = m;
    const ctx = this.ctx;
    if (!ctx || m === this.moodNow) return;
    const old = this.layer;
    if (old) {
      old.gain.gain.setTargetAtTime(0, ctx.currentTime, 0.8);
      window.setTimeout(() => old.stop(), 3500);
    }
    this.moodNow = m;
    this.layer = this.startLayer(MOODS[m]);
  }

  private startLayer(def: MoodDef): { stop(): void; gain: GainNode } {
    const ctx = this.ctx as AudioContext;
    const gain = ctx.createGain();
    gain.gain.value = 0;
    gain.gain.setTargetAtTime(def.share, ctx.currentTime, 1.2);
    gain.connect(this.musicBus);
    const send = ctx.createGain();
    send.gain.value = 0.55;
    gain.connect(send).connect(this.delay);
    const nodes: AudioNode[] = [gain, send];
    const stops: Array<() => void> = [];
    const beat = 60 / def.bpm;
    let step = 0;
    let chordIdx = 0;
    let next = ctx.currentTime + 0.2;
    let pos = Math.floor(Math.random() * def.scale.length);

    const padChord = (when: number, chord: number[]): void => {
      const len = beat * 8;
      for (const semi of chord) {
        for (const detune of [-6, 6]) {
          const o = ctx.createOscillator();
          o.type = def.voice === 'bell' ? 'sine' : 'triangle';
          o.frequency.value = mtof(def.root / 2, semi);
          o.detune.value = detune;
          const g = ctx.createGain();
          const lp = ctx.createBiquadFilter();
          lp.type = 'lowpass';
          lp.frequency.value = 900;
          g.gain.setValueAtTime(0, when);
          g.gain.linearRampToValueAtTime(0.05 * def.pad, when + len * 0.35);
          g.gain.linearRampToValueAtTime(0, when + len + 1.5);
          o.connect(lp).connect(g).connect(gain);
          o.start(when);
          o.stop(when + len + 1.8);
        }
      }
    };

    const note = (when: number, freq: number, vel: number): void => {
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      const dur = def.voice === 'soft' ? beat * 2.2 : def.voice === 'bell' ? beat * 3 : def.voice === 'box' ? beat * 1.4 : beat * 1.1;
      o.type = def.voice === 'bell' || def.voice === 'box' ? 'sine' : def.voice === 'soft' ? 'triangle' : 'triangle';
      o.frequency.value = freq;
      const peak = 0.11 * vel;
      g.gain.setValueAtTime(0, when);
      g.gain.linearRampToValueAtTime(peak, when + (def.voice === 'soft' ? 0.18 : 0.012));
      g.gain.exponentialRampToValueAtTime(0.0008, when + dur);
      o.connect(g).connect(gain);
      o.start(when);
      o.stop(when + dur + 0.1);
      if (def.voice === 'bell' || def.voice === 'box') {
        const o2 = ctx.createOscillator();
        const g2 = ctx.createGain();
        o2.type = 'sine';
        o2.frequency.value = freq * 2.01;
        g2.gain.setValueAtTime(0, when);
        g2.gain.linearRampToValueAtTime(peak * 0.35, when + 0.01);
        g2.gain.exponentialRampToValueAtTime(0.0005, when + dur * 0.5);
        o2.connect(g2).connect(gain);
        o2.start(when);
        o2.stop(when + dur);
      }
    };

    const pulse = (when: number): void => {
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.type = 'sine';
      o.frequency.setValueAtTime(110, when);
      o.frequency.exponentialRampToValueAtTime(48, when + 0.18);
      g.gain.setValueAtTime(0.16 * (def.pulse ?? 0), when);
      g.gain.exponentialRampToValueAtTime(0.001, when + 0.28);
      o.connect(g).connect(gain);
      o.start(when);
      o.stop(when + 0.3);
    };

    if (def.noise && this.noiseBuf) {
      const src = ctx.createBufferSource();
      src.buffer = this.noiseBuf;
      src.loop = true;
      const bp = ctx.createBiquadFilter();
      bp.type = 'lowpass';
      bp.frequency.value = def.noise.kind === 'wind' ? 520 : 900;
      const ng = ctx.createGain();
      ng.gain.value = def.noise.level;
      const lfo = ctx.createOscillator();
      lfo.frequency.value = def.noise.kind === 'wind' ? 0.11 : 0.09;
      const lg = ctx.createGain();
      lg.gain.value = def.noise.level * 0.7;
      lfo.connect(lg).connect(ng.gain);
      src.connect(bp).connect(ng).connect(gain);
      src.start();
      lfo.start();
      stops.push(() => { try { src.stop(); lfo.stop(); } catch { /* already stopped */ } });
    }

    const tick = (): void => {
      // schedule everything that falls in the next second
      while (next < ctx.currentTime + 1.0) {
        if (step % 8 === 0) {
          padChord(next, (def.chords[chordIdx % def.chords.length] as number[]).map((s) => s));
          chordIdx++;
        }
        if (def.pulse && step % 2 === 0) pulse(next);
        if (Math.random() < def.density) {
          // walk gently on the scale: mostly small steps, sometimes a leap
          pos = Math.max(0, Math.min(def.scale.length * 2 - 1, pos + (Math.random() < 0.7 ? (Math.random() < 0.5 ? -1 : 1) : (Math.random() < 0.5 ? -3 : 3))));
          const semis = (def.scale[pos % def.scale.length] as number) + 12 * Math.floor(pos / def.scale.length) + 12 * def.octave;
          note(next, mtof(def.root, semis), 0.55 + Math.random() * 0.45);
        }
        next += beat;
        step++;
      }
    };
    tick();
    const timer = window.setInterval(tick, 400);
    return {
      gain,
      stop: () => {
        window.clearInterval(timer);
        stops.forEach((s) => s());
        for (const n of nodes) { try { n.disconnect(); } catch { /* gone */ } }
      },
    };
  }

  // ----- effects -----
  private tone(freq: number, dur: number, type: OscillatorType, vol: number, when = 0, slideTo?: number): void {
    const ctx = this.ctx;
    if (!ctx || !this.settings.sfxOn) return;
    const t = ctx.currentTime + when;
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type = type;
    o.frequency.setValueAtTime(freq, t);
    if (slideTo) o.frequency.exponentialRampToValueAtTime(slideTo, t + dur);
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(vol, t + 0.01);
    g.gain.exponentialRampToValueAtTime(0.0008, t + dur);
    o.connect(g).connect(this.sfxBus);
    o.start(t);
    o.stop(t + dur + 0.05);
  }

  private burst(dur: number, vol: number, from: number, to: number, when = 0): void {
    const ctx = this.ctx;
    if (!ctx || !this.noiseBuf || !this.settings.sfxOn) return;
    const t = ctx.currentTime + when;
    const src = ctx.createBufferSource();
    src.buffer = this.noiseBuf;
    const f = ctx.createBiquadFilter();
    f.type = 'bandpass';
    f.frequency.setValueAtTime(from, t);
    f.frequency.exponentialRampToValueAtTime(to, t + dur);
    const g = ctx.createGain();
    g.gain.setValueAtTime(vol, t);
    g.gain.exponentialRampToValueAtTime(0.001, t + dur);
    src.connect(f).connect(g).connect(this.sfxBus);
    src.start(t);
    src.stop(t + dur + 0.05);
  }

  sfx(name: Sfx): void {
    if (!this.ctx || !this.settings.sfxOn) return;
    switch (name) {
      case 'click': this.tone(660, 0.07, 'triangle', 0.12); break;
      case 'open': this.tone(440, 0.18, 'triangle', 0.14, 0, 880); break;
      case 'close': this.tone(660, 0.16, 'triangle', 0.12, 0, 330); break;
      case 'pickup': this.tone(784, 0.12, 'sine', 0.2); this.tone(1175, 0.2, 'sine', 0.18, 0.09); break;
      case 'coin': this.tone(1318, 0.09, 'square', 0.07); this.tone(1760, 0.18, 'square', 0.06, 0.07); break;
      case 'diary': this.burst(0.25, 0.12, 2500, 900); this.tone(988, 0.5, 'sine', 0.16, 0.12); this.tone(1319, 0.6, 'sine', 0.12, 0.22); break;
      case 'creature': [880, 1100, 1320].forEach((f, i) => this.tone(f, 0.12, 'sine', 0.16, i * 0.09, f * 1.08)); break;
      case 'success': [523, 659, 784, 1047].forEach((f, i) => this.tone(f, 0.18, 'triangle', 0.16, i * 0.08)); break;
      case 'fail': this.tone(220, 0.3, 'triangle', 0.18, 0, 150); break;
      case 'hurt': this.burst(0.3, 0.3, 1800, 200); this.tone(180, 0.28, 'sawtooth', 0.12, 0, 70); break;
      case 'bit': this.tone(1200, 0.06, 'square', 0.05, 0, 1800); break;
      case 'mend': [660, 880, 1320].forEach((f, i) => this.tone(f, 0.2, 'sine', 0.15, i * 0.06)); this.burst(0.35, 0.06, 3000, 6000); break;
      case 'bossHit': this.tone(90, 0.4, 'sine', 0.35, 0, 40); this.burst(0.25, 0.2, 900, 120); this.tone(330, 0.3, 'triangle', 0.1, 0.05, 220); break;
      case 'door': this.burst(0.5, 0.16, 300, 900); this.tone(110, 0.35, 'triangle', 0.12, 0.05, 90); break;
      case 'thread': this.tone(520, 0.8, 'sine', 0.13, 0, 1560); this.tone(780, 0.8, 'sine', 0.08, 0.05, 2340); break;
      case 'prize': [523, 659, 784, 1047, 1319].forEach((f, i) => this.tone(f, 0.28, 'triangle', 0.17, i * 0.1)); break;
      case 'warn': this.tone(300, 0.14, 'square', 0.06); this.tone(300, 0.14, 'square', 0.06, 0.2); break;
      case 'fanfare': [392, 523, 659, 784, 1047].forEach((f, i) => this.tone(f, 0.45, 'triangle', 0.17, i * 0.14)); this.tone(1319, 0.9, 'sine', 0.14, 0.7); break;
      case 'pop': this.tone(500, 0.12, 'sine', 0.16, 0, 1000); break;
    }
  }
}

export const audio = new AudioHub();

/** The mood of each region of the valley. */
export const REGION_MOOD: Record<string, Mood> = {
  hearth: 'village', market: 'market', moor: 'moor', mill: 'mill', tower: 'tower', orchard: 'orchard', woods: 'woods', coast: 'coast',
};
