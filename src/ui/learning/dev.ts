// Dev harness for the learning screens: ?screen=lesson&step=3 | quiz | game&level=hard | menu
import '../../styles.css';
import { SaveStore } from '../../core/save';
import { loadLessonContent, openLesson, openMinigame, openMinigameMenu, openQuiz } from './index';

const q = new URLSearchParams(location.search);
const save = new SaveStore(null);
const content = loadLessonContent();
const out = (v: unknown): void => { (window as unknown as { __out: unknown[] }).__out.push(v); };
(window as unknown as { __out: unknown[]; __save: SaveStore }).__out = [];
(window as unknown as { __save: SaveStore }).__save = save;

const screen = q.get('screen') ?? 'lesson';
if (screen === 'lesson') {
  const step = Number(q.get('step') ?? 0);
  content.lesson.steps.slice(0, step).forEach((s) => { save.lesson('lesson01').checks[s.id] = true; });
  openLesson(content.lesson, save, { onClose: (d) => out({ lessonDone: d }) });
} else if (screen === 'quiz') {
  openQuiz(content.quiz, save, { onClose: (r) => out(r) });
} else if (screen === 'game') {
  openMinigame(content.minigame, (q.get('level') ?? 'easy') as 'easy', save, { onClose: (r) => out(r) });
} else {
  openMinigameMenu(content.minigame, save, { onClose: () => out('menu closed') });
}
