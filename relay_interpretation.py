"""Combine learned role assignments with Relay's date and household constraints."""
from collections import defaultdict
from datetime import date
import os
import re

from relay_intake import DETAIL_LIMIT, explicit_date, explicit_time, extract


MODEL_MINIMUM = {
    "title": .70, "date": .74, "time": .78, "person": .76, "responsibility": .80,
    "location": .75, "deadline": .80, "preparation": .73, "instructions": .70,
}
REVIEW_MINIMUM = .57
GENERIC_TITLES = {"fyi", "update", "reminder", "heads up", "schedule", "practice", "meeting"}
NON_LOCATIONS = {"a", "an", "the", "there", "here", "near", "by", "at", "in"}
SCHEDULE_FIELDS = ("date", "time", "deadline", "location", "preparation", "person", "responsibility")
DUE_CUE = re.compile(r"\b(?:due(?:\s+(?:by|on))?|deadline:?|rsvp(?:\s+by)?)\s*$", re.I)


def visible_text(text):
    """Mask quoted history and mail headers without moving source offsets."""
    lines, content, mail_header, history = [], False, False, False
    for line in text.splitlines(keepends=True):
        if content and re.match(r"\s*(?:On .+ wrote:|-+\s*(?:Original Message|Forwarded message)\s*-+)", line, re.I):
            history = True
        if re.match(r"\s*From:\s*.+@", line, re.I):
            mail_header = True
        header = mail_header and re.match(r"\s*(?:From|Date|Sent|To|Cc|Bcc|Reply-to):", line, re.I)
        if history or header or line.lstrip().startswith(">"):
            lines.append("".join(char if char in "\r\n" else " " for char in line))
            continue
        if not re.match(r"\s*Subject:", line, re.I):
            mail_header = False
        content = content or bool(line.strip())
        lines.append(line)
    return "".join(lines)


def evidence_for(text, span):
    # Preserve the exact Unicode-source slice, never model-generated text.
    return {"line": len(text[:span.start].splitlines()) + (span.start == 0 or text[span.start-1:span.start] in ("\n", "\r")),
            "value": text[span.start:span.end], "start": span.start, "end": span.end}


def role_is_consistent(text, field, entries):
    for _, entry in entries:
        context = text[max(0, entry["start"] - 36):entry["start"]].casefold()
        if field in ("date", "time") and (DUE_CUE.search(context) or re.search(r"\bby\s*$", context)):
            return False
        if field == "location" and entry["value"].casefold() in NON_LOCATIONS:
            return False
    return True


def normalize(field, value, names, anchor):
    if field == "time":
        return explicit_time(" ".join(value.split()))
    if field in ("date", "deadline"):
        return explicit_date(" ".join(value.split()), anchor)
    if field in ("person", "responsibility"):
        key = " ".join(value.split()).casefold()
        exact = [name for name in names if " ".join(name.split()).casefold() == key]
        if exact:
            return exact[0]
        first = [name for name in names if name.split() and name.split()[0].casefold() == key]
        return first[0] if len(first) == 1 else ""
    return value


def interpret(text, members, source_date="", model=None):
    values, evidence = extract(text, members, source_date)
    if model is None:
        return values, evidence
    result = model.predict(visible_text(text), members)
    if result is None:
        return values, evidence
    evidence["_model"] = {"kind": result.kind, "kindConfidence": round(result.kind_confidence, 3),
                          "intent": result.intent, "intentConfidence": round(result.intent_confidence, 3)}
    if result.intent in ("cancel", "multiple", "none") and result.intent_confidence >= .72:
        if result.intent != "none":
            for field in SCHEDULE_FIELDS:
                values.pop(field, None)
                if field in evidence:
                    evidence[field]["status"] = "ambiguous"
        return values, evidence

    anchor = date.fromisoformat(source_date) if source_date else None
    candidates = defaultdict(list)
    for span in result.spans:
        if span.confidence >= REVIEW_MINIMUM:
            field = span.field
            if field == "date" and DUE_CUE.search(text[max(0, span.start - 36):span.start]):
                field = "deadline"
            candidates[field].append((span, evidence_for(text, span)))

    # Process the date before the start time. Explicit rule evidence always wins.
    for field, minimum in MODEL_MINIMUM.items():
        if field in evidence or not candidates[field]:
            continue
        unique = {}
        for span, entry in candidates[field]:
            key = (span.start, span.end)
            if key not in unique or span.confidence > unique[key][0].confidence:
                unique[key] = (span, entry)
        entries = list(unique.values())
        confidence = min(span.confidence for span, _ in entries)
        raw = [entry["value"] for _, entry in entries]
        interpreted = [normalize(field, value, members, anchor) for value in raw]
        interpreted = list(dict.fromkeys(interpreted))
        report = {"status": "low_confidence", "evidence": [entry for _, entry in entries],
                  "confidence": round(confidence, 3), "method": "model"}
        evidence[field] = report
        if confidence < minimum:
            continue
        if not role_is_consistent(text, field, entries):
            report["status"] = "ambiguous"
            continue
        if "" in interpreted:
            report["status"] = "needs_context"
            continue
        if field in ("preparation", "instructions"):
            interpreted = ["\n".join(interpreted)]
        if len(interpreted) != 1:
            report["status"] = "conflicting"
            continue
        value = interpreted[0]
        limit = 160 if field in ("title", "location") else 80 if field in ("person", "responsibility") else DETAIL_LIMIT
        if not value or len(value) > limit or field == "title" and value.casefold() in GENERIC_TITLES:
            report["status"] = "invalid"
            continue
        if field == "time" and not values.get("date"):
            report["status"] = "needs_date"
            report["candidate"] = value
            continue
        values[field] = value
        report["status"] = "suggested"
        if field in ("date", "deadline") and source_date and any(not explicit_date(item) for item in raw):
            report["anchor"] = source_date
        if field in ("person", "responsibility") and any(value.casefold() != item.casefold() for item in raw):
            report["inferred"] = True
    return values, evidence


def active_notice_model():
    default = "0" if os.environ.get("VERCEL_ENV") == "production" else "1"
    if os.environ.get("RELAY_NLU_ENABLED", default) != "1":
        return None
    try:
        from relay_nlu import deployed_model
    except ImportError:
        return None
    return deployed_model()


def interpret_notice(text, members, source_date=""):
    return interpret(text, members, source_date, active_notice_model())
