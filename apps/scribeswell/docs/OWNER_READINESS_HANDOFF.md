# Scribeswell owner readiness handoff

As of 2026-10-27, after local checkpoint `321f7eb`. This is an operational handoff,
not a new feature specification, accepted owner contract or release authorization.
The [canonical spec](../../../_bmad-output/specs/spec-scribeswell-studies/SPEC.md),
[Access contract](../../../services/access/STUDIES-ENROLLMENT.md) and
[final integration evidence](FINAL_INTEGRATION_EVIDENCE.md) remain authoritative.

Personal Studies and genuine standalone signup have passed the isolated real-owner
qualification. The next bounded delivery is **default Access startup and coordinated
release evidence**, after the two owner contracts below are updated. Sharing remains
separate; implementing a substitute Access or Notification path would cross ownership.

## Access/Identity owner: current-head Studies readiness

Evidence: `services/access/studies_readiness.py` requires exactly `identity_0021` /
`access_0016` in both `prepare` and `validate_artifact`. Current migration heads and
the successful app fixture use `identity_0025` / `access_0018`.
`services/access/main.py:create_app` requires the validated artifact when constructing
Studies database connections from environment settings. The app fixture intentionally
injects those databases and therefore does not prove this default startup path.
No current-head readiness artifact was generated or claimed by Scribeswell.

Copy this request to the owning Access/KDG session:

> Continue the delivered personal Studies enrollment/check readiness contract for
> current Identity/Access heads. Read Scribeswell's OWNER_READINESS_HANDOFF.md and
> existing STUDIES-ENROLLMENT.md; preserve the working tree and KDG compatibility.
> Reconcile studies_readiness.py prepare/validate with the owner-approved current
> heads (currently identity_0025/access_0018) and refresh genuine source-bound owner
> qualification. Preserve exact principal/service-executor binding, restricted roles,
> source/catalogue verification, current Auth/profile evidence, migration ordering,
> revocation, deadlines and refusal of stale/partial/unsafe evidence. Do not simply
> accept arbitrary newer revision strings or synthesize successful proof fields.
> Use BMAD with ATDD/TDD and actual native qualification. Return the adopted contract,
> exact startup environment/artifact interface and source-bound evidence showing the
> unmodified default create_app path starts on prepared current owners, while missing,
> stale, mismatched and unsafe preparation still refuses. Keep recipient/invitation
> delivery separate and explicitly undelivered unless you implement/qualify it.

Owner chooses the compatible artifact/version policy. Scribeswell consumes that
published policy; it does not relax the owner's validation or fabricate its artifact.

## Application and platform release owners: truthful private-head reporting

`apps/scribeswell/deployment/studies_migrate.py:upgrade` upgrades Alembic `head` but
returns `after:scribeswell_studies_0001`. Both
`apps/scribeswell/deployment/migrate.py` and `platform/deployment/host-release.py`
require that exact four-field result. Actual private head is
`scribeswell_studies_0009`. Existing native ledger proof establishes the real schema;
the old release report cannot be treated as evidence that head0009 was recorded.

Request for the platform release owner, coordinated with this application session:

> Agree and publish a compatible private migration-report contract with Scribeswell.
> Require truthful observed before/after ledger revisions and the intended release
> target, while retaining controlled migration-before-activation, bounded supervision,
> previous-running-version compatibility and forward recovery. Update the helper,
> application supervisor, host validator and affected tests together; do not change
> only the application's hard-coded marker or accept arbitrary successful JSON.
> Qualify real current-head upgrade and repeat, wrong head, failed/unknown outcome,
> stale evidence and activation refusal, plus ordinary compatible release/recovery.
> Do not deploy or activate production as part of the contract change. Preserve all
> unrelated Leave/Access/platform working-tree changes.

The report shape/version remains an owner decision. This handoff adopts no new wire.

## Scribeswell continuation after owner delivery

Consume the adopted artifacts in the existing isolated fixture (Auth55491/DB55492),
with a fresh canonical run ID and immediate port/subnet checks. First observe the
relevant failure on the current default-startup/release boundary; implement the app
consumer against the published contract. Then prove default service startup with real
restricted owner credentials and actual provider checks, followed by the existing
browser/SQL/signup/privacy cases. Verify coordinated migration reports and refusal
paths without production activation. Keep KDG55481/55482 and Leave environments alone.

Production signup/SMTP requires the deployment owner's real environment and delivery
verification. Local Mailpit proof is complete and must not be relabelled external mail
proof. Physical iOS/Android selection, OS Copy and keyboard acceptance needs actual
devices. Neither gate can be completed by another intercepted browser test.

## Sharing remains a separate owner dependency

The [recipient/invitation facade](../../../platform/docs/architecture/contracts/scribeswell-study-enrollment.md)
and [Notification/inbox contract](../../../platform/docs/architecture/contracts/notification-delivery-and-account-inbox.md)
are still explicitly proposed and undelivered. No matching recipient facade or common
notification runtime was found in the current service tree. Before a sharing consumer,
owners must publish implemented recipient resolve/verify/error/freshness contracts and
qualified account-scoped notification acceptance/inbox/dedup/retry/retention behavior.
Scribeswell then owns invitation/share transitions and its outbox under those contracts.
Existing own copies do not establish shared-source/private-response delivery.

## Checks and limits

Read-only focused verification:

```sh
PYTHONDONTWRITEBYTECODE=1 apps/scribeswell/.local/owner-integration-20261027/python/bin/python -m pytest services/access/tests/test_studies_readiness.py apps/scribeswell/tests/test_personal_notes_release.py -q
```

**7 passed in0.43s**. These tests exercise the existing older contract and release
refusals; they do not prove current-head default startup or a coordinated release.
[Source references/hashes and result](evidence/owner-readiness-handoff-20261027/checks.json)
are after-only observations, not a before/after source freeze. No new native fixture,
migration, readiness artifact, provider request or activation ran for this handoff.

Impacts: documentation only; no scaffold, shared UI, agent-context, ADR, runtime or
owner implementation changes. Existing foreign changes are preserved. Coordinator
model/effort inherited, actual model/usage/compute elapsed unavailable; no subagents
or implementation retries. Test duration above is measured separately.
