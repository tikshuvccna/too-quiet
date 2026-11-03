import { el } from '../dom';
import type { SaveStore } from '../../core/save';
import { LEVELS, type Level, type MiniTask, type MinigameData, type MinigameResult } from './types';
import { type GameState, answerTask, mergeBest, newGame, passMin, prepareTask, rulesFor, summarize } from './minigameLogic';
import { confirmDialog, createOverlay } from './overlay';
import { applyPrize, prizeFor } from './prizes';
import { mulberry32 } from './util';
import { reducedMotion } from './widgetKit';

export const LEVEL_NAME: Record<Level, string> = { easy: 'קל', medium: 'בינוני', hard: 'קשה' };

const heart = (full: boolean): HTMLElement => el('span', `lrn-heart${full ? '' : ' lost'}`, '♥');

/**
 * One run of the mini-game. Tasks are small valley stories with options. A mistake costs a heart, a streak
 * and speed add points, and running out of hearts (or time) only ends the run with a calm message.
 */
export function openMinigame(data: MinigameData, level: Level, save: SaveStore, opts: { onClose(result: MinigameResult): void }): () => void {
  const ov = createOverlay('lrn-mini');
  const lv = data.levels[level];
  const rules = rulesFor(level, lv);
  let tasks: MiniTask[] = [];
  let state: GameState = newGame(rules);
  let elapsed = 0;
  let timing = false;
  let raf = 0;
  let pendingTimeout: (() => void) | null = null;
  let closed = false;
  let last: MinigameResult = { level, points: 0, passed: false, prizeGranted: false };

  const title = el('h1', 'lrn-title', `${data.title} · ${LEVEL_NAME[level]}`);
  const hearts = el('div', 'lrn-hearts');
  hearts.setAttribute('aria-label', 'חיים');
  const points = el('span', 'lrn-points', '0');
  const streak = el('span', 'lrn-streak', '');
  const closeBtn = el('button', 'lrn-x', '✕');
  closeBtn.type = 'button';
  closeBtn.setAttribute('aria-label', 'יציאה מהמשחקון');
  const timerFill = el('i', 'lrn-timer-fill');
  const timer = el('div', 'lrn-timer', '', [timerFill]);
  timer.hidden = !rules.timeLimit;
  const head = el('header', 'lrn-head', '', [
    el('div', 'lrn-head-main', '', [title, el('div', 'lrn-hud', '', [hearts, el('span', 'lrn-points-w', '', [points, document.createTextNode(' נק׳')]), streak])]),
    closeBtn,
  ]);
  const arena = el('main', 'lrn-body lrn-arena');
  ov.root.append(head, timer, arena);

  function paintHud(): void {
    hearts.replaceChildren(...Array.from({ length: rules.lives }, (_, i) => heart(i < state.lives)));
    points.textContent = String(state.points);
    streak.textContent = state.streak >= 2 ? `\u{1F525} רצף ${state.streak}` : '';
    streak.classList.remove('pop');
    void streak.offsetWidth;
    if (state.streak >= 2) streak.classList.add('pop');
  }

  function begin(): void {
    const rng = mulberry32((Date.now() ^ 0x9e3779b9) >>> 0);
    tasks = lv.tasks.map((t) => prepareTask(t, level, rng));
    state = newGame(rules);
    timer.hidden = !rules.timeLimit;
    paintHud();
    showTask();
  }

  function stopTimer(): void {
    timing = false;
    cancelAnimationFrame(raf);
  }

  function startTimer(onTimeout: () => void, keepElapsed = false): void {
    stopTimer();
    pendingTimeout = onTimeout;
    if (!keepElapsed) elapsed = 0;
    const limit = rules.timeLimit;
    if (!limit) return;
    timing = true;
    let prev = performance.now();
    const tick = (now: number): void => {
      if (!timing) return;
      // A hidden tab must not eat the time: one frame never counts for more than a quarter second.
      elapsed += Math.min(0.25, (now - prev) / 1000);
      prev = now;
      const left = Math.max(0, 1 - elapsed / limit);
      timerFill.style.width = `${left * 100}%`;
      timerFill.classList.toggle('low', left < 0.25);
      if (elapsed >= limit) { stopTimer(); onTimeout(); return; }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
  }

  function showTask(): void {
    const task = tasks[state.index];
    if (!task) return;
    const fb = el('div', 'lrn-feedback');
    fb.setAttribute('aria-live', 'polite');
    const buttons = task.options.map((text, i) => {
      const b = el('button', 'lrn-opt lrn-big-opt', text);
      b.type = 'button';
      b.addEventListener('click', () => resolve(i, b));
      return b;
    });
    const card = el('section', 'lrn-task lrn-in', '', [
      el('p', 'lrn-task-n', `משימה ${state.index + 1} מתוך ${rules.total}`),
      el('p', 'lrn-scenario', task.scenario),
      el('div', 'lrn-opts', '', buttons),
      fb,
    ]);
    arena.replaceChildren(card);

    function resolve(pick: number | null, btn: HTMLElement | null): void {
      stopTimer();
      pendingTimeout = null;
      const ok = pick === task?.correct;
      const before = state;
      const res = answerTask(state, rules, ok, elapsed);
      state = res.state;
      buttons.forEach((b, i) => { b.disabled = true; b.classList.toggle('right', i === task?.correct); });
      if (!ok && btn) btn.classList.add('wrong');
      const lostLife = state.lives < before.lives;
      if (ok) {
        flash('good');
        floatText(btn ?? card, `+${res.gained}`, 'good');
        fb.className = 'lrn-feedback good';
        fb.textContent = `נכון! ${task?.why ?? ''}`;
      } else {
        flash('bad');
        arena.classList.remove('shake');
        void arena.offsetWidth;
        arena.classList.add('shake');
        fb.className = 'lrn-feedback warn';
        fb.textContent = pick === null ? `הזמן נגמר, זה בסדר. ${task?.why ?? ''}` : `לא הפעם. ${task?.why ?? ''}`;
      }
      paintHud();
      if (lostLife) hearts.children[state.lives]?.classList.add('breaking');
      const final = state.over || state.finished;
      const more = el('button', 'btn primary lrn-more', final ? (state.over ? 'להמשך ←' : 'לתוצאות ←') : 'המשימה הבאה ←');
      more.type = 'button';
      more.addEventListener('click', () => { if (final) showEnd(); else showTask(); });
      card.append(more);
      more.focus();
    }

    timerFill.style.width = '100%';
    timerFill.classList.remove('low');
    if (rules.timeLimit) startTimer(() => resolve(null, null));
  }

  function flash(kind: 'good' | 'bad'): void {
    if (reducedMotion()) return;
    arena.classList.remove('flash-good', 'flash-bad');
    void arena.offsetWidth;
    arena.classList.add(kind === 'good' ? 'flash-good' : 'flash-bad');
  }

  function floatText(anchor: HTMLElement, text: string, tone: string): void {
    const a = anchor.getBoundingClientRect();
    const r = ov.root.getBoundingClientRect();
    const f = el('span', `lrn-float ${tone}`, text);
    f.style.left = `${a.left - r.left + a.width / 2}px`;
    f.style.top = `${a.top - r.top + a.height / 2}px`;
    ov.root.append(f);
    window.setTimeout(() => f.remove(), 1300);
  }

  function showEnd(): void {
    stopTimer();
    timer.hidden = true;
    const sum = summarize(state, rules);
    const prev = save.lesson(lessonId()).games[level];
    save.lesson(lessonId()).games[level] = mergeBest(prev, sum.points, sum.passed);
    let prizeGranted = false;
    let prizeBox: HTMLElement | null = null;
    if (sum.passed) {
      const out = applyPrize(save, level, { flawless: sum.flawless });
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
      el('h2', '', state.over ? 'נגמרו החיים, וזה בסדר' : sum.passed ? 'כל הכבוד, עברתם!' : 'כמעט'),
      el('p', 'lrn-big', `${sum.points} נקודות${bonusLine}`),
      el('p', 'lrn-sub', state.over
        ? 'אין עונש ואין הפסד: אפשר להתחיל מחדש עכשיו, כמה פעמים שרוצים.'
        : `ענו נכון על ${state.correct} מתוך ${rules.total} משימות. ${sum.passed ? '' : `צריך לפחות ${need} כדי לעבור, ואפשר לנסות שוב בחינם.`}`),
      el('p', 'lrn-sub', `רצף הנכונות הארוך שלכם: ${state.bestStreak}`),
      prizeBox,
      el('div', 'lrn-row', '', [again, done]),
    ]));
    done.focus();
  }

  const lessonId = (): string => data.id.replace(/^minigame/, 'lesson');

  function teardown(): void {
    if (closed) return;
    closed = true;
    stopTimer();
    document.removeEventListener('keydown', onKey, true);
    ov.destroy();
  }

  function close(): void {
    if (closed) return;
    teardown();
    opts.onClose(last);
  }

  async function askClose(): Promise<void> {
    if (state.finished || state.over || state.index === 0) { close(); return; }
    const wasTiming = timing;
    stopTimer();
    if (await confirmDialog(ov.root, 'לצאת מהמשחקון? הריצה הזאת לא תישמר, אפשר להתחיל מחדש בחינם.', 'כן, לצאת', 'להמשיך לשחק')) {
      close();
    } else if (wasTiming && pendingTimeout) {
      // The time spent in the dialog is not counted: it must never cost a life.
      startTimer(pendingTimeout, true);
    }
  }

  function onKey(e: KeyboardEvent): void {
    if (ov.root.querySelector('.lrn-confirm')) return;
    if (e.key === 'Escape') { e.preventDefault(); void askClose(); return; }
    const n = Number(e.key);
    if (n >= 1 && n <= 4) {
      const b = arena.querySelectorAll<HTMLButtonElement>('.lrn-opt:not([disabled])')[n - 1];
      b?.click();
    }
  }

  closeBtn.addEventListener('click', () => { void askClose(); });
  document.addEventListener('keydown', onKey, true);
  begin();
  return () => teardown();
}

/** Level select: three levels, none locks another, every one can be replayed for free. */
export function openMinigameMenu(data: MinigameData, save: SaveStore, opts: { onClose(): void; onResult?(r: MinigameResult): void }): () => void {
  const ov = createOverlay('lrn-mini lrn-menu');
  const lessonId = data.id.replace(/^minigame/, 'lesson');
  let closed = false;
  let child: (() => void) | null = null;

  const closeBtn = el('button', 'lrn-x', '✕');
  closeBtn.type = 'button';
  closeBtn.setAttribute('aria-label', 'סגירה');
  const head = el('header', 'lrn-head', '', [el('div', 'lrn-head-main', '', [el('h1', 'lrn-title', data.title)]), closeBtn]);
  const body = el('main', 'lrn-body');
  ov.root.append(head, body);

  function render(): void {
    const cards = LEVELS.map((level) => {
      const lv = data.levels[level];
      const p = prizeFor(level, data.prizes);
      const best = save.lesson(lessonId).games[level];
      const play = el('button', 'btn primary', best ? 'שחקו שוב' : 'התחילו');
      play.type = 'button';
      play.addEventListener('click', () => {
        child = openMinigame(data, level, save, {
          onClose: (r) => { child = null; opts.onResult?.(r); render(); },
        });
      });
      return el('section', `lrn-level ${level}${best?.passed ? ' passed' : ''}`, '', [
        el('h2', '', `${LEVEL_NAME[level]}${best?.passed ? ' ✓' : ''}`),
        el('ul', 'lrn-facts', '', [
          el('li', '', `♥ ${lv.lives} חיים`),
          el('li', '', lv.timeLimitPerTaskSec ? `${lv.timeLimitPerTaskSec} שניות למשימה` : 'בלי הגבלת זמן'),
          el('li', '', `${lv.tasks.length} משימות`),
          el('li', 'best', best ? `שיא: ${best.points} נקודות` : 'עוד לא שיחקתם'),
        ]),
        el('div', 'lrn-prize', '', [el('h3', '', `פרס: ${p.name}`), el('p', '', p.description)]),
        play,
      ]);
    });
    body.replaceChildren(
      el('p', 'lrn-story', data.story),
      el('div', 'lrn-levels', '', cards),
      el('p', 'lrn-sub', 'אפשר לבחור כל רמה, בכל סדר, ולנסות שוב בחינם.'),
    );
  }

  function close(): void {
    if (closed) return;
    closed = true;
    child?.();
    document.removeEventListener('keydown', onKey, true);
    ov.destroy();
    opts.onClose();
  }

  function onKey(e: KeyboardEvent): void {
    if (child) return;
    if (e.key === 'Escape') { e.preventDefault(); close(); }
  }

  closeBtn.addEventListener('click', close);
  document.addEventListener('keydown', onKey, true);
  render();
  return () => {
    if (closed) return;
    closed = true;
    child?.();
    document.removeEventListener('keydown', onKey, true);
    ov.destroy();
  };
}
