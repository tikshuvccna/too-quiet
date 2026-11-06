import { describe, expect, it } from 'vitest';
import { nextLessonTarget } from './lessonTarget';

const probe = (flags: string[], lessons: string[]) => ({
  has: (f: string) => flags.includes(f),
  lessonDone: (id: string) => lessons.includes(id),
  hasScene: () => true,
});

describe('next lesson target', () => {
  it('starts with Dvora in the tower', () => {
    expect(nextLessonTarget(probe([], []))?.targetId).toBe('door:tower');
  });
  it('waits for problem 1 before the second lesson opens', () => {
    expect(nextLessonTarget(probe([], ['lesson01']))).toBeNull();
  });
  it('sends the player to the teacher of the next open problem', () => {
    const t = nextLessonTarget(probe(['p1_complete'], ['lesson01']));
    expect(t?.lessonId).toBe('lesson02');
    expect(t?.targetId).toBe('npc:npc_innkeeper');
    const t3 = nextLessonTarget(probe(['p1_complete', 'p2_complete'], ['lesson01', 'lesson02']));
    expect(t3?.lessonId).toBe('lesson03');
  });
  it('has nothing left when all lessons are done', () => {
    expect(nextLessonTarget(probe(['p1_complete', 'p2_complete', 'p3_complete', 'p4_complete', 'p5_complete'], ['lesson01', 'lesson02', 'lesson03', 'lesson04', 'lesson05']))).toBeNull();
  });
});
