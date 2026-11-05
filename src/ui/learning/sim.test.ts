import { describe, expect, it } from 'vitest';
import sim05 from '../../../content/he/sim05.json';
import { type SimData, type SimDevice, canLink, linkId, runPings } from './simLogic';

const data = sim05 as unknown as SimData;
const dev = (id: string, kind: SimDevice['kind'], label = id): SimDevice => ({ id, kind, label, x: 0, y: 0, fixed: true });

describe('simulator rules', () => {
  it('a computer has one port, a switch eight', () => {
    const ds = [dev('a', 'pc'), dev('b', 'pc'), dev('c', 'pc'), dev('s', 'switch')];
    const links = new Set([linkId('a', 's')]);
    expect(canLink(ds, links, 'a', 'b').ok).toBe(false);
    expect(canLink(ds, links, 'b', 's').ok).toBe(true);
    const full = new Set(Array.from({ length: 8 }, (_, i) => linkId(`x${i}`, 's')));
    expect(canLink([...ds, ...Array.from({ length: 8 }, (_, i) => dev(`x${i}`, 'pc'))], full, 'c', 's').ok).toBe(false);
  });

  it('pings follow the wires and need a switch in the middle', () => {
    const ds = [dev('a', 'pc', 'א'), dev('b', 'pc', 'ב'), dev('s', 'switch')];
    const round = { text: '', given: [], tools: {}, pairs: [['*pc', '*pc']] as Array<[string, string]>, why: '' };
    expect(runPings(round, ds, new Set()).ok).toBe(false);
    expect(runPings(round, ds, new Set([linkId('a', 's'), linkId('b', 's')])).ok).toBe(true);
    expect(runPings(round, ds, new Set([linkId('a', 'b')])).ok).toBe(true);
  });

  it('limits: not enough devices, too many switches', () => {
    const ds = [dev('a', 'pc'), dev('s1', 'switch'), dev('s2', 'switch')];
    const links = new Set([linkId('a', 's1'), linkId('s1', 's2')]);
    const r = { text: '', given: [], tools: {}, needs: { pc: 2 }, pairs: [['*pc', '*pc']] as Array<[string, string]>, why: '' };
    expect(runPings(r, ds, links).ok).toBe(false);
    const r2 = { ...r, needs: {}, maxSwitches: 1, pairs: [['*pc', '*switch']] as Array<[string, string]> };
    const v = runPings(r2, ds, links);
    expect(v.ok).toBe(false);
  });
});

describe('simulator content', () => {
  const rounds = (['easy', 'medium', 'hard'] as const).flatMap((l) => data.levels[l].rounds.map((r) => ({ l, r })));

  it('has the three levels with at least 6 rounds', () => {
    for (const l of ['easy', 'medium', 'hard'] as const) expect(data.levels[l].rounds.length).toBeGreaterThanOrEqual(6);
  });

  it('every round can be solved within its own limits', () => {
    for (const { l, r } of rounds) {
      const kinds = { pc: r.given.filter((g) => g.kind === 'pc').length, server: r.given.filter((g) => g.kind === 'server').length, switch: r.given.filter((g) => g.kind === 'switch').length };
      const tools = r.tools as Record<string, number | undefined>;
      for (const k of ['pc', 'server', 'switch'] as const) {
        const need = (r.needs as Record<string, number> | undefined)?.[k] ?? 0;
        expect(kinds[k] + (tools[k] ?? 0), `${l}: ${r.text} (${k})`).toBeGreaterThanOrEqual(need);
      }
      const endDevices = Math.max(kinds.pc + kinds.server, (r.needs as Record<string, number> | undefined) ? ((r.needs as Record<string, number>).pc ?? 0) + ((r.needs as Record<string, number>).server ?? 0) : 0, kinds.pc + kinds.server + (tools.pc ?? 0) * 0);
      // one switch holds 8 devices; s linked switches hold 8s - 2(s-1)
      const needSwitches = r.pairs.length === 1 && endDevices <= 2 && kinds.switch === 0 && !(tools.switch) ? 0 : Math.ceil((endDevices - 2) / 6) || 1;
      const allowed = r.maxSwitches ?? kinds.switch + (tools.switch ?? 0);
      if (needSwitches > 0 && endDevices > 2) expect(allowed, `${l}: ${r.text}`).toBeGreaterThanOrEqual(Math.min(needSwitches, 2));
    }
  });

  it('round text and explanations are present', () => {
    for (const { r } of rounds) {
      expect(r.text.length).toBeGreaterThan(10);
      expect(r.why.length).toBeGreaterThan(10);
    }
  });
});
