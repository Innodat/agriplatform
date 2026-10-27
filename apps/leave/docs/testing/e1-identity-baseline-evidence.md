# E1-ID-A: existing Identity baseline evidence reconciliation

2026-10-26. [Execution spec](../../../../_bmad-output/implementation-artifacts/spec-1-4-e1-id-a-identity-migration-baseline.md).
Story authority: [E1-ID-A criteria](../../../../_bmad-output/planning-artifacts/epics.md#candidate-story-e1-id-a-establish-a-verified-identity-migration-baseline).

**Status: accepted; tracker review — 2026-10-26.** After reviewing the concrete
reuse proposal, the user approved the existing hardened sequential Identity history
as Leave's foundation and authorized ID-B. A separate hardened pre-ID-B history is
not required. Revision 0001 alone remains unsafe; later revisions 0008/0009/0010/0020
supply the safeguards. This acceptance does not complete ID-B or expand the historical
proof into fresh current-head database/provider qualification or live activation.
Earlier unresolved-independence entries below preserve the pre-approval assessment;
they are superseded only by this explicit user disposition, also recorded in the
owning story.

No production implementation, applied migration, reference, historical receipt or
database is changed by this reconciliation. Normal development continues on shared
KDG; any future destructive acceptance uses the existing disposable Leave target with
root-controlled setup. No fixtures or retained qualification drivers were rerun here.

## Requirement traceability

Paths in this table are repository-relative. CPU tests establish source/wrapper
behavior; actual permission, rollback and Auth claims come from the historical
synthetic database proofs cited separately. Current source ends at `identity_0021`.

| Original story criterion | Existing source and focused tests | Actual retained proof and remaining limitation |
| --- | --- | --- |
| Fresh controlled baseline creates owned objects once, separate private history and restricted roles; no takeover of Access/Auth/other owners; public routine and Auth trigger included | `services/access/identity-alembic.ini`; `identity-migrations/env.py`; `identity_baseline.py`; `versions/0001_baseline.py`. `test_identity_baseline.py`: pinned sources, scoped integration, private ledger, known-head and final-postcondition tests | [Baseline evidence](../../../../services/access/IDENTITY_BASELINE_EVIDENCE.md): actual `identity_migrator` LOGIN clean/repeat at revision 1, Access history untouched, project-owned public routine/trigger and actual native Auth setup. Auth schema/table owners separately grant only required hook privileges. This is selected synthetic-owner proof, not transfer/adoption of a live target or fresh revision 21 proof. |
| Matching legacy schema adopts without record recreation; mismatch refuses safely; no blind stamp/destructive repair; UUID/reference meanings preserved | `identity_baseline.py` source/reference pins, legacy/owned fingerprints and preflight; `env.py` refuses stamp/ensure-version/offline paths. `test_identity_baseline.py`: source/reference tamper, mismatch, private ledger, exact catalog/revision, rollback-postcondition tests | Baseline `second-cases/identity-qualification.json` and `review-cases/` prove actual equivalent adoption/repeat with row, sequence and original ledger/external finance/CS reference preservation; ACL/trigger/owner/default/column/history mismatches refuse. Exact-owner equivalence intentionally rejects other-owner or independently hardened targets. Recovery requires reviewed forward repair or tested restore, never target self-approval. |
| One authority per adopted object; handover in composer/configuration; Finance/content and supported clean bootstrap preserved | `tools/py/run_compose_supabase.py` explicit owned selection and `validate_identity_seeds`; `test_identity_composition.py`: exact source handover, duplicate/stale output and seed refusal before writers | Baseline proof executes nine composed non-Identity sources and retained synthetic seeds at historical revision 1, preserving finance/CS dependencies. Current revision 17 cutover deliberately requires `--no-seeds`; that historical seeded route is not the supported current owned route. Both current composer checks are recorded separately below. No generated SQL was edited. |
| Intended Auth/profile behavior supported; privileged self-update, unauthorized role lookup and unsafe helper execution prevented; owners/search paths/execute grants explicit | `versions/0008_profile_fields.py`, `0009_legacy_roles.py`, `0010_token_hook.py`, `0020_check_reader_bridge.py`; `identity_baseline.py` effective privilege/catalog checks. `test_profile_fields.py`, `test_legacy_roles.py`, `test_token_hook.py`, `test_check_reader_bridge.py` | [Profile](../../../../services/access/PROFILE_FIELDS_EVIDENCE.md) proves protected-column denials and supported writes; [roles](../../../../services/access/LEGACY_ROLE_LOOKUP_EVIDENCE.md) proves exact active token binding/native helper parity; [hook](../../../../services/access/TOKEN_HOOK_EVIDENCE.md) proves active membership/org selection and claim compatibility; [bridge](../../../../services/access/CHECK_READER_BRIDGE_EVIDENCE.md) proves restricted six-routine ACLs, owner-only `create_user`, supported Auth/Expense callers and denied forged-context reader calls. Baseline-only characterization showed a real unsafe UPDATE-only self-admin path and retained PUBLIC execution; revision 1 is insufficient. Provider sign-in/JWT pipeline and live legacy target compatibility remain unqualified. |
| Failure blocks dependent activation; completed changes accurately reported; explicit recovery exercised on disposable data; no startup migration/runtime DDL/automatic downgrade | `env.py` bounded atomic transaction and safe reconciliation errors; owner migration downgrade refusals; `tools/py/deploy_pts.py` `migration_owners`, `migrate`, exclusive per-attempt evidence and `activation_allowed=false`. `apps/pts/tests/test_release.py`: failure stop/no reverse, partial failure evidence, Identity-first order and separate configuration | Baseline actual coordinator mismatch blocks Access/Content/PtS with target unchanged; actual trigger-install failure rolls back before forward retry; advisory lock contention/retry and runtime denials are retained. Later profile/role/hook/bridge proofs add injected revision failure, exact rollback/reconciliation/retry, private ledger and restricted permission checks. This does not qualify real release activation, an arbitrary incompatible live adoption or provider maintenance recovery. |
| Failing-first clean/adopt/mismatch/privilege/failure tests independently of ID-B; exact commands, inventory/recovery/reuse recorded; no production destructive fixture/migration claim | Focused seven-file CPU suite and both current composer checks below; owner runbook/inventory; historical ATDD records in each owner evidence file | Historical baseline final 23 CPU tests and native revision 1 proofs predate ID-B but leave privilege safety unmet. Later hardened proofs depend on the sequential Identity history containing ID-B. Current CPU passes cannot establish independent native acceptance. Keep in progress pending a supported explicit disposition; do not waive or silently reinterpret this criterion. |

## Historical proof custody

Read these owner files in full for exact commands, failures, source/reference pins and
qualification limits. Final frames supersede earlier attempts only for their declared
source; earlier failures and original receipts remain evidence. The profile, role and
hook rows are historical owner-reported proof; their separate final frames were not
byte-audited in this reconciliation. The new byte audit below covers the original
baseline and final check-reader bridge artifacts only.

| Owner evidence | Final retained frame under `platform/deployment/.local/identity-baseline/` | Declared final proof |
| --- | --- | --- |
| `IDENTITY_BASELINE_EVIDENCE.md` | `qualification-im60qj1l/review-cases/` (with original `second-cases/` retained) | Restricted clean/adopt/refusal/rollback/retry/composition proof; final reference `ae183b435b2659efbe1a9f2ffdf3eaf1b8d64b2f9256ea72927b6f78453beb00`. Four overwritten second-case focused-check output paths are an acknowledged historical custody limitation; their earlier exact bytes were not recovered. |
| `PROFILE_FIELDS_EVIDENCE.md` | `profile-fields-reviewed-y531afuh/` | Historical owner-reported proof (not separately audited here): actual matrix PASS in 43.923 s, 22 stages; affected CPU 474 PASS. Final profile reference `05ccb6afc5c546d18ea16747a59d4e63c6f8576718d885b43ecc03e676779868`. |
| `LEGACY_ROLE_LOOKUP_EVIDENCE.md` | `legacy-roles-final-x3t9_a5_/` | Historical owner-reported proof (not separately audited here): native-parity actual matrix PASS in 59.688 s, 20 steps; affected CPU 523 PASS. Final role reference `983d00ac73bfc9d86188ce166cece3c246926f169b9993af0141a527d8bbd0aa`. Earlier blank-sub native failure remains recorded. |
| `TOKEN_HOOK_EVIDENCE.md` | `token-hook-reviewed-p8m4d4yu/` | Historical owner-reported proof (not separately audited here): actual matrix PASS in 30.111 s, 19 stages; affected CPU 577 PASS. Final hook reference `f227a7839ba8e04fe1626254e91678c73cf3fc2aa5e38fdb0a5b1ec6a3633263`. |
| `CHECK_READER_BRIDGE_EVIDENCE.md` | `check-reader-bridge-reviewed-20261022/` | Final native 11 stages and separate retained inspection exit 0; affected CPU 1745 PASS. Final bridge reference `154c165f0f5635d42f2ecca1a0b75033be0aa7ef344353042cbcfc3ed72770a7`; 178 source hashes, 29 logs, 83 catalog and 24 snapshot categories bound. Earlier blocked and failed bridge frames remain. |

Root's new read-only baseline/bridge custody audit passed; exact results and commands
are recorded in the [2026-10-26 machine receipt](evidence/e1-identity-baseline-20261026.json). It verified
20 original baseline files against historical Git `e4723c5ca371df01779af3964d306d0fcd38bc0c`,
seven original source pins and the baseline reference, 30/30 baseline log hashes, three
published hardening receipt anchors, 29/29 hardening log hashes and 43 historical revision 19
bootstrap files against their source Git. Of 178 recorded hardening sources, 172 still
match current bytes. Six have later drift: `platform/deployment/dev.py`,
`platform/deployment/native_cli.py`, `services/access/identity-migrations/identity_baseline.py`,
`services/access/main.py`, `services/access/migrations/access_baseline.py` and
`services/access/tests/test_check_reader_bridge.py`. Relevant revisions
0001/0008/0009/0010/0020 bytes still match. The audit made no database contacts and
does not assert
retained database state or fresh head 21 execution.
A source differing from a historically captured source is not fresh execution proof
and does not itself invalidate a correctly bound historical run. No new database
requalification is claimed by reading or hashing retained artifacts.

## Current verification

Root repeated the focused suite with source capture: **300 passed in 7.79 s**, with
both composer checks exit 0. The initial unbound-source run passed in 30.61 s and is
retained separately. The repeat records 90 selected source hashes unchanged throughout
verification, the selected interpreter hash/version, installed package versions and
explicit plugin/bytecode environment settings. These are current CPU/source-selection checks, separate from historical actual
database qualification. Exact commands/results and hashes are recorded in the machine
receipt. The receipt embeds the read-only audit source for inspection/reproduction,
anchors baseline audit-input hashes and identifies each resolved baseline log path and
expected digest. Reproduction requires the retained local artifacts; it does not create
fixtures or contact a database. Execution used the prepared Python without dependency changes:

```sh
OWNER_PYTHON=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests/test_identity_baseline.py services/access/tests/test_identity_composition.py services/access/tests/test_profile_fields.py services/access/tests/test_legacy_roles.py services/access/tests/test_token_hook.py services/access/tests/test_check_reader_bridge.py apps/pts/tests/test_release.py -q -p no:cacheprovider
"$OWNER_PYTHON" -B tools/py/run_compose_supabase.py --check-only
"$OWNER_PYTHON" -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only
```

No broader repository suite, live adoption, provider operation or release activation
is qualified. Root npm wrappers are not used as application/repository verification.

## Acceptance disposition history and impacts

The following records the pre-approval question. The user resolved it above on
2026-10-26; no acceptance decision is pending.

The unresolved question is whether an already delivered, hardened sequential owner
history that includes ID-B can satisfy the approved **independently of ID-B** completion
criterion. Historical revision 1 proof cannot answer yes because its documented privilege
safety was insufficient. Later restricted-role proofs establish the fixes at their
declared heads; they do not establish an isolated hardened ID-A route. No new production
behavior or migration-history rewrite is authorized to manufacture that route. Keep
E1-ID-A in progress until an explicit supported disposition exists. The user owns this
acceptance decision. Root has asked the user to choose between accepting the existing
hardened shared history and retaining strict independence with a separately planned
solution. No waiver has been granted and no next dependency may proceed yet. This reconciliation
does not complete ID-B, authorize Access/Leave activation or change approved criteria.

Scaffold: reuse delivered owner/composer/coordinator evidence; no new scaffold change
or promotion is justified here. Shared UI: none. Agent context: existing rules suffice.
Documentation: clarify the owner runbook/inventory and map Leave evidence; root updates
tracking after review. ADR: existing decisions apply; accepted ADRs remain unchanged.
