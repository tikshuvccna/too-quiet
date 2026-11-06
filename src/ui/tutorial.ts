import { HELP, type TutorialCard } from './help';
import { el } from './dom';
import { createOverlay } from './learning/overlay';
import type { SaveStore } from '../core/save';

export const TUTORIAL_FLAG = 'tutorial_seen';

const NS = 'http://www.w3.org/2000/svg';

/** Small drawn pictures (inline SVG, no emoji, no files). */
const ART: Record<TutorialCard['art'], string> = {
  play: `
<circle cx="52" cy="62" r="34" fill="rgba(20,19,46,.7)" stroke="#ffd27a" stroke-width="2.5"/>
<circle cx="52" cy="62" r="14" fill="#ffd27a" opacity=".85"/>
<path d="M52 24v8M52 92v8M14 62h8M82 62h8" stroke="#5cf0d0" stroke-width="3" stroke-linecap="round"/>
<circle cx="124" cy="62" r="24" fill="#5cf0d0" stroke="#0a6a56" stroke-width="3"/>
<text x="124" y="70" text-anchor="middle" font-size="22" font-weight="800" fill="#07352c" font-family="Arial, sans-serif">E</text>
<path d="M170 94c14-36 30 6 52-28" fill="none" stroke="#ffd27a" stroke-width="2.5" stroke-dasharray="5 4"/>
<circle cx="170" cy="94" r="7" fill="#5cf0d0"/><circle cx="222" cy="66" r="7" fill="#5cf0d0"/>
<path d="M188 34q18-15 36 0q-18 15-36 0z" fill="none" stroke="#ffd27a" stroke-width="2.5"/><circle cx="206" cy="34" r="5" fill="#ffd27a"/>`,
  storm: `
<rect x="26" y="52" width="34" height="62" fill="#3b3a78" stroke="#ffd27a" stroke-width="2.5"/>
<path d="M20 54 43 24 66 54z" fill="#6b4aa8" stroke="#ffd27a" stroke-width="2.5"/>
<rect x="38" y="68" width="10" height="14" fill="#ffd27a"/>
<path d="M104 52a16 16 0 0 1 30-8 14 14 0 0 1 24 12 12 12 0 0 1-4 24h-50a14 14 0 0 1 0-28z" fill="#4a4580" stroke="#b3b2d8" stroke-width="2.5"/>
<path d="M136 70l-8 16h10l-8 16" fill="none" stroke="#ffd27a" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M184 100h40M210 88l14 12-14 12" fill="none" stroke="#5cf0d0" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>`,
  hints: `
<rect x="14" y="26" width="104" height="32" rx="16" fill="#e0a944" stroke="#fff0c4" stroke-width="2.5"/>
<circle cx="40" cy="41" r="8" fill="rgba(255,255,255,.35)" stroke="#3a2606" stroke-width="3"/><path d="M46 47l9 9" stroke="#3a2606" stroke-width="4" stroke-linecap="round"/>
<text x="88" y="48" text-anchor="middle" font-size="20" font-weight="800" fill="#3a2606" font-family="Arial, sans-serif">רמז</text>
<rect x="136" y="20" width="40" height="54" rx="6" fill="#272560" stroke="#5cf0d0" stroke-width="2.5"/><path d="M146 38h20M146 48h20M146 58h12" stroke="#b3b2d8" stroke-width="3" stroke-linecap="round"/>
<circle cx="208" cy="46" r="18" fill="#ffd27a" stroke="#b8862f" stroke-width="3"/><path d="M208 36v20M202 42h12" stroke="#b8862f" stroke-width="3" stroke-linecap="round"/>
<path d="M30 100q30-24 60 0t60 0t60 0" fill="none" stroke="#ffd27a" stroke-width="2.5" stroke-dasharray="5 4"/>
<circle cx="30" cy="100" r="6" fill="#5cf0d0"/><circle cx="210" cy="100" r="6" fill="#5cf0d0"/>`,
};

function art(kind: TutorialCard['art']): SVGElement {
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('viewBox', '0 0 240 124');
  svg.setAttribute('class', 'tut-art');
  svg.setAttribute('aria-hidden', 'true');
  svg.setAttribute('focusable', 'false');
  svg.innerHTML = ART[kind];
  return svg;
}

/**
 * The quick tutorial: up to three cards, each with a drawn picture, a title and two short lines. Resolves when it is
 * finished or skipped. Both set the save flag `tutorial_seen`, so it shows once by itself; `again` reopens it from the help.
 */
export function openTutorial(save: SaveStore, again: boolean): Promise<void> {
  return new Promise((resolve) => {
    const T = HELP.tutorial;
    const ov = createOverlay('tut', null);
    let i = 0;
    const card = el('section', 'tut-card');
    const dots = el('div', 'tut-dots', '', T.cards.map(() => el('span', 'tut-dot')));
    const skip = el('button', 'btn', T.skip);
    const next = el('button', 'btn primary', T.next);
    skip.type = 'button';
    next.type = 'button';
    ov.root.append(el('div', 'tut-wrap', '', [card, dots, el('div', 'tut-row', '', [skip, next])]));
    ov.root.setAttribute('aria-label', 'הסבר קצר');

    let finished = false;
    const finish = (): void => {
      if (finished) return;
      finished = true;
      window.removeEventListener('keydown', onKey, true);
      if (!save.hasFlag(TUTORIAL_FLAG)) save.setFlag(TUTORIAL_FLAG);
      ov.destroy();
      resolve();
    };
    const paint = (): void => {
      const c = T.cards[i] as TutorialCard;
      const last = i === T.cards.length - 1;
      card.replaceChildren(art(c.art), el('h2', '', c.title), ...c.lines.map((l) => el('p', '', l)));
      Array.from(dots.children).forEach((d, k) => d.classList.toggle('on', k === i));
      next.textContent = last ? (again ? T.done : T.start) : T.next;
      skip.style.display = last ? 'none' : '';
      next.focus();
    };
    const go = (): void => {
      if (i >= T.cards.length - 1) finish();
      else { i++; paint(); }
    };
    const onKey = (e: KeyboardEvent): void => {
      if (e.key === 'Escape') { e.preventDefault(); e.stopImmediatePropagation(); finish(); }
      else if (e.key === 'Enter' && document.activeElement !== skip) { e.preventDefault(); e.stopImmediatePropagation(); go(); }
    };
    window.addEventListener('keydown', onKey, true);
    skip.addEventListener('click', finish);
    next.addEventListener('click', go);
    paint();
  });
}
