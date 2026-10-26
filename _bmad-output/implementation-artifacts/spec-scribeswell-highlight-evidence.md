---
title: 'Exact highlight evidence comparison'
type: 'feature'
created: '2026-10-26'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Provide the small, pure comparison primitive required before implementing note-owned highlights. Given one canonical verse, exact current token surfaces/positions/IDs, and a caller-owned current publication observation, produce ready evidence only when the complete verse matches its recorded digest and observed IDs. Compare a saved anchor segment against that evidence: unchanged token identity across a new revision or regenerated database IDs remains valid; changed text requires review; missing or inconsistent current proof is unavailable. Never treat a reused word ID as text identity.

This primitive cannot establish that a publication is active, perform authorization, access a database, seal an audit, or accept a private note write. The future snapshot/publication adapter must supply trusted observations. No runtime route or schema activation is included. Existing standalone account creation and Access ownership remain unchanged.

</frozen-after-approval>

## Implementation Notes

- Investigation found source digest encoding reusable in backend/corpus_evidence.py; reader currently has separate observations and no live publication proof. This slice introduces only backend/highlight_evidence.py, focused Python tests and a contract document. No intent gap, irreversible action or owner-service change.
- Technical decisions: strict bounded canonical single-verse coordinates; decimal bigint observed IDs; safe fixed errors for malformed saved segments; fail-closed unavailable for malformed publication/reader inputs. Comparison checks source/catalogue/versification/tokenization and complete verse digest, independently of source revision and database IDs. Inclusive selection positions must exist.
- Scaffold/shared UI/agent context/ADR: no reusable promotion or decision change; app-specific pure code only. Documentation records proposed adapter boundary versus implemented comparison behavior. Final native/publication/browser/device/release checks remain open, including the previously unexplained anonymous mobile scroll failure.

- ATDD chronology: initial collection failed for absent module; explicit unavailable stub then produced 16 acceptance failures and 10 passes. Implementation passed 26; review coverage additions passed 41 in 13.68s. `python3 -m pytest -q apps/scribeswell/tests/test_highlight_evidence.py apps/scribeswell/tests/test_corpus_evidence.py` passed 75 in 107.70s on the original 26-case highlight tests (the running process had already collected before additions). The attempted additional test_reader_integrity.py run failed during collection because psycopg is missing; no reader test result claimed. No browser/native test run.

## Review Triage Log

- Low / patch: malformed current evidence branch lacked direct coverage; six direct rejection cases added and passed.
- Low / patch: inclusive selected subrange/end-of-verse/out-of-range behavior lacked coverage; three cases added and passed.
- Low / patch: exact Unicode/invisible/invalid/oversized surface behavior lacked local coverage; five cases added and passed.
- Low / patch: output containment and list isolation promises lacked proof; exact fields and mutation-isolation assertions added and passed.

Only configured oneshot blind layer ran, fresh context-free same-capability reviewer; all four findings addressed. Publication authority, full catalogue eligibility and live adapter integration remain explicitly outside this comparison primitive.
