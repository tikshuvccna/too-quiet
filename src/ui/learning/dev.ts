// Dev harness for the learning screens: ?screen=lesson&step=3 | quiz | game&level=hard | menu
import '../../styles.css';
import { SaveStore } from '../../core/save';
import { NPC_GAMES, openNpcGame } from '../npcgames';
import { openShop } from '../shop';
import { loadLessonContent, openLesson, openMinigame, openMinigameMenu, openQuiz, openGameShell, wiringGame } from './index';

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
  const lvl = (q.get('level') ?? 'easy') as 'easy';
  if (content.minigame.wiring) openGameShell(wiringGame(content.minigame.wiring, content.minigame), content.minigame, lvl, save, { onClose: (r: unknown) => out(r) });
  else openMinigame(content.minigame, lvl, save, { onClose: (r) => out(r) });
} else if (screen === 'shop') {
  save.data.coins = 100;
  void openShop(save, { onChange: () => out('changed') });
} else if (screen === 'npc') {
  void openNpcGame(NPC_GAMES[q.get('id') ?? 'npc_bellBoy']!, save, q.has('calm'));
} else {
  openMinigameMenu(content.minigame, save, { onClose: () => out('menu closed') });
}
