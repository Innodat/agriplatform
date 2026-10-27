---
title: 'E1-ID-B: Complete shared person linking and own-account preferences'
type: feature
created: '2026-10-26'
status: done
route: dispatch
baseline_commit: 6926cb527e319e1842c105c06fcd5d5fabac4a45
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/development/migration-verification.md'
  - '{project-root}/platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md'
---

<frozen-after-approval reason="approved Leave implementation continuation; epic-level review">

## Intent

Complete E1-ID-B using delivered actor/membership foundations. Add the missing independent
person identity, verified account/person linking and own-account language persistence
inside the existing Identity maintenance/service boundary. Preserve retained account,
actor and membership meanings. User accepted hardened shared history as ID-A foundation.

## Boundaries & Constraints

Always use additive Identity migrations after0021, controlled owner commands, current
exact authority and atomic compact outcomes/evidence. One person may have several
separately authorized accounts; accountless people are supported. Account linking
never allocates/replaces an actor or creates employment, membership or grants. No email
merge or conflicting relink. Preserve historical sources/references and dirty work.

No new runtime service, live migration/account/provider operation, shared KDG mutation,
automatic repair/downgrade, startup migration, grant union, copied personal documents,
whole-profile evidence, root dependency change, commit or remote operation. Root alone
owns native fixture/lifecycle/reference recording on the existing disposable Leave run.

</frozen-after-approval>

## Code Map

- Story authority: `_bmad-output/planning-artifacts/epics.md`, E1-ID-B. Owner semantics and
  language wire contract: `platform/docs/architecture/contracts/identity-access-employment-e1.md`
  (person/account distinction; final account-language section). Read relevant sections.
- `services/access/identity-migrations/versions/0018_account_actor_ensure.py`: protected
  account command, live-account verification, lock/replay, typed outcomes/events; reuse.
  `0005_operator_authority.py` defines command scope CHECK and authority function allowlist.
  Extend their active definitions additively, never historical files.
- `identity_operator_input.py`, `identity_operator.py`, `operator_cli.py`: closed parsed
  commands, JCS fingerprints/UUID normalization, typed receipts, original-login worker and
  execute/outcome transport. Preserve existing four commands and Access transport.
- `identity-migrations/identity_baseline.py`, `identity_studies_catalog.py`: current0021
  dispatch/postcondition/reference pattern. New reference independently rehearsed by root;
  missing reference fails closed. Existing references never regenerated.
- `services/access/main.py`, `organization_check.py`, `studies_identity.py`: existing
  verified user/service FastAPI and bounded DB adapter seams. Add isolated language router;
  do not change existing check/enrollment behavior or use migrations at startup.
- `tests/qualify_studies_enrollment.py:clean_upgrade`: known empty current-head/Auth
  substrate recipe. Hardcoded old KDG inputs are unsuitable; root adapts narrowly to Leave.

## Tasks & Acceptance

**Execution:**
- [x] `services/access/tests/test_person_links.py`, `test_language_preferences.py` --
  observe relevant acceptance failures before implementing; cover contract edge cases.
- [x] `services/access/identity-migrations/versions/0022_person_links.py` and owner
  catalog support -- independent person, protected link/history, immutable references,
  server actor/UTC attribution and narrow projections; extend existing command guards.
- [x] `services/access/identity_operator_input.py`, `identity_operator.py`, `operator_cli.py`
  -- typed person.create/account.link_person execution and scoped original-outcome lookup.
- [x] Additive preference migration, `services/access/identity_preferences.py`, `main.py`
  -- authenticated restricted own-account GET/PUT, persistence, revision and retry contract;
  synchronize owning OpenAPI through its generator, not generated-file edits.
- [x] `services/access/tests/qualify_person_links.py` -- consume explicitly prepared
  synthetic fixture, real restricted logins, clean/previous/repeat/failure/race/transition
  proof and language HTTP/DB checks. No fixture discovery or infrastructure provisioning.
- [x] `services/access/IDENTITY-MIGRATIONS.md`, Leave evidence/tracker -- exact commands,
  requirement mapping, existing delivered credit, recovery and five impact decisions.

**Acceptance Criteria:**
- Given an authorized person.create command with stable nonzero person_id and expected
  absence, when accepted, then independent identity and atomic immutable evidence/outcome
  exist without any account or other-owner effects; identical mapping can be unchanged.
- Given account.link_person with explicit account/person/stable actor, verification
  evidence_ref and expected absence or link revision, when accepted, then live account,
  existing stable account actor and person are verified; one retained link per account
  and atomic evidence/outcome commit. Conflicting person/actor mapping is rejected.
- Given concurrent/retried/changed or unauthorized commands, when executing or recovering,
  then exact command/target/current authority and existing operation namespaces apply;
  no duplicate effects/events or partial accepted change after evidence failure.
- Given missing/inactive mapping or service failure, when resolving own person, then
  absence/setup-needed is distinguishable from unavailable and no person/grant is invented.
- Given existing membership/role/hooks and retained/recreated synthetic three-account
  cohorts, when proving transitions, then original attribution/history remains, replaced
  accounts cannot inherit identity/access, membership replay cannot affect later rejoin,
  and old Access/writer activation remains gated. People/Leave integration stays downstream.
- Given verified own-account context, when GET /v2/me/preferences/language runs, then
  known absence returns English and revision zero; unavailable is never absence.
- Given PUT with operation_id, expected_revision and exact registered preferred_locale,
  when accepted, then desired locale/revision/server attribution and compact outcome commit
  atomically. Changed retries, stale revisions, invalid locale and account/org overrides
  fail safely; same retry returns original outcome. No person/member/employment/grant is
  required solely for a preference. Desired Portuguese persists across org switches even
  while rendering falls back to English; no UI/translation delivery is implied.
- Given real restricted roles and migration/command failure, when verifying, then raw
  browser/runtime writes, other-account reads, owner DDL and private ledger access deny;
  rollback, activation block, explicit forward retry and previous consumer compatibility
  are evidenced separately from source tests. No production proof is inferred.

## Implementation Notes

Implementation agent owns service code/tests and runbook. Root owns private fixture,
actual native execution/reference publication, Leave tracking/evidence and final review.
Use existing frozen Python environment; no installs. Prefer minimal owner-local code over
new generic engines. Root will establish absent-feature native evidence; agent must
retain failing-first focused test output before source edits. Missing actor attribution
must have a deliberate safe owner solution; never assume a person or app grant to save
preferences. Registered locale choices are en/pt (English/Portuguese), preserving desired
locale independently of presentation fallback. Positive bigint revisions use existing
decimal-string wire convention; zero denotes known preference absence.

## Spec Change Log

## Review Triage Log

2026-10-26: all three externally supplied layers received before triage. Finding-floor arithmetic is metadata, not an additional finding. All17 findings are recorded individually; duplicate roots B4/E2 and B7/V2 share corrections. The fixes preserve existing contract intent and add no business capability.

| Finding | Verdict | Route | Evidence / correction |
| --- | --- | --- | --- |
| B1 | medium | patch | Head22/23 omit predecessor verify_roles; the inherited snapshot does not cover every Studies owner membership edge. Restore the original role guard and prove unexpected membership rejection. |
| B2 | medium | patch | Head22 compares reference bytes but omits revision21 source digest comparison. Restore source-pin verification. |
| B3 | medium | patch | Preferences only reference actor existence; neither table structurally binds account/actor pair. Fixed routines validate normal writes, but ADR0035 requires alternate write rejection. Add composite local account_actor foreign keys for server attribution. |
| B4 | medium | patch | Routes register success only; generated types omit existing stable error responses. Declare the existing wire error schemas/statuses and regenerate types without changing runtime surface. |
| B5 | medium | patch | Person/transition loaders compare claimed run/port but no running container/network identity or approved scratch prefix. Add actual guard and prefix before connections. |
| B6 | medium | patch | Language output open(x) follows mutations; journal absence can allow an occupied output path. Reject/reserve output before any auth or mutation. |
| B7 | medium | patch | Person projection assertion ignores selected person_id; exact linked/absent actor/person/inactive native results are unproved. Add exact projection assertions. |
| B8 | medium | patch | Raced create compares receipts but not exact operation/event counts or relationship. Assert native one-outcome/one-event linkage. |
| B9 | medium | patch | Only person-create is raced; competing person links need actual same-account contention with loser producing no evidence. Add fresh explicitly prepared unlinked account proof. |
| B10 | medium | patch | Revocation qualifier covers lookup only and runtime deny is not operator target scoping. Add wrong-target/revoked execute and lookup with unchanged identity/evidence counts. |
| E1 | medium | patch | _person_receipt checks non-null for creation but uses truthiness for UUID validation; empty string passes. Validate all non-null events. |
| E2 | medium | patch | Duplicate of B4, independently verified missing existing stable error schemas for generated consumers. |
| E3 | medium | patch | Language journal os.write return count is ignored; short writes can precede mutation without full operation reference. Complete the write before fsync or fail before the request. |
| V1 | medium | patch | Pre-verified gap: native successful writes all persist pt, so update omission survives tests. Prove pt to en persistence, GET and old-operation replay. |
| V2 | medium | patch | Pre-verified gap: own-person assertion ignores person and revision. Same correction as B7. |
| V3 | medium | patch | Pre-verified gap: new commands bypass successful CLI worker execution/recovery. Add actual isolated worker native proof for both commands with explicit protected disposable target descriptor. |
| V4 | medium | patch | Pre-verified gap: native409 checks omit identifiers. Assert exact changed-operation/stale-revision/race error envelopes. |


## Verification

Prepared Python: `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
Use `-I -B -m pytest`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, `-p no:cacheprovider` for
focused new tests and affected operator/CLI/catalog/API tests; root runs final affected
owner/release regressions. Both composer checks, owned with `--no-seeds`, must pass.
Native proof uses Leave-local run88a737dd-ad7b-429a-a83c-5d103716d659/port55582 with
private validated fixture; never read or connect through old KDG credentials. Record
complete commands, source/tool/log hashes and all failed attempts, with no secrets.

Root pre-edit acceptance: existing person.create parser rejects the valid planned command;
actual existing FastAPI language GET returns404 under the complete Access environment.
Initial attempted API RED used the migration-only environment and lacked httpx; retained
as an environment failure, not acceptance evidence. Exact logs: .local/leave-id-b-20261026/red.json.

## Historical review execution state

Implementation and native verification completed2026-10-26. One blind reviewer launched, then was stopped after the other launches failed;
context-free edge and verification launches failed with `agent thread limit reached`.
No review triage has been performed. The BMAD step04 unavailable-reviewer fallback
requires standalone packets and a halt. Use the three `review-e1-id-b-*.md` packets in
separate sessions, retain their findings, then resume step04 triage including a fresh blind
review. This is a runtime-capacity limitation, not a user approval or readiness decision.
Custom Leave tracker remains in progress; no commit, activation or next-story start.

2026-10-26 continuation: user supplied all three findings; runtime review blocker resolved. Correct confirmed defects, retain earlier frames and requalify changed source on fresh disposable cases.

## Review resolution — 2026-10-26

All17 findings fixed, no deferrals. B4/E2 and B7/V2 share fixes while retaining individual
triage rows. Final regression1996PASS in112.84s with selected source unchanged throughout;
generated typed-error/consumer checks and both composers PASS. Fresh native person10,
language8, transition5 and supplemental structural/role8 probes PASS, plus evidence-write
rollback/retry, controlled migration recovery and actual release failure gate. The exact
commands, source hashes, preserved original frames and additional failed attempts are
bound by `apps/leave/docs/testing/evidence/e1-identity-links-preferences-review-20261026.json`.
No live activation, commit or Access grant-integration claim. The earlier review-capacity
block is historical and resolved by user-supplied findings. Custom Leave tracker: review;
ACCESS-A remains next, with current authority and membership binding still required.
