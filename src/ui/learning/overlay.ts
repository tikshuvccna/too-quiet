import './learning.css';
import { el, uiRoot } from '../dom';

export interface Overlay { root: HTMLElement; destroy(): void }

/** A full-screen layer that sits above the game. Keyboard handling is added by the caller. */
export function createOverlay(cls: string): Overlay {
  const root = el('div', `lrn ${cls}`);
  root.dir = 'rtl';
  root.lang = 'he';
  root.setAttribute('role', 'dialog');
  root.setAttribute('aria-modal', 'true');
  (document.getElementById('ui') ? uiRoot() : document.body).append(root);
  return { root, destroy: () => root.remove() };
}

/** Small in-page confirmation: window.confirm is ugly and sometimes blocked on phones. */
export function confirmDialog(parent: HTMLElement, message: string, yes: string, no: string): Promise<boolean> {
  return new Promise((resolve) => {
    const finish = (v: boolean): void => { wrap.remove(); resolve(v); };
    const bYes = el('button', 'btn primary', yes);
    const bNo = el('button', 'btn', no);
    bYes.type = 'button';
    bNo.type = 'button';
    bYes.addEventListener('click', () => finish(true));
    bNo.addEventListener('click', () => finish(false));
    const wrap = el('div', 'lrn-confirm', '', [el('div', 'lrn-confirm-card', '', [el('p', '', message), el('div', 'lrn-row', '', [bNo, bYes])])]);
    wrap.addEventListener('keydown', (e) => { if (e.key === 'Escape') { e.stopPropagation(); finish(false); } });
    parent.append(wrap);
    bNo.focus();
  });
}

const ALLOWED = new Set(['P', 'B', 'I', 'CODE', 'UL', 'OL', 'LI', 'BR', 'SPAN', 'H4', 'TABLE', 'THEAD', 'TBODY', 'TR', 'TH', 'TD']);

/**
 * Builds the content html through an allow-list. Unknown tags are dropped but their text is kept, and no
 * attribute is ever copied, so nothing in the content can run script or load anything.
 */
export function sanitizeInto(target: HTMLElement, html: string): void {
  const doc = new DOMParser().parseFromString(`<body>${html}</body>`, 'text/html');
  const copy = (from: Node, to: Node): void => {
    for (const child of Array.from(from.childNodes)) {
      if (child.nodeType === Node.TEXT_NODE) {
        to.appendChild(document.createTextNode(child.textContent ?? ''));
      } else if (child instanceof Element) {
        const tag = child.tagName.toUpperCase();
        if (ALLOWED.has(tag)) {
          const e = document.createElement(tag.toLowerCase());
          copy(child, e);
          to.appendChild(e);
        } else if (tag !== 'SCRIPT' && tag !== 'STYLE') {
          copy(child, to);
        }
      }
    }
  };
  target.replaceChildren();
  copy(doc.body, target);
}

/** Wrap tables so they can scroll sideways on a narrow screen instead of breaking the page. */
export function wrapTables(root: HTMLElement): void {
  for (const t of Array.from(root.querySelectorAll('table'))) {
    const w = el('div', 'lrn-tablewrap');
    t.replaceWith(w);
    w.append(t);
  }
}
