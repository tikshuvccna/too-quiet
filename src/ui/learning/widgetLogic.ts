/** Pure logic behind the lesson widgets, kept free of the DOM so it can be tested. */

// ---- connect_threads -------------------------------------------------------

export const MAX_THREADS = 6;

export function edgeKey(a: string, b: string): string {
  return a < b ? `${a}|${b}` : `${b}|${a}`;
}

export function splitEdge(key: string): [string, string] {
  const [a = '', b = ''] = key.split('|');
  return [a, b];
}

export type ToggleResult = { edges: string[]; action: 'added' | 'removed' | 'full' | 'same' };

/** Pressing two devices adds a thread; pressing the same pair again removes it. */
export function toggleEdge(edges: readonly string[], a: string, b: string, max = MAX_THREADS): ToggleResult {
  if (a === b) return { edges: edges.slice(), action: 'same' };
  const k = edgeKey(a, b);
  if (edges.includes(k)) return { edges: edges.filter((e) => e !== k), action: 'removed' };
  if (edges.length >= max) return { edges: edges.slice(), action: 'full' };
  return { edges: [...edges, k], action: 'added' };
}

function neighbours(edges: readonly string[]): Map<string, string[]> {
  const m = new Map<string, string[]>();
  for (const e of edges) {
    const [a, b] = splitEdge(e);
    m.set(a, [...(m.get(a) ?? []), b]);
    m.set(b, [...(m.get(b) ?? []), a]);
  }
  return m;
}

/** Shortest path of device ids along the threads, or null when there is none. */
export function findPath(edges: readonly string[], from: string, to: string): string[] | null {
  if (from === to) return [from];
  const nb = neighbours(edges);
  const prev = new Map<string, string>();
  const seen = new Set<string>([from]);
  const queue = [from];
  while (queue.length) {
    const cur = queue.shift() as string;
    for (const n of nb.get(cur) ?? []) {
      if (seen.has(n)) continue;
      seen.add(n);
      prev.set(n, cur);
      if (n === to) {
        const path = [to];
        let p = to;
        while (prev.has(p)) {
          p = prev.get(p) as string;
          path.unshift(p);
        }
        return path;
      }
      queue.push(n);
    }
  }
  return null;
}

/** True when every device can reach every other one. */
export function allConnected(ids: readonly string[], edges: readonly string[]): boolean {
  const first = ids[0];
  if (first === undefined) return false;
  return ids.every((id) => findPath(edges, first, id) !== null);
}

// ---- sorting cards and matching --------------------------------------------

export function isRight(answer: string, picked: string): boolean {
  return answer === picked;
}

/** After two wrong tries on the same item the right answer is hinted. */
export function needsHint(wrongCount: number): boolean {
  return wrongCount >= 2;
}

// ---- client_server_toy -----------------------------------------------------

export type Power = 'weak' | 'medium' | 'strong';
/** Customers the server handles per second, from the content: 1, 2, 5. */
export const SERVICE_RATE: Record<Power, number> = { weak: 1, medium: 2, strong: 5 };
export const TRAVEL_SEC = 0.25;

export interface Job { start: number; arrive: number; serviceStart: number; serviceEnd: number; back: number; failed: boolean }

/** One server that handles one request at a time. With the server down every request just comes back empty. */
export function scheduleRequests(starts: readonly number[], rate: number, travel = TRAVEL_SEC, serverDown = false): Job[] {
  let free = 0;
  return starts.map((start) => {
    const arrive = start + travel;
    if (serverDown) return { start, arrive, serviceStart: arrive, serviceEnd: arrive, back: arrive + travel, failed: true };
    const serviceStart = Math.max(arrive, free);
    const serviceEnd = serviceStart + 1 / rate;
    free = serviceEnd;
    return { start, arrive, serviceStart, serviceEnd, back: serviceEnd + travel, failed: false };
  });
}

export function longestWait(jobs: readonly Job[]): number {
  return jobs.reduce((m, j) => Math.max(m, j.back - j.start), 0);
}

export const POWER_BARS: Record<Power, [number, number, number]> = {
  weak: [0.25, 0.2, 0.3],
  medium: [0.55, 0.5, 0.6],
  strong: [0.95, 0.9, 0.95],
};

// ---- atm_toy ---------------------------------------------------------------

export type AtmMode = 'connected' | 'offline';
export type AtmName = 'metula' | 'eilat';
export const START_BALANCE = 500;

export interface AtmState {
  mode: AtmMode;
  shown: Record<AtmName, number>;
  withdrawn: number;
  used: Record<AtmName, boolean>;
}

export function atmInit(mode: AtmMode): AtmState {
  return { mode, shown: { metula: START_BALANCE, eilat: START_BALANCE }, withdrawn: 0, used: { metula: false, eilat: false } };
}

/** Connected machines all ask the bank server, so every one shows the new balance. Offline, only the used one changes. */
export function atmWithdraw(s: AtmState, atm: AtmName, amount: number): AtmState {
  const shown = s.mode === 'connected'
    ? { metula: s.shown.metula - amount, eilat: s.shown.eilat - amount }
    : { ...s.shown, [atm]: s.shown[atm] - amount };
  return { ...s, shown, withdrawn: s.withdrawn + amount, used: { ...s.used, [atm]: true } };
}

export function atmTruth(s: AtmState): number {
  return START_BALANCE - s.withdrawn;
}

/** The balances disagree with the truth: the bank did not know. */
export function atmOutOfSync(s: AtmState): boolean {
  return s.shown.metula !== atmTruth(s) || s.shown.eilat !== atmTruth(s);
}

export function atmBothUsed(s: AtmState): boolean {
  return s.used.metula && s.used.eilat;
}

export function money(n: number): string {
  return `${n < 0 ? '−' : ''}${Math.abs(n).toLocaleString('en-US')} ₪`;
}

// ---- p2p_vs_cs_toy ---------------------------------------------------------

/** In peer-to-peer the asker is the client and the partner is the server. Prefer the last asker so roles visibly swap. */
export function pickPartner(on: readonly boolean[], client: number, lastClient: number | null): number | null {
  if (lastClient !== null && lastClient !== client && on[lastClient]) return lastClient;
  for (let step = 1; step < on.length; step++) {
    const j = (client + step) % on.length;
    if (on[j]) return j;
  }
  return null;
}

export function rolesSwapped(clients: ReadonlySet<number>, servers: ReadonlySet<number>): boolean {
  for (const c of clients) if (servers.has(c)) return true;
  return false;
}
