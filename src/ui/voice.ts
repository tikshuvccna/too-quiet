import type { VoicePlayer } from './dialogue';

/**
 * Plays a recorded line when assets/voice/<id>.mp3 exists and is listed in assets/voice/index.json
 * ({"ids": ["r1.p0.narrator.0001", ...]}). Lines that are not listed stay silent: the subtitles carry them.
 */
export function createVoicePlayer(isOn: () => boolean, volume: () => number): VoicePlayer {
  const base = `${import.meta.env.BASE_URL}assets/voice/`;
  let ids: Set<string> | null = null;
  const load = fetch(`${base}index.json`)
    .then((r) => (r.ok ? r.json() : { ids: [] }))
    .then((j: { ids?: string[] }) => { ids = new Set(j.ids ?? []); })
    .catch(() => { ids = new Set(); });
  let current: HTMLAudioElement | null = null;
  return {
    play(lineId: string): void {
      void load.then(() => {
        if (!isOn() || !ids?.has(lineId)) return;
        current?.pause();
        const a = new Audio(`${base}${lineId}.mp3`);
        a.volume = Math.min(1, Math.max(0, volume()));
        current = a;
        void a.play().catch(() => { /* blocked until the first tap: the subtitles still show */ });
      });
    },
    stop(): void {
      current?.pause();
      current = null;
    },
  };
}
