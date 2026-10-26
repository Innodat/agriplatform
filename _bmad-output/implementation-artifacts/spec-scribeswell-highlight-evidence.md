---
title: 'Exact highlight evidence comparison'
type: 'feature'
created: '2026-10-26'
status: 'in-progress'
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
