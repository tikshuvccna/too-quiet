import type { Level } from './types';

export type Model = 'p2p' | 'cs';

export interface WiringRound {
  need: Model;
  text: string;
  devices: string[];
  why: string;
}

export interface WiringData {
  id: string;
  title: string;
  intro: string;
  howTo: string[];
  levels: Record<Level, { attempts: number; rounds: WiringRound[] }>;
}

/** The server node has index -1 in a link key. Keys are always "low-high". */
export const SERVER = -1;
export const linkKey = (a: number, b: number): string => (a < b ? `${a}-${b}` : `${b}-${a}`);

export interface Wiring { server: boolean; links: Set<string> }

export type Verdict =
  | { ok: true }
  | { ok: false; code: 'extra_server' | 'no_server' | 'missing' | 'extra_links' | 'nothing'; message: string; missing?: string[] };

/** Number of threads the right network needs. */
export function threadsNeeded(round: WiringRound): number {
  const n = round.devices.length;
  return round.need === 'cs' ? n : (n * (n - 1)) / 2;
}

/**
 * The rule is the lesson: equal devices share directly (every device to every other, no server);
 * a server in the middle serves clients (every client to the server, and clients do not talk directly).
 */
export function evaluate(round: WiringRound, w: Wiring): Verdict {
  const n = round.devices.length;
  if (w.links.size === 0) return { ok: false, code: 'nothing', message: 'עוד אין חוטים. חברו את המכשירים ושלחו שוב.' };
  if (round.need === 'p2p') {
    if (w.server) return { ok: false, code: 'extra_server', message: 'המכשירים כאן שווים, ואין מה שמנהל אותם. שרת באמצע הוא מיותר ויקר: הסירו אותו וחברו את המכשירים ישירות.' };
    const missing: string[] = [];
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) if (!w.links.has(linkKey(i, j))) missing.push(`${round.devices[i]} ו${round.devices[j]}`);
    if (missing.length) return { ok: false, code: 'missing', missing, message: `חסר חיבור ישיר בין ${missing[0]}. בעמית לעמית כל מכשיר מדבר ישר עם כל מכשיר אחר.` };
    return { ok: true };
  }
  if (!w.server) return { ok: false, code: 'no_server', message: 'המידע הזה צריך להיות במקום אחד. בלי שרת הלקוחות לא יודעים למי לפנות: הציבו שרת.' };
  const missing: string[] = [];
  for (let i = 0; i < n; i++) if (!w.links.has(linkKey(i, SERVER))) missing.push(round.devices[i] as string);
  if (missing.length) return { ok: false, code: 'missing', missing, message: `${missing[0]} לא מחובר לשרת, וההודעה שלו לא תגיע.` };
  const direct = [...w.links].some((k) => !k.startsWith('-1-') && !k.endsWith('--1'));
  if (direct) return { ok: false, code: 'extra_links', message: 'בלקוח-שרת הלקוחות פונים לשרת ולא זה לזה. נתקו את החוטים שבין הלקוחות.' };
  return { ok: true };
}

/** Place devices on an arc (or the whole ring) around the centre; the server sits in the middle. Positions are 0..1. */
export function layout(n: number): Array<{ x: number; y: number }> {
  return Array.from({ length: n }, (_, i) => {
    const a = -Math.PI / 2 + (i / n) * Math.PI * 2;
    return { x: 0.5 + Math.cos(a) * 0.36, y: 0.52 + Math.sin(a) * 0.34 };
  });
}
