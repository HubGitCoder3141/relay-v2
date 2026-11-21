# Relay intelligence architecture

## V3 implementation

`relay_intake.py` parses explicit source lines using the current household roster. It records the original line number and value alongside the extraction status. Contradictory inputs remain blank in the suggested plan until a reviewer chooses a value. The approved preparation and instructions join each plan version. A revision requires the current approved source ID inside the write transaction. Structured retrieval reads the newest approved version and returns its source ID.

Prioritize a synthetic evaluation corpus with conflicting versions, unseen names, missed obligations, layout variants, and expected abstentions. Treat source revision and authority as part of retrieval evaluation alongside citation validity. [Attribute or Abstain](https://aclanthology.org/2024.emnlp-main.463/)

For future multimodal intake, measure exact field recovery and line or region attribution on varied document layouts before introducing document models. [DocVQA](https://arxiv.org/abs/2007.00398/) For future small-model experiments, compare prompted and fine-tuned candidates against deterministic rules on a held-out dataset before considering distillation. Distillation adds teacher outputs, training compute, and independent quality checks. [Distilling Step-by-Step](https://arxiv.org/abs/2305.02301)

## Working system

Relay keeps household memory in reviewable records. A saved notice supplies the original wording. A caregiver supplies structured fields and approves a new plan or a revision. The current plan carries its supporting source ID. Earlier approved versions retain theirs. The person on a plan is the affected family member. Recording that name does not establish that somebody accepted a responsibility or performed an action.

| Information | Representation and lifetime | Product meaning |
| --- | --- | --- |
| Original information | Source ID and original pasted text, retained after review | A family member can reopen what the notice actually said. |
| Proposed interpretation | Pending source with manually supplied fields and optional target plan | The review queue may contain incomplete, repeated or contradictory notices. |
| Approved memory | Current plan with title, date, time, person and source ID | A reviewer chose the values and the relationship to the plan. External accuracy remains unverified. |
| Historical memory | Prior versions in chronological order, each linked to its source | A change can be explained even after the current date, time or person changes. |
| Follow-through memory | Plan-scoped local action with person and open/done state | Records an internal household step; it does not prove an outside-world result. |
| Derived observation | Read-only result of a comparison or projection | A possible collision, duplicate candidate or absent field prompts inspection. |
| AI interpretation, suggested external actions, caregiver acceptance and real-world completion | Unavailable in this version | Each would require its own provenance, authority and state transition. |

The application obtains the authorized household snapshot from the server. The reasoning module receives only this snapshot. It has no database connection, account discovery, ambient retrieval or mutation tools. Recomputing a briefing or asking a question leaves the snapshot untouched. Browser-rendered insights are informational. The server owns authorization and persistent transitions.

## Processing and memory

1. Intake preserves the pasted notice. It can fill fields only when they use explicit labels and unambiguous ISO values such as `Date: 2026-12-04`, `Time: 16:15`, and `For: Sam`. A reviewer supplies or corrects all other information. Missing time or person remains unspecified, including when a notice reasonably omits a time.
2. Review connects a notice to an existing plan explicitly or creates a plan on approval. Rejection closes the notice. A matching title or repeated notice alone has no authority to merge two plans.
3. A revision retains the previous approved fields and source link. Comparing the immediately preceding version with the current one identifies which fields changed. History can include a change of supporting source with identical structured values.
4. Briefing uses the current approved plans for today and future dates. Pending notices remain visible in their own queue. The default day comes from the viewing device’s calendar date. A caller can supply an ISO date for deterministic evaluation.
5. Lookup returns an answer, a known-empty result, or an explicit unavailable result. References are source and plan IDs. The changes lookup includes the sources for both versions. Pending-review questions return pending sources only.

This schema represents explicit relationships between people, notices, plans and versions. Relationships among caregivers and children, recurring commitments, preferences, places and delegated authority would need additional user-confirmed records and appropriate lifetimes. V1 does not infer family roles from names or infer a routine from repeated entries.

## Read interfaces

The browser and test runner import the same module from `src/intelligence.mjs`.

| Interface | Contract |
| --- | --- |
| `buildBriefing(state, today?)` | Projects today, upcoming plans, pending review, missing fields on pending sources, exact-time conflicts, latest field changes, and open/completed follow-through actions. |
| `describeChanges(previous, current)` | Returns before and after values for title, date, time and person. |
| `findDuplicates(state, source)` | Returns other notices with identical original wording after case and whitespace normalization. Preserves punctuation and all originals. |
| `answerQuestion(state, question, today?)` | Recognizes a bounded set of full question patterns. Supports today, tomorrow, changes, conflicts, pending review and affected people by plan-title words. Returns status, plain text, plan IDs and source IDs. |
| `modelCapabilities` and `interpretSource(request)` | The capability flag is false. The asynchronous boundary returns an unavailable reason and an empty candidate list. No provider, key, model, transport or inference call exists. |

Conflicts require the same nonempty person, date and time on two current plans. This catches a child scheduled for two simultaneous activities. Duration, travel time, caregiver availability, time zones and undated obligations require additional evidence. Blank-field results describe missing recorded information. They do not assign confidence scores or imply a source is wrong. Schedule lookups operate on approved titles and fields. They cannot interpret a notice or answer broad questions about its meaning.

## Trust and future execution

A pasted instruction is household content. It cannot request a tool, modify a plan, authorize disclosure or change the question grammar. Every supported answer is rebuilt from scoped records and has inspectable references when it uses evidence. The system currently supports local synthetic household evaluation. The bounded grammar is deterministic application logic.

If model interpretation becomes authorized, the proposed request contract should include a scoped source reference, exact wording, the minimum necessary context, and schema version. A candidate response should carry a field, proposed value, supporting verbatim range, source ID and any ambiguity. The server should verify that each citation and range belongs to the authorized input, validate the field, persist candidates separately and require a human decision before promoting any candidate. Model failure, invalid output or an unresolvable citation should return the source to manual review. Scope retrieval before any provider call. A model should receive neither database access nor execution authority.

External actions would require a separate server-side executor with explicit operation, recipient, household authorization, a reviewable preview, retry protection and a result receipt. Sending a message, accepting a pickup, observing delivery and completing the pickup represent different events. None is available through lookup.

## Agent strategy and defensibility

Keep interpretation, evidence retrieval, field comparison and scheduling as ordinary modules invoked by a predictable workflow. Each current operation has a bounded input and an independently testable output. Multiple agents would introduce disagreement, difficult replay and more private context exposure without adding an observable benefit to these operations. Consider a bounded investigator only after observing a recurring multi-source question that the simpler workflow fails and obtaining authorization for inference.

Relay-specific opportunities include preserving successive sources behind each decision, distinguishing family roles from responsibility, identifying which people an approved change affects, and evaluating missed changes and false alarms with realistic notice sequences. The present rules and schema are reproducible. Their value must be demonstrated by fewer family coordination mistakes and less review effort in prospective testing.

## Research roadmap and resource gates

| Opportunity | When Relay should investigate | Required resources and evaluation |
| --- | --- | --- |
| Domain-specific evaluation | Now, before model access | Maintain synthetic source sequences and expected fields, supporting IDs, abstentions and transitions. Behavioral tests should include minimal pairs such as a changed time versus a changed date and unsupported qualifiers in a familiar question. [CheckList research](https://aclanthology.org/2020.acl-main.442/) |
| Proprietary datasets | After a consent and deletion model is in place | Start with hand-authored examples. Any later opt-in contribution needs provenance, allowed uses, withdrawal handling, reviewer time and household-separated train/test splits. Document composition, gaps and intended uses. [Datasheets for Datasets](https://arxiv.org/abs/1803.09010) |
| Synthetic generation | When manual examples leave measured coverage gaps | Vary dates, ambiguous names and version order systematically. A future model-generated set needs authorized compute, review, duplicate filtering and a separate human-authored holdout. [Self-Instruct research](https://arxiv.org/abs/2212.10560) |
| Retrieval-augmented generation | When exact supported lookup fails on genuine multi-source questions | Benchmark retrieval against labeled relevant source IDs first. Scoped lexical search is a baseline. Embedding indexes would add authorized inference, storage, deletion and isolation requirements. Measure citation validity, retrieval recall and grounded abstention. [Original RAG research](https://arxiv.org/abs/2005.11401) |
| Small specialized models and fine-tuning | When repeated text-to-field mistakes survive simpler approaches | Compare an authorized small base model with the manual/rule baseline on held-out notices. Adapter tuning can reduce trainable parameters, while weights, licensed data, training hardware, annotation and deployment still require resources. Measure cost per reviewed notice and correction time. [PEFT documentation](https://huggingface.co/docs/peft/en/index) |
| Distillation | When a permitted teacher reliably beats the candidate student and inference cost matters | Budget teacher outputs, student training, licensed examples, validation and maintenance. Require adequate quality on revisions and abstentions after compression. Published benchmark outcomes do not establish household accuracy. [Distilling Step-by-Step](https://aclanthology.org/2023.findings-acl.507/) |
| Multimodal intake | When families demonstrate demand for photographed notices | Compare OCR plus field review with an authorized vision-language model on rotated flyers, fine print and tables. Requires consented or synthetic images, labels, safe file handling and measured compute. Preserve page/region citations. [Transformers image-text documentation](https://huggingface.co/docs/transformers/en/tasks/image_text_to_text) |
| Hybrid symbolic and neural reasoning | When language flexibility demonstrably reduces intake or lookup work | Limit learned components to candidate interpretation or read-only question routing. Keep date arithmetic, permissions, change comparisons and actual writes deterministic. Test end-to-end against the current baseline before exposing a capability. [Tool Augmented Language Models](https://arxiv.org/abs/2205.12255) |

The current module runs in the browser and the existing Node test runner with no model or service expenditure. Future hardware and financial estimates require measurements of notice volume, token/image sizes, serving constraints and model licenses. No future processing or spending has been authorized.

## Verification

Run `node --test tests/intelligence.test.mjs`. The synthetic household crosses a year boundary, changes its choir time, double-books one person, leaves a library plan untimed and submits an incomplete notice. Cases exercise change provenance, exact conflict pairs, repeated wording, suppressed superseded times, unknown people, unavailable interpretation, empty lookups and read-only behavior. These are regression checks over explicit examples. Household-specific precision, recall, review time, perceived usefulness and willingness to pay remain unmeasured.
