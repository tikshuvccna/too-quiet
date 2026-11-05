import { audio } from '../audio/audio';
import { playCutscene } from './cutscene';
import { el, uiRoot } from './dom';

export type CelebrateKind = 'sight' | 'house' | 'creature' | 'diary' | 'card' | 'curio';

interface Info { title: string; text: string; svg: string }

const STROKE = 'stroke="#2b2150" stroke-width="3" stroke-linejoin="round"';
const SVG: Record<CelebrateKind, string> = {
  sight: '<svg viewBox="0 0 64 64"><path d="M6 46 C 20 8, 44 60, 58 18" stroke="#5cf0d0" stroke-width="6" fill="none" stroke-linecap="round"/><circle cx="6" cy="46" r="6" fill="#ffd36b"/><circle cx="58" cy="18" r="6" fill="#ffd36b"/></svg>',
  house: `<svg viewBox="0 0 64 64"><rect x="14" y="30" width="36" height="26" rx="3" fill="#ffb59a" ${STROKE}/><path d="M8 32 L32 10 L56 32 Z" fill="#c85a4a" ${STROKE}/><rect x="27" y="40" width="10" height="16" fill="#ffd36b" ${STROKE}/></svg>`,
  creature: `<svg viewBox="0 0 64 64"><path d="M14 26 L18 8 L28 20 Z M50 26 L46 8 L36 20 Z" fill="#ffd36b" ${STROKE}/><circle cx="32" cy="36" r="20" fill="#ffe8b0" ${STROKE}/><circle cx="25" cy="33" r="3" fill="#2b2150"/><circle cx="39" cy="33" r="3" fill="#2b2150"/><path d="M26 43 Q32 49 38 43" stroke="#2b2150" stroke-width="3" fill="none" stroke-linecap="round"/></svg>`,
  diary: `<svg viewBox="0 0 64 64"><rect x="12" y="8" width="40" height="48" rx="4" fill="#ff9ad0" ${STROKE}/><path d="M20 20 H44 M20 28 H44 M20 36 H36" stroke="#2b2150" stroke-width="3" stroke-linecap="round"/></svg>`,
  card: `<svg viewBox="0 0 64 64"><rect x="14" y="8" width="36" height="48" rx="6" fill="#ffd36b" ${STROKE}/><circle cx="32" cy="32" r="9" fill="#fff4d6" ${STROKE}/></svg>`,
  curio: `<svg viewBox="0 0 64 64"><path d="M32 6 L56 32 L32 58 L8 32 Z" fill="#5cf0d0" ${STROKE}/><path d="M32 6 L32 58 M8 32 H56" stroke="#2b2150" stroke-width="2"/></svg>`,
};

const INFO: Record<CelebrateKind, Omit<Info, 'svg'>> = {
  sight: { title: 'ראיית חוטים', text: 'המחט מראה את מה שמתחת לעולם: חוטים, שליחים ותקלות.' },
  house: { title: 'הבית הראשון', text: 'בכל בית יש סיפור, חפצים וסוד.' },
  creature: { title: 'חבר חדש', text: 'כל יצור בעמק מייצג רעיון מעולם הרשתות.' },
  diary: { title: 'דף יומן', text: 'נועם כתב כאן. מי היה לפניכם בעמק?' },
  card: { title: 'כרטיס חדש', text: 'עוד מושג נכנס לאוסף.' },
  curio: { title: 'חפץ מיוחד', text: 'משהו קטן שמספר על העמק.' },
};

/**
 * The first time something happens, a short clip plays (or a card, until the clip exists) and the player taps to go on.
 * The next times, a small icon jumps up, spins and fades, so the moment is felt without stopping the game.
 */
export async function celebrate(kind: CelebrateKind, first: boolean, label?: string): Promise<void> {
  if (first) {
    audio.sfx('fanfare');
    if (await playCutscene(`first_${kind}`)) return;
    await new Promise<void>((resolve) => {
      const go = el('button', 'btn primary', 'ממשיכים');
      go.type = 'button';
      const icon = el('div', 'first-icon');
      icon.innerHTML = SVG[kind];
      const card = el('div', 'first-card', '', [icon, el('h2', '', INFO[kind].title), el('p', '', label ? `${label}. ${INFO[kind].text}` : INFO[kind].text), go]);
      const screen = el('div', 'screen first', '', [card]);
      uiRoot().append(screen);
      const close = (): void => { screen.remove(); resolve(); };
      go.addEventListener('click', close);
      window.setTimeout(close, 9000);
      go.focus();
    });
    return;
  }
  audio.sfx('pop');
  const icon = el('div', 'pop-icon');
  icon.innerHTML = SVG[kind];
  const pop = el('div', 'popspin', '', [icon, label ? el('span', 'pop-label', label) : null]);
  uiRoot().append(pop);
  window.setTimeout(() => pop.remove(), 1900);
}
