import { el } from '../dom';
import type { GameMount, NpcGameDef } from './framework';
import { FLY_CFG, judgeTap, makeSequence, passed } from './fireflies.logic';

/** Fireflies with Rotem: they glow in a pattern, tap them in the same order to guide them into the jar. */
const mount: GameMount = (host, level, run) => {
  const cfg = FLY_CFG[level];
  const step = cfg.stepSec * (run.calm ? 1.4 : 1);
  const round = el('div', 'npcg-status', '');
  const msg = el('div', 'npcg-status fly-msg', '');
  const jar = el('div', 'fly-jar', '', cfg.rounds.map(() => el('span', 'fly-dot')));
  const flies = Array.from({ length: cfg.flies }, (_, i) => {
    const b = el('button', 'fly', '');
    b.type = 'button';
    b.setAttribute('aria-label', `גחלילית ${i + 1}`);
    b.addEventListener('pointerdown', (e) => { e.preventDefault(); tap(i); });
    return b;
  });
  const pond = el('div', `fly-pond n${cfg.flies}`, '', flies);
  host.append(round, pond, el('div', 'fly-jarrow', '', [el('span', 'lrn-sub', 'הצנצנת'), jar]), msg);

  let r = 0;
  let seq: number[] = [];
  let progress = 0;
  let misses = 0;
  let listening = false;
  let dead = false;
  const timers: number[] = [];
  const later = (fn: () => void, sec: number): void => { timers.push(window.setTimeout(fn, sec * 1000)); };

  function glow(i: number, sec: number): void {
    const f = flies[i] as HTMLElement;
    f.classList.add('lit');
    later(() => f.classList.remove('lit'), sec);
  }
  function show(): void {
    listening = false;
    progress = 0;
    round.textContent = `סבב ${r + 1} מתוך ${cfg.rounds.length}`;
    msg.textContent = 'צפו בגחליליות';
    seq.forEach((v, k) => later(() => glow(v, step * 0.8), 0.8 + k * step));
    later(() => { listening = true; msg.textContent = 'עכשיו אתם'; }, 0.8 + seq.length * step);
  }
  function startRound(): void {
    seq = makeSequence(100 + r * 13 + cfg.flies, cfg.flies, cfg.rounds[r] as number);
    show();
  }
  function tap(i: number): void {
    if (!listening || dead) return;
    glow(i, 0.25);
    const res = judgeTap(seq, progress, i);
    if (res === 'ok') { progress++; return; }
    if (res === 'wrong') {
      misses++;
      listening = false;
      progress = 0;
      if (!passed(misses, cfg, run.calm)) {
        dead = true;
        msg.textContent = 'הגחליליות התפזרו';
        later(() => run.finish({ passed: false, summary: `הובלתם ${r} מתוך ${cfg.rounds.length} סבבים` }), 0.9);
        return;
      }
      msg.textContent = 'כמעט. הנה שוב';
      later(show, 1.0);
      return;
    }
    listening = false;
    jar.children[r]?.classList.add('full');
    r++;
    if (r >= cfg.rounds.length) {
      dead = true;
      msg.textContent = 'כולן בצנצנת';
      later(() => run.finish({ passed: true, summary: `כל ${cfg.rounds.length} הסבבים, ${misses} טעויות` }), 0.9);
      return;
    }
    msg.textContent = 'יפה!';
    later(startRound, 0.9);
  }
  startRound();
  return () => {
    dead = true;
    timers.forEach((t) => window.clearTimeout(t));
  };
};

export const FIREFLIES_GAME: NpcGameDef = {
  id: 'fireflies',
  title: 'גחליליות',
  rules: 'הגחליליות מאירות בסדר מסוים. חזרו על הסדר בדיוק כדי להכניס אותן לצנצנת. מותר לטעות מעט.',
  controls: 'נוגעים בגחלילית, או לוחצים עליה בעכבר.',
  mount,
  rewards: {
    easy: { coins: 8 },
    medium: { coins: 12, food: { key: 'food_honey', name: 'טיפות דבש', n: 1 } },
    hard: { coins: 20, keepsake: { flag: 'decor.firefly_jar', name: 'צנצנת אור' } },
  },
};
