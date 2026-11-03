import Phaser from 'phaser';
import './styles.css';
import { bus } from './core/bus';
import { Session } from './core/session';
import { SaveStore, type Look } from './core/save';
import { CTX_KEY, type GameContext } from './game/context';
import { Controller } from './game/controller';
import { BootScene } from './scenes/BootScene';
import { HouseScene } from './scenes/HouseScene';
import { WorldScene } from './scenes/WorldScene';
import { DialogueUI } from './ui/dialogue';
import { el, uiRoot } from './ui/dom';
import { Hud } from './ui/hud';
import { Joystick } from './ui/joystick';

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
  const hud = new Hud();
  const dialogue = new DialogueUI();
  dialogue.subtitles = save.data.settings.subtitles;
  const joystick = new Joystick();
  const ctx: GameContext = { save, session, hud, dialogue, joystick, art: new Set(), modal: true };

  const game = new Phaser.Game({
    type: Phaser.AUTO,
    parent: 'game',
    backgroundColor: '#0d0f1f',
    scale: { mode: Phaser.Scale.RESIZE, width: window.innerWidth, height: window.innerHeight },
    render: { antialias: true, roundPixels: false },
    scene: [BootScene, WorldScene, HouseScene],
    callbacks: { preBoot: (g) => g.registry.set(CTX_KEY, ctx) },
  });
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
    ctx.save.data.started = true;
    ctx.save.save();
    screen.remove();
    ctx.modal = false;
    ctx.hud.setVisible(true);
    ctx.joystick.setVisible(true);
    void controller.begin();
  };
  const girl = el('button', 'btn primary', 'מתלמדת');
  const boy = el('button', 'btn primary', 'מתלמד');
  girl.onclick = () => start('girl');
  boy.onclick = () => start('boy');
  const cont = el('button', 'btn primary', 'המשך');
  cont.onclick = () => start();
  const screen = el('div', 'screen title', '', [
    el('div', '', '', [
      el('h1', '', 'שקט מדי'),
      el('div', 'sub', 'העמק נראה מושלם. כולם אומרים שהכול בסדר.'),
      started ? el('div', 'row', '', [cont]) : el('div', '', '', [el('p', '', 'מי מגיע לעמק?'), el('div', 'row', '', [girl, boy])]),
      el('p', 'sub', 'סקיצה לבדיקה. העיצוב והתוכן עדיין בעבודה.'),
    ]),
  ]);
  uiRoot().append(screen);
}

boot();
