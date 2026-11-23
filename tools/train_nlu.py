"""Train, calibrate, evaluate, and export Relay's CPU model.

Run from the repository root with python -m tools.train_nlu.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
from time import perf_counter

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader

from relay_nlu import (CHAR_BUCKETS, CHAR_SLOTS, FIELDS, INTENTS, KINDS, MAX_TOKENS,
                       MODEL_PATH, SHAPES, NoticeEnsemble, NoticeModel, encode, lexical_key, probabilities, tokens)
from tools.nlu_data import Example, evaluation_examples, training_examples


class Network(nn.Module):
    def __init__(self, words):
        super().__init__()
        self.word = nn.Embedding(words, 40, padding_idx=0)
        self.shape = nn.Embedding(SHAPES, 6)
        self.char = nn.Embedding(CHAR_BUCKETS, 18, padding_idx=0)
        self.gru = nn.GRU(64, 48, batch_first=True, bidirectional=True)
        self.dropout = nn.Dropout(0.16)
        self.slots = nn.Linear(96, len(FIELDS) * 3)
        self.kind = nn.Linear(96, len(KINDS))
        self.intent = nn.Linear(96, len(INTENTS))

    def forward(self, word, shape, chars, lengths):
        if self.training:
            # Make the character channel useful on names and words absent from training.
            word = torch.where((torch.rand_like(word, dtype=torch.float32) < 0.13) & (word > 1), 1, word)
        character = self.char(chars).sum(2) / (chars != 0).sum(2, keepdim=True).clamp(min=1)
        embedded = self.dropout(torch.cat((self.word(word), self.shape(shape), character), dim=-1))
        packed = nn.utils.rnn.pack_padded_sequence(embedded, lengths, batch_first=True, enforce_sorted=False)
        context, _ = self.gru(packed)
        context, _ = nn.utils.rnn.pad_packed_sequence(context, batch_first=True)
        context = self.dropout(context)
        pooled = context.sum(1) / lengths[:, None]
        return self.slots(context).reshape(*context.shape[:2], len(FIELDS), 3), self.kind(pooled), self.intent(pooled)


def labels_for(example, matches):
    labels = np.zeros((len(matches), len(FIELDS)), dtype=np.int64)
    for field, start, end in example.spans:
        indexes = [i for i, match in enumerate(matches) if match.start() >= start and match.end() <= end]
        if not indexes or matches[indexes[0]].start() != start or matches[indexes[-1]].end() != end:
            raise ValueError(f"Span for {field} must align with tokens: {example.text[start:end]!r}")
        j = FIELDS.index(field)
        if labels[indexes, j].any():
            raise ValueError("Overlapping spans of the same field")
        labels[indexes, j] = [1] + [2] * (len(indexes) - 1)
    return labels


def rows_for(examples, vocabulary):
    rows = []
    for example in examples:
        matches = tokens(example.text)
        if not matches or len(matches) > MAX_TOKENS:
            raise ValueError("Example is empty or exceeds model input length")
        rows.append((*encode(matches, vocabulary, example.members), labels_for(example, matches),
                     KINDS.index(example.kind), INTENTS.index(example.intent)))
    return rows


def batch(items):
    lengths = torch.tensor([len(item[0]) for item in items])
    size = (len(items), int(lengths.max()))
    word = torch.zeros(size, dtype=torch.long)
    shape = torch.zeros_like(word)
    chars = torch.zeros((*size, CHAR_SLOTS), dtype=torch.long)
    labels = torch.full((*size, len(FIELDS)), -100, dtype=torch.long)
    for i, (w, s, c, y, _, _) in enumerate(items):
        length = len(w)
        word[i, :length], shape[i, :length], chars[i, :length], labels[i, :length] = map(torch.from_numpy, (w, s, c, y))
    return word, shape, chars, lengths, labels, torch.tensor([item[4] for item in items]), torch.tensor([item[5] for item in items])


def calibrate(logits, target):
    # Fit a single scalar with held-out negative log likelihood.
    def loss(temperature):
        values = probabilities(logits, temperature)
        return -np.log(np.maximum(1e-9, values[np.arange(len(target)), target])).mean()
    return float(min(np.linspace(0.6, 3.5, 30), key=loss))


def score(examples, model):
    correct = predicted = expected = kind_hits = intent_hits = 0
    counts = {field: [0, 0, 0] for field in FIELDS}
    bins = [[0, 0, 0.0] for _ in range(10)]
    latency = []
    for example in examples:
        start = perf_counter()
        result = model.predict(example.text, example.members)
        latency.append((perf_counter() - start) * 1000)
        actual = {(s.field, s.start, s.end) for s in result.spans if s.confidence >= 0.65}
        truth = set(example.spans)
        overlap = actual & truth
        correct += len(overlap)
        predicted += len(actual)
        expected += len(truth)
        kind_hits += result.kind == example.kind
        intent_hits += result.intent == example.intent
        for field, column in counts.items():
            for i, values in enumerate((overlap, actual, truth)):
                column[i] += sum(row[0] == field for row in values)
        for span in result.spans:
            n = min(int(span.confidence * 10), 9)
            bins[n][0] += 1
            bins[n][1] += (span.field, span.start, span.end) in truth
            bins[n][2] += span.confidence
    def prf(hit, found, gold):
        return {"precision": round(hit / max(found, 1), 3), "recall": round(hit / max(gold, 1), 3),
                "f1": round(2 * hit / max(found + gold, 1), 3), "support": gold}
    return {
        "examples": len(examples), "span_exact": prf(correct, predicted, expected),
        "field_exact": {key: prf(*value) for key, value in counts.items()},
        "kind_accuracy": round(kind_hits / len(examples), 3), "intent_accuracy": round(intent_hits / len(examples), 3),
        "span_ece": round(sum(abs(hits - confidence) for _, hits, confidence in bins) / max(1, sum(row[0] for row in bins)), 3),
        "p95_ms": round(float(np.percentile(latency, 95)), 2),
    }


def load_rows(path):
    with Path(path).open(encoding="utf-8") as file:
        data = [json.loads(line) for line in file if line.strip()]
    return [Example(row["text"], row["kind"], row["intent"],
                    tuple((slot["field"], slot["start"], slot["end"]) for slot in row["spans"]),
                    tuple(row.get("members", ()))) for row in data]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=18)
    parser.add_argument("--per-frame", type=int, default=20)
    parser.add_argument("--seed", type=int, default=41)
    parser.add_argument("--train")
    parser.add_argument("--calibration")
    parser.add_argument("--test")
    parser.add_argument("--output", type=Path, default=MODEL_PATH)
    parser.add_argument("--evaluate-only", action="store_true")
    parser.add_argument("--challenge", action="store_true", help="Evaluate the separate versioned challenge set")
    parser.add_argument("--release-check", action="store_true", help="Evaluate the fixed post-selection set")
    parser.add_argument("--reference", type=Path, help="Include a reference artifact when evaluating")
    args = parser.parse_args()
    torch.set_num_threads(2)
    torch.manual_seed(args.seed)
    torch.use_deterministic_algorithms(True)
    examples = load_rows(args.train) if args.train else training_examples(args.seed, args.per_frame)
    calibration = load_rows(args.calibration) if args.calibration else evaluation_examples("calibration")
    test = load_rows(args.test) if args.test else evaluation_examples("test")
    if args.challenge or args.release_check:
        from tools.nlu_challenge import examples as challenge_examples
        test = challenge_examples(release=args.release_check)
    if args.evaluate_only:
        candidate = NoticeModel(args.output)
        if args.reference:
            candidate = NoticeEnsemble(candidate, NoticeModel(args.reference))
        print(json.dumps(score(test, candidate), indent=2))
        return
    splits = [{row.text for row in split} for split in (examples, calibration, test)]
    if not all(splits) or splits[0] & splits[1] or splits[0] & splits[2] or splits[1] & splits[2]:
        raise ValueError("Train, calibration, and test sets must be nonempty and distinct")
    frequencies = Counter(lexical_key(match.group()) for row in examples for match in tokens(row.text))
    vocabulary = {word: i + 2 for i, (word, _) in enumerate(frequencies.most_common(2500))}
    data = DataLoader(rows_for(examples, vocabulary), batch_size=64, shuffle=True, collate_fn=batch,
                      generator=torch.Generator().manual_seed(args.seed))
    model = Network(len(vocabulary) + 2)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.003)
    weights = torch.tensor([0.35, 2., 1.])
    for epoch in range(args.epochs):
        total = 0.
        for word, shape, chars, length, labels, kind, intent in data:
            optimizer.zero_grad()
            slots, categories, acts = model(word, shape, chars, length)
            loss = (F.cross_entropy(slots.reshape(-1, 3), labels.flatten(), weight=weights) +
                    0.55 * F.cross_entropy(categories, kind) + 0.55 * F.cross_entropy(acts, intent))
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 2.)
            optimizer.step()
            total += float(loss.detach())
        if epoch == 0 or (epoch + 1) % 3 == 0:
            print(f"Epoch {epoch + 1}: objective {total / len(data):.4f}", flush=True)

    model.eval()
    word, shape, chars, length, y, k, a = batch(rows_for(calibration, vocabulary))
    with torch.inference_mode():
        slots, kinds, intents = [value.numpy() for value in model(word, shape, chars, length)]
    labels = y.numpy()
    slot_temperatures = []
    for j in range(len(FIELDS)):
        valid = labels[:, :, j] >= 0
        slot_temperatures.append(calibrate(slots[:, :, j, :][valid], labels[:, :, j][valid]))
    metadata = {"version": 2, "fields": list(FIELDS), "vocabulary": vocabulary, "seed": args.seed,
                "epochs": args.epochs, "per_frame": args.per_frame,
                "train_examples": len(examples), "calibration_examples": len(calibration),
                "temperatures": {"slots": slot_temperatures, "kind": calibrate(kinds, k.numpy()),
                                 "intent": calibrate(intents, a.numpy())}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    candidate = args.output.with_suffix(".candidate.npz")
    with candidate.open("wb") as artifact:
        np.savez_compressed(artifact, metadata=json.dumps(metadata),
                            **{name: value.numpy() for name, value in model.state_dict().items()})
    exported = NoticeModel(candidate)
    first = tokens(calibration[0].text)
    for numpy_result, torch_result in zip(exported.logits(first, calibration[0].members), (slots[0, :len(first)], kinds[0], intents[0])):
        np.testing.assert_allclose(numpy_result, torch_result, rtol=1e-4, atol=2e-5)
    candidate.replace(args.output)
    print(json.dumps({"artifact":str(args.output), "bytes":args.output.stat().st_size,
                      "holdout":score(test, exported)}, indent=2))


if __name__ == "__main__":
    main()
