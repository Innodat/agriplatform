You are acting as a senior Python engineer, computational linguist, NLP researcher, and solution architect.

Build a working research prototype called:

Psalm Poetry Engine

# 1. Purpose

The system will assist Bible translators in creating draft song-oriented translations of the Psalms.

The first target language is Afrikaans because I can evaluate Afrikaans output myself.

The longer-term goal is to support gateway languages such as:

- Spanish
- Portuguese
- French
- Swahili

This is not intended to replace Bible translators. The system must generate transparent, reviewable draft translations for qualified translators, poets, musicians, and translation consultants to evaluate and revise.

The prototype must implement this complete vertical flow:

Biblical Hebrew Psalm
    -> MorphHB linguistic data
    -> ETCBC linguistic data
    -> poetic annotations extracted from research PDFs
    -> Canonical Psalm Representation
    -> LLM translation prompt
    -> Afrikaans draft translation
    -> structured human evaluation

# 2. Central Research Hypothesis

Direct LLM translation from Biblical Hebrew into a target language often loses or weakens important poetic characteristics.

The prototype should test whether an intermediate Canonical Psalm Representation improves the preservation of:

- semantic meaning
- theological meaning
- Hebrew imagery
- metaphor
- poetic line structure
- synonymous parallelism
- antithetical parallelism
- synthetic or developmental parallelism
- repetition
- keywords and lexical links
- inclusio
- chiasm, when defensibly identified
- discourse progression
- emotional progression
- rhetorical emphasis
- suitability for later song adaptation

The Canonical Psalm Representation is the primary output of the Psalm analysis stage.

The Afrikaans translation is generated from this representation and the underlying source evidence.

# 3. Important Architectural Decision

Do not build this as a RAG chatbot.

Do not introduce a vector database in the first prototype.

Do not implement a complex multi-agent architecture.

Do not fine-tune a model yet.

Do not train a transformer from scratch yet.

Do not build a full BMAD implementation.

Use a lightweight, research-oriented development process with:

- a short product brief
- explicit research questions
- architectural decisions
- experiment definitions
- acceptance criteria
- evaluation results
- documented assumptions

The first objective is to validate that the Canonical Psalm Representation is useful.

Use the simplest architecture that can test this hypothesis.

# 4. Technology Requirements

Use:

- Python 3.12 or a currently supported Python version
- Pydantic v2 for schemas and validation
- FastAPI for the optional API layer
- pytest for tests
- Jupyter notebooks for exploration
- Pandas where tabular analysis is useful
- JSON or JSONL for portable datasets
- SQLite for local experiment metadata if persistence is required
- PyMuPDF or another suitable Python PDF extraction library
- provider-neutral LLM interfaces

Keep core domain logic independent of FastAPI and independent of any specific LLM provider.

The application must be runnable locally.

Use environment variables for secrets.

Include:

- pyproject.toml
- .env.example
- README.md
- type hints
- logging
- tests
- sample data
- command-line entry points

Prefer small, composable Python modules over a large framework.

# 5. Data Sources

The initial system should support two principal Biblical Hebrew linguistic sources:

## MorphHB

Use MorphHB for information such as:

- Hebrew surface form
- lexical form
- lemma
- morphology
- part of speech
- grammatical features
- Strong's references where available
- verse and word alignment

## ETCBC

Use ETCBC data for information such as:

- books, chapters, verses, sentences, clauses, phrases, and words
- phrase and clause boundaries
- syntactic functions
- grammatical relationships
- discourse-related features where present
- word-level and phrase-level linguistic annotations

Prefer Text-Fabric when it is the appropriate supported way to access ETCBC/BHSA data.

Do not assume that MorphHB and ETCBC have identical tokenization.

Implement an alignment layer that:

1. preserves both source identifiers;
2. normalizes Hebrew carefully;
3. handles cantillation and vowel marks explicitly;
4. records uncertain alignments;
5. never silently drops unmatched tokens;
6. allows one-to-one, one-to-many, and many-to-one token mappings;
7. emits an alignment report.

Do not redistribute source corpora unless their licenses explicitly permit it.

Create scripts that allow an authorized user to place or fetch datasets according to the respective license terms.

Before implementing data download or redistribution:

- inspect the current license of every source;
- record the source URL;
- record the license identifier;
- record attribution requirements;
- record commercial and redistribution restrictions;
- distinguish software license from dataset license;
- fail safely when data is not locally available.

Add a THIRD_PARTY_DATA.md file and a machine-readable data_sources.yaml file.

If licensing is unclear, document the uncertainty instead of guessing.

# 6. PDF-Based Poetic Research

I will supply PDFs containing research and guidance about Biblical Hebrew poetry.

The prototype must support ingesting those PDFs into a research evidence layer.

The PDFs must not initially be treated as unrestricted training data.

Implement a PDF ingestion process that:

1. extracts text page by page;
2. preserves document title and page number;
3. creates stable source identifiers;
4. records bibliographic metadata;
5. stores short evidence excerpts or structured notes only where legally appropriate;
6. separates source evidence from model-generated interpretation;
7. allows a human reviewer to approve extracted poetic principles;
8. records confidence and provenance.

Create a schema for poetic principles such as:

- principle ID
- name
- description
- feature type
- diagnostic indicators
- constraints
- examples
- counterexamples
- source document
- page number
- reviewer status
- reviewer notes

The system must not treat every statement extracted from a PDF as fact.

Use the PDF material to build a reviewed poetic framework, not merely a bag of retrieved text.

For the MVP, retrieval can be deterministic and metadata-based. Do not add embeddings unless an experiment later demonstrates that they are necessary.

# 7. Canonical Psalm Representation

Design a versioned Pydantic schema called CanonicalPsalmRepresentation.

The representation must distinguish between:

1. source facts;
2. imported linguistic annotations;
3. rule-derived analysis;
4. LLM-proposed interpretation;
5. human-reviewed interpretation.

Every interpretive field should support:

- value
- confidence
- evidence
- provenance
- method
- reviewer status
- reviewer notes

The schema should support both a whole psalm and smaller units such as:

- stanza
- strophe
- verse
- colon
- line
- clause
- phrase
- token

At minimum, include the following sections.

## Identity and versioning

- schema version
- representation ID
- source dataset versions
- creation timestamp
- updated timestamp
- pipeline version
- Psalm reference

## Source text

- Hebrew with cantillation
- Hebrew without cantillation
- Hebrew consonantal form
- transliteration, if available
- token identifiers
- line and verse boundaries

## Lexical analysis

For each token:

- surface form
- normalized form
- lemma
- glosses
- part of speech
- morphology
- Strong's identifier where available
- MorphHB identifier
- ETCBC identifier
- semantic possibilities
- ambiguity notes

Do not reduce a Hebrew word to a single English gloss when ambiguity is meaningful.

## Syntax and discourse

- clauses
- phrases
- subjects and predicates where available
- syntactic relationships
- discourse relationships
- participants
- changes in speaker or addressee
- tense, aspect, and modality observations
- ellipsis where defensibly identified

## Semantic content

- conservative literal proposition
- semantic roles
- entities
- actions
- relationships
- ambiguities
- translation hazards
- cultural concepts
- theological terms
- constraints that must not be lost

## Poetic analysis

- cola or poetic lines
- line groupings
- parallelism type
- correspondence between lines
- repeated words, roots, sounds, or concepts
- contrast
- progression
- metaphor
- imagery
- symbols
- wordplay
- alliteration or assonance where defensible
- chiasm
- inclusio
- acrostic structure
- refrain
- rhetorical questions
- imperatives
- emphasis
- emotional movement
- genre
- uncertainty and competing analyses

Do not force every verse into a parallelism category.

Allow null, unknown, disputed, and multiple proposed analyses.

## Translation brief

- target language
- target audience
- translation purpose
- translation philosophy
- required preserved features
- negotiable features
- terms requiring special attention
- desired register
- line constraints
- song adaptation constraints

## Translation outputs

Support at least three output modes:

1. literal study rendering;
2. poetic draft translation;
3. song-oriented draft.

For each candidate record:

- candidate text
- line divisions
- source representation version
- model provider
- model identifier
- generation settings
- prompt version
- generated timestamp
- self-reported rationale
- uncertainty
- human evaluation
- revision history

# 8. Important Song Translation Distinction

Do not assume that a poetic translation is automatically singable.

A song-oriented translation may eventually require:

- melody
- meter
- syllable count
- stressed syllable positions
- note duration
- melisma
- rhyme scheme
- breath points
- congregational readability

In the initial prototype, there may be no melody.

Therefore label the third output accurately as:

"song-oriented draft without melody constraints"

Do not claim full singability unless a melody and musical constraints are provided.

Design the schema so melody-specific constraints can be added later.

# 9. Human Poetic Annotation Dataset

Create an annotation format for human analysts.

The annotation system must permit:

- multiple annotators;
- disagreements;
- confidence levels;
- adjudication;
- comments;
- evidence from Hebrew;
- evidence from ETCBC;
- evidence from MorphHB;
- evidence from PDF research;
- revision history.

Create JSONL as the canonical exchange format.

Provide CSV export only for flattened views.

Create an annotation guide explaining:

- what each field means;
- when to use it;
- common mistakes;
- when to mark something unknown;
- when competing analyses are acceptable.

Include initial controlled vocabularies, but allow extensions.

# 10. Translation Generation

Implement a provider-neutral TranslationGenerator interface.

It should accept:

- CanonicalPsalmRepresentation
- target language
- output mode
- translation constraints
- optional translator instructions

It should return structured output validated by Pydantic.

For Afrikaans generation, the LLM must be instructed to:

- translate primarily from the Hebrew evidence;
- use the Canonical Psalm Representation as an analytical aid;
- preserve theological and semantic constraints;
- preserve important Hebrew imagery;
- preserve meaningful poetic relationships;
- avoid introducing unsupported theological interpretations;
- identify unavoidable losses;
- produce multiple candidates when constraints conflict;
- distinguish translation from explanation;
- use natural Afrikaans;
- avoid treating an existing English translation as the source text;
- not silently harmonize the Psalm with other biblical passages.

Produce three candidates where appropriate:

1. meaning-prioritized;
2. poetry-prioritized;
3. song-oriented without melody constraints.

The prompt should request concise translation notes with traceable references to representation fields.

Do not expose hidden chain-of-thought. Request short, evidence-based decision notes only.

# 11. Comparative Experiment

Implement an experiment comparing:

## Baseline A

Direct Biblical Hebrew to Afrikaans LLM translation.

## Baseline B

Biblical Hebrew plus MorphHB to Afrikaans.

## Candidate C

Biblical Hebrew plus MorphHB, ETCBC, and Canonical Psalm Representation to Afrikaans.

## Candidate D

The complete representation plus reviewed PDF-derived poetic principles.

Use the same model and comparable generation settings in all conditions.

Store:

- exact input
- representation version
- prompt version
- model
- parameters
- output
- latency
- estimated token usage
- evaluation results

The experiment must help answer whether the representation improves output rather than assuming that it does.

# 12. Evaluation Framework

Do not rely primarily on BLEU.

Create a human evaluation rubric with 1-to-5 scores for:

- source meaning fidelity
- theological fidelity
- lexical accuracy
- handling of ambiguity
- preservation of imagery
- preservation of parallelism
- preservation of discourse progression
- natural Afrikaans
- poetic quality
- suitability for song adaptation
- transparency of translation decisions
- amount of human revision required

Also record:

- critical meaning errors
- unsupported additions
- omissions
- flattened metaphors
- interpretation presented as translation
- awkward Afrikaans
- poetic gains
- poetic losses
- preferred candidate
- translator revision
- reviewer comments

Create a weighted score, but retain every individual category.

Support evaluations by different roles:

- Biblical Hebrew specialist
- Bible translator
- Afrikaans language expert
- poet or lyricist
- musician
- translation consultant

Do not use existing copyrighted translations as ground truth unless permission and licensing allow it.

References may be used for comparison only when their terms permit that use.

# 13. Initial Scope

Use one Psalm for the end-to-end technical demonstration, preferably Psalm 23.

However, do not hard-code the application around Psalm 23.

After the first successful run, make it possible to test a deliberately varied evaluation set, for example:

- Psalm 1
- Psalm 13
- Psalm 23
- Psalm 96
- Psalm 119:1-8
- Psalm 137
- Psalm 150

This varied set is intended to expose:

- wisdom structure
- lament
- trust imagery
- praise
- acrostic poetry
- emotional difficulty
- repeated imperatives

Do not claim general success based on only Psalm 23.

# 14. Suggested Repository Structure

Create or refine a structure similar to:

psalm-poetry-engine/
    README.md
    pyproject.toml
    .env.example
    THIRD_PARTY_DATA.md
    data_sources.yaml

    docs/
        product-brief.md
        architecture.md
        canonical-representation.md
        annotation-guide.md
        evaluation-guide.md
        research-questions.md
        decisions/
            ADR-001-canonical-representation.md
            ADR-002-no-rag-for-mvp.md
            ADR-003-provenance-model.md

    data/
        README.md
        raw/
            morphhb/
            etcbc/
            pdfs/
        interim/
        processed/
        annotations/
        experiments/
        samples/

    notebooks/
        01_inspect_morphhb.ipynb
        02_inspect_etcbc.ipynb
        03_align_sources.ipynb
        04_pdf_poetry_extraction.ipynb
        05_build_canonical_representation.ipynb
        06_generate_afrikaans.ipynb
        07_compare_experiments.ipynb

    src/
        psalm_engine/
            __init__.py
            config.py

            domain/
                models.py
                enums.py
                provenance.py

            sources/
                morphhb.py
                etcbc.py
                pdfs.py

            alignment/
                normalize.py
                token_alignment.py
                reports.py

            poetry/
                principles.py
                analyzer.py
                annotations.py

            representation/
                schema.py
                builder.py
                validators.py
                serialization.py

            generation/
                base.py
                prompts.py
                translation.py
                providers/

            evaluation/
                rubric.py
                compare.py
                reports.py

            cli.py

    tests/
        fixtures/
        unit/
        integration/
        golden/

# 15. CLI Requirements

Implement CLI commands resembling:

psalm-engine inspect-sources
psalm-engine import-morphhb
psalm-engine import-etcbc
psalm-engine align --psalm 23
psalm-engine ingest-pdf path/to/file.pdf
psalm-engine build-representation --psalm 23
psalm-engine validate-representation path/to/psalm_023.json
psalm-engine translate --psalm 23 --language af --mode poetic
psalm-engine experiment --psalm 23
psalm-engine evaluate --experiment-id ID

Exact command syntax may change if you document the reasons.

# 16. API Requirements

The API is secondary to the research pipeline.

If implemented, expose only a thin FastAPI layer over the domain services.

Suggested endpoints:

- GET /health
- GET /psalms/{psalm}/representation
- POST /psalms/{psalm}/representation/build
- POST /translations/generate
- POST /evaluations
- GET /experiments/{experiment_id}

Do not put business logic in route handlers.

Generate OpenAPI documentation through FastAPI.

# 17. Reproducibility and Provenance

Every representation and translation must be reproducible as far as the LLM provider permits.

Record:

- Git commit
- schema version
- source dataset versions
- input hashes
- PDF hashes
- annotation versions
- prompt version
- model identifier
- model settings
- timestamp
- transformation steps

Never overwrite previous representations or translations silently.

Use immutable experiment records or explicit versioning.

# 18. Safety and Scholarly Integrity

The tool must:

- show uncertainty;
- preserve competing interpretations;
- avoid presenting generated analysis as established scholarship;
- provide source provenance;
- flag unsupported additions;
- keep human approval central;
- make clear that outputs are draft translations;
- avoid silently altering source data;
- keep source text, imported data, inferred analysis, and human judgments separate.

The user interface and README must not claim the tool produces authoritative Bible translations.

# 19. What I Want You to Do First

Do not attempt the whole implementation in one uncontrolled pass.

First inspect the current repository.

Then produce:

1. a concise repository assessment;
2. a minimal product brief;
3. an architecture proposal;
4. the first version of the CanonicalPsalmRepresentation schema;
5. a source and license inventory template;
6. a phased implementation plan;
7. explicit assumptions and open questions;
8. acceptance criteria for the first vertical slice.

After that, implement the first vertical slice:

Psalm 23
    -> load MorphHB data
    -> load ETCBC data
    -> align the source tokens
    -> add a small manually reviewed poetic annotation
    -> build and validate CanonicalPsalmRepresentation JSON
    -> generate direct and representation-assisted Afrikaans drafts
    -> save a comparison report

If actual source data is unavailable:

- create adapters and fixture-sized synthetic structural examples;
- clearly label all synthetic content;
- do not fabricate linguistic facts;
- provide exact instructions for adding the real datasets;
- ensure the tests can later run against licensed local data.

# 20. Acceptance Criteria for the First Vertical Slice

The first milestone is complete when:

- the project installs successfully;
- unit tests pass;
- Psalm 23 source data can be loaded from configured local sources;
- MorphHB and ETCBC tokens are aligned with uncertainty recorded;
- a valid CanonicalPsalmRepresentation JSON file is produced;
- every important analytical claim has provenance;
- a reviewed poetic annotation can be included;
- the LLM generator can be replaced without changing domain logic;
- direct and representation-assisted Afrikaans drafts can be generated;
- experiment inputs and outputs are saved;
- the translation evaluation rubric can be completed;
- the README explains how to reproduce the experiment;
- data licenses and restrictions are documented;
- nothing is represented as an authoritative translation.

# 21. Engineering Behaviour

Work incrementally.

Before editing:

- inspect the repository;
- inspect existing conventions;
- identify reusable code;
- state the implementation plan.

During implementation:

- make small cohesive changes;
- validate Pydantic models;
- add tests with each feature;
- avoid unnecessary dependencies;
- do not hide exceptions;
- log warnings for uncertain alignments;
- keep sample data clearly separated from licensed source data.

After implementation:

- run formatting;
- run linting;
- run type checking;
- run tests;
- run the Psalm 23 vertical slice;
- inspect generated JSON;
- report failures honestly;
- summarize created files and architectural decisions.

Do not write placeholder code and call the milestone complete.

Start now by inspecting the repository and producing the assessment, architecture proposal, schema design, phased plan, and acceptance criteria before implementing the first vertical slice.
