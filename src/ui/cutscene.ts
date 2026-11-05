import { audio } from '../audio/audio';
import { el, uiRoot } from './dom';

/**
 * Short illustrated clips for the big moments. A clip exists only when its file is listed in
 * assets/cutscenes/index.json, so the game works the same with none, some or all of them.
 */
let manifest: Promise<Set<string>> | null = null;

function ids(): Promise<Set<string>> {
  manifest ??= fetch(`${import.meta.env.BASE_URL}assets/cutscenes/index.json`)
    .then((r) => (r.ok ? (r.json() as Promise<{ ids?: string[] }>) : { ids: [] }))
    .then((j) => new Set(j.ids ?? []))
    .catch(() => new Set<string>());
  return manifest;
}

export async function hasCutscene(id: string): Promise<boolean> {
  return (await ids()).has(id);
}

/** Plays the clip full screen with a skip button. Resolves true when a clip was shown, false when there is none. */
export async function playCutscene(id: string): Promise<boolean> {
  if (!(await hasCutscene(id))) return false;
  await new Promise<void>((resolve) => {
    const video = el('video', 'cutvid-video');
    video.src = `${import.meta.env.BASE_URL}assets/cutscenes/${id}.mp4`;
    video.autoplay = true;
    video.playsInline = true;
    video.volume = audio.settings.sfxOn ? Math.min(1, audio.settings.sfxVol + 0.1) : 0;
    const skip = el('button', 'btn cutvid-skip', 'דלגו');
    skip.type = 'button';
    const wrap = el('div', 'screen cutvid', '', [video, skip]);
    uiRoot().append(wrap);
    // the opening clip is silent: the opening theme plays over it; other clips pause the music
    const popMood = id === 'cs_valley_arrival' ? audio.pushOverlay('intro') : null;
    if (!popMood) audio.hold(true);
    let done = false;
    const end = (): void => {
      if (done) return;
      done = true;
      video.pause();
      wrap.remove();
      if (popMood) popMood();
      else audio.hold(false);
      resolve();
    };
    skip.addEventListener('click', end);
    video.addEventListener('ended', end);
    video.addEventListener('error', end);
    void video.play().catch(() => {
      // autoplay with sound can be refused: try muted rather than lose the clip
      video.muted = true;
      void video.play().catch(end);
    });
  });
  return true;
}
