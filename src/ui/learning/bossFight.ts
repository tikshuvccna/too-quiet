import type { SaveStore } from '../../core/save';
import { el } from '../dom';
import { bossData, bossRounds, type BossRound } from './bossGame';
import {
  DAMAGE, MAX_HP, PHASE_SEQUENCE, PHASE_TOPIC, PHASES, buildArena, difficulty, phaseOf, walk,
  type Arena, type BNode, type FaultType,
} from './bossLogic';
import { createOverlay } from './overlay';
import { applyPrize, prizeFor } from './prizes';
import { reducedMotion } from './widgetKit';
import wiring01 from '../../../content/he/wiring01.json';
import journey02 from '../../../content/he/journey02.json';
import map04 from '../../../content/he/map04.json';
import type { JourneyData, MapData } from './lessonGames';
import type { WiringData } from './wiringLogic';

interface Atlas { img: HTMLImageElement; frames: Record<string, { x: number; y: number; w: number; h: number }> }

async function loadAtlas(base: string, name: string, frameKey?: (k: string) => string): Promise<Atlas | null> {
  try {
    const [json, img] = await Promise.all([
      fetch(`${base}${name}.json`).then((r) => r.json() as Promise<{ frames: Record<string, { frame?: { x: number; y: number; w: number; h: number }; x?: number; y?: number; w?: number; h?: number }> }>),
      new Promise<HTMLImageElement>((resolve, reject) => { const i = new Image(); i.onload = () => resolve(i); i.onerror = reject; i.src = `${base}${name}.png`; }),
    ]);
    const frames: Atlas['frames'] = {};
    for (const [k, v] of Object.entries(json.frames)) {
      const f = v.frame ?? (v as { x: number; y: number; w: number; h: number });
      frames[frameKey ? frameKey(k) : k] = { x: f.x, y: f.y, w: f.w, h: f.h };
    }
    return { img, frames };
  } catch {
    return null;
  }
}

interface Fault { type: FaultType; phase: number; progress: number; born: number }
interface Stream { path: string[]; pts: Array<[number, number]>; len: number; telegraph: number; travelled: number; bits: number; hit: boolean }
interface Shot { pts: Array<[number, number]>; len: number; travelled: number; dmg: number; count: number; landed: boolean }
interface Float { x: number; y: number; text: string; color: string; age: number }

/** One decision at a fault: a scenario and the choices, taken from the same material the mini-games use. */
interface Choice { topic: string; q: string; options: string[]; correct: number; explain: string }

function shuffled<T>(a: T[]): T[] {
  const out = [...a];
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j] as T, out[i] as T];
  }
  return out;
}

/** Lesson 1: peer to peer or client-server? (the wiring rounds, as a question). */
function choicesLesson1(): Choice[] {
  const d = wiring01 as unknown as WiringData;
  return shuffled([...d.levels.easy.rounds, ...d.levels.medium.rounds, ...d.levels.hard.rounds]).slice(0, 6).map((r) => ({
    topic: 'שיעור 1', q: `${r.text} איזה מבנה מתאים כאן?`, options: ['עמית לעמית: בלי שרת', 'לקוח-שרת: עם שרת'], correct: r.need === 'p2p' ? 0 : 1, explain: r.why,
  }));
}

/** Lesson 2: what is this part of the message's road? */
function choicesLesson2(): Choice[] {
  const d = journey02 as unknown as JourneyData;
  const rounds = shuffled([...d.levels.easy.rounds, ...d.levels.medium.rounds, ...d.levels.hard.rounds]).slice(0, 6);
  return rounds.map((r) => {
    const i = Math.floor(Math.random() * r.path.length);
    const label = r.path[i] as string;
    const kind = d.roles[label];
    const where = i === 0 ? ' (ממנו יוצאת ההודעה)' : i === r.path.length - 1 ? ' (אליו היא מגיעה)' : '';
    return { topic: 'שיעור 2', q: `בדרך של הודעה: "${label}"${where}. מה זה?`, options: ['התקן קצה', 'התקן אמצע', 'מדיה'], correct: kind === 'end' ? 0 : kind === 'mid' ? 1 : 2, explain: r.why };
  });
}

/** Lesson 4: LAN, WAN or the Internet on a map. */
function choicesLesson4(): Choice[] {
  const d = map04 as unknown as MapData;
  const out: Choice[] = [];
  for (const r of shuffled([...d.levels.easy.rounds, ...d.levels.medium.rounds, ...d.levels.hard.rounds]).slice(0, 8)) {
    const name = (id: string): string => r.nodes.find((n) => n.id === id)?.label ?? id;
    const m = r.marks[Math.floor(Math.random() * r.marks.length)];
    if (!m) continue;
    const label = m.target.includes('|') ? `החיבור בין "${name(m.target.split('|')[0] as string)}" ל"${name(m.target.split('|')[1] as string)}"` : `"${name(m.target)}"`;
    out.push({ topic: 'שיעור 4', q: `${r.text} ${label}: מה זה?`, options: ['LAN', 'WAN', 'האינטרנט'], correct: m.answer === 'lan' ? 0 : m.answer === 'wan' ? 1 : 2, explain: m.why });
  }
  return out.slice(0, 6);
}

/** The decisions for each phase: the special ones first, then the summary questions of the lesson. */
function buildChoices(pool: BossRound[]): Map<number, Choice[]> {
  const special: Record<number, Choice[]> = { 1: choicesLesson1(), 2: choicesLesson2(), 4: choicesLesson4() };
  const out = new Map<number, Choice[]>();
  for (let n = 1; n <= PHASES; n++) {
    const quiz = shuffled(pool.filter((r) => r.lessonNo === n)).map((r): Choice => ({ topic: `שיעור ${n}`, q: r.q.q, options: r.q.options, correct: r.q.correct, explain: r.q.explain }));
    out.set(n, [...(special[n] ?? []), ...quiz]);
  }
  return out;
}

/**
 * The fight with the Head, in real time. The Head cuts threads and breaks houses, and sends streams of bits down the
 * threads at the player. The player runs along the threads to the faults and mends them: some only need a moment,
 * others ask a question from the lessons. Every mend sends bits up to the Head and takes some of its strength away.
 */
export function openBossFight(save: SaveStore, opts: { onClose(r: { passed: boolean }): void }): () => void {
  const ov = createOverlay('lrn-mini boss');
  const arena: Arena = buildArena();
  const choices = buildChoices(bossRounds());
  const base = `${import.meta.env.BASE_URL}assets/`;

  const hearts = el('div', 'lrn-hearts');
  const calmFill = el('i', 'boss-calm-fill');
  const calm = el('div', 'boss-calm', '', [calmFill]);
  const phaseLabel = el('span', 'lrn-streak', '');
  const closeBtn = el('button', 'lrn-x', '×');
  closeBtn.type = 'button';
  closeBtn.setAttribute('aria-label', 'יציאה');
  const head = el('header', 'lrn-head', '', [
    el('div', 'lrn-head-main', '', [el('h1', 'lrn-title', 'הראש'), el('div', 'lrn-hud', '', [hearts, phaseLabel])]),
    closeBtn,
  ]);
  const canvas = el('canvas', 'boss-canvas');
  const hint = el('div', 'boss-hint', '');
  const panel = el('div', 'boss-panel');
  const stage = el('div', 'boss-stage', '', [canvas, hint, panel]);
  ov.root.append(head, calm, stage);

  // ----- state -----
  let W = 0;
  let H = 0;
  const dpr = Math.min(2, window.devicePixelRatio || 1);
  const fit = (): void => {
    W = stage.clientWidth;
    H = stage.clientHeight;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
  };
  const ro = new ResizeObserver(fit);
  ro.observe(stage);
  fit();

  const nodeOf = new Map(arena.nodes.map((n) => [n.id, n]));
  const px = (id: string): [number, number] => { const n = nodeOf.get(id) as BNode; return [n.x * W, n.y * H]; };
  const maxLives = 5;
  let lives = maxLives;
  let hp = MAX_HP;
  let phase = 0;
  let faultsDone = 0; // in the current phase
  let seqIndex = 0;
  let time = 0;
  let spawnClock = 2.5;
  let streamClock = 3.5;
  let invuln = 0;
  let shake = 0;
  let banner = 0;
  let paused = true;
  let over = false;
  let closed = false;
  const faults = new Map<string, Fault>();
  const streams: Stream[] = [];
  const shots: Shot[] = [];
  const floats: Float[] = [];
  const askedIdx = new Map<number, number>();
  const player = { a: arena.start, b: null as string | null, t: 0, queue: [] as string[], face: 1 };
  let heroAtlas: Atlas | null = null;
  let headAtlas: Atlas | null = null;
  const heroKey = save.data.look === 'boy' ? 'apprentice_boy' : 'apprentice_girl';

  function paintHearts(): void {
    hearts.replaceChildren(...Array.from({ length: maxLives }, (_, i) => el('span', `lrn-heart${i < lives ? '' : ' lost'}`, '♥')));
    calmFill.style.width = `${((MAX_HP - hp) / MAX_HP) * 100}%`;
    phaseLabel.textContent = `שלב ${phase + 1} מתוך ${PHASES}: ${PHASE_TOPIC[phase] ?? ''}`;
  }

  // ----- helpers -----
  function playerPos(): [number, number] {
    const [ax, ay] = px(player.a);
    if (!player.b) return [ax, ay];
    const [bx, by] = px(player.b);
    return [ax + (bx - ax) * player.t, ay + (by - ay) * player.t];
  }
  const blocked = (): Set<string> => new Set(faults.keys());

  function goTo(target: string): void {
    if (paused || over) return;
    const standing = faults.get(target);
    if (player.b === null && target === player.a && standing?.type === 'choice') { ask(target); return; }
    if (player.b === null) {
      const path = walk(arena.adj, player.a, target, blocked());
      if (path) { player.queue = path.slice(1); if (player.queue.length) { player.b = player.queue.shift() as string; player.t = 0; } }
      return;
    }
    // between two nodes: either go on to `b` first, or turn back to `a`
    const viaB = walk(arena.adj, player.b, target, blocked());
    const viaA = walk(arena.adj, player.a, target, blocked());
    const lenB = viaB ? viaB.length : Infinity;
    const lenA = viaA ? viaA.length + 1 : Infinity;
    if (lenB <= lenA && viaB) { player.queue = viaB.slice(1); return; }
    if (viaA) {
      const oldA = player.a;
      player.a = player.b;
      player.b = oldA;
      player.t = 1 - player.t;
      player.queue = viaA.slice(1);
    }
  }

  function stepDir(dx: number, dy: number): void {
    if (paused || over || player.b !== null) return;
    const [ax, ay] = px(player.a);
    let best: string | null = null;
    let score = 0.35;
    for (const nb of arena.adj.get(player.a) ?? []) {
      if (nb === arena.boss) continue;
      const [bx, by] = px(nb);
      const len = Math.hypot(bx - ax, by - ay) || 1;
      const s = ((bx - ax) * dx + (by - ay) * dy) / len;
      if (s > score) { score = s; best = nb; }
    }
    if (best) goTo(best);
  }

  function addFloat(x: number, y: number, text: string, color: string): void {
    floats.push({ x, y, text, color, age: 0 });
  }

  function randomFaultNode(): string | null {
    const [pxX, pxY] = playerPos();
    const candidates = arena.nodes.filter((n) => n.kind !== 'boss' && n.kind !== 'start' && !faults.has(n.id) && n.id !== player.a && n.id !== player.b);
    const far = candidates.filter((n) => Math.hypot(n.x * W - pxX, n.y * H - pxY) > Math.min(W, H) * 0.3);
    const list = far.length ? far : candidates;
    return list.length ? (list[Math.floor(Math.random() * list.length)] as BNode).id : null;
  }

  function polyline(path: string[]): { pts: Array<[number, number]>; len: number } {
    const pts = path.map((id) => px(id));
    let len = 0;
    for (let i = 1; i < pts.length; i++) len += Math.hypot((pts[i]![0] - pts[i - 1]![0]), (pts[i]![1] - pts[i - 1]![1]));
    return { pts, len };
  }
  function at(pts: Array<[number, number]>, d: number): [number, number] {
    let left = Math.max(0, d);
    for (let i = 1; i < pts.length; i++) {
      const [x0, y0] = pts[i - 1] as [number, number];
      const [x1, y1] = pts[i] as [number, number];
      const seg = Math.hypot(x1 - x0, y1 - y0);
      if (left <= seg) return [x0 + ((x1 - x0) * left) / (seg || 1), y0 + ((y1 - y0) * left) / (seg || 1)];
      left -= seg;
    }
    return pts[pts.length - 1] as [number, number];
  }

  function hurt(reason: string): void {
    if (invuln > 0 || over) return;
    lives--;
    invuln = 1.4;
    shake = 0.3;
    const [x, y] = playerPos();
    addFloat(x, y - 40, reason, '#ff6b7d');
    paintHearts();
    if (lives <= 0) endFight(false);
  }

  function mend(nodeId: string): void {
    const f = faults.get(nodeId);
    if (!f) return;
    faults.delete(nodeId);
    const dmg = DAMAGE[f.type];
    const path = walk(arena.adj, nodeId, arena.boss, blocked(), true) ?? [nodeId, arena.boss];
    const { pts, len } = polyline(path);
    shots.push({ pts, len, travelled: 0, dmg, count: f.type === 'choice' ? 9 : 4, landed: false });
    const [x, y] = px(nodeId);
    addFloat(x, y - 30, f.type === 'choice' ? 'נכון!' : 'תוקן!', '#5cf0d0');
  }

  function landShot(s: Shot): void {
    s.landed = true;
    hp = Math.max(0, hp - s.dmg);
    shake = 0.45;
    const [x, y] = px(arena.boss);
    addFloat(x, y + 40, `-${s.dmg}`, '#ffd36b');
    const before = phase;
    phase = phaseOf(hp);
    if (phase !== before) { banner = 2.6; faultsDone = 0; seqIndex = 0; }
    paintHearts();
    if (hp <= 0) endFight(true);
  }

  // ----- question panel -----
  function ask(nodeId: string): void {
    const f = faults.get(nodeId);
    if (!f) return;
    paused = true;
    const lessonNo = f.phase + 1;
    const list = choices.get(lessonNo) ?? [];
    const idx = askedIdx.get(lessonNo) ?? 0;
    askedIdx.set(lessonNo, idx + 1);
    const r = list.length ? list[idx % list.length] : undefined;
    if (!r) { paused = false; mend(nodeId); return; }
    currentCorrect = r.correct;
    const feedback = el('div', 'lrn-wire-msg', '');
    const opts2 = r.options.map((text, i) => {
      const b = el('button', 'lrn-opt lrn-big-opt', text);
      b.type = 'button';
      b.addEventListener('click', () => {
        opts2.forEach((o, k) => { o.disabled = true; o.classList.toggle('right', k === r.correct); });
        const ok = i === r.correct;
        if (!ok) b.classList.add('wrong');
        feedback.className = `lrn-wire-msg ${ok ? 'good' : 'warn'}`;
        feedback.textContent = `${ok ? 'נכון! ' : 'לא בדיוק. '}${r.explain}`;
        const go = el('button', 'btn primary', ok ? 'לתקן!' : 'להמשיך');
        go.type = 'button';
        go.addEventListener('click', () => {
          panel.classList.remove('show');
          panel.replaceChildren();
          paused = false;
          if (ok) mend(nodeId);
          else hurt('טעות');
        });
        panel.querySelector('.boss-panel-card')?.append(feedback, go);
        go.focus();
      });
      return b;
    });
    panel.replaceChildren(el('div', 'boss-panel-card', '', [
      el('span', 'lrn-banner-n', `תקלה שדורשת החלטה · ${r.topic}`),
      el('p', 'boss-q', r.q),
      el('div', 'lrn-opts', '', opts2),
    ]));
    panel.classList.add('show');
  }

  // ----- flow -----
  function endFight(won: boolean): void {
    if (over) return;
    over = true;
    paused = true;
    const card = el('div', 'boss-panel-card');
    if (won) {
      const out = applyPrize(save, 'hard', { flawless: false, lessonId: 'lessonboss' });
      save.save();
      const p = prizeFor('hard', bossData().prizes);
      card.append(
        el('h2', '', 'הראש נרגע'),
        el('p', '', 'כל החוטים מחוברים, וההודעות עוברות. הראש מביט למטה, בשקט.'),
        el('div', 'lrn-prize', '', [el('h3', '', out.granted ? `פרס חדש: ${p.name}` : `הפרס שלכם: ${p.name}`), el('p', '', p.description), el('p', 'lrn-prize-fx', out.granted ? `${p.effect} (+${out.coins} מטבעות)` : '')]),
      );
      const done = el('button', 'btn primary', 'להמשיך');
      done.type = 'button';
      done.addEventListener('click', () => close(true));
      card.append(done);
    } else {
      card.append(el('h2', '', 'הראש חזק היום'), el('p', '', 'נגמרו הלבבות, וזה בסדר: אפשר לנסות שוב, בלי שום עונש.'));
      const again = el('button', 'btn primary', 'לנסות שוב');
      const out = el('button', 'btn', 'יציאה');
      again.type = 'button';
      out.type = 'button';
      again.addEventListener('click', reset);
      out.addEventListener('click', () => close(false));
      card.append(el('div', 'lrn-row', '', [out, again]));
    }
    panel.replaceChildren(card);
    panel.classList.add('show');
  }

  function reset(): void {
    lives = maxLives;
    hp = MAX_HP;
    phase = 0;
    faultsDone = 0;
    seqIndex = 0;
    time = 0;
    spawnClock = 2;
    streamClock = 3;
    faults.clear();
    streams.length = 0;
    shots.length = 0;
    floats.length = 0;
    askedIdx.clear();
    player.a = arena.start;
    player.b = null;
    player.queue = [];
    over = false;
    paused = false;
    banner = 2.6;
    panel.classList.remove('show');
    panel.replaceChildren();
    paintHearts();
  }

  function intro(): void {
    const go = el('button', 'btn primary', 'לצאת לקרב');
    go.type = 'button';
    go.addEventListener('click', () => { panel.classList.remove('show'); panel.replaceChildren(); reset(); });
    panel.replaceChildren(el('div', 'boss-panel-card', '', [
      el('h2', '', 'הראש'),
      el('p', '', 'הראש מנתק חוטים ושולח זרמי ביטים. כל תיקון שולח ביטים בחזרה אליו ומרגיע אותו.'),
      el('ul', 'lrn-facts', '', [
        el('li', '', 'לחצו על נקודה על החוטים כדי לרוץ אליה (או חצים במקלדת).'),
        el('li', '', 'רוצו אל תקלה אדומה ועמדו עליה כדי לתקן. תקלה עם סימן שאלה מבקשת החלטה מהחומר.'),
        el('li', '', 'הימנעו מהזרם האדום: כשחוט מהבהב באדום, זזו מהנקודה שלכם.'),
      ]),
      go,
    ]));
    panel.classList.add('show');
  }

  // ----- update -----
  function update(dt: number): void {
    time += dt;
    if (invuln > 0) invuln -= dt;
    if (shake > 0) shake -= dt;
    if (banner > 0) banner -= dt;
    for (const f of floats) f.age += dt;
    while (floats.length && (floats[0] as Float).age > 1.4) floats.shift();
    if (paused || over) return;
    const d = difficulty(phase);
    const speed = 300 * (Math.min(W, 900) / 900) + 60;

    // walking along the threads
    if (player.b) {
      const [ax, ay] = px(player.a);
      const [bx, by] = px(player.b);
      const seg = Math.hypot(bx - ax, by - ay) || 1;
      player.t += (speed * dt) / seg;
      player.face = bx >= ax ? 1 : -1;
      if (player.t >= 1) {
        player.a = player.b;
        player.b = player.queue.shift() ?? null;
        player.t = 0;
        if (!player.b) {
          const f = faults.get(player.a);
          if (f && f.type === 'choice') ask(player.a);
        }
      }
    } else if (player.queue.length) {
      player.b = player.queue.shift() as string;
    }
    // standing on a plain fault repairs it
    const here = player.b ? undefined : faults.get(player.a);
    if (here && here.type === 'simple') {
      here.progress += dt / 1.3;
      if (here.progress >= 1) { mend(player.a); }
    }

    // the Head cuts and breaks things
    spawnClock -= dt;
    if (spawnClock <= 0 && faults.size < d.maxFaults && faultsDone < PHASE_SEQUENCE.length) {
      const id = randomFaultNode();
      if (id) {
        const type = PHASE_SEQUENCE[seqIndex % PHASE_SEQUENCE.length] as FaultType;
        seqIndex++;
        faultsDone++;
        faults.set(id, { type, phase, progress: 0, born: time });
        shake = 0.2;
        const [x, y] = px(id);
        addFloat(x, y - 28, 'נותק!', '#ff6b7d');
      }
      spawnClock = d.faultEvery;
    }

    // streams of bits aimed at where the player stands
    streamClock -= dt;
    if (streamClock <= 0) {
      streamClock = d.streamEvery;
      const target = player.b ?? player.a;
      const path = walk(arena.adj, arena.boss, target, new Set([...faults.keys()].filter((k) => k !== target)), true);
      if (path && path.length > 1) {
        const { pts, len } = polyline(path);
        streams.push({ path, pts, len, telegraph: 1.15, travelled: 0, bits: d.bits, hit: false });
      }
    }
    for (const s of streams) {
      if (s.telegraph > 0) { s.telegraph -= dt; continue; }
      s.travelled += d.streamSpeed * Math.max(W, 600) * dt;
      const [qx, qy] = playerPos();
      for (let i = 0; i < s.bits; i++) {
        const [bx, by] = at(s.pts, s.travelled - i * 26);
        if (s.travelled - i * 26 < 0 || s.travelled - i * 26 > s.len) continue;
        if (Math.hypot(bx - qx, by - qy) < 20) hurt('זרם ביטים!');
      }
    }
    for (let i = streams.length - 1; i >= 0; i--) {
      const s = streams[i] as Stream;
      if (s.telegraph <= 0 && s.travelled - s.bits * 26 > s.len) streams.splice(i, 1);
    }

    // the bits we send to the Head
    for (const s of shots) {
      s.travelled += 560 * dt * (Math.max(W, 600) / 900);
      if (!s.landed && s.travelled >= s.len) landShot(s);
    }
    for (let i = shots.length - 1; i >= 0; i--) if ((shots[i] as Shot).landed) shots.splice(i, 1);

    const nearest = [...faults.entries()].sort((a, b) => a[1].born - b[1].born)[0];
    hint.textContent = banner > 0
      ? `שלב ${phase + 1}: ${PHASE_TOPIC[phase] ?? ''}`
      : nearest ? (nearest[1].type === 'choice' ? 'רוצו אל התקלה עם סימן השאלה וענו נכון.' : 'רוצו אל התקלה האדומה ועמדו עליה כדי לתקן.') : 'הראש מנתק חוט... היו מוכנים.';
  }

  // ----- drawing -----
  const c = canvas.getContext('2d') as CanvasRenderingContext2D;

  function drawHead(): void {
    const [x, y] = px(arena.boss);
    const w = Math.min(W * 0.62, 560);
    const truth = hp > MAX_HP * 0.5;
    const key = `the_head_${truth ? 'truth' : 'benevolent'}_${Math.floor(time * 0.8) % 2}`;
    const f = headAtlas?.frames[key];
    const jitter = shake > 0 ? (Math.random() - 0.5) * 8 : 0;
    c.save();
    c.translate(x + jitter, y + 6);
    if (headAtlas && f) {
      const h = (w * f.h) / f.w;
      c.globalAlpha = 0.95;
      c.drawImage(headAtlas.img, f.x, f.y, f.w, f.h, -w / 2, -h * 0.5, w, h);
      c.globalAlpha = 1;
    } else {
      c.fillStyle = 'rgba(230,236,255,.85)';
      c.beginPath(); c.ellipse(0, 0, w * 0.4, w * 0.2, 0, 0, 7); c.fill();
    }
    c.restore();
  }

  function drawFault(id: string, f: Fault): void {
    const [x, y] = px(id);
    const n = nodeOf.get(id) as BNode;
    const pulse = 1 + Math.sin(time * 9) * 0.12;
    c.save();
    c.translate(x, y);
    c.strokeStyle = '#ff6b7d';
    c.fillStyle = 'rgba(255,107,125,.28)';
    c.lineWidth = 4;
    c.beginPath(); c.arc(0, 0, (n.kind === 'mid' ? 16 : 28) * pulse, 0, 7); c.fill(); c.stroke();
    c.beginPath(); c.moveTo(-9, -9); c.lineTo(9, 9); c.moveTo(9, -9); c.lineTo(-9, 9); c.stroke();
    if (f.type === 'choice') {
      c.fillStyle = '#ffd36b';
      c.strokeStyle = '#2b2150';
      c.lineWidth = 3;
      c.beginPath(); c.arc(0, -38, 15, 0, 7); c.fill(); c.stroke();
      c.fillStyle = '#2b2150';
      c.font = 'bold 20px sans-serif';
      c.textAlign = 'center';
      c.fillText('?', 0, -31);
    }
    if (f.progress > 0) {
      c.strokeStyle = '#5cf0d0';
      c.lineWidth = 6;
      c.beginPath(); c.arc(0, 0, 24, -Math.PI / 2, -Math.PI / 2 + f.progress * Math.PI * 2); c.stroke();
    }
    c.restore();
  }

  function draw(): void {
    c.setTransform(dpr, 0, 0, dpr, 0, 0);
    const g = c.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#1a1448'); g.addColorStop(0.5, '#2c2468'); g.addColorStop(1, '#3a3380');
    c.fillStyle = g;
    c.fillRect(0, 0, W, H);
    c.save();
    if (shake > 0 && !reducedMotion()) c.translate((Math.random() - 0.5) * 5, (Math.random() - 0.5) * 5);

    drawHead();

    // threads (every link is two halves through its middle node, so a cut can sit anywhere on it)
    for (const n of arena.nodes) {
      for (const nb of arena.adj.get(n.id) ?? []) {
        if (n.id > nb) continue;
        const m = nodeOf.get(nb) as BNode;
        const [ax, ay] = px(n.id);
        const [bx, by] = px(nb);
        const cut = faults.has(n.id) || faults.has(nb);
        c.lineWidth = 4;
        c.strokeStyle = cut ? 'rgba(255,107,125,.35)' : 'rgba(92,240,208,.85)';
        c.shadowColor = cut ? 'transparent' : '#5cf0d0';
        c.shadowBlur = cut ? 0 : 8;
        c.setLineDash(cut ? [4, 9] : []);
        c.beginPath(); c.moveTo(ax, ay); c.lineTo(bx, by); c.stroke();
        c.setLineDash([]);
        c.shadowBlur = 0;
        void m;
      }
    }
    // telegraphed streams
    for (const s of streams) {
      if (s.telegraph <= 0) continue;
      c.strokeStyle = `rgba(255,107,125,${0.4 + 0.4 * Math.sin(time * 18)})`;
      c.lineWidth = 7;
      c.beginPath();
      s.pts.forEach(([x, y], i) => (i ? c.lineTo(x, y) : c.moveTo(x, y)));
      c.stroke();
    }
    // nodes
    for (const n of arena.nodes) {
      const [x, y] = px(n.id);
      if (n.kind === 'boss') continue;
      if (n.kind === 'mid') {
        if (!faults.has(n.id)) { c.fillStyle = 'rgba(92,240,208,.9)'; c.beginPath(); c.arc(x, y, 4, 0, 7); c.fill(); }
        continue;
      }
      c.save();
      c.translate(x, y);
      const bad = faults.has(n.id);
      if (n.kind === 'hub') {
        c.fillStyle = bad ? '#7a3340' : '#ffd36b';
        c.strokeStyle = '#2b2150';
        c.lineWidth = 3;
        c.beginPath(); c.arc(0, 0, 15, 0, 7); c.fill(); c.stroke();
      } else if (n.kind === 'start') {
        c.fillStyle = '#c6a2ff';
        c.strokeStyle = '#2b2150';
        c.lineWidth = 3;
        c.beginPath(); c.roundRect(-26, -14, 52, 28, 8); c.fill(); c.stroke();
      } else {
        c.fillStyle = bad ? '#7a3340' : '#ffb59a';
        c.strokeStyle = '#2b2150';
        c.lineWidth = 3;
        c.beginPath(); c.roundRect(-16, -8, 32, 24, 5); c.fill(); c.stroke();
        c.fillStyle = '#c85a4a';
        c.beginPath(); c.moveTo(-20, -8); c.lineTo(0, -24); c.lineTo(20, -8); c.closePath(); c.fill(); c.stroke();
      }
      if (n.label) {
        c.fillStyle = '#fff';
        c.font = '12px sans-serif';
        c.textAlign = 'center';
        c.direction = 'rtl';
        c.fillText(n.label, 0, 32);
      }
      c.restore();
    }
    for (const [id, f] of faults) drawFault(id, f);

    // bits of the Head
    c.font = 'bold 13px monospace';
    c.textAlign = 'center';
    for (const s of streams) {
      if (s.telegraph > 0) continue;
      for (let i = 0; i < s.bits; i++) {
        const d = s.travelled - i * 26;
        if (d < 0 || d > s.len) continue;
        const [bx, by] = at(s.pts, d);
        c.fillStyle = '#ff4d63';
        c.strokeStyle = '#fff';
        c.lineWidth = 2;
        c.beginPath(); c.roundRect(bx - 11, by - 11, 22, 22, 5); c.fill(); c.stroke();
        c.fillStyle = '#fff';
        c.fillText((i + Math.floor(time * 5)) % 2 ? '1' : '0', bx, by + 5);
      }
    }
    // our bits flying up to the Head
    for (const s of shots) {
      for (let i = 0; i < s.count; i++) {
        const d = s.travelled - i * 22;
        if (d < 0 || d > s.len) continue;
        const [bx, by] = at(s.pts, d);
        c.fillStyle = '#5cf0d0';
        c.strokeStyle = '#fff';
        c.lineWidth = 2;
        c.shadowColor = '#5cf0d0';
        c.shadowBlur = 12;
        c.beginPath(); c.roundRect(bx - 10, by - 10, 20, 20, 5); c.fill(); c.stroke();
        c.shadowBlur = 0;
        c.fillStyle = '#103a34';
        c.fillText((i + Math.floor(time * 6)) % 2 ? '1' : '0', bx, by + 5);
      }
    }
    // the apprentice
    const [qx, qy] = playerPos();
    const blink = invuln > 0 && Math.floor(time * 14) % 2 === 0;
    if (!blink) {
      c.save();
      c.translate(qx, qy);
      c.fillStyle = 'rgba(0,0,0,.3)';
      c.beginPath(); c.ellipse(0, 4, 14, 5, 0, 0, 7); c.fill();
      const f = heroAtlas?.frames['idle_S_0'];
      if (heroAtlas && f) {
        const s = Math.max(0.42, Math.min(0.62, H / 900));
        c.scale(player.face * s, s);
        c.drawImage(heroAtlas.img, f.x, f.y, f.w, f.h, -64, -110, f.w, f.h);
      } else {
        c.fillStyle = '#ffd36b';
        c.beginPath(); c.arc(0, -18, 13, 0, 7); c.fill();
      }
      c.restore();
    }
    // floating words
    c.font = 'bold 18px sans-serif';
    c.textAlign = 'center';
    c.direction = 'rtl';
    for (const f of floats) {
      c.globalAlpha = Math.max(0, 1 - f.age / 1.4);
      c.fillStyle = f.color;
      c.strokeStyle = 'rgba(8,9,24,.9)';
      c.lineWidth = 4;
      c.strokeText(f.text, f.x, f.y - f.age * 30);
      c.fillText(f.text, f.x, f.y - f.age * 30);
    }
    c.globalAlpha = 1;
    if (banner > 0) {
      c.globalAlpha = Math.min(1, banner);
      c.fillStyle = 'rgba(8,9,24,.65)';
      c.fillRect(0, H * 0.45, W, 60);
      c.fillStyle = '#ffd36b';
      c.font = 'bold 24px sans-serif';
      c.fillText(`שלב ${phase + 1}: ${PHASE_TOPIC[phase] ?? ''}`, W / 2, H * 0.45 + 38);
      c.globalAlpha = 1;
    }
    c.restore();
  }

  // ----- input -----
  canvas.addEventListener('pointerdown', (e) => {
    const r = canvas.getBoundingClientRect();
    const x = e.clientX - r.left;
    const y = e.clientY - r.top;
    let best: string | null = null;
    let bd = 42;
    for (const n of arena.nodes) {
      if (n.kind === 'boss') continue;
      const [nx, ny] = px(n.id);
      const d = Math.hypot(nx - x, ny - y);
      if (d < bd) { bd = d; best = n.id; }
    }
    if (best) goTo(best);
  });
  const onKey = (e: KeyboardEvent): void => {
    if (e.key === 'Escape') { e.preventDefault(); close(false); return; }
    const m: Record<string, [number, number]> = { ArrowLeft: [-1, 0], a: [-1, 0], ArrowRight: [1, 0], d: [1, 0], ArrowUp: [0, -1], w: [0, -1], ArrowDown: [0, 1], s: [0, 1] };
    const v = m[e.key];
    if (v) { e.preventDefault(); stepDir(v[0], v[1]); }
  };
  document.addEventListener('keydown', onKey, true);

  let raf = 0;
  let prev = performance.now();
  const frame = (now: number): void => {
    raf = requestAnimationFrame(frame);
    const cap = (window as unknown as { __bossDtCap?: number }).__bossDtCap ?? 0.05; // raised only by tests on a slow browser
    const dt = Math.min(cap, (now - prev) / 1000);
    prev = now;
    update(dt);
    draw();
  };

  function close(passed: boolean): void {
    if (closed) return;
    closed = true;
    cancelAnimationFrame(raf);
    ro.disconnect();
    document.removeEventListener('keydown', onKey, true);
    ov.destroy();
    opts.onClose({ passed });
  }
  closeBtn.addEventListener('click', () => close(false));

  // a small handle for tests on a slow browser (nothing in the game uses it)
  let currentCorrect = -1;
  (window as unknown as { __boss?: unknown }).__boss = {
    faults: () => [...faults.entries()].map(([id, f]) => ({ id, type: f.type })),
    goTo: (id: string) => goTo(id),
    state: () => ({ hp, lives, phase, paused, over }),
    correct: () => currentCorrect,
  };
  paintHearts();
  void Promise.all([
    loadAtlas(`${base}creatures/`, 'the_head'),
    loadAtlas(`${base}characters_v2/`, heroKey),
  ]).then(([h, p]) => { headAtlas = h; heroAtlas = p; });
  raf = requestAnimationFrame(frame);
  intro();
  return () => close(false);
}
