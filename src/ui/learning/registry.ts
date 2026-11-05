import type { GameDef } from './gameShell';
import { journeyGame, sorterGame, topologyGame, hotspotGame, type HotspotData, type JourneyData, type SorterData } from './lessonGames';
import { LESSON_PRIZES } from './prizesByLesson';
import type { TopologyData } from './topologyLogic';
import { simGame } from './simGame';
import type { SimData } from './simLogic';
import type { LessonData, MinigameData, Prize, QuizData } from './types';
import { wiringGame } from './wiring';
import type { WiringData } from './wiringLogic';

type Mod = Record<string, { default: unknown }>;
const lessons = import.meta.glob('../../../content/he/lesson0*.json', { eager: true }) as Mod;
const quizzes = import.meta.glob('../../../content/he/quiz0*.json', { eager: true }) as Mod;
const minigames = import.meta.glob('../../../content/he/minigame0*.json', { eager: true }) as Mod;
const wirings = import.meta.glob('../../../content/he/wiring0*.json', { eager: true }) as Mod;
const sorters = import.meta.glob('../../../content/he/sorter0*.json', { eager: true }) as Mod;
const topologies = import.meta.glob('../../../content/he/topology0*.json', { eager: true }) as Mod;
const hotspots = import.meta.glob('../../../content/he/hotspot0*.json', { eager: true }) as Mod;
const journeys = import.meta.glob('../../../content/he/journey0*.json', { eager: true }) as Mod;
const sims = import.meta.glob('../../../content/he/sim0*.json', { eager: true }) as Mod;

/** "../../../content/he/lesson02.json" -> "02" */
function numberOf(path: string): string {
  return /(\d\d)\.json$/.exec(path)?.[1] ?? '';
}
function byNumber(mod: Mod): Map<string, unknown> {
  return new Map(Object.entries(mod).map(([p, m]) => [numberOf(p), m.default]));
}
const L = byNumber(lessons);
const Q = byNumber(quizzes);
const M = byNumber(minigames);
const W = byNumber(wirings);
const S = byNumber(sorters);
const T = byNumber(topologies);
const H = byNumber(hotspots);
const SIM = byNumber(sims);
const J = byNumber(journeys);

export interface LessonBundle {
  /** "lesson02". */
  id: string;
  lesson: LessonData;
  quiz: QuizData;
  minigame: MinigameData;
  game: GameDef;
  gameKind: 'wiring' | 'sorter' | 'topology' | 'hotspot' | 'sim' | 'journey';
}

/** Lessons that have everything: the lesson, its summary questions and a mini-game. Sorted. */
export function lessonIds(): string[] {
  return [...L.keys()].filter((n) => Q.has(n) && (W.has(n) || S.has(n) || T.has(n) || H.has(n) || SIM.has(n) || J.has(n))).sort().map((n) => `lesson${n}`);
}

function prizesFor(id: string, fallback?: MinigameData['prizes']): MinigameData['prizes'] {
  if (fallback) return fallback;
  const table = LESSON_PRIZES[id];
  const p = (l: 'easy' | 'medium' | 'hard'): Prize => {
    const x = table?.[l];
    return { name: x?.name ?? '', type: l === 'easy' ? 'progress' : l === 'medium' ? 'capped_upgrade' : 'prestige', description: x?.description ?? '', effect: x?.effect ?? '' };
  };
  return {
    principles: ['הפרסים קבועים ולא מגרילים', 'כל רמה נותנת משהו אחר שמקדם אתכם', 'מותר לנסות שוב בחינם, בכל רמה'],
    easy: p('easy'), medium: p('medium'), hard: p('hard'),
  };
}

export function loadBundle(id: string): LessonBundle | null {
  const n = id.replace(/^lesson/, '');
  const lesson = L.get(n) as LessonData | undefined;
  const quiz = Q.get(n) as QuizData | undefined;
  if (!lesson || !quiz) return null;
  const given = M.get(n) as MinigameData | undefined;
  let game: GameDef;
  let kind: LessonBundle['gameKind'];
  let title: string;
  let intro: string;
  if (W.has(n)) { kind = 'wiring'; const d = W.get(n) as WiringData; title = d.title; intro = d.intro; game = wiringGameFor(d, given, n); }
  else if (J.has(n)) { kind = 'journey'; const d = J.get(n) as JourneyData; title = d.title; intro = d.intro; game = journeyGame(d); }
  else if (S.has(n)) { kind = 'sorter'; const d = S.get(n) as SorterData; title = d.title; intro = d.intro; game = sorterGame(d); }
  else if (T.has(n)) { kind = 'topology'; const d = T.get(n) as TopologyData; title = d.title; intro = d.intro; game = topologyGame(d); }
  else if (SIM.has(n)) { kind = 'sim'; const d = SIM.get(n) as SimData; title = d.title; intro = d.intro; game = simGame(d); }
  else if (H.has(n)) { kind = 'hotspot'; const d = H.get(n) as HotspotData; title = d.title; intro = d.intro; game = hotspotGame(d); }
  else return null;
  const levelOf = (l: 'easy' | 'medium' | 'hard'): MinigameData['levels']['easy'] => ({
    lives: game.levels[l].lives, timeLimitPerTaskSec: game.levels[l].timeLimit, tasksCount: game.levels[l].count, passRule: '', tasks: [],
  });
  const minigame: MinigameData = given
    ? { ...given, prizes: prizesFor(id, given.prizes) }
    : {
      id: `minigame${n}`, title, story: intro, source: '', rules: [], needsTeacher: [],
      levels: { easy: levelOf('easy'), medium: levelOf('medium'), hard: levelOf('hard') },
      prizes: prizesFor(id),
    } as unknown as MinigameData;
  return { id, lesson, quiz, minigame, game, gameKind: kind };
}

function wiringGameFor(d: WiringData, given: MinigameData | undefined, n: string): GameDef {
  const data = given ?? ({ id: `minigame${n}`, levels: { easy: { lives: 5, timeLimitPerTaskSec: null }, medium: { lives: 3, timeLimitPerTaskSec: 60 }, hard: { lives: 3, timeLimitPerTaskSec: 70 } } } as unknown as MinigameData);
  return wiringGame(d, data);
}
