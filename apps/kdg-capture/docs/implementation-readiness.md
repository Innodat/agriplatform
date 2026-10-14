# KDG Capture — implementation planning readiness

2026-10-14 final successor checkpoint. Installed bmad-sprint-planning, readiness-only.
**Verdict: PASS — planning supports ordered shared foundations and the 19 approved KDG stories.**
A developer can implement this plan without inventing an unrecorded load-bearing design
choice. This is planning readiness, not completed runtime prerequisites, production/pilot
readiness or implementation permission. No sprint-status file is generated.

## Planning authority and closure

All five epics/19 stories remain approved (7/4/2/2/4); 18 FR, 5 NFR, 14 UX and
22 acceptance groups retain owning story coverage. App PRD/UX/spine/contracts/epics/
testing remain authority, with no parallel product specifications. The sole owner
acknowledged shared ownership for all efforts; existing components retain delivery items.

| Planning boundary | Selected contract / conclusion |
| --- | --- |
| Ownership, KDG capability/resource scope, membership renewal and targets | [Shared addendum](../../../platform/docs/architecture/contracts/kdg-shared-readiness.md) and [acknowledged handoff](shared-platform-handoff.md); exact nine organization capabilities/default bundles/read.own entry, own-account/all-org union, current target/setup policy, new membership ID on rejoin |
| ENV/P1/SERVICE | [Environment/generation contract](../../../platform/docs/architecture/contracts/scaffold-environment-and-generation.md) and [exact pins](../../../platform/docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md); newest stable TypeScript 7.0.2, explicit disposable commands/targets/schema/pattern/extension/seed ownership |
| ID-A/B, ACCESS-A/B | [Execution substrate](../../../platform/docs/architecture/contracts/identity-access-execution-substrate.md); physical actor/member/registry/grant constraints, current/target projections, restricted user/setup/operator roles, pre-grant verification, entry/owner commands and source/adoption matrix |
| WRITE/security | [Owned write and secret execution](../../../platform/docs/architecture/contracts/owned-write-and-secret-execution.md) plus [KDG fingerprint disposition](../../../platform/docs/architecture/contracts/operation-fingerprint-security-evolution.md#kdg-initial-fingerprint-disposition--2026-10-14); exact atomic outcome/evidence/FK/lock/role/error/recovery and HMAC/JCS/file/restore inputs |
| Application behavior/contracts | [contracts.md](contracts.md); command/receipt/noop/unknown, prior-child eligibility, bounded pagination, own-only offline/online all-admin, immutable original versions and update-first behavior |
| Dependency and impact ownership | [shared-prerequisites.md](shared-prerequisites.md), [delivery-impact.md](delivery-impact.md); existing shared items precede actual consumers, no duplicate generator/service or whole-Leave dependency |

Architecture finalization and independent reviews close semantic findings. Story coverage,
preceding dependencies and user-value increments remain valid. Existing packages/templates
and accepted designs do not masquerade as implemented KDG APIs/scaffold/current Access.

## Required delivery and release gates

These remain obligations at their consuming items, not unknown architecture choices:

- Shared foundations: actual generator/guarded environment commands, owner/root locks,
  compatible image/container/OS resolution and restricted-role query/constraint/actor/
  operator/current-access tests. Characterize supported legacy writers before migration;
  verify actual target equivalence and coordinated adoption before any live cutover.
- First KDG slice: real app sign-in/fixed Khula/initial version/assigned child/explicit
  offline Save/reopen/reconnect/sync/server record, followed by early installed Android/
  iPhone proof. Local synthetic login is not Entra qualification; LAN HTTPS/DNS/CA/provider
  assumptions must pass actual acceptance. PtS/shared stability is tested after version
  selection and before affected activation.
- Every affected write/update/release: ATDD failure first, focused TDD, actual role/RLS/
  concurrency/rollback/lost-response/recovery and prior payload/schema compatibility.
  KDG HMAC material never enters browser/DB/logs; prove active/old keys, nonroot mount,
  rotation/rollback and matching data+key restore. Migration failure blocks activation;
  no startup migration or automatic destructive downgrade.
- Before affected UI/pilot: Afrikaans content and neutral-theme/contrast review; named
  Khula child-data processing/device and business/audit/pending/locked retention/disposal
  policies, actual backup/archive/decryption identities and release/restore evidence.
  Seven-day access/30-day download are not retention. No real data or pilot is authorized.

Actual generated OpenAPI/Pydantic/TypeScript become model authority during Build.
Concrete changed-schema/payload pairs are supplied with their consuming releases,
not speculative universal adapters. No People/Content/worker/launcher/all-Leave planning
prerequisite is introduced. Leave first slice and own-person requirements remain intact.

## Ordered delivery and authorization boundary

ENV/minimum scaffold → Identity baseline/actor/membership → Access registry/current
KDG checks → trusted owner setup → KDG 1.1 fixed-org entry. WRITE precedes owned domain
persistence/sync, not the read-only context endpoint. Then initial version/child/assignment,
PWA explicit Save/read/sync/device proof; E2 own edits/conflicts → E3 online all-admin →
E4 editor/Publish → E5 children/assignments/update/pilot completion.

**Stop for review before code.** Separate implementation approval is still required.
The next authorized delivery workflow would be bmad-build for the first bounded shared
foundation, with ATDD/focused TDD; do not start a complete editor or implement Leave.
A planning PASS never authorizes migration, grant, secret, infrastructure or deployment.

## Verification evidence and limits

Independent architecture rubric/adversary/technology checks and final readiness review
are in reviews/ and summarized in [review-resolution.md](review-resolution.md).
All applied findings preserve product scope, current authority and owner boundaries.
Planning lint/Markdown/story/diff checks are recorded in the final validation/memlog.
No application/SQL/device test or dependency installation was performed. Earlier FAIL
checkpoints are historical; this report is the current readiness verdict.


Final checks: `python3 .agents/skills/bmad-architecture/scripts/lint_spine.py --workspace apps/kdg-capture/docs`
PASS/zero findings; `python3 /tmp/check-final-kdg-planning.py` 84 Markdown files with
zero findings and all 19 approved story IDs; scoped `git diff --check` PASS. Independent
final-readiness reviewer finds no critical/high design blocker; stale labels reconciled.
Installed readiness question rerun: PASS, with recorded later delivery/pilot gates intact.
