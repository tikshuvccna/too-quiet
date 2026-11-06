import { el } from './dom';
import { audio } from '../audio/audio';
import { createOverlay } from './learning/overlay';
import shortsData from '../../content/he/shorts.json';

/** A Short from the channel. It plays from YouTube (nothing is downloaded until the player taps), with the small local copy as a fallback. */
export interface ShortInfo {
  id: string;
  title: string;
  youtube: string;
  seconds: number;
}

export const SHORTS: ShortInfo[] = shortsData as ShortInfo[];

export const shortById = (id: string): ShortInfo | undefined => SHORTS.find((s) => s.id === id);

/** The 11 character video id inside a youtube.com/shorts/<id> or watch?v=<id> or youtu.be/<id> link. */
export function youtubeId(url: string): string | null {
  const m = /(?:shorts\/|v=|youtu\.be\/|embed\/)([A-Za-z0-9_-]{11})/.exec(url);
  return m ? (m[1] as string) : null;
}

/** The privacy-friendly embed address (no tracking cookies until the video is played). */
export function embedUrl(url: string): string | null {
  const id = youtubeId(url);
  return id ? `https://www.youtube-nocookie.com/embed/${id}?rel=0&playsinline=1&modestbranding=1&autoplay=1` : null;
}

const asset = (id: string, ext: string): string => `${import.meta.env.BASE_URL}assets/shorts/${id}.${ext}`;

/** A small card (poster, title, length) that opens the player when tapped. */
export function shortCard(id: string): HTMLElement | null {
  const s = shortById(id);
  if (!s) return null;
  const poster = el('img', 'short-poster') as HTMLImageElement;
  poster.src = asset(id, 'jpg');
  poster.alt = '';
  poster.loading = 'lazy';
  poster.addEventListener('error', () => poster.remove());
  const btn = el('button', 'btn primary', `לצפות (${Math.max(1, Math.round(s.seconds / 60))} דקה)`) as HTMLButtonElement;
  btn.type = 'button';
  btn.addEventListener('click', () => openShort(id));
  return el('section', 'lrn-short short-card', '', [poster, el('div', 'short-meta', '', [el('h3', '', s.title), btn])]);
}

/** Full-screen player: YouTube first, and a button for the local copy when the embed does not load (offline, blocked at school). */
export function openShort(id: string, onClose?: () => void): () => void {
  const s = shortById(id);
  if (!s) { onClose?.(); return () => undefined; }
  const ov = createOverlay('lrn-mini short-overlay', null);
  audio.duck(true);
  const stage = el('div', 'short-stage');
  const closeBtn = el('button', 'lrn-x', '×') as HTMLButtonElement;
  closeBtn.type = 'button';
  closeBtn.setAttribute('aria-label', 'סגירה');
  const fallback = el('button', 'btn', 'לא נטען? צפו כאן') as HTMLButtonElement;
  fallback.type = 'button';
  const link = el('a', 'btn', 'לצפות ביוטיוב') as HTMLAnchorElement;
  link.href = s.youtube;
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  const head = el('header', 'lrn-head', '', [el('div', 'lrn-head-main', '', [el('h1', 'lrn-title', s.title)]), closeBtn]);
  const row = el('div', 'lrn-row short-row', '', [fallback, link]);
  ov.root.append(head, el('main', 'lrn-body short-body', '', [stage, row]));

  const playOnline = (): void => {
    const url = embedUrl(s.youtube);
    if (!url || !navigator.onLine) { playLocal(); return; }
    const f = el('iframe', 'short-frame') as HTMLIFrameElement;
    f.src = url;
    f.title = s.title;
    f.allow = 'autoplay; encrypted-media; picture-in-picture';
    f.allowFullscreen = true;
    f.referrerPolicy = 'strict-origin-when-cross-origin';
    stage.replaceChildren(f);
  };
  const playLocal = (): void => {
    const v = el('video', 'short-frame') as HTMLVideoElement;
    v.src = asset(id, 'mp4');
    v.controls = true;
    v.autoplay = true;
    v.playsInline = true;
    stage.replaceChildren(v);
    fallback.remove();
  };
  fallback.addEventListener('click', playLocal);

  let closed = false;
  const close = (): void => {
    if (closed) return;
    closed = true;
    document.removeEventListener('keydown', onKey, true);
    audio.duck(false);
    ov.destroy();
    onClose?.();
  };
  const onKey = (e: KeyboardEvent): void => { if (e.key === 'Escape') { e.preventDefault(); close(); } };
  closeBtn.addEventListener('click', close);
  document.addEventListener('keydown', onKey, true);
  playOnline();
  return close;
}
