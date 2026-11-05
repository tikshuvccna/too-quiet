/** Pure rules of the fight with the Head: the thread map, the walk, the phases and the difficulty. */

export type NodeKind = 'boss' | 'hub' | 'house' | 'start' | 'mid';
export interface BNode { id: string; x: number; y: number; kind: NodeKind; label: string }

export interface Arena {
  nodes: BNode[];
  /** Neighbours of every node (every real link has a middle node, so a cut can happen anywhere along a thread). */
  adj: Map<string, string[]>;
  start: string;
  boss: string;
}

const REAL: Array<Omit<BNode, 'kind'> & { kind: Exclude<NodeKind, 'mid'> }> = [
  { id: 'H', x: 0.5, y: 0.14, kind: 'boss', label: '' },
  { id: 'hA', x: 0.2, y: 0.4, kind: 'hub', label: 'פנס א' },
  { id: 'hB', x: 0.5, y: 0.4, kind: 'hub', label: 'פנס ב' },
  { id: 'hC', x: 0.8, y: 0.4, kind: 'hub', label: 'פנס ג' },
  { id: 'h1', x: 0.07, y: 0.68, kind: 'house', label: 'בית 1' },
  { id: 'h2', x: 0.27, y: 0.68, kind: 'house', label: 'בית 2' },
  { id: 'h3', x: 0.4, y: 0.68, kind: 'house', label: 'בית 3' },
  { id: 'h4', x: 0.6, y: 0.68, kind: 'house', label: 'בית 4' },
  { id: 'h5', x: 0.73, y: 0.68, kind: 'house', label: 'בית 5' },
  { id: 'h6', x: 0.93, y: 0.68, kind: 'house', label: 'בית 6' },
  { id: 'S', x: 0.5, y: 0.9, kind: 'start', label: 'שער הכפר' },
];

const LINKS: Array<[string, string]> = [
  ['H', 'hA'], ['H', 'hB'], ['H', 'hC'],
  ['hA', 'h1'], ['hA', 'h2'], ['hB', 'h3'], ['hB', 'h4'], ['hC', 'h5'], ['hC', 'h6'],
  ['hA', 'hB'], ['hB', 'hC'], ['h2', 'h3'], ['h4', 'h5'], ['S', 'h3'], ['S', 'h4'],
];

export function buildArena(): Arena {
  const nodes: BNode[] = REAL.map((n) => ({ ...n }));
  const adj = new Map<string, string[]>();
  const link = (a: string, b: string): void => {
    (adj.get(a) ?? adj.set(a, []).get(a) as string[]).push(b);
    (adj.get(b) ?? adj.set(b, []).get(b) as string[]).push(a);
  };
  for (const [a, b] of LINKS) {
    const na = REAL.find((n) => n.id === a) as (typeof REAL)[number];
    const nb = REAL.find((n) => n.id === b) as (typeof REAL)[number];
    const mid: BNode = { id: `${a}~${b}`, x: (na.x + nb.x) / 2, y: (na.y + nb.y) / 2, kind: 'mid', label: '' };
    nodes.push(mid);
    link(a, mid.id);
    link(mid.id, b);
  }
  return { nodes, adj, start: 'S', boss: 'H' };
}

/** Shortest walk from `from` to `to` that never passes through a blocked node (the target itself may be blocked). */
export function walk(adj: Map<string, string[]>, from: string, to: string, blocked: ReadonlySet<string>, passBoss = false): string[] | null {
  if (from === to) return [from];
  const prev = new Map<string, string | null>([[from, null]]);
  const queue = [from];
  while (queue.length) {
    const cur = queue.shift() as string;
    for (const nx of adj.get(cur) ?? []) {
      if (prev.has(nx)) continue;
      if (nx !== to && blocked.has(nx)) continue;
      if (nx === 'H' && nx !== to && !passBoss) continue;
      prev.set(nx, cur);
      if (nx === to) {
        const path: string[] = [];
        for (let n: string | null = to; n; n = prev.get(n) ?? null) path.unshift(n);
        return path;
      }
      queue.push(nx);
    }
  }
  return null;
}

export const PHASES = 5;
export const PHASE_HP = 8;
export const MAX_HP = PHASES * PHASE_HP;
/** The kind of fault each phase throws up, in order: a plain cut, then a question, and again. */
export const PHASE_SEQUENCE = ['simple', 'choice', 'simple', 'choice'] as const;
export type FaultType = (typeof PHASE_SEQUENCE)[number];
export const DAMAGE: Record<FaultType, number> = { simple: 1, choice: 3 };

/** Phase number 0..4 from the Head's remaining strength. */
export function phaseOf(hp: number): number {
  const done = MAX_HP - hp;
  return Math.min(PHASES - 1, Math.max(0, Math.floor(done / PHASE_HP)));
}

export interface Difficulty { maxFaults: number; faultEvery: number; streamEvery: number; streamSpeed: number; bits: number }

export function difficulty(phase: number): Difficulty {
  return {
    maxFaults: phase < 2 ? 1 : phase < 4 ? 2 : 3,
    faultEvery: Math.max(3.5, 7 - phase),
    streamEvery: Math.max(2.4, 5.2 - phase * 0.7),
    streamSpeed: 0.62 + phase * 0.09,
    bits: 5 + Math.min(3, phase),
  };
}

/** What the player sees in the Head's name for each topic (phase n is lesson n+1). */
export const PHASE_TOPIC = ['רשתות ולקוח-שרת', 'רכיבי הרשת', 'טופולוגיות', 'LAN, WAN ואינטרנט', 'תכנון ב-Packet Tracer'];

/** Length of a walk in arena units, used to time the bits. */
export function pathLength(arena: Arena, path: string[], w: number, h: number): number {
  let sum = 0;
  for (let i = 1; i < path.length; i++) {
    const a = arena.nodes.find((n) => n.id === path[i - 1]) as BNode;
    const b = arena.nodes.find((n) => n.id === path[i]) as BNode;
    sum += Math.hypot((a.x - b.x) * w, (a.y - b.y) * h);
  }
  return sum;
}
