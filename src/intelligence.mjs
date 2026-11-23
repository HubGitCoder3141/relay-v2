/** @typedef {import('./household').Household} Household */
/** @typedef {import('./household').FamilyPlan} FamilyPlan */
/** @typedef {import('./household').PlanVersion} PlanVersion */

// Read-only projections over one authorized household snapshot.
// Calendar dates and wall-clock times have already been validated by the store.
const planFields = /** @type {const} */ (['title', 'date', 'time', 'person']);
const revisionFields = /** @type {const} */ ([...planFields, 'preparation', 'instructions', 'location', 'responsibility', 'deadline']);

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
  return revisionFields.filter(field => (previous[field] || '') !== (current[field] || ''))
    .map(field => ({ field, before: previous[field] || '', after: current[field] || '' }));
}

function localDay() {
  const now = new Date();
  return [now.getFullYear(), String(now.getMonth() + 1).padStart(2, '0'), String(now.getDate()).padStart(2, '0')].join('-');
}

/** @param {string} day */
function nextDay(day, offset = 1) {
  const next = new Date(day + 'T00:00:00Z');
  next.setUTCDate(next.getUTCDate() + offset);
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

const weekdays = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday'];
const monthNames = ['january','february','march','april','may','june','july','august','september','october','november','december'];
const displayFields = {
  date:'Date', time:'Start time', location:'Location', person:'Person listed',
  responsibility:'Responsible person', preparation:'What to bring', deadline:'Deadline', instructions:'Instructions'
};

function dateScope(phrase, today) {
  if (phrase === 'today') return [today, nextDay(today)];
  if (phrase === 'tomorrow') return [nextDay(today), nextDay(today, 2)];
  if (phrase === 'this week' || phrase === 'next seven days') return [today, nextDay(today, 7)];
  const weekday = new Date(today + 'T00:00:00Z').getUTCDay();
  if (phrase === 'this weekend') {
    const saturday = weekday === 0 ? nextDay(today, -1) : nextDay(today, 6 - weekday);
    return [today > saturday ? today : saturday, nextDay(saturday, 2)];
  }
  if (phrase === 'next week') {
    const monday = nextDay(today, 7 - (weekday + 6) % 7);
    return [monday, nextDay(monday, 7)];
  }
  const index = weekdays.indexOf(phrase);
  if (index >= 0) {
    const date = nextDay(today, (index - weekday + 7) % 7);
    return [date, nextDay(date)];
  }
  if (/^\d{4}-\d{2}-\d{2}$/u.test(phrase)) {
    const parsed = new Date(phrase + 'T00:00:00Z');
    if (!Number.isNaN(parsed.valueOf()) && parsed.toISOString().slice(0,10) === phrase) return [phrase, nextDay(phrase)];
  }
  const monthDay = /^([a-z]+) (\d{1,2})(?:st|nd|rd|th)?(?:,? (\d{4}))?$/u.exec(phrase);
  if (monthDay) {
    const month = monthNames.findIndex(value => value === monthDay[1] || value.slice(0,3) === monthDay[1]) + 1;
    if (!month) return null;
    const year = Number(today.slice(0,4));
    const suffix = '-' + String(month).padStart(2,'0') + '-' + monthDay[2].padStart(2,'0');
    const thisYear = year + suffix;
    const day = monthDay[3] ? monthDay[3] + suffix : (thisYear < today ? year + 1 + suffix : thisYear);
    return dateScope(day, today);
  }
  return null;
}

function namedMember(state, name) {
  return (state.members ?? []).find(person => normalized(person) === name);
}

function planMatches(plans, title) {
  const exact = plans.filter(plan => normalized(plan.title) === title);
  if (exact.length) return exact;
  const words = value => (normalized(value).match(/[\p{L}\p{N}]+/gu) ?? []);
  const wanted = words(title).filter(word => !['a','an','the','our'].includes(word));
  return plans.filter(plan => wanted.length && wanted.every(word => words(plan.title).includes(word)));
}

function planDetails(state, title, fields, today, previousPlanId) {
  const suffix = /\s+(?:on\s+)?(today|tomorrow|this weekend|next week|\d{4}-\d{2}-\d{2}|sunday|monday|tuesday|wednesday|thursday|friday|saturday)$/u.exec(title);
  const scope = suffix && dateScope(suffix[1], today);
  const name = scope ? title.slice(0, suffix.index).trim().replace(/ (?:start|begin|take place)$/u,'') : title;
  const plans = sortedPlans(/^(it|that|that plan)$/u.test(name)
    ? state.plans.filter(plan => plan.id === previousPlanId)
    : planMatches(state.plans, name).filter(plan => !scope || plan.date >= scope[0] && plan.date < scope[1]));
  if (!plans.length) {
    return response('empty', /^(it|that|that plan)$/u.test(name)
      ? 'Which plan do you mean? Include its name in your question.'
      : 'No approved plan matches that name. Try its title from Family plan.');
  }
  if (plans.length > 1) {
    const options = planAnswer(plans, '');
    return {...options, text:'Several approved plans match. Which one do you mean? You can include the date.\n' + options.text};
  }
  const [plan] = plans;
  const lines = fields.map(field => displayFields[field] + ' · ' + (plan[field] || 'Not recorded'));
  return response('answered', [plan.title, ...lines].join('\n'), plans);
}

function actionAnswer(state, query, today) {
  const match = /^(?:show (?:me )?|list )?(overdue|open|incomplete|completed|due|all) (?:family )?(?:actions|tasks|chores)(?: (?:for|assigned to) (.+?))?(?: (?:due )?(today|tomorrow|this week|next week|this weekend))?$/u.exec(query);
  const whatsDue = /^(?:what(?:'s| is) due|what do we need to do)(?: (today|tomorrow|this week|next week|this weekend))?$/u.exec(query);
  if (!match && !whatsDue) return null;
  const mode = match?.[1] || (whatsDue?.[1] || /^what(?:'s| is) due/u.test(query) ? 'due' : 'open');
  const person = match?.[2] && namedMember(state, match[2]);
  if (match?.[2] && !person) return response('empty', 'That name is not in this household’s roster.');
  const period = match?.[3] || whatsDue?.[1];
  const scope = period && dateScope(period, today);
  const tasks = (state.tasks ?? []).filter(task =>
    (!person || task.person === person) &&
    (mode === 'all' || task.status === (mode === 'completed' ? 'done' : 'open')) &&
    (mode !== 'overdue' || task.due && task.due < today) &&
    (mode !== 'due' || task.due) &&
    (!scope || task.due && task.due >= scope[0] && task.due < scope[1]));
  const deadlines = mode === 'due' ? sortedPlans(state.plans.filter(plan =>
    plan.deadline && (!scope ? plan.deadline >= today : plan.deadline >= scope[0] && plan.deadline < scope[1]) &&
    (!person || plan.person === person || plan.responsibility === person))) : [];
  if (!tasks.length && !deadlines.length) return response('empty', 'No saved actions or plan deadlines match that request.');
  const linkedPlans = tasks.map(task => state.plans.find(plan => plan.id === task.plan)).filter(Boolean);
  const lines = [
    ...tasks.map(task => ({date:task.due, text:[task.title, task.person || 'Household', task.due || 'No due date', task.status === 'done' && 'Completed'].filter(Boolean).join(' · ')})),
    ...deadlines.map(plan => ({date:plan.deadline, text:plan.title + ' · Plan deadline · ' + plan.deadline}))
  ].sort((a,b) => (a.date || '9999').localeCompare(b.date || '9999'));
  return {...response('answered', lines.map(line => line.text).join('\n'), [...linkedPlans, ...deadlines]),
    taskIds:tasks.map(task => task.id)};
}

function flexibleLookup(state, query, today, previousPlanId) {
  const actions = actionAnswer(state, query, today);
  if (actions) return actions;
  const detailPatterns = [
    [/^(?:when is|what's) (?:the )?(?:deadline|rsvp) (?:for|on) (.+)$/u, ['deadline']],
    [/^(?:where (?:is|are)|where do (?:i|we) go for|what(?:'s| is) the location (?:of|for)) (.+)$/u, ['location']],
    [/^(?:what time (?:is|does)|when (?:is|does)) (.+?)(?: (?:start|begin|take place))?$/u, ['date','time']],
    [/^who(?:'s| is) (?:handling|responsible for|in charge of) (.+)$/u, ['responsibility']],
    [/^what (?:should|do|does) (?:i|we|they) (?:bring|pack)(?: (?:to|for))? (.+)$/u, ['preparation','instructions']],
    [/^(?:tell me about|show me (?:the )?details (?:for|about)) (.+)$/u, ['date','time','location','person','responsibility','preparation','deadline','instructions']]
  ];
  for (const [pattern, fields] of detailPatterns) {
    const match = pattern.exec(query);
    if (match) return planDetails(state, match[1], fields, today, previousPlanId);
  }
  const familySchedule = /^(?:what(?:'s| is) (?:on|happening|scheduled)(?: (?:for|on))?|what do we have(?: on)?|(?:show|check)(?: me)? (?:the )?(?:family )?(?:plans?|schedule|calendar)(?: (?:for|on))?) (.+)$/u.exec(query);
  const personSchedule = /^(?:what does (.+?) have|what(?:'s| is) on (.+?)(?:'s) (?:calendar|schedule))(?: (.+))?$/u.exec(query);
  if (familySchedule || personSchedule) {
    const period = personSchedule ? personSchedule[3] || 'this week' : familySchedule[1];
    const scope = dateScope(period.replace(/^on /u,''), today);
    if (!scope) return null;
    const member = personSchedule && namedMember(state, personSchedule[1] || personSchedule[2]);
    if (personSchedule && !member) return response('empty', 'That name is not in this household’s roster.');
    const matches = sortedPlans(state.plans.filter(plan =>
      plan.date >= scope[0] && plan.date < scope[1] && (!member || plan.person === member)));
    return planAnswer(matches, member ? 'No approved plans list ' + member + ' for that period.' : 'No approved plans for that period.');
  }
  return null;
}

/** @param {Household} state
 * @param {string} question */
export function answerQuestion(state, question, today = localDay(), previousPlanId = '') {
  const query = normalized(question).replace(/[?.!]+$/u, '').replace(/[’‘]/gu,"'");
  const briefing = buildBriefing(state, today);
  if (/^(?:(?:what is|what's) (?:on|happening) this week|what should we prepare)$/u.test(query)) {
    const end = nextDay(today, 7);
    const week = [...briefing.today, ...briefing.upcoming.filter(plan => plan.date < end)];
    if (query !== 'what should we prepare') return planAnswer(week, 'No approved plans in the next seven days.');
    const plans = week.filter(plan => plan.preparation || plan.instructions);
    if (!plans.length) return response('empty', 'No approved preparation or instructions for the next seven days.');
    return response('answered', plans.map(plan => [plan.title, plan.preparation, plan.instructions].filter(Boolean).join(' · ')).join('\n'), plans);
  }
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
  if (/^what needs (?:my |our )?attention$/u.test(query)) {
    const due = actionAnswer(state, 'what is due today', today);
    const late = actionAnswer(state, 'overdue actions', today);
    const sections = [
      late.status === 'answered' && 'Overdue\n' + late.text,
      due.status === 'answered' && 'Due today\n' + due.text,
      briefing.review.length && 'Needs review\n' + briefing.review.map(source => source.title || source.text.slice(0,100)).join('\n')
    ].filter(Boolean);
    if (!sections.length) return response('empty', 'No overdue or due-today work and no notices waiting for review.');
    return {status:'answered',text:sections.join('\n\n'),planIds:[...new Set([...late.planIds,...due.planIds])],
      sourceIds:[...new Set([...late.sourceIds,...due.sourceIds,...briefing.review.map(source => source.id)])],
      taskIds:[...new Set([...(late.taskIds ?? []),...(due.taskIds ?? [])])]};
  }
  if (/^(?:what needs review|show pending (?:review|sources))$/u.test(query)) {
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
  return flexibleLookup(state, query, today, previousPlanId) ??
    response('unavailable', 'Try a date, the name of a plan, or a question about deadlines or actions. I can look up saved household information.');
}

export function groupActions(tasks, today) {
  const groups = { overdue: [], today: [], upcoming: [], anytime: [], done: [] };
  for (const task of tasks) {
    const group = task.status === 'done' ? 'done' : !task.due ? 'anytime' :
      task.due < today ? 'overdue' : task.due === today ? 'today' : 'upcoming';
    groups[group].push(task);
  }
  for (const group of ['overdue', 'upcoming']) groups[group].sort((a,b) => a.due.localeCompare(b.due));
  return groups;
}
