const statusOrder = { pending: 0, accepted: 1, completed: 2 };

export function summarize(items) {
  return items.reduce((counts, item) => {
    counts.all += 1;
    if (item.status in counts) counts[item.status] += 1;
    return counts;
  }, { all: 0, pending: 0, accepted: 0, completed: 0 });
}

export function visibleCommitments(items, filter) {
  return items.filter(item => filter === 'all' || item.status === filter).sort((a, b) =>
    (statusOrder[a.status] ?? 3) - (statusOrder[b.status] ?? 3) || a.dueDate.localeCompare(b.dueDate)
  );
}

export function dueDescription(date, today) {
  const days = Math.round((Date.parse(`${date}T00:00:00Z`) - Date.parse(`${today}T00:00:00Z`)) / 86400000);
  if (days < 0) return 'Overdue';
  if (days === 0) return 'Due today';
  if (days === 1) return 'Due tomorrow';
  const options = { month: 'short', day: 'numeric', timeZone: 'UTC' };
  if (date.slice(0, 4) !== today.slice(0, 4)) options.year = 'numeric';
  return `Due ${new Intl.DateTimeFormat('en-US', options).format(new Date(`${date}T00:00:00Z`))}`;
}
