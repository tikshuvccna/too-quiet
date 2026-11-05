import { describe, expect, it, vi } from 'vitest';
import { Session } from './session';
import { Bus } from './bus';
import { SaveStore, SAVE_KEY, emptySave, normalize } from './save';

describe('Session', () => {
  it('warns, then storms at the cap', () => {
    const onWarning = vi.fn();
    const onStorm = vi.fn();
    const s = new Session({ capSeconds: 10, warnAtSeconds: 8, onWarning, onStorm });
    s.tick(7.9);
    expect(s.phase).toBe('free');
    s.tick(0.2);
    expect(s.phase).toBe('warning');
    expect(onWarning).toHaveBeenCalledOnce();
    s.tick(2);
    expect(s.phase).toBe('storm');
    expect(onStorm).toHaveBeenCalledOnce();
    s.tick(5);
    expect(onStorm).toHaveBeenCalledOnce();
  });

  it('does not count time while paused', () => {
    const s = new Session({ capSeconds: 10 });
    s.pause();
    s.tick(100);
    expect(s.elapsed).toBe(0);
    s.resume();
    s.tick(1);
    expect(s.elapsed).toBe(1);
    expect(s.remaining).toBe(9);
  });

  it('restarts for a new session', () => {
    const s = new Session({ capSeconds: 5, warnAtSeconds: 3 });
    s.tick(6);
    expect(s.phase).toBe('storm');
    s.restart();
    expect(s.phase).toBe('free');
    expect(s.elapsed).toBe(0);
  });

  it('keeps the warning before the cap even for a tiny cap', () => {
    const s = new Session({ capSeconds: 2 });
    expect(s.warnAt).toBeLessThan(s.cap);
  });
});

describe('SaveStore', () => {
  const mem = () => {
    const m = new Map<string, string>();
    return { getItem: (k: string) => m.get(k) ?? null, setItem: (k: string, v: string) => void m.set(k, v), removeItem: (k: string) => void m.delete(k), m };
  };

  it('round-trips data', () => {
    const store = mem();
    const a = new SaveStore(store);
    a.load();
    a.data.coins = 7;
    a.setFlag('met-dvora');
    const b = new SaveStore(store);
    b.load();
    expect(b.data.coins).toBe(7);
    expect(b.hasFlag('met-dvora')).toBe(true);
  });

  it('falls back to a fresh save on corrupted data', () => {
    const store = mem();
    store.setItem(SAVE_KEY, '{not json');
    const s = new SaveStore(store);
    expect(s.load()).toEqual(emptySave());
  });

  it('keeps older saves working when new fields appear', () => {
    const d = normalize({ coins: 3, settings: { subtitles: false } });
    expect(d.coins).toBe(3);
    expect(d.settings).toEqual({ subtitles: false, sound: false, quality: 'auto', showFps: false, musicOn: true, sfxOn: true, musicVol: 0.5, sfxVol: 0.8 });
    expect(d.lessons).toEqual({});
  });

  it('works without any storage', () => {
    const s = new SaveStore(null);
    s.load();
    s.setFlag('x');
    expect(s.hasFlag('x')).toBe(true);
  });

  it('computes power from completed lessons', () => {
    const s = new SaveStore(null);
    s.load();
    s.lesson('l1').done = true;
    s.lesson('l2');
    expect(s.recomputePower()).toBe(1);
  });
});

describe('Bus', () => {
  it('delivers events and unsubscribes', () => {
    const bus = new Bus();
    const h = vi.fn();
    const off = bus.on('sight:toggle', h);
    bus.emit('sight:toggle', { on: true });
    off();
    bus.emit('sight:toggle', { on: false });
    expect(h).toHaveBeenCalledOnce();
    expect(h).toHaveBeenCalledWith({ on: true });
  });
});
