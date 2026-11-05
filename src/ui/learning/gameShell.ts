import { el } from '../dom';
import type { SaveStore } from '../../core/save';
import { LEVELS, type Level, type MinigameData, type MinigameResult } from './types';
import { type GameState, answerTask, mergeBest, newGame, passMin, summarize } from './minigameLogic';
import { confirmDialog, createOverlay } from './overlay';
import { applyPrize, prizeFor } from './prizes';
import { reducedMotion } from './widgetKit';

export const GAME_LEVEL_NAME: Record<Level, string> = { easy: 'קל', medium: 'בינוני', hard: 'קשה' };

export interface RoundApi {
  /** End the round. `ok` = solved. `text` is the explanation shown under the stage. `quick` skips the pause after a right answer. */
  resolve(ok: boolean, text: string, quick?: boolean): void;
  /** Seconds since the round started (frozen while a dialog is open or while the renderer says it is busy). */
  elapsed(): number;
  readonly timeLimit: number | null;
  /** Called once if the time runs out; the renderer should resolve the round. */
  onTimeout(cb: () => void): void;
  /** Stop the clock while an animation plays. */
  setBusy(busy: boolean): void;
  /** True while the "leave?" dialog is open. */
  isPaused(): boolean;
  flash(kind: 'good' | 'bad'): void;
}

export interface LevelInfo { count: number; lives: number; timeLimit: number | null; blurb: string }

export interface GameDef {
  title: string;
  intro: string;
  howTo: string[];
  levels: Record<Level, LevelInfo>;
  /** Draw round `index` of `level` into `host`; return a cleanup function. */
  mountRound(level: Level, index: number, host: HTMLElement, api: RoundApi): () => void;
}

/**
 * The frame shared by all the lesson mini-games: header with hearts, points and streak, intro, a per-round timer,
 * feedback, the end screen with the fixed prize, and a safe way out. A game only draws its own rounds.
 */
export function openGameShell(def: GameDef, data: MinigameData, level: Level, save: SaveStore, opts: { onClose(result: MinigameResult): void }): () => void {
  const ov = createOverlay('lrn-mini');
  const info = def.levels[level];
  const rules = { level, lives: info.lives, timeLimit: info.timeLimit, total: info.count };
  const lessonId = data.id.replace(/^minigame/, 'lesson');
  let state: GameState = newGame(rules);
  let closed = false;
  let paused = false;
  let roundCleanup: (() => void) | null = null;
  let raf = 0;
  let last: MinigameResult = { level, points: 0, passed: false, prizeGranted: false };

  const hearts = el('div', 'lrn-hearts');
  const points = el('span', 'lrn-points', '0');
  const streak = el('span', 'lrn-streak', '');
  const closeBtn = el('button', 'lrn-x', '×');
  closeBtn.type = 'button';
  closeBtn.setAttribute('aria-label', 'יציאה מהמשחקון');
  const timerFill = el('i', 'lrn-timer-fill');
  const timer = el('div', 'lrn-timer', '', [timerFill]);
  timer.hidden = true;
  const head = el('header', 'lrn-head', '', [
    el('div', 'lrn-head-main', '', [el('h1', 'lrn-title', `${def.title} · ${GAME_LEVEL_NAME[level]}`), el('div', 'lrn-hud', '', [hearts, el('span', 'lrn-points-w', '', [points, document.createTextNode(' נק׳')]), streak])]),
    closeBtn,
  ]);
  const arena = el('main', 'lrn-body lrn-arena');
  ov.root.append(head, timer, arena);

  const heart = (full: boolean): HTMLElement => el('span', `lrn-heart${full ? '' : ' lost'}`, '♥');
  function paintHud(): void {
    hearts.replaceChildren(...Array.from({ length: rules.lives }, (_, i) => heart(i < state.lives)));
    points.textContent = String(state.points);
    streak.textContent = state.streak >= 2 ? `\u{1F525} רצף ${state.streak}` : '';
  }

  function flash(kind: 'good' | 'bad'): void {
    if (reducedMotion()) return;
    arena.classList.remove('flash-good', 'flash-bad');
    void arena.offsetWidth;
    arena.classList.add(kind === 'good' ? 'flash-good' : 'flash-bad');
  }

  function stopRound(): void {
    cancelAnimationFrame(raf);
    roundCleanup?.();
    roundCleanup = null;
  }

  function intro(): void {
    const go = el('button', 'btn primary', 'מתחילים');
    go.type = 'button';
    go.addEventListener('click', begin);
    timer.hidden = true;
    arena.replaceChildren(el('section', 'lrn-task lrn-in', '', [
      el('p', 'lrn-story', def.intro),
      el('ul', 'lrn-facts', '', def.howTo.map((t) => el('li', '', t))),
      el('p', 'lrn-sub', info.blurb),
      go,
    ]));
    paintHud();
    go.focus();
  }

  function begin(): void {
    state = newGame(rules);
    paintHud();
    showRound();
  }

  function showRound(): void {
    stopRound();
    const index = state.index;
    const host = el('section', 'lrn-wire');
    const feedback = el('div', 'lrn-wire-msg', '');
    feedback.setAttribute('aria-live', 'polite');
    const bar = el('div', 'lrn-row lrn-wire-controls');
    arena.replaceChildren(el('div', 'lrn-shell-round', '', [host, feedback, bar]));
    timer.hidden = !rules.timeLimit;
    timerFill.style.width = '0%';
    timerFill.classList.remove('low');

    let resolved = false;
    let busy = false;
    let elapsed = 0;
    let timeoutCb: (() => void) | null = null;
    let prev = performance.now();
    const tick = (now: number): void => {
      raf = requestAnimationFrame(tick);
      const dt = Math.min(0.25, (now - prev) / 1000);
      prev = now;
      if (resolved || paused || busy) return;
      elapsed += dt;
      if (rules.timeLimit) {
        const p = Math.min(1, elapsed / rules.timeLimit);
        timerFill.style.width = `${p * 100}%`;
        timerFill.classList.toggle('low', p > 0.8);
        if (elapsed >= rules.timeLimit && timeoutCb) {
          const cb = timeoutCb;
          timeoutCb = null;
          cb();
        }
      }
    };
    raf = requestAnimationFrame(tick);

    const api: RoundApi = {
      timeLimit: rules.timeLimit,
      elapsed: () => elapsed,
      onTimeout: (cb) => { timeoutCb = cb; },
      setBusy: (b) => { busy = b; },
      isPaused: () => paused,
      flash,
      resolve(ok, text, quick = false) {
        if (resolved) return;
        resolved = true;
        const before = state;
        const res = answerTask(state, rules, ok, Math.min(elapsed, rules.timeLimit ?? elapsed));
        state = res.state;
        paintHud();
        if (state.lives < before.lives) hearts.children[state.lives]?.classList.add('breaking');
        flash(ok ? 'good' : 'bad');
        const final = state.over || state.finished;
        feedback.className = `lrn-wire-msg ${ok ? 'good' : 'warn'}`;
        feedback.textContent = `${ok ? `נכון! +${res.gained}. ` : 'לא הפעם. '}${text}`;
        const next = (): void => { if (final) showEnd(); else showRound(); };
        if (ok && quick && !final) {
          window.setTimeout(() => { if (!closed && state.index === index + 1) next(); }, 650);
          return;
        }
        const more = el('button', 'btn primary lrn-more', final ? (state.over ? 'להמשך ←' : 'לתוצאות ←') : 'הבא ←');
        more.type = 'button';
        more.addEventListener('click', next);
        bar.replaceChildren(more);
        more.focus();
      },
    };
    roundCleanup = def.mountRound(level, index, host, api);
  }

  function showEnd(): void {
    stopRound();
    timer.hidden = true;
    const sum = summarize(state, rules);
    const prev = save.lesson(lessonId).games[level];
    save.lesson(lessonId).games[level] = mergeBest(prev, sum.points, sum.passed);
    let prizeGranted = false;
    let prizeBox: HTMLElement | null = null;
    if (sum.passed) {
      const out = applyPrize(save, level, { flawless: sum.flawless, lessonId });
      prizeGranted = out.granted;
      const p = prizeFor(level, data.prizes);
      prizeBox = el('div', 'lrn-prize', '', [
        el('h3', '', out.granted ? `פרס חדש: ${p.name}` : `הפרס שלכם: ${p.name}`),
        el('p', '', p.description),
        el('p', 'lrn-prize-fx', out.granted ? `${p.effect} (+${out.coins} מטבעות)` : 'כבר קיבלתם את הפרס הזה: הוא נשאר שלכם.'),
        out.flawlessBadge ? el('p', 'lrn-prize-fx', 'ותג ״ערב נאה בעמק״: סיימתם בלי לאבד חיים.') : null,
      ]);
    }
    save.save();
    last = { level, points: sum.points, passed: sum.passed, prizeGranted };
    const need = passMin(level, rules.total);
    const again = el('button', 'btn', 'שחקו שוב');
    const done = el('button', 'btn primary', 'סגירה');
    again.type = 'button';
    done.type = 'button';
    again.addEventListener('click', begin);
    done.addEventListener('click', () => close());
    const bonusLine = sum.lifeBonus > 0 ? ` (כולל ${sum.lifeBonus} על חיים שנשארו)` : '';
    arena.replaceChildren(el('section', 'lrn-task results lrn-in', '', [
      el('h2', '', state.over ? 'נגמרו החיים, וזה בסדר' : sum.passed ? 'כל הכבוד!' : 'כמעט'),
      el('p', 'lrn-big', `${sum.points} נקודות${bonusLine}`),
      el('p', 'lrn-sub', state.over
        ? 'אין עונש ואין הפסד: אפשר להתחיל מחדש עכשיו, כמה פעמים שרוצים.'
        : `הצלחתם ב-${state.correct} מתוך ${rules.total}. ${sum.passed ? '' : `צריך לפחות ${need} כדי לעבור, ואפשר לנסות שוב בחינם.`}`),
      el('p', 'lrn-sub', `רצף הנכונות הארוך שלכם: ${state.bestStreak}`),
      prizeBox,
      el('div', 'lrn-row', '', [again, done]),
    ]));
    done.focus();
  }

  function teardown(): void {
    if (closed) return;
    closed = true;
    stopRound();
    document.removeEventListener('keydown', onKey, true);
    ov.destroy();
  }
  function close(): void {
    if (closed) return;
    teardown();
    opts.onClose(last);
  }
  async function askClose(): Promise<void> {
    if (state.finished || state.over || !arena.querySelector('.lrn-shell-round')) { close(); return; }
    paused = true;
    const leave = await confirmDialog(ov.root, 'לצאת מהמשחקון? הריצה הזאת לא תישמר, אפשר להתחיל מחדש בחינם.', 'כן, לצאת', 'להמשיך לשחק');
    paused = false;
    if (leave) close();
  }
  function onKey(e: KeyboardEvent): void {
    if (ov.root.querySelector('.lrn-confirm')) return;
    if (e.key === 'Escape') { e.preventDefault(); void askClose(); }
  }
  closeBtn.addEventListener('click', () => { void askClose(); });
  document.addEventListener('keydown', onKey, true);
  intro();
  return () => teardown();
}

export { LEVELS };
