import Phaser from 'phaser';

interface AnimDef { frames: string[]; frameRate: number; repeat: number }

/** Loads one character sheet on demand (outfits are not loaded at start, to keep the first load small). */
export function ensureCharSheet(scene: Phaser.Scene, key: string): Promise<boolean> {
  if (scene.textures.exists(key) && scene.anims.exists(`${key}:idle_S`)) return Promise.resolve(true);
  return new Promise((resolve) => {
    const base = import.meta.env.BASE_URL;
    scene.load.atlas(key, `${base}assets/characters_v2/${key}.png`, `${base}assets/characters_v2/${key}.json`);
    scene.load.json(`${key}:anims`, `${base}assets/characters_v2/${key}.json`);
    scene.load.once(Phaser.Loader.Events.COMPLETE, () => {
      if (!scene.textures.exists(key)) { resolve(false); return; }
      const data = scene.cache.json.get(`${key}:anims`) as { anims?: Record<string, AnimDef> } | undefined;
      for (const [name, a] of Object.entries(data?.anims ?? {})) {
        const animKey = `${key}:${name}`;
        if (!scene.anims.exists(animKey)) scene.anims.create({ key: animKey, frames: a.frames.map((f) => ({ key, frame: f })), frameRate: a.frameRate, repeat: a.repeat });
      }
      resolve(true);
    });
    scene.load.start();
  });
}
