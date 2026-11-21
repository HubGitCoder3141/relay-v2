import test from 'node:test';
import assert from 'node:assert/strict';
import { summarize, visibleCommitments, dueDescription } from '../src/presentation.mjs';

const items = [
  { id: 'done', status: 'completed', dueDate: '2026-12-01' },
  { id: 'later', status: 'pending', dueDate: '2026-12-12' },
  { id: 'doing', status: 'accepted', dueDate: '2026-12-03' },
  { id: 'sooner', status: 'pending', dueDate: '2026-12-02' },
];

test('the plan orders unanswered work first by due date', () => {
  assert.deepEqual(visibleCommitments(items, 'all').map(item => item.id), ['sooner', 'later', 'doing', 'done']);
  assert.deepEqual(visibleCommitments(items, 'pending').map(item => item.id), ['sooner', 'later']);
});

test('summary counts distinguish waiting, accepted, and complete', () => {
  assert.deepEqual(summarize(items), { all: 4, pending: 2, accepted: 1, completed: 1 });
});

test('due descriptions make urgency clear without changing the stored date', () => {
  assert.equal(dueDescription('2026-11-21', '2026-11-21'), 'Due today');
  assert.equal(dueDescription('2026-11-22', '2026-11-21'), 'Due tomorrow');
  assert.equal(dueDescription('2026-11-20', '2026-11-21'), 'Overdue');
  assert.equal(dueDescription('2026-12-04', '2026-11-21'), 'Due Dec 4');
});
