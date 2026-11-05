import { el } from '../dom';
import type { GameDef, RoundApi } from './gameShell';
import type { Level } from './types';
import { type TopologyData, type TopologyRound, cutOff, survivors } from './topologyLogic';

type LevelBase = { lives: number; timeLimitPerTaskSec: number | null };
const LEVELS_3: Level[] = ['easy', 'medium', 'hard'];

function levelsOf<T extends LevelBase>(data: { levels: Record<Level, T> }, count: (l: T) => number, noun: string): GameDef['levels'] {
  const out = {} as GameDef['levels'];
  for (const lv of LEVELS_3) {
    const l = data.levels[lv];
    out[lv] = {
      count: count(l),
      lives: l.lives,
      timeLimit: l.timeLimitPerTaskSec,
      blurb: `${count(l)} ${noun}. ${l.timeLimitPerTaskSec ? `${l.timeLimitPerTaskSec} שניות לכל אחד. ` : 'בלי הגבלת זמן. '}${l.lives} חיים.`,
    };
  }
  return out;
}

/* ------------------------------------------------------------------ belt sorter ------------------------------------------------------------------ */

export interface SorterData {
  id: string;
  title: string;
  intro: string;
  bins: Array<{ id: string; label: string }>;
  levels: Record<Level, LevelBase & { items: Array<{ label: string; bin: string; why: string }> }>;
}

const BIN_COLORS = ['#ff9f7a', '#7ad6ff', '#c6a2ff', '#ffd36b'];

/** Cards slide down a belt; send each one to the right basket before it reaches the end. */
export function sorterGame(data: SorterData): GameDef {
  return {
    title: data.title,
    intro: data.intro,
    howTo: ['כרטיס גולש על הסרט. לחצו על הסל שמתאים לו לפני שהוא מגיע לקצה.', `אפשר גם עם המקשים 1 עד ${data.bins.length}.`],
    levels: levelsOf(data, (l) => l.items.length, 'כרטיסים'),
    mountRound: (level, index, host, api) => mountSorterRound(data, data.levels[level].items[index] as SorterData['levels']['easy']['items'][number], host, api),
  };
}

function mountSorterRound(data: SorterData, item: { label: string; bin: string; why: string }, host: HTMLElement, api: RoundApi): () => void {
  const card = el('div', 'srt-card', item.label);
  const belt = el('div', 'srt-belt', '', [el('div', 'srt-lane'), card]);
  const bins = data.bins.map((b, i) => {
    const btn = el('button', 'btn srt-bin', `${i + 1}. ${b.label}`);
    btn.type = 'button';
    btn.style.borderColor = BIN_COLORS[i % BIN_COLORS.length] as string;
    btn.addEventListener('click', () => pick(b.id));
    return btn;
  });
  host.append(belt, el('div', 'npcg-row', '', bins));
  let done = false;
  function pick(id: string | null): void {
    if (done) return;
    done = true;
    bins.forEach((b) => (b.disabled = true));
    const ok = id === item.bin;
    const right = data.bins.find((b) => b.id === item.bin)?.label ?? '';
    card.classList.add(ok ? 'srt-ok' : 'srt-bad');
    api.resolve(ok, ok ? item.why : `${id === null ? 'הכרטיס הגיע לקצה. ' : ''}"${item.label}" שייך ל"${right}". ${item.why}`, true);
  }
  api.onTimeout(() => pick(null));
  const onKey = (e: KeyboardEvent): void => {
    const n = Number(e.key);
    if (n >= 1 && n <= data.bins.length) pick((data.bins[n - 1] as { id: string }).id);
  };
  document.addEventListener('keydown', onKey);
  let raf = 0;
  const tick = (): void => {
    raf = requestAnimationFrame(tick);
    const limit = api.timeLimit ?? 14;
    const p = Math.min(1, api.timeLimit ? api.elapsed() / limit : Math.min(0.55, api.elapsed() / 20));
    card.style.top = `${6 + p * 62}%`;
  };
  raf = requestAnimationFrame(tick);
  return () => {
    cancelAnimationFrame(raf);
    document.removeEventListener('keydown', onKey);
  };
}

/* ------------------------------------------------------------------ topology ------------------------------------------------------------------ */

/** A network is drawn, one thing breaks, and the player taps the devices that lose contact with the target. */
export function topologyGame(data: TopologyData): GameDef {
  return {
    title: data.title,
    intro: data.intro,
    howTo: ['מופיעה רשת, ומשהו בה נשבר (חוט חתוך או מכשיר שנפל).', 'לחצו על כל המכשירים שמאבדים קשר עם היעד המסומן בזהב, ואז על "בדקו".'],
    levels: levelsOf(data, (l) => l.rounds.length, 'סיבובים'),
    mountRound: (level, index, host, api) => mountTopologyRound(data.levels[level].rounds[index] as TopologyRound, host, api),
  };
}

function mountTopologyRound(round: TopologyRound, host: HTMLElement, api: RoundApi): () => void {
  const canvas = el('canvas', 'lrn-canvas');
  const stage = el('div', 'lrn-wire-stage', '', [canvas]);
  const checkBtn = el('button', 'btn primary', 'בדקו');
  checkBtn.type = 'button';
  const msg = el('div', 'lrn-wire-msg', 'סמנו את המכשירים שמאבדים קשר עם היעד. אם אף אחד לא מאבד, לחצו על "בדקו" בלי לסמן.');
  host.append(el('div', 'lrn-wire-banner', '', [el('p', '', round.text)]), stage, msg, el('div', 'lrn-row lrn-wire-controls', '', [checkBtn]));

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

  const picked = new Set<string>();
  const expected = new Set(cutOff(round));
  const { nodes: alive, links: liveLinks } = survivors(round);
  let done = false;
  const pos = (id: string): [number, number] => {
    const n = round.nodes.find((x) => x.id === id) as { x: number; y: number };
    return [n.x * W, n.y * H];
  };
  const R = (): number => Math.max(24, Math.min(W, H) * 0.075);

  canvas.addEventListener('pointerdown', (e) => {
    if (done) return;
    const r = stage.getBoundingClientRect();
    const x = e.clientX - r.left;
    const y = e.clientY - r.top;
    for (const n of round.nodes) {
      if (n.kind !== 'device' || n.id === round.target || !alive.has(n.id)) continue;
      const [nx, ny] = pos(n.id);
      if (Math.hypot(x - nx, y - ny) < R() * 1.2) {
        if (picked.has(n.id)) picked.delete(n.id);
        else picked.add(n.id);
        return;
      }
    }
  });

  function check(): void {
    if (done) return;
    done = true;
    checkBtn.remove();
    const ok = picked.size === expected.size && [...picked].every((id) => expected.has(id));
    const names = [...expected].map((id) => round.nodes.find((n) => n.id === id)?.label).join(', ');
    api.resolve(ok, ok ? round.why : `${expected.size ? `מאבדים קשר: ${names}.` : 'אף מכשיר לא מאבד קשר.'} ${round.why}`);
  }
  checkBtn.addEventListener('click', check);
  api.onTimeout(check);

  const c = canvas.getContext('2d') as CanvasRenderingContext2D;
  let raf = 0;
  let t = 0;
  let prev = performance.now();
  const frame = (now: number): void => {
    raf = requestAnimationFrame(frame);
    t += Math.min(0.25, (now - prev) / 1000);
    prev = now;
    c.setTransform(dpr, 0, 0, dpr, 0, 0);
    const g = c.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#2a2468'); g.addColorStop(1, '#6a5aa8');
    c.fillStyle = g;
    c.fillRect(0, 0, W, H);
    // links: working ones glow, the failed one is drawn broken
    for (const [a, b] of round.links) {
      const [ax, ay] = pos(a);
      const [bx, by] = pos(b);
      const working = liveLinks.some(([x, y]) => (x === a && y === b) || (x === b && y === a));
      c.strokeStyle = working ? '#5cf0d0' : 'rgba(255,107,125,.8)';
      c.lineWidth = working ? 4 : 3;
      c.setLineDash(working ? [] : [6, 8]);
      c.beginPath(); c.moveTo(ax, ay); c.lineTo(bx, by); c.stroke();
      c.setLineDash([]);
      if (!working && round.failure.type === 'link') {
        const mx = (ax + bx) / 2;
        const my = (ay + by) / 2;
        c.strokeStyle = '#ff6b7d';
        c.lineWidth = 5;
        c.beginPath(); c.moveTo(mx - 10, my - 10); c.lineTo(mx + 10, my + 10); c.moveTo(mx + 10, my - 10); c.lineTo(mx - 10, my + 10); c.stroke();
      }
    }
    const r = R();
    for (const n of round.nodes) {
      const [x, y] = pos(n.id);
      const failed = !alive.has(n.id);
      c.save();
      c.translate(x, y);
      if (n.kind === 'link') {
        c.fillStyle = failed ? '#7a3340' : '#ffd36b';
        c.beginPath(); c.arc(0, 0, r * 0.32, 0, 7); c.fill();
        c.fillStyle = '#fff';
        c.font = `${Math.max(11, r * 0.4)}px sans-serif`;
        c.textAlign = 'center';
        c.direction = 'rtl';
        if (n.label) c.fillText(n.label, 0, r * 0.85);
      } else {
        const isTarget = n.id === round.target;
        const sel = picked.has(n.id);
        if (isTarget || sel) { c.shadowColor = isTarget ? '#ffd36b' : '#ff6b7d'; c.shadowBlur = 20 + Math.sin(t * 4) * 4; }
        c.fillStyle = failed ? '#4a3a4a' : sel ? '#ff8a9a' : isTarget ? '#ffd36b' : '#7ad6ff';
        c.strokeStyle = '#2b2150';
        c.lineWidth = 3;
        c.beginPath(); c.roundRect(-r * 0.75, -r * 0.55, r * 1.5, r * 1.1, 10); c.fill(); c.stroke();
        c.shadowBlur = 0;
        c.fillStyle = '#1a1440';
        c.fillRect(-r * 0.45, -r * 0.3, r * 0.9, r * 0.45);
        if (failed) {
          c.strokeStyle = '#ff6b7d';
          c.lineWidth = 5;
          c.beginPath(); c.moveTo(-r * 0.6, -r * 0.5); c.lineTo(r * 0.6, r * 0.5); c.moveTo(r * 0.6, -r * 0.5); c.lineTo(-r * 0.6, r * 0.5); c.stroke();
        }
        c.fillStyle = '#fff';
        c.font = `bold ${Math.max(11, r * 0.42)}px sans-serif`;
        c.textAlign = 'center';
        c.direction = 'rtl';
        c.lineWidth = 4;
        c.strokeStyle = 'rgba(8,9,24,.9)';
        c.strokeText(isTarget ? `${n.label} (יעד)` : n.label, 0, r * 1.25);
        c.fillText(isTarget ? `${n.label} (יעד)` : n.label, 0, r * 1.25);
      }
      c.restore();
    }
  };
  raf = requestAnimationFrame(frame);
  return () => {
    cancelAnimationFrame(raf);
    ro.disconnect();
  };
}

/* ------------------------------------------------------------------ hotspot ------------------------------------------------------------------ */

export interface HotspotRound {
  text: string;
  layout: string;
  regions: Array<{ id: string; label: string; x: number; y: number; w: number; h: number }>;
  answer: string;
  why: string;
}
export interface HotspotData {
  id: string;
  title: string;
  intro: string;
  levels: Record<Level, LevelBase & { rounds: HotspotRound[] }>;
}

const LAYOUT_TITLES: Record<string, string> = {
  main: 'החלון הראשי של הסימולטור',
  workspace: 'אזור העבודה',
  'device-config': 'חלון הגדרות של התקן',
  simulation: 'מצב סימולציה',
};

/** A schematic simulator window drawn as labelled boxes: tap the box where the thing happens. */
export function hotspotGame(data: HotspotData): GameDef {
  return {
    title: data.title,
    intro: data.intro,
    howTo: ['מופיע שרטוט של חלון הסימולטור, מחולק לאזורים.', 'קראו מה צריך לעשות ולחצו על האזור המתאים.'],
    levels: levelsOf(data, (l) => l.rounds.length, 'סיבובים'),
    mountRound: (level, index, host, api) => mountHotspotRound(data.levels[level].rounds[index] as HotspotRound, host, api),
  };
}

function mountHotspotRound(round: HotspotRound, host: HTMLElement, api: RoundApi): () => void {
  let done = false;
  const boxes = round.regions.map((r) => {
    const b = el('button', 'hot-region', r.label);
    b.type = 'button';
    Object.assign(b.style, { left: `${r.x * 100}%`, top: `${r.y * 100}%`, width: `${r.w * 100}%`, height: `${r.h * 100}%` });
    b.addEventListener('click', () => pick(r.id, b));
    return b;
  });
  const win = el('div', 'hot-window', '', [el('div', 'hot-title', LAYOUT_TITLES[round.layout] ?? 'חלון הסימולטור'), el('div', 'hot-inner', '', boxes)]);
  host.append(el('div', 'lrn-wire-banner', '', [el('p', '', round.text)]), win);
  function pick(id: string | null, btn: HTMLElement | null): void {
    if (done) return;
    done = true;
    boxes.forEach((b) => (b.disabled = true));
    const ok = id === round.answer;
    const idx = round.regions.findIndex((r) => r.id === round.answer);
    boxes[idx]?.classList.add('hot-right');
    if (!ok) btn?.classList.add('hot-wrong');
    api.resolve(ok, round.why);
  }
  api.onTimeout(() => pick(null, null));
  return () => {};
}

/* ------------------------------------------------------------------ message journey ------------------------------------------------------------------ */

export interface JourneyData {
  id: string;
  title: string;
  intro: string;
  howTo: string[];
  /** label -> "end" | "mid" | "media" */
  roles: Record<string, 'end' | 'mid' | 'media'>;
  levels: Record<Level, LevelBase & { mistakes: number; rounds: Array<{ text: string; path: string[]; why: string }> }>;
}

type JourneyRole = 'source' | 'media' | 'mid' | 'dest';
const JOURNEY_BUTTONS: Array<{ role: JourneyRole; label: string }> = [
  { role: 'source', label: 'מקור' }, { role: 'media', label: 'מדיה' }, { role: 'mid', label: 'התקן אמצע' }, { role: 'dest', label: 'יעד' },
];
const JOURNEY_NAME: Record<JourneyRole, string> = { source: 'מקור', media: 'מדיה', mid: 'התקן אמצע', dest: 'יעד' };

/** A message travels from a source to a destination; at every stop the player says what the stop is. */
export function journeyGame(data: JourneyData): GameDef {
  return {
    title: data.title,
    intro: data.intro,
    howTo: data.howTo,
    levels: (() => {
      const out = {} as GameDef['levels'];
      for (const lv of LEVELS_3) {
        const l = data.levels[lv];
        out[lv] = { count: l.rounds.length, lives: l.lives, timeLimit: l.timeLimitPerTaskSec, blurb: `${l.rounds.length} מסעות. ${l.timeLimitPerTaskSec ? `${l.timeLimitPerTaskSec} שניות לכל מסע. ` : 'בלי הגבלת זמן. '}מותר ${l.mistakes} טעויות בכל מסע.` };
      }
      return out;
    })(),
    mountRound: (level, index, host, api) => mountJourney(data, data.levels[level].mistakes, data.levels[level].rounds[index] as JourneyData['levels']['easy']['rounds'][number], host, api),
  };
}

function mountJourney(data: JourneyData, allowed: number, round: { text: string; path: string[]; why: string }, host: HTMLElement, api: RoundApi): () => void {
  const roleOf = (i: number): JourneyRole => (i === 0 ? 'source' : i === round.path.length - 1 ? 'dest' : data.roles[round.path[i] as string] === 'media' ? 'media' : 'mid');
  let at = 0;
  let mistakes = 0;
  let done = false;
  const chips = round.path.map((label) => el('div', 'jr-chip', label));
  const lane = el('div', 'jr-lane', '', chips.flatMap((c, i) => (i ? [el('span', 'jr-arrow'), c] : [c])));
  const msg = el('div', 'lrn-wire-msg', 'מה זה?');
  const buttons = JOURNEY_BUTTONS.map((b) => {
    const btn = el('button', 'btn jr-role', b.label);
    btn.type = 'button';
    btn.addEventListener('click', () => choose(b.role, btn));
    return btn;
  });
  host.append(el('div', 'lrn-wire-banner', '', [el('p', '', round.text)]), lane, msg, el('div', 'npcg-row', '', buttons));
  paint();

  function paint(): void {
    chips.forEach((c, i) => {
      c.classList.toggle('jr-here', i === at && !done);
      c.classList.toggle('jr-done', i < at);
    });
    chips[at]?.scrollIntoView?.({ block: 'nearest', inline: 'center' });
  }

  function choose(role: JourneyRole, btn: HTMLElement): void {
    if (done) return;
    const right = roleOf(at);
    if (role === right) {
      const c = chips[at] as HTMLElement;
      c.append(el('small', 'jr-tag', JOURNEY_NAME[right]));
      at++;
      msg.className = 'lrn-wire-msg';
      msg.textContent = 'מה זה?';
      if (at >= round.path.length) {
        done = true;
        buttons.forEach((b) => (b.disabled = true));
        paint();
        api.resolve(true, `${mistakes ? 'סיימתם את המסע, עם כמה טעויות בדרך. ' : ''}${round.why}`);
        return;
      }
      paint();
      return;
    }
    mistakes++;
    api.flash('bad');
    btn.classList.add('wrong');
    window.setTimeout(() => btn.classList.remove('wrong'), 500);
    msg.className = 'lrn-wire-msg warn';
    msg.textContent = `לא בדיוק: "${round.path[at]}" אינו ${JOURNEY_NAME[role]}.`;
    if (mistakes > allowed) {
      done = true;
      buttons.forEach((b) => (b.disabled = true));
      api.resolve(false, `"${round.path[at]}" הוא ${JOURNEY_NAME[right]}. ${round.why}`);
    }
  }
  api.onTimeout(() => {
    if (done) return;
    done = true;
    buttons.forEach((b) => (b.disabled = true));
    api.resolve(false, `הזמן נגמר. ${round.why}`);
  });
  return () => {};
}

/* ------------------------------------------------------------------ network map ------------------------------------------------------------------ */

type NetKind = 'lan' | 'wan' | 'internet';
type MapRound = {
  text: string;
  nodes: Array<{ id: string; label: string; x: number; y: number; type: 'area' | 'cloud' }>;
  links: Array<[string, string]>;
  marks: Array<{ target: string; answer: NetKind; why: string }>;
};
export interface MapData {
  id: string;
  title: string;
  intro: string;
  howTo: string[];
  levels: Record<Level, LevelBase & { mistakes: number; rounds: MapRound[] }>;
}

const NET_NAME: Record<NetKind, string> = { lan: 'LAN', wan: 'WAN', internet: 'האינטרנט' };
const NET_COLOR: Record<NetKind, string> = { lan: '#5cf0d0', wan: '#ffd36b', internet: '#c6a2ff' };

/** A map of places and the connections between them: tap each thing and say what kind of network it is. */
export function mapGame(data: MapData): GameDef {
  const out = {} as GameDef['levels'];
  for (const lv of LEVELS_3) {
    const l = data.levels[lv];
    out[lv] = { count: l.rounds.length, lives: l.lives, timeLimit: l.timeLimitPerTaskSec, blurb: `${l.rounds.length} מפות. ${l.timeLimitPerTaskSec ? `${l.timeLimitPerTaskSec} שניות לכל מפה. ` : 'בלי הגבלת זמן. '}מותר ${l.mistakes} טעויות בכל מפה.` };
  }
  return {
    title: data.title,
    intro: data.intro,
    howTo: data.howTo,
    levels: out,
    mountRound: (level, index, host, api) => mountMap(data.levels[level].mistakes, data.levels[level].rounds[index] as MapRound, host, api),
  };
}

function mountMap(allowed: number, round: MapRound, host: HTMLElement, api: RoundApi): () => void {
  const canvas = el('canvas', 'lrn-canvas');
  const stage = el('div', 'lrn-wire-stage', '', [canvas]);
  const msg = el('div', 'lrn-wire-msg', 'לחצו על סימן שאלה במפה, ואז על הסוג שלו.');
  const kinds: NetKind[] = ['lan', 'wan', 'internet'];
  const buttons = kinds.map((k, i) => {
    const b = el('button', 'btn jr-role', `${i + 1}. ${NET_NAME[k]}`);
    b.type = 'button';
    b.style.borderColor = NET_COLOR[k];
    b.addEventListener('click', () => choose(k));
    return b;
  });
  host.append(el('div', 'lrn-wire-banner', '', [el('p', '', round.text)]), stage, msg, el('div', 'npcg-row', '', buttons));

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

  const node = (id: string): MapRound['nodes'][number] => round.nodes.find((n) => n.id === id) as MapRound['nodes'][number];
  const spot = (target: string): [number, number] => {
    if (target.includes('|')) {
      const [a, b] = target.split('|') as [string, string];
      const na = node(a);
      const nb = node(b);
      return [((na.x + nb.x) / 2) * W, ((na.y + nb.y) / 2) * H];
    }
    const n = node(target);
    return [n.x * W, n.y * H + Math.min(34, H * 0.07)];
  };
  const done = new Map<string, NetKind>();
  let selected: string | null = null;
  let mistakes = 0;
  let finished = false;

  canvas.addEventListener('pointerdown', (e) => {
    if (finished) return;
    const r = stage.getBoundingClientRect();
    const x = e.clientX - r.left;
    const y = e.clientY - r.top;
    let best: string | null = null;
    let bd = 34;
    for (const m of round.marks) {
      if (done.has(m.target)) continue;
      const [sx, sy] = spot(m.target);
      const d = Math.hypot(x - sx, y - sy);
      if (d < bd) { bd = d; best = m.target; }
    }
    if (best) { selected = best; msg.className = 'lrn-wire-msg'; msg.textContent = 'ומה זה?'; }
  });

  function choose(kind: NetKind): void {
    if (finished) return;
    if (!selected) { msg.textContent = 'קודם לחצו על סימן שאלה במפה.'; return; }
    const mark = round.marks.find((m) => m.target === selected) as MapRound['marks'][number];
    if (kind === mark.answer) {
      done.set(mark.target, kind);
      selected = null;
      msg.className = 'lrn-wire-msg good';
      msg.textContent = mark.why;
      if (done.size >= round.marks.length) {
        finished = true;
        buttons.forEach((b) => (b.disabled = true));
        api.resolve(true, `${mistakes ? 'סיימתם את המפה, עם כמה טעויות בדרך. ' : ''}${[...new Set(round.marks.map((m) => m.why))].slice(0, 2).join(' ')}`);
      }
      return;
    }
    mistakes++;
    api.flash('bad');
    msg.className = 'lrn-wire-msg warn';
    msg.textContent = `לא בדיוק: זה לא ${NET_NAME[kind]}.`;
    if (mistakes > allowed) {
      finished = true;
      buttons.forEach((b) => (b.disabled = true));
      api.resolve(false, `הנכון: ${NET_NAME[mark.answer]}. ${mark.why}`);
    }
  }
  api.onTimeout(() => {
    if (finished) return;
    finished = true;
    buttons.forEach((b) => (b.disabled = true));
    api.resolve(false, `הזמן נגמר. ${round.marks[0]?.why ?? ''}`);
  });
  const onKey = (e: KeyboardEvent): void => {
    const n = Number(e.key);
    if (n >= 1 && n <= 3) choose(kinds[n - 1] as NetKind);
  };
  document.addEventListener('keydown', onKey);

  const c = canvas.getContext('2d') as CanvasRenderingContext2D;
  let raf = 0;
  let t = 0;
  let prev = performance.now();
  const frame = (now: number): void => {
    raf = requestAnimationFrame(frame);
    t += Math.min(0.25, (now - prev) / 1000);
    prev = now;
    c.setTransform(dpr, 0, 0, dpr, 0, 0);
    const g = c.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#24406a'); g.addColorStop(1, '#3f7a5a');
    c.fillStyle = g;
    c.fillRect(0, 0, W, H);
    for (const [a, b] of round.links) {
      const na = node(a);
      const nb = node(b);
      c.strokeStyle = 'rgba(255,255,255,.7)';
      c.lineWidth = 3;
      c.setLineDash([10, 8]);
      c.beginPath(); c.moveTo(na.x * W, na.y * H); c.lineTo(nb.x * W, nb.y * H); c.stroke();
      c.setLineDash([]);
    }
    for (const n of round.nodes) {
      c.save();
      c.translate(n.x * W, n.y * H);
      if (n.type === 'cloud') {
        c.fillStyle = '#e8ecff';
        c.strokeStyle = '#6a5aa8';
        c.lineWidth = 3;
        c.beginPath();
        c.arc(-34, 4, 26, Math.PI * 0.5, Math.PI * 1.5); c.arc(0, -16, 32, Math.PI, 0); c.arc(34, 4, 26, Math.PI * 1.5, Math.PI * 0.5); c.closePath();
        c.fill(); c.stroke();
        c.fillStyle = '#2b2150';
      } else {
        c.fillStyle = 'rgba(30,20,70,.55)';
        c.strokeStyle = '#ffd36b';
        c.lineWidth = 3;
        c.beginPath(); c.roundRect(-64, -24, 128, 48, 16); c.fill(); c.stroke();
        c.fillStyle = '#fff';
      }
      c.font = 'bold 14px sans-serif';
      c.textAlign = 'center';
      c.direction = 'rtl';
      c.fillText(n.label, 0, 5, 118);
      c.restore();
    }
    for (const m of round.marks) {
      const [sx, sy] = spot(m.target);
      const kind = done.get(m.target);
      c.save();
      c.translate(sx, sy);
      if (kind) {
        c.fillStyle = NET_COLOR[kind];
        c.strokeStyle = '#1a1440';
        c.lineWidth = 2;
        c.beginPath(); c.roundRect(-30, -13, 60, 26, 13); c.fill(); c.stroke();
        c.fillStyle = '#1a1440';
        c.font = 'bold 13px sans-serif';
        c.textAlign = 'center';
        c.direction = 'rtl';
        c.fillText(NET_NAME[kind], 0, 5);
      } else {
        const sel = selected === m.target;
        c.fillStyle = sel ? '#ffd36b' : '#fff';
        c.strokeStyle = sel ? '#fff' : '#6a5aa8';
        c.lineWidth = 3;
        c.beginPath(); c.arc(0, 0, 15 + Math.sin(t * 5) * (sel ? 2 : 0.8), 0, 7); c.fill(); c.stroke();
        c.fillStyle = '#2b2150';
        c.font = 'bold 18px sans-serif';
        c.textAlign = 'center';
        c.fillText('?', 0, 6);
      }
      c.restore();
    }
  };
  raf = requestAnimationFrame(frame);
  return () => {
    cancelAnimationFrame(raf);
    ro.disconnect();
    document.removeEventListener('keydown', onKey);
  };
}
