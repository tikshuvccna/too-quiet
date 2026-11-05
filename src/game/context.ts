import type { SaveStore } from '../core/save';
import type { Session } from '../core/session';
import type { DialogueUI } from '../ui/dialogue';
import type { Hud } from '../ui/hud';
import type { Joystick } from '../ui/joystick';
import type { SkyHead } from '../ui/skyHead';

/** Everything the scenes and the controller share. Created once in main.ts. */
import type { QualityManager } from '../core/quality';

export interface GameContext {
  save: SaveStore;
  session: Session;
  hud: Hud;
  dialogue: DialogueUI;
  joystick: Joystick;
  head: SkyHead;
  quality: QualityManager;
  /** Texture keys that real (Blender) art provides; scenes fall back to generated placeholders otherwise. */
  art: Set<string>;
  /** Set by the controller while a lesson, quiz, mini-game or dialogue owns the screen. */
  modal: boolean;
}

export const CTX_KEY = 'ctx';
