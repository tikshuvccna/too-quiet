import type { Look, SaveStore } from '../core/save';

/** An outfit for the apprentice, sold at the tailor's. Each one is a full sprite sheet: assets/characters_v2/<id>.png. */
export interface Skin {
  id: string;
  look: Look;
  name: string;
  price: number;
}

const GIRL: Array<[string, string]> = [
  ['amber', 'אמבר'], ['sea', 'ים'], ['rose', 'ורד'], ['forest', 'יער'], ['violet', 'סגול'],
  ['sun', 'שמש'], ['night', 'לילה'], ['berry', 'פירות יער'], ['snow', 'שלג'], ['poppy', 'פרג'],
];
const BOY: Array<[string, string]> = [
  ['moss', 'אזוב'], ['navy', 'כחול עמוק'], ['rust', 'חלודה'], ['sand', 'חול'], ['plum', 'שזיף'],
  ['sky', 'שמיים'], ['ember', 'גחלת'], ['teal', 'טורקיז'], ['ash', 'אפר'], ['gold', 'זהב'],
];
const PRICES = [80, 80, 80, 90, 90, 100, 100, 110, 120, 150];

export const SKINS: Skin[] = [
  ...GIRL.map(([k, name], i): Skin => ({ id: `skin_girl_${k}`, look: 'girl', name, price: PRICES[i] as number })),
  ...BOY.map(([k, name], i): Skin => ({ id: `skin_boy_${k}`, look: 'boy', name, price: PRICES[i] as number })),
];

export const baseChar = (look: Look): string => (look === 'boy' ? 'apprentice_boy' : 'apprentice_girl');

/** The outfit worn now, or undefined for the original clothes. */
export const equippedSkin = (save: SaveStore): Skin | undefined =>
  SKINS.find((s) => s.look === save.data.look && save.hasFlag(`equip.${s.id}`));

/** The sprite sheet key of the apprentice as the player wants to see them. */
export const charKey = (save: SaveStore): string => equippedSkin(save)?.id ?? baseChar(save.data.look);
