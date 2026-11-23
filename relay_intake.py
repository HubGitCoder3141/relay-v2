"""Deterministic extraction for recognized lines in family notices."""
import re
from datetime import date, timedelta

DETAIL_LIMIT = 480
LABELS = {
    "subject": "title", "event": "title", "title": "title",
    "date": "date", "time": "time", "start time": "time",
    "for": "person", "affected person": "person",
    "bring": "preparation", "what to bring": "preparation", "preparation": "preparation",
    "instructions": "instructions", "notes": "instructions",
    "where": "location", "location": "location", "venue": "location",
    "responsible": "responsibility", "assigned to": "responsibility",
    "deadline": "deadline", "due": "deadline", "rsvp by": "deadline", "due date": "deadline",
    "starts": "time", "start": "time", "address": "location", "pickup location": "location",
    "child": "person", "student": "person", "assigned": "responsibility",
}
MONTHS = "january february march april may june july august september october november december".split()
WEEKDAYS = "monday tuesday wednesday thursday friday saturday sunday".split()
MONTH_NAMES = {name: i for i, month in enumerate(MONTHS, 1) for name in (month, month[:3])}
MONTH_NAMES["sept"] = 9
DAY_NAMES = {name: i for i, day in enumerate(WEEKDAYS) for name in (day, day[:3])}
DAY_NAMES.update(tues=1, thurs=3, thur=3, weds=2)
DATE_WORDS = "(?:" + "|".join(MONTH_NAMES) + r")\.?\s+[0-9]{1,2}(?:st|nd|rd|th)?(?:,?\s+[0-9]{4})?"
DAY_WORDS = "(?:" + "|".join(DAY_NAMES) + r")\.?"
ISO = r"[0-9]{4}-[0-9]{2}-[0-9]{2}"
DATE_TEXT = rf"(?:{ISO}|(?:{DAY_WORDS}[, ]+)?{DATE_WORDS}|(?:this\s+)?{DAY_WORDS}|today|tomorrow)"
TIME_TEXT = r"(?:noon|midnight|[0-9]{1,2}(?::[0-9]{2})?\s*[ap]\.?m\.?|[0-9]{2}:[0-9]{2})(?![\w:])"
WHEN_TEXT = re.compile(rf"(?P<date>{DATE_TEXT})(?:\s*(?:,\s*|\bat\s+|@\s*|\s+)(?P<time>{TIME_TEXT}))?", re.I)


def valid_date(value):
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def valid_time(value):
    return re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", value) is not None


def explicit_date(value, anchor=None):
    if valid_date(value):
        return value
    normalized = value.casefold().strip()
    if anchor and normalized in ("today", "tomorrow"):
        try:
            return (anchor + timedelta(days=normalized == "tomorrow")).isoformat()
        except OverflowError:
            return ""
    weekday_only = re.fullmatch(rf"(?:this\s+)?({DAY_WORDS})", normalized)
    if anchor and weekday_only:
        day_number = DAY_NAMES[weekday_only[1].rstrip(".")]
        try:
            return (anchor + timedelta(days=(day_number - anchor.weekday()) % 7)).isoformat()
        except OverflowError:
            return ""
    match = re.fullmatch(r"(?:(\w+)\.?,?\s+)?([a-z]+)\.?\s+([0-9]{1,2})(?:st|nd|rd|th)?(?:,?\s+([0-9]{4}))?", normalized)
    if not match:
        return ""
    weekday, month, day, year = match.groups()
    if month not in MONTH_NAMES or (weekday and weekday not in DAY_NAMES) or not (year or anchor):
        return ""
    try:
        result = date(int(year) if year else anchor.year, MONTH_NAMES[month], int(day))
        if not year and result < anchor:
            result = result.replace(year=anchor.year + 1)
        if not year and (result - anchor).days > 183:
            return ""
    except ValueError:
        return ""
    return result.isoformat() if not weekday or DAY_NAMES[weekday] == result.weekday() else ""


def explicit_time(value):
    if valid_time(value):
        return value
    if value.casefold() in ("noon", "midnight"):
        return "12:00" if value.casefold() == "noon" else "00:00"
    match = re.fullmatch(r"(1[0-2]|0?[1-9])(?::([0-5][0-9]))?\s*([ap])\.?m\.?", value, re.I)
    if not match:
        return ""
    hour, minute, period = match.groups()
    return f"{int(hour) % 12 + (12 if period.lower() == 'p' else 0):02}:{minute or '00'}"


def schedule_fields(value):
    schedule = WHEN_TEXT.match(value)
    if not schedule:
        return [("date", value)]
    rest = value[schedule.end():].strip()
    fields = [("date", schedule["date"])]
    if schedule["time"]:
        time_range = re.match(rf"^(?:to\s+|[-–—]\s*)({TIME_TEXT})(?:\s+|$|(?=[.]))", rest, re.I)
        if time_range and explicit_time(schedule["time"]) < explicit_time(time_range[1]):
            rest = rest[time_range.end():].strip()
    if rest and re.match(r"^(?:or\b|and\b|/|to\b|[-–—])", rest, re.I):
        return [("date", value)]
    if schedule["time"]:
        fields.append(("time", schedule["time"]))
    if not rest or rest == ".":
        return fields
    location = re.fullmatch(r"(?:at|in)\s+(.+?)[.]?", rest, re.I)
    if location:
        if not schedule["time"] and re.match(r"[0-9]", location[1]):
            return [*fields, ("time", location[1])]
        return [*fields, ("location", location[1])]
    return [("date", value)]


def source_fields(line):
    line = re.sub(r"^\s*(?:[-*•]\s+)?", "", line).strip()
    label, separator, value = line.partition(":")
    key = label.strip().casefold()
    if separator and key in ("when", "schedule", "date and time"):
        return schedule_fields(value.strip())
    if separator and key in LABELS:
        field = LABELS[key]
        return schedule_fields(value.strip()) if field == "date" else [(field, value.strip())]
    bring = re.fullmatch(r"(?:please\s+)?(?:bring|pack)\s+(.+?)\.?\s*", line, re.I)
    if bring:
        return [("preparation", bring[1])]
    deadline = re.fullmatch(rf"(?:please\s+)?(?:rsvp|register|sign up|return\s+.+?|submit\s+.+?|pay\s+.+?)\s+by\s+({DATE_TEXT})[.]?", line, re.I)
    if deadline:
        return [("deadline", deadline[1]), ("instructions", line)]
    instruction = re.match(r"^(?:please\s+)?(?:arrive|check in|enter|use|meet|pick up|drop off)\s+", line, re.I)
    if instruction:
        return [("instructions", line)]
    event = re.fullmatch(rf"(.{{2,110}}?)\s+(?:is\s+on|will\s+be\s+(?:held\s+)?on|takes\s+place\s+on|starts\s+on|is\s+scheduled\s+for)\s+({DATE_TEXT}.*)", line, re.I)
    if event:
        if re.search(r"\b(?:if|not|tentative|cancel(?:led|ed))\b", event[1], re.I):
            return [("date", line)]
        return [("title", event[1]), *schedule_fields(event[2])]
    time_first = re.fullmatch(rf"(.{{2,110}}?)\s+(?:starts|begins)\s+at\s+({TIME_TEXT})\s+on\s+({DATE_TEXT})(?:\s+(?:at|in)\s+(.+?))?[.]?", line, re.I)
    if time_first:
        title, clock, day, location = time_first.groups()
        return [("title", title), ("date", day), ("time", clock), *([("location", location)] if location else [])]
    activity = re.fullmatch(rf"(.{{1,80}}?)\s+has\s+(.{{2,110}}?)\s+on\s+({DATE_TEXT}.*)", line, re.I)
    if activity and not re.search(r"\b(?:if|maybe|tentative)\b", activity[1], re.I):
        return [("person", activity[1]), ("title", activity[2]), *schedule_fields(activity[3])]
    return []


def extract(text, members, source_date=""):
    evidence = {key: [] for key in dict.fromkeys(LABELS.values())}
    anchor = date.fromisoformat(source_date) if source_date else None
    subject_evidence = []
    cancellation = False
    in_mail_header = False
    for number, line in enumerate(text.splitlines(), 1):
        if re.fullmatch(r"\s*(?:On .+ wrote:|-+\s*(?:Original Message|Forwarded message)\s*-+)\s*", line, re.I) and any(evidence.values()):
            break
        if line.lstrip().startswith(">"):
            continue
        if re.match(r"^\s*from:\s*.+@", line, re.I):
            in_mail_header = True
            continue
        if in_mail_header and re.match(r"^\s*(?:date|sent|to|cc|bcc|reply-to):", line, re.I):
            continue
        if not re.match(r"^\s*subject:", line, re.I):
            in_mail_header = False
        if re.search(r"^\s*(?:subject:\s*)?(?:cancel(?:l?ed|lation):|.+\b(?:is|has been) cancel(?:l?ed)\s*[.!]?$)", line, re.I):
            cancellation = True
        if re.match(r"^\s*(?:[-*•]\s+)?(?:subject|title|event)\s*:", line, re.I):
            subject_evidence.extend({"line": number, "value": value} for key, value in source_fields(line) if key == "title")
            continue
        for sentence in re.split(r"\.(?=\s+(?:Please|Bring|Pack|Arrive|Use|Enter|RSVP|Meet|Check|Upload|Submit|Drop)\b)", line):
            for key, value in source_fields(sentence):
                evidence[key].append({"line": number, "value": value})
    multiple_activities = len({item["value"].casefold() for item in evidence["title"]}) > 1
    if subject_evidence:
        evidence["title"] = subject_evidence

    def name_key(value):
        return " ".join(value.split()).casefold()

    names = {name_key(member): member for member in members}
    normalize = {
        "date": lambda value: explicit_date(value, anchor), "deadline": lambda value: explicit_date(value, anchor), "time": explicit_time,
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
        if key in ("preparation", "instructions") and all(candidates):
            candidates = ["\n".join(dict.fromkeys(candidates))]
        if multiple_activities and key != "title":
            status = "conflicting"
        elif cancellation and key in ("date", "time", "deadline", "location", "preparation"):
            status = "invalid"
        elif not all(0 < len(value) <= limit for value in candidates):
            status = "invalid"
        elif len(set(candidates)) > 1:
            status = "conflicting"
        elif key == "time" and "date" not in values:
            status = "needs_date"
        else:
            status = "suggested"
            values[key] = candidates[0]
        report[key] = {"status": status, "evidence": entries}
        if key in ("date", "deadline") and status == "suggested" and any(not explicit_date(value) for value in raw):
            report[key]["anchor"] = source_date
    return values, report
