/** Rules of bridge building: every bank and house must be joined by planks, using no more planks than the budget. Pure functions, no DOM. */

export type BridgeLevel = 'easy' | 'medium' | 'hard';
export interface BNode { x: number; y: number; kind: 'bank' | 'house' }
/** a and b are node indexes, cost is the number of planks the link needs. */
export interface BEdge { a: number; b: number; cost: number }
export interface BridgeCfg { nodes: BNode[]; edges: BEdge[]; slack: number }

const bank = (x: number, y: number): BNode => ({ x, y, kind: 'bank' });
const house = (x: number, y: number): BNode => ({ x, y, kind: 'house' });

export const BRIDGE_CFG: Record<BridgeLevel, BridgeCfg> = {
  easy: {
    nodes: [bank(40, 130), house(140, 60), house(140, 200), house(260, 130), bank(360, 130)],
    edges: [
      { a: 0, b: 1, cost: 1 }, { a: 0, b: 2, cost: 1 }, { a: 1, b: 2, cost: 1 },
      { a: 1, b: 3, cost: 1 }, { a: 2, b: 3, cost: 1 }, { a: 3, b: 4, cost: 1 },
    ],
    slack: 1,
  },
  medium: {
    nodes: [bank(40, 130), house(120, 50), house(120, 210), house(220, 110), house(240, 215), bank(360, 130)],
    edges: [
      { a: 0, b: 1, cost: 2 }, { a: 0, b: 2, cost: 2 }, { a: 1, b: 2, cost: 3 }, { a: 1, b: 3, cost: 2 },
      { a: 2, b: 3, cost: 2 }, { a: 2, b: 4, cost: 2 }, { a: 3, b: 4, cost: 2 }, { a: 3, b: 5, cost: 3 }, { a: 4, b: 5, cost: 2 },
    ],
    slack: 1,
  },
  hard: {
    nodes: [bank(40, 130), house(120, 50), house(120, 210), house(220, 120), house(240, 220), house(300, 40), bank(360, 130)],
    edges: [
      { a: 0, b: 1, cost: 2 }, { a: 0, b: 2, cost: 2 }, { a: 1, b: 2, cost: 3 }, { a: 1, b: 3, cost: 3 },
      { a: 2, b: 3, cost: 2 }, { a: 2, b: 4, cost: 2 }, { a: 3, b: 4, cost: 2 }, { a: 3, b: 5, cost: 2 },
      { a: 3, b: 6, cost: 3 }, { a: 4, b: 6, cost: 2 }, { a: 5, b: 6, cost: 2 }, { a: 1, b: 5, cost: 4 },
    ],
    slack: 0,
  },
};

/** Number of separate groups the chosen links leave (1 means everything is joined). */
export function groupCount(nodeCount: number, edges: readonly BEdge[], chosen: ReadonlySet<number>): number {
  const parent = Array.from({ length: nodeCount }, (_, i) => i);
  const find = (i: number): number => {
    while (parent[i] !== i) i = parent[i] = parent[parent[i] as number] as number;
    return i;
  };
  let groups = nodeCount;
  for (const idx of chosen) {
    const e = edges[idx];
    if (!e) continue;
    const ra = find(e.a);
    const rb = find(e.b);
    if (ra !== rb) { parent[ra] = rb; groups--; }
  }
  return groups;
}

export const allConnected = (nodeCount: number, edges: readonly BEdge[], chosen: ReadonlySet<number>): boolean =>
  groupCount(nodeCount, edges, chosen) === 1;

export function totalCost(edges: readonly BEdge[], chosen: ReadonlySet<number>): number {
  let sum = 0;
  for (const idx of chosen) sum += edges[idx]?.cost ?? 0;
  return sum;
}

/** The fewest planks that can join everything: cheapest links first, skipping any that close a loop. */
export function minimumCost(nodeCount: number, edges: readonly BEdge[]): number {
  const order = edges.map((_, i) => i).sort((p, q) => (edges[p] as BEdge).cost - (edges[q] as BEdge).cost);
  const picked = new Set<number>();
  let sum = 0;
  for (const idx of order) {
    const before = groupCount(nodeCount, edges, picked);
    picked.add(idx);
    if (groupCount(nodeCount, edges, picked) < before) sum += (edges[idx] as BEdge).cost;
    else picked.delete(idx);
  }
  return sum;
}

export const budgetOf = (cfg: BridgeCfg, calm: boolean): number => minimumCost(cfg.nodes.length, cfg.edges) + cfg.slack + (calm ? 1 : 0);

export type BridgeState = 'open' | 'over' | 'done';
/** done: everything joined within the budget; over: joined but too many planks; open: still gaps. */
export function bridgeState(cfg: BridgeCfg, chosen: ReadonlySet<number>, budget: number): BridgeState {
  if (!allConnected(cfg.nodes.length, cfg.edges, chosen)) return 'open';
  return totalCost(cfg.edges, chosen) <= budget ? 'done' : 'over';
}
