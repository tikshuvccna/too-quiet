import './learning.css';
import lesson01 from '../../../content/he/lesson01.json';
import quiz01 from '../../../content/he/quiz01.json';
import minigame01 from '../../../content/he/minigame01.json';
import type { LessonContent, LessonData, MinigameData, QuizData } from './types';

export { openLesson } from './lesson';
export { openQuiz } from './quiz';
export { openMinigame, openMinigameMenu } from './minigame';
export { applyPrize, prizeFor } from './prizes';
export { mountWidget } from './widgets';
export type {
  LessonContent, LessonData, MinigameData, MinigameResult, QuizData, QuizResult, Level,
} from './types';

/** The Hebrew content of lesson 01, typed. The JSON files are the source of truth for the facts. */
export function loadLessonContent(): LessonContent {
  return {
    lesson: lesson01 as unknown as LessonData,
    quiz: quiz01 as unknown as QuizData,
    minigame: minigame01 as unknown as MinigameData,
  };
}
