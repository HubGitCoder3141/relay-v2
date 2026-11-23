"""CPU inference for Relay's trainable contextual span and intent model."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from zipfile import BadZipFile
from zlib import crc32
import json
import math
import re

import numpy as np


FIELDS = ("title", "date", "time", "person", "location", "responsibility", "deadline", "preparation", "instructions")
KINDS = ("sports", "homework", "meeting", "appointment", "reminder", "trip", "event", "unknown")
INTENTS = ("schedule", "update", "cancel", "multiple", "none")
MAX_TOKENS = 192
CHAR_BUCKETS = 512
CHAR_SLOTS = 10
SHAPES = 16
TOKEN = re.compile(r"[^\W\d_]+|\d+|[^\w\s]|_", re.UNICODE)
MODEL_PATH = Path(__file__).with_name("models") / "relay_nlu_v2.npz"
REFERENCE_PATH = MODEL_PATH.with_name("relay_nlu_v1.npz")


@dataclass(frozen=True)
class Span:
    field: str
    start: int
    end: int
    confidence: float


@dataclass(frozen=True)
class Prediction:
    kind: str
    kind_confidence: float
    intent: str
    intent_confidence: float
    spans: tuple[Span, ...]


def tokens(text):
    return list(TOKEN.finditer(text))


def lexical_key(word):
    return "<number>" if word.isdecimal() else word.casefold()


def token_features(word):
    key = lexical_key(word)
    spelling = "^" + key + "$"
    fragments = (list(dict.fromkeys([spelling[:3], spelling[-3:],
                 *(spelling[i:i+3] for i in range(len(spelling)-2))]))[:CHAR_SLOTS])
    chars = [1 + crc32(fragment.encode()) % (CHAR_BUCKETS-1) for fragment in fragments]
    chars.extend([0] * (CHAR_SLOTS - len(chars)))
    if word.isdecimal():
        shape = 1 + min(len(word), 4)
    elif word.isupper():
        shape = 6
    elif word[:1].isupper():
        shape = 7
    else:
        shape = 1 if word.isalpha() else 0
    return key, shape, chars


def encode(matches, vocabulary, members=()):
    features = [token_features(match.group()) for match in matches]
    sequence = [feature[0] for feature in features]
    roster = [tuple(lexical_key(match.group()) for match in tokens(name)) for name in members]
    first_names = [name[0] for name in roster if name]
    known = {name for name in roster if name}
    known.update((first,) for first in first_names if first_names.count(first) == 1)
    by_first = {}
    for name in known:
        by_first.setdefault(name[0], []).append(name)
    name_positions = set()
    for i, key in enumerate(sequence):
        for name in by_first.get(key, ()):
            if tuple(sequence[i:i+len(name)]) == name:
                name_positions.update(range(i, i + len(name)))
    word = np.array([vocabulary.get(f[0], 1) for f in features], dtype=np.int64)
    shape = np.array([f[1] + (8 if i in name_positions else 0) for i, f in enumerate(features)], dtype=np.int64)
    char = np.array([f[2] for f in features], dtype=np.int64)
    return word, shape, char


def probabilities(logits, temperature):
    scores = logits / temperature
    exponent = np.exp(scores - scores.max(axis=-1, keepdims=True))
    return exponent / exponent.sum(axis=-1, keepdims=True)


def decode_spans(text, matches, scores):
    spans = []
    # Optimize the complete tag path instead of deciding span boundaries token by token.
    breaks = [True, *(
        any(char in text[previous.end():current.start()] for char in "\r\n")
        for previous, current in zip(matches, matches[1:])
    )]
    log_scores = np.log(np.maximum(scores, 1e-12))
    for field_index, field in enumerate(FIELDS):
        first = None
        token_scores = []
        likelihood = np.array([0., -np.inf, -np.inf])
        path = []
        for row, line_break in zip(log_scores[:, field_index, :], breaks):
            best = int(likelihood.argmax())
            inside = int(likelihood[2] > likelihood[1]) + 1
            path.append((best, best, inside))
            likelihood = row + [likelihood[best], likelihood[best], -np.inf if line_break else likelihood[inside]]
        tags = [int(likelihood.argmax())]
        for parents in reversed(path[1:]):
            tags.append(parents[tags[-1]])
        for i, (tag, row) in enumerate(zip(reversed(tags), scores[:, field_index, :])):
            if first is not None and tag != 2:
                spans.append(Span(field, matches[first].start(), matches[i-1].end(),
                                  math.prod(token_scores) ** (1 / len(token_scores))))
                first = None
                token_scores = []
            if tag == 1:
                first = i
                token_scores = [float(row[1])]
            elif tag == 2:
                token_scores.append(float(row[2]))
        if first is not None:
            spans.append(Span(field, matches[first].start(), matches[-1].end(),
                              math.prod(token_scores) ** (1 / len(token_scores))))
    return tuple(spans)


class NoticeModel:
    def __init__(self, path=MODEL_PATH):
        with np.load(path, allow_pickle=False) as archive:
            self.metadata = json.loads(str(archive["metadata"]))
            if self.metadata.get("version") != 2 or self.metadata.get("fields") != list(FIELDS):
                raise ValueError("Unsupported Relay NLU artifact")
            self.weights = {name: archive[name] for name in archive.files if name != "metadata"}
        self.vocabulary = self.metadata["vocabulary"]
        expected = {"word.weight": (len(self.vocabulary) + 2, 40), "shape.weight": (SHAPES, 6),
                    "char.weight": (CHAR_BUCKETS, 18)}
        for suffix in ("", "_reverse"):
            expected.update({"gru.weight_ih_l0" + suffix: (144, 64), "gru.weight_hh_l0" + suffix: (144, 48),
                             "gru.bias_ih_l0" + suffix: (144,), "gru.bias_hh_l0" + suffix: (144,)})
        for head, size in (("slots", len(FIELDS)*3), ("kind", len(KINDS)), ("intent", len(INTENTS))):
            expected.update({head + ".weight": (size, 96), head + ".bias": (size,)})
        if any(self.weights[key].shape != shape or self.weights[key].dtype != np.float32 or
               not np.isfinite(self.weights[key]).all() for key, shape in expected.items()):
            raise ValueError("Invalid Relay NLU weights")

    def context(self, inputs, suffix):
        w = self.weights
        hidden = np.zeros(w["gru.bias_hh_l0" + suffix].size // 3, dtype=np.float32)
        projected = inputs @ w["gru.weight_ih_l0" + suffix].T + w["gru.bias_ih_l0" + suffix]
        result = []
        for row in projected[::-1] if suffix else projected:
            source_r, source_z, source_n = np.split(row, 3)
            hidden_r, hidden_z, hidden_n = np.split(
                w["gru.weight_hh_l0" + suffix] @ hidden + w["gru.bias_hh_l0" + suffix], 3)
            reset, update = 1 / (1 + np.exp(-np.clip([source_r + hidden_r, source_z + hidden_z], -40, 40)))
            candidate = np.tanh(source_n + reset * hidden_n)
            hidden = (1 - update) * candidate + update * hidden
            result.append(hidden)
        return np.stack(result[::-1] if suffix else result)

    def logits(self, matches, members=()):
        word, shape, char = encode(matches, self.vocabulary, members)
        w = self.weights
        inputs = np.concatenate((w["word.weight"][word], w["shape.weight"][shape],
                                 w["char.weight"][char].sum(axis=1) / np.maximum(1, (char != 0).sum(axis=1, keepdims=True))), axis=1)
        inputs = inputs.astype(np.float32)
        context = np.concatenate((self.context(inputs, ""), self.context(inputs, "_reverse")), axis=1)
        pooled = context.mean(axis=0)
        def project(name, matrix):
            return matrix @ w[name + ".weight"].T + w[name + ".bias"]
        return project("slots", context).reshape(-1, len(FIELDS), 3), project("kind", pooled), project("intent", pooled)

    def posteriors(self, matches, members):
        slots, kind, intent = self.logits(matches, members)
        temperatures = self.metadata["temperatures"]
        return (probabilities(slots, np.array(temperatures["slots"])[:, None]),
                probabilities(kind, temperatures["kind"]), probabilities(intent, temperatures["intent"]))

    def predict(self, text, members=()):
        matches = tokens(text)
        if not matches or len(matches) > MAX_TOKENS:
            return None
        slot_scores, kind, intent = self.posteriors(matches, members)
        return Prediction(KINDS[int(kind.argmax())], float(kind.max()), INTENTS[int(intent.argmax())],
                          float(intent.max()), decode_spans(text, matches, slot_scores))


class NoticeEnsemble(NoticeModel):
    """Mix calibrated scores while retaining the verified clock and roster heads."""
    def __init__(self, primary, reference):
        self.primary = primary
        self.reference = reference

    def posteriors(self, matches, members):
        slots, kind, intent = self.primary.posteriors(matches, members)
        other_slots, other_kind, other_intent = self.reference.posteriors(matches, members)
        weight = np.array([0. if field in ("time", "person", "responsibility") else .75
                           for field in FIELDS])[None, :, None]
        return (slots * weight + other_slots * (1 - weight),
                .75 * kind + .25 * other_kind, .75 * intent + .25 * other_intent)


@lru_cache(maxsize=1)
def deployed_model():
    models = []
    for path in (MODEL_PATH, REFERENCE_PATH):
        try:
            models.append(NoticeModel(path))
        except (OSError, ValueError, KeyError, BadZipFile):
            continue
    if len(models) == 2:
        return NoticeEnsemble(*models)
    return models[0] if models else None
