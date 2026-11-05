import { el } from '../dom';
import { BRIDGE_CFG, bridgeState, budgetOf, totalCost, type BEdge } from './bridge.logic';
import type { GameMount, NpcGameDef } from './framework';

/** Bridge building with Mr Benjamin: join both banks and every house with planks, using no more planks than the budget. */
const NS = 'http://www.w3.org/2000/svg';
function svg<K extends keyof SVGElementTagNameMap>(tag: K, attrs: Record<string, string | number>, text?: string): SVGElementTagNameMap[K] {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, String(v));
  if (text !== undefined) n.textContent = text;
  return n;
}

const mount: GameMount = (host, level, run) => {
  const cfg = BRIDGE_CFG[level];
  const budget = budgetOf(cfg, run.calm);
  const chosen = new Set<number>();
  let done = false;
  const timers: number[] = [];

  const root = svg('svg', { viewBox: '0 0 400 260', class: 'bridge-svg', role: 'img', 'aria-label': 'נחל עם שני גדות ובתים' });
  root.append(
    svg('rect', { x: 0, y: 0, width: 400, height: 260, fill: '#2a5d86' }),
    svg('rect', { x: 0, y: 0, width: 62, height: 260, fill: '#4a7a3c' }),
    svg('rect', { x: 338, y: 0, width: 62, height: 260, fill: '#4a7a3c' }),
  );
  const edgeEls = cfg.edges.map((e: BEdge, i: number) => {
    const a = cfg.nodes[e.a]!;
    const b = cfg.nodes[e.b]!;
    const line = svg('line', { x1: a.x, y1: a.y, x2: b.x, y2: b.y, class: 'bridge-link' });
    const hit = svg('line', { x1: a.x, y1: a.y, x2: b.x, y2: b.y, class: 'bridge-hit' });
    const mx = (a.x + b.x) / 2;
    const my = (a.y + b.y) / 2;
    const tag = svg('g', { class: 'bridge-tag' }, undefined);
    tag.append(svg('circle', { cx: mx, cy: my, r: 11 }), svg('text', { x: mx, y: my + 4.5 }, String(e.cost)));
    const toggle = (ev: Event): void => { ev.preventDefault(); flip(i); };
    hit.addEventListener('pointerdown', toggle);
    tag.addEventListener('pointerdown', toggle);
    return { line, tag, hit };
  });
  edgeEls.forEach((x) => root.append(x.line));
  edgeEls.forEach((x) => root.append(x.hit));
  edgeEls.forEach((x) => root.append(x.tag));
  cfg.nodes.forEach((n) => {
    if (n.kind === 'bank') root.append(svg('rect', { x: n.x - 14, y: n.y - 14, width: 28, height: 28, rx: 6, fill: '#7a5a34', stroke: '#e8d9a8', 'stroke-width': 2 }));
    else root.append(svg('circle', { cx: n.x, cy: n.y, r: 17, fill: '#f3e6c0', stroke: '#8a6a3c', 'stroke-width': 3 }), svg('text', { x: n.x, y: n.y + 6, class: 'bridge-house' }, '🏠'));
  });

  const status = el('div', 'npcg-status', '');
  const msg = el('div', 'npcg-status', '');
  const clear = el('button', 'btn npcg-big', 'התחילו מחדש');
  clear.type = 'button';
  clear.addEventListener('click', () => { if (!done) { chosen.clear(); paint(); } });
  const wrap = el('div', 'bridge-wrap');
  wrap.append(root);
  host.append(el('div', 'npcg-split', '', [wrap, el('div', 'npcg-side', '', [el('div', 'npcg-row', '', [clear]), status, msg])]));

  function flip(i: number): void {
    if (done) return;
    if (chosen.has(i)) chosen.delete(i); else chosen.add(i);
    paint();
    const st = bridgeState(cfg, chosen, budget);
    if (st === 'done') {
      done = true;
      msg.textContent = 'הגשר מחבר הכול. העגלה עוברת!';
      timers.push(window.setTimeout(() => run.finish({ passed: true, summary: `הגשר מוכן, ${totalCost(cfg.edges, chosen)} קרשים מתוך ${budget}` }), 900));
    } else if (st === 'over') msg.textContent = 'הכול מחובר, אבל יש יותר מדי קרשים. הורידו קישור מיותר.';
    else msg.textContent = '';
  }
  function paint(): void {
    edgeEls.forEach((x, i) => {
      x.line.classList.toggle('on', chosen.has(i));
      x.tag.classList.toggle('on', chosen.has(i));
    });
    const used = totalCost(cfg.edges, chosen);
    status.textContent = `קרשים: ${used} מתוך ${budget}`;
    status.classList.toggle('bad', used > budget);
  }
  paint();
  msg.textContent = 'חברו את שני הגדות ואת כל הבתים. המספר הוא כמות הקרשים.';
  return () => {
    done = true;
    timers.forEach((t) => window.clearTimeout(t));
  };
};

export const BRIDGE_GAME: NpcGameDef = {
  id: 'bridge_build',
  title: 'בניית גשר',
  rules: 'חברו את שני גדות הנחל ואת כל הבתים בקישורים. לכל קישור יש מספר קרשים, והקרשים מוגבלים. כשהכול מחובר, העגלה עוברת.',
  controls: 'נוגעים בקישור כדי להניח אותו, ושוב כדי להסיר.',
  mount,
  rewards: {
    easy: { coins: 8 },
    medium: { coins: 12, food: { key: 'food_honey', name: 'טיפות דבש', n: 1 } },
    hard: { coins: 20, keepsake: { flag: 'decor.little_bridge', name: 'גשר מיניאטורי' } },
  },
};
