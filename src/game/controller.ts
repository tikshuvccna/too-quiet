import type Phaser from 'phaser';
import { WORLD_NPC_INFO, conversationFor } from '../content/world';
import { NPC_GAMES, openNpcGame } from '../ui/npcgames';
import { openShop } from '../ui/shop';
import { openSettings } from '../ui/settings';
import { perksOf } from './perks';
import { audio } from '../audio/audio';
import { celebrate, type CelebrateKind } from '../ui/celebrate';
import { playCutscene } from '../ui/cutscene';
import { PROBLEMS, PROBLEM_COINS, objectiveFor, problemForNpc, stageOf, type Probe } from './problems';
import { CREATURES, HEAD_INFO, HOUSES, ITEMS_IN_OBJECT, LINES, SCENES, itemById, lineOf, SPEAKER_NAMES } from '../content';
import { bus } from '../core/bus';
import { openCollection } from '../ui/collection';
import { el, uiRoot } from '../ui/dom';
import { BUILDINGS, TOWER_SPAWN } from '../world/layout';
import { WORLD_BUILDINGS } from '../world/worldMap';
import type { GameContext } from './context';
import { SceneRunner } from './sceneRunner';

const FIXES: Array<{ flag: string; scene: string }> = [
  { flag: 'fix_grandma_done', scene: 'fix_grandma' },
  { flag: 'fix_clinic_done', scene: 'fix_clinic' },
  { flag: 'fix_mill_done', scene: 'fix_mill' },
];

/** Glue between the Phaser scenes and the DOM screens: houses, the story, the storm teleport. */
export class Controller {
  private readonly runner: SceneRunner;
  private barkIndex = new Map<string, number>();
  private busy = false;
  private pendingClassroom = false;

  constructor(private readonly game: Phaser.Game, private readonly ctx: GameContext) {
    this.runner = new SceneRunner(ctx.dialogue, ctx.save, {
      toTower: () => this.teleportToTower(),
      onFlag: (name) => {
        if (name === 'start_lesson01') this.pendingClassroom = true;
        // the prologue ends with meeting Grandpa Hed: remember it at once, so a reload does not replay it
        if (name === 'met_hubGrandpa') this.ctx.save.setFlag('prologue_done');
        const done = PROBLEMS.find((p) => p.complete === name);
        if (done) this.problemSolved(done.n);
        if (name === 'p5_complete' && !this.has('final_unlocked')) {
          this.ctx.save.setFlag('final_unlocked');
          this.ctx.hud.toast('הדרך אל הצריח הגדול נפתחה. בצד המזרחי של העמק.', 'clue', 6000);
        }
        this.refreshObjective();
      },
    });
    bus.on('world:enter-house', ({ houseId }) => this.enterHouse(houseId));
    bus.on('world:exit-house', ({ houseId }) => this.exitHouse(houseId));
    bus.on('house:entered', ({ houseId }) => void this.onHouseEntered(houseId));
    bus.on('session:warning', () => void this.onWarning());
    bus.on('session:storm', () => void this.storm());
    bus.on('fault:fixed', ({ evidence }) => this.faultFixed(evidence));
    bus.on('item:collected', ({ id }) => void this.onCollected(id));
    bus.on('creature:met', ({ key }) => void this.meetCreature(key));
    bus.on('sight:toggle', ({ on }) => {
      if (!on || this.has('first_sight') || this.ctx.save.data.started === false) return;
      this.ctx.save.setFlag('first_sight');
      void this.withModal(() => celebrate('sight', true));
    });
    bus.on('boss:end', ({ won }) => void this.bossEnded(won));
    bus.on('head:seen', () => {
      // unlocked quietly: the player is not told what they saw
      ctx.save.data.collected['creature_the_head'] = true;
      ctx.save.save();
    });
    bus.on('interact:use', ({ id }) => this.onUse(id));
    ctx.hud.onCollection = () => void this.collection();
    ctx.hud.onSettings = () => {
      if (this.ctx.modal) return;
      this.ctx.modal = true;
      this.ctx.session.pause();
      openSettings(this.ctx.save, this.ctx.quality, {
        onChange: () => (this.ctx as unknown as { fpsMeter?: { show(on: boolean): void } }).fpsMeter?.show(this.ctx.save.data.settings.showFps),
        onClose: () => {
          this.ctx.dialogue.subtitles = this.ctx.save.data.settings.subtitles;
          this.ctx.modal = false;
          this.ctx.session.resume();
        },
      });
    };
    this.refreshObjective();
  }

  /** Called once the player leaves the title screen. */
  async begin(): Promise<void> {
    if (!this.ctx.save.hasFlag('prologue_done')) {
      await this.withModal(async () => {
        // the prologue continues into village_meet by itself
        await this.runScene('prologue');
        this.ctx.save.setFlag('prologue_done');
      });
    }
    this.refreshObjective();
  }

  /** Plays a scene; if it ended with "start the lesson", opens the classroom. */
  private async runScene(id: string): Promise<void> {
    await this.runner.run(id);
    if (this.pendingClassroom) {
      this.pendingClassroom = false;
      await this.classroom();
    }
  }

  // ---- state helpers ----

  private has(flag: string): boolean {
    return this.ctx.save.hasFlag(flag);
  }

  /** The end of the whole game: the Head comes down over the village, and the apprentice mends the web with the thread-sight. */
  private async faceTheHead(): Promise<void> {
    if (this.has('head_calmed')) return;
    await this.withModal(async () => {
      await this.ctx.dialogue.say([
        { speaker: '', text: 'הענן הענק יורד אל הכפר. החוטים בשמיים רועדים.' },
        { speaker: '', text: 'הוא לא נראה כועס. הוא נראה סקרן, והוא חותך חוטים.' },
        { speaker: 'dvora', text: 'המחט רואה אותם עכשיו. רוצו אל החוט החתוך, וחברו אותו נכון.' },
      ]);
    });
    await playCutscene('boss_intro');
    bus.emit('boss:start', undefined);
  }

  /** The fight is over (the world scene reports it). */
  private async bossEnded(won: boolean): Promise<void> {
    await this.withModal(async () => {
      if (!won) {
        await this.ctx.dialogue.say([{ speaker: '', text: 'הראש מחכה בסבלנות. אפשר לקרוא לו שוב מתי שרוצים.' }]);
        return;
      }
      this.ctx.save.setFlag('head_calmed');
      this.ctx.save.save();
      await playCutscene('ending');
      const { applyPrize, prizeFor } = await import('../ui/learning');
      const { bossData } = await import('../ui/learning/bossGame');
      const out = applyPrize(this.ctx.save, 'hard', { lessonId: 'lessonboss' });
      const prize = prizeFor('hard', bossData().prizes);
      await this.ctx.dialogue.say([
        { speaker: '', text: 'הראש מרפה את אצבעותיו. החוטים יורדים בשקט, וכל אחד נקשר לבית שלו.' },
        { speaker: '', text: 'הוא לא נעלם. הוא מביט, ושואל: מה עוד אפשר ללמוד?' },
        { speaker: '', text: 'בעמק זמזום חדש. לא קול של הד: קול של רשת.' },
      ]);
      if (out.granted) this.ctx.hud.toast(`פרס: ${prize.name} (+${out.coins} מטבעות)`, 'good', 6000);
      this.ctx.hud.toast('סוף הסיפור הראשי. תודה ששיחקתם!', 'good', 7000);
    });
    this.refreshObjective();
  }

  private probe(): Probe {
    return {
      has: (f) => this.has(f),
      lessonDone: (id) => this.ctx.save.lesson(id).done,
      hasScene: (id) => !!SCENES[id],
    };
  }

  /** A later problem was mended: a fixed reward and a short note. */
  private problemSolved(n: number): void {
    if (this.has(`p${n}_rewarded`)) return;
    this.ctx.save.setFlag(`p${n}_rewarded`);
    this.ctx.save.data.coins += PROBLEM_COINS;
    this.ctx.save.save();
    this.ctx.hud.toast(`הבעיה נפתרה! +${PROBLEM_COINS} מטבעות`, 'good', 4200);
  }

  private lessonDone(): boolean {
    return this.ctx.save.lesson('lesson01').done;
  }

  refreshObjective(): void {
    const f = (n: string): boolean => this.has(n);
    let text = 'גלו את הכפר: בתים, אנשים, וחפצים שמחכים לאיסוף.';
    if (f('p1_complete')) text = objectiveFor(this.probe()) ?? 'סוף הדוגמית. נשארו עוד חפצים וסודות בכפר.';
    else if (f('bakery_fixed')) text = 'לכו אל הגשר שעל הנחל והסתכלו על החוט.';
    else if (FIXES.every((x) => f(x.flag))) text = 'חזרו לנחתום במאפייה.';
    else if (this.lessonDone()) text = 'תקנו: בית סבתא שושנה, המרפאה והטחנה.';
    else if (f('needle_blur_seen') || f('neighbours_asked')) text = 'המחט מטושטשת. לכו למגדל האורגים כדי ללמוד.';
    else if (f('houses_unlocked')) text = 'מה קורה במאפייה? דברו עם הנחתום.';
    this.ctx.hud.setObjective(text);
  }

  // ---- scenes and movement ----

  private scene(): Phaser.Scenes.ScenePlugin {
    return this.game.scene.getScenes(true)[0]!.scene;
  }

  private fade(then: () => void): void {
    const cam = this.game.scene.getScenes(true)[0]?.cameras.main;
    if (!cam) return then();
    cam.fadeOut(260, 8, 9, 20);
    cam.once('camerafadeoutcomplete', then);
  }

  /** Start a scene and fade it in once it has been created (a scene's camera does not exist before that). */
  private startScene(key: string, data: object, fadeMs = 260): void {
    const target = this.game.scene.getScene(key);
    target.events.once('create', () => target.cameras.main.fadeIn(fadeMs, 8, 9, 20));
    this.scene().start(key, data);
  }

  private enterHouse(houseId: string): void {
    if (this.ctx.modal) return;
    audio.sfx('door');
    this.ctx.modal = true;
    this.fade(() => {
      this.ctx.modal = false;
      this.startScene('House', { houseId });
    });
  }

  private exitHouse(houseId: string): void {
    if (this.ctx.modal) return;
    audio.sfx('door');
    const b = BUILDINGS.find((x) => x.id === houseId) ?? WORLD_BUILDINGS.find((x) => `house-${x.id}` === houseId);
    this.ctx.modal = true;
    this.fade(() => {
      this.ctx.modal = false;
      this.startScene('World', { spawn: b ? { x: b.door.x, y: b.door.y + 70 } : undefined });
    });
  }

  /** Fade to the tower. Resolves when the world is back; `modal` stays as the caller left it. */
  private teleportToTower(): Promise<void> {
    return new Promise((resolve) => {
      this.fade(() => {
        this.startScene('World', { spawn: TOWER_SPAWN }, 400);
        window.setTimeout(resolve, 550);
      });
    });
  }

  // ---- interaction ----

  private onUse(id: string): void {
    if (this.ctx.modal || this.busy) return;
    if (id.startsWith('npc:')) void this.talk(id.slice(4));
    else if (id === 'boss:head') void this.faceTheHead();
    else if (id === 'door:tower') void this.tower();
    else if (id === 'spot:sky') void this.meetCreature('cloud_whale');
    else if (id === 'spot:bridge') void this.withModal(async () => {
      await this.runScene('ending_clue');
      this.refreshObjective();
    });
    else if (id.startsWith('obj:')) void this.inspect(id);
  }

  private async withModal(fn: () => Promise<void>): Promise<void> {
    if (this.busy) return;
    this.busy = true;
    this.ctx.modal = true;
    this.ctx.session.pause();
    try {
      await fn();
    } finally {
      this.ctx.dialogue.close();
      this.ctx.modal = false;
      this.ctx.session.resume();
      this.busy = false;
    }
  }

  private nextBark(speaker: string): string | null {
    const steps = SCENES.village_idle_barks?.steps ?? [];
    const ids = steps.flatMap((s) => ('line' in s && lineOf(s.line).speaker === speaker ? [s.line] : []));
    if (!ids.length) return null;
    const i = this.barkIndex.get(speaker) ?? 0;
    this.barkIndex.set(speaker, i + 1);
    return ids[i % ids.length] as string;
  }

  async talk(npcId: string): Promise<void> {
    const save = this.ctx.save;
    await this.withModal(async () => {
      const wn = WORLD_NPC_INFO.find((n) => n.id === npcId);
      const problem = problemForNpc(npcId);
      if (problem) {
        const stage = stageOf(problem, this.probe());
        if (stage === 'chaos') {
          await this.runScene(problem.chaos);
          save.setFlag(problem.seen);
          save.save();
          this.refreshObjective();
          return;
        }
        if (stage === 'fix') {
          await this.runScene(problem.fix);
          this.refreshObjective();
          return;
        }
        if (stage === 'learn') {
          await this.ctx.dialogue.say([{ speaker: '', text: `המחט עוד מטושטשת. כדאי ללמוד קודם אצל דבורה (שיעור ${problem.n}).` }]);
          this.refreshObjective();
          return;
        }
      }
      if (wn) {
        const key = `met_${wn.id}`;
        const ids = conversationFor(wn, save.hasFlag(key) ? 'later' : 'first');
        save.setFlag(key);
        save.save();
        if (ids.length) {
          await this.ctx.dialogue.say(ids.map((id) => ({ id, speaker: lineOf(id).speaker, text: lineOf(id).text.split('{name}').join(save.data.name || 'אורח') })));
        } else await this.ctx.dialogue.say([{ speaker: wn.speaker, text: '...' }]);
        if (wn.id === 'npc_tailor') {
          this.ctx.dialogue.close();
          const go = await this.ctx.dialogue.choose({ speaker: wn.speaker, text: 'רוצים להסתכל בחנות?' }, [
            { text: 'כן, לראות', value: 'yes' },
            { text: 'אולי אחר כך', value: 'no' },
          ]);
          if (go === 'yes') {
            await openShop(save, {
              onChange: () => {
                this.ctx.session.bonus = perksOf(save).timeBonus;
                (this.scene().get('World') as unknown as { applyAura?: () => void } | null)?.applyAura?.();
              },
            });
          }
          return;
        }
        const game = NPC_GAMES[wn.id];
        if (game) {
          this.ctx.dialogue.close();
          const yes = await this.ctx.dialogue.choose({ speaker: wn.speaker, text: `רוצים לשחק ב"${game.title}"?` }, [
            { text: 'כן, בואו', value: 'yes' },
            { text: 'אולי אחר כך', value: 'no' },
          ]);
          if (yes === 'yes') await openNpcGame(game, save, false);
        }
        return;
      }
      if (npcId === 'dvora') return this.towerFlow();
      if (npcId === 'baker') {
        if (FIXES.every((x) => this.has(x.flag)) && !this.has('bakery_fixed')) return this.runScene('bakery_fixed');
        if (!this.lessonDone() && !this.has('needle_blur_seen') && !this.has('neighbours_asked')) return this.runScene('bakery_chaos');
      }
      if (npcId === 'miller' && this.lessonDone() && !this.has('fix_mill_done')) return this.runScene('fix_mill');
      const id = this.nextBark(npcId === 'villager2' || npcId === 'villager3' ? npcId : npcId);
      const line = id ? lineOf(id) : null;
      if (line) await this.ctx.dialogue.say([{ id: id ?? undefined, speaker: line.speaker, text: line.text }]);
      else await this.ctx.dialogue.say([{ speaker: npcId, text: '…' }]);
      void save;
    });
    this.refreshObjective();
  }

  async tower(): Promise<void> {
    await this.withModal(() => this.towerFlow());
    this.refreshObjective();
  }

  /** In the tower: first the story, then the classroom menu (lesson, quiz, mini-game). */
  private async towerFlow(): Promise<void> {
    if (!this.has('start_lesson01')) {
      await this.runScene('tower_dvora');
      return;
    }
    await this.classroom();
  }

  /** Classroom menu: lesson, quiz, mini-game. Wired to the learning screens in `learningBridge`. */
  private async classroom(): Promise<void> {
    const { openClassroom } = await import('./learningBridge');
    await openClassroom(this.ctx, async () => {
      if (this.lessonDone() && !this.has('lesson01_done')) await this.runScene('return_after_lesson');
    });
    this.refreshObjective();
  }

  private async inspect(id: string): Promise<void> {
    const [, houseId, objId] = id.split(':') as [string, string, string];
    const house = HOUSES.find((h) => h.id === houseId);
    const obj = house?.objects.find((o) => o.id === objId);
    if (!house || !obj) return;
    await this.withModal(async () => {
      await this.ctx.dialogue.say([{ speaker: '', text: `${obj.name}: ${obj.text}` }]);
      const items = ITEMS_IN_OBJECT[`${houseId}:${objId}`] ?? [];
      for (const itemId of items) {
        if (this.ctx.save.data.collected[itemId]) continue;
        this.ctx.save.data.collected[itemId] = true;
        this.ctx.save.save();
        const item = itemById(itemId);
        if (item) {
          this.ctx.hud.toast(`נמצא: ${item.title}`, 'good', 4200);
          await this.ctx.dialogue.say([{ speaker: '', text: `${item.title}. ${item.text}` }]);
        }
      }
    });
  }

  private async onHouseEntered(contentHouseId: string): Promise<void> {
    if (!this.has('first_house')) {
      this.ctx.save.setFlag('first_house');
      await this.withModal(() => celebrate('house', true));
    }
    if (!this.lessonDone()) return;
    const fix = { house_grandma: FIXES[0], house_clinic: FIXES[1] }[contentHouseId as 'house_grandma' | 'house_clinic'];
    if (!fix || this.has(fix.flag)) return;
    await this.withModal(async () => {
      await this.runScene(fix.scene);
      const house = HOUSES.find((h) => h.id === contentHouseId);
      if (house?.threadSightClue) this.ctx.hud.toast('המחט מראה משהו חדש בבית הזה. (ראיית חוטים: Q)', 'clue', 5200);
    });
    this.refreshObjective();
  }

  private async meetCreature(key: string): Promise<void> {
    const info = key === 'the_head' ? HEAD_INFO : CREATURES[key];
    if (!info) return;
    const first = !this.ctx.save.data.collected[`creature_${key}`];
    await this.withModal(async () => {
      this.ctx.save.data.collected[`creature_${key}`] = true;
      this.ctx.save.save();
      audio.sfx('creature');
      if (first) {
        const firstEver = !this.has('first_creature');
        this.ctx.save.setFlag('first_creature');
        await celebrate('creature', firstEver, info.name_he);
      }
      const lines = [{ speaker: '', text: `${info.name_he}. ${info.concept_he}` }];
      if (info.legend_he) lines.unshift({ speaker: '', text: info.legend_he });
      await this.ctx.dialogue.say(lines);
      if (first) this.ctx.hud.toast(`נוסף לאוסף: ${info.name_he}`, 'good', 3600);
      await this.offerFood(key, info.name_he, info.legendary);
    });
  }

  /** Any creature food will do: fixed and simple. A fed creature becomes a friend and follows the player. */
  private async offerFood(key: string, name: string, legendary: boolean): Promise<void> {
    const save = this.ctx.save;
    const foods = Object.entries(save.data.inv).filter(([, n]) => n > 0);
    const flag = `friend_${key}`;
    if (legendary || key === 'the_head' || save.data.collected[flag] || !foods.length) return;
    this.ctx.dialogue.close();
    const yes = await this.ctx.dialogue.choose({ speaker: '', text: `להאכיל את ${name}? (יש לכם אוכל ליצורים)` }, [
      { text: 'כן, בעדינות', value: 'yes' },
      { text: 'לא עכשיו', value: 'no' },
    ]);
    if (yes !== 'yes') return;
    const [food] = foods[0] as [string, number];
    save.data.inv[food] = (save.data.inv[food] ?? 1) - 1;
    save.data.collected[flag] = true;
    save.save();
    (this.scene().get('World') as unknown as { refreshFriends?: () => void } | null)?.refreshFriends?.();
    this.ctx.hud.toast(`${name} התיידד איתכם ויתלווה אליכם`, 'good', 4200);
  }

  private async onCollected(id: string): Promise<void> {
    const item = itemById(id);
    if (!item) return;
    this.ctx.hud.toast(`נאסף: ${item.title}`, 'good', 3600);
    audio.sfx(item.kind === 'diary' ? 'diary' : 'pickup');
    const kind: CelebrateKind = item.kind;
    const first = !this.has(`first_${kind}`);
    this.ctx.save.setFlag(`first_${kind}`);
    await this.withModal(async () => {
      await celebrate(kind, first, item.title);
      await this.ctx.dialogue.say([{ speaker: '', text: `${item.title}. ${item.text}` }]);
    });
  }

  private async collection(): Promise<void> {
    if (this.ctx.modal) return;
    this.ctx.modal = true;
    this.ctx.session.pause();
    openCollection(this.ctx.save, () => {
      this.ctx.modal = false;
      this.ctx.session.resume();
    });
  }

  private faultFixed(evidence: 'natural' | 'hand'): void {
    const text = evidence === 'hand' ? 'ראיה: יד אדם. חיתוך נקי וקשר של אורג בשני סיבובים.' : 'ראיה: תקלה טבעית.';
    this.ctx.hud.toast('החוט תוקן', 'good');
    this.ctx.hud.toast(text, 'clue', 5200);
  }

  private async onWarning(): Promise<void> {
    if (this.has('storm_warned')) {
      this.ctx.hud.toast('העננים מתכנסים… סערת חוטים בקרוב.', 'clue', 6000);
      return;
    }
    await this.withModal(() => this.runScene('thread_storm_warning'));
  }

  private async storm(): Promise<void> {
    this.busy = true;
    this.ctx.modal = true;
    this.ctx.dialogue.close();
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
    this.busy = false;
    this.ctx.modal = false;
    this.ctx.hud.toast('הגעתם למגדל האורגים. דבורה מחכה.', 'clue');
    void LINES;
    void SPEAKER_NAMES;
    const { lessonIds } = await import('../ui/learning');
    if (lessonIds().some((id) => !this.ctx.save.lesson(id).done)) await this.tower();
  }
}
