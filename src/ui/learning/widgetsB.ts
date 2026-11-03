import { el } from '../dom';
import type { AtmSpec, ClientServerSpec, P2pSpec } from './types';
import {
  type AtmMode, type AtmName, type AtmState, type Job, type Power,
  POWER_BARS, SERVICE_RATE, atmBothUsed, atmInit, atmOutOfSync, atmTruth, atmWithdraw, longestWait, money,
  pickPartner, rolesSwapped, scheduleRequests,
} from './widgetLogic';
import { type Mount, Runner, checklist, envelope, lerp, node, reducedMotion, ringPositions, say, setPos, svg } from './widgetKit';

const CLIENTS = ['נחתום', 'בית ספר', 'אכסניה', 'משפחת כהן', 'משפחת לוי'];
const POWER_LABEL: Record<Power, string> = { weak: 'חלש', medium: 'בינוני', strong: 'חזק' };

function seg(labels: string[], onPick: (i: number) => void): { root: HTMLElement; set(i: number): void } {
  const btns = labels.map((l, i) => {
    const b = el('button', 'lw-seg', l);
    b.type = 'button';
    b.addEventListener('click', () => onPick(i));
    return b;
  });
  return { root: el('div', 'lw-segs', '', btns), set: (i) => btns.forEach((b, k) => b.classList.toggle('on', k === i)) };
}

function btn(label: string, cls: string, fn: () => void): HTMLButtonElement {
  const b = el('button', cls, label);
  b.type = 'button';
  b.addEventListener('click', fn);
  return b;
}

/**
 * client_server_toy. The timings come straight from the spec: the server handles 1, 2 or 5 customers a
 * second, so five at once wait about 5.5 s on a weak server and 1.5 s on a strong one. The schedule is
 * pure (scheduleRequests) and the frame loop only draws where each messenger is at time t.
 */
export const clientServerToy: Mount<ClientServerSpec> = (host, spec, api) => {
  const run = new Runner();
  const W = 160;
  const H = 110;
  const S = { x: 80, y: 55 };
  const ring = ringPositions(5, 80, 55, 57, 38);
  let power: Power = 'weak';
  let down = false;
  let busy = false;
  let next = 0;
  const label = (id: string, fb: string): string => spec.controls.find((c) => c.id === id)?.label ?? fb;
  const goals = checklist(['לקוח אחד מבקש', 'כולם יחד', 'שינוי עוצמת שרת', 'תקלה בשרת']);

  const envLayer = svg('g');
  const lines = svg('g', {}, ring.map((p) => svg('line', { x1: p.x, y1: p.y, x2: S.x, y2: S.y, class: 'lw-thread' })));
  const scene = el('div', 'lw-scene lw-scene-b', '', [svg('svg', { viewBox: `0 0 ${W} ${H}`, class: 'lw-svg' }, [lines, envLayer])]);
  const queueEl = el('span', 'lw-server-q', '');
  const server = el('div', 'lw-server', '', [el('span', 'lw-server-ic', '\u{1F33E}'), el('span', 'lw-server-t', 'הטוחן (שרת)'), queueEl]);
  Object.assign(server.style, node(S.x / W, S.y / H));
  scene.append(server);
  const clientEls = ring.map((p, i) => {
    const c = el('div', 'lw-client', '', [el('span', 'lw-client-t', CLIENTS[i] ?? ''), el('span', 'lw-client-b', '')]);
    Object.assign(c.style, node(p.x / W, p.y / H));
    scene.append(c);
    return c;
  });

  const waitEl = el('span', 'lw-wait-n', '0.0');
  const wait = el('p', 'lw-wait', '', [el('span', '', 'זמן המתנה: '), waitEl, el('span', '', ' שנ׳')]);
  const status = el('p', 'lw-status', 'לחצו על ״כולם מבקשים יחד״ וראו מה קורה עם שרת חלש.');
  status.setAttribute('aria-live', 'polite');

  const bars = ['מעבד (CPU)', 'זיכרון (RAM)', 'אחסון (Storage)'].map((t) => {
    const fill = el('i', 'lw-bar-fill');
    return { fill, row: el('div', 'lw-bar', '', [el('span', 'lw-bar-t', t), el('span', 'lw-bar-track', '', [fill])]) };
  });
  const paintBars = (): void => POWER_BARS[power].forEach((v, i) => { const b = bars[i]; if (b) b.fill.style.width = `${v * 100}%`; });

  const pw = seg((['weak', 'medium', 'strong'] as Power[]).map((p) => POWER_LABEL[p]), (i) => {
    power = (['weak', 'medium', 'strong'] as Power[])[i] ?? 'weak';
    pw.set(i);
    paintBars();
    goals.tick(2);
    say(status, `עוצמת השרת: ${POWER_LABEL[power]}. מטפל ב-${SERVICE_RATE[power]} לקוחות בכל שנייה.`);
    check();
  });
  pw.set(0);
  paintBars();

  const bOne = btn(label('one', 'לקוח אחד מבקש'), 'btn', () => { goals.tick(0); void batch([next++ % 5]); });
  const bAll = btn(label('all', 'כולם מבקשים יחד'), 'btn primary', () => { goals.tick(1); void batch([0, 1, 2, 3, 4]); });
  const bFail = btn('תקלה בשרת', 'btn', () => {
    down = !down;
    server.classList.toggle('down', down);
    bFail.textContent = down ? 'תקנו את השרת' : 'תקלה בשרת';
    if (down) goals.tick(3);
    say(status, down ? 'הטוחן קפא. נסו לבקש משהו.' : 'השרת חזר לעבוד.', down ? 'warn' : 'good');
    check();
  });
  const buttons = [bOne, bAll, bFail];

  function check(): void {
    if (goals.all()) api.done();
  }

  async function batch(who: number[]): Promise<void> {
    if (busy) return;
    busy = true;
    buttons.forEach((b) => { b.disabled = true; });
    const jobs: Job[] = scheduleRequests(who.map(() => 0), SERVICE_RATE[power], undefined, down);
    const envs = jobs.map((j) => envelope(j.failed));
    envs.forEach((e) => { e.style.display = 'none'; envLayer.append(e); });
    const end = longestWait(jobs);
    const finish = (): void => {
      envs.forEach((e) => e.remove());
      waitEl.textContent = end.toFixed(1);
      queueEl.textContent = '';
      server.classList.remove('busy');
      who.forEach((c, k) => {
        const badge = clientEls[c]?.querySelector('.lw-client-b');
        if (badge) badge.textContent = jobs[k]?.failed ? 'אין שירות' : '✓';
        clientEls[c]?.classList.toggle('lost', !!jobs[k]?.failed);
        clientEls[c]?.classList.toggle('ok', !jobs[k]?.failed);
      });
      say(status, down
        ? 'כל השליחים חזרו בידיים ריקות. הלקוחות לא יכולים לעשות כלום בלי השרת הזה.'
        : who.length === 1
          ? 'שליח אחד רץ לשרת ובחזרה: מי שמבקש הוא הלקוח, מי שנותן הוא השרת.'
          : `זמן ההמתנה הארוך ביותר: ${end.toFixed(1)} שנ׳. ${power === 'strong' ? 'שרת חזק משרת את כולם כמעט יחד.' : 'שרת חלש יוצר תור. לכן שרתים הם בדרך כלל מחשבים חזקים.'}`, down ? 'warn' : 'good');
      buttons.forEach((b) => { b.disabled = false; });
      busy = false;
      check();
    };
    who.forEach((c) => { const cl = clientEls[c]; cl?.classList.remove('ok', 'lost'); const b = cl?.querySelector('.lw-client-b'); if (b) b.textContent = ''; });
    say(status, '', '');
    if (reducedMotion()) {
      finish();
      return;
    }
    let t = 0;
    await new Promise<void>((resolve) => {
      run.loop((dt) => {
        t += dt;
        let waiting = 0;
        let serving = false;
        jobs.forEach((j, k) => {
          const env = envs[k];
          const p = ring[who[k] ?? 0];
          if (!env || !p) return;
          const dest = { x: lerp(p.x, S.x, 0.7), y: lerp(p.y, S.y, 0.7) };
          let pos: { x: number; y: number } | null = null;
          if (t < j.arrive) pos = { x: lerp(p.x, dest.x, t / (j.arrive - j.start)), y: lerp(p.y, dest.y, t / (j.arrive - j.start)) };
          else if (t < j.serviceEnd || (j.failed && t < j.arrive + 0.1)) {
            pos = dest;
            if (t < j.serviceStart) waiting++;
            else serving = true;
          } else if (t < j.back) {
            const f = (t - j.serviceEnd) / (j.back - j.serviceEnd);
            pos = { x: lerp(dest.x, p.x, f), y: lerp(dest.y, p.y, f) };
            env.classList.add('back');
          }
          env.style.display = pos ? '' : 'none';
          if (pos) setPos(env, pos.x, pos.y);
        });
        waitEl.textContent = Math.min(t, end).toFixed(1);
        queueEl.textContent = waiting > 0 ? `בתור: ${waiting}` : '';
        server.classList.toggle('busy', serving);
        if (t >= end) { resolve(); return false; }
        return true;
      });
    });
    finish();
  }

  host.append(
    scene,
    el('div', 'lw-controls', '', [bOne, bAll, bFail]),
    el('div', 'lw-powerrow', '', [el('span', 'lw-lbl', label('power', 'עוצמת השרת') + ':'), pw.root]),
    el('div', 'lw-bars', '', bars.map((b) => b.row)),
    wait,
    status,
    goals.root,
  );
  return () => run.dispose();
};

/**
 * atm_toy. Each mode is its own run that starts from 500. Switching mode resets, so the two stories are
 * never mixed. api.done fires once the learner has tried both withdrawals in both modes.
 */
export const atmToy: Mount<AtmSpec> = (host, spec, api) => {
  const run = new Runner();
  const W = 160;
  const H = 120;
  const pos = { server: { x: 80, y: 20 }, metula: { x: 36, y: 90 }, eilat: { x: 124, y: 90 } };
  let state: AtmState = atmInit('connected');
  let busy = false;
  const triedBoth: Record<AtmMode, boolean> = { connected: false, offline: false };

  const envLayer = svg('g');
  const mkLine = (a: { x: number; y: number }): SVGLineElement => svg('line', { x1: a.x, y1: a.y, x2: pos.server.x, y2: pos.server.y, class: 'lw-thread' });
  const lineM = mkLine(pos.metula);
  const lineE = mkLine(pos.eilat);
  const cut = svg('text', { x: 80, y: 56, class: 'lw-cut' });
  cut.textContent = '✕ אין רשת';
  const scene = el('div', 'lw-scene lw-scene-c', '', [svg('svg', { viewBox: `0 0 ${W} ${H}`, class: 'lw-svg' }, [lineM, lineE, cut, envLayer])]);

  const bal = (cls: string): HTMLElement => el('span', `lw-money ${cls}`);
  const serverBal = bal('sv');
  const server = el('div', 'lw-box lw-box-server', '', [el('span', 'lw-box-t', '\u{1F3E6} שרת הבנק'), serverBal]);
  Object.assign(server.style, node(pos.server.x / W, pos.server.y / H));
  const boxes: Record<AtmName, { box: HTMLElement; bal: HTMLElement }> = {
    metula: mkBox('כספומט מטולה', pos.metula),
    eilat: mkBox('כספומט אילת', pos.eilat),
  };
  function mkBox(title: string, p: { x: number; y: number }): { box: HTMLElement; bal: HTMLElement } {
    const b = bal('');
    const box = el('div', 'lw-box', '', [el('span', 'lw-box-t', title), b]);
    Object.assign(box.style, node(p.x / W, p.y / H));
    return { box, bal: b };
  }
  scene.append(server, boxes.metula.box, boxes.eilat.box);

  const status = el('p', 'lw-status', '');
  status.setAttribute('aria-live', 'polite');
  const truth = el('p', 'lw-truth', '');
  const buttons: HTMLButtonElement[] = [];
  const label = (i: number, fb: string): string => spec.buttons[i] ?? fb;
  const modeLabel = (id: AtmMode, fb: string): string => spec.modes.find((m) => m.id === id)?.label ?? fb;
  const modeSeg = seg([modeLabel('connected', 'מחוברים לשרת הבנק'), modeLabel('offline', 'בלי רשת (המחשה)')], (i) => setMode(i === 0 ? 'connected' : 'offline'));

  function setMode(m: AtmMode): void {
    if (busy) return;
    state = atmInit(m);
    modeSeg.set(m === 'connected' ? 0 : 1);
    say(status, m === 'connected' ? 'הכספומטים מחוברים לאותו שרת. נסו למשוך במטולה ואחר כך באילת.' : 'בלי רשת כל כספומט זוכר רק את עצמו. נסו אותן שתי משיכות.');
    paint();
  }

  function paint(): void {
    const on = state.mode === 'connected';
    scene.classList.toggle('offline', !on);
    cut.style.display = on ? 'none' : '';
    boxes.metula.bal.replaceChildren(moneyEl(state.shown.metula));
    boxes.eilat.bal.replaceChildren(moneyEl(state.shown.eilat));
    serverBal.replaceChildren(on ? moneyEl(atmTruth(state)) : document.createTextNode('לא מחובר'));
    server.classList.toggle('dim', !on);
    truth.replaceChildren(el('span', '', 'היתרה האמיתית של החשבון: '), moneyEl(atmTruth(state)));
    truth.classList.toggle('mismatch', atmOutOfSync(state));
  }

  function moneyEl(n: number): HTMLElement {
    const s = el('span', n < 0 ? 'neg' : '', money(n));
    s.dir = 'ltr';
    return s;
  }

  async function withdraw(atm: AtmName, amount: number): Promise<void> {
    if (busy) return;
    busy = true;
    buttons.forEach((b) => { b.disabled = true; });
    const connected = state.mode === 'connected';
    if (connected) {
      const env = envelope();
      envLayer.append(env);
      const a = pos[atm];
      await run.tween(550, (p) => setPos(env, lerp(a.x, pos.server.x, p), lerp(a.y, pos.server.y, p)));
      env.remove();
      state = atmWithdraw(state, atm, amount);
      serverBal.replaceChildren(moneyEl(atmTruth(state)));
      const back = (['metula', 'eilat'] as AtmName[]).map(() => envelope());
      back.forEach((e) => envLayer.append(e));
      await run.tween(550, (p) => (['metula', 'eilat'] as AtmName[]).forEach((n, k) => {
        const e = back[k];
        if (e) setPos(e, lerp(pos.server.x, pos[n].x, p), lerp(pos.server.y, pos[n].y, p));
      }));
      back.forEach((e) => e.remove());
    } else {
      boxes[atm].box.classList.add('flash');
      await run.wait(450);
      boxes[atm].box.classList.remove('flash');
      state = atmWithdraw(state, atm, amount);
    }
    paint();
    if (atmBothUsed(state)) triedBoth[state.mode] = true;
    say(status, atmMessage(), atmOutOfSync(state) ? 'warn' : 'good');
    busy = false;
    buttons.forEach((b) => { b.disabled = false; });
    if (triedBoth.connected && triedBoth.offline) {
      api.done();
    } else if (triedBoth[state.mode]) {
      status.textContent += state.mode === 'connected' ? ' עכשיו נסו גם את מצב ״בלי רשת״.' : ' עכשיו נסו גם את מצב ״מחוברים לשרת הבנק״.';
    }
  }

  function atmMessage(): string {
    const t = atmTruth(state);
    if (state.mode === 'connected') {
      return `השרת עדכן את שני הכספומטים בבת אחת: ${money(t)}. לא משנה מאיפה מושכים.`;
    }
    return atmOutOfSync(state)
      ? `כל כספומט מכיר רק את עצמו. סך המשיכות ${money(state.withdrawn)}, והיתרה האמיתית צריכה להיות ${money(t)}. השרת לא ידע.`
      : 'כספומט אחד ידע רק על עצמו.';
  }

  buttons.push(
    btn(label(0, 'משיכה של 1,000 במטולה'), 'btn primary', () => { void withdraw('metula', 1000); }),
    btn(label(1, 'משיכה של 500 באילת'), 'btn primary', () => { void withdraw('eilat', 500); }),
  );
  const reset = btn(label(2, 'איפוס'), 'btn', () => setMode(state.mode));

  host.append(modeSeg.root, scene, truth, el('div', 'lw-controls', '', [...buttons, reset]), status);
  setMode('connected');
  return () => run.dispose();
};

type PanelKind = 'p2p' | 'cs';

/**
 * p2p_vs_cs_toy. On wide screens both boards sit side by side, on a phone two tabs show one at a time.
 * Interpretation of "tap a computer" in peer-to-peer: the computer you tap becomes the client and a partner
 * (the previous asker when possible) becomes the server, so the roles visibly swap between taps.
 * The goal (api.done) is a checklist of five things to try.
 */
export const p2pVsCsToy: Mount<P2pSpec> = (host, _spec, api) => {
  const run = new Runner();
  const W = 160;
  const H = 100;
  const goals = checklist(['עמית: תפקידים מתחלפים', 'לקוח-שרת: בקשה', 'כמה זה עולה', 'כיבוי מחשב', 'כיבוי השרת']);
  let cost = false;
  let lastClient: number | null = null;
  const clientsSeen = new Set<number>();
  const serversSeen = new Set<number>();
  const finish = (): void => { if (goals.all()) api.done(); };

  const panels = (['p2p', 'cs'] as PanelKind[]).map((kind) => build(kind));

  function build(kind: PanelKind): { root: HTMLElement; setCost(): void; reset(): void } {
    const ring = ringPositions(5, 80, kind === 'cs' ? 52 : 50, kind === 'cs' ? 58 : 50, kind === 'cs' ? 36 : 36);
    const on = [true, true, true, true, true];
    let serverOn = true;
    let busy = false;
    const lineEls: SVGLineElement[] = [];
    const lines = svg('g');
    if (kind === 'p2p') {
      for (let a = 0; a < 5; a++) for (let b = a + 1; b < 5; b++) lines.append(svg('line', { x1: ring[a]?.x ?? 0, y1: ring[a]?.y ?? 0, x2: ring[b]?.x ?? 0, y2: ring[b]?.y ?? 0, class: 'lw-thread soft' }));
    } else {
      ring.forEach((p) => { const l = svg('line', { x1: p.x, y1: p.y, x2: 80, y2: 52, class: 'lw-thread' }); lineEls.push(l); lines.append(l); });
    }
    const envLayer = svg('g');
    const scene = el('div', 'lw-scene lw-scene-d', '', [svg('svg', { viewBox: `0 0 ${W} ${H}`, class: 'lw-svg' }, [lines, envLayer])]);
    const status = el('p', 'lw-status', kind === 'p2p' ? 'לחצו על מחשב: הוא מבקש קובץ ממחשב אחר.' : 'לחצו על מחשב: הוא מבקש מהשרת.');
    status.setAttribute('aria-live', 'polite');

    const comps = ring.map((p, i) => {
      const tag = el('span', 'lw-tag', '');
      const b = el('button', 'lw-comp', '', [tag, el('span', 'lw-comp-ic', '\u{1F4BB}'), el('span', 'lw-comp-t', `מחשב ${i + 1}`)]);
      b.type = 'button';
      Object.assign(b.style, node(p.x / W, p.y / H));
      b.addEventListener('click', () => { void tap(i); });
      scene.append(b);
      return { b, tag };
    });

    let serverBox: HTMLElement | null = null;
    if (kind === 'cs') {
      const bars = el('div', 'lw-mini-bars', '', ['CPU', 'RAM', 'Storage'].map((t) => el('span', 'lw-mini', t, [el('i')])));
      serverBox = el('div', 'lw-server small', '', [el('span', 'lw-server-ic', '\u{1F5A5}️'), el('span', 'lw-server-t', 'שרת'), bars]);
      Object.assign(serverBox.style, node(80 / W, 52 / H));
      scene.append(serverBox);
    }
    const caption = el('p', 'lw-caption', kind === 'p2p' ? '5 מחשבים רגילים, בלי שרת ייעודי.' : '5 מחשבים ועוד שרת חזק.');

    function clearTags(): void { comps.forEach((c) => { c.tag.textContent = ''; c.tag.className = 'lw-tag'; }); }
    function repaint(): void {
      comps.forEach((c, i) => {
        c.b.classList.toggle('off', !on[i]);
        c.b.setAttribute('aria-label', `מחשב ${i + 1}${on[i] ? '' : ' (כבוי)'}`);
      });
      serverBox?.classList.toggle('down', !serverOn);
      lineEls.forEach((l, i) => l.classList.toggle('dead', !serverOn || !on[i]));
    }

    async function fly(from: { x: number; y: number }, to: { x: number; y: number }, failed: boolean): Promise<void> {
      const e = envelope(failed);
      envLayer.append(e);
      await run.tween(520, (p) => setPos(e, lerp(from.x, to.x, p), lerp(from.y, to.y, p)));
      e.remove();
    }

    async function tap(i: number): Promise<void> {
      if (busy) return;
      const me = ring[i];
      if (!me) return;
      if (!on[i]) { say(status, 'המחשב הזה כבוי.', 'warn'); return; }
      busy = true;
      clearTags();
      if (kind === 'p2p') {
        const j = pickPartner(on, i, lastClient);
        const other = j === null ? null : ring[j];
        if (j === null || !other) { say(status, 'אין עם מי לדבר: כל השאר כבויים.', 'warn'); busy = false; return; }
        comps[i]?.tag.append(document.createTextNode('לקוח'));
        comps[i]?.tag.classList.add('client');
        comps[j]?.tag.append(document.createTextNode('שרת'));
        comps[j]?.tag.classList.add('server');
        clientsSeen.add(i);
        serversSeen.add(j);
        say(status, `מחשב ${i + 1} מבקש קובץ ממחשב ${j + 1}: עכשיו הוא לקוח וההוא שרת. בהמשך יוכלו להתחלף.`);
        await fly(me, other, false);
        await fly(other, me, false);
        lastClient = i;
        if (rolesSwapped(clientsSeen, serversSeen)) goals.tick(0);
        if (rolesSwapped(clientsSeen, serversSeen)) say(status, `כל מחשב יכול להיות גם לקוח וגם שרת: זה עמית לעמית.`, 'good');
      } else {
        const sv = { x: 80, y: 52 };
        const target = { x: lerp(me.x, sv.x, 0.72), y: lerp(me.y, sv.y, 0.72) };
        comps[i]?.tag.append(document.createTextNode('לקוח'));
        comps[i]?.tag.classList.add('client');
        serverBox?.classList.add('flagged');
        await fly(me, target, !serverOn);
        if (serverOn) await fly(target, me, false);
        else await fly(target, me, true);
        goals.tick(1);
        say(status, serverOn ? 'הבקשה עברה לשרת וחזרה. המחשבים תמיד לקוחות, והשרת תמיד שרת.' : 'השרת כבוי: אף לקוח לא קיבל שירות.', serverOn ? 'good' : 'warn');
      }
      busy = false;
      finish();
    }

    const offOne = btn('כבו מחשב אחד', 'btn', () => {
      const i = lastClient !== null && on[lastClient] ? lastClient : on[2] ? 2 : on.indexOf(true);
      if (i < 0) return;
      on[i] = false;
      clearTags();
      repaint();
      goals.tick(3);
      say(status, kind === 'p2p'
        ? `מחשב ${i + 1} כבוי. האחרים ממשיכים לדבר זה עם זה. רק קבצים שהיו רק עליו לא זמינים.`
        : `מחשב ${i + 1} כבוי. שאר הלקוחות ממשיכים לעבוד מול השרת.`, 'warn');
      finish();
    });
    const offServer = kind === 'cs' ? btn('כבו את השרת', 'btn', () => {
      serverOn = false;
      repaint();
      goals.tick(4);
      say(status, 'השרת כבוי: כל הלקוחות מאבדים שירות. אין מי שיענה להם.', 'warn');
      finish();
    }) : null;
    const allOn = btn('הדליקו הכול', 'btn', () => reset());

    function reset(): void {
      on.fill(true);
      serverOn = true;
      lastClient = null;
      clearTags();
      repaint();
      say(status, 'הכול דולק שוב.', 'good');
    }

    const root = el('section', 'lw-panel', '', [
      el('h5', 'lw-panel-t', kind === 'p2p' ? 'עמית לעמית' : 'לקוח-שרת'),
      scene,
      caption,
      el('div', 'lw-controls', '', [offOne, offServer, allOn]),
      status,
    ]);
    repaint();
    return { root, setCost: () => root.classList.toggle('show-cost', cost), reset };
  }

  const costBtn = btn('כמה זה עולה?', 'btn', () => {
    cost = !cost;
    costBtn.classList.toggle('on', cost);
    panels.forEach((p) => p.setCost());
    if (cost) goals.tick(2);
    finish();
  });
  const tabs = seg(['עמית לעמית', 'לקוח-שרת'], (i) => showTab(i));
  tabs.root.classList.add('lw-tabs');
  function showTab(i: number): void {
    tabs.set(i);
    panels.forEach((p, k) => p.root.classList.toggle('is-active', k === i));
  }
  host.append(tabs.root, el('div', 'lw-panels', '', panels.map((p) => p.root)), el('div', 'lw-controls', '', [costBtn]), goals.root);
  showTab(0);
  return () => run.dispose();
};
