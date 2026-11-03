import { describe, expect, it } from 'vitest';
import { SaveStore } from '../../core/save';
import lesson01 from '../../../content/he/lesson01.json';
import quiz01 from '../../../content/he/quiz01.json';
import minigame01 from '../../../content/he/minigame01.json';
import type { LessonData, MinigameData, QuizData } from './types';
import { PASS_MIN_CORRECT, isOrderCorrect, maxScore, pointsFor, resolveAttempt, tally, togglePick, type Outcome } from './quizLogic';
import { answerTask, mergeBest, newGame, passMin, prepareTask, rulesFor, scoreTask, summarize } from './minigameLogic';
import { FLAWLESS_FLAG, PRIZE_COINS, applyPrize, prizeFor } from './prizes';
import { canAdvance, checkForDisplay, clampStep, isLast, resumeIndex } from './lessonLogic';
import { mulberry32, shuffleOptions } from './util';

const lesson = lesson01 as unknown as LessonData;
const quiz = quiz01 as unknown as QuizData;
const mini = minigame01 as unknown as MinigameData;

describe('quiz scoring', () => {
  it('awards 10/15/20 and half on a retry', () => {
    expect(pointsFor('easy', 'first')).toBe(10);
    expect(pointsFor('medium', 'first')).toBe(15);
    expect(pointsFor('hard', 'first')).toBe(20);
    expect(pointsFor('easy', 'retry')).toBe(5);
    expect(pointsFor('hard', 'retry')).toBe(10);
    expect(pointsFor('medium', 'retry')).toBe(7);
    expect(pointsFor('hard', 'miss')).toBe(0);
  });

  it('gives one retry per question', () => {
    expect(resolveAttempt(1, true)).toEqual({ kind: 'done', outcome: 'first' });
    expect(resolveAttempt(1, false)).toEqual({ kind: 'again' });
    expect(resolveAttempt(2, true)).toEqual({ kind: 'done', outcome: 'retry' });
    expect(resolveAttempt(2, false)).toEqual({ kind: 'done', outcome: 'miss' });
  });

  it('computes the max from the real quiz (3 easy, 3 medium, 2 hard)', () => {
    expect(quiz.questions).toHaveLength(8);
    expect(maxScore(quiz.questions)).toBe(3 * 10 + 3 * 15 + 2 * 20);
  });

  it('passes with at least 5 of 8 correct, retries included', () => {
    const f: Outcome[] = Array<Outcome>(8).fill('first');
    expect(tally(quiz.questions, f).passed).toBe(true);
    expect(tally(quiz.questions, f).score).toBe(115);
    const five: Outcome[] = ['first', 'retry', 'retry', 'first', 'retry', 'miss', 'miss', 'miss'];
    expect(tally(quiz.questions, five).correct).toBe(PASS_MIN_CORRECT);
    expect(tally(quiz.questions, five).passed).toBe(true);
    const four: Outcome[] = ['first', 'first', 'first', 'first', 'miss', 'miss', 'miss', 'miss'];
    expect(tally(quiz.questions, four).passed).toBe(false);
  });

  it('checks order answers and toggles picks', () => {
    expect(isOrderCorrect([1, 3, 0, 2], [1, 3, 0, 2])).toBe(true);
    expect(isOrderCorrect([1, 3, 2, 0], [1, 3, 0, 2])).toBe(false);
    expect(isOrderCorrect([1, 3], [1, 3, 0, 2])).toBe(false);
    expect(togglePick([1, 3], 0)).toEqual([1, 3, 0]);
    expect(togglePick([1, 3, 0], 3)).toEqual([1, 0]);
  });

  it('keeps the correct answer when shuffling', () => {
    for (const q of quiz.questions) {
      if (q.type !== 'mcq') continue;
      for (let seed = 1; seed < 20; seed++) {
        const sh = shuffleOptions(q.options, q.correct, mulberry32(seed));
        expect(sh.options[sh.correct]).toBe(q.options[q.correct]);
        expect([...sh.options].sort()).toEqual([...q.options].sort());
      }
    }
  });
});

describe('minigame rules', () => {
  const easy = rulesFor('easy', mini.levels.easy);
  const medium = rulesFor('medium', mini.levels.medium);
  const hard = rulesFor('hard', mini.levels.hard);

  it('reads lives, limits and counts from the content', () => {
    expect(easy).toMatchObject({ lives: 5, timeLimit: null, total: 8 });
    expect(medium).toMatchObject({ lives: 3, timeLimit: 25, total: 10 });
    expect(hard).toMatchObject({ lives: 3, timeLimit: 20, total: 10 });
  });

  it('computes pass minimums (70 percent, hard 80)', () => {
    expect(passMin('easy', 8)).toBe(6);
    expect(passMin('medium', 10)).toBe(7);
    expect(passMin('hard', 10)).toBe(8);
  });

  it('scores a streak and speed on timed levels only', () => {
    expect(scoreTask('easy', 0, 3, null)).toMatchObject({ base: 100, speed: 0, streak: 0, total: 100 });
    expect(scoreTask('easy', 2, 3, null).total).toBe(120);
    expect(scoreTask('easy', 99, 0, null).streak).toBe(50);
    expect(scoreTask('medium', 0, 0, 25).speed).toBe(75);
    expect(scoreTask('medium', 0, 25, 25).speed).toBe(0);
    expect(scoreTask('hard', 0, 100, 20).speed).toBe(0);
  });

  it('loses a life and the streak on a mistake', () => {
    let s = newGame(easy);
    s = answerTask(s, easy, true, 1).state;
    s = answerTask(s, easy, true, 1).state;
    expect(s.streak).toBe(2);
    const r = answerTask(s, easy, false, 1);
    expect(r.state.lives).toBe(4);
    expect(r.state.streak).toBe(0);
    expect(r.state.bestStreak).toBe(2);
    expect(r.gained).toBe(0);
  });

  it('ends the run when lives run out with tasks left, and not on the last task', () => {
    let s = newGame(hard);
    for (let i = 0; i < 3; i++) s = answerTask(s, hard, false, 1).state;
    expect(s.over).toBe(true);
    expect(summarize(s, hard).passed).toBe(false);
    expect(answerTask(s, hard, true, 1).state).toBe(s);

    let t = newGame(medium);
    for (let i = 0; i < 7; i++) t = answerTask(t, medium, true, 5).state;
    for (let i = 0; i < 3; i++) t = answerTask(t, medium, false, 5).state;
    expect(t.finished).toBe(true);
    expect(t.over).toBe(false);
    expect(summarize(t, medium).passed).toBe(true);
  });

  it('passes a clean run with life bonus and flawless flag', () => {
    let s = newGame(easy);
    for (let i = 0; i < 8; i++) s = answerTask(s, easy, true, 1).state;
    const sum = summarize(s, easy);
    expect(sum.passed).toBe(true);
    expect(sum.flawless).toBe(true);
    expect(sum.lifeBonus).toBe(125);
    expect(sum.points).toBe(s.points + 125);
  });

  it('fails when too few are right even though lives remain', () => {
    let s = newGame(easy);
    for (let i = 0; i < 5; i++) s = answerTask(s, easy, true, 1).state;
    for (let i = 0; i < 3; i++) s = answerTask(s, easy, false, 1).state;
    expect(s.finished).toBe(true);
    expect(summarize(s, easy).passed).toBe(false);
  });

  it('keeps best points and a sticky pass', () => {
    expect(mergeBest(undefined, 300, false)).toEqual({ points: 300, passed: false });
    expect(mergeBest({ points: 500, passed: true }, 200, false)).toEqual({ points: 500, passed: true });
  });

  it('shuffles hard options without losing the right one', () => {
    for (const t of mini.levels.hard.tasks) {
      const p = prepareTask(t, 'hard', mulberry32(7));
      expect(p.options[p.correct]).toBe(t.options[t.correct]);
    }
    const e = mini.levels.easy.tasks[0];
    if (e) expect(prepareTask(e, 'easy', mulberry32(7))).toBe(e);
  });

  it('has every task with a valid correct index', () => {
    for (const lv of Object.values(mini.levels)) {
      expect(lv.tasks).toHaveLength(lv.tasksCount);
      for (const t of lv.tasks) expect(t.options[t.correct]).toBeTruthy();
    }
  });
});

describe('prizes', () => {
  it('returns the prize record from the content', () => {
    expect(prizeFor('easy').name).toBe(mini.prizes.easy.name);
    expect(prizeFor('hard').name).toBe(mini.prizes.hard.name);
  });

  it('is applied once per level, deterministically', () => {
    const save = new SaveStore(null);
    const a = applyPrize(save, 'easy');
    expect(a).toEqual({ granted: true, coins: PRIZE_COINS.easy, flawlessBadge: false });
    expect(save.data.coins).toBe(PRIZE_COINS.easy);
    expect(save.hasFlag('prize.easy')).toBe(true);
    expect(save.hasFlag('unlock.lesson02')).toBe(true);
    const b = applyPrize(save, 'easy');
    expect(b.granted).toBe(false);
    expect(save.data.coins).toBe(PRIZE_COINS.easy);
    applyPrize(save, 'medium');
    expect(save.data.coins).toBe(PRIZE_COINS.easy + PRIZE_COINS.medium);
    expect(save.hasFlag('prize.hard')).toBe(false);
  });

  it('gives the flawless badge once, only on hard', () => {
    const save = new SaveStore(null);
    expect(applyPrize(save, 'easy', { flawless: true }).flawlessBadge).toBe(false);
    expect(applyPrize(save, 'hard', { flawless: true }).flawlessBadge).toBe(true);
    expect(save.hasFlag(FLAWLESS_FLAG)).toBe(true);
    const again = applyPrize(save, 'hard', { flawless: true });
    expect(again).toEqual({ granted: false, coins: 0, flawlessBadge: false });
  });
});

describe('lesson gating', () => {
  const steps = lesson.steps;

  it('has 8 steps, each with a widget and a check', () => {
    expect(steps).toHaveLength(8);
    for (const s of steps) {
      expect(s.widget.type).toBeTruthy();
      expect(s.check.options[s.check.correct]).toBeTruthy();
    }
  });

  it('blocks next until the check is answered', () => {
    const first = steps[0];
    if (!first) throw new Error('no step');
    expect(canAdvance(first, {})).toBe(false);
    expect(canAdvance(first, { s1: true })).toBe(true);
  });

  it('resumes at the first unanswered step, and at the start when done', () => {
    expect(resumeIndex(steps, {}, false)).toBe(0);
    expect(resumeIndex(steps, { s1: true, s2: true, s3: true }, false)).toBe(3);
    expect(resumeIndex(steps, { s1: true, s2: true, s3: true }, true)).toBe(0);
    const all = Object.fromEntries(steps.map((s) => [s.id, true]));
    expect(resumeIndex(steps, all, false)).toBe(7);
  });

  it('knows the last step and clamps', () => {
    expect(isLast(7, 8)).toBe(true);
    expect(isLast(6, 8)).toBe(false);
    expect(clampStep(-3, 8)).toBe(0);
    expect(clampStep(99, 8)).toBe(7);
  });

  it('shows check options in a stable shuffled order with the right answer kept', () => {
    for (const s of steps) {
      const a = checkForDisplay(s);
      const b = checkForDisplay(s);
      expect(a).toEqual(b);
      expect(a.options[a.correct]).toBe(s.check.options[s.check.correct]);
    }
  });

  it('every widget type is one the code handles', () => {
    expect(steps.map((s) => s.widget.type)).toEqual([
      'connect_threads', 'tap_to_classify', 'network_size_chooser', 'advantage_matcher',
      'client_server_toy', 'atm_toy', 'p2p_vs_cs_toy', 'need_sorter',
    ]);
  });
});
