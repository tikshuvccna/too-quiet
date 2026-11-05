import type { Level } from './types';

export interface LessonPrize { name: string; description: string; effect: string; flags: string[]; coins: number }

/**
 * What each lesson's mini-game gives. Three tiers: easy is guaranteed progress, medium a capped upgrade,
 * hard prestige (a glowing cloak). Everything is fixed and permanent, and every effect is applied in `game/perks.ts`
 * or the shop (cloaks are auras). Lesson 01 keeps its own table in minigame01.json and prizes.ts.
 */
export const LESSON_PRIZES: Record<string, Record<Level, LessonPrize>> = {
  lesson02: {
    easy: { name: 'כיס המטבעות', description: 'כיס קטן שמחזיק יותר: כל מטבע שתמצאו שווה קצת יותר.', effect: 'קבוע: 25 אחוז יותר מטבעות ממשחקוני צד וחיפוש בעצים.', flags: ['prize.lesson02.easy', 'perk.coin_pouch'], coins: 10 },
    medium: { name: 'צעדי שליח', description: 'שליחים לומדים לקצר דרכים, וגם אתם.', effect: 'קבוע: מהירות הליכה גדולה ב-8 אחוז.', flags: ['prize.lesson02.medium', 'perk.sure_feet'], coins: 20 },
    hard: { name: 'גלימת התכלת', description: 'גלימה בצבע הים, למי שמכיר כל רכיב ברשת.', effect: 'הילה כחולה קבועה סביב הדמות, ותג "מכיר רכיבים".', flags: ['prize.lesson02.hard', 'cosmetic.cloak_blue', 'equip.aura_blue', 'badge.component_expert'], coins: 40 },
  },
  lesson03: {
    easy: { name: 'עיני החוטים', description: 'מי שמבין צורות של רשת רואה ניצוצות מרחוק.', effect: 'קבוע: הניצוצות בעצים נראים ממרחק גדול ב-50 אחוז.', flags: ['prize.lesson03.easy', 'perk.keen_eyes'], coins: 10 },
    medium: { name: 'נשימה ארוכה', description: 'סבלנות של מי שבנה רשת עמידה.', effect: 'קבוע: עוד 45 שניות בין קפיצה למגדל.', flags: ['prize.lesson03.medium', 'perk.long_breath_03'], coins: 20 },
    hard: { name: 'גלימת הסגול', description: 'גלימה למי שיודע איפה רשת נשברת ואיך לא להישבר.', effect: 'הילה סגולה קבועה סביב הדמות, ותג "בונה רשתות עמידות".', flags: ['prize.lesson03.hard', 'cosmetic.cloak_violet', 'equip.aura_violet', 'badge.resilient_builder'], coins: 40 },
  },
  lesson04: {
    easy: { name: 'ידיים ארוכות', description: 'אפשר להושיט יד רחוק יותר, כמו חוט שמגיע לעיר אחרת.', effect: 'קבוע: טווח הגישה גדל ב-20 אחוז.', flags: ['prize.lesson04.easy', 'perk.long_arms'], coins: 10 },
    medium: { name: 'חוש החוטים', description: 'המחט מרגישה תקלות בעולם רחב יותר.', effect: 'קבוע: טווח הזיהוי של המחט גדל.', flags: ['prize.lesson04.medium', 'perk.thread_sense'], coins: 20 },
    hard: { name: 'גלימת הוורד', description: 'גלימה למי שמחבר בין רשת קטנה לעולם הגדול.', effect: 'הילה ורדרדה קבועה סביב הדמות, ותג "מחבר עולמות".', flags: ['prize.lesson04.hard', 'cosmetic.cloak_rose', 'equip.aura_rose2', 'badge.world_connector'], coins: 40 },
  },
  lesson05: {
    easy: { name: 'צעדים קלים', description: 'מי שמתכנן לפני שהוא בונה, חוסך צעדים.', effect: 'קבוע: מהירות הליכה גדולה ב-8 אחוז.', flags: ['prize.lesson05.easy', 'perk.light_steps'], coins: 10 },
    medium: { name: 'נשימת המתכנן', description: 'שולחן התכנון נותן עוד קצת זמן.', effect: 'קבוע: עוד 45 שניות בין קפיצה למגדל.', flags: ['prize.lesson05.medium', 'perk.long_breath_05'], coins: 20 },
    hard: { name: 'גלימת הלבן', description: 'גלימה נקייה של מי שמכיר את שולחן התכנון.', effect: 'הילה לבנה קבועה סביב הדמות, ותג "מתכנן הרשת".', flags: ['prize.lesson05.hard', 'cosmetic.cloak_white', 'equip.aura_white', 'badge.network_planner'], coins: 40 },
  },
};
