import { el } from './dom';
import { createOverlay } from './learning/overlay';

/** Exact credits text, as requested by the owner. Do not reword. */
export const CREDITS = {
  title: 'קרדיטים',
  made: 'משחק זה פותח ונבנה על ידי מיכאל תקשוב מאתר מגמת תקשוב.',
  url: 'https://tikshuv-ccna.com',
  services: 'לפיתוח משחקים, סרטונים שיווקיים, תוכנות וייעוץ פנו.',
  email: 'tikshuvccna@gmail.com',
  escape: 'לפניות בנושא בניית חדרי בריחה דיגיטליים ופיזיים בהתאמה אישית:',
  escapeUrl: 'https://escapebuilder.com',
  thanks: 'תודה לכל המסייעים, בטא טסטרים ומייעצים.',
};

/** A link that opens in a new tab. The address stays left-to-right inside the Hebrew text. */
export function creditsLink(url: string = CREDITS.url): HTMLAnchorElement {
  const a = el('a', 'credits-link', url);
  a.href = url;
  a.target = '_blank';
  a.rel = 'noopener noreferrer';
  a.dir = 'ltr';
  return a;
}

function mailLink(): HTMLAnchorElement {
  const a = el('a', 'credits-link', CREDITS.email);
  a.href = `mailto:${CREDITS.email}`;
  a.dir = 'ltr';
  return a;
}

/** Credits screen. The promise resolves when it is closed (so the end of the game can wait for it). */
export function openCredits(): Promise<void> {
  return new Promise((resolve) => {
    const ov = createOverlay('lrn-mini credits', null);
    const closeBtn = el('button', 'lrn-x', '×');
    closeBtn.type = 'button';
    closeBtn.setAttribute('aria-label', 'סגירה');
    ov.root.append(el('header', 'lrn-head', '', [el('div', 'lrn-head-main', '', [el('h1', 'lrn-title', CREDITS.title)]), closeBtn]));
    const back = el('button', 'btn primary', 'חזרה');
    back.type = 'button';
    ov.root.append(el('main', 'lrn-body credits-body', '', [
      el('p', 'credits-main', CREDITS.made),
      el('p', 'credits-url', '', [creditsLink()]),
      el('p', 'credits-main', CREDITS.services),
      el('p', 'credits-url', '', [mailLink()]),
      el('p', 'credits-main credits-gap', CREDITS.escape),
      el('p', 'credits-url', '', [creditsLink(CREDITS.escapeUrl)]),
      el('p', 'credits-thanks', CREDITS.thanks),
      el('div', 'help-foot', '', [back]),
    ]));

    let closed = false;
    const close = (): void => {
      if (closed) return;
      closed = true;
      window.removeEventListener('keydown', onKey, true);
      ov.destroy();
      resolve();
    };
    // capture on window: Escape closes only the credits and not the screen underneath
    const onKey = (e: KeyboardEvent): void => {
      if (e.key !== 'Escape') return;
      e.preventDefault();
      e.stopImmediatePropagation();
      close();
    };
    window.addEventListener('keydown', onKey, true);
    closeBtn.addEventListener('click', close);
    back.addEventListener('click', close);
    back.focus();
  });
}
