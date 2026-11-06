import { QUALITY_NAME, type QualityManager, type QualitySetting } from '../core/quality';
import { audio } from '../audio/audio';
import type { SaveStore } from '../core/save';
import { el } from './dom';
import { createOverlay } from './learning/overlay';

/** Small settings screen: picture quality (recommended by default), the FPS counter and subtitles. */
export function openSettings(save: SaveStore, quality: QualityManager, opts: { onChange(): void; onClose(): void; onHelp?(): void }): void {
  const ov = createOverlay('lrn-mini npcg', null);
  const closeBtn = el('button', 'lrn-x', '×');
  closeBtn.type = 'button';
  closeBtn.setAttribute('aria-label', 'סגירה');
  const head = el('header', 'lrn-head', '', [el('div', 'lrn-head-main', '', [el('h1', 'lrn-title', 'הגדרות')]), closeBtn]);
  const body = el('main', 'lrn-body');
  ov.root.append(head, body);

  const close = (): void => {
    document.removeEventListener('keydown', onKey, true);
    ov.destroy();
    opts.onClose();
  };
  const onKey = (e: KeyboardEvent): void => { if (e.key === 'Escape') { e.preventDefault(); close(); } };
  closeBtn.addEventListener('click', close);
  document.addEventListener('keydown', onKey, true);

  const choices: Array<{ value: QualitySetting; title: string; desc: string }> = [
    { value: 'auto', title: `מומלצת למכשיר שלכם (${QUALITY_NAME[quality.recommendedLevel]})`, desc: 'נבחרת לפי המכשיר, ויורדת בעצמה אם המשחק מגמגם.' },
    { value: 'high', title: 'גבוהה', desc: 'כל האפקטים: זוהר, עננים, אור וצללים. למחשבים וטלפונים חזקים.' },
    { value: 'medium', title: 'בינונית', desc: 'פחות אפקטים, בלי זוהר סביב דמויות.' },
    { value: 'low', title: 'נמוכה', desc: 'הכי מהיר: 30 פריימים בשנייה, בלי אפקטי מסך וצללים. המשחק נשאר אותו משחק.' },
  ];

  function render(): void {
    const cards = choices.map((c) => {
      const on = quality.setting === c.value;
      const b = el('button', `btn ${on ? 'primary' : ''}`, on ? `✓ ${c.title}` : c.title);
      b.type = 'button';
      b.addEventListener('click', () => { quality.set(c.value); opts.onChange(); render(); });
      return el('section', `lrn-level ${on ? 'passed' : ''}`, '', [b, el('p', 'lrn-sub', c.desc)]);
    });
    const fps = el('button', `btn ${save.data.settings.showFps ? 'primary' : ''}`, save.data.settings.showFps ? '✓ מד FPS מוצג' : 'להציג מד FPS');
    fps.type = 'button';
    fps.addEventListener('click', () => { save.data.settings.showFps = !save.data.settings.showFps; save.save(); opts.onChange(); render(); });
    const subs = el('button', `btn ${save.data.settings.subtitles ? 'primary' : ''}`, save.data.settings.subtitles ? '✓ כתוביות פעילות' : 'להפעיל כתוביות');
    subs.type = 'button';
    subs.addEventListener('click', () => { save.data.settings.subtitles = !save.data.settings.subtitles; save.save(); opts.onChange(); render(); });
    const slider = (label: string, key: 'musicVol' | 'sfxVol', onKey: 'musicOn' | 'sfxOn'): HTMLElement => {
      const s = save.data.settings;
      const input = el('input', 'vol-range');
      input.type = 'range';
      input.min = '0';
      input.max = '100';
      input.value = String(Math.round(s[key] * 100));
      input.setAttribute('aria-label', label);
      input.addEventListener('input', () => {
        s[key] = Number(input.value) / 100;
        audio.configure({ [key]: s[key] });
        save.save();
      });
      input.addEventListener('change', () => audio.sfx('click'));
      const off = el('button', `btn ${s[onKey] ? '' : 'primary'}`, s[onKey] ? 'השתיקו' : 'מושתק: להחזיר');
      off.type = 'button';
      off.addEventListener('click', () => { s[onKey] = !s[onKey]; audio.configure({ [onKey]: s[onKey] }); save.save(); render(); });
      return el('div', 'vol-row', '', [el('span', 'vol-label', label), input, off]);
    };
    body.replaceChildren(
      el('h2', 'lrn-sub', 'צליל'),
      slider('מוזיקה', 'musicVol', 'musicOn'),
      slider('אפקטים', 'sfxVol', 'sfxOn'),
      el('p', 'lrn-sub', 'במשימות ובשיעורים המוזיקה שקטה במיוחד, כדי שיהיה קל להתרכז.'),
      el('h2', 'lrn-sub', 'איכות תמונה'),
      el('p', 'lrn-sub', `רמה פעילה כרגע: ${QUALITY_NAME[quality.level]}. אפשר לשנות בכל זמן, וההתקדמות נשמרת.`),
      el('div', 'lrn-levels', '', cards),
      el('div', 'npcg-row', '', [fps, subs]),
      ...(opts.onHelp ? [(() => {
        const h = el('button', 'btn', 'עזרה: איך משחקים');
        h.type = 'button';
        h.addEventListener('click', () => opts.onHelp?.());
        return el('div', 'npcg-row', '', [h]);
      })()] : []),
    );
  }
  render();
}
