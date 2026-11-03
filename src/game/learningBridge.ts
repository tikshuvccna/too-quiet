import { el, uiRoot } from '../ui/dom';
import type { GameContext } from './context';

/** Temporary classroom until the lesson, quiz and mini-game screens are connected. */
export function openClassroom(ctx: GameContext, after: () => Promise<void>): Promise<void> {
  return new Promise((resolve) => {
    const done = el('button', 'btn primary', 'סימנתי שלמדתי (בדיקה)');
    const back = el('button', 'btn', 'חזרה לעולם');
    const screen = el('div', 'screen', '', [
      el('div', 'card', '', [
        el('h2', '', 'הכיתה של דבורה'),
        el('p', '', 'השיעורים בבנייה.'),
        el('div', 'row', '', [done, back]),
      ]),
    ]);
    const close = (): void => {
      screen.remove();
      void after().then(resolve);
    };
    done.addEventListener('click', () => {
      ctx.save.lesson('lesson01').done = true;
      ctx.save.recomputePower();
      ctx.save.save();
      close();
    });
    back.addEventListener('click', close);
    uiRoot().append(screen);
  });
}
