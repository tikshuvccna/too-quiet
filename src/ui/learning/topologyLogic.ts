import type { Level } from './types';

export interface TopoNode { id: string; label: string; x: number; y: number; kind: 'device' | 'link' }
export type TopoFailure = { type: 'link'; a: string; b: string } | { type: 'node'; id: string };

export interface TopologyRound {
  text: string;
  nodes: TopoNode[];
  links: Array<[string, string]>;
  failure: TopoFailure;
  /** The device everyone wants to reach. */
  target: string;
  why: string;
}

export interface TopologyData {
  id: string;
  title: string;
  intro: string;
  levels: Record<Level, { lives: number; timeLimitPerTaskSec: number | null; rounds: TopologyRound[] }>;
}

/** Nodes still alive after the failure, and the links that still work. */
export function survivors(r: TopologyRound): { nodes: Set<string>; links: Array<[string, string]> } {
  const f = r.failure;
  const nodes = new Set(r.nodes.map((n) => n.id));
  if (f.type === 'node') nodes.delete(f.id);
  const links = r.links.filter(([a, b]) => {
    if (!nodes.has(a) || !nodes.has(b)) return false;
    if (f.type === 'link' && ((f.a === a && f.b === b) || (f.a === b && f.b === a))) return false;
    return true;
  });
  return { nodes, links };
}

/** The component of the graph that still contains `from`. */
export function reachable(r: TopologyRound, from: string): Set<string> {
  const { nodes, links } = survivors(r);
  const seen = new Set<string>();
  if (!nodes.has(from)) return seen;
  const adj = new Map<string, string[]>();
  for (const [a, b] of links) {
    (adj.get(a) ?? adj.set(a, []).get(a) as string[]).push(b);
    (adj.get(b) ?? adj.set(b, []).get(b) as string[]).push(a);
  }
  const stack = [from];
  seen.add(from);
  while (stack.length) {
    const cur = stack.pop() as string;
    for (const nx of adj.get(cur) ?? []) if (!seen.has(nx)) { seen.add(nx); stack.push(nx); }
  }
  return seen;
}

/**
 * The devices that lose contact with the target. A device that itself failed is not asked about
 * (it is shown as broken), and the target never counts as cut off from itself.
 */
export function cutOff(r: TopologyRound): string[] {
  const ok = reachable(r, r.target);
  const f = r.failure;
  return r.nodes
    .filter((n) => n.kind === 'device' && n.id !== r.target && !(f.type === 'node' && f.id === n.id))
    .filter((n) => !ok.has(n.id))
    .map((n) => n.id);
}
