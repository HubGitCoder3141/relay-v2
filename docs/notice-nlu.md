# Relay notice understanding

Relay trains and serves a local contextual model. Pasted messages stay inside the Relay server and model process. The model returns source spans that Relay can use in a pending suggestion. The reviewer still decides what becomes a plan.

## Model and runtime

The PyTorch model embeds case-folded words, hashed character trigrams and token shape with a roster-membership feature. A two-direction GRU shares context between nine independent BIO span heads and two message-level classifiers. Character features help represent new names and words. Word masking and dropout reduce reliance on memorized phrases. Each span head assigns its own role, so the location can be inside an instruction and the same message can distinguish a child from a responsible caregiver. The message heads predict plan type and whether the message schedules, updates or cancels a plan, names multiple events, or has insufficient plan information.

The relation model binds typed spans to one plan frame. It distinguishes roles such as start time, deadline, affected person and responsible person. It does not assemble a graph of multiple events. Messages classified as cancellations or containing multiple activities stay in review. The integration keeps explicit field evidence, applies field-specific model thresholds, verifies date and time values, and restricts people to the household roster. Dates relative to a message require its original sent date. A unique first name can resolve to a roster entry, with the inference visible in review.

For “soccer practice is Tuesday at 5 PM … Meet Coach Alex at the community field by 4:45,” the event time is 5 PM. The earlier number stays in the instruction. Coach Alex is a contact in that instruction. The affected person, caregiver responsibility, and separate due date need supporting information.

The exported NPZ contains only weights, vocabulary and scalar temperatures. Vercel uses NumPy for CPU inference and loads the weights once per warm process. Training uses PyTorch. The server caps model input at 192 tokens and uses the deterministic intake path for longer messages or a missing model. Preprocessing masks quoted history and mail headers while preserving source offsets. Exact text spans, model scores and inference notes are persisted with the draft in the existing evidence field. The API creates pending suggestions only. It does not approve plans or submit actions.

## Reproduce and evaluate

From the repository root with Python 3.12 or newer:

```powershell
python -m pip install -r requirements-training.txt
$env:OPENBLAS_NUM_THREADS = '1'
python -m tools.train_nlu --epochs 15 --per-frame 22
"Hey, soccer practice is Tuesday at 5 PM. Bring cleats and water. Meet Coach Alex at the community field by 4:45." |
  python -m tools.predict_nlu --source-date 2026-11-23
```

Optional `--train`, `--calibration`, and `--test` take UTF-8 JSONL. Each row contains `text`, `kind`, `intent`, an optional `members` roster, and a `spans` list of objects with `field`, `start` and `end`. Offsets are zero-based Python character offsets, inclusive at the start and exclusive at the end. Span boundaries must align with tokenizer boundaries. Split by household and message thread or template family before writing the JSONL. Keep consented evaluation data and its labels outside Git and deployment bundles. Run `python -m tools.train_nlu --evaluate-only --test <path>` to evaluate a compatible artifact without retraining.

Training uses weighted per-token cross entropy, separate kind and intent losses, AdamW and gradient clipping. Temperature fitting uses a calibration split. Export checks PyTorch and NumPy logits agree before replacing the artifact. Evaluation reports exact-span micro and per-field precision, recall and F1, intent/type accuracy, approximate span calibration error and warm CPU latency. Temperatures are fitted for token scores. The displayed span score aggregates token scores and needs calibration against a larger independent corpus before it can be treated as an accuracy probability.

The checked-in artifact used 5,642 generated training examples, nine calibration messages and ten separately written synthetic evaluation messages. Raw exact-span precision was 0.697, recall 0.742 and F1 0.719 on that set. Plan type and message intent each matched all ten labels. Warm CPU p95 was about 1.8 ms for model inference alone. Field coverage varied, and the few person and responsibility examples are insufficient to establish reliability. These examples were used during development and do not estimate live accuracy.

## Architecture recommendation

| Approach | Fit for Relay |
|---|---|
| Custom contextual span model | Implemented baseline with small artifacts, cheap inference and inspectable evidence. Its language coverage depends heavily on labeled examples. |
| Pretrained bidirectional transformer | Stronger next candidate for unfamiliar wording. Fine-tune the same field and intent heads from a compact pretrained encoder and compare both models on the same household-held-out data. |
| Fine-tuned generative model | Can handle richer language and multiple events. Keep output schema-constrained and enforce evidence alignment, date validation and abstention. Benchmark the extra latency and unnecessary fields it may introduce. |
| Hybrid structured extraction | Recommended. Pair learned role extraction with deterministic date resolution, roster matching, ambiguity handling and approval. Preserve these safeguards when changing the encoder. |

The primary dataset should be consented, redacted family notices annotated for exact spans, normalized dates, participant roles, cancellation and multiple events. Keep separate slices for sports, school, appointments, forwarded threads and ambiguous dates. Use synthetic notices for coverage and safe regressions. MATRES can supplement temporal-relation evaluation, and OntoNotes can supplement entity and predicate-argument evaluation, subject to their licenses. Neither provides a representative household test set. Review correction patterns from separately consented examples and select ambiguous or high-disagreement cases for a second annotation round. [MATRES research](https://aclanthology.org/P18-1122/) · [OntoNotes catalog and license](https://catalog.ldc.upenn.edu/products/LDC2013T19)

Relevant research includes [neural sequence labeling](https://aclanthology.org/N16-1030/), [compact bidirectional entity extraction](https://aclanthology.org/2024.naacl-long.300/), and [multi-axis temporal relations](https://aclanthology.org/P18-1122/).

## Release and monitoring

Local and protected Preview load the bundled model by default. Production requires `RELAY_NLU_ENABLED=1`. Before enabling it, compare accepted-field precision, coverage, calibration and correction rates against the current release on an independent set. Pay particular attention to event times, deadlines, cancellation and caregiver attribution. Measure warm and cold HTTP latency on the hosted target. Set `RELAY_NLU_ENABLED=0` and redeploy to roll back to the deterministic path. No schema migration is required.

Web and mobile browsers use the same server endpoint and receive only the suggestion and evidence. The CPU timing in the training report excludes network time and serverless cold start. If offline extraction becomes necessary, export a quantized ONNX or mobile-friendly encoder and verify parity plus memory and latency on actual devices first.
