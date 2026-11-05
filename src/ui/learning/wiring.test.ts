import { describe, expect, it } from 'vitest';
import wiring01 from '../../../content/he/wiring01.json';
import { SERVER, type Wiring, type WiringData, type WiringRound, evaluate, linkKey, threadsNeeded } from './wiringLogic';

const data = wiring01 as unknown as WiringData;

function solution(r: WiringRound): Wiring {
  const links = new Set<string>();
  const n = r.devices.length;
  if (r.need === 'cs') for (let i = 0; i < n; i++) links.add(linkKey(i, SERVER));
  else for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) links.add(linkKey(i, j));
  return { server: r.need === 'cs', links };
}

describe('wiring game rules', () => {
  const all = (['easy', 'medium', 'hard'] as const).flatMap((l) => data.levels[l].rounds.map((r) => ({ l, r })));

  it('every round has exactly one right answer that the checker accepts', () => {
    for (const { l, r } of all) expect(evaluate(r, solution(r)), `${l}: ${r.text}`).toEqual({ ok: true });
  });

  it('uses the number of threads the lesson implies', () => {
    for (const { r } of all) expect(solution(r).links.size).toBe(threadsNeeded(r));
  });

  it('rejects the other model and half-finished wiring, with a reason', () => {
    for (const { r } of all) {
      const right = solution(r);
      const wrongModel: Wiring = { server: !right.server, links: right.links };
      const v1 = evaluate(r, wrongModel);
      expect(v1.ok, r.text).toBe(false);
      const partial: Wiring = { server: right.server, links: new Set([...right.links].slice(1)) };
      const v2 = evaluate(r, partial);
      if (right.links.size > 1 || r.need === 'cs') expect(v2.ok, r.text).toBe(false);
      if (!v1.ok) expect(v1.message.length).toBeGreaterThan(10);
      expect(evaluate(r, { server: right.server, links: new Set() }).ok).toBe(false);
    }
  });

  it('flags direct client links in a client-server network', () => {
    const r = data.levels.easy.rounds.find((x) => x.need === 'cs' && x.devices.length >= 3) as WiringRound;
    const w = solution(r);
    w.links.add(linkKey(0, 1));
    const v = evaluate(r, w);
    expect(v.ok).toBe(false);
    if (!v.ok) expect(v.code).toBe('extra_links');
  });

  it('keeps every level balanced and short enough', () => {
    for (const l of ['easy', 'medium', 'hard'] as const) {
      const rounds = data.levels[l].rounds;
      expect(rounds.length).toBeGreaterThanOrEqual(8);
      expect(rounds.some((r) => r.need === 'p2p')).toBe(true);
      expect(rounds.some((r) => r.need === 'cs')).toBe(true);
      for (const r of rounds) for (const d of r.devices) expect(d.length).toBeLessThanOrEqual(16);
    }
  });
});
