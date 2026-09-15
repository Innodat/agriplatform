# Historical Psalm 23 principle — excluded from current guide scope

The user subsequently restricted guide evidence to Appendix B (Exegetical Layout)
and Appendix C (Flower Garden). This principle cites the page-17 checklist in the
ten-step material, so it is **out of scope** and cannot enter new prompts or satisfy
condition D. Its approval record is preserved as history, not silently relabelled
as scholarly rejection or moved to a different source page. Follow the
[current review workflow](guide-review.md) for eligible material.

The project user originally approved this principle on 2026-09-12. The decision is preserved
in [revision 2](../data/annotations/principles.reviewed-v2.jsonl), with the original
machine proposal unchanged. New guide material is not covered by this approval.
Continue with [the all-guide review workflow](guide-review.md).

Source: [psalms-23.pdf](../resources/psalms-23.pdf), PDF page 17, “Poetic checklist”.
The extracted page is locally available in `data/interim/psalms-23-pages.json`.
Source SHA-256: `6e3e56b3a7f3c0dc9c3b4b202089430d1c0cd4829ee120a316052105329acde4`.

Proposed record: `ps23-review-imagery-parallelism-v1` in
[data/annotations/principles.proposed.jsonl](../data/annotations/principles.proposed.jsonl).
The original record remains a pending machine proposal; revision 2 records approval.

## Proposed principle

Evaluate whether a draft preserves parallel line relationships and metaphorical
imagery, and record losses separately from the translation.

## What the page supports

The checklist asks: “Did you keep the synonymous words and lines in the parallelisms?”
It also asks readers to evaluate how metaphors and other figures of speech have
been rendered. Those two checks support comparing source and target relationships
and identifying imagery replaced by abstract explanation.

Recording losses separately is this experiment's reporting convention; the page
is not explicit about that format. The safeguard against forcing uncertain
parallelism classifications is also an experiment constraint, not a quotation
from this checklist. The record's 0.8 confidence is a machine estimate, not a human
assessment of the source or translation.

The same checklist mentions lament genre, rhythm, syllables and enjambment.
Those statements do not establish a genre analysis for Psalm 23, a specific
metrical scheme, or singability. They are outside this proposed principle.

## Historical review procedure

The previous workflow allowed a reviewed revision of this proposal to satisfy
condition D. That procedure has been superseded: approval of this page cannot
make it eligible under the Appendix B/C restriction. Use new, separately reviewed
in-scope claims for future PDF-assisted experiments.

For translation evaluation, use the generated `evaluation-template.json` and
[the evaluation guide](evaluation-guide.md). Compare meaning and omissions first,
then imagery, line relationships, natural Afrikaans and poetic quality. Record
scores yourself; no generated notes count as human evaluation.
