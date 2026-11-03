/** Tiny typed event bus between Phaser scenes and the DOM UI. */
export interface GameEvents {
  'interact:available': { id: string; label: string } | null;
  'interact:use': { id: string };
  'world:enter-house': { houseId: string };
  'world:exit-house': { houseId: string };
  'house:entered': { houseId: string };
  'sight:toggle': { on: boolean };
  'fault:fixed': { id: string; evidence: 'natural' | 'hand' };
  'item:collected': { id: string };
  'session:warning': undefined;
  'session:storm': undefined;
  'ui:pause': { paused: boolean };
}

type Handler<T> = (payload: T) => void;

export class Bus {
  private map = new Map<keyof GameEvents, Set<Handler<never>>>();

  on<K extends keyof GameEvents>(k: K, h: Handler<GameEvents[K]>): () => void {
    let s = this.map.get(k);
    if (!s) this.map.set(k, (s = new Set()));
    s.add(h as Handler<never>);
    return () => s?.delete(h as Handler<never>);
  }

  emit<K extends keyof GameEvents>(k: K, payload: GameEvents[K]): void {
    this.map.get(k)?.forEach((h) => (h as Handler<GameEvents[K]>)(payload));
  }
}

export const bus = new Bus();
