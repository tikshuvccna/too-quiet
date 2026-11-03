import { SCENES, SPEAKER_NAMES, lineOf, type SceneDef } from '../content';
import type { SaveStore } from '../core/save';
import type { DialogueUI } from '../ui/dialogue';
import { el, uiRoot } from '../ui/dom';

/** After these scenes the story waits for the player to go somewhere, instead of following `next`. */
export const STOP_AFTER = new Set(['village_houses', 'return_after_lesson', 'fix_grandma_ok', 'fix_clinic_ok', 'fix_mill_ok', 'bakery_fixed']);

export interface RunnerHooks {
  /** Called when the story has to continue in the Weavers' Tower (teleport first). */
  toTower(): Promise<void>;
  onFlag?(name: string): void;
}

/** Plays a scene from scenes.json: lines, choices that jump to other scenes, flags and cutscene cards. */
export class SceneRunner {
  constructor(
    private readonly dialogue: DialogueUI,
    private readonly save: SaveStore,
    private readonly hooks: RunnerHooks,
  ) {
    dialogue.names = SPEAKER_NAMES;
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
        const text = this.save.data.look === 'girl' && l.textF ? l.textF : l.text;
        await this.dialogue.say([{ id: st.line, speaker: l.speaker, text }]);
      } else if ('flag' in st) {
        this.save.setFlag(st.flag);
        this.hooks.onFlag?.(st.flag);
      } else if ('cutscene' in st) {
        await this.cutscene(st.cutscene, scene.title);
      } else {
        this.dialogue.close();
        const answer = await this.dialogue.choose(
          { speaker: '', text: st.choice.prompt },
          st.choice.options.map((o) => ({ text: o.text, value: o.goto })),
        );
        return answer;
      }
    }
    return null;
  }

  /** In-engine cutscene card. Real illustrated or video cutscenes replace this later. */
  private cutscene(id: string, title: string): Promise<void> {
    return new Promise((resolve) => {
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
