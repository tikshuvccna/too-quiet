import Phaser from 'phaser';
import type { CharKey } from '../scenes/BootScene';

/** The sprite sheets list directions in this order. */
export const DIRS = ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE'] as const;
export type Dir = (typeof DIRS)[number];

/** Ground contact point inside a 128px cell, from the art pipeline. */
export const FOOT_Y = 110 / 128;

export function dirFromVector(vx: number, vy: number): Dir | null {
  if (Math.abs(vx) < 0.01 && Math.abs(vy) < 0.01) return null;
  // angle 0 = east, increasing clockwise on screen (y down). S = 90deg.
  const a = (Math.atan2(vy, vx) * 180) / Math.PI;
  const idx = Math.round(((a - 90 + 360) % 360) / 45) % 8;
  return DIRS[idx] as Dir;
}

export interface Actor {
  sprite: Phaser.GameObjects.Sprite;
  shadow: Phaser.GameObjects.Image;
  facing: Dir;
  moving: boolean;
  char: CharKey;
}

export function createActor(scene: Phaser.Scene, char: CharKey, x: number, y: number, tint?: number, scale = 1): Actor {
  const shadow = scene.add.image(x, y, 'blob').setScale(1.1 * scale, 0.9 * scale).setAlpha(0.9);
  const sprite = scene.add.sprite(x, y, char, 'idle_S_0').setOrigin(0.5, FOOT_Y).setScale(scale);
  if (tint !== undefined) sprite.setTint(tint);
  sprite.play(`${char}:idle_S`);
  return { sprite, shadow, facing: 'S', moving: false, char };
}

/** Move the actor's visuals to (x, y) and play the right directional animation. */
export function updateActor(a: Actor, x: number, y: number, vx: number, vy: number): void {
  a.sprite.setPosition(x, y);
  a.shadow.setPosition(x, y - 2);
  a.sprite.setDepth(y);
  a.shadow.setDepth(y - 1);
  const d = dirFromVector(vx, vy);
  const moving = d !== null;
  if (d) a.facing = d;
  if (moving !== a.moving || (moving && a.sprite.anims.currentAnim?.key !== `${a.char}:walk_${a.facing}`)) {
    a.moving = moving;
    a.sprite.play(`${a.char}:${moving ? 'walk' : 'idle'}_${a.facing}`, true);
  }
}

export function setIdleFacing(a: Actor, d: Dir): void {
  a.facing = d;
  a.sprite.play(`${a.char}:idle_${d}`, true);
}
