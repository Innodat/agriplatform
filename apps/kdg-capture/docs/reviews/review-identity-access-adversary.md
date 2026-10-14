# Identity/Access execution adversary gate — 2026-10-14

Verdict: the physical ownership, new-ID membership lifecycle and restricted projection design are coherent, but four bounded input/authority gaps prevent independently implemented components from converging. Fix them in planning before claiming this substrate closes executable command/context choices. No code or live target was inspected or changed for this review.

Reviewed `identity-access-execution-substrate.md` against the shared KDG addendum, canonical Identity/Access capability-check contract and controlled provisioning command catalogue.

## H1 — Entry-set persistence lacks a supported write command

The new `access.entry_permissions` table has exact shape and KDG read.own is selected, but no exact command adds that row. `application.register` accepts only app_id/expected_absent; `permission.register` accepts app_id/permission/scope_kind/expected_absent. Operators have command EXECUTE without raw registry DML. The activation sequence requires explicit registered entry configuration, yet these exact payloads cannot express it.

Independent implementation A inserts KDG entry rows in migrations; B changes permission.register to infer entry from suffix or accepts an extra flag. A hardcodes app configuration in schema rollout, while B violates the closed payload or implicitly grants entry semantics. A third implementation leaves the table empty, so KDG direct action checks can work while entry/discovery never qualifies.

Disposition: select one explicit owner command for immutable entry registration, with exact app/permission association, expected absence or declared identical no-op semantics, command authority and compact receipt/evidence. If entry association is mutable, its update/removal and revision protection also need a declared model; do not infer it from permission names. Include wrong-app association, duplicate/no-op, ordinary-operator denial and actual KDG entry acceptance.

## H2 — Accountless setup target queries have no exact SQL context variant

The projection section initially requires trusted app.account_id/app.actor_id/app.org_id context and says missing required context fails closed. Target setup is explicitly service-executor-only, with no user bearer or synthetic Auth account; target routines are not allowed to substitute the target into the caller account context. No paragraph distinguishes which context fields setup must populate, versus acting-user runtime target calls.

Independent implementation A applies a universal non-null account guard and rejects legitimate setup verification. B invents an account selector or synthetic setup account to satisfy it. C omits account context for all target calls but has no stated invariant binding the runtime acting account after assignment.manage verification. The HTTP policy is sound; the internal context contract remains ambiguous.

Disposition: declare closed target execution contexts: runtime has verified acting account/actor/org plus already checked assignment.manage; setup has protected credential-mapped service executor actor/org and exact assignment_target.verify authority, with no account GUC required or fabricated. Target arguments remain distinct from caller identity. Define the common RLS org guard and exact required fields for each variant. Prove accountless setup success, missing/wrong executor/org denial, user/runtime-to-setup denial and pooled-context clearing.

## M1 — is_owner=true has no distinguishable operator authority

membership.join permits true only when “exact owner authority” permits it, but the authority tuple has only command/scope/app/target. The join command authority as specified cannot distinguish ordinary member creation from owner creation; no exact owner-elevation command or protected flag is declared.

Independent command A interprets membership.join authority as allowing either boolean. B always rejects true unless an undeclared extra permission exists. The first can elevate an operator provisioned solely for ordinary memberships; the second prevents intended controlled owner bootstrap.

Disposition: name a separate exact protected authority literal checked when true, or add one explicit narrowly scoped authority attribute with structural checks. Ordinary membership.join authority must permit false only. Do not infer owner authority from app administration, the executor's membership, or the target's old is_owner history. Fixture both permitted controlled bootstrap and denied ordinary join elevation.

## M2 — Account-only projection cannot clearly preserve actor-setup error ordering

`current_account_actor()` returns actor_id nonnullable and describes current profile plus permanent account mapping. An absent profile yields no context, while an absent mapping must yield the safe actor_setup_required outcome **after** authority checks. The account/org routine expressly has nullable internal actor_id, but the account-only routine does not provide an equivalent distinguishable state. access_check_reader is restricted to current projections rather than raw Identity tables.

Independent Access A treats a missing projection row as inactive/absent account and denies PtS authority. B treats it as missing actor and exposes actor_setup_required even when the profile is inactive/absent. Both can claim the stated routine behavior; neither reliably establishes the canonical disclosure ordering.

Disposition: let the account-only projection return active verified account/profile with nullable internal actor_id, or provide a separate fixed current-profile projection used to establish the distinction. HTTP success still requires nonnull account actor. Evaluate current account grant/admission before the missing-actor setup response. Add account-only fixtures for active authorized account without mapping, inactive profile, absent profile and denied grant without mapping. No person or membership requirement is introduced for PtS.

## Attacks already closed

- Identity and Access keep separate histories and DDL ownership; Access references Identity IDs externally without cross-owner grant FKs. KDG cannot read Identity tables.
- Identity candidate projection and Access grant/admission filtering run as one read statement; public limit follows eligibility, so a page cannot disappear merely because early raw candidates lack grants. Replaced membership never substitutes into a point check.
- Distinct account and target DB principals limit normal current checks versus intentional current-org target inspection. NOLOGIN readers are not table owners; FORCE RLS and nonrecursive member context policies are expressly required. Fully qualified routines and controlled ACLs protect definer execution; actual privilege/connection-pool evidence remains a gate.
- Operators derive executor from session_user rather than current_user/SET ROLE/GUC/payload; separate owner mapping/command authority and no raw DML prevent self-grants.
- Membership joins serialize org/account, require predecessor history and allocate new IDs without copied roles/grants. Retirement names exact membership/revision; old delayed retirement cannot hit a replacement. Unique active membership and noncascading retained history are explicit.
- Grants preserve legacy text IDs and provenance; unmatched references cannot become effective. Incompatible legacy direct writers require characterized adoption and maintenance cutover rather than an assumed additive safe transition.

WRITE outcome/evidence detail remains explicitly deferred. This review does not turn deferred runtime proof into planning approval or authorize schema/code implementation.

## Resolution recheck — 2026-10-14

Verdict: all four findings are resolved in the amended planning contract. No remaining blocker from this review.

- H1: `entry_permission.register` now has exact app/permission/expected-absence payload, verified matching association, immutable mapping and compact receipt semantics, with identical mapping unchanged and no implicit permission/grant creation.
- H2: user and accountless setup contexts are explicit. Separate setup-only login/NOLOGIN reader authority permits only point verification, rejects mixed context and leaves account_id absent; service executor attribution cannot become target identity.
- M1: `is_owner=true` requires the additional protected `membership.join_owner` authority for the exact scope/target; ordinary join authority permits false without that elevation.
- M2: current-account projection now distinguishes absent profile/no row from verified profile/missing actor through nullable internal mapping fields. Public success still requires an account actor, and authority checks precede the setup response.

The restricted pre-grant Identity projection grant makes Access's current-member verification implementable without requiring the very capability being assigned. PostgreSQL15+ is now an explicit target qualification floor. Actual ACLs, forced-RLS execution, pool context clearing, command concurrency and clean/adopt compatibility remain the declared delivery evidence gates.
