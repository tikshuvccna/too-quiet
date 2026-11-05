import { lessonIds, loadBundle, openLesson, openMinigameMenu, openQuiz, type LessonBundle } from '../ui/learning';
import { el, uiRoot } from '../ui/dom';
import { playCutscene } from '../ui/cutscene';
import type { GameContext } from './context';

const QUIZ_COINS = 15;

/**
 * Dvora's classroom: pick a lesson (they open one after the other), then the lesson itself,
 * the summary questions, and at the end the three-level mini-game.
 * `afterLesson` runs once, right after a lesson is finished (the story beat in the tower).
 */
export function openClassroom(ctx: GameContext, afterLesson: (lessonId: string) => Promise<void>): Promise<void> {
  const ids = lessonIds();
  const isDone = (id: string): boolean => ctx.save.lesson(id).done;
  // the lesson to show first: the first one that is not finished yet, or the last one
  let current = ids.find((id) => !isDone(id)) ?? (ids[ids.length - 1] as string);
  const unlocked = (id: string): boolean => {
    const i = ids.indexOf(id);
    return i <= 0 || isDone(ids[i - 1] as string);
  };
  return new Promise((resolve) => {
    let screen: HTMLElement | null = null;

    const closeScreen = (): void => {
      screen?.remove();
      screen = null;
    };

    const render = (): void => {
      closeScreen();
      const content = loadBundle(current) as LessonBundle;
      const lessonId = content.id;
      const l = ctx.save.lesson(lessonId);
      const best = Object.values(l.games).reduce((n, g) => Math.max(n, g.points), 0);
      const passed = Object.values(l.games).filter((g) => g.passed).length;

      const lessonBtn = el('button', 'btn primary', l.done ? 'לחזור על השיעור' : 'להתחיל את השיעור');
      const quizBtn = el('button', 'btn', 'שאלות סיכום');
      const gameBtn = el('button', 'btn', l.quizPassed ? 'המשחקון (שלוש רמות)' : 'המשחקון (אחרי שאלות הסיכום)');
      const back = el('button', 'btn', 'חזרה לעולם');
      quizBtn.disabled = !l.done;
      gameBtn.disabled = !l.done || !l.quizPassed;

      lessonBtn.addEventListener('click', () => {
        closeScreen();
        const no = lessonId.replace(/^lesson/, '');
        void playCutscene(`lesson_start_${no}`).then(() => {
          openLesson(content.lesson, ctx.save, {
            onClose: (done) => {
              if (!done) return render();
              void playCutscene(`lesson_end_${no}`).then(() => afterLesson(lessonId)).then(render);
            },
          });
        });
      });
      quizBtn.addEventListener('click', () => {
        closeScreen();
        openQuiz(content.quiz, ctx.save, {
          lessonId,
          onClose: (r) => {
            const marker = `prize.quiz.${lessonId}`;
            if (r.passed && !ctx.save.hasFlag(marker) && !(lessonId === 'lesson01' && ctx.save.hasFlag('prize.quiz'))) {
              ctx.save.data.coins += QUIZ_COINS;
              ctx.save.setFlag(marker);
              ctx.hud.toast(`עברתם את שאלות הסיכום! +${QUIZ_COINS} מטבעות`, 'good');
            }
            render();
          },
        });
      });
      gameBtn.addEventListener('click', () => {
        closeScreen();
        openMinigameMenu(content.minigame, ctx.save, { onClose: render }, content.game);
      });
      back.addEventListener('click', () => {
        closeScreen();
        resolve();
      });

      // the lessons, in order: each opens when the one before it is finished
      const chips = ids.length > 1
        ? el('div', 'row', '', ids.map((id, i) => {
          const b = el('button', `btn${id === current ? ' on' : ''}`, `שיעור ${i + 1}${isDone(id) ? ' ✓' : ''}`);
          b.disabled = !unlocked(id);
          b.addEventListener('click', () => { current = id; render(); });
          return b;
        }))
        : null;

      screen = el('div', 'screen', '', [
        el('div', 'card', '', [
          el('h2', '', 'הכיתה של דבורה'),
          chips,
          el('p', '', content.lesson.title),
          el('p', 'class-status', l.done
            ? `השיעור הושלם. שאלות סיכום: ${l.quizPassed ? 'עברתם, והמשחקון פתוח' : 'עוד לא עברתם (צריך לעבור כדי לפתוח את המשחקון)'}. משחקון: ${passed} מתוך 3 רמות, שיא ${best} נקודות.`
            : 'קודם לומדים, ואחר כך המחט מבינה את מה שהיא רואה. אחרי השיעור באות שאלות סיכום, ובסופן המשחקון.'),
          el('div', 'row', '', [lessonBtn, quizBtn, gameBtn, back]),
        ]),
      ]);
      uiRoot().append(screen);
    };

    render();
  });
}
