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
