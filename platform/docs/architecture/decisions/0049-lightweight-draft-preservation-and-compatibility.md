# ADR-0049: Lightweight Draft Preservation and Compatibility

**Status:** Accepted  
**Date:** 2026-10-04  
**Scope:** Platform-wide non-consequential draft preservation

## Decision

Keep saving unfinished work independent of configuration and business validation that
is needed only for calculations, submission or other consequential actions. Validate
configuration at its owning editor/provisioning boundary. Missing or invalid business
setup should not block an otherwise authorized, structurally safe draft save merely
because the eventual action cannot yet complete. Present a small actionable notice
where useful, without forcing administrator contact just to preserve input. Never
present saved input as validated, eligible, approved or submitted.

Do not build elaborate release-compatibility machinery solely to retain obsolete draft
choices. An application may clear a definitively obsolete selection with a brief notice
and ask the user to choose again. It must explicitly identify which fields can safely
be cleared and preserve independent useful input. Do not silently choose replacements,
convert values, fill restored blanks with defaults or erase an entire draft under this
rule. Incomplete typed input is not automatically obsolete; dependency failure is not
proof that a choice is invalid. Unknown stored formats require an explicit bounded
compatibility disposition, not arbitrary deletion or unsafe decoding.

Reads remain read-only. Persist a cleared field through the normal authorized write
with current revision/lifecycle and operation handling; acknowledge Saved only after
persistence succeeds. Retain the simple draft failure exits in
[ADR-0048](./0048-simple-draft-save-failure-navigation.md). No extra technical explanation
or user decision is needed merely because internal recovery has several possible states.

Applications define what is necessary for safe preservation: current authorization,
correct owner/scope, structural limits, safe input handling, attribution, confidentiality,
revision and lifecycle protections remain binding. Missing identity/ownership or an
unavailable required authorization check does not fail open. A confirmed noneditable
lifecycle still prevents writing. If saving itself causes a consequential effect, that
effect keeps its validation and consistency requirements; calling it a draft does not
exempt it. Business configuration cannot be made a prerequisite for preservation merely
because a later action needs it.

Submission, approval, payment, reservation, signing, publication, deliberate discard and
other consequential commands retain their domain validation, confirmation, audit and
consistency requirements. Submitted/finalized records and their historical snapshots
are not subject to this draft-clearing policy. No generic auto-expiry or cleanup rule
is introduced. Safe release/migration compatibility remains required under ADR-0020;
this decision narrows draft product guarantees, not database integrity or release safety.

## Ownership and adoption

The platform owns the preservation/validation distinction and reusable status, field
notice and guarded-write primitives. Each application owns field obsolescence, its
safe reset list, domain lifecycle and consequential validation. Do not create a shared
runtime draft service or generic migration engine merely to implement this convention.
Promote proven build-time/shared UI patterns with their first consumer.

[Leave ADR-0122](../../../../apps/leave/docs/architecture/decisions/0122-lightweight-draft-compatibility-and-setup.md)
is the first application-specific adoption: missing work timezone does not block
preservation, and obsolete type/mode choices may be cleared without erasing useful
dates/notes. Its accepted text remains unchanged; this decision generalizes the approach
without copying Leave's employment or duration rules into other applications.

## Impacts and verification

- Scaffold/shared UI: separate preservation schemas from consequential validation;
  support simple setup/reset notices and revision-safe field changes. Prove before
  promotion, and update templates/fixtures/docs in the same delivery item.
- Acceptance: missing business setup with successful authorized preservation; consequent
  action still blocked; obsolete field reset with notice; useful input retained; dependency
  outage does not trigger reset; GET has no mutation; late/stale/unauthorized writes fail.
- Agent context: distinguish essential draft safety from later business prerequisites.
- Documentation: platform EXPERIENCE/builder guidance and consuming app contracts link
  this decision. Reconcile existing story criteria rather than adding competing rules.
- ADR: additive generalization; complements 0012/0013/0020/0032/0033/0044/0048 without
  weakening their safeguards. Accepted prior ADR files remain unchanged.
- Planning only; no code, stored draft clearing, migration or readiness pass implied.
