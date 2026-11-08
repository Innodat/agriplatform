# Studies production target readiness — 2026-10-28

**Cross-release continuation — 2026-11-01:** use the
[Leave E1 / Scribeswell-PtS ownership handoff](OWNER_READINESS_HANDOFF.md#leave-e1--scribeswell-pts-release-alignment--2026-11-01).
The existing production-adoption delivery owns the shared transition and consumes
completed E1-PTS-ADOPT work. Its recorded 2026-10-28 scope decision supersedes the
scope-pending wording below. Reconcile the frozen Identity0026 Studies candidate with
PtS/Leave's Identity0030 requirement before qualifying the exact release; no new
readiness pass or production execution is implied. Full Leave E1 closure is not a gate.

Private access to `machon` is restored. The latest read-only target checks are
recorded in [safe target evidence](evidence/bounded-studies-rollout-20261028/target-readiness.json).
This supersedes the earlier connectivity blocker, not the migration/readiness gates.
No production release is currently eligible for approval or activation.

## Actual running state

The backend runs `2480de173149cc646e8c1c55d088a93c4b196f47` in Compose project
`agriplatform-production`; all five APIs are healthy, with zero restarts, and the
gateway is running. No application/TLS activation marker is pending. Public Bible
books return HTTP200 with39 books; private Studies returns404. The public frontend
identity reports `b7cb5b8c9ebb455eabaa7f1995353c9ecfd1c32c`; its separate current
build identity must be preserved in frontend preparation.

| Owner | Current state | Release prerequisite |
|---|---|---|
| Identity | postgres-owned schema, no owned ledger | Explicitly qualified legacy-profile adoption to Identity0026 |
| Access | `access_0001`; migrator/runtime INHERIT=true; three PtS grants | Scoped authority preparation, explicit grant adoption and consumer coordination before0019 |
| Public corpus | postgres-owned schema, no owned ledger | Existing documented restricted migrator/ownership preparation and exact-reference adoption |
| Private Studies | No schema or roles | Restricted role preparation and controlled migration to0009 |
| Content / PtS | `content_0004` / `pts_0001` | Preserve running contracts until their explicit coordinated replacement |

The known consumer still exists and is confirmed. Its three existing grants are
`pts.poetry.read`, `pts.poetry.export` and `pts.poetry.documents`. They are legacy
organization grants, not authority to fabricate Studies or new account-scoped grants.
No account identity or credential is included in safe evidence.

## Concrete release blockers

1. **Identity adoption is unsupported for this baseline.** The owner guide explicitly
   excludes postgres ownership and the production correction that already denies
   PUBLIC execution of `public.get_user_roles()`. Authenticated execution remains
   enabled. Ownership transfer alone cannot establish catalogue/ACL equivalence.
   See [the owner contract](../../../services/access/IDENTITY-MIGRATIONS.md).
   A new owner-reviewed profile must be derived independently from pinned bootstrap
   sources and the reviewed security correction. Never record the target's catalogue
   as its own trusted reference or temporarily reopen PUBLIC execution.
2. **The existing PtS caller is incompatible with the selected Access image.** Read-only
   inspection of the actual running PtS image confirms `/v1/check` use; its source
   hash matches the retained client. Inspection of the actual frozen Access image
   `792933a8b3678b78657588e230e4f14dbbfe0e44909e616b56e1f9cf25448eba`
   confirms the handler deliberately returns503, matching exact source
   `deb424b0c4d29016917c9df39b540a468ca8e1cf`. This is established behavior, not
   an inferred network outage. Replacing Access alone would disable protected PtS.
3. **Existing grants cannot be silently upgraded.** Access0012 installs registered
   permission/scope and complete active provenance constraints without backfilling
   the three current grants. Accepted [ADR-0052](../../../platform/docs/architecture/decisions/0052-pts-account-scoped-access-and-coordinated-adoption.md)
   requires explicit account capability provisioning and coordinated PtS/Access/
   Directory adoption, with the corpus/Content boundary settled before implementation.
   Do not recreate a legacy compatibility facade or infer account authority from
   existing organization grants.
4. **The managed deployment authority differs from the qualification fixture.** Its
   `postgres` login can create roles but is not superuser. The current Studies role
   helper explicitly requires superuser. Native-superuser success cannot establish
   that helper is executable on this managed target. Required owner/runtime roles
   are absent; current PUBLIC-derived TEMP privileges also require an explicit
   least-privilege preparation plan preserving legitimate consumers.
5. **Qualification material must be durably recoverable.** The original current-head
   archive and raw qualification were retained under `/tmp`; those paths are now
   unavailable. The qualified frozen image is still present and unchanged. Earlier
   Identity25/Access18 records retained under `.local` cannot stand in for the exact
   Identity26/Access19 preparation contract. Recover/reissue required owner evidence
   into protected durable operational storage before the release gate is usable.

## Bounded next delivery

The next decision is whether to include the coordinated owner/PtS prerequisite in
this Studies release task. Routine BMAD checkpoints do not imply that scope change.
The pending question is recorded in the new delivery draft; production stays unchanged.

If included, first settle the app corpus/Content authorization boundary under the
accepted ADRs and record explicit intended account grants. Then prepare an isolated
owner adoption bundle and managed-database provisioning recipe for this exact source-
reproducible legacy profile. Keep immutable histories/references and the original
qualified runtime inputs unchanged; prove exact final convergence before using the
original readiness contract. Coordinate actual PtS/Directory consumers and preserve
Expense's authenticated helper/Auth hook behavior.

Qualification should cover this one initial production profile and its specific
failure/forward-retry/recovery cases with synthetic rows and external-reference
sentinels. This is a targeted prerequisite, not a broad version-upgrade rehearsal.
Public corpus preparation already has an owning contract; do not invent another.
No implementation is authorized merely by this operational report.

After prerequisites pass, the [bounded Studies runbook](BOUNDED_STUDIES_ROLLOUT.md)
remains the app cutover plan: one configured account, current Access checks, no
self-enrollment, migration-before-activation, a15minute maintenance limit and public-
reader recovery that preserves private schema, saved rows, revisions and receipts.
Actual publication, grants, migrations, activation and any production verification
writes require a concrete reviewed execution approval. Do not request approval for
an execution sequence that is known to fail readiness.

## Evidence and impact

The current checks performed read-only SQL with transaction_read_only=on, public
HTTP GETs and network-isolated frozen-image byte inspection. No production SQL
mutation, grant/account change, mail, image publication or activation occurred.

Automatic approval review rejected exporting full Compose because it could contain
embedded secrets. No such export occurred. The completed collector retains only an
explicit metadata allowlist; raw environment/configuration values and TLS keys stay
on the host. Private operational records remain under the ignored app `.local` tree.

Scaffold/shared UI/agent context/ADR: no changes in this investigation. Documentation
and delivery tracking record the actual target mismatch; unrelated staged and working
changes, including Identity0027, remain untouched.


## Shared release continuation — 2026-11-01

The historical findings above remain the observed production predecessor. The
owner subsequently authorized the targeted coordinated Identity/Access/PtS
prerequisite within this Scribeswell release. This release owns shared adoption,
cutover and recovery; Leave and KDG consume its result afterward. Their application
activation, full Leave E1 and hosted Reference verification are outside this release.

The selected managed-host equivalent is `hosted-e1-v1`, with true eventual heads
`identity_0031_e1_hosted` / `access_0020_hosted` and independent operational reference
`7420343a374758599dacf4b8d93dc690197bb8bc0bec2fbee4441b145b617b85`.
It preserves the reviewed People27/actor28/session29/cleanup30 and Access19
contracts. Canonical0030/0019 were not executed or stamped on this profile. Frozen
Studies0026/0019 and KDG0028 proof retain their original identities; neither is
evidence for this successor. See the current
[owner handoff](OWNER_READINESS_HANDOFF.md) and existing production adoption spec.

Operational predecessor and hosted E1, restricted owner command transport, managed
Studies preparation, packaged private-only/PtS migrations, retained-data failure/
forward retry, maintenance stop/backup coordination, public-only API recovery and
both frontend variants have focused source/native/image evidence linked from the
handoff. Content/PtS target schemas already have the correct owners; preserve
existing provider role edges. These proofs do not establish target adoption or
final coupled readiness. All actual-target work so far remains read-only.

Remaining release gates are final successor readiness/activation integration and
source-bound coupled qualification, concrete private owner/principal/grant/corpus/
Content binding commands, dedicated file DNS/certificate preparation, final review
and explicit production execution approval. Public reading and saved data must
survive failure/recovery; no rollback of applied owner histories or restored dump
over later acknowledged saves is authorized. No production activation or image/
frontend publication has occurred.


Current preparation update — 2026-11-02: selected hosted31/20 equivalent to reviewed
canonical30/19 now has source-bound genuine owner/provider qualification, separate-
target readiness, actual default API/Access save/recovery, and complete eight-image
inspection. Real Scribeswell-root `/` + current PtS `/pts/` builds/browser checks
passed at their recorded canonical boundary. The gateway metadata correction leaves
q3's338 sources and API/migration/runtime owner closures exact. Private target owner/
role/credential/grant/corpus/Content proposals and ordered recovery run card exist;
all remain unapplied. See OWNER_READINESS_HANDOFF.md for exact proof boundaries.
Canonical successor/review, actual provider/certificate/runtime staging/publication,
callback allowlist compatibility and explicit execution approval remain. Automatic
review rejected API token verification before execution; specific credential egress/
custody authorization is still required. Production reading/data remain unchanged.
