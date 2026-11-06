import './houseActivities.css';
import { audio } from '../audio/audio';
import type { SecretDef } from '../world/secrets';
import { el } from './dom';
import { createOverlay } from './learning/overlay';

/** A small full-screen card with one close button. Resolves when closed. */
function card(cls: string, build: () => HTMLElement[], sfx: 'prize' | 'pickup'): Promise<void> {
  return new Promise((resolve) => {
    const ov = createOverlay('hx-reveal');
    const close = el('button', 'btn primary', 'סגירה');
    close.type = 'button';
    const box = el('div', `hx-card-big ${cls}`, '', [...build(), el('div', 'hx-row', '', [close])]);
    ov.root.append(el('main', 'lrn-body', '', [box]));
    let closed = false;
    const done = (): void => {
      if (closed) return;
      closed = true;
      document.removeEventListener('keydown', onKey, true);
      ov.destroy();
      resolve();
    };
    const onKey = (e: KeyboardEvent): void => { if (e.key === 'Escape' || e.key === 'Enter') { e.preventDefault(); done(); } };
    document.addEventListener('keydown', onKey, true);
    close.addEventListener('click', done);
    audio.sfx(sfx);
    close.focus();
  });
}

/** The scroll / note / rhyme that holds the clue. Can be opened again at the same object. */
export function showClue(def: SecretDef, firstTime: boolean): Promise<void> {
  return card('hx-scroll', () => {
    const out: HTMLElement[] = [el('h2', '', def.clue.title)];
    if (firstTime) out.push(el('p', '', def.clue.found));
    out.push(el('ol', '', '', def.clue.lines.map((l) => el('li', '', l))));
    if (def.clue.footer) out.push(el('p', 'hx-foot', def.clue.footer));
    return out;
  }, 'pickup');
}

/** The short reveal when a sequence is solved. */
export function showReveal(def: SecretDef, prize: string): Promise<void> {
  return card('', () => [
    el('h2', '', def.reveal.title),
    ...def.reveal.lines.map((l) => el('p', '', l)),
    el('p', 'hx-prize', `מצאתם: ${prize}`),
  ], 'prize');
}
