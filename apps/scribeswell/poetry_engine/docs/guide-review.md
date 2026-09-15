# Review Psalm guide appendices B and C

The user's corrected scope applies to **every supplied guide**:

- Use **Appendix B: Exegetical Layout**.
- Use **Appendix C: Flower Garden**, where present.
- Ignore introductory material, all ten steps across the three phases, all of
  Appendix A (both translations), and every other appendix or section.

Cross-references inside B/C do not authorise retrieving excluded sections. Keep
independent analysis, qualifications and competing interpretations within B/C.
Text, colour, diagrams and Hebrew layout still need human review before claims
can be promoted into prompts. Section eligibility is not scholarly approval.

## Current approval workflow

For Psalms 1, 23, 133 and 42–43, use the new [image-assisted review items](image-assisted-review.md).
They replace fragment-by-fragment approval with 85 coherent proposals, editable
categories and saved/restored work. The packets below remain raw coverage archives;
they should not be mistaken for the improved review queue. Other guides still need
comparable visual curation.

## Raw coverage archive

Open [the Appendix B/C index](../data/interim/guide-review-bc-v1/index.html),
or [Psalm 23](../data/interim/guide-review-bc-v1/psalms-23.html). Psalm 23 retains
only PDF pages **20–23 (B)** and **24 (C)**. Excluded pages have coverage entries,
but no source text or review cards. A guide without Appendix C uses only B; the
inventory explicitly records the absent section.

The earlier v1–v3 packets are historical and obsolete. The initial v4 attempt is
also incomplete; use the index above. Export rejects old packets. The historical
page-17 imagery/parallelism approval is outside the corrected scope, cannot enter
new prompts, and cannot satisfy condition D. Its original approval is preserved;
this is a scope change, not a scholarly rejection or permission to move its citation.
Previously generated translations remain historical artifacts and were not rerun.

Each retained passage records the PDF checksum, Psalm scope, page, appendix, stable
ID and text checksum. Search or read in page order, then open the PDF page to check
layout and context. Review a question as a question, not an answer the guide never
gave. Preserve disagreements rather than merging them into a certain assertion.

## Record decisions

1. Enter a reviewer identifier.
2. Choose approved, rejected, disputed, or reference context only.
3. Choose Psalm analysis or translation/evaluation guidance and a category.
4. Write the concise claim in your own words, retaining uncertainty and alternatives.
5. Add notes explaining qualifications, corrections or disagreement.
6. Download the decisions before closing; the form does not save automatically.

Partial review is allowed; untouched passages stay pending. Export into a new directory:

```bash
uv run psalm-engine export-guide-review --packet data/interim/guide-review-bc-v1/psalms-23.json --decisions /path/to/guide-review-decisions.json --psalm 23 --output data/interim/psalm-23-bc-reviewed-v1
```

The outputs are `annotations.jsonl`, `principles.jsonl`, `pdf-evidence.json` and a
review audit. Export verifies the current packet policy, PDF/passages' checksums,
allowed section/page, reviewer and Psalm applicability. Only concise claims enter
annotation files; full source passages stay in the ignored review directory.
Rejected/disputed records retain their status and cannot become prompt evidence.

Build a new representation using these files and preserve existing Hebrew
annotations. Do **not** combine the old page-17 principle into the new review set.
A–C exclude PDF material. D includes only approved PDF principles and approved
Psalm-specific claims; every guide citation must be on an allowed B/C page.
A claim mixing allowed and excluded guide citations is excluded as a whole.
D still requires at least one eligible approved PDF principle.

## Recreate and verify

```bash
uv run psalm-engine extract-guides --resources resources --output data/interim/guide-review-bc-next
```

`ingest-pdf` applies the same scope to supplied Psalm guides. The extractor identifies
actual appendix headings, verifies B/C titles and continuation pages, and stops at
later appendices. It excludes running navigation and footer text. Empty retained
pages, unknown layouts or boundaries fail extraction; the old navigation-only
Psalm 33 exception is unnecessary because that page is outside B/C.

`src/psalm_engine/guide_scope.json` stores only source checksums and section page
numbers. Real-PDF tests verify these boundaries for all supplied guides. This also
lets prompt preparation reject older out-of-scope claims without needing full PDF
text in an experiment. New or changed guide files need verified scope inventory
entries before use. Saved requests containing excluded claims fail before a
provider call; create a new run rather than modifying historical requests.

Full passages, HTML and derived caches remain under ignored `data/interim/`.
No provider call or human approval is made by extraction.

## Verification — 2026-09-12

The current packets cover all **25 guides**, retaining **2,256 passages on 116
Appendix B/C pages** and recording **482 excluded pages** without source text.
Fourteen guides have no Appendix C. PDF checksums, section/page membership,
coverage entries and all review/index files were checked against the inventory.

Actual later headings exclude Psalm 11 page 22 onward (D), Psalm 124 page 26 (E),
Psalm 29 page 26 onward (D/F), and Psalm 95 page 30 onward (D/E/F/G). Those pages
were incorrectly carried forward as B/C by the previous extractor and are absent
from this review set.

Acceptance tests first demonstrated that the old extractor retained Psalm 23
pages 1–19 and that the old page-17 approval could enter D. Both now pass with the
corrected restrictions. `.venv/bin/pytest -q` passed **70 tests**, including all
25 real PDFs. After extending the guard to direct provider calls,
`.venv/bin/pytest -q tests/test_experiment.py tests/test_cline_runner.py` passed
**36 tests**. Ruff lint/format checks, `mypy src --ignore-missing-imports`, and
`git diff --check` passed. Synthetic test approvals are not research decisions.
No new human approval or translation-provider run was created.
