import { el } from '../dom';
import type { SaveStore } from '../../core/save';
import { LEVELS, type Level, type MiniTask, type MinigameData, type MinigameResult } from './types';
import { type GameState, answerTask, mergeBest, newGame, passMin, prepareTask, rulesFor, summarize } from './minigameLogic';
import { confirmDialog, createOverlay } from './overlay';
import { applyPrize, prizeFor } from './prizes';
import { mulberry32 } from './util';
import { reducedMotion } from './widgetKit';
import { openGameShell, type GameDef } from './gameShell';
import { wiringGame } from './wiring';

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
  let stageKey: ((k: string) => boolean) | null = null;
  let closed = false;
  let last: MinigameResult = { level, points: 0, passed: false, prizeGranted: false };

  const title = el('h1', 'lrn-title', `${data.title} · ${LEVEL_NAME[level]}`);
  const hearts = el('div', 'lrn-hearts');
  hearts.setAttribute('aria-label', 'חיים');
  const points = el('span', 'lrn-points', '0');
  const streak = el('span', 'lrn-streak', '');
  const closeBtn = el('button', 'lrn-x', '×');
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

  /** Gate-runner stage: a paper-crane messenger flies up the valley, one gate per task, one lane per answer. */
  const LANE_COLORS = ['#ff9f7a', '#7ad6ff', '#c6a2ff', '#ffd36b'];
  let stageStop: (() => void) | null = null;
  let stagePaused = false;

  function showTask(): void {
    const task = tasks[state.index];
    if (!task) return;
    stageStop?.();
    const n = task.options.length;
    const approach = rules.timeLimit ? rules.timeLimit * (level === 'hard' ? 0.8 : 0.6) : 13;
    const stage = el('div', 'lrn-stage');
    const canvas = el('canvas', 'lrn-canvas');
    const banner = el('div', 'lrn-banner', '', [
      el('span', 'lrn-banner-n', `משימה ${state.index + 1} מתוך ${rules.total}`),
      el('p', '', task.scenario),
    ]);
    const gate = el('div', 'lrn-gate', '', task.options.map((t, i) => {
      const c = el('div', 'lrn-gate-cell', t);
      c.style.setProperty('--c', LANE_COLORS[i % LANE_COLORS.length] ?? '#fff');
      return c;
    }));
    const hint = el('div', 'lrn-stage-hint', 'גררו, לחצו על מסלול, או השתמשו בחצים');
    stage.append(canvas, banner, gate, hint);
    arena.replaceChildren(stage);
    timer.hidden = false;
    timerFill.style.width = '0%';
    timerFill.classList.remove('low');

    const dpr = Math.min(2, window.devicePixelRatio || 1);
    let W = 0;
    let H = 0;
    const fit = (): void => {
      W = stage.clientWidth;
      H = stage.clientHeight;
      canvas.width = Math.round(W * dpr);
      canvas.height = Math.round(H * dpr);
    };
    fit();
    const ro = new ResizeObserver(fit);
    ro.observe(stage);

    let lane = Math.floor((n - 1) / 2);
    let px = (lane + 0.5) / n;
    let touched = false;
    let t = 0;
    let lastChange = 0;
    let resolved = false;
    const rng = mulberry32((state.index * 7919 + 13) >>> 0);
    const coins = Array.from({ length: 5 }, (_, k) => ({ lane: Math.floor(rng() * n), at: 0.1 + k * 0.17, got: false }));
    let coinsGot = 0;
    const setLane = (l: number): void => {
      const nl = Math.max(0, Math.min(n - 1, l));
      if (nl !== lane) { lane = nl; lastChange = t; }
      touched = true;
      hint.classList.add('gone');
    };
    const laneAt = (clientX: number): number => {
      const r = stage.getBoundingClientRect();
      return Math.floor(((clientX - r.left) / r.width) * n);
    };
    let dragging = false;
    stage.addEventListener('pointerdown', (e) => { if (!resolved) { dragging = true; setLane(laneAt(e.clientX)); } });
    stage.addEventListener('pointermove', (e) => { if (dragging && !resolved) setLane(laneAt(e.clientX)); });
    const up = (): void => { dragging = false; };
    window.addEventListener('pointerup', up);
    stageKey = (k: string): boolean => {
      if (resolved) return false;
      if (k === 'ArrowLeft' || k === 'a') { setLane(lane - 1); return true; }
      if (k === 'ArrowRight' || k === 'd') { setLane(lane + 1); return true; }
      const num = Number(k);
      if (num >= 1 && num <= n) { setLane(num - 1); return true; }
      return false;
    };

    const ctx2 = canvas.getContext('2d');
    const crane = (c: CanvasRenderingContext2D, x: number, y: number, flap: number, tilt: number): void => {
      c.save();
      c.translate(x, y);
      c.fillStyle = 'rgba(0,0,0,.25)';
      c.beginPath(); c.ellipse(0, 34, 22, 7, 0, 0, Math.PI * 2); c.fill();
      c.rotate(tilt);
      const w = 26 + flap * 12;
      c.fillStyle = '#fff4d6'; c.strokeStyle = '#6d4a10'; c.lineWidth = 2; c.lineJoin = 'round';
      for (const s of [-1, 1]) {
        c.beginPath(); c.moveTo(0, -4); c.lineTo(s * w, -14 - flap * 10); c.lineTo(s * (w - 8), 12); c.lineTo(0, 8); c.closePath(); c.fill(); c.stroke();
      }
      c.fillStyle = '#ffd36b';
      c.beginPath(); c.moveTo(0, -26); c.lineTo(8, 4); c.lineTo(0, 20); c.lineTo(-8, 4); c.closePath(); c.fill(); c.stroke();
      c.fillStyle = '#ff7a59';
      c.beginPath(); c.moveTo(0, -26); c.lineTo(5, -33); c.lineTo(-5, -26); c.closePath(); c.fill(); c.stroke();
      c.fillStyle = '#2b2150'; c.beginPath(); c.arc(-2, -20, 1.6, 0, 7); c.fill();
      c.restore();
    };

    const gateH = 74;
    let prev = performance.now();
    const frame = (now: number): void => {
      raf = requestAnimationFrame(frame);
      const dt = Math.min(0.25, (now - prev) / 1000);
      prev = now;
      if (!ctx2 || resolved) return;
      if (!stagePaused) {
        const hover = !rules.timeLimit && !touched && t >= approach * 0.8;
        if (!hover) t += dt;
      }
      const prog = Math.min(1, t / approach);
      const catchY = H * 0.78;
      const gateY = -gateH + prog * (catchY - 14 + gateH);
      gate.style.transform = `translateY(${gateY}px)`;
      gate.style.height = `${gateH}px`;
      timerFill.style.width = `${prog * 100}%`;
      timerFill.classList.toggle('low', prog > 0.8);
      px += ((lane + 0.5) / n - px) * Math.min(1, dt * 10);
      const c = ctx2;
      c.setTransform(dpr, 0, 0, dpr, 0, 0);
      const g = c.createLinearGradient(0, 0, 0, H);
      g.addColorStop(0, '#2a2468'); g.addColorStop(0.55, '#6a5aa8'); g.addColorStop(1, '#f2b985');
      c.fillStyle = g; c.fillRect(0, 0, W, H);
      const scroll = (now / 1000) * 90;
      for (let i = 0; i < n; i++) {
        const x0 = (i / n) * W;
        const lw = W / n;
        c.fillStyle = i % 2 ? 'rgba(255,255,255,.07)' : 'rgba(0,0,0,.08)';
        c.fillRect(x0, 0, lw, H);
        c.strokeStyle = 'rgba(255,230,160,.5)'; c.lineWidth = 2; c.setLineDash([14, 16]); c.lineDashOffset = scroll;
        c.beginPath(); c.moveTo(x0 + lw / 2, 0); c.lineTo(x0 + lw / 2, H); c.stroke(); c.setLineDash([]);
      }
      // coins ride between the gate and the messenger; catch them by standing in their lane
      for (const co of coins) {
        if (co.got) continue;
        const y = gateY + gateH + 20 + (catchY - gateY - gateH - 20) * co.at * 1.1;
        if (y > catchY + 30) { co.got = true; continue; }
        const cx = ((co.lane + 0.5) / n) * W;
        if (Math.abs(y - catchY) < 26 && co.lane === lane) {
          co.got = true;
          coinsGot++;
          floatText(stage, '+10', 'good');
          continue;
        }
        c.fillStyle = '#ffd36b'; c.strokeStyle = '#8a5a12'; c.lineWidth = 2;
        c.beginPath(); c.arc(cx, y, 9, 0, 7); c.fill(); c.stroke();
        c.strokeStyle = '#fff3b0'; c.beginPath(); c.arc(cx, y, 4, 0, 7); c.stroke();
      }
      const flap = (Math.sin(now / 90) + 1) / 2;
      crane(c, px * W, catchY, flap, ((lane + 0.5) / n - px) * 1.4);
      if (prog >= 1) resolve(lane);
    };
    raf = requestAnimationFrame(frame);

    const fb = el('div', 'lrn-feedback');
    fb.setAttribute('aria-live', 'polite');

    function resolve(pick: number): void {
      if (resolved) return;
      resolved = true;
      stageStop?.();
      const ok = pick === task?.correct;
      const before = state;
      const used = (lastChange / approach) * (rules.timeLimit ?? 0);
      const res = answerTask(state, rules, ok, used);
      state = { ...res.state, points: res.state.points + coinsGot * 10 };
      const lostLife = state.lives < before.lives;
      gate.querySelectorAll('.lrn-gate-cell').forEach((cell, i) => {
        cell.classList.toggle('right', i === task?.correct);
        if (i === pick && !ok) cell.classList.add('wrong');
      });
      if (ok) {
        flash('good');
        floatText(gate, `+${res.gained}`, 'good');
        fb.className = 'lrn-feedback good';
        fb.textContent = `נכון! ${task?.why ?? ''}`;
      } else {
        flash('bad');
        arena.classList.remove('shake');
        void arena.offsetWidth;
        arena.classList.add('shake');
        fb.className = 'lrn-feedback warn';
        fb.textContent = `לא הפעם. ${task?.why ?? ''}`;
      }
      paintHud();
      if (lostLife) hearts.children[state.lives]?.classList.add('breaking');
      const final = state.over || state.finished;
      const more = el('button', 'btn primary lrn-more', final ? (state.over ? 'להמשך ←' : 'לתוצאות ←') : 'השער הבא ←');
      more.type = 'button';
      more.addEventListener('click', () => { if (final) showEnd(); else showTask(); });
      stage.append(el('div', 'lrn-stage-result', '', [fb, more]));
      more.focus();
    }

    stageStop = () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
      window.removeEventListener('pointerup', up);
      stageStop = null;
    };
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
    stageStop?.();
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
    stageStop?.();
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
    stagePaused = true;
    const leave = await confirmDialog(ov.root, 'לצאת מהמשחקון? הריצה הזאת לא תישמר, אפשר להתחיל מחדש בחינם.', 'כן, לצאת', 'להמשיך לשחק');
    stagePaused = false;
    if (leave) close();
  }

  function onKey(e: KeyboardEvent): void {
    if (ov.root.querySelector('.lrn-confirm')) return;
    if (e.key === 'Escape') { e.preventDefault(); void askClose(); return; }
    if (stageKey?.(e.key)) e.preventDefault();
  }

  closeBtn.addEventListener('click', () => { void askClose(); });
  document.addEventListener('keydown', onKey, true);
  begin();
  return () => teardown();
}

/** Level select: three levels, none locks another, every one can be replayed for free. */
export function openMinigameMenu(data: MinigameData, save: SaveStore, opts: { onClose(): void; onResult?(r: MinigameResult): void }, game?: GameDef): () => void {
  const ov = createOverlay('lrn-mini lrn-menu');
  const lessonId = data.id.replace(/^minigame/, 'lesson');
  let closed = false;
  let child: (() => void) | null = null;

  const closeBtn = el('button', 'lrn-x', '×');
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
        const onClose = (r: MinigameResult): void => { child = null; opts.onResult?.(r); render(); };
        child = game ? openGameShell(game, data, level, save, { onClose }) : data.wiring ? openGameShell(wiringGame(data.wiring, data), data, level, save, { onClose }) : openMinigame(data, level, save, { onClose });
      });
      return el('section', `lrn-level ${level}${best?.passed ? ' passed' : ''}`, '', [
        el('h2', '', `${LEVEL_NAME[level]}${best?.passed ? ' ✓' : ''}`),
        el('ul', 'lrn-facts', '', [
          el('li', '', `♥ ${game ? game.levels[level].lives : lv.lives} חיים`),
          el('li', '', (game ? game.levels[level].timeLimit : lv.timeLimitPerTaskSec) ? `${game ? game.levels[level].timeLimit : lv.timeLimitPerTaskSec} שניות לסיבוב` : 'בלי הגבלת זמן'),
          el('li', '', game ? `${game.levels[level].count} סיבובים` : data.wiring ? `${data.wiring.levels[level].rounds.length} סיבובים, ${data.wiring.levels[level].attempts} ניסיונות בכל אחד` : `${lv.tasks.length} משימות`),
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
