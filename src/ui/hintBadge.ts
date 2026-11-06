import './help.css';
/** The small gold "רמז" badge: a magnifier with a glint, drawn inline (no emoji, no image file). */
const SVG = `<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false">
<circle cx="9.5" cy="9.5" r="5.6" fill="rgba(255,243,200,.35)" stroke="currentColor" stroke-width="2.2"/>
<path d="M13.8 13.8 20.5 20.5" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
<path class="glint" d="M7 7.2l1.1 1.1M9.3 6l.4 1.6" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>
</svg>`;

export function hintBadge(): HTMLElement {
  const b = document.createElement('span');
  b.className = 'hint-badge';
  b.setAttribute('data-hint', '1');
  b.innerHTML = `${SVG}<span class="hint-badge-word">רמז</span>`;
  return b;
}
