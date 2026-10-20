# Existing token hook: current organization evidence

Bounded Identity ID-B correction, 2026-10-20. The accepted E1 membership contract
requires Auth hooks to select active membership and nonretired organization. This
increment filters the existing legacy hook; JWT claims remain historical hints and
never replace current Access authorization. See [Build](../../_bmad-output/implementation-artifacts/spec-id-b-token-hook.md)
and [owner runbook](IDENTITY-MIGRATIONS.md). Full ID-B/Access/WRITE/KDG readiness remains open.

## Scope and compatibility

Identity revision10 replaces only identity.custom_access_token_hook(jsonb) body and
search_path through the existing Identity owner. Fallback and org_ids exclude retired
organizations; exact member lookup requires current account, active membership and active
organization. Existing top-level event.user_metadata selection, owners-first/created_at
fallback, explicit invalid selection without substitution, active organization slug,
claim shapes, other event/claim fields, role deletion and typed UUID errors remain.
Profile lifecycle is unchanged. Existing owner, exact ACL/effective execute grants and
all other functions are preserved. No new roles, credentials, schema/API/service or UI.
Nine historical revisions/references/source pins, original SQL and generated composer
outputs remain immutable. This does not activate membership lifecycle or Access grants.

## Requirement-to-test evidence

| Requirement | Executed proof |
| --- | --- |
| Observe gap before correcting legacy behavior | Focused CPU acceptance RED missing10/head; root head9-observation.json records actual retired selected/fallback membership/admin/owner claims and retired org_ids, mutations rolled back |
| Emit authority only for own active membership/organization; preserve selection and shape | TokenHookQualification characterization/reads, existing restricted access_runtime login SET supabase_auth_admin, rollback-only fixture changes |
| Preserve compatibility, migration safety and source custody | Qualifier per-function/ACL comparison; clean/adopt/exact9/repeat; injected CREATE FUNCTION rollback/recovery, drift/unknown refusal; full data/external-reference hashes; recorder tests |
| Bounded isolated execution and restoration | SQL/lock deadlines, private durable required/restored witnesses, temporary SET-only edges restored exactly, pooling/search-path proof |

Actual proof starts at platform/deployment/.local/identity-baseline/token-hook-qv4fbmr4/.
The root uses the frozen approved owner environment; no dependencies or pins change.
Scratch Auth users are synthetic stub rows; auth.uid/auth.jwt definitions match native.
Direct database invocation does not prove provider/JWT-signature/HTTP integration or
real account onboarding. The existing native project is used only as an isolated local
server; no real accounts, access, production migration/provision/deploy/pilot or deletion.

## Five impact decisions

- Scaffold: reuse the existing Identity migration/reference/recorder/qualification
  pattern. No new generator, recipe or runtime abstraction is needed for one legacy hook.
- Shared UI: no user interface change or component promotion.
- Agent context: existing AGENTS.md rules suffice; current limits and verified commands
  live in the owner runbook and KDG continuation document.
- Documentation: this evidence, owner runbook, ownership inventory and KDG navigation
  identify the delivered boundary and still-open owner work.
- ADR: implements existing accepted E1 membership/organization and ADR0020 migration
  safety contracts. No new architectural decision; accepted ADRs remain immutable.

## Verification status

Initial actual matrix PASS27.914s with source_unchanged true. The first attempt stopped
before migration because root grouped characterization setup with three required prior
upgrade receipts. Original four-receipt record and failed attempt are retained; splitting
the characterization receipt corrected proof bookkeeping without changing source/tests.
The successful matrix records16 stages plus recorder/characterization and exact SET-edge
restoration. Full per-function comparison proves only the hook body/search_path differs.
Source bytes and all earlier sources/references are retained; no failure is erased.

Affected suite567 PASS22.38s, no skips, using the frozen owner Python:
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider`.
Both `tools/py/run_compose_supabase.py --check-only` and
`--identity-authority owned --check-only` exit0. New reference SHA256:
f227a7839ba8e04fe1626254e91678c73cf3fc2aa5e38fdb0a5b1ec6a3633263.
Root independent review and final source-bound checks follow; no permission to activate
a real target is implied.


## Final reviewed-source acceptance

Retained final frame: platform/deployment/.local/identity-baseline/token-hook-reviewed-p8m4d4yu/.
Full actual matrix PASS30.111s, source unchanged;19 recorded stages include unchanged9
characterization and restricted-role/migration/read proof. All matrix rows execute and
pass, including complete no-eligible-org fallback, deleted-member identity/owner/org_ids,
active membership with no roles, absent claims initialization, distinct missing account,
metadata selection, foreign/retired contexts, spoof/pool reuse and unchanged data hashes.
Per-function comparison allows only hook body/search_path changes; ACL/declaration and
all other catalog categories/functions stay. Clean/adopt/exact9/repeat, actual injected
mid-revision failure/atomic rollback/recovery and drift/unknown refusals pass. Temporary
role edges and injected failure objects restore exactly. New SQL/reference/pin unchanged.

All three independent reviews complete (Blind10, Edge0, Verification0). Nine direct
documentation/fixture-test corrections are verified. A low suggestion to add automatic
cluster locking was rejected: this root-only synthetic route requires sequential
same-cluster execution, now explicit beside the commands. No new locking framework or
deferred finding. Grant failures before mutation/after commit and failed cleanup now
prove exact handler/receipt behavior. Existing membership FK remains; this hook adds no
active-profile check and preserves the tested soft-deleted-profile behavior.

Final affected suite577 PASS26.24s, no skips; both composition checks and whitespace
check PASS. No root-wide npm verification exists; the stale root wrappers are not used.
All five impacts remain as recorded above. Normal retained-data stop, preservation/safe
output audits, final source manifest and local scoped commit receipt complete this frame.
All2635 protected originals remain; only seven intended existing files change. Original
concurrent Scribeswell/Expense/brainstorming/spec work and all prior failed frames,
receipts/state/data/resources remain. No broader Identity/Access/KDG readiness is claimed.
