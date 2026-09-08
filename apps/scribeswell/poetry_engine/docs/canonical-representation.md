# Canonical Psalm Representation v0.1.0

The authoritative implementation is `src/psalm_engine/models.py`. Generate its JSON
schema with `psalm-engine schema --output NEW_PATH.json`; do not hand-edit generated
schema artifacts.

A representation contains an immutable identity, schema/pipeline versions, timestamp,
Psalm number, source revisions/hashes, original tokens, imported verse/clause/phrase/
sentence units, explicit alignment, analytical claims, poetic principles and a
translation brief. Tokens retain original Hebrew, lexical and morphological data.
Consonantal and cantillation-stripped views are derived without changing source forms.

Interpretation is expressed through evidence-bearing Claim records, with method,
confidence, alternatives, revision links and human review status. This supports
semantic, lexical, poetic, discourse and theological analyses without falsely claiming
the first pipeline automatically discovers all of them. Stanza, strophe, colon and
line units can be supplied with token references when justified; imported syntactic
boundaries are not automatically poetic lines.

Every source token appears in exactly one alignment group. One-to-many and many-to-one
mappings are explicit. Unmatched groups survive validation and are logged. Matching
uses verse-local contiguous consonantal strings (groups up to four tokens), minimizing
unmatched tokens before group size. It does not adjudicate competing vocalizations or
all alternative repeated-string alignments. All inferred mappings start pending review.
An explicit empty BHSA source form is distinguishable from an invalid missing surface.

Translation candidates are separate immutable experiment records, linked to a hashed
representation snapshot. They store lines, concise evidence references, losses and
uncertainty. Generation records retain provider/model/settings, prompt version,
timestamps, latency and reported usage. Human evaluation and translation revisions
are additional artifacts rather than edits to old results. Future musical constraints
have a reserved field; the current supported song output has no melody constraints.
