/**
 * The house book: one card per building of the valley, discovered in three layers.
 * 1. picture, name, owner   2. history   3. what is wrong and what needs fixing.
 */
import infoJson from '../../content/he/world/house_info.json';

export interface HouseInfo {
  id: string;
  atlas: 'buildings' | 'buildings2a' | 'buildings2b';
  frame: string;
  name: string;
  owner: string;
  role: string;
  history: string[];
  problem: string;
  topic: string;
  /** "מה חשוב כאן": the one important thing of the house. */
  important: string;
  /** Flag set when the owner was talked to. */
  met?: string;
  /** Story flags (any of them) that show layer 3. Without them layer 3 comes after the owner conversation. */
  fix?: string[];
  /** Extra flags that show layer 1 / layer 2 (for buildings without a door). */
  l1?: string[];
  l2?: string[];
}

export const HOUSE_INFO = (infoJson as unknown as { houses: HouseInfo[] }).houses;

export interface BookProbe {
  has(flag: string): boolean;
  /** How many flags start with this prefix. */
  count(prefix: string): number;
}

export interface Layers { l1: boolean; l2: boolean; l3: boolean }

export const bookFlag = (id: string): string => `book:${id}`;
export const inspectedFlag = (houseId: string, objectId: string): string => `insp:${houseId}:${objectId}`;

export function layersOf(h: HouseInfo, p: BookProbe): Layers {
  const met = !!h.met && p.has(h.met);
  const l1 = p.has(bookFlag(h.id)) || met || !!h.l1?.some((f) => p.has(f));
  if (!l1) return { l1: false, l2: false, l3: false };
  const l3 = h.fix ? h.fix.some((f) => p.has(f)) : met;
  const l2 = l3 || met || p.count(`insp:${h.id}:`) >= 2 || !!h.l2?.some((f) => p.has(f));
  return { l1, l2, l3 };
}
