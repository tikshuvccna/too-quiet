/**
 * The story layer of lessons 02-05, like problem 1 for lesson 01: a problem waits at one place in the world,
 * the apprentice cannot mend it yet, learns the lesson from the problem's NPC (lesson 1 is Dvora's), comes back and mends it.
 */
export interface Problem {
  n: number;
  lesson: string;
  /** World NPC (id in npcs_world.json) who shows the problem. */
  npc: string;
  chaos: string;
  fix: string;
  seen: string;
  complete: string;
  /** The previous problem must be complete first (problem 2 waits for the end of problem 1). */
  after: string;
  site: string;
  who: string;
  /** The teacher of the lesson: the problem's NPC, with the name shown in the lesson menu. */
  teacher: string;
}

export const PROBLEMS: Problem[] = [
  { n: 2, lesson: 'lesson02', npc: 'npc_innkeeper', chaos: 'p2_chaos', fix: 'p2_fix', seen: 'p2_seen', complete: 'p2_complete', after: 'p1_complete', site: 'אכסניית הפנס', who: 'בעלת האכסניה', teacher: 'גברת תמר' },
  { n: 3, lesson: 'lesson03', npc: 'npc_mender', chaos: 'p3_chaos', fix: 'p3_fix', seen: 'p3_seen', complete: 'p3_complete', after: 'p2_complete', site: 'בית המלאכה בעמק הטחנה', who: 'המתקן', teacher: 'גברת אסתר' },
  { n: 4, lesson: 'lesson04', npc: 'npc_dockHand', chaos: 'p4_chaos', fix: 'p4_fix', seen: 'p4_seen', complete: 'p4_complete', after: 'p3_complete', site: 'הנמל בחוף', who: 'איש הנמל', teacher: 'מר צבי' },
  { n: 5, lesson: 'lesson05', npc: 'npc_guildMaster', chaos: 'p5_chaos', fix: 'p5_fix', seen: 'p5_seen', complete: 'p5_complete', after: 'p4_complete', site: 'אולם הגילדה', who: 'ראש הגילדה', teacher: 'מר מנחם' },
];

export const PROBLEM_COINS = 30;

export type Stage = 'locked' | 'chaos' | 'learn' | 'fix' | 'done';

export interface Probe {
  has(flag: string): boolean;
  lessonDone(lessonId: string): boolean;
  hasScene(id: string): boolean;
}

/** Where the player is in a problem. A problem without its scenes written yet stays locked. */
export function stageOf(p: Problem, probe: Probe): Stage {
  if (!probe.hasScene(p.chaos) || !probe.hasScene(p.fix)) return 'locked';
  if (probe.has(p.complete)) return 'done';
  if (!probe.has(p.after)) return 'locked';
  if (!probe.has(p.seen)) return 'chaos';
  return probe.lessonDone(p.lesson) ? 'fix' : 'learn';
}

export function problemForNpc(npc: string): Problem | undefined {
  return PROBLEMS.find((p) => p.npc === npc);
}

/** The next problem that is open, with what the player should do about it. */
export function objectiveFor(probe: Probe): string | null {
  for (const p of PROBLEMS) {
    const st = stageOf(p, probe);
    if (st === 'done' || st === 'locked') continue;
    if (st === 'chaos') return `בעיה חדשה: ${p.site}. דברו עם ${p.who}.`;
    if (st === 'learn') return `שיעור ${p.n} אצל ${p.teacher}: ${p.site}.`;
    return `עכשיו אפשר לתקן: חזרו אל ${p.who} ב${p.site}.`;
  }
  return null;
}
