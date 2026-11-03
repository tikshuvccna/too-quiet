import type Phaser from 'phaser';
import { bus } from '../core/bus';
import { el, uiRoot } from '../ui/dom';
import type { GameContext } from './context';
import { BUILDINGS, TOWER_SPAWN } from '../world/layout';

/** Glue between the Phaser scenes and the DOM screens: houses, the storm teleport, dialogue, lessons. */
export class Controller {
  constructor(private readonly game: Phaser.Game, private readonly ctx: GameContext) {
    bus.on('world:enter-house', ({ houseId }) => this.enterHouse(houseId));
    bus.on('world:exit-house', ({ houseId }) => this.exitHouse(houseId));
    bus.on('session:warning', () => ctx.hud.toast('העננים מתכנסים… סערת חוטים בעוד כמה דקות.', 'clue', 6000));
    bus.on('session:storm', () => void this.storm());
    bus.on('fault:fixed', ({ id, evidence }) => this.faultFixed(id, evidence));
    bus.on('interact:use', ({ id }) => this.onUse(id));
  }

  private scene(): Phaser.Scenes.ScenePlugin {
    return this.game.scene.getScenes(true)[0]!.scene;
  }

  private fade(then: () => void): void {
    const cam = this.game.scene.getScenes(true)[0]?.cameras.main;
    if (!cam) return then();
    cam.fadeOut(260, 8, 9, 20);
    cam.once('camerafadeoutcomplete', then);
  }

  private enterHouse(houseId: string): void {
    this.ctx.modal = true;
    this.fade(() => {
      this.ctx.modal = false;
      this.scene().start('House', { houseId });
      this.game.scene.getScene('House').cameras.main.fadeIn(260, 8, 9, 20);
    });
  }

  private exitHouse(houseId: string): void {
    const b = BUILDINGS.find((x) => x.id === houseId);
    this.ctx.modal = true;
    this.fade(() => {
      this.ctx.modal = false;
      this.scene().start('World', { spawn: b ? { x: b.door.x, y: b.door.y + 70 } : undefined });
    });
  }

  private onUse(id: string): void {
    if (this.ctx.modal) return;
    if (id.startsWith('npc:')) void this.talk(id.slice(4));
    else if (id === 'door:tower') void this.tower();
    else if (id.startsWith('obj:')) void this.inspect(id);
  }

  private async withModal(fn: () => Promise<void>): Promise<void> {
    this.ctx.modal = true;
    this.ctx.session.pause();
    try {
      await fn();
    } finally {
      this.ctx.modal = false;
      this.ctx.session.resume();
    }
  }

  async talk(npcId: string): Promise<void> {
    await this.withModal(() => this.ctx.dialogue.say([{ speaker: npcId, text: '(השיחה הזו עוד בבנייה.)' }]));
  }

  async tower(): Promise<void> {
    await this.withModal(() => this.ctx.dialogue.say([{ speaker: 'dvora', text: '(הכיתה בבנייה.)' }]));
  }

  async inspect(id: string): Promise<void> {
    await this.withModal(() => this.ctx.dialogue.say([{ speaker: '', text: `(${id})` }]));
  }

  private faultFixed(id: string, evidence: 'natural' | 'hand'): void {
    const text = evidence === 'hand' ? 'ראיה: יד אדם. חיתוך נקי וקשר של אורג בשני סיבובים.' : 'ראיה: תקלה טבעית.';
    this.ctx.hud.toast('החוט תוקן', 'good');
    this.ctx.hud.toast(text, 'clue', 5200);
    void id;
  }

  private async storm(): Promise<void> {
    this.ctx.modal = true;
    const msg = el('div', 'msg', 'סערת חוטים! הרוח מוליכה אתכם אל מגדל האורגים…');
    const screen = el('div', 'screen storm', '', [msg]);
    uiRoot().append(screen);
    requestAnimationFrame(() => screen.classList.add('on'));
    await new Promise((r) => setTimeout(r, 3400));
    this.scene().start('World', { spawn: TOWER_SPAWN });
    this.ctx.session.restart();
    screen.classList.remove('on');
    await new Promise((r) => setTimeout(r, 1300));
    screen.remove();
    this.ctx.modal = false;
    this.ctx.hud.toast('הגעתם למגדל האורגים. דבורה מחכה.', 'clue');
  }
}
