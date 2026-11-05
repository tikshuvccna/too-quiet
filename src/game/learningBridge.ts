import { loadLessonContent, openLesson, openMinigameMenu, openQuiz } from '../ui/learning';
import { el, uiRoot } from '../ui/dom';
import type { GameContext } from './context';

const QUIZ_COINS = 15;

/**
 * Dvora's classroom: the lesson first, then the quiz and the three-level mini-game.
 * `afterLesson` runs once, right after the lesson is finished (the story beat in the tower).
 */
export function openClassroom(ctx: GameContext, afterLesson: () => Promise<void>): Promise<void> {
  const content = loadLessonContent();
  const lessonId = 'lesson01';
  return new Promise((resolve) => {
    let screen: HTMLElement | null = null;

    const closeScreen = (): void => {
      screen?.remove();
      screen = null;
    };

    const render = (): void => {
      closeScreen();
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
        openLesson(content.lesson, ctx.save, {
          onClose: (done) => {
            if (!done) return render();
            void afterLesson().then(render);
          },
        });
      });
      quizBtn.addEventListener('click', () => {
        closeScreen();
        openQuiz(content.quiz, ctx.save, {
          lessonId,
          onClose: (r) => {
            if (r.passed && !ctx.save.hasFlag('prize.quiz')) {
              ctx.save.data.coins += QUIZ_COINS;
              ctx.save.setFlag('prize.quiz');
              ctx.hud.toast(`עברתם את שאלות הסיכום! +${QUIZ_COINS} מטבעות`, 'good');
            }
            render();
          },
        });
      });
      gameBtn.addEventListener('click', () => {
        closeScreen();
        openMinigameMenu(content.minigame, ctx.save, { onClose: render });
      });
      back.addEventListener('click', () => {
        closeScreen();
        resolve();
      });

      screen = el('div', 'screen', '', [
        el('div', 'card', '', [
          el('h2', '', 'הכיתה של דבורה'),
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
