# Psalm 23 condition D continuation

The user's `data/interim/psalms-23.decisions.json` validated against the immutable
image-assisted Psalm 23 packet. All 20 decisions were explicit approvals: 19 Psalm
analyses and one poetic principle. Exported records and the decision audit are at
`data/interim/psalm-23-reviewed-20260913`. Evidence is restricted to Appendix B/C,
PDF pages 20–24. The historical page-17 principle was removed from the new input.

Condition D generated successfully through Cline 3.0.61 using
`cline / anthropic/claude-sonnet-5`, poetic Afrikaans and default settings.
The new immutable run is `runs/psalm-023-0f4d28a6-b2f7-436b-b65b-3602f773bd35`.
It includes exact request/response, timing, transport provenance, source hashes,
continuation provenance, comparison and blank evaluation form.

[Combined A–D comparison](../../runs/psalm-023-comparison-abcd-20260913/comparison.md)
and [evaluation template](../../runs/psalm-023-comparison-abcd-20260913/evaluation-template.json)
retain the three previous conditions from
`psalm-023-recovery-da8f0302-2e11-459e-a65e-d3ed5acac868` and add D. The aggregate
contains five candidates, validated against their original requests; its
`comparison-provenance.json` identifies the original runs and request/response hashes.
A completed copy of its evaluation template can be validated with
`psalm-engine evaluate runs/psalm-023-comparison-abcd-20260913 --evaluations PATH`.

The model, settings, mode, language, Hebrew, linguistic data, non-PDF claims and
translation brief match the prior comparison. D uses prompt version 0.2.0, adding
the Appendix B/C restriction; A–C used 0.1.0. This is a descriptive continuation,
not a controlled rerun with an unchanged prompt policy. Generation and schema/
provenance validation are complete; human quality evaluation remains outstanding.
No software implementation changed for this run, and no automatic quality scores
or human translation evaluations were invented.
