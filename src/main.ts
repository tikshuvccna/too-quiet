import Phaser from 'phaser';
import './styles.css';
import { bus } from './core/bus';
import { QUALITY_NAME, QualityManager } from './core/quality';
import { Session } from './core/session';
import { FpsMeter } from './ui/fpsMeter';
import { audio } from './audio/audio';
import { SaveStore, type Look } from './core/save';
import { CTX_KEY, type GameContext } from './game/context';
import { Controller } from './game/controller';
import { perksOf } from './game/perks';
import { BootScene } from './scenes/BootScene';
import { HouseScene } from './scenes/HouseScene';
import { WorldScene } from './scenes/WorldScene';
import { DialogueUI } from './ui/dialogue';
import { createVoicePlayer } from './ui/voice';
import { el, uiRoot } from './ui/dom';
import { Hud } from './ui/hud';
import { Joystick } from './ui/joystick';
import { SkyHead } from './ui/skyHead';

function boot(): void {
  const params = new URLSearchParams(location.search);
  const cap = Number(params.get('cap')) || undefined;
  const save = new SaveStore();
  save.load();
  if (params.has('fresh')) save.reset();

  const session = new Session({
    capSeconds: cap,
    warnAtSeconds: cap ? Math.max(1, cap - 10) : undefined,
    onWarning: () => bus.emit('session:warning', undefined),
    onStorm: () => bus.emit('session:storm', undefined),
  });
  session.bonus = perksOf(save).timeBonus;
  const hud = new Hud();
  const dialogue = new DialogueUI();
  dialogue.subtitles = save.data.settings.subtitles;
  dialogue.look = save.data.look;
  dialogue.voice = createVoicePlayer(() => save.data.settings.sfxOn, () => save.data.settings.sfxVol, (on) => audio.duck(on));
  audio.configure({ musicOn: save.data.settings.musicOn, sfxOn: save.data.settings.sfxOn, musicVol: save.data.settings.musicVol, sfxVol: save.data.settings.sfxVol });
  // sound can start only after a tap: the first one anywhere does it; every button also clicks softly
  const unlock = (): void => audio.unlock();
  window.addEventListener('pointerdown', unlock, { once: true, capture: true });
  window.addEventListener('keydown', unlock, { once: true, capture: true });
  document.addEventListener('click', (e) => { if ((e.target as HTMLElement | null)?.closest?.('button')) audio.sfx('click'); }, true);
  const quality = new QualityManager(save);
  const fpsMeter = new FpsMeter(hud.row);
  fpsMeter.show(save.data.settings.showFps);
  const head = new SkyHead();
  head.onSeen = () => bus.emit('head:seen', undefined);
  const joystick = new Joystick();
  let modal = true;
  const ctx: GameContext = {
    save, session, hud, dialogue, joystick, head, quality, art: new Set(),
    get modal() { return modal; },
    set modal(v: boolean) {
      modal = v;
      document.body.classList.toggle('modal', v);
    },
  };
  document.body.classList.add('modal');

  const game = new Phaser.Game({
    type: Phaser.AUTO,
    parent: 'game',
    backgroundColor: '#0d0f1f',
    scale: { mode: Phaser.Scale.RESIZE, width: window.innerWidth, height: window.innerHeight },
    render: { antialias: true, roundPixels: false },
    scene: [BootScene, WorldScene, HouseScene],
    callbacks: { preBoot: (g) => g.registry.set(CTX_KEY, ctx) },
  });
  // frame limit (30 on the lowest level) and the once-a-second watcher that can lower quality by itself
  const applyFpsLimit = (): void => {
    const loop = game.loop as unknown as { fpsLimit: number; hasFpsLimit: boolean; _limitRate: number; raf: { stop(): void; start(cb: (t: number) => void, f: boolean, d: number): void }; stepLimitFPS(t: number): void; step(t: number): void; forceSetTimeOut: boolean; _target: number; running: boolean };
    const limit = quality.profile.targetFps < 60 ? quality.profile.targetFps : 0;
    if (loop.fpsLimit === limit) return;
    loop.fpsLimit = limit;
    loop.hasFpsLimit = limit > 0;
    loop._limitRate = limit > 0 ? 1000 / limit : 0;
    if (loop.running && loop.raf) {
      loop.raf.stop();
      loop.raf.start(limit > 0 ? loop.stepLimitFPS.bind(loop) : loop.step.bind(loop), loop.forceSetTimeOut, loop._target);
    }
  };
  applyFpsLimit();
  quality.onChange(applyFpsLimit);
  quality.onAutoLowered = (to) => hud.toast(`המשחק מגמגם, אז הורדנו את האיכות ל${QUALITY_NAME[to]}. אפשר לשנות בהגדרות.`, 'clue', 5200);
  window.setInterval(() => {
    const fps = game.loop.actualFps;
    fpsMeter.set(fps, QUALITY_NAME[quality.level]);
    if (!ctx.modal && !document.hidden) quality.sample(fps);
  }, 1000);
  (ctx as unknown as { fpsMeter: FpsMeter }).fpsMeter = fpsMeter;
  const controller = new Controller(game, ctx);
  hud.setVisible(false);
  joystick.setVisible(false);
  (window as unknown as { __tq: unknown }).__tq = { game, ctx, bus };
  titleScreen(ctx, controller);
}

function titleScreen(ctx: GameContext, controller: Controller): void {
  const started = ctx.save.data.started;
  const start = (look?: Look): void => {
    if (look) ctx.save.data.look = look;
    ctx.dialogue.look = ctx.save.data.look;
    ctx.save.data.started = true;
    ctx.save.save();
    screen.remove();
    ctx.modal = false;
    ctx.hud.setVisible(true);
    ctx.joystick.setVisible(true);
    void controller.begin();
  };
  let chosen: Look | null = null;
  const nameInput = el('input', 'name-input');
  nameInput.maxLength = 12;
  nameInput.placeholder = 'איך קוראים לך?';
  nameInput.setAttribute('aria-label', 'שם');
  const go = el('button', 'btn primary', 'יוצאים לדרך');
  go.disabled = true;
  const sync = (): void => { go.disabled = !chosen || nameInput.value.trim().length === 0; };
  const girl = el('button', 'btn', 'בת');
  const boy = el('button', 'btn', 'בן');
  const pick = (l: Look): void => {
    chosen = l;
    girl.classList.toggle('on', l === 'girl');
    boy.classList.toggle('on', l === 'boy');
    sync();
  };
  girl.onclick = () => pick('girl');
  boy.onclick = () => pick('boy');
  nameInput.oninput = sync;
  go.onclick = () => {
    if (!chosen) return;
    ctx.save.data.name = nameInput.value.trim();
    start(chosen);
  };
  const cont = el('button', 'btn primary', 'המשך');
  cont.onclick = () => start();
  const screen = el('div', 'screen title', '', [
    el('div', '', '', [
      el('h1', '', 'שקט מדי'),
      el('div', 'sub', 'העמק נראה מושלם. כולם אומרים שהכול בסדר.'),
      started ? el('div', 'row', '', [cont]) : el('div', '', '', [el('p', '', 'מי מגיע לעמק?'), el('div', 'row', '', [girl, boy]), el('div', 'row name-row', '', [nameInput]), el('div', 'row', '', [go])]),
      el('p', 'sub', 'סקיצה לבדיקה. העיצוב והתוכן עדיין בעבודה.'),
    ]),
  ]);
  uiRoot().append(screen);
}

boot();
