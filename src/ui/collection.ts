import { CREATURES, HEAD_INFO, allItems, type ItemInfo } from '../content';
import type { SaveStore } from '../core/save';
import { el, uiRoot } from './dom';
import { flatten } from './portraits';

const TABS: Array<{ kind: ItemInfo['kind'] | 'creature'; title: string; mystery: string }> = [
  { kind: 'card', title: 'כרטיסי חוט', mystery: 'כרטיס שעוד לא נמצא' },
  { kind: 'diary', title: 'דפי היומן של נועם', mystery: 'דף שעוד לא נמצא' },
  { kind: 'curio', title: 'חפצים מוזרים', mystery: 'חפץ שעוד לא נמצא' },
  { kind: 'creature', title: 'יצורי העמק', mystery: 'יצור שעוד לא פגשתם' },
];

/** The collection screen: found items show their text, missing ones stay a mystery. */
interface CodexSheet { w: number; h: number; url: string; frames: Record<string, { x: number; y: number; w: number; h: number }> }
let codex: Promise<CodexSheet[]> | null = null;

function loadOne(name: string): Promise<CodexSheet | null> {
  return fetch(`${import.meta.env.BASE_URL}assets/creatures/${name}.json`)
    .then((r) => (r.ok ? r.json() : null))
    .then((j: { frames: Parameters<typeof flatten>[0]; meta: { size: { w: number; h: number } } } | null) => (j ? { w: j.meta.size.w, h: j.meta.size.h, frames: flatten(j.frames), url: `${import.meta.env.BASE_URL}assets/creatures/${name}.png` } : null))
    .catch(() => null);
}

/** The first codex sheet is the original creatures, the second one the creatures of the big world. */
function loadCodex(): Promise<CodexSheet[]> {
  codex ??= Promise.all([loadOne('codex'), loadOne('wc_codex')]).then((l) => l.filter((x): x is CodexSheet => !!x));
  return codex;
}

function creatureItems(): ItemInfo[] {
  const list: ItemInfo[] = Object.entries(CREATURES).map(([key, c]) => ({ id: `creature_${key}`, kind: 'curio', title: c.name_he, text: c.legend_he ? `${c.legend_he} ${c.concept_he}` : c.concept_he }));
  list.push({ id: 'creature_the_head', kind: 'curio', title: HEAD_INFO.name_he, text: HEAD_INFO.concept_he });
  return list;
}

export function openCollection(save: SaveStore, onClose: () => void): void {
  const items = allItems();
  let tab = 0;
  const body = el('div', 'col-body');
  const tabs = el('div', 'row col-tabs');
  const close = el('button', 'btn primary', 'סגירה');
  const render = (): void => {
    const t = TABS[tab] as (typeof TABS)[number];
    const mine = t.kind === 'creature' ? creatureItems() : items.filter((i) => i.kind === t.kind);
    const got = mine.filter((i) => save.data.collected[i.id]).length;
    body.replaceChildren(
      el('p', 'col-count', `${got} מתוך ${mine.length}`),
      ...mine.map((i) => {
        const have = !!save.data.collected[i.id];
        const row = el('div', `col-item${have ? '' : ' missing'}`, '', [
          el('b', '', have ? i.title : '???'),
          el('span', '', have ? i.text : t.mystery),
        ]);
        if (t.kind === 'creature') {
          const key = i.id.slice(9);
          const thumb = el('div', 'col-thumb');
          row.prepend(thumb);
          row.classList.add('has-thumb');
          void loadCodex().then((sheets) => {
            const sheet = sheets.find((s) => s.frames[key]);
            const f = sheet?.frames[key];
            if (!sheet || !f) return thumb.remove();
            const k = 72 / f.w;
            Object.assign(thumb.style, {
              backgroundImage: `url(${sheet.url})`,
              backgroundSize: `${sheet.w * k}px ${sheet.h * k}px`,
              backgroundPosition: `-${f.x * k}px -${f.y * k}px`,
              filter: have ? 'none' : 'brightness(0) opacity(.5)',
            });
          });
        }
        return row;
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
