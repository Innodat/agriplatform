---
title: 'Bound complete corpus manifest candidates'
type: 'feature'
created: '2026-10-26'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

As the next highlight prerequisite, assemble an immutable, complete corpus manifest candidate from qualified source bytes and a full observed word-ID inventory. Bind it to the exact source identity/checksum, revision, executor actor, attempt UUID and positive generation; reject wrong expected attempt/generation and incomplete, extra or duplicated observations. Reuse existing source qualification and digest encoding. This is preparation for the protected publication transition, never proof that an audit ran under a fence or permission to activate a publication. No SQL, owner service, runtime route, credentials or operational tooling is added.

</frozen-after-approval>

## Implementation Notes

- Small pure model in backend/corpus_manifest.py with focused tests and an app contract addendum; no irreversible action or product intent gaps. Existing corpus_evidence.build_source_candidate owns full 39-book input validation and complete ordered digest inventory. Existing corpus_database_audit._compare will eventually supply observed inventory inside the protected transition. Current historical audit remains publication:false and is not accepted as authority.
- Frozen dataclasses/tuples prevent in-process mutation of assembled candidates; all IDs canonical and positive. Caller expected attempt/generation is checked explicitly. Boundaries are explicit: this cannot independently check current DB state, publisher authority, full reference-catalogue alignment, or fence custody. Source revision and executor actor are nonzero canonical UUIDs. No runtime can claim publication readiness from this object alone.
- Scaffold/shared UI/agent context/ADR impact: app-specific model, no promotion or ADR change; update existing highlight evidence contract. Final SQL/owner/device/release and prior unexplained scroll qualification remain deferred.

- Genuine stub red: 1 failure/13 pass; first implementation 55 combined pass. Boolean coordinate alias test then failed; strict coordinate types corrected it, 56 combined pass8.29s. Initial wider pure regression105pass68.57s predates review corrections.
- Review four findings triaged: direct mutable constructor inventory confirmed by retained-list red (IndexError after caller list clear); constructor tuple snapshots fix it. Three coverage roots patched with multi-token nonnumeric ID order, multi-chapter/verse coordinate mapping and wrong-coordinate rejection, and source label/checksum/per-verse digest/change assertions. Final pure regression running; no native/browser qualification claimed.

## Review Triage Log

- Low / patch: direct constructor mutable lists broke the advertised immutable model; reproduced and tuple snapshots added to both frozen records.
- Low / patch: single-token fixtures could miss ID reordering; exact deliberately unsorted multi-token order asserted.
- Low / patch: single chapter/verse fixture could miss lost coordinates; multi-chapter/verse mapping and moved-coordinate rejection asserted.
- Low / patch: successful assembly did not assert all source bindings; compare full source labels/checksum/digests with existing qualifier and show exact surface change affects only its verse digest.

Only configured fresh context-free same-capability blind review ran. All findings addressed; no other review layer configured.

- Final corrected verification: `python3 -m pytest -q apps/scribeswell/tests/test_corpus_manifest.py apps/scribeswell/tests/test_highlight_evidence.py apps/scribeswell/tests/test_corpus_evidence.py` passed107 in62.64s exit0. No browser build required for these Python-only changes. Reader dependency gap and preexisting broad browser-scroll failure remain open; neither is erased by pure test passes.
