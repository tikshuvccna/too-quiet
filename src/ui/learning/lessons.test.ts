import { describe, expect, it } from 'vitest';
import { lessonIds, loadBundle } from './registry';
import { cutOff } from './topologyLogic';
import type { SorterData, HotspotData } from './lessonGames';
import type { TopologyData } from './topologyLogic';
import type { JourneyData } from './lessonGames';

const WIDGETS = new Set(['connect_threads', 'tap_to_classify', 'network_size_chooser', 'advantage_matcher', 'client_server_toy', 'atm_toy', 'p2p_vs_cs_toy', 'need_sorter']);
const ids = lessonIds();

function allText(v: unknown, out: string[] = []): string[] {
  if (typeof v === 'string') out.push(v);
  else if (Array.isArray(v)) v.forEach((x) => allText(x, out));
  else if (v && typeof v === 'object') Object.entries(v).forEach(([k, x]) => { if (!k.startsWith('needsTeacher') && k !== 'note' && k !== 'notes' && k !== 'source') allText(x, out); });
  return out;
}

describe('lessons found', () => {
  it('has lessons 01 to 05 in order', () => {
    expect(ids).toEqual(['lesson01', 'lesson02', 'lesson03', 'lesson04', 'lesson05']);
  });
});

describe.each(ids)('%s content', (id) => {
  const b = loadBundle(id);
  it('loads with a lesson, quiz, game and three prizes', () => {
    expect(b).not.toBeNull();
    if (!b) return;
    expect(b.lesson.steps.length).toBeGreaterThanOrEqual(5);
    expect(b.quiz.questions.length).toBe(8);
    for (const l of ['easy', 'medium', 'hard'] as const) {
      expect(b.minigame.prizes[l].name.length, `${id} ${l} prize`).toBeGreaterThan(0);
      expect(b.game.levels[l].count, `${id} ${l} count`).toBeGreaterThanOrEqual(8);
    }
  });

  it('lesson steps are well formed', () => {
    const b2 = loadBundle(id);
    if (!b2) return;
    for (const s of b2.lesson.steps) {
      expect(WIDGETS.has(s.widget.type), `${s.id} ${s.widget.type}`).toBe(true);
      expect(s.check.options.length).toBeGreaterThanOrEqual(2);
      expect(s.check.correct).toBeGreaterThanOrEqual(0);
      expect(s.check.correct).toBeLessThan(s.check.options.length);
    }
    expect(new Set(b2.lesson.steps.map((s) => s.id)).size).toBe(b2.lesson.steps.length);
  });

  it('quiz questions have a valid answer and an explanation', () => {
    const b2 = loadBundle(id);
    if (!b2) return;
    for (const q of b2.quiz.questions) {
      expect(q.explain.length, q.id).toBeGreaterThan(5);
      if (q.type === 'order') expect([...q.correct].sort()).toEqual(q.options.map((_, i) => i).sort());
      else {
        expect(q.correct).toBeGreaterThanOrEqual(0);
        expect(q.correct).toBeLessThan(q.options.length);
      }
    }
  });

  it('never cites the book in text shown to the player', () => {
    const b2 = loadBundle(id);
    if (!b2) return;
    const text = allText([b2.lesson, b2.quiz]).join('\n');
    expect(text).not.toMatch(/כתוב בספר|בספר:|הספר אומר|לפי הספר|עמ' \d/);
  });
});

describe('game data integrity', () => {
  it('sorter items point at real bins, with short labels', async () => {
    const mods = import.meta.glob('../../../content/he/sorter0*.json', { eager: true }) as Record<string, { default: SorterData }>;
    for (const m of Object.values(mods)) {
      const d = m.default;
      const bins = new Set(d.bins.map((x) => x.id));
      for (const l of ['easy', 'medium', 'hard'] as const) for (const it of d.levels[l].items) {
        expect(bins.has(it.bin), `${d.id} ${it.label}`).toBe(true);
        expect(it.label.split(/\s+/).length, it.label).toBeLessThanOrEqual(4);
      }
    }
  });

  it('topology rounds are consistent and solvable', () => {
    const mods = import.meta.glob('../../../content/he/topology0*.json', { eager: true }) as Record<string, { default: TopologyData }>;
    for (const m of Object.values(mods)) for (const l of ['easy', 'medium', 'hard'] as const) for (const r of m.default.levels[l].rounds) {
      const nodeIds = new Set(r.nodes.map((n) => n.id));
      expect(nodeIds.has(r.target), r.text).toBe(true);
      for (const [a, c] of r.links) { expect(nodeIds.has(a) && nodeIds.has(c), r.text).toBe(true); }
      if (r.failure.type === 'node') expect(nodeIds.has(r.failure.id), r.text).toBe(true);
      expect(Array.isArray(cutOff(r))).toBe(true);
    }
  });

  it('journey paths alternate end, media, middle, media, end and use known labels', () => {
    const mods = import.meta.glob('../../../content/he/journey0*.json', { eager: true }) as Record<string, { default: JourneyData }>;
    for (const m of Object.values(mods)) for (const l of ['easy', 'medium', 'hard'] as const) for (const r of m.default.levels[l].rounds) {
      const roles = m.default.roles;
      expect(r.path.length % 2, r.text).toBe(1);
      expect(roles[r.path[0] as string], r.text).toBe('end');
      expect(roles[r.path[r.path.length - 1] as string], r.text).toBe('end');
      r.path.slice(1, -1).forEach((lab, i) => expect(roles[lab], `${r.text}: ${lab}`).toBe(i % 2 === 0 ? 'media' : 'mid'));
    }
  });

  it('hotspot answers are real regions', () => {
    const mods = import.meta.glob('../../../content/he/hotspot0*.json', { eager: true }) as Record<string, { default: HotspotData }>;
    for (const m of Object.values(mods)) for (const l of ['easy', 'medium', 'hard'] as const) for (const r of m.default.levels[l].rounds) {
      expect(r.regions.some((x) => x.id === r.answer), r.text).toBe(true);
      for (const x of r.regions) { expect(x.x + x.w).toBeLessThanOrEqual(1.001); expect(x.y + x.h).toBeLessThanOrEqual(1.001); }
    }
  });
});
