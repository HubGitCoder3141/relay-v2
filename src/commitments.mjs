function required(value, label) {
  const clean = String(value ?? '').trim();
  if (!clean) throw new Error(`${label} is required.`);
  return clean;
}

function validDate(value) {
  const date = String(value ?? '');
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || new Date(`${date}T00:00:00.000Z`).toISOString().slice(0, 10) !== date) {
    throw new Error('Enter a valid date.');
  }
  return date;
}

export function createCommitment(input, at, id) {
  const title = required(input.title, 'Task');
  const dueDate = validDate(input.dueDate);
  const caregiver = required(input.caregiver, 'Caregiver');
  const source = required(input.source, 'Original notice');
  return {
    id, title, dueDate, caregiver, source, status: 'pending',
    completionNote: '',
    history: [{ type: 'created', at }],
  };
}

export function acceptCommitment(item, at) {
  if (item.status !== 'pending') throw new Error('Only a pending commitment can be accepted.');
  return { ...item, status: 'accepted', history: [...item.history, { type: 'accepted', at, caregiver: item.caregiver }] };
}

export function completeCommitment(item, at, note) {
  if (item.status !== 'accepted') throw new Error('The caregiver must accept this commitment first.');
  const completionNote = required(note, 'Completion note');
  return { ...item, status: 'completed', completionNote, history: [...item.history, { type: 'completed', at, note: completionNote }] };
}

export function reviseCommitment(item, update, at) {
  const dueDate = validDate(update.dueDate);
  const caregiver = required(update.caregiver, 'Caregiver');
  const source = required(update.source, 'Updated notice');
  if (dueDate === item.dueDate && caregiver === item.caregiver && source === item.source) {
    throw new Error('Add a changed date, caregiver, or notice before saving.');
  }
  const previous = { dueDate: item.dueDate, caregiver: item.caregiver, source: item.source };
  return {
    ...item, dueDate, caregiver, source, status: 'pending', completionNote: '',
    history: [...item.history, { type: 'revised', at, previous }],
  };
}
