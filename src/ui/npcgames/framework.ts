import type { SaveStore } from '../../core/save';
import { el } from '../dom';
import { createOverlay } from '../learning/overlay';
import { perksOf } from '../../game/perks';

export type NpcLevel = 'easy' | 'medium' | 'hard';
export const NPC_LEVELS: readonly NpcLevel[] = ['easy', 'medium', 'hard'];
export const NPC_LEVEL_NAME: Record<NpcLevel, string> = { easy: 'קל', medium: 'בינוני', hard: 'קשה' };

export interface GameResult { passed: boolean; /** What the player sees, e.g. "6 מתוך 8". */ summary: string }

export interface GameRun {
  /** Called by a game when the round ends. */
  finish(r: GameResult): void;
  /** Reduced speed and wider success areas (the calm mode in settings). */
  calm: boolean;
}

/** A game mounts itself into `host` and returns its cleanup. */
export type GameMount = (host: HTMLElement, level: NpcLevel, run: GameRun) => () => void;

export interface Reward {
  coins: number;
  /** Creature food or other stackable item: key in save.data.inv and its Hebrew name. */
  food?: { key: string; name: string; n: number };
  /** One-time keepsake (cosmetic, decoration or card), stored as a flag. */
  keepsake?: { flag: string; name: string };
}

export interface NpcGameDef {
  id: string;
  title: string;
  /** Short rules in Hebrew, shown on the level screen. */
  rules: string;
  controls: string;
  mount: GameMount;
  rewards: Record<NpcLevel, Reward>;
}

const REPEAT_COINS = 3;
const TRY_COINS = 2;

export interface Payout { text: string; coins: number }

/** Fixed prizes: the first success of a level pays in full, later successes 3 coins, a miss 2 coins. Never random. */
export function payout(save: SaveStore, def: NpcGameDef, level: NpcLevel, passed: boolean): Payout {
  const flag = `npcgame.${def.id}.${level}`;
  if (!passed) {
    save.data.coins += Math.round(TRY_COINS * perksOf(save).coinMul);
    save.save();
    return { coins: TRY_COINS, text: `לא הפעם. ${TRY_COINS} מטבעות על המאמץ, ואפשר לנסות שוב מיד.` };
  }
  if (save.hasFlag(flag)) {
    save.data.coins += Math.round(REPEAT_COINS * perksOf(save).coinMul);
    save.save();
    return { coins: REPEAT_COINS, text: `יפה! ${REPEAT_COINS} מטבעות.` };
  }
  const r = def.rewards[level];
  save.setFlag(flag);
  const gained = Math.round(r.coins * perksOf(save).coinMul);
  save.data.coins += gained;
  const parts = [`${gained} מטבעות`];
  if (r.food) {
    save.data.inv[r.food.key] = (save.data.inv[r.food.key] ?? 0) + r.food.n;
    parts.push(`${r.food.n} ${r.food.name} ליצורים`);
  }
  if (r.keepsake) {
    save.setFlag(r.keepsake.flag);
    parts.push(r.keepsake.name);
  }
  save.save();
  return { coins: r.coins, text: `פרס חדש: ${parts.join(', ')}.` };
}

/** Level screen, then the round, then the prize. Resolves when the player closes it. */
export function openNpcGame(def: NpcGameDef, save: SaveStore, calm = false): Promise<void> {
  return new Promise((resolve) => {
    const ov = createOverlay('lrn-mini npcg');
    const closeBtn = el('button', 'lrn-x', '×');
    closeBtn.type = 'button';
    closeBtn.setAttribute('aria-label', 'יציאה');
    const head = el('header', 'lrn-head', '', [el('div', 'lrn-head-main', '', [el('h1', 'lrn-title', def.title)]), closeBtn]);
    const body = el('main', 'lrn-body');
    ov.root.append(head, body);
    let cleanup: (() => void) | null = null;
    let closed = false;

    const close = (): void => {
      if (closed) return;
      closed = true;
      cleanup?.();
      document.removeEventListener('keydown', onKey, true);
      ov.destroy();
      resolve();
    };
    const onKey = (e: KeyboardEvent): void => {
      if (e.key === 'Escape') {
        e.preventDefault();
        if (cleanup) menu();
        else close();
      }
    };
    closeBtn.addEventListener('click', close);
    document.addEventListener('keydown', onKey, true);

    function menu(): void {
      cleanup?.();
      cleanup = null;
      const cards = NPC_LEVELS.map((level) => {
        const done = save.hasFlag(`npcgame.${def.id}.${level}`);
        const r = def.rewards[level];
        const prize = [`${r.coins} מטבעות`, r.food ? `${r.food.n} ${r.food.name}` : '', r.keepsake?.name ?? ''].filter(Boolean).join(' + ');
        const go = el('button', 'btn primary', done ? 'שחקו שוב' : 'התחילו');
        go.type = 'button';
        go.addEventListener('click', () => play(level));
        return el('section', `lrn-level ${level}${done ? ' passed' : ''}`, '', [
          el('h2', '', `${NPC_LEVEL_NAME[level]}${done ? ' ✓' : ''}`),
          el('div', 'lrn-prize', '', [el('h3', '', 'פרס'), el('p', '', done ? 'כבר קיבלתם. כל הצלחה נוספת: 3 מטבעות.' : prize)]),
          go,
        ]);
      });
      body.replaceChildren(
        el('p', 'lrn-story', def.rules),
        el('p', 'lrn-sub', def.controls),
        el('div', 'lrn-levels', '', cards),
        el('p', 'lrn-sub', 'בלי חיים ובלי עונש. אפשר לנסות שוב בחינם, בכל רמה, בכל סדר.'),
      );
    }

    function play(level: NpcLevel): void {
      cleanup?.();
      const stage = el('div', 'npcg-stage');
      body.replaceChildren(stage);
      const stop = def.mount(stage, level, {
        calm,
        finish: (r) => {
          stop();
          cleanup = null;
          const p = payout(save, def, level, r.passed);
          const again = el('button', 'btn primary', 'שוב');
          const back = el('button', 'btn', 'לרמות');
          again.type = 'button';
          back.type = 'button';
          again.addEventListener('click', () => play(level));
          back.addEventListener('click', menu);
          body.replaceChildren(el('section', 'lrn-task results lrn-in', '', [
            el('h2', '', r.passed ? 'כל הכבוד!' : 'כמעט'),
            el('p', 'lrn-big', r.summary),
            el('p', 'lrn-sub', p.text),
            el('div', 'lrn-row', '', [back, again]),
          ]));
          again.focus();
        },
      });
      cleanup = stop;
    }

    menu();
  });
}
