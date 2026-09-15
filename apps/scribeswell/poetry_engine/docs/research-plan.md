# Psalm Poetry Engine: first research slice

## Repository assessment and product brief

Scribeswell already supplies a Hebrew reader and a repaired reference database.
Its source export lacks original MorphHB token IDs and dataset revision metadata.
A separate local MorphHB checkout is available at `/home/ck/repos/temp/morphhb`
(commit `3d15126fb1ef74867fc1434be1942e837932691f`). The engine should read licensed
source files directly; it must not infer canonical source identifiers from database
surrogate keys. The existing 25 research PDFs have not yet been bibliographically
reviewed. At initial assessment no BHSA dataset or translation-provider configuration was found.
The pinned BHSA features have since been acquired and verified. The user selected
Cline’s `cline` provider and `anthropic/claude-sonnet-5` for poetic Afrikaans Psalm 23.

Help qualified translators compare Afrikaans Psalm drafts while retaining evidence,
ambiguity and poetic structure. First research question: does an explicit canonical
representation improve preservation enough to reduce human revision effort?
Psalm 23 demonstrates the pipeline; it cannot establish general effectiveness.

## Architecture proposal and decisions

A small installable Python package, independent of the existing API and database.
Pydantic validates versioned source, alignment, annotation and translation records.
MorphHB OSIS XML and local Text-Fabric BHSA adapters preserve source IDs and hashes.
Alignment is verse-local and supports contiguous token groups in either source;
unmatched tokens remain explicit. Consonantal agreement is an alignment heuristic,
not evidence that vowel forms, interpretations or token analyses are identical.

JSON/JSONL is the persistence boundary. Outputs use exclusive creation and unique
run IDs. A provider-neutral generator accepts a structured request and returns a
validated response. The first concrete adapter invokes a configured executable
with JSON on stdin (no shell); this supports provider SDKs without importing them
into the domain. Requests can also be exported for external generation and results
imported with declared model/settings. No RAG, embeddings, fine-tuning or multi-agent
system. No UI/API layer until the research pipeline is useful.

The representation includes source tokens, source structures, normalized text,
alignment, evidence-bearing analytical claims, translation constraints and reviewed
poetic principles. Open categories allow future semantics, discourse, song constraints
and competing interpretations without pretending these analyses already exist.
Source facts and imported annotations are distinct from rules, model proposals and
human review. Unknown is preferable to invented linguistic facts.

## Phases and acceptance

1. Repair and independently audit Scribeswell data; fail on skipped records.
2. Load real Psalm 23 MorphHB and BHSA, preserve source versions/hashes, align every
   token or mark it unmatched, and produce validated representation and audit JSON.
3. Prepare A (Hebrew), B (+MorphHB), C (+BHSA/representation), D (+reviewed PDF
   principles from guide appendices B/C only). Keep model, output mode, language and settings constant. Do not
   silently run C without BHSA or D without human-approved PDF principles.
4. Generate and store exact requests/responses, timing, provider-reported usage,
   model/settings, prompt version, input hashes and code revision. Save comparative
   report and blank rubric. Tests use conspicuously synthetic generator output;
   never present a test run as research evidence.
5. Qualified humans review annotations and score candidate quality, critical errors,
   ambiguity, imagery, poetry and revision effort. Expand the Psalm set only after
   the first complete evaluated run.

A technical preparation run may finish without provider access. A research milestone
requires actual generated drafts and actual human review; neither can be simulated
and called complete. No claim of singability without melody constraints.

## Assumptions and open questions

- The user confirmed this is a free, noncommercial project; BHSA's dataset restrictions differ
  from its repository software license (see THIRD_PARTY_DATA.md).
- Afrikaans, general adult audience, natural contemporary register, poetic draft
  are defaults. Target audience/register and theological terminology remain editable.
- The user chooses the provider/model and supplies credentials through their local
  provider runner. No API keys are stored in experiment records.
- Reviewed Psalm 23 analysis and reviewed PDF principles require a named human;
  machine-created proposals stay pending until that happens.
- Verse numbering and ketiv/qere differences require explicit inspection. The first
  MorphHB adapter reads main-text word nodes and records excluded alternative-reading
  notes; it does not silently mix them into a source stream.
- Full scholarly accuracy of the old reader's morphology parser is outside the
  database repair. The experiment preserves raw MorphHB/ETCBC annotations.

## Delivery impacts

User explicitly exempted this research task from BMAD. No platform/scaffold/shared-UI
changes; no cross-silo runtime dependency or accepted ADR changes. This document
records prototype decisions, not a new generic workflow. The master brief remains
the research requirements source. Agent context: fail on invalid or incomplete
required evidence; preserve uncertainty rather than replacing it with empty success.

## Guide scope correction — 2026-09-12

Use only Appendix B: Exegetical Layout and Appendix C: Flower Garden from all
supplied guides. Ignore all ten steps/three phases, the introduction, Appendix A
and every other section. The prior Psalm 23 page-17 approval is historical and
ineligible under this scope. Extraction, review export, new prompts and execution
of saved requests enforce the restriction. See `guide-review.md` for verification.
No scaffold/shared-UI, platform or ADR changes; local agent instructions updated.
