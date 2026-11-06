import hintsJson from '../../content/he/world/hints.json';

/** Lines and found objects that are real hints (they get the gold "רמז" badge). Plain chat is not listed. */
export interface HintData { lines: string[]; objects: string[] }

export const HINTS: HintData = hintsJson as unknown as HintData;

const LINE_SET = new Set(HINTS.lines);
const OBJECT_SET = new Set(HINTS.objects);

export const isHintLine = (lineId: string | undefined): boolean => !!lineId && LINE_SET.has(lineId);
export const isHintObject = (houseId: string, objectId: string): boolean => OBJECT_SET.has(`${houseId}:${objectId}`);
