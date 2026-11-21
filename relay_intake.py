"""Deterministic extraction for recognized lines in family notices."""
import re
from datetime import date

DETAIL_LIMIT = 480
LABELS = {
    "subject": "title", "event": "title", "title": "title",
    "date": "date", "time": "time", "start time": "time",
    "for": "person", "affected person": "person",
    "bring": "preparation", "what to bring": "preparation", "preparation": "preparation",
    "instructions": "instructions", "notes": "instructions",
    "where": "location", "location": "location", "venue": "location",
    "responsible": "responsibility", "assigned to": "responsibility",
    "deadline": "deadline", "due": "deadline", "rsvp by": "deadline",
}
MONTHS = "january february march april may june july august september october november december".split()
WEEKDAYS = "monday tuesday wednesday thursday friday saturday sunday".split()


def valid_date(value):
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def valid_time(value):
    return re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", value) is not None


def explicit_date(value):
    if valid_date(value):
        return value
    match = re.fullmatch(r"(?:(\w+),?\s+)?([a-z]+)\s+([0-9]{1,2}),?\s+([0-9]{4})", value.lower())
    if not match:
        return ""
    weekday, month, day, year = match.groups()
    try:
        result = date(int(year), MONTHS.index(month) + 1, int(day))
    except ValueError:
        return ""
    return result.isoformat() if not weekday or WEEKDAYS[result.weekday()] == weekday else ""


def explicit_time(value):
    if valid_time(value):
        return value
    match = re.fullmatch(r"(1[0-2]|0?[1-9])(?::([0-5][0-9]))?\s*([ap])\.?m\.?", value, re.I)
    if not match:
        return ""
    hour, minute, period = match.groups()
    return f"{int(hour) % 12 + (12 if period.lower() == 'p' else 0):02}:{minute or '00'}"


def source_fields(line):
    label, separator, value = line.partition(":")
    key = label.strip().casefold()
    if separator and key == "when":
        parts = re.split(r"\s+at\s+", value.strip(), maxsplit=1, flags=re.I)
        return zip(("date", "time"), parts)
    if separator and key in LABELS:
        return [(LABELS[key], value.strip())]
    bring = re.fullmatch(r"\s*please bring\s+(.+?)\.?\s*", line, re.I)
    return [("preparation", bring[1])] if bring else []


def extract(text, members):
    evidence = {key: [] for key in dict.fromkeys(LABELS.values())}
    for number, line in enumerate(text.splitlines(), 1):
        for key, value in source_fields(line):
            evidence[key].append({"line": number, "value": value})

    def name_key(value):
        return " ".join(value.split()).casefold()

    names = {name_key(member): member for member in members}
    normalize = {
        "date": explicit_date, "deadline": explicit_date, "time": explicit_time,
        "person": lambda value: names.get(name_key(value), ""),
        "responsibility": lambda value: names.get(name_key(value), ""),
    }
    values, report = {}, {}
    for key, entries in evidence.items():
        if not entries:
            continue
        raw = [item["value"] for item in entries]
        candidates = [normalize[key](value) for value in raw] if key in normalize else raw
        limit = 160 if key in ("title", "location") else DETAIL_LIMIT
        if not all(0 < len(value) <= limit for value in candidates):
            status = "invalid"
        elif len(set(candidates)) > 1:
            status = "conflicting"
        elif key == "time" and "date" not in values:
            status = "needs_date"
        else:
            status = "suggested"
            values[key] = candidates[0]
        report[key] = {"status": status, "evidence": entries}
    return values, report
