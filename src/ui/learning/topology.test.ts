import { describe, expect, it } from 'vitest';
import { type TopologyRound, cutOff } from './topologyLogic';

const dev = (id: string, x: number, y: number) => ({ id, label: id, x, y, kind: 'device' as const });
const jn = (id: string, x: number, y: number) => ({ id, label: '', x, y, kind: 'link' as const });

describe('topology failures', () => {
  it('star: a dead central switch cuts every device off, a dead device cuts only itself (not asked about)', () => {
    const base = {
      text: '', why: '', target: 'a',
      nodes: [dev('a', 0, 0), dev('b', 0, 0), dev('c', 0, 0), jn('sw', 0, 0)],
      links: [['a', 'sw'], ['b', 'sw'], ['c', 'sw']] as Array<[string, string]>,
    };
    const dead: TopologyRound = { ...base, failure: { type: 'node', id: 'sw' } };
    expect(cutOff(dead).sort()).toEqual(['b', 'c']);
    const oneDevice: TopologyRound = { ...base, failure: { type: 'node', id: 'c' } };
    expect(cutOff(oneDevice)).toEqual([]);
    const cable: TopologyRound = { ...base, failure: { type: 'link', a: 'b', b: 'sw' } };
    expect(cutOff(cable)).toEqual(['b']);
  });

  it('bus: cutting the shared line splits the devices on the far side', () => {
    const r: TopologyRound = {
      text: '', why: '', target: 'a',
      nodes: [dev('a', 0, 0), dev('b', 0, 0), dev('c', 0, 0), dev('d', 0, 0), jn('j1', 0, 0), jn('j2', 0, 0), jn('j3', 0, 0), jn('j4', 0, 0)],
      links: [['j1', 'j2'], ['j2', 'j3'], ['j3', 'j4'], ['a', 'j1'], ['b', 'j2'], ['c', 'j3'], ['d', 'j4']],
      failure: { type: 'link', a: 'j2', b: 'j3' },
    };
    expect(cutOff(r).sort()).toEqual(['c', 'd']);
  });

  it('ring and mesh: one cut leaves everyone connected through the other way round', () => {
    const ring: TopologyRound = {
      text: '', why: '', target: 'a',
      nodes: ['a', 'b', 'c', 'd'].map((id) => dev(id, 0, 0)),
      links: [['a', 'b'], ['b', 'c'], ['c', 'd'], ['d', 'a']],
      failure: { type: 'link', a: 'b', b: 'c' },
    };
    expect(cutOff(ring)).toEqual([]);
  });
});
