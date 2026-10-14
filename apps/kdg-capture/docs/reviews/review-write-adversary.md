# WRITE and secret execution adversary gate — 2026-10-14

Verdict: atomic successful outcomes, authorization-before-replay, short transactions and fail-closed HMAC recovery are coherent. Three bounded physical/execution clarifications remain before declaring the selected substrate convergent. No critical authorization bypass established; no code, SQL, secret or live environment changed.

Reviewed `owned-write-and-secret-execution.md`, KDG command/recovery contracts, Identity/Access execution substrate, common API recovery, controlled provisioning and KDG fingerprint disposition.

## M1 — Declare local attribution and revision/outcome linkage constraints

Identity-owned outcome/event executor and initiator fields are UUIDs without an explicit local actor FK in the new physical contract. Identity owns the actor registry, so these are local references, unlike Access/KDG's deliberately external actor references. KDG revision records carry “operation identity,” but no exact local outcome link or executor/command/org binding is specified. The explicit event→outcome FK is strong; equivalent structural linkage remains unspecified for these references.

Independent implementation A adds local Identity actor FKs and a KDG revision→outcome key binding. B allows arbitrary actor UUIDs in Identity outcomes/events and revision operation IDs unrelated to a committed outcome, relying solely on helpers. Both satisfy the listed column shapes. Alternate write paths or accidental grants can leave permanent evidence referring to nonexistent actors or an unrelated operation even though immutable rows cannot later be repaired normally.

Disposition: explicitly require Identity local executor/verified-initiator FKs to identity.actor with noncascading retention. Preserve Access/KDG actor IDs as verified external references. Define KDG non-noop revision's local outcome association, including matching org/executor/command/operation key, through an outcome UUID/FK or exact composite binding. No-op outcomes deliberately need no new revision. Keep same-transaction insertion order and bootstrap self-reference constraints implementable. Add alternate-write nonexistent-actor and wrong-outcome/org/executor fixtures; avoid cross-owner FKs.

## M2 — Secret mount directory ownership is ambiguous

Files are explicitly mode0400 owned by runtime UID10001, and the directory is mode0700. The next sentence calls the host secret source root-owned. A bind mount preserves directory ownership/mode; a root-owned mode0700 directory cannot be traversed by UID10001 even when its files are readable by that UID.

Independent deployment A makes the mounted directory UID10001-owned with a read-only bind mount. B treats “root-owned host secret source” as requiring root-owned directory0700, causing every activation/write to report missing/unreadable keys. A third weakens directory permissions to make it work, departing from the exact selected shape.

Disposition: distinguish protected root-owned staging/archive source from the projected runtime mount. Declare the mounted directory's exact UID/GID/traversal permissions, using UID10001-owned0700 in a read-only mount or an explicitly qualified projection mechanism that preserves the selected access rules. Retain root-controlled provisioning and no runtime host-source writes. Fixture the actual nonroot container user reading active/old keys and refusal of writable/untrusted mounts; do not use successful root reads as proof.

## M3 — Lock-release recheck must not reset the total attempt deadline

Step1 correctly says one ten-second monotonic budget includes waits/rechecks. Step3 says “restart the bounded execution if needed” after releasing locks for an external recheck. This can be read as a transaction restart under the original deadline, or a fresh ten-second internal execution budget.

Independent helper A retains the original deadline and fails when insufficient budget remains. B resets it after every recheck, extending a single server request indefinitely through repeated lock contention. The former complies with step1; the latter can cite step3. This also breaks browser12-second wait assumptions and the previously selected bound.

Disposition: change this to rollback/restart the **local transaction within the original executing-attempt deadline**. If that budget expires, return the truthful bounded error/uncertainty path; only a new client-requested attempt gets a fresh ten-second budget and fresh authority. Add a forced recheck/lock-contention fixture demonstrating that the total budget cannot reset.

## Low mechanical correction

The protected secret-backup manifest declares `verified_restore_ref`, while its following bounds paragraph names `restore_ref`. Use the declared field consistently; do not accidentally accept an undeclared extra key in the closed manifest.

## Attacks already closed

- Fresh Access/operator authority precedes the outcome lock; replay rechecks stored resource/command authority before fingerprint comparison. Neither query command_type nor a matching old digest grants current access. Receipt-only lookup remains distinct from mutation replay.
- Outcome key includes org/caller/command/operation identity; operator platform null scope uses NULLS NOT DISTINCT. Advisory-hash collision serializes unrelated operations but cannot substitute for actual unique identity.
- Atomic state/evidence/outcome commit and rollback eliminate orphan successful placeholders. Current revision and structural constraints arbitrate different operations; receipts preserve original revisions, and no-op changes create no fake domain transition.
- RLS contexts and immutable-table guards prevent alternative runtime update/delete paths; verified all mode does not come from an HTTP role/owner field. Narrow constraint mapping and stripped validation dumps protect sensitive content.
- Missing/unsupported verification keys do not erase outcomes, become unresolved, authorize fresh execution or fall back to SHA. Retained/overlap/rollback/restore keys are required by the original key-specific fingerprint.
- Key files bind owner/environment/key identity, never reach frontend/database/image/logs, and separately encrypted backup does not share database decryption credentials. Concrete archive/backend identities remain correctly qualified release inputs.
- Client recovery keeps original payload/operation identity and bounded lookups/retry; denied or conflicted actions do not enter unknown-outcome retry. Later edits remain ordered behind unresolved predecessors.

All actual privilege, alternate-write, interruption, restore and old/new deployment proof remains delivery acceptance. This report does not authorize implementation or claim readiness PASS.

## Resolution recheck — 2026-10-14

Verdict: PASS for the addressed WRITE planning findings; no residual blocking finding or resulting inconsistency identified in this bounded recheck. This is a document-review result, not implementation verification or overall readiness PASS.

- M1 closed: Identity outcome/event actor references now require local RESTRICT FKs with actor-first bootstrap ordering. KDG revision binds outcome/org/command/operation/executor through an explicit composite local FK and referenced UNIQUE key; scoped capture linkage also preserves original ownership. No-op semantics and external Access/KDG actor ownership remain intact. Alternate-write actor/linkage rejection is required delivery evidence.
- M2 closed: root-controlled staging/archive is distinguished from the UID/GID10001-owned0700 runtime leaf and0400 files; the leaf projects read-only and permits traversal by the actual runtime user. Root-owned0700 mounted leaves are explicitly invalid. The selected layout is physically coherent without weaker permissions.
- M3 closed: the ten-second monotonic budget includes waits/rechecks, and rollback/recheck/restart explicitly stays within the original budget. No internal deadline reset is permitted. Timeout/lock behavior still requires executable delivery proof.
- Manifest correction closed: the declared field and bounds both use verified_restore_ref.
- Earlier fixes remain coherent: bounded canonical target_key supplies the event uniqueness key, and fresh external authority precedes locks/replay; a stored-target mismatch releases the transaction before its exact authority check. No network wait is introduced under business locks.

No code, SQL, secret, migration or environment was changed by this recheck.
