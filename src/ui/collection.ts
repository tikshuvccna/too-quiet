import { CREATURES, HEAD_INFO, allItems, type ItemInfo } from '../content';
import type { SaveStore } from '../core/save';
import { el, uiRoot } from './dom';
import { flatten } from './portraits';
import { HOUSE_INFO, layersOf, type HouseInfo } from '../game/houseBook';

const TABS: Array<{ kind: ItemInfo['kind'] | 'creature' | 'house'; title: string; mystery: string }> = [
  { kind: 'card', title: 'כרטיסי חוט', mystery: 'כרטיס שעוד לא נמצא' },
  { kind: 'diary', title: 'דפי היומן של נועם', mystery: 'דף שעוד לא נמצא' },
  { kind: 'curio', title: 'חפצים מוזרים', mystery: 'חפץ שעוד לא נמצא' },
  { kind: 'creature', title: 'יצורי העמק', mystery: 'יצור שעוד לא פגשתם' },
  { kind: 'house', title: 'בתים', mystery: 'בית שעוד לא ביקרתם בו' },
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

const buildingSheets = new Map<string, Promise<CodexSheet | null>>();
function loadBuildings(name: string): Promise<CodexSheet | null> {
  let p = buildingSheets.get(name);
  if (!p) {
    p = fetch(`${import.meta.env.BASE_URL}assets/buildings/${name}.json`)
      .then((r) => (r.ok ? r.json() : null))
      .then((j: { frames: Parameters<typeof flatten>[0]; meta: { size: { w: number; h: number } } } | null) => (j ? { w: j.meta.size.w, h: j.meta.size.h, frames: flatten(j.frames), url: `${import.meta.env.BASE_URL}assets/buildings/${name}.png` } : null))
      .catch(() => null);
    buildingSheets.set(name, p);
  }
  return p;
}

const UNKNOWN = 'עוד לא ידוע';

/** One card of the house book: the picture is cropped from the buildings atlas. */
function houseCard(h: HouseInfo, save: SaveStore): HTMLElement {
  const flags = save.data.flags;
  const layers = layersOf(h, { has: (f) => !!flags[f], count: (p) => Object.keys(flags).filter((k) => k.startsWith(p)).length });
  const thumb = el('div', 'house-thumb');
  void loadBuildings(h.atlas).then((sheet) => {
    const f = sheet?.frames[h.frame];
    if (!sheet || !f) return thumb.remove();
    const k = Math.min(96 / f.w, 84 / f.h);
    Object.assign(thumb.style, {
      width: `${f.w * k}px`, height: `${f.h * k}px`,
      backgroundImage: `url(${sheet.url})`,
      backgroundSize: `${sheet.w * k}px ${sheet.h * k}px`,
      backgroundPosition: `-${f.x * k}px -${f.y * k}px`,
      filter: layers.l1 ? 'none' : 'brightness(0) opacity(.55)',
    });
  });
  if (!layers.l1) {
    return el('div', 'col-item house-card missing', '', [thumb, el('b', '', '?'), el('span', '', 'בית שעוד לא ביקרתם בו')]);
  }
  const owner = h.owner === 'לא ידוע' ? 'לא ידוע' : `${h.owner}, ${h.role}`;
  const part = (label: string, text: string | null): HTMLElement =>
    el('p', `house-part${text ? '' : ' unknown'}`, '', [el('i', '', `${label}: `), document.createTextNode(text ?? UNKNOWN)]);
  return el('div', 'col-item house-card', '', [
    thumb,
    el('b', '', h.name),
    el('span', 'house-owner', owner),
    el('div', 'house-body', '', [
      part('היסטוריה', layers.l2 ? h.history.join(' ') : null),
      part('מה לא בסדר', layers.l3 ? `${h.problem} ${h.topic}` : null),
      part('מה חשוב כאן', layers.l3 ? h.important : null),
    ]),
  ]);
}

export function openCollection(save: SaveStore, onClose: () => void): void {
  const items = allItems();
  let tab = 0;
  const body = el('div', 'col-body');
  const tabs = el('div', 'row col-tabs');
  const close = el('button', 'btn primary', 'סגירה');
  const render = (): void => {
    const t = TABS[tab] as (typeof TABS)[number];
    if (t.kind === 'house') {
      const seen = HOUSE_INFO.filter((h) => layersOf(h, { has: (f) => !!save.data.flags[f], count: (p) => Object.keys(save.data.flags).filter((k) => k.startsWith(p)).length }).l1).length;
      body.replaceChildren(el('p', 'col-count', `${seen} מתוך ${HOUSE_INFO.length}`), ...HOUSE_INFO.map((h) => houseCard(h, save)));
      [...tabs.children].forEach((b, idx) => b.classList.toggle('on', idx === tab));
      return;
    }
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
