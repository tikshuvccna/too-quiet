import { describe, expect, it } from 'vitest';
import { QualityManager, detectQuality } from './quality';
import { SaveStore } from './save';

const nav = (deviceMemory: number | undefined, hardwareConcurrency: number | undefined, userAgent = 'x') => ({ deviceMemory, hardwareConcurrency, userAgent });

describe('quality detection', () => {
  it('rates a strong desktop high, a weak phone low and a Chromebook lower', () => {
    expect(detectQuality(nav(8, 12), false, 1)).toBe('high');
    expect(detectQuality(nav(2, 4), true, 3)).toBe('low');
    expect(detectQuality(nav(4, 4, 'Mozilla CrOS'), false, 1)).toBe('medium');
    expect(detectQuality(nav(undefined, undefined), false, 1)).toBe('medium');
  });
});

describe('quality manager', () => {
  const make = (rec: 'low' | 'medium' | 'high') => {
    const save = new SaveStore(null);
    save.load();
    return { save, q: new QualityManager(save, rec) };
  };

  it('uses the recommendation by default and a fixed level when chosen', () => {
    const { q } = make('medium');
    expect(q.level).toBe('medium');
    q.set('high');
    expect(q.level).toBe('high');
    q.set('auto');
    expect(q.level).toBe('medium');
  });

  it('steps down by itself in auto mode after six slow seconds, never below low', () => {
    const { q } = make('high');
    const lowered: string[] = [];
    q.onAutoLowered = (to) => lowered.push(to);
    for (let i = 0; i < 5; i++) q.sample(20);
    expect(q.level).toBe('high');
    q.sample(20);
    expect(q.level).toBe('medium');
    for (let i = 0; i < 12; i++) q.sample(10);
    expect(q.level).toBe('low');
    for (let i = 0; i < 12; i++) q.sample(10);
    expect(q.level).toBe('low');
    expect(lowered).toEqual(['medium', 'low']);
  });

  it('does not touch a level the player fixed, and a good second resets the count', () => {
    const { q } = make('high');
    q.set('high');
    for (let i = 0; i < 20; i++) q.sample(5);
    expect(q.level).toBe('high');
    q.set('auto');
    for (let i = 0; i < 5; i++) q.sample(20);
    q.sample(60);
    for (let i = 0; i < 5; i++) q.sample(20);
    expect(q.level).toBe('high');
  });
});
