export type Level = 'easy' | 'medium' | 'hard';
export const LEVELS: readonly Level[] = ['easy', 'medium', 'hard'];

export interface Check {
  q: string;
  options: string[];
  correct: number;
  explain: string;
}

export interface Node2D { id: string; label: string; x: number; y: number }
export interface ConnectSpec { nodes: Node2D[] }
export interface ClassifySpec {
  instruction: string;
  items: { label: string; answer: 'network' | 'none'; why: string }[];
}
export interface SizeSpec {
  categories: { id: string; label: string }[];
  scenarios: { text: string; answer: string; why: string }[];
}
export interface AdvantageSpec {
  advantages: string[];
  pairs: { example: string; advantage: string }[];
}
export interface ClientServerSpec { controls: { id: string; label: string; effect: string }[] }
export interface AtmSpec { modes: { id: string; label: string }[]; buttons: string[] }
export interface P2pSpec { interactions: { id: string; label: string }[] }
export interface NeedSpec {
  choices: string[];
  scenarios: { text: string; answer: string; why: string }[];
}

export type WidgetDef =
  | { type: 'connect_threads'; title: string; spec: ConnectSpec }
  | { type: 'tap_to_classify'; title: string; spec: ClassifySpec }
  | { type: 'network_size_chooser'; title: string; spec: SizeSpec }
  | { type: 'advantage_matcher'; title: string; spec: AdvantageSpec }
  | { type: 'client_server_toy'; title: string; spec: ClientServerSpec }
  | { type: 'atm_toy'; title: string; spec: AtmSpec }
  | { type: 'p2p_vs_cs_toy'; title: string; spec: P2pSpec }
  | { type: 'need_sorter'; title: string; spec: NeedSpec };

export interface LessonStep {
  id: string;
  title: string;
  html: string;
  widget: WidgetDef;
  check: Check;
  recap?: string[];
  video?: { src: string; title: string };
  /** A Short from content/he/shorts.json, shown as a card that plays from YouTube. */
  short?: string;
}
export interface LessonData { id: string; title: string; where?: string; estimatedMinutes?: number; steps: LessonStep[] }

export type Difficulty = 'easy' | 'medium' | 'hard';
interface QuizBase { id: string; difficulty: Difficulty; q: string; options: string[]; explain: string }
export interface ChoiceQuestion extends QuizBase { type: 'mcq' | 'tf'; correct: number }
export interface OrderQuestion extends QuizBase { type: 'order'; correct: number[] }
export type QuizQuestion = ChoiceQuestion | OrderQuestion;
export interface QuizData { id: string; title: string; source?: string; questions: QuizQuestion[] }

export interface MiniTask { scenario: string; options: string[]; correct: number; why: string }
export interface MiniLevel {
  lives: number;
  timeLimitPerTaskSec: number | null;
  tasksCount: number;
  passRule: string;
  tasks: MiniTask[];
}
export interface Prize {
  name: string;
  type: string;
  description: string;
  effect: string;
  cap?: string;
  extra?: string;
}
export interface MinigameData {
  /** When present, the level screen plays the wiring game built from this data instead of the question stage. */
  wiring?: import('./wiringLogic').WiringData;
  id: string;
  title: string;
  story: string;
  rules: string[];
  levels: Record<Level, MiniLevel>;
  prizes: { principles: string[] } & Record<Level, Prize>;
}

export interface MinigameResult { level: Level; points: number; passed: boolean; prizeGranted: boolean }
export interface QuizResult { score: number; max: number; passed: boolean }
export interface LessonContent { lesson: LessonData; quiz: QuizData; minigame: MinigameData }
