import { el } from '../dom';
import { audio } from '../../audio/audio';
import { shortCard } from '../shorts';
import type { SaveStore } from '../../core/save';
import type { LessonData, LessonStep } from './types';
import { canAdvance, checkForDisplay, clampStep, dotState, isLast, resumeIndex } from './lessonLogic';
import { confirmDialog, createOverlay, sanitizeInto, wrapTables } from './overlay';
import { mountWidget } from './widgets';

/**
 * The lesson screen: one step at a time, text then a toy, then a comprehension check that must be answered
 * before moving on. Progress is kept as "checks answered", so reopening resumes at the first open step.
 */
export function openLesson(data: LessonData, save: SaveStore, opts: { onClose(done: boolean): void }): () => void {
  const ov = createOverlay('lrn-lesson');
  const prog = save.lesson(data.id);
  const steps = data.steps;
  const attempts = new Map<string, number>();
  let index = resumeIndex(steps, prog.checks, prog.done);
  let widgetCleanup: (() => void) | null = null;
  let closed = false;

  const title = el('h1', 'lrn-title', data.title);
  const dots = el('div', 'lrn-dots');
  const closeBtn = el('button', 'lrn-x', '×');
  closeBtn.type = 'button';
  closeBtn.setAttribute('aria-label', 'יציאה מהשיעור');
  const head = el('header', 'lrn-head', '', [el('div', 'lrn-head-main', '', [title, dots]), closeBtn]);
  const body = el('main', 'lrn-body');
  const hint = el('span', 'lrn-foot-hint', '');
  const prev = el('button', 'btn', '→ הקודם');
  const next = el('button', 'btn primary', 'הבא ←');
  prev.type = 'button';
  next.type = 'button';
  const foot = el('footer', 'lrn-foot', '', [prev, hint, next]);
  ov.root.append(head, body, foot);

  const answered = (s: LessonStep): boolean => canAdvance(s, prog.checks);
  /** Furthest step the learner may open: everything up to and including the first unanswered one. */
  const reach = (): number => {
    const i = steps.findIndex((s) => !answered(s));
    return i === -1 ? steps.length - 1 : i;
  };

  function renderDots(): void {
    dots.replaceChildren(
      ...steps.map((s, i) => {
        const d = el('button', `lrn-dot ${dotState(i, index, prog.checks, steps)}`);
        d.type = 'button';
        d.setAttribute('aria-label', `שלב ${i + 1}: ${s.title}`);
        d.disabled = i > reach();
        d.addEventListener('click', () => go(i));
        return d;
      }),
    );
  }

  function renderFooter(): void {
    const s = steps[index];
    if (!s) return;
    const ok = answered(s);
    const last = isLast(index, steps.length);
    prev.disabled = index === 0;
    next.disabled = !ok;
    next.textContent = last ? 'סיום השיעור ✓' : 'הבא ←';
    hint.textContent = ok ? `שלב ${index + 1} מתוך ${steps.length}` : 'ענו על שאלת ההבנה כדי להמשיך';
    next.classList.toggle('pulse', ok);
  }

  function renderCheck(step: LessonStep): HTMLElement {
    const c = checkForDisplay(step);
    const fb = el('div', 'lrn-feedback');
    fb.setAttribute('aria-live', 'polite');
    const opts = c.options.map((text, i) => {
      const b = el('button', 'lrn-opt', text);
      b.type = 'button';
      b.addEventListener('click', () => choose(i));
      return b;
    });
    const recap = el('div', 'lrn-recap');
    const box = el('section', 'lrn-check', '', [el('h3', '', 'בדקו את עצמכם'), el('p', 'lrn-q', c.q), el('div', 'lrn-opts', '', opts), fb, recap]);

    function lock(): void {
      opts.forEach((o, i) => { o.disabled = true; o.classList.toggle('right', i === c.correct); });
      fb.className = 'lrn-feedback good';
      fb.textContent = `נכון! ${c.explain}`;
      if (isLast(index, steps.length) && step.recap) {
        recap.replaceChildren(el('h4', '', 'מה למדנו'), el('ul', '', '', step.recap.map((r) => el('li', '', r))));
      }
    }

    function choose(i: number): void {
      attempts.set(step.id, (attempts.get(step.id) ?? 0) + 1);
      const o = opts[i];
      audio.sfx(i === c.correct ? 'success' : 'fail');
      if (i === c.correct) {
        prog.checks[step.id] = true;
        save.save();
        lock();
        renderDots();
        renderFooter();
        return;
      }
      o?.classList.remove('shake');
      void o?.offsetWidth;
      o?.classList.add('wrong', 'shake');
      fb.className = 'lrn-feedback warn';
      fb.textContent = `לא בדיוק. ${c.explain} אפשר לנסות שוב.`;
    }

    if (answered(step)) lock();
    return box;
  }

  function renderVideo(step: LessonStep): HTMLElement | '' {
    if (step.short) return shortCard(step.short) ?? '';
    if (!step.video) return '';
    const v = el('video', 'lrn-video');
    v.src = `${import.meta.env.BASE_URL}${step.video.src}`;
    v.controls = true;
    v.preload = 'none';
    v.playsInline = true;
    return el('section', 'lrn-short', '', [el('h3', '', step.video.title), v]) as HTMLElement;
  }

  function render(): void {
    const step = steps[index];
    if (!step) return;
    widgetCleanup?.();
    widgetCleanup = null;
    const text = el('div', 'lrn-text');
    sanitizeInto(text, step.html);
    wrapTables(text);
    const host = el('div', 'lw-host');
    const widgetBox = el('section', 'lrn-widget', '', [el('h3', '', step.widget.title), host]);
    const done = el('p', 'lrn-widget-done', '');
    widgetBox.append(done);
    body.replaceChildren(el('h2', 'lrn-step-title', step.title), text, renderVideo(step), widgetBox, renderCheck(step));
    widgetCleanup = mountWidget(step.widget, host, {
      done: () => { widgetBox.classList.add('complete'); done.textContent = '✓ עשיתם את זה'; },
    });
    body.scrollTop = 0;
    renderDots();
    renderFooter();
  }

  function go(i: number): void {
    index = clampStep(Math.min(i, reach()), steps.length);
    render();
  }

  function finish(): void {
    prog.done = true;
    save.recomputePower();
    save.save();
    teardown();
    opts.onClose(true);
  }

  function advance(): void {
    const s = steps[index];
    if (!s || !answered(s)) return;
    if (isLast(index, steps.length)) finish();
    else go(index + 1);
  }

  async function askClose(): Promise<void> {
    if (await confirmDialog(ov.root, 'לצאת מהשיעור? ההתקדמות נשמרת ואפשר להמשיך אחר כך.', 'כן, לצאת', 'להמשיך בשיעור')) {
      teardown();
      opts.onClose(false);
    }
  }

  function teardown(): void {
    if (closed) return;
    closed = true;
    widgetCleanup?.();
    document.removeEventListener('keydown', onKey, true);
    ov.destroy();
  }

  function onKey(e: KeyboardEvent): void {
    if (ov.root.querySelector('.lrn-confirm')) return;
    const t = e.target as HTMLElement | null;
    const typing = t instanceof HTMLInputElement || t instanceof HTMLTextAreaElement;
    if (typing) return;
    if (e.key === 'ArrowLeft') { e.preventDefault(); advance(); }
    else if (e.key === 'ArrowRight') { e.preventDefault(); if (index > 0) go(index - 1); }
    else if (e.key === 'Enter' && !(t instanceof HTMLButtonElement)) { e.preventDefault(); advance(); }
    else if (e.key === 'Escape') { e.preventDefault(); void askClose(); }
  }

  prev.addEventListener('click', () => go(index - 1));
  next.addEventListener('click', advance);
  closeBtn.addEventListener('click', () => { void askClose(); });
  document.addEventListener('keydown', onKey, true);
  render();
  next.focus({ preventScroll: true });

  return () => teardown();
}
