import type { Level } from './types';

export type SimKind = 'pc' | 'server' | 'switch';

export interface SimDevice { id: string; kind: SimKind; label: string; x: number; y: number; /** Given by the round (cannot be removed). */ fixed: boolean }

export interface SimRound {
  text: string;
  /** Devices that are already on the table, not connected. */
  given: Array<{ kind: SimKind; label: string; x: number; y: number }>;
  /** How many more of each kind the player may place. */
  tools: Partial<Record<SimKind, number>>;
  /** Minimum number of each kind on the table at the end (given ones count). */
  needs?: Partial<Record<SimKind, number>>;
  /** Pairs that must be able to ping each other: a device label, or "*pc" / "*server" for every device of that kind. */
  pairs: Array<[string, string]>;
  /** Hard rounds: no more than this many switches in total. */
  maxSwitches?: number;
  why: string;
}

export interface SimData {
  id: string;
  title: string;
  intro: string;
  howTo: string[];
  levels: Record<Level, { lives: number; timeLimitPerTaskSec: number | null; attempts: number; rounds: SimRound[] }>;
}

export const MAX_PORTS: Record<SimKind, number> = { pc: 1, server: 1, switch: 8 };
export const KIND_NAME: Record<SimKind, string> = { pc: 'מחשב', server: 'שרת', switch: 'מתג' };

export const linkId = (a: string, b: string): string => (a < b ? `${a}|${b}` : `${b}|${a}`);

export function degree(links: Set<string>, id: string): number {
  let n = 0;
  for (const k of links) if (k.split('|').includes(id)) n++;
  return n;
}

export type LinkCheck = { ok: true } | { ok: false; message: string };

/** A computer or a server has one network port; a switch has many. Two switches may be linked, a device may not link to itself. */
export function canLink(devices: SimDevice[], links: Set<string>, a: string, b: string): LinkCheck {
  if (a === b) return { ok: false, message: '' };
  const da = devices.find((d) => d.id === a);
  const db = devices.find((d) => d.id === b);
  if (!da || !db) return { ok: false, message: '' };
  if (links.has(linkId(a, b))) return { ok: true };
  for (const d of [da, db]) {
    if (degree(links, d.id) >= MAX_PORTS[d.kind]) return { ok: false, message: `ל${KIND_NAME[d.kind]} "${d.label}" יש רק ${MAX_PORTS[d.kind] === 1 ? 'חיבור אחד' : `${MAX_PORTS[d.kind]} חיבורים`}. כדי לחבר עוד מכשירים צריך מתג.` };
  }
  return { ok: true };
}

/** Shortest path of device ids from a to b, or null. */
export function findPath(devices: SimDevice[], links: Set<string>, a: string, b: string): string[] | null {
  const adj = new Map<string, string[]>();
  for (const k of links) {
    const [x, y] = k.split('|') as [string, string];
    (adj.get(x) ?? adj.set(x, []).get(x) as string[]).push(y);
    (adj.get(y) ?? adj.set(y, []).get(y) as string[]).push(x);
  }
  const prev = new Map<string, string | null>([[a, null]]);
  const queue = [a];
  while (queue.length) {
    const cur = queue.shift() as string;
    if (cur === b) {
      const path: string[] = [];
      for (let n: string | null = b; n; n = prev.get(n) ?? null) path.unshift(n);
      return path;
    }
    for (const nx of adj.get(cur) ?? []) if (!prev.has(nx)) { prev.set(nx, cur); queue.push(nx); }
  }
  void devices;
  return null;
}

export interface PingResult { from: string; to: string; path: string[] | null }

export type SimVerdict = { ok: true; pings: PingResult[] } | { ok: false; message: string; pings: PingResult[] };

function expand(devices: SimDevice[], label: string): SimDevice[] {
  if (label.startsWith('*')) return devices.filter((d) => d.kind === label.slice(1));
  return devices.filter((d) => d.label === label);
}

/** Run the round's pings and check the round's limits. */
export function runPings(round: SimRound, devices: SimDevice[], links: Set<string>): SimVerdict {
  const pings: PingResult[] = [];
  const seen = new Set<string>();
  for (const [a, b] of round.pairs) {
    for (const da of expand(devices, a)) {
      for (const db of expand(devices, b)) {
        if (da.id === db.id) continue;
        const key = linkId(da.id, db.id);
        if (seen.has(key)) continue;
        seen.add(key);
        pings.push({ from: da.label, to: db.label, path: findPath(devices, links, da.id, db.id) });
      }
    }
  }
  for (const [kind, n] of Object.entries(round.needs ?? {}) as Array<[SimKind, number]>) {
    const have = devices.filter((d) => d.kind === kind).length;
    if (have < n) return { ok: false, pings, message: `צריך ${n} ${kind === 'pc' ? 'מחשבים' : kind === 'server' ? 'שרתים' : 'מתגים'} ברשת, ויש רק ${have}. הציבו עוד.` };
  }
  const switches = devices.filter((d) => d.kind === 'switch').length;
  if (round.maxSwitches !== undefined && switches > round.maxSwitches) {
    return { ok: false, pings, message: `יש כאן ${switches} מתגים, ואפשר להסתדר עם ${round.maxSwitches}. נסו לחסוך בציוד.` };
  }
  if (!pings.length) return { ok: false, pings, message: 'אין עדיין מה לבדוק. חברו מכשירים.' };
  const bad = pings.find((p) => !p.path);
  if (bad) return { ok: false, pings, message: `הפינג מ"${bad.from}" אל "${bad.to}" לא הגיע: אין דרך מחוברת ביניהם.` };
  return { ok: true, pings };
}
