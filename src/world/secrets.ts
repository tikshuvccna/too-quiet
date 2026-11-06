import data from '../../content/he/world/secrets.json';
import type { SaveStore } from '../core/save';

export type Glyph = 'sun' | 'moon' | 'star' | 'wave' | 'leaf' | 'flame' | 'bell' | 'lamp' | 'mushroom' | 'rings';

export interface SecretNode { id: string; x: number; y: number; glyph: Glyph; color: string; label: string; size?: number; n?: number }
export interface SecretReward {
  coins: number;
  food?: { key: string; name: string; n: number };
  keepsake?: { flag: string; name: string };
}
export interface SecretClue { house: string; object: string; title: string; found: string; lines: string[]; footer: string }
export interface SecretDef {
  id: string;
  name: string;
  region: string;
  style: 'stones' | 'bells' | 'lamps' | 'mushrooms' | 'tree';
  center: [number, number];
  showRadius: number;
  nodes: SecretNode[];
  order: string[];
  nodeNames?: Record<string, string>;
  wrongHint: string;
  clue: SecretClue;
  hintAfterClue: string;
  reveal: { title: string; lines: string[] };
  reward: SecretReward;
  hatch?: [number, number];
}

export const SECRETS: SecretDef[] = (data as unknown as { secrets: SecretDef[] }).secrets;

export const solvedFlag = (id: string): string => `secret.${id}.solved`;
export const clueFlag = (id: string): string => `clue.${id}.found`;
export const targetId = (secretId: string, nodeId: string): string => `secret:${secretId}:${nodeId}`;

export function parseTarget(id: string): { secretId: string; nodeId: string } | null {
  const [p, secretId, nodeId] = id.split(':');
  if (p !== 'secret' || !secretId || !nodeId) return null;
  return { secretId, nodeId };
}

export type StepResult = 'ok' | 'wrong' | 'solved';

/** Pure checker: the player's presses so far (ids) and one more press. A wrong press clears everything. */
export function step(order: readonly string[], pressed: readonly string[], nodeId: string): { result: StepResult; pressed: string[] } {
  const next = [...pressed, nodeId];
  if (order[pressed.length] !== nodeId) return { result: 'wrong', pressed: [] };
  return next.length === order.length ? { result: 'solved', pressed: next } : { result: 'ok', pressed: next };
}

/** In-memory progress of the current attempt (not saved: a puzzle is solved or not). */
const progress = new Map<string, string[]>();
export const progressOf = (id: string): readonly string[] => progress.get(id) ?? [];
export function resetProgress(id?: string): void {
  if (id) progress.delete(id);
  else progress.clear();
}

export function press(def: SecretDef, nodeId: string): StepResult {
  const r = step(def.order, progressOf(def.id), nodeId);
  if (r.result === 'solved') progress.delete(def.id);
  else if (r.pressed.length) progress.set(def.id, r.pressed);
  else progress.delete(def.id);
  return r.result;
}

export const isSolved = (save: SaveStore, def: SecretDef): boolean => save.hasFlag(solvedFlag(def.id));
export const clueFound = (save: SaveStore, def: SecretDef): boolean => save.hasFlag(clueFlag(def.id));

/** Paid once. Returns the text of what was given, or null when the secret was already solved. */
export function grantReward(save: SaveStore, def: SecretDef, coinMul = 1): string | null {
  if (save.hasFlag(solvedFlag(def.id))) return null;
  const r = def.reward;
  const gained = Math.round(r.coins * coinMul);
  save.data.coins += gained;
  const parts = [`${gained} מטבעות`];
  if (r.food) {
    save.data.inv[r.food.key] = (save.data.inv[r.food.key] ?? 0) + r.food.n;
    parts.push(`${r.food.n} ${r.food.name} ליצורים`);
  }
  if (r.keepsake) {
    save.data.flags[r.keepsake.flag] = true;
    parts.push(r.keepsake.name);
  }
  save.data.flags[solvedFlag(def.id)] = true;
  save.save();
  return parts.join(', ');
}

/** Secrets with an object in this house that carries their clue. */
export function cluesIn(houseId: string, objectId: string): SecretDef[] {
  return SECRETS.filter((s) => s.clue.house === houseId && s.clue.object === objectId);
}

/** A subtle line for the objective bar, only once a clue was found and its puzzle is still open. */
export function hintFor(save: SaveStore): string | null {
  const s = SECRETS.find((d) => clueFound(save, d) && !isSolved(save, d));
  return s ? s.hintAfterClue : null;
}

export const secretById = (id: string): SecretDef | undefined => SECRETS.find((s) => s.id === id);
