import { describe, expect, it } from 'vitest';
import {
  MAX_THREADS, SERVICE_RATE, allConnected, atmBothUsed, atmInit, atmOutOfSync, atmTruth, atmWithdraw, edgeKey,
  findPath, isRight, longestWait, money, needsHint, pickPartner, rolesSwapped, scheduleRequests, toggleEdge,
} from './widgetLogic';

describe('connect_threads logic', () => {
  it('adds, removes and limits threads', () => {
    let r = toggleEdge([], 'a', 'b');
    expect(r).toEqual({ edges: ['a|b'], action: 'added' });
    expect(edgeKey('b', 'a')).toBe('a|b');
    r = toggleEdge(r.edges, 'b', 'a');
    expect(r).toEqual({ edges: [], action: 'removed' });
    expect(toggleEdge([], 'a', 'a').action).toBe('same');
    const six = ['a|b', 'a|c', 'a|d', 'b|c', 'b|d', 'c|d'];
    expect(six).toHaveLength(MAX_THREADS);
    expect(toggleEdge(six, 'a', 'e').action).toBe('full');
  });

  it('finds a path through devices in between, or none', () => {
    const edges = ['a|b', 'b|c'];
    expect(findPath(edges, 'a', 'c')).toEqual(['a', 'b', 'c']);
    expect(findPath(edges, 'c', 'a')).toEqual(['c', 'b', 'a']);
    expect(findPath(edges, 'a', 'd')).toBeNull();
    expect(findPath([], 'a', 'a')).toEqual(['a']);
  });

  it('detects a single connected group', () => {
    const ids = ['a', 'b', 'c', 'd'];
    expect(allConnected(ids, ['a|b', 'b|c'])).toBe(false);
    expect(allConnected(ids, ['a|b', 'b|c', 'c|d'])).toBe(true);
    expect(allConnected(ids, ['a|b', 'c|d'])).toBe(false);
    expect(allConnected([], [])).toBe(false);
  });
});

describe('sorting and matching logic', () => {
  it('judges and hints', () => {
    expect(isRight('home', 'home')).toBe(true);
    expect(isRight('home', 'soho')).toBe(false);
    expect(needsHint(1)).toBe(false);
    expect(needsHint(2)).toBe(true);
  });
});

describe('client_server schedule', () => {
  it('serves one customer in about a second on a weak server', () => {
    const [j] = scheduleRequests([0], SERVICE_RATE.weak);
    expect(j?.back).toBeCloseTo(1.5, 5);
  });

  it('queues five at once: 5.5 s weak, 1.5 s strong', () => {
    const weak = scheduleRequests([0, 0, 0, 0, 0], SERVICE_RATE.weak);
    const strong = scheduleRequests([0, 0, 0, 0, 0], SERVICE_RATE.strong);
    expect(longestWait(weak)).toBeCloseTo(5.5, 5);
    expect(longestWait(strong)).toBeCloseTo(1.5, 5);
    expect(longestWait(scheduleRequests([0, 0, 0, 0, 0], SERVICE_RATE.medium))).toBeCloseTo(3, 5);
    expect(weak[1]?.serviceStart).toBeCloseTo(weak[0]?.serviceEnd ?? -1, 5);
  });

  it('sends everything back empty when the server is down', () => {
    const jobs = scheduleRequests([0, 0], 5, 0.25, true);
    expect(jobs.every((j) => j.failed)).toBe(true);
    expect(longestWait(jobs)).toBeCloseTo(0.5, 5);
  });
});

describe('atm logic', () => {
  it('connected: both machines show the shared balance', () => {
    let s = atmInit('connected');
    s = atmWithdraw(s, 'metula', 1000);
    expect(s.shown).toEqual({ metula: -500, eilat: -500 });
    s = atmWithdraw(s, 'eilat', 500);
    expect(s.shown).toEqual({ metula: -1000, eilat: -1000 });
    expect(atmTruth(s)).toBe(-1000);
    expect(atmOutOfSync(s)).toBe(false);
    expect(atmBothUsed(s)).toBe(true);
  });

  it('offline: each machine only knows itself, the bank is not told', () => {
    let s = atmInit('offline');
    s = atmWithdraw(s, 'metula', 1000);
    expect(s.shown).toEqual({ metula: -500, eilat: 500 });
    s = atmWithdraw(s, 'eilat', 500);
    expect(s.shown).toEqual({ metula: -500, eilat: 0 });
    expect(atmTruth(s)).toBe(-1000);
    expect(s.withdrawn).toBe(1500);
    expect(atmOutOfSync(s)).toBe(true);
  });

  it('formats money with a real minus sign', () => {
    expect(money(-1000)).toBe('−1,000 ₪');
    expect(money(500)).toBe('500 ₪');
  });
});

describe('p2p logic', () => {
  it('prefers the previous asker as the server so the roles swap', () => {
    const on = [true, true, true, true, true];
    expect(pickPartner(on, 0, null)).toBe(1);
    expect(pickPartner(on, 3, 0)).toBe(0);
    expect(pickPartner(on, 0, 0)).toBe(1);
  });

  it('skips switched-off computers and returns null when alone', () => {
    expect(pickPartner([true, false, true, true, true], 0, null)).toBe(2);
    expect(pickPartner([true, true, true, true, true], 2, 1)).toBe(1);
    expect(pickPartner([true, false, true, true, true], 2, 1)).toBe(3);
    expect(pickPartner([true, false, false, false, false], 0, null)).toBeNull();
  });

  it('detects a computer that was both client and server', () => {
    expect(rolesSwapped(new Set([0]), new Set([1]))).toBe(false);
    expect(rolesSwapped(new Set([0, 1]), new Set([1, 0]))).toBe(true);
  });
});
