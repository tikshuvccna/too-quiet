import { el } from '../dom';
import { audio } from '../../audio/audio';
import type { SaveStore } from '../../core/save';
import type { QuizData, QuizQuestion, QuizResult } from './types';
import { PASS_MIN_CORRECT, POINTS, type Outcome, isOrderCorrect, pointsFor, resolveAttempt, tally, togglePick } from './quizLogic';
import { confirmDialog, createOverlay } from './overlay';
import { shuffleOptions } from './util';

const DIFF_LABEL = { easy: 'קל', medium: 'בינוני', hard: 'קשה' } as const;

/** Quiz screen: one question at a time, one retry for half points, explanation after every answer, results at the end. */
export function openQuiz(data: QuizData, save: SaveStore, opts: { onClose(result: QuizResult): void; lessonId?: string }): () => void {
  const ov = createOverlay('lrn-quiz');
  const qs = data.questions;
  let qi = 0;
  let outcomes: (Outcome | undefined)[] = [];
  let closed = false;

  const title = el('h1', 'lrn-title', data.title);
  const meta = el('span', 'lrn-meta', '');
  const closeBtn = el('button', 'lrn-x', '×');
  closeBtn.type = 'button';
  closeBtn.setAttribute('aria-label', 'יציאה מהחידון');
  const bar = el('i', 'lrn-bar-fill');
  const head = el('header', 'lrn-head', '', [el('div', 'lrn-head-main', '', [title, meta, el('div', 'lrn-bar', '', [bar])]), closeBtn]);
  const body = el('main', 'lrn-body');
  ov.root.append(head, body);

  const current = (): ReturnType<typeof tally> => tally(qs, outcomes);

  function start(): void {
    qi = 0;
    outcomes = [];
    showQuestion();
  }

  function showQuestion(): void {
    const q = qs[qi];
    if (!q) { showResults(); return; }
    meta.textContent = `שאלה ${qi + 1} מתוך ${qs.length} · ${current().score} נקודות`;
    bar.style.width = `${(qi / qs.length) * 100}%`;
    body.scrollTop = 0;
    body.replaceChildren(q.type === 'order' ? orderCard(q) : choiceCard(q));
  }

  function header(q: QuizQuestion): HTMLElement {
    return el('div', 'lrn-qhead', '', [
      el('span', `lrn-badge ${q.difficulty}`, `${DIFF_LABEL[q.difficulty]} · ${POINTS[q.difficulty]} נק׳`),
      el('p', 'lrn-q', q.q),
    ]);
  }

  /** Shows the explanation and the way on. */
  function conclude(card: HTMLElement, fb: HTMLElement, q: QuizQuestion, outcome: Outcome): void {
    outcomes[qi] = outcome;
    const pts = pointsFor(q.difficulty, outcome);
    fb.className = `lrn-feedback ${outcome === 'miss' ? 'warn' : 'good'}`;
    fb.textContent = `${outcome === 'miss' ? 'לא הפעם.' : outcome === 'retry' ? `נכון, בניסיון השני: +${pts}.` : `נכון! +${pts}.`} ${q.explain}`;
    meta.textContent = `שאלה ${qi + 1} מתוך ${qs.length} · ${current().score} נקודות`;
    const more = el('button', 'btn primary lrn-more', qi + 1 >= qs.length ? 'לתוצאות ←' : 'השאלה הבאה ←');
    more.type = 'button';
    more.addEventListener('click', () => { qi++; showQuestion(); });
    card.append(more);
    more.focus({ preventScroll: false });
  }

  function choiceCard(q: Extract<QuizQuestion, { type: 'mcq' | 'tf' }>): HTMLElement {
    const sh = q.type === 'mcq' ? shuffleOptions(q.options, q.correct, Math.random) : { options: q.options, correct: q.correct };
    let attempt = 1;
    const fb = el('div', 'lrn-feedback');
    fb.setAttribute('aria-live', 'polite');
    const card = el('section', `lrn-qcard ${q.type}`);
    const btns = sh.options.map((text, i) => {
      const b = el('button', 'lrn-opt', text);
      b.type = 'button';
      b.addEventListener('click', () => {
        const r = resolveAttempt(attempt, i === sh.correct);
        audio.sfx(i === sh.correct ? 'success' : 'fail');
        if (r.kind === 'again') {
          attempt++;
          b.disabled = true;
          b.classList.add('wrong', 'shake');
          fb.className = 'lrn-feedback warn';
          fb.textContent = 'לא בדיוק. נסו שוב: ניסיון שני מזכה בחצי מהנקודות.';
          return;
        }
        btns.forEach((x, k) => { x.disabled = true; x.classList.toggle('right', k === sh.correct); });
        if (i !== sh.correct) b.classList.add('wrong');
        conclude(card, fb, q, r.outcome);
      });
      return b;
    });
    card.append(header(q), el('div', 'lrn-opts', '', btns), fb);
    return card;
  }

  function orderCard(q: Extract<QuizQuestion, { type: 'order' }>): HTMLElement {
    let attempt = 1;
    let picked: number[] = [];
    const fb = el('div', 'lrn-feedback');
    fb.setAttribute('aria-live', 'polite');
    const card = el('section', 'lrn-qcard order');
    const items = q.options.map((text, i) => {
      const num = el('span', 'lrn-num', '');
      const b = el('button', 'lrn-opt lrn-item', '', [num, el('span', '', text)]);
      b.type = 'button';
      b.addEventListener('click', () => { picked = togglePick(picked, i); paint(); });
      return { b, num };
    });
    const check = el('button', 'btn primary', 'בדיקה');
    const clear = el('button', 'btn', 'ניקוי');
    check.type = 'button';
    clear.type = 'button';
    clear.addEventListener('click', () => { picked = []; paint(); });

    function paint(): void {
      items.forEach(({ b, num }, i) => {
        const pos = picked.indexOf(i);
        b.classList.toggle('picked', pos >= 0);
        num.textContent = pos >= 0 ? String(pos + 1) : '';
      });
      check.disabled = picked.length !== q.options.length;
    }

    check.addEventListener('click', () => {
      const r = resolveAttempt(attempt, isOrderCorrect(picked, q.correct));
      if (r.kind === 'again') {
        attempt++;
        picked = [];
        paint();
        card.classList.remove('shake');
        void card.offsetWidth;
        card.classList.add('shake');
        fb.className = 'lrn-feedback warn';
        fb.textContent = 'הסדר עדיין לא נכון. נסו שוב: ניסיון שני מזכה בחצי מהנקודות.';
        return;
      }
      picked = r.outcome === 'miss' ? [...q.correct] : picked;
      paint();
      items.forEach(({ b }) => { b.disabled = true; });
      check.remove();
      clear.remove();
      conclude(card, fb, q, r.outcome);
    });

    card.append(header(q), el('p', 'lrn-instruction', 'לחצו על השלבים לפי הסדר: הראשון קודם. לחיצה נוספת מבטלת.'), el('div', 'lrn-opts', '', items.map((x) => x.b)), el('div', 'lrn-row', '', [clear, check]), fb);
    paint();
    return card;
  }

  function showResults(): void {
    const t = current();
    const life = save.lesson(lessonId());
    life.quizBest = Math.max(life.quizBest, t.score);
    life.quizPassed = life.quizPassed || t.passed;
    save.save();
    meta.textContent = `${t.score} מתוך ${t.max}`;
    bar.style.width = '100%';
    const rows = qs.map((q, i) => {
      const o = outcomes[i] ?? 'miss';
      return el('li', `lrn-sum ${o}`, '', [
        el('span', 'lrn-sum-ic', o === 'miss' ? '×' : '✓'),
        el('span', 'lrn-sum-q', q.q),
        el('span', 'lrn-sum-pts', o === 'retry' ? `${pointsFor(q.difficulty, o)} (ניסיון שני)` : String(pointsFor(q.difficulty, o))),
      ]);
    });
    const again = el('button', 'btn', 'נסו שוב');
    const done = el('button', 'btn primary', 'סגירה');
    again.type = 'button';
    done.type = 'button';
    again.addEventListener('click', start);
    done.addEventListener('click', () => close());
    body.replaceChildren(el('section', 'lrn-qcard results', '', [
      el('h2', '', t.passed ? 'עברתם את החידון!' : 'עוד קצת ותגיעו'),
      el('p', 'lrn-big', `${t.score} מתוך ${t.max} נקודות`),
      el('p', 'lrn-sub', t.passed
        ? `ענו נכון על ${t.correct} מתוך ${t.total} שאלות (צריך ${PASS_MIN_CORRECT}).`
        : `ענו נכון על ${t.correct} מתוך ${t.total} שאלות. צריך ${PASS_MIN_CORRECT} כדי לעבור, ואפשר לנסות שוב בלי עונש.`),
      el('p', 'lrn-sub', `השיא שלכם: ${life.quizBest} נקודות.`),
      el('ol', 'lrn-sums', '', rows),
      el('div', 'lrn-row', '', [again, done]),
    ]));
    done.focus();
  }

  function lessonId(): string {
    // quiz ids look like "quiz01" and belong to "lesson01"
    return opts.lessonId ?? data.id.replace(/^quiz/, 'lesson');
  }

  function close(): void {
    if (closed) return;
    closed = true;
    document.removeEventListener('keydown', onKey, true);
    ov.destroy();
    const t = current();
    opts.onClose({ score: t.score, max: t.max, passed: t.passed });
  }

  function teardown(): void {
    if (closed) return;
    closed = true;
    document.removeEventListener('keydown', onKey, true);
    ov.destroy();
  }

  async function askClose(): Promise<void> {
    if (qi >= qs.length) { close(); return; }
    if (await confirmDialog(ov.root, 'לצאת מהחידון? התוצאה של הניסיון הזה לא תישמר.', 'כן, לצאת', 'להמשיך בחידון')) {
      closed = true;
      document.removeEventListener('keydown', onKey, true);
      ov.destroy();
      opts.onClose({ score: 0, max: current().max, passed: false });
    }
  }

  function onKey(e: KeyboardEvent): void {
    if (ov.root.querySelector('.lrn-confirm')) return;
    if (e.key === 'Escape') { e.preventDefault(); void askClose(); }
  }

  closeBtn.addEventListener('click', () => { void askClose(); });
  document.addEventListener('keydown', onKey, true);
  start();
  return () => teardown();
}
