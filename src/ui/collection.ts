import { allItems, type ItemInfo } from '../content';
import type { SaveStore } from '../core/save';
import { el, uiRoot } from './dom';

const TABS: Array<{ kind: ItemInfo['kind']; title: string; mystery: string }> = [
  { kind: 'card', title: 'כרטיסי חוט', mystery: 'כרטיס שעוד לא נמצא' },
  { kind: 'diary', title: 'דפי היומן של נועם', mystery: 'דף שעוד לא נמצא' },
  { kind: 'curio', title: 'חפצים מוזרים', mystery: 'חפץ שעוד לא נמצא' },
];

/** The collection screen: found items show their text, missing ones stay a mystery. */
export function openCollection(save: SaveStore, onClose: () => void): void {
  const items = allItems();
  let tab = 0;
  const body = el('div', 'col-body');
  const tabs = el('div', 'row col-tabs');
  const close = el('button', 'btn primary', 'סגירה');
  const render = (): void => {
    const t = TABS[tab] as (typeof TABS)[number];
    const mine = items.filter((i) => i.kind === t.kind);
    const got = mine.filter((i) => save.data.collected[i.id]).length;
    body.replaceChildren(
      el('p', 'col-count', `${got} מתוך ${mine.length}`),
      ...mine.map((i) => {
        const have = !!save.data.collected[i.id];
        return el('div', `col-item${have ? '' : ' missing'}`, '', [
          el('b', '', have ? i.title : '???'),
          el('span', '', have ? i.text : t.mystery),
        ]);
      }),
    );
    [...tabs.children].forEach((b, idx) => b.classList.toggle('on', idx === tab));
  };
  TABS.forEach((t, idx) => {
    const b = el('button', 'btn', t.title);
    b.addEventListener('click', () => {
      tab = idx;
      render();
    });
    tabs.append(b);
  });
  const screen = el('div', 'screen', '', [el('div', 'card', '', [el('h2', '', 'האוסף שלי'), tabs, body, el('div', 'row', '', [close])])]);
  close.addEventListener('click', () => {
    screen.remove();
    onClose();
  });
  uiRoot().append(screen);
  render();
}
