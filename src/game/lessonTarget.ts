import { PROBLEMS, stageOf, type Probe } from './problems';

/** Where the player has to go for the next lesson: the target id the world uses (an NPC or the tower door), who teaches and where. */
export interface LessonTarget {
  lessonId: string;
  targetId: string;
  teacher: string;
  place: string;
}

/** The next lesson the player can take now, or null when every open lesson is done or none is open yet. */
export function nextLessonTarget(probe: Probe): LessonTarget | null {
  if (!probe.lessonDone('lesson01')) return { lessonId: 'lesson01', targetId: 'door:tower', teacher: 'דבורה', place: 'מגדל האורגים' };
  for (const p of PROBLEMS) {
    if (probe.lessonDone(p.lesson)) continue;
    const st = stageOf(p, probe);
    if (st === 'chaos' || st === 'learn') return { lessonId: p.lesson, targetId: `npc:${p.npc}`, teacher: p.teacher, place: p.site };
  }
  return null;
}
