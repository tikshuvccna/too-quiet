import { audio } from '../audio/audio';
import { ITEMS_IN_OBJECT } from '../content';
import { perksOf } from '../game/perks';
import type { GameContext } from '../game/context';
import { clueFlag, cluesIn } from '../world/secrets';
import { openActivity } from './houseActivities';
import { ACTIVITIES, doneFlag, grantFind } from './houseActivitiesLogic';
import { showClue } from './secretsUi';
import { shortById, openShort } from './shorts';
import houseShortsJson from '../../content/he/world/house_shorts.json';

const HOUSE_SHORTS = (houseShortsJson as { shorts: Record<string, string> }).shorts;
const SHORT_COINS = 3;

/**
 * What an inspected object adds after its own text: the clue of a secret sequence (re-readable), or a small
 * one-time find when the object holds no collectible. Call inside the controller's modal.
 */
export async function afterInspect(ctx: GameContext, houseId: string, objId: string): Promise<void> {
  const clues = cluesIn(houseId, objId);
  for (const c of clues) {
    const first = !ctx.save.hasFlag(clueFlag(c.id));
    if (first) {
      ctx.save.setFlag(clueFlag(c.id));
      ctx.hud.toast(`נמצא: ${c.clue.title}`, 'clue', 4200, true);
    }
    ctx.dialogue.close();
    await showClue(c, first);
    if (first) ctx.hud.toast(c.hintAfterClue, 'clue', 5200, true);
  }
  await offerShort(ctx, `${houseId}:${objId}`);
  if (clues.length || (ITEMS_IN_OBJECT[`${houseId}:${objId}`] ?? []).length) return;
  const line = grantFind(ctx.save, houseId, objId, perksOf(ctx.save).coinMul);
  if (line) {
    audio.sfx('pickup');
    ctx.hud.toast(line, 'good', 3600);
  }
}

export const activityTargetId = (houseId: string): string => `act:${houseId}`;

export function activityLabel(ctx: GameContext, houseId: string): string | null {
  const a = ACTIVITIES[houseId];
  if (!a) return null;
  return ctx.save.hasFlag(doneFlag(houseId)) ? `${a.spot} (בוצע)` : a.spot;
}

/** Use of the activity marker: opens the activity, or only reminds what it taught when it is done. */
export async function useActivity(ctx: GameContext, houseId: string): Promise<void> {
  const a = ACTIVITIES[houseId];
  if (!a) return;
  if (ctx.save.hasFlag(doneFlag(houseId))) {
    await ctx.dialogue.say([{ speaker: '', text: a.done }]);
    return;
  }
  await openActivity(houseId, ctx.save);
}

/** Some objects hold a Short from the channel that explains the idea: offered after the object's own text. */
async function offerShort(ctx: GameContext, key: string): Promise<void> {
  const id = HOUSE_SHORTS[key];
  const s = id ? shortById(id) : undefined;
  if (!id || !s) return;
  const flag = `short.${id}`;
  const seen = ctx.save.hasFlag(flag);
  ctx.dialogue.close();
  const yes = await ctx.dialogue.choose({ speaker: '', text: `על החפץ הזה יש סרטון קצר: ${s.title}. לצפות?${seen ? ' (כבר ראיתם)' : ''}` }, [
    { text: 'כן, בשמחה', value: 'yes' },
    { text: 'אולי אחר כך', value: 'no' },
  ]);
  if (yes !== 'yes') return;
  await new Promise<void>((res) => openShort(id, res));
  if (!seen) {
    ctx.save.setFlag(flag);
    ctx.save.data.coins += SHORT_COINS;
    ctx.save.save();
    ctx.hud.toast(`נוספו ${SHORT_COINS} מטבעות על הצפייה`, 'good', 3200);
  }
}
