import { SCENES, SPEAKER_NAMES, lineOf, type SceneDef } from '../content';
import { bus } from '../core/bus';
import type { SaveStore } from '../core/save';
import type { DialogueUI } from '../ui/dialogue';
import { el, uiRoot } from '../ui/dom';
import { playCutscene } from '../ui/cutscene';

/** After these scenes the story waits for the player to go somewhere, instead of following `next`. */
export const STOP_AFTER = new Set(['village_houses', 'return_after_lesson', 'fix_grandma_ok', 'fix_clinic_ok', 'fix_mill_ok', 'bakery_fixed']);

export interface RunnerHooks {
  /** Called when the story has to continue in the Weavers' Tower (teleport first). */
  toTower(): Promise<void>;
  onFlag?(name: string): void;
}

/** Fix-it questions have one right option leading to a scene named "..._ok": its place is mixed so it is not always first. */
function shuffleIfQuiz<T extends { goto: string }>(options: T[]): T[] {
  if (!options.some((o) => /_ok$/.test(o.goto))) return options;
  const a = [...options];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j] as T, a[i] as T];
  }
  return a;
}

/** Plays a scene from scenes.json: lines, choices that jump to other scenes, flags and cutscene cards. */
export class SceneRunner {
  private catchphrases = 0;

  constructor(
    private readonly dialogue: DialogueUI,
    private readonly save: SaveStore,
    private readonly hooks: RunnerHooks,
  ) {
    dialogue.names = { ...SPEAKER_NAMES, player: save.data.name || SPEAKER_NAMES.player || 'אני' };
  }

  async run(sceneId: string): Promise<void> {
    let id: string | undefined = sceneId;
    let guard = 0;
    while (id && guard++ < 40) {
      const scene: SceneDef | undefined = SCENES[id];
      if (!scene) return;
      const jump = await this.play(scene);
      this.dialogue.close();
      if (jump) {
        id = await this.afterJump(id, jump);
        continue;
      }
      if (!scene.next || STOP_AFTER.has(id)) return;
      id = await this.afterJump(id, scene.next);
    }
  }

  private async afterJump(from: string, to: string): Promise<string> {
    const target = SCENES[to];
    const here = SCENES[from];
    if (target && here && here.where !== target.where && target.where.includes('מגדל האורגים') && !here.where.includes('מגדל האורגים')) {
      await this.hooks.toTower();
    }
    return to;
  }

  private async play(scene: SceneDef): Promise<string | null> {
    for (const st of scene.steps) {
      if ('line' in st) {
        const l = lineOf(st.line);
        const raw = this.save.data.look === 'girl' && l.textF ? l.textF : l.text;
        const text = raw.split('{name}').join(this.save.data.name || 'אורח');
        // only now and then, when someone repeats the catchphrase, the truth shows through for a moment
        if (text.includes('הכול בסדר') && ++this.catchphrases % 3 === 2) bus.emit('truth:flash', { ms: 450 });
        await this.dialogue.say([{ id: st.line, speaker: l.speaker, text }]);
      } else if ('flag' in st) {
        this.save.setFlag(st.flag);
        this.hooks.onFlag?.(st.flag);
        await playCutscene(`flag_${st.flag}`);
      } else if ('cutscene' in st) {
        await this.cutscene(st.cutscene, scene.title);
      } else {
        this.dialogue.close();
        const answer = await this.dialogue.choose(
          { speaker: '', text: st.choice.prompt },
          shuffleIfQuiz(st.choice.options).map((o) => ({ text: o.text, value: o.goto })),
        );
        return answer;
      }
    }
    return null;
  }

  /** In-engine cutscene card. Real illustrated or video cutscenes replace this later. */
  private async cutscene(id: string, title: string): Promise<void> {
    if (await playCutscene(id)) return;
    await new Promise<void>((resolve) => {
      const done = (): void => {
        screen.remove();
        resolve();
      };
      const screen = el('div', 'screen cutscene', '', [
        el('div', 'card cs-card', '', [
          el('div', 'cs-tag', 'קטע קולנוע'),
          el('h2', '', title),
          el('p', 'cs-id', id),
          el('div', 'row', '', [(() => {
            const b = el('button', 'btn primary', 'המשך');
            b.addEventListener('click', done);
            return b;
          })()]),
        ]),
      ]);
      uiRoot().append(screen);
    });
  }
}
