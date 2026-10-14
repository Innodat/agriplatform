# Operation fingerprint security enhancement candidate

**Status:** Logged future security enhancement; not an implementation commitment
**Date:** 2026-10-01
**Owners:** Platform security/API lead and consuming application lead

## Current scope

Leave E1 uses a versioned SHA-256 fingerprint of the canonical command to detect
changed-content reuse of an operation ID. This is a consistency mechanism, not an
access control, encryption or guarantee that deleted input cannot be inferred. No
fingerprint secret, keyring or key rotation is required in the current E1 design.
Operation IDs, current authorization, revisions, local atomic outcome records and
lifecycle protection remain mandatory under the existing platform ADRs.

The user requested that stronger fingerprint protection be logged for future work
and raised concern about AI-assisted attacks. Record that concern without assuming
AI makes cryptographic hashes reversible or that a specific future breach is certain.
The relevant attack is candidate guessing: with known command context and a small set
of plausible sensitive inputs, a stolen unkeyed digest can help confirm a guess.
Automation can make that threat worth reassessing; the data and exposure determine
whether the protection is needed.

## Candidate enhancement

Offer HMAC-SHA-256 fingerprinting through the reusable platform operation mechanism,
with application/environment-scoped secret management. Select it through the adopting
application's reviewed threat model and versioned contract, not a user-facing toggle
or a universal requirement for every draft.

Benefit: an attacker with only database/backup outcome records cannot independently
check candidate payloads without the separate secret. Limitation: it does not encrypt
active drafts, prevent authorized/compromised runtime access, protect a separately
leaked payload, or provide an immutable/tamper-proof audit log merely by existing.
It loses that benefit if the attacker also obtains the key or an unrestricted oracle.

Keyed fingerprints may be appropriate at initial delivery for highly sensitive and
predictable inputs (medical/HR details, small sets of confidential financial values),
long-lived outcome retention, or a required database-only compromise boundary. They
need not wait for an incident or platform-wide rollout. Public or low-sensitivity
commands may reasonably use the simpler consistency hash.

## Revisit triggers and evidence

- A consuming app's threat assessment finds that offline confirmation of a sensitive
  value would have material impact. Leave may contain health-related notes/type data;
  do not classify all Leave drafts as low sensitivity by default.
- Outcome records survive longer or have broader access/export/backup exposure than
  the original draft, or protection after content discard becomes a requirement.
- A client requirement, concrete incident/near miss or changed attack capability
  warrants stronger separation of database evidence from verification secrets.
- Platform secret infrastructure makes the additional key lifecycle support practical.

At Leave pilot security assessment, explicitly evaluate the plain fingerprint's
candidate-guessing exposure and record the disposition. If unacceptable for the actual
payload/retention/access model, adopt stronger protection before exposing that data;
"future enhancement" is not a waiver. This uses existing security/implementation/pilot
checks and creates no separate generic approval workflow.

Before implementing HMAC, define independent secret storage, active/verification keys,
rotation/restore, lost-key/compromise handling and versioned retry compatibility. Preserve
recognition of old outcomes; never turn missing keys into fresh execution. Assess both
new records and retained unkeyed fingerprints; a later change cannot undo earlier
exposure. No automatic data rewrite or indefinite legacy key commitment is decided here.

Acceptance: identical retries survive supported upgrades/rotation/restart; changed
payloads are rejected; missing keys fail safely; no key/payload leaks in logs/artifacts;
database-only disclosure does not offer the unkeyed candidate-checking capability;
application authorization remains independent. Reuse platform tests with per-app scope.

## References and delivery impacts

[HMAC RFC 2104](https://www.rfc-editor.org/rfc/rfc2104) describes the keyed construction;
use a maintained implementation with SHA-256, not the historical RFC's MD5 examples.
[OWASP Key Management](https://cheatsheetseries.owasp.org/cheatsheets/Key_Management_Cheat_Sheet.html)
describes key lifecycle/storage/recovery responsibilities. These inform the candidate,
not a claim that a specific application requires it.

Scaffold: retain a versioned fingerprint boundary; implement only the selected current
algorithm, not a speculative pluggable crypto framework. Shared UI: no setting needed.
Agent context: existing safe logging/service ownership guidance suffices. Documentation:
this candidate and the Leave tracker. ADR: no accepted decision mandated HMAC; update
the mutable contract, leaving accepted ADRs unchanged. No implementation performed.

## KDG initial fingerprint disposition — 2026-10-14

Selected engineering baseline for review by the acknowledged sole platform/KDG owner.
KDG observation answers concern identifiable children and small predictable rating/
boolean sets. Treat database/backup-only guessing of those values as material; select
HMAC-SHA-256 from initial capture.create/capture.edit delivery, not unkeyed SHA-256.
This is an application assessment under the existing candidate, not a universal mandate
or a change to Leave's selected design. Source basis checked 2026-10-14:
[RFC 2104](https://www.rfc-editor.org/rfc/rfc2104),
[RFC 8785](https://www.rfc-editor.org/rfc/rfc8785), and
[OWASP key lifecycle guidance](https://cheatsheetseries.owasp.org/cheatsheets/Key_Management_Cheat_Sheet.html).
HMAC prevents independent database-only candidate checking when the key stays separate;
it does not encrypt records or protect a compromised runtime/key/authorized API oracle.

Fingerprint is the full 32-byte HMAC over UTF-8 JCS bytes of KDG's existing canonical
envelope, using 32 randomly generated key bytes. No truncation or custom cryptography.
Persist `fingerprint_version: 1`, `fingerprint_algorithm: hmac-sha256`, an opaque
`fingerprint_key_id` (1–64 ASCII letters/digits/_/-) and the digest with the outcome;
never return/log any of these fields or the canonical answer bytes. Compare with a
maintained constant-time primitive. Keep command version and fingerprint version
separate. There are no legacy KDG unkeyed outcomes to convert.

Keys belong only to the KDG environment's restricted API execution secret set, separate
from the database/outcome backups. Use explicit deployed secret-file references and
active key ID; no checked-in values, browser key, app migration key generation or
fallback development key. Local/CI uses synthetic disposable keys. Release preparation
must verify file permissions, independent encrypted backup access and restore wiring
before real data. Protected key metadata binds owner_id `kdg_capture`, environment identity and key_id.
ENV validates those against the explicit deployment target before activation, refusing
absent/mismatched ownership/environment; a copied key from another environment cannot
be adopted implicitly. Verify secret provenance and key-ID consistency through the
restricted secret configuration, not a client flag or payload. The concrete secret-file paths/access principals are ENV inputs,
not a claim that a managed key service is installed.

Start with one active key. On deliberate rotation, provision the new key and retain
old verification keys before activation; old release instances retain their own
active key during overlap. A replay first loads its stored version/algorithm/key ID
and recomputes with that key; new outcomes use the executing release's active key.
Never rewrite old digest/key IDs or compare an old receipt using only the new key.
Supported ordinary rollback retains all keys required by either release and live
outcomes. Concurrency and duplicate constraints still protect overlap execution.

Verification-key retention follows retained recoverable outcomes and restorable backups;
no calendar retirement date is invented before KDG's retention policy. Retire a key only
after owner evidence establishes no supported live/restore retry requires it. Missing
active key blocks writes/activation; missing referenced verification key returns HTTP
503 `operation_verification_unavailable`, preserves outcome/input and blocks re-execution.
It never becomes `unresolved`, payload mismatch, fresh execution or silent hash fallback.
Authorized compact receipt lookup may still return an existing committed receipt without
recomputing a payload; lookup is not permission to repeat the mutation.

Restore recovers matching owner data and separately backed-up verification keys and
proves a prior retained retry before activation. On loss/compromise, suspend affected
write verification, investigate secret/data exposure and restore trusted configuration;
do not erase receipts to make writes run. Key compromise invalidates the database-only
confidentiality benefit; rotation cannot undo prior exposure. Recovery uses the existing
release/incident process, with no user-facing key setting or speculative keyring service.

WRITE/KDG A09 fixtures: JCS non-BMP object-key ordering, Unicode preservation, duplicate/
invalid input refusal; identical/mismatched/concurrent retry; account/org/type binding;
restart, overlapping releases, rotation/rollback and data+key restore; missing active/
verification keys; wrong-environment key; no canonical payload/key/digest in errors/logs.
Shared WRITE accepts the selected versioned mechanism while KDG owns sensitive command
meaning. Affected schemas/generated clients and release evidence land together in the
first consumer. Physical paths, role permissions, library pin/conformance and actual
restore proof remain prerequisite delivery work. No secrets, schemas or code changed.
