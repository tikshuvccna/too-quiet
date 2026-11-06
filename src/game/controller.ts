import type Phaser from 'phaser';
import { WORLD_NPC_INFO, conversationFor } from '../content/world';
import { NPC_GAMES, openNpcGame } from '../ui/npcgames';
import { openShop } from '../ui/shop';
import { openSettings } from '../ui/settings';
import { perksOf } from './perks';
import { equippedSkin } from './skins';
import { audio } from '../audio/audio';
import { celebrate, type CelebrateKind } from '../ui/celebrate';
import { playCutscene } from '../ui/cutscene';
import { PROBLEMS, PROBLEM_COINS, objectiveFor, problemForNpc, stageOf, type Probe } from './problems';
import type { LessonTarget } from './lessonTarget';
import { CREATURES, HEAD_INFO, HOUSES, ITEMS_IN_OBJECT, LINES, SCENES, TEACHER_INTRO, itemById, lineOf, SPEAKER_NAMES } from '../content';
import { bus } from '../core/bus';
import { openCollection } from '../ui/collection';
import { bookFlag, inspectedFlag } from './houseBook';
import { el, uiRoot } from '../ui/dom';
import { BUILDINGS, TOWER_SPAWN } from '../world/layout';
import { WORLD_BUILDINGS } from '../world/worldMap';
import type { GameContext } from './context';
import { SceneRunner } from './sceneRunner';
import { afterInspect, useActivity } from '../ui/houseExtras';
import { showReveal } from '../ui/secretsUi';
import { hintFor, grantReward, parseTarget, press, secretById } from '../world/secrets';

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
    bus.on('session:notice', ({ left }) => this.onNotice(left));
    bus.on('session:storm', ({ n }) => this.onStormStart(n));
    bus.on('session:stormend', () => this.onStormEnd());
    bus.on('session:teleport', () => void this.storm());
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
        { id: 'boss.narrator.0001', speaker: '', text: 'הענן הענק יורד אל הכפר. החוטים בשמיים רועדים.' },
        { id: 'boss.narrator.0002', speaker: '', text: 'הוא לא נראה כועס. הוא נראה סקרן, והוא חותך חוטים.' },
        { id: 'boss.dvora.0003', speaker: 'dvora', text: 'המחט רואה אותם עכשיו. רוצו אל החוט החתוך, וחברו אותו נכון.' },
      ]);
    });
    await playCutscene('boss_intro');
    bus.emit('boss:start', undefined);
  }

  /** The fight is over (the world scene reports it). */
  private async bossEnded(won: boolean): Promise<void> {
    const ending: { pop: (() => void) | null } = { pop: null };
    await this.withModal(async () => {
      if (!won) {
        await this.ctx.dialogue.say([{ speaker: '', text: 'הראש מחכה בסבלנות. אפשר לקרוא לו שוב מתי שרוצים.' }]);
        return;
      }
      this.ctx.save.setFlag('head_calmed');
      this.ctx.save.save();
      ending.pop = audio.pushOverlay('ending');
      await playCutscene('ending');
      const { applyPrize, prizeFor } = await import('../ui/learning');
      const { bossData } = await import('../ui/learning/bossGame');
      const out = applyPrize(this.ctx.save, 'hard', { lessonId: 'lessonboss' });
      const prize = prizeFor('hard', bossData().prizes);
      await this.ctx.dialogue.say([
        { id: 'end.narrator.0001', speaker: '', text: 'הראש מרפה את אצבעותיו. החוטים יורדים בשקט, וכל אחד נקשר לבית שלו.' },
        { id: 'end.narrator.0002', speaker: '', text: 'הוא לא נעלם. הוא מביט, ושואל: מה עוד אפשר ללמוד?' },
        { id: 'end.narrator.0003', speaker: '', text: 'בעמק זמזום חדש. לא קול של הד: קול של רשת.' },
      ]);
      if (out.granted) this.ctx.hud.toast(`פרס: ${prize.name} (+${out.coins} מטבעות)`, 'good', 6000);
      this.ctx.hud.toast('סוף הסיפור הראשי. תודה ששיחקתם!', 'good', 7000);
    });
    ending.pop?.();
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
    const ph = this.ctx.session.phase;
    if (ph === 'warning' || ph === 'storm' || ph === 'grace') {
      const t = this.lessonDest();
      if (t) {
        this.ctx.hud.setObjective(this.ctx.session.safe ? `הגעתם. דברו עם ${t.teacher}.` : `הסערה מתקרבת! לכו אל ${t.teacher}: ${t.place}.`);
        return;
      }
    }
    const f = (n: string): boolean => this.has(n);
    let text = 'גלו את הכפר: בתים, אנשים, וחפצים שמחכים לאיסוף.';
    if (f('p1_complete')) {
      text = objectiveFor(this.probe())
        ?? (f('final_unlocked') && !f('head_calmed')
          ? 'הכול מתוקן, חוץ מהראש. לכו למגדל האורגים וקראו לו.'
          : 'סוף הדוגמית. נשארו עוד חפצים וסודות בכפר.');
    }
    else if (f('bakery_fixed')) text = 'לכו אל הגשר שעל הנחל והסתכלו על החוט.';
    else if (FIXES.every((x) => f(x.flag))) text = 'חזרו לנחתום במאפייה.';
    else if (this.lessonDone()) text = 'תקנו: בית סבתא שושנה, המרפאה והטחנה.';
    else if (f('needle_blur_seen') || f('neighbours_asked')) text = 'המחט מטושטשת. לכו למגדל האורגים כדי ללמוד.';
    else if (f('houses_unlocked')) text = 'מה קורה במאפייה? דברו עם הנחתום.';
    const secretHint = hintFor(this.ctx.save);
    if (secretHint && (text.startsWith('גלו את הכפר') || text.startsWith('סוף הדוגמית'))) text = `${text} ${secretHint}`;
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
    else if (id.startsWith('act:')) void this.withModal(() => useActivity(this.ctx, id.slice(4)));
    else if (id.startsWith('secret:')) void this.secretPress(id);
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
      // the house book: meeting an owner outdoors adds the house card
      const bookId = wn?.house ?? ({ baker: 'bakery', miller: 'mill', dvora: 'tower' } as Record<string, string>)[npcId];
      if (!wn) save.setFlag(`met_${npcId}`);
      if (bookId) this.markBook(bookId);
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
          // the NPC of the problem teaches this lesson: two short lines, then the lesson menu
          const intro = TEACHER_INTRO[problem.lesson];
          if (intro) {
            await this.ctx.dialogue.say(intro.lines.map((id) => ({ id, speaker: lineOf(id).speaker, text: lineOf(id).text })));
            this.ctx.dialogue.close();
          }
          await this.classroom({ only: problem.lesson, teacher: problem.teacher });
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
                void (this.scene().get('World') as unknown as { applySkin?: () => Promise<void> } | null)?.applySkin?.();
                this.ctx.dialogue.playerSheet = equippedSkin(save)?.id ?? null;
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

  /** Adds a house to the house book (once) with a small toast. */
  private markBook(infoId: string): void {
    if (this.has(bookFlag(infoId))) return;
    this.ctx.save.setFlag(bookFlag(infoId));
    this.ctx.save.save();
    this.ctx.hud.toast('נוסף לספר הבתים', 'good');
  }

  async tower(): Promise<void> {
    this.markBook('tower');
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
  private async classroom(opts: { only?: string; teacher?: string } = {}): Promise<void> {
    const { openClassroom } = await import('./learningBridge');
    const doneBefore = ['lesson01', 'lesson02', 'lesson03', 'lesson04', 'lesson05'].filter((id) => this.ctx.save.lesson(id).done).length;
    await openClassroom(this.ctx, async () => {
      if (!opts.only && this.lessonDone() && !this.has('lesson01_done')) await this.runScene('return_after_lesson');
    }, opts);
    const doneAfter = ['lesson01', 'lesson02', 'lesson03', 'lesson04', 'lesson05'].filter((id) => this.ctx.save.lesson(id).done).length;
    // a finished lesson gives a fresh stretch of roaming time
    if (doneAfter > doneBefore) this.ctx.session.restart();
    this.refreshObjective();
  }

  private async inspect(id: string): Promise<void> {
    const [, houseId, objId] = id.split(':') as [string, string, string];
    const house = HOUSES.find((h) => h.id === houseId);
    const obj = house?.objects.find((o) => o.id === objId);
    if (!house || !obj) return;
    this.ctx.save.setFlag(inspectedFlag(houseId, objId));
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
      await afterInspect(this.ctx, houseId, objId);
    });
  }

  /** A glowing marker of a secret sequence was pressed. Wrong order: gentle reset. Right order: reveal and a fixed prize. */
  private async secretPress(id: string): Promise<void> {
    const t = parseTarget(id);
    const def = t ? secretById(t.secretId) : undefined;
    if (!t || !def || this.has(`secret.${def.id}.solved`)) return;
    const node = def.nodes.find((n) => n.id === t.nodeId);
    if (!node) return;
    const r = press(def, t.nodeId);
    if (r === 'ok') {
      audio.sfx('pop');
      return;
    }
    if (r === 'wrong') {
      audio.sfx('fail');
      this.ctx.hud.toast(def.wrongHint, 'clue', 3400);
      return;
    }
    const prize = grantReward(this.ctx.save, def, perksOf(this.ctx.save).coinMul);
    this.refreshObjective();
    if (!prize) return;
    await this.withModal(() => showReveal(def, prize));
    this.refreshObjective();
  }

  private async onHouseEntered(contentHouseId: string): Promise<void> {
    this.markBook(contentHouseId);
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

  /** The next lesson to take and where it waits (null when no lesson is open: then the clouds only gather). */
  private lessonDest(): (LessonTarget & { x: number; y: number }) | null {
    return (this.scene().get('World') as unknown as { lessonDestination?: () => (LessonTarget & { x: number; y: number }) | null } | null)?.lessonDestination?.() ?? null;
  }

  private async onWarning(): Promise<void> {
    const t = this.lessonDest();
    this.refreshObjective();
    if (!t) {
      this.ctx.hud.toast('העננים מתכנסים. אפשר להמשיך לשוטט.', 'clue', 5000);
      return;
    }
    if (!this.has('storm_warned') && t.targetId === 'door:tower') {
      await this.withModal(() => this.runScene('thread_storm_warning'));
    }
    this.ctx.hud.toast(`הענן מתכנס! בעוד שתי דקות סערה. לכו אל ${t.teacher} ב${t.place}. החץ מראה את הדרך.`, 'clue', 7000);
  }

  private onNotice(left: number): void {
    const t = this.lessonDest();
    if (!t || this.ctx.session.safe) return;
    this.ctx.hud.toast(left >= 60 ? `עוד דקה לסערה! מהרו אל ${t.teacher}.` : `עוד ${left} שניות! ${t.teacher} מחכה.`, 'clue', 4500);
    audio.sfx('warn');
  }

  private onStormStart(n: number): void {
    const t = this.lessonDest();
    if (!t) {
      this.ctx.session.restart();
      this.refreshObjective();
      return;
    }
    this.refreshObjective();
    audio.sfx('warn');
    this.ctx.hud.toast(n === 1 ? 'הענן משתגע! הסערה מסובבת אתכם.' : `הענן משתגע שוב! אם לא תגיעו אל ${t.teacher}, הסערה תסחוף אתכם לשם.`, 'clue', 5000);
  }

  private onStormEnd(): void {
    const t = this.lessonDest();
    if (!t || this.ctx.session.safe) return;
    this.ctx.hud.toast(`הסערה שככה. יש לכם דקה להגיע אל ${t.teacher}.`, 'clue', 5200);
  }

  /** The third trigger: the storm carries the player to the door of the next lesson. */
  private async storm(): Promise<void> {
    const t = this.lessonDest();
    if (!t) {
      this.ctx.session.restart();
      this.refreshObjective();
      return;
    }
    this.busy = true;
    this.ctx.modal = true;
    this.ctx.dialogue.close();
    const msg = el('div', 'msg', `סערת חוטים! הרוח סוחפת אתכם אל ${t.teacher}…`);
    const screen = el('div', 'screen storm', '', [msg]);
    uiRoot().append(screen);
    requestAnimationFrame(() => screen.classList.add('on'));
    await new Promise((r) => setTimeout(r, 3400));
    this.scene().start('World', { spawn: { x: t.x, y: t.y + 90 } });
    this.ctx.session.restart();
    screen.classList.remove('on');
    await new Promise((r) => setTimeout(r, 1300));
    screen.remove();
    this.busy = false;
    this.ctx.modal = false;
    this.refreshObjective();
    this.ctx.hud.toast(`הגעתם אל ${t.place}. ${t.teacher} מחכה.`, 'clue', 5200);
    void LINES;
    void SPEAKER_NAMES;
  }
}
