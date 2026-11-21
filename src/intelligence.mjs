/** @typedef {import('./household').Household} Household */
/** @typedef {import('./household').FamilyPlan} FamilyPlan */
/** @typedef {import('./household').PlanVersion} PlanVersion */

// Read-only projections over one authorized household snapshot.
// Calendar dates and wall-clock times have already been validated by the store.
const planFields = /** @type {const} */ (['title', 'date', 'time', 'person']);

export const modelCapabilities = Object.freeze({ available: false, reason: 'model_unavailable' });

/** Input is untrusted source content. This interface has no tools, credentials or write access.
 * @param {{text: string}} _request
 */
export async function interpretSource(_request) {
  return { status: 'unavailable', reason: modelCapabilities.reason, candidates: [] };
}

function normalized(value = '') {
  return value.trim().toLowerCase().replace(/\s+/gu, ' ');
}

/** @param {Household} state
 * @param {{id?: string, text: string}} source */
export function findDuplicates(state, source) {
  const text = normalized(source.text);
  return text ? state.sources.filter(other => other.id !== source.id && normalized(other.text) === text) : [];
}

/** @param {PlanVersion} previous
 * @param {PlanVersion} current */
export function describeChanges(previous, current) {
  return planFields.filter(field => previous[field] !== current[field])
    .map(field => ({ field, before: previous[field] || '', after: current[field] || '' }));
}

function localDay() {
  const now = new Date();
  return [now.getFullYear(), String(now.getMonth() + 1).padStart(2, '0'), String(now.getDate()).padStart(2, '0')].join('-');
}

/** @param {string} day */
function nextDay(day) {
  const next = new Date(day + 'T00:00:00Z');
  next.setUTCDate(next.getUTCDate() + 1);
  return next.toISOString().slice(0, 10);
}

/** @param {FamilyPlan[]} plans */
function sortedPlans(plans) {
  return [...plans].sort((a, b) => a.date.localeCompare(b.date)
    || (a.time || '24:00').localeCompare(b.time || '24:00')
    || a.title.localeCompare(b.title) || a.id.localeCompare(b.id));
}

/** @param {FamilyPlan[]} plans */
function conflictsFor(plans) {
  /** @type {Map<string, FamilyPlan[]>} */
  const slots = new Map();
  const conflicts = [];
  for (const plan of plans) {
    const { person, date, time } = plan;
    if (!person || !date || !time) continue;
    const key = JSON.stringify([person, date, time]);
    const others = slots.get(key) ?? [];
    for (const other of others) conflicts.push({person, date, time, plans: [other, plan]});
    others.push(plan);
    slots.set(key, others);
  }
  return conflicts;
}

/** @param {Household} state */
export function buildBriefing(state, today = localDay()) {
  const plans = sortedPlans(state.plans);
  const review = state.sources.filter(source => source.status === 'pending');
  const tasks = state.tasks ?? [];
  const changes = [];
  for (const plan of plans) {
    const previous = plan.history?.at(-1);
    if (!previous) continue;
    const fields = describeChanges(previous, plan);
    if (fields.length) changes.push({plan, fields});
  }
  return {
    today: plans.filter(plan => plan.date === today),
    upcoming: plans.filter(plan => plan.date > today),
    review,
    conflicts: conflictsFor(plans.filter(plan => plan.date >= today)),
    uncertainties: review.map(source => ({sourceId:source.id, fields:planFields.filter(field => !source[field])}))
      .filter(item => item.fields.length),
    changes,
    openTasks: tasks.filter(task => task.status === 'open'),
    completedTasks: tasks.filter(task => task.status === 'done')
  };
}

/** @param {"empty"|"answered"|"unavailable"} status
 * @param {string} text
 * @param {FamilyPlan[]} [plans]
 * @param {string[]} [sourceIds] */
function response(status, text, plans = [], sourceIds = plans.map(plan => plan.sourceId)) {
  return {status, text, planIds:[...new Set(plans.map(plan => plan.id))], sourceIds:[...new Set(sourceIds.filter(Boolean))]};
}

/** @param {FamilyPlan[]} plans
 * @param {string} emptyMessage */
function planAnswer(plans, emptyMessage) {
  if (!plans.length) return response('empty', emptyMessage);
  const lines = plans.map(plan => [plan.title, plan.date || 'Date open', plan.time, plan.person || 'Person unspecified'].filter(Boolean).join(' · '));
  return response('answered', lines.join('\n'), plans);
}

/** @param {Household} state
 * @param {string} question */
export function answerQuestion(state, question, today = localDay()) {
  const query = normalized(question).replace(/[?.!]+$/u, '').replace(/[’‘]/gu,"'");
  const briefing = buildBriefing(state, today);
  const dayMatch = /^(?:(?:what is|what's|whats) (?:on |happening |scheduled )?(?:the (?:family )?(?:plan|schedule) (?:for )?)?|show (?:the )?(?:plan for )?)(today|tomorrow)$/u.exec(query);
  if (dayMatch) {
    const day = dayMatch[1] === 'today' ? today : nextDay(today);
    return planAnswer(sortedPlans(state.plans.filter(plan => plan.date === day)), 'No approved plans for ' + day + '.');
  }
  if (/^(?:what(?: has)? changed|show (?:recent )?changes)$/u.test(query)) {
    if (!briefing.changes.length) return response('empty','No field changes in the latest approved revisions.');
    const lines = briefing.changes.map(({plan,fields}) => plan.title + ' — ' + fields.map(
      delta => delta.field + ' from ' + (delta.before || 'unspecified') + ' to ' + (delta.after || 'unspecified')
    ).join(', '));
    const plans = briefing.changes.map(change => change.plan);
    return response('answered', lines.join('\n'), plans, plans.flatMap(plan => [plan.history[plan.history.length - 1].sourceId, plan.sourceId]));
  }
  if (/^(?:any conflicts|are there (?:any )?(?:schedule )?conflicts|show conflicts)$/u.test(query)) {
    if (!briefing.conflicts.length) return response('empty','No exact-time conflicts among plans with a named person from today onward.');
    const lines = briefing.conflicts.map(({plans,person,date,time}) => person + ' has ' + plans[0].title + ' and ' + plans[1].title + ' at ' + time + ' on ' + date + '.');
    return response('answered', lines.join('\n'), briefing.conflicts.flatMap(conflict => conflict.plans));
  }
  if (/^(?:what needs review|what needs (?:my |our )?attention|show pending (?:review|sources))$/u.test(query)) {
    if (!briefing.review.length) return response('empty','No sources are waiting for review.');
    return response('answered', briefing.review.map(source => source.title || source.text.slice(0,100)).join('\n'), [], briefing.review.map(source => source.id));
  }
  const personMatch = /^(?:who is|who's) (?:scheduled for|listed for) (.+)$/u.exec(query);
  if (personMatch) {
    const words = personMatch[1].match(/[\p{L}\p{N}]+/gu) ?? [];
    const wanted = words.filter(word => !['a','an','the'].includes(word));
    const matches = sortedPlans(state.plans.filter(plan => {
      /** @type {string[]} */
      const title = normalized(plan.title).match(/[\p{L}\p{N}]+/gu) ?? [];
      return wanted.length && wanted.every(word => title.includes(word));
    }));
    return planAnswer(matches,'No approved plan matches that title.');
  }
  return response('unavailable', 'This lookup supports today, tomorrow, changes, conflicts, pending review and people by plan title. Open-ended interpretation is unavailable.');
}

