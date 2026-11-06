import './help.css';
import helpJson from '../../content/he/help.json';
import { el } from './dom';
import { hintBadge } from './hintBadge';
import { createOverlay } from './learning/overlay';

export interface HelpSection { id: string; title: string; lines: string[] }
export interface TutorialCard { art: 'play' | 'storm' | 'hints'; title: string; lines: string[] }
export interface HelpContent {
  title: string; intro: string; legend: string; tutorialButton: string; closeLabel: string;
  sections: HelpSection[];
  tutorial: { next: string; skip: string; start: string; done: string; cards: TutorialCard[] };
}

export const HELP = helpJson as unknown as HelpContent;

/** Full-screen help with short expandable sections. `onTutorial` reopens the quick tutorial. */
export function openHelp(opts: { onTutorial(): void; onClose(): void }): void {
  const ov = createOverlay('lrn-mini help', null);
  const closeBtn = el('button', 'lrn-x', '×');
  closeBtn.type = 'button';
  closeBtn.setAttribute('aria-label', HELP.closeLabel);
  ov.root.append(el('header', 'lrn-head', '', [el('div', 'lrn-head-main', '', [el('h1', 'lrn-title', HELP.title)]), closeBtn]));

  const body = el('main', 'lrn-body');
  const legend = el('p', 'help-legend', '', [hintBadge(), el('span', '', HELP.legend.replace(/^רמז:\s*/, ''))]);
  const list = el('div', 'help-list');
  const all: HTMLDetailsElement[] = [];
  for (const s of HELP.sections) {
    const d = document.createElement('details');
    d.className = 'help-sec';
    d.id = `help-${s.id}`;
    d.append(el('summary', '', s.title), el('ul', '', '', s.lines.map((l) => el('li', '', l))));
    // one section open at a time keeps the page short on a phone
    d.addEventListener('toggle', () => {
      if (!d.open) return;
      for (const o of all) if (o !== d) o.open = false;
    });
    all.push(d);
    list.append(d);
  }
  const again = el('button', 'btn primary', HELP.tutorialButton);
  again.type = 'button';
  again.addEventListener('click', () => opts.onTutorial());
  body.append(el('p', 'lrn-sub', HELP.intro), legend, list, el('div', 'help-foot', '', [again]));
  ov.root.append(body);

  let closed = false;
  const close = (): void => {
    if (closed) return;
    closed = true;
    window.removeEventListener('keydown', onKey, true);
    ov.destroy();
    opts.onClose();
  };
  // on window in the capture phase, so Escape closes only the help and not the settings underneath
  const onKey = (e: KeyboardEvent): void => {
    if (e.key !== 'Escape' || document.querySelector('.tut')) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    close();
  };
  window.addEventListener('keydown', onKey, true);
  closeBtn.addEventListener('click', close);
  closeBtn.focus();
}
