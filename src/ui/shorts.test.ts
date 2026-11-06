import { describe, expect, it } from 'vitest';
import { existsSync } from 'node:fs';
import { SHORTS, embedUrl, youtubeId } from './shorts';

describe('shorts', () => {
  it('reads the video id from the channel links', () => {
    expect(youtubeId('https://youtube.com/shorts/EQqfUSg7lDU')).toBe('EQqfUSg7lDU');
    expect(youtubeId('https://www.youtube.com/watch?v=VR8bbiaSYpg&t=3')).toBe('VR8bbiaSYpg');
    expect(youtubeId('https://youtu.be/gBvT9uR5nQw')).toBe('gBvT9uR5nQw');
    expect(youtubeId('not a link')).toBeNull();
  });

  it('embeds without tracking cookies', () => {
    expect(embedUrl('https://youtube.com/shorts/EQqfUSg7lDU')).toContain('youtube-nocookie.com/embed/EQqfUSg7lDU');
  });

  it('every short has a link, a title and a local fallback copy', () => {
    expect(SHORTS.length).toBeGreaterThanOrEqual(15);
    for (const s of SHORTS) {
      expect(youtubeId(s.youtube)).not.toBeNull();
      expect(s.title.length).toBeGreaterThan(3);
      expect(existsSync(`public/assets/shorts/${s.id}.mp4`)).toBe(true);
      expect(existsSync(`public/assets/shorts/${s.id}.jpg`)).toBe(true);
    }
  });
});
