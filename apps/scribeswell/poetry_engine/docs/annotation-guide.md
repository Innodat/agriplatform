# Human annotation guide

JSONL is the canonical exchange format: one Claim per line. CSV is a flattened review
view and does not preserve full evidence. The initial files are machine proposals;
do not treat them as approved human analysis.

`id` identifies an analytical claim; `category` is an extensible feature name such as
metaphor, parallelism, inclusio, discourse, ambiguity or poetry_principle. `value` is
a concise proposition, not a long quotation. `scope` identifies source tokens when
applicable. `evidence` names source IDs and locators; PDF evidence needs a page number.
Evidence must exist in the representation. Source IDs are original MorphHB IDs or BHSA
nodes qualified by dataset; neither is a database row ID.

`method` distinguishes imported annotations, deterministic rules, LLM proposals and
human analyses. Approval does not change the original method: a reviewed LLM proposal
still originated with an LLM. `confidence` is optional and is not a calibrated
probability. Unknown should remain null; do not create certainty to fill a field.

A human reviewer sets `reviewer_status` to approved, rejected or disputed, supplies a
stable reviewer name/identifier and explains the decision in `reviewer_notes`. Keep
the original file. Save the revision to a new JSONL file, increment `revision` and
link `supersedes`. Different annotators can submit separate claims/revisions with
conflicting values. Use `alternatives` and reviewer notes to explain disagreements;
adjudication is a later named human revision, not an automatic majority vote.

For principles, include diagnostic indicators, constraints, examples and counterexamples
when available. Do not force a parallelism class onto every verse. Do not conflate
semantic interpretation with lexical facts or treat every PDF statement as scholarship
accepted by all analysts. In particular, the supplied Psalm 23 PDF contains interpretive
claims that need assessment; extraction does not turn them into translation constraints.

The sample proposes preserving the shepherd image in Psalm 23:1. Its separate PDF
principle proposes checking parallel relationships and imagery during evaluation.
Both are pending. A programmer or model must not invent your review or mark them
approved to make condition D run.
