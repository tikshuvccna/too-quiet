// Dev harness for the learning screens: ?screen=lesson&step=3 | quiz | game&level=hard | menu
import '../../styles.css';
import { SaveStore } from '../../core/save';
import { NPC_GAMES, openNpcGame } from '../npcgames';
import { openShop } from '../shop';
import { hotspotGame, sorterGame, topologyGame } from './lessonGames';
import { loadLessonContent, openLesson, openMinigame, openMinigameMenu, openQuiz, openGameShell, loadBundle } from './index';

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
  const b = loadBundle(`lesson${q.get('n') ?? '01'}`);
  if (b) openGameShell(b.game, b.minigame, lvl, save, { onClose: (r: unknown) => out(r) });
  else openMinigame(content.minigame, lvl, save, { onClose: (r) => out(r) });
} else if (screen === 'sample') {
  // visual check of the three generic games with throw-away data
  const b = loadBundle('lesson01');
  const lv = { lives: 3, timeLimitPerTaskSec: 8 };
  const kind = q.get('kind') ?? 'sorter';
  const sorter = { id: 's', title: 'דוגמה: מיון', intro: 'בדיקה', bins: [{ id: 'a', label: 'התקן קצה' }, { id: 'b', label: 'התקן ביניים' }, { id: 'c', label: 'מדיה' }],
    levels: { easy: { ...lv, items: [{ label: 'טלפון', bin: 'a', why: 'טלפון הוא התקן קצה.' }, { label: 'מתג', bin: 'b', why: 'מתג מחבר.' }] }, medium: { ...lv, items: [] }, hard: { ...lv, items: [] } } };
  const nodes = [
    { id: 'sw', label: 'מתג', x: 0.5, y: 0.5, kind: 'link' as const },
    { id: 'a', label: 'שרת', x: 0.5, y: 0.15, kind: 'device' as const }, { id: 'b', label: 'מחשב', x: 0.15, y: 0.7, kind: 'device' as const }, { id: 'c', label: 'מדפסת', x: 0.85, y: 0.7, kind: 'device' as const },
  ];
  const topo = { id: 't', title: 'דוגמה: טופולוגיה', intro: 'בדיקה', levels: { easy: { ...lv, rounds: [{ text: 'המתג נפל. מי מאבד קשר עם השרת?', nodes, links: [['a', 'sw'], ['b', 'sw'], ['c', 'sw']] as Array<[string, string]>, failure: { type: 'node' as const, id: 'sw' }, target: 'a', why: 'כל החוטים עוברים במתג.' }] }, medium: { ...lv, rounds: [] }, hard: { ...lv, rounds: [] } } };
  const hot = { id: 'h', title: 'דוגמה: חלון', intro: 'בדיקה', levels: { easy: { ...lv, rounds: [{ text: 'איפה בוחרים התקן להוספה?', layout: 'main', regions: [{ id: 'tool', label: 'ארגז הכלים', x: 0.02, y: 0.12, w: 0.28, h: 0.8 }, { id: 'ws', label: 'אזור העבודה', x: 0.34, y: 0.12, w: 0.62, h: 0.8 }], answer: 'tool', why: 'ההתקנים נמצאים בארגז הכלים.' }] }, medium: { ...lv, rounds: [] }, hard: { ...lv, rounds: [] } } };
  const def = kind === 'topology' ? topologyGame(topo as never) : kind === 'hotspot' ? hotspotGame(hot as never) : sorterGame(sorter as never);
  if (b) openGameShell(def, b.minigame, 'easy', save, { onClose: (r: unknown) => out(r) });
} else if (screen === 'shop') {
  save.data.coins = 100;
  void openShop(save, { onChange: () => out('changed') });
} else if (screen === 'npc') {
  void openNpcGame(NPC_GAMES[q.get('id') ?? 'npc_bellBoy']!, save, q.has('calm'));
} else {
  openMinigameMenu(content.minigame, save, { onClose: () => out('menu closed') });
}
