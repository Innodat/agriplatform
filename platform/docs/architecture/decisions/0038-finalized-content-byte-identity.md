# ADR-0038: Finalized Content Byte Identity

**Status:** Accepted

**Date:** 2026-09-23

**Scope:** Shared Content Service and application attachment contracts

## Decision

Once finalized, a content ID identifies the exact verified file contents. Persisted
verification evidence and any enabled safety result apply to that fixed byte/version
identity. Reads and domain associations must resolve those same contents; they must
not silently follow a mutable storage key to replacement bytes.

An outstanding or replayed upload capability, including an in-flight upload completing
after finalization, must not replace the finalized contents behind that identity.
Verification and finalization must also prevent a race between checking bytes and
binding the finalized identity. A checksum recorded against a still-mutable object
is not by itself enforcement of this invariant.

Replacing a document requires a new content identity, fresh verification and an
authorized, audited application attachment change. Preserve existing decision evidence
and apply the application's established correction/approval rules. Normal duplicate-safe
finalization/association retries reuse the same identity and do not create replacements.
This does not introduce a document-versioning UI or exempt content from authorized
retention/disposal rules; deleted content must never resolve to different replacement bytes.

Provider-specific enforcement remains a Content Service implementation decision. Before
the first affected attachment story is ready, define and test the binding protocol,
including concurrent upload/finalization and still-valid upload capability replay.
The signed-operation lifetime target in ADR-0036 remains separate and unchanged.

## Impact and verification

- Acceptance: attempt overwrite with an outstanding upload capability after finalization;
  race verification/finalization against upload completion; verify reads/associations
  retain the verified identity; replacement receives new identity, verification and
  authorized audited linkage; ordinary retries remain idempotent.
- Scaffold: shared content client/types and adapter contract tests must preserve stable
  finalized content identity; promote proven implementations through existing tooling.
- Shared UI: existing upload/replacement controls suffice; no additional employee steps
  or document-versioning interface required.
- Agent context: existing service ownership, privacy and test requirements suffice.
- Documentation: Leave architecture, requirements and delivery gates link this invariant.
- ADR: complements 0004, 0005, 0030 and 0036; accepted originals unchanged.
- Planning only; this closes a contract gap, not a demonstrated runtime vulnerability.
