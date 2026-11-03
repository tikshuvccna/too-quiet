import { el } from '../dom';
import type { AdvantageSpec, ClassifySpec, ConnectSpec, NeedSpec, SizeSpec } from './types';
import { allConnected, findPath, isRight, needsHint, splitEdge, toggleEdge } from './widgetLogic';
import { type Mount, Runner, bannerEl, envelope, lerp, node, reducedMotion, say, setPos, svg } from './widgetKit';
import { hashString, mulberry32, shuffled } from './util';

const ICONS: Record<string, string> = { tablet: '\u{1F4F1}', phone: '\u{1F4DE}', printer: '\u{1F5A8}️', pc: '\u{1F4BB}' };

/**
 * connect_threads. Interpretation: two modes, "connect" and "send", switched by a segmented control, so a tap
 * on a device never means two things at once. The goal (and api.done) is a single connected group; sending
 * is optional practice but it is what shows why the threads matter.
 */
export const connectThreads: Mount<ConnectSpec> = (host, spec, api) => {
  const run = new Runner();
  const W = 160;
  const H = 100;
  const nodes = spec.nodes;
  const byId = new Map(nodes.map((n) => [n.id, n]));
  const pt = (id: string): { x: number; y: number } => {
    const n = byId.get(id);
    return { x: (n?.x ?? 0) * W, y: (n?.y ?? 0) * H };
  };
  let edges: string[] = [];
  let mode: 'connect' | 'send' = 'connect';
  let sel: string | null = null;
  let busy = false;
  let finished = false;
  const sent = new Set<string>();

  const lines = svg('g');
  const envLayer = svg('g');
  const scene = el('div', 'lw-scene lw-scene-a', '', [svg('svg', { viewBox: `0 0 ${W} ${H}`, class: 'lw-svg' }, [lines, envLayer])]);
  const status = el('p', 'lw-status', '');
  status.setAttribute('aria-live', 'polite');
  const banner = bannerEl('רשת תקשורת: מארחים וציוד מחוברים, ויכולים לתקשר');
  banner.hidden = true;

  const buttons = new Map<string, HTMLButtonElement>();
  for (const n of nodes) {
    const b = el('button', 'lw-node', '', [el('span', 'lw-node-ic', ICONS[n.id] ?? '●'), el('span', 'lw-node-lb', n.label), el('span', 'lw-node-ok', '✓')]);
    b.type = 'button';
    Object.assign(b.style, node(n.x, n.y));
    b.addEventListener('click', () => onNode(n.id));
    buttons.set(n.id, b);
    scene.append(b);
  }

  const modeBtns = (['connect', 'send'] as const).map((m) => {
    const b = el('button', 'lw-seg', m === 'connect' ? 'חיבור חוטים' : 'שלחו שליח');
    b.type = 'button';
    b.addEventListener('click', () => setMode(m));
    return b;
  });
  const seg = el('div', 'lw-segs', '', modeBtns);

  function setMode(m: 'connect' | 'send'): void {
    mode = m;
    sel = null;
    modeBtns.forEach((b, i) => b.classList.toggle('on', (i === 0) === (m === 'connect')));
    say(status, m === 'connect' ? 'לחצו על התקן ואז על התקן אחר: נוצר חוט ביניהם. לחצו על חוט כדי למחוק אותו.' : 'בחרו מוצא ואז יעד: שליח ינסה להגיע לאורך החוטים.');
    paint();
  }

  function paint(): void {
    for (const [id, b] of buttons) {
      b.classList.toggle('sel', id === sel);
      b.classList.toggle('sent', sent.has(id));
      const linked = edges.some((e) => splitEdge(e).includes(id));
      b.classList.toggle('lonely', !linked && edges.length > 0);
    }
    lines.replaceChildren(
      ...edges.map((e) => {
        const [a, b] = splitEdge(e);
        const pa = pt(a);
        const pb = pt(b);
        const g = svg('g', { class: 'lw-edge' }, [
          svg('line', { x1: pa.x, y1: pa.y, x2: pb.x, y2: pb.y, class: 'lw-thread' }),
          svg('line', { x1: pa.x, y1: pa.y, x2: pb.x, y2: pb.y, class: 'lw-thread-hit' }),
        ]);
        g.addEventListener('click', () => {
          if (busy) return;
          edges = edges.filter((x) => x !== e);
          sent.clear();
          say(status, 'החוט נמחק.');
          paint();
        });
        return g;
      }),
    );
    const ok = allConnected(nodes.map((n) => n.id), edges);
    banner.hidden = !ok;
    if (ok && !finished) {
      finished = true;
      api.done();
    }
  }

  function onNode(id: string): void {
    if (busy) return;
    if (sel === null) {
      sel = id;
      paint();
      return;
    }
    if (sel === id) {
      sel = null;
      paint();
      return;
    }
    const from = sel;
    sel = null;
    if (mode === 'connect') {
      const r = toggleEdge(edges, from, id);
      edges = r.edges;
      sent.clear();
      say(status, r.action === 'added' ? 'חוט חדש! עכשיו אפשר לשלוח דרכו.' : r.action === 'removed' ? 'החוט נמחק.' : 'יש מקסימום 6 חוטים. מחקו חוט כדי להוסיף אחר.', r.action === 'full' ? 'warn' : '');
      paint();
    } else {
      paint();
      void sendMessenger(from, id);
    }
  }

  async function sendMessenger(from: string, to: string): Promise<void> {
    busy = true;
    const path = findPath(edges, from, to);
    const env = envelope(!path);
    envLayer.append(env);
    const a = pt(from);
    if (path) {
      say(status, 'השליח יצא לדרך...');
      const pts = path.map(pt);
      const segs = pts.length - 1;
      await run.tween(550 * segs, (p) => {
        const f = Math.min(segs - 1e-6, p * segs);
        const i = Math.floor(f);
        const p0 = pts[i];
        const p1 = pts[i + 1];
        if (p0 && p1) setPos(env, lerp(p0.x, p1.x, f - i), lerp(p0.y, p1.y, f - i));
      });
      env.remove();
      sent.add(from);
      say(status, 'ההודעה הגיעה. יש חוט, יש הודעה.', 'good');
    } else {
      say(status, 'אין חוט, אין הודעה.', 'warn');
      await run.tween(1100, (p) => {
        setPos(env, a.x + Math.cos(p * 26) * 3 * (1 - p), a.y + Math.sin(p * 26) * 3 * (1 - p) - p * 4);
        env.style.opacity = String(1 - p * p);
      });
      env.remove();
      const puff = el('div', 'lw-puff', 'אין חוט, אין הודעה');
      Object.assign(puff.style, node(byId.get(from)?.x ?? 0.5, (byId.get(from)?.y ?? 0.5) - 0.12));
      scene.append(puff);
      await run.wait(reducedMotion() ? 1800 : 1500);
      puff.remove();
    }
    busy = false;
    paint();
  }

  host.append(seg, scene, status, banner);
  setMode('connect');
  return () => run.dispose();
};

/** tap_to_classify: each item shows two buttons. A wrong answer is a gentle orange and can be changed. */
export const tapToClassify: Mount<ClassifySpec> = (host, spec, api) => {
  const total = spec.items.length;
  const right = new Set<number>();
  const prog = el('p', 'lw-progress', '');
  const updateProg = (): void => { prog.textContent = `${right.size} מתוך ${total}`; };
  updateProg();
  const list = el('div', 'lw-list');
  spec.items.forEach((item, i) => {
    const why = el('p', 'lw-why', '');
    const card = el('div', 'lw-row', '', [el('p', 'lw-row-t', item.label)]);
    const mk = (answer: 'network' | 'none', label: string): HTMLButtonElement => {
      const b = el('button', 'lw-choice', label);
      b.type = 'button';
      b.addEventListener('click', () => {
        if (right.has(i)) return;
        if (isRight(item.answer, answer)) {
          right.add(i);
          card.classList.remove('bad');
          card.classList.add('good');
          why.textContent = item.why;
          for (const x of card.querySelectorAll('button')) (x as HTMLButtonElement).disabled = true;
          b.classList.add('picked');
          updateProg();
          if (right.size === total) api.done();
        } else {
          card.classList.remove('shake');
          void card.offsetWidth;
          card.classList.add('bad', 'shake');
          why.textContent = 'לא בדיוק. אפשר לנסות שוב.';
        }
      });
      return b;
    };
    card.append(el('div', 'lw-btnrow', '', [mk('network', 'משתמש ברשת'), mk('none', 'לא משתמש ברשת')]), why);
    list.append(card);
  });
  host.append(el('p', 'lw-instruction', spec.instruction), list, prog);
  return () => undefined;
};

interface SortCard { text: string; answer: string; why: string }

/**
 * Shared by network_size_chooser and need_sorter. Interpretation: one card at a time, and the baskets are
 * the answer buttons (tap a basket). Mouse users can also drag the card onto a basket; touch drag is left out
 * on purpose, because it would fight page scrolling.
 */
function mountSorter(host: HTMLElement, cats: { id: string; label: string }[], cards: SortCard[], api: { done(): void }, doneText: string): () => void {
  const run = new Runner();
  let i = 0;
  const wrong = new Map<number, number>();
  const counts = new Map<string, number>();
  const prog = el('p', 'lw-progress', '');
  const stage = el('div', 'lw-stage');
  const feedback = el('p', 'lw-feedback', 'לחצו על הסל המתאים (או גררו אליו בעכבר).');
  feedback.setAttribute('aria-live', 'polite');
  const basketEls = new Map<string, HTMLButtonElement>();
  const baskets = el('div', `lw-baskets n${cats.length}`);
  for (const c of cats) {
    const count = el('span', 'lw-basket-n', '0');
    const b = el('button', 'lw-basket', '', [el('span', 'lw-basket-t', c.label), count]);
    b.type = 'button';
    b.dataset.cat = c.id;
    b.addEventListener('click', () => place(c.id));
    basketEls.set(c.id, b);
    baskets.append(b);
  }
  host.append(prog, stage, feedback, baskets);

  function show(): void {
    const c = cards[i];
    if (!c) {
      prog.textContent = 'סיימתם!';
      stage.replaceChildren(bannerEl(doneText));
      baskets.classList.add('off');
      for (const b of basketEls.values()) b.disabled = true;
      api.done();
      return;
    }
    prog.textContent = `כרטיס ${i + 1} מתוך ${cards.length}`;
    const card = el('div', 'lw-bigcard lw-in', c.text);
    attachDrag(card);
    stage.replaceChildren(card);
  }

  function place(cat: string): void {
    const c = cards[i];
    const card = stage.firstElementChild as HTMLElement | null;
    if (!c || !card) return;
    if (isRight(c.answer, cat)) {
      counts.set(cat, (counts.get(cat) ?? 0) + 1);
      const n = basketEls.get(cat)?.querySelector('.lw-basket-n');
      if (n) n.textContent = String(counts.get(cat));
      const b = basketEls.get(cat);
      b?.classList.remove('pop');
      void b?.offsetWidth;
      b?.classList.add('pop');
      say(feedback, `נכון! ${c.why}`, 'good');
      i++;
      show();
    } else {
      const w = (wrong.get(i) ?? 0) + 1;
      wrong.set(i, w);
      card.classList.remove('shake');
      void card.offsetWidth;
      card.classList.add('shake');
      say(feedback, needsHint(w) ? `לא בדיוק. רמז: ${c.why}` : 'לא בדיוק, נסו סל אחר. אין עונש.', 'warn');
    }
  }

  function attachDrag(card: HTMLElement): void {
    card.addEventListener('pointerdown', (e) => {
      if (e.pointerType === 'touch') return;
      const sx = e.clientX;
      const sy = e.clientY;
      let moved = false;
      card.setPointerCapture(e.pointerId);
      const basketAt = (x: number, y: number): HTMLElement | undefined =>
        document.elementsFromPoint(x, y).find((n) => n instanceof HTMLElement && n.classList.contains('lw-basket')) as HTMLElement | undefined;
      const move = (ev: PointerEvent): void => {
        if (!moved && Math.hypot(ev.clientX - sx, ev.clientY - sy) > 6) {
          moved = true;
          card.classList.add('dragging');
        }
        if (!moved) return;
        card.style.transform = `translate(${ev.clientX - sx}px, ${ev.clientY - sy}px) rotate(-2deg)`;
        const over = basketAt(ev.clientX, ev.clientY);
        for (const b of basketEls.values()) b.classList.toggle('hover', b === over);
      };
      const end = (ev: PointerEvent): void => {
        card.removeEventListener('pointermove', move);
        card.removeEventListener('pointerup', end);
        card.removeEventListener('pointercancel', end);
        const target = moved && ev.type === 'pointerup' ? basketAt(ev.clientX, ev.clientY) : undefined;
        card.style.transform = '';
        card.classList.remove('dragging');
        for (const b of basketEls.values()) b.classList.remove('hover');
        if (target?.dataset.cat) place(target.dataset.cat);
      };
      card.addEventListener('pointermove', move);
      card.addEventListener('pointerup', end);
      card.addEventListener('pointercancel', end);
    });
  }

  show();
  return () => run.dispose();
}

export const networkSizeChooser: Mount<SizeSpec> = (host, spec, api) =>
  mountSorter(host, spec.categories, spec.scenarios, api, 'כל הרשתות במקום. עכשיו אתם יודעים להבחין ביניהן.');

export const needSorter: Mount<NeedSpec> = (host, spec, api) =>
  mountSorter(host, spec.choices.map((c) => ({ id: c, label: c })), spec.scenarios, api, 'לכל צורך רשת אחרת: זו הבחירה הנכונה, לא ״טוב״ מול ״רע״.');

/**
 * advantage_matcher. Interpretation: tap an example and then an advantage (either order). A correct pair
 * locks with a shared colour; a wrong tap shakes and, after two misses on one example, the right advantage
 * glows. Dragging threads is replaced by taps, which the spec allows.
 */
export const advantageMatcher: Mount<AdvantageSpec> = (host, spec, api) => {
  const pairs = spec.pairs;
  const order = shuffled(spec.advantages.map((_, i) => i), mulberry32(hashString(pairs[0]?.example ?? 'adv')));
  const matched = new Map<number, number>();
  const wrong = new Map<number, number>();
  let selEx: number | null = null;
  let selAdv: number | null = null;
  const status = el('p', 'lw-status', 'בחרו דוגמה ואז את היתרון שמתאים לה.');
  status.setAttribute('aria-live', 'polite');

  const exBtns = pairs.map((p, i) => {
    const b = el('button', 'lw-pairbtn', '', [el('span', 'lw-pair-t', p.example), el('span', 'lw-pair-adv', '')]);
    b.type = 'button';
    b.addEventListener('click', () => { selEx = selEx === i ? null : i; tryJudge(); paint(); });
    return b;
  });
  const advBtns = order.map((ai) => {
    const b = el('button', 'lw-pairbtn lw-advbtn', spec.advantages[ai] ?? '');
    b.type = 'button';
    b.addEventListener('click', () => { selAdv = selAdv === ai ? null : ai; tryJudge(); paint(); });
    return { ai, b };
  });

  const adv = (ai: number | null): string => (ai === null ? '' : (spec.advantages[ai] ?? ''));

  function tryJudge(): void {
    if (selEx === null || selAdv === null) return;
    const ex = selEx;
    const ai = selAdv;
    const pair = pairs[ex];
    selEx = null;
    selAdv = null;
    if (!pair) return;
    if (isRight(pair.advantage, adv(ai))) {
      matched.set(ex, ai);
      say(status, 'חיבור נכון! החוט נשאר זוהר.', 'good');
      if (matched.size === pairs.length) {
        say(status, 'כל הדוגמאות מחוברות ליתרונות שלהן.', 'good');
        api.done();
      }
    } else {
      wrong.set(ex, (wrong.get(ex) ?? 0) + 1);
      say(status, needsHint(wrong.get(ex) ?? 0) ? 'עוד לא. היתרון הנכון מהבהב עכשיו.' : 'לא מתאים. נסו שוב, בלי נקודות שליליות.', 'warn');
      for (const b of [exBtns[ex], advBtns.find((x) => x.ai === ai)?.b]) {
        b?.classList.remove('shake');
        void b?.offsetWidth;
        b?.classList.add('shake');
      }
    }
  }

  function paint(): void {
    exBtns.forEach((b, i) => {
      const m = matched.get(i);
      b.disabled = m !== undefined;
      b.classList.toggle('sel', selEx === i);
      b.className = b.className.replace(/ lw-c\d/g, '');
      const slot = b.querySelector('.lw-pair-adv');
      if (m !== undefined) {
        b.classList.add('locked', `lw-c${i % 6}`);
        if (slot) slot.textContent = adv(m);
      }
    });
    const hinted = new Set<string>();
    for (const [ex, n] of wrong) {
      const p = pairs[ex];
      if (needsHint(n) && p && !matched.has(ex)) hinted.add(p.advantage);
    }
    for (const { ai, b } of advBtns) {
      const owner = [...matched].find(([, a]) => a === ai)?.[0];
      b.disabled = owner !== undefined;
      b.classList.toggle('sel', selAdv === ai);
      b.className = b.className.replace(/ lw-c\d/g, '');
      if (owner !== undefined) b.classList.add('locked', `lw-c${owner % 6}`);
      b.classList.toggle('glow', hinted.has(adv(ai)) && owner === undefined);
    }
  }

  host.append(
    el('div', 'lw-cols', '', [el('div', 'lw-col', '', exBtns), el('div', 'lw-col', '', advBtns.map((x) => x.b))]),
    status,
  );
  paint();
  return () => undefined;
};
