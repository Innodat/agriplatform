# ADR-0056: Durable Actor Registry Separate from Login Accounts

**Status:** Accepted — user agreement 2026-10-07; implementation readiness pending
**Date:** 2026-10-07
**Scope:** Identity, record attribution, controlled support/migration/service operations
**Refines:** [ADR-0025](./0025-record-attribution-and-audit-provenance.md) and
[ADR-0042](./0042-person-account-employment-and-legacy-adoption.md).
Accepted predecessor files remain unchanged.

## Decision

Use a small Identity-owned actor registry, separate from login account profiles.
Keep identity.users as the profile of an Auth account, with its existing Auth UUID
meaning. Do not broaden it into a polymorphic person/service directory. System and
Migrate remain important named attribution identities in the actor registry; new
system/service actors need neither Auth accounts nor employment/membership records.

- Each actor has a stable UUID, account-versus-system/service classification and display
  name. Account associations are explicit and constrained; exact owned DDL is a readiness
  input. Text identifiers could also be constrained correctly: UUID selection preserves
  existing reference conventions, not a claim that text identifiers are inherently unsafe.
- One account has one stable account actor. Separate accounts belonging to the same
  person retain separate actors and grants. Supported multiple sign-in methods linked
  to one Auth account use that account's actor; no new actor per provider or login session.
- Person identity remains separate from account/actor and employment. Do not create a
  person or employee merely to attribute a PtS action or system operation. Actor registry
  records grant no permissions and are not authentication credentials.
- Preserve human legacy actor UUIDs and System/Migrate UUIDs where verified, with explicit
  classification and mappings. Named service/import/job actors identify their executing
  role without creating an actor for every run. Run/command/release IDs belong in evidence.
- Derive created_by/updated_by from trusted execution context, not browser input. Normal
  user operations use their verified account actor; an independently executing worker,
  importer or migration uses its own actor and preserves any verified human initiator
  separately. A support person directly performing an authorized correction uses their
  support account actor, not anonymous System attribution.
- Retain actors and historical associations after account deactivation/removal. Never
  reassign an old actor to a recreated account or cascade-delete business attribution.
  Exact Auth deletion and account-association retention constraints must be proved;
  retaining history does not retain authentication or restore grants.

## Adoption and scope

Current legacy identity.users has a required FK to auth.users, and System/Migrate seed
rows therefore have synthetic Auth records. This is a schema dependency, not a Supabase
requirement for service database connectivity. Backend database roles and service
credentials remain separate from attribution identity.

Migrate attribution deliberately: inventory UUID references, ON DELETE SET NULL/cascade
behavior, text values such as service:pts-import, trigger defaults and supported writers.
Preserve old evidence; do not cast service text blindly or overwrite authorship. Existing
system Auth/profile rows may remain while consumers need them. Remove or retire them
only after references, provisioning and privileges are safely transitioned; this decision
is not authorization to delete live Auth records or system access.

ID-B owns the registry, controlled account_actor.ensure and named System/Migrate/service
bootstrap under the established operator contract. ID-A still establishes the current
baseline first. APIs/DB writes must receive validated actor context across normal,
import/support/migration paths; system attribution cannot be guaranteed merely by having
seed rows. Schema-only migrations use operational deployment evidence; they do not need
to rewrite business-record updated_by fields without a business-data change.

No actor-management UI, account-merging feature, generic identity framework or new
runtime service. Exact actor table/link design and restricted projection belong to the
existing Identity owner. Reuse existing display resolution and owner-controlled setup.

## Acceptance and impacts

Prove account actor without person/organization, System/Migrate without new Auth accounts,
service executor plus human initiator, stable mapping on later person link, separate
accounts for one person, retained attribution after account removal, deliberate new-ID
recreation, safe conflicting/retried provisioning and rejected spoofed actor input.
Verify actual supported bulk/direct writer paths and transaction rollback, not only ORM.

Scaffold: actor-aware attribution, typed current context and owner fixture/migration
patterns. Shared UI resolves permitted display names without showing technical actor
configuration. Agent context and identity/provisioning/legacy-inventory docs link this
choice; consumers adopt references within their delivery items. Accepted ADRs unchanged.
No schema implementation, Auth user deletion, migration execution or readiness pass.
