import './learning.css';
import lesson01 from '../../../content/he/lesson01.json';
import quiz01 from '../../../content/he/quiz01.json';
import type { LessonContent } from './types';
import { loadBundle } from './registry';

export { openLesson } from './lesson';
export { openQuiz } from './quiz';
export { openMinigame, openMinigameMenu } from './minigame';
export { wiringGame } from './wiring';
export { lessonIds, loadBundle } from './registry';
export type { LessonBundle } from './registry';
export { openGameShell } from './gameShell';
export { applyPrize, prizeFor } from './prizes';
export { mountWidget } from './widgets';
export type {
  LessonContent, LessonData, MinigameData, MinigameResult, QuizData, QuizResult, Level,
} from './types';

/** The content of lesson 01 (the lesson the story starts with). Other lessons come from `loadBundle(id)`. */
export function loadLessonContent(): LessonContent {
  const b = loadBundle('lesson01');
  if (!b) throw new Error('lesson01 content is missing');
  return { lesson: b.lesson, quiz: b.quiz, minigame: b.minigame };
}
