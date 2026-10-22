---
title: Copyable keyed command fingerprint foundation
created: '2026-10-22'
type: feature
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 1f7edfe61e314d76fa1f4a4e0a0c6ba768adffcc
context:
  - AGENTS.md
  - platform/docs/architecture/contracts/owned-write-and-secret-execution.md
---

<frozen-after-approval reason="standing approval for bounded lean WRITE prerequisites and continued implementation">

## Intent

Supply the next missing WRITE prerequisite: a small copyable JCS/HMAC command fingerprint
example in the existing builder, proven with KDG-shaped normalized commands. This lets
an owner recognize identical retained retries without storing a plain guessable hash.
It is a prerequisite candidate, not an installed generic runtime or complete WRITE.

## Boundaries & Constraints

Use pinned rfc8785==0.1.4 and standard hmac/hashlib SHA-256/compare_digest. Full32-byte
digests,32-byte keys, explicit fingerprint version1/algorithm hmac-sha256/key ID
(1–64 ASCII letters/digits/_/-). Original stored metadata selects the verification key;
new active keys cannot replace missing old material. Keep strings unchanged and arrays
ordered. Validate JSON-compatible input, Unicode/NUL/nonfinite/integer-domain boundaries
safely before canonicalization. Inputs are already domain-validated and typed-normalized
Python JSON objects; raw HTTP decoding, duplicate-key detection and domain DTOs remain
the consumer's responsibility. No secret/payload/digest in repr, errors or diagnostics.
No log/HTTP/CLI fingerprint serialization is introduced.

Reuse existing scaffold extension import/preservation. Do not promote a proven runtime
pattern, change generated templates, add a Python runtime package, import Access/Identity
server code, introduce pluggable algorithms, provision/load/mount keys, migrate databases,
start Docker, implement KDG API/editor/Leave or change dependency baselines. Preserve
concurrent work, historical receipts and resources. Synthetic offline verification only.

## I/O & Edge-Case Matrix

| Scenario | Required behavior |
| --- | --- |
| Same normalized document/key; reordered object keys | Same internal fingerprint; constant-time verification succeeds |
| Changed payload, account, organization, command or array order | Verification returns false with original metadata intact |
| Non-BMP keys, number formatting, composed/decomposed Unicode | Match independent RFC/JCS vectors; preserve text distinction |
| Rotation/restart with old key retained | Old receipt verifies by its recorded key; new creation uses explicitly selected new key |
| Missing/bad key, unsupported/malformed stored metadata | Safe operation_verification_unavailable; never mismatch/fresh execution/hash fallback |
| Unsupported JSON value, NUL/surrogate/nonfinite/out-of-domain integer | Safe bounded error without input content |
| Scaffold imported copy and rerun | Exact initial helper bytes execute; subsequent owner changes/provenance survive existing installer rerun |

</frozen-after-approval>

## Code Map

- platform/builder-cli/examples/owned-service/transaction_context.py: established copyable
  example convention; leave its behavior unchanged. Add command_fingerprint.py beside it.
- services/access/identity_operator.py and identity_operator_input.py: implementation
  examples only, never runtime imports; historical fingerprints stay unchanged.
- platform/deployment/qualification/python/tests/test_baseline.py: independent JCS vector
  precedents. Existing approved prepared owner Python environment contains required pins.
- platform/builder-cli/src/scaffold-install.ts and tests/scaffold-extensions.test.mjs:
  reuse existing installScaffold/checkScaffold for actual copied helper proof; no second installer.
- apps/kdg-capture/docs/contracts.md canonical submitted meaning: KDG owns envelope/domain
  normalization. Tests use explicit command/org/account/payload fixture without building its API.

## Tasks & Acceptance

- [x] Add examples/owned-service/command_fingerprint.py: immutable internal redacted
  fingerprint metadata, create_fingerprint(document,key_id=...,key=...) and
  verify_fingerprint(document,stored,keys=...) only for selected algorithm. Keep key
  bytes out of returned metadata. Unsupported stored versions stay untouched.
- [x] Add platform/builder-cli/tests/test_command_fingerprint.py: focused matrix tests,
  independent canonical/digest expectations and real existing-installer copied module
  execution/preservation. Observe failing acceptance before production code; focused TDD.
- [x] Update examples/owned-service/README.md and owner WRITE_FINGERPRINT_EVIDENCE.md:
  exact commands/results, requirement-to-test links and five impact decisions. Root updates
  current KDG handoff only; all other owners and old evidence stay unchanged.

Given a retained fingerprint, when verifying after key rotation or a reconstructed
process, then only its recorded supported metadata/key determine the result, with
safe refusal on unavailable verification material and no mutation. Given the scaffold
copy, when installing/replaying with owner edits, then the existing provenance and
preservation contract holds and the copied helper runs the same fingerprint checks.

## Implementation Notes

No intent questions or irreversible operations. Dirty-tree preservation is explicitly
approved. Root owns initial RED, final affected checks, evidence audit/review/commit and
KDG handoff; implementation agent owns helper, focused tests and example documentation.
No root lifecycle/review/commit inside agent. Root's existing approved interpreter:
platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python.
Approved Node: platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node.
Tests must receive this explicit Node binary for copied proof, fail rather than silently
skip when unavailable. Do not add dependency locks to an example with no runtime owner.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| Blind1: acyclic shared graphs can expand without a budget | low | Accepted repeated Python references can expand exponentially; this candidate is only called after owner validation/normalization, with no raw/server caller installed. Reject a new traversal/output budget for this uncommon programmatic input; patch README to state normalized-document bounds remain a consumer precondition and no helper resource-budget claim is made. |
| Blind2: copied installer subprocess has no timeout | medium | subprocess.run has no timeout, and an installer subprocess stall has occurred in this environment. Patch a short explicit timeout and safe failure. |
| Blind3: installer failures discard diagnostics | low | Captured output is discarded in favor of a single assertion. Patch bounded diagnostic context for this synthetic fixture so importer/process/scaffold failures can be distinguished without an unbounded dump. |
| Blind4: RFC vectors miss escaping and difficult number cases | medium | Current vectors prove ordering/basic numerics but omit escaping/rounding-sensitive values. Patch a small independent RFC8785 section3.2.2 sample; the published primary source confirms expected bytes. |
| Blind5: documented exact-type/root and sanitized exception branches untested | medium | Tests cover unsupported ordinary values but not exact-type subclasses/non-dict roots or the canonicalizer failure path. Patch focused cases and formatted-traceback canary exclusion. |
| Blind6: acceptance source/RED only referenced in tmp | low | The focused committed test reproduces the same missing-module/identical-retry check, but the independent root witness is only in tmp. Root copies exact acceptance source and original RED log into the existing retained owner proof directory, hashes them and names the committed equivalent. No new production test harness. |

Edge-case review: no findings. Verification-gap review: no findings. No deferred entry
is required: consumer resource bounds are already an explicit validation prerequisite,
and the remaining findings are direct test/documentation corrections.


## Verification

Root: missing helper acceptance RED, focused pytest file, existing builder Node tests
using prepared Node, copied-helper execution and preservation, source/diff audit.
No Access regression, database composition or Docker startup is required for an isolated
example that does not alter those owners. Record any verification limits explicitly.
Scaffold: candidate copyable example/import proof only. Shared UI: unchanged. Context:
existing rules suffice. Docs: example/evidence/current handoff. ADR: unchanged.


## Completion

Root observed missing-helper RED before source edits and final identical-retry GREEN.
Final focused63 tests and affected existing builder62 tests pass. All three review
lenses complete; six blind findings individually triaged, direct test/doc corrections
verified, no new deferrals. Root audit binds308 sources/locks and9 proof inputs/logs;
303 of304 pre-existing owner files unchanged (only intended example README differs).
No database/Docker or other owner behavior changed. Scope-only local commit retains
all concurrent work and the approved baseline; next owner-local WRITE proof remains gated.
