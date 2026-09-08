# Technical verification, 2026-09-08

This is a pipeline verification record, not a translation-quality result.

## Real source slice

The CLI built `data/samples/psalm-023.json` and its alignment report from the pinned
MorphHB and BHSA files, plus the supplied Psalm 23 PDF's source metadata and two
pending annotation proposals. It contains 57 MorphHB tokens, 69 BHSA tokens and
84 imported structural units. Every token appears exactly once in alignment; zero
groups are unmatched. BHSA node 313945 has an explicitly empty written form.
Consonantal matches remain pending human review. PDF extraction produced 24 local
pages, retaining page numbers and PDF metadata; no full extracted text is tracked.

Build command (from the engine directory):

```bash
uv run psalm-engine build-representation --psalm 23 --morphhb data/raw/morphhb/Ps.xml --morphhb-revision 3d15126fb1ef74867fc1434be1942e837932691f --bhsa data/raw/bhsa-2021 --annotations data/annotations/psalm-023.proposed.jsonl --principles data/annotations/principles.proposed.jsonl --pdf-evidence data/interim/psalms-23-pages.json --output data/samples/psalm-023.json
```

The existing output is immutable; choose a new output path when reproducing.
The PDF artifact was produced with `psalm-engine ingest-pdf resources/psalms-23.pdf
--output data/interim/psalms-23-pages.json`.

## Commands and outcomes

Executed using the installed engine `.venv/bin` executables:

| Command from engine directory | Result |
| --- | --- |
| `python -m pytest tests -q` | 15 passed, including real-source coverage and subprocess generator integration |
| `ruff check src tests` | Passed |
| `ruff format --check src tests` | 12 files already formatted |
| `mypy src --ignore-missing-imports` | Passed, 10 source files; third-party library internals not checked |
| `psalm-engine validate-representation data/samples/psalm-023.json` | Validated Psalm 23, 126 source tokens |

From repository root, the data/API regression suite passed 8 tests using:

```bash
uv run --with supabase --with python-dotenv --with pytest --with fastapi --with pydantic-settings --with 'python-jose[cryptography]' python -m pytest apps/scribeswell/tests -q --disable-warnings
```

There were 13 third-party deprecation warnings. Changed importer/API files passed
Ruff checks. `git diff --check -- apps/scribeswell` passed. The real database reader
matched source counts for Psalm 23 (6 verses, 57 words), Psalm 119 (176 verses,
1,067 words), and Psalm 150 (6 verses, 37 words); Psalm 23 word morphology was present.
See the separate full-database repair and audit logs under `apps/scribeswell/docs/verification/` from repository root.

## Research status

The tests generate clearly marked synthetic strings to verify orchestration, failure
records, immutable artifacts, baseline separation, evidence-reference validation and
rubric persistence. They do not evaluate translation quality. No real LLM provider
or model has been selected/configured, no human annotation approval has been recorded,
and no real translation comparison or quality evaluation is claimed. Condition D
correctly refuses the pending sample principle. Completing the research milestone
requires those actual inputs and reviews.
