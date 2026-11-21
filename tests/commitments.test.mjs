import test from 'node:test';
import assert from 'node:assert/strict';
import { createCommitment, acceptCommitment, completeCommitment, reviseCommitment } from '../src/commitments.mjs';

const input = {
  title: 'Return museum form',
  dueDate: '2026-12-04',
  caregiver: 'Alex',
  source: 'Please return the museum form by Friday, December 4.',
};

test('a new commitment keeps its source and awaits acceptance', () => {
  const item = createCommitment(input, '2026-11-21T12:00:00.000Z', 'item-1');
  assert.equal(item.status, 'pending');
  assert.equal(item.source, input.source);
  assert.equal(item.history[0].type, 'created');
});

test('a commitment needs a title, date, caregiver, and source', () => {
  assert.throws(() => createCommitment({ ...input, source: '   ' }, '2026-11-21T12:00:00.000Z', 'item-1'), /original notice/i);
  assert.throws(() => createCommitment({ ...input, dueDate: '2026-02-31' }, '2026-11-21T12:00:00.000Z', 'item-1'), /valid date/i);
});

test('acceptance and completion record distinct steps', () => {
  const item = createCommitment(input, '2026-11-21T12:00:00.000Z', 'item-1');
  const accepted = acceptCommitment(item, '2026-11-21T12:01:00.000Z');
  const completed = completeCommitment(accepted, '2026-11-21T12:02:00.000Z', 'Form handed to teacher');
  assert.equal(accepted.status, 'accepted');
  assert.equal(completed.status, 'completed');
  assert.equal(completed.completionNote, 'Form handed to teacher');
  assert.deepEqual(completed.history.map(event => event.type), ['created', 'accepted', 'completed']);
  assert.equal(item.status, 'pending');
});

test('completion cannot silently stand in for acceptance', () => {
  const item = createCommitment(input, '2026-11-21T12:00:00.000Z', 'item-1');
  assert.throws(() => completeCommitment(item, '2026-11-21T12:02:00.000Z', 'Done'), /accept/i);
});

test('a changed notice preserves old details and asks for fresh acceptance', () => {
  const accepted = acceptCommitment(createCommitment(input, '2026-11-21T12:00:00.000Z', 'item-1'), '2026-11-21T12:01:00.000Z');
  const revised = reviseCommitment(accepted, {
    dueDate: '2026-12-05',
    caregiver: 'Sam',
    source: 'Update: forms are due Saturday, December 5.',
  }, '2026-11-22T12:00:00.000Z');
  assert.equal(revised.status, 'pending');
  assert.equal(revised.dueDate, '2026-12-05');
  assert.equal(revised.source, 'Update: forms are due Saturday, December 5.');
  assert.equal(revised.history.at(-1).previous.dueDate, '2026-12-04');
  assert.equal(revised.history.at(-1).previous.source, input.source);
  assert.equal(accepted.dueDate, '2026-12-04');
});
