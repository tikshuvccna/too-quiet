import { el } from '../dom';
import type { GameDef, RoundApi } from './gameShell';
import { lessonIds, loadBundle } from './registry';
import type { ChoiceQuestion, Level, MinigameData } from './types';

export interface BossRound { lessonNo: number; lessonTitle: string; q: ChoiceQuestion }

/**
 * The Head asks everything that was learned. Each phase is one lesson's topic (one easy, one medium and one hard
 * question from that lesson's summary questions). Nothing is lost for a wrong answer except a heart,
 * and the Head calms down as the answers get right.
 */
export function bossRounds(): BossRound[] {
  const out: BossRound[] = [];
  for (const id of lessonIds()) {
    const b = loadBundle(id);
    if (!b) continue;
    const no = Number(id.replace(/^lesson/, ''));
    const pool = b.quiz.questions.filter((q): q is ChoiceQuestion => q.type !== 'order');
    for (const d of ['easy', 'medium', 'hard'] as const) {
      const pick = pool.find((q) => q.difficulty === d && !out.some((r) => r.q.id === q.id && r.lessonNo === no)) ?? pool.find((q) => !out.some((r) => r.q.id === q.id && r.lessonNo === no));
      if (pick) out.push({ lessonNo: no, lessonTitle: b.lesson.title, q: pick });
    }
  }
  return out;
}

export const BOSS_LEVEL: Level = 'hard';

export function bossGame(rounds: BossRound[] = bossRounds()): GameDef {
  const info = { count: rounds.length, lives: 5, timeLimit: null, blurb: `${rounds.length} שאלות מכל מה שלמדתם. 5 חיים, בלי שעון. הראש נרגע עם כל תשובה נכונה.` };
  return {
    title: 'הראש',
    intro: 'ענן ענק של חוטים מביט מלמעלה, ושואל. הוא לא כועס: הוא רוצה לדעת אם הבנתם איך הרשת בנויה. ענו נכון, והוא נרגע.',
    howTo: ['כל שאלה היא מנושא אחר ממה שלמדתם.', 'תשובה נכונה מרגיעה את הראש. טעות עולה בלב אחד, בלי עונש אחר, ואפשר לנסות שוב מההתחלה.'],
    levels: { easy: info, medium: info, hard: info },
    mountRound: (_level, index, host, api) => mountBossRound(rounds[index] as BossRound, index, rounds.length, host, api),
  };
}

function mountBossRound(r: BossRound, index: number, total: number, host: HTMLElement, api: RoundApi): () => void {
  const calm = el('div', 'boss-calm', '', [el('i', 'boss-calm-fill')]);
  (calm.firstElementChild as HTMLElement).style.width = `${(index / total) * 100}%`;
  const buttons = r.q.options.map((text, i) => {
    const b = el('button', 'lrn-opt lrn-big-opt', text);
    b.type = 'button';
    b.addEventListener('click', () => pick(i));
    return b;
  });
  host.append(
    el('div', 'lrn-wire-banner', '', [el('span', 'lrn-banner-n', `שיעור ${r.lessonNo}: ${r.lessonTitle}`), el('p', '', r.q.q)]),
    calm,
    el('div', 'lrn-opts', '', buttons),
  );
  let done = false;
  function pick(i: number): void {
    if (done) return;
    done = true;
    buttons.forEach((b, k) => { b.disabled = true; b.classList.toggle('right', k === r.q.correct); });
    if (i !== r.q.correct) buttons[i]?.classList.add('wrong');
    (calm.firstElementChild as HTMLElement).style.width = `${((index + (i === r.q.correct ? 1 : 0)) / total) * 100}%`;
    api.resolve(i === r.q.correct, r.q.explain);
  }
  const onKey = (e: KeyboardEvent): void => {
    const n = Number(e.key);
    if (n >= 1 && n <= buttons.length) pick(n - 1);
  };
  document.addEventListener('keydown', onKey);
  return () => document.removeEventListener('keydown', onKey);
}

export function bossData(): MinigameData {
  const prize = { name: 'גלימת הראש', type: 'prestige', description: 'הראש נרגע, והחוטים בעמק מזמזמים אחרת.', effect: 'הילה בצבע אור הבוקר קבועה סביב הדמות, ותג "מי שהבין את הרשת".' };
  return {
    id: 'minigameboss', title: 'הראש', story: '', rules: [], source: '', needsTeacher: [],
    levels: { easy: { lives: 5, timeLimitPerTaskSec: null, tasksCount: 0, passRule: '', tasks: [] }, medium: { lives: 5, timeLimitPerTaskSec: null, tasksCount: 0, passRule: '', tasks: [] }, hard: { lives: 5, timeLimitPerTaskSec: null, tasksCount: 0, passRule: '', tasks: [] } },
    prizes: { principles: [], easy: prize, medium: prize, hard: prize },
  } as unknown as MinigameData;
}
