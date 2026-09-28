---
title: Single-environment production delivery
created: 2026-09-27
type: chore
status: done
route: oneshot
baseline_commit: 9b21c961fd3d171ad4c67f5e673abaf23f37b585
---

<frozen-after-approval>
## Intent

The user chose to omit staging for the first platform release and use one CPX12
(1 shared vCPU, 2 GB RAM) production host. Replace the active staging/promotion
workflows with main-to-production delivery, keeping full build, test, immutable
image, target-binding, migration-before-activation, health and recovery safeguards.
Manual dispatch may release only main's exact event SHA. No persistent Supabase
branch or staging host is required. Prepare locally only; actual resource creation,
production schema/import changes, DNS and first public activation still need a
concrete reviewed plan and the user's approval. Future staging remains possible.
</frozen-after-approval>

## Implementation Notes

No unresolved implementation intent; original user requested automatic main release
when no staging environment is used. Local workflow/config/documentation edits are
reversible, with no deployment triggered or remote push. Reuse the already-tested
staging sequence as the production sequence, remove the staging trigger, and retain
optional staged-release helpers without invoking them. Update proposed ADR0043
(never accepted), current runbook and release inventory; retain original delivery
spec as historical evidence. Scaffold: same manifest contract. Shared UI and agent
context: unchanged. Size remains an unmeasured starting estimate; require actual
host memory/load checks before activation. CI builds images away from the host.


2026-09-28 completion: production.yml now includes all previous staging checks and
main-only manual dispatch, uses exact event SHA, and publishes production after
ordered host migration/health gates. Removed active staging.yml; optional staging
helpers remain inactive. Added prepublication Netlify site/domain binding and
postpublication exact identity plus public API/CORS verification. Default and
example Terraform use production/CPX12. Proposed ADR0043, index, runbook and PtS
inventory updated; historical SPEC retained with current-scope pointer.

Validation: observed three initial acceptance failures before workflow/config
changes and missing-recorder failure before implementation. Added provider rejection
fixtures, public probe checks and no-success-marker failure coverage. Parent found
the transferred workflow only installed Scribeswell's browser revision while PtS
locks another; observed regression failure, then explicitly installed both revisions.
`python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`: 34 passed.
`node --test platform/deployment/tests/release.test.mjs`: passed.
`terraform -chdir=platform/deployment/terraform fmt -check` and `validate`: passed.
Parsed production workflow YAML with PyYAML and checked main push/manual triggers,
one production job and environment. `git diff --check`: passed. Application code,
images and runtime topology are unchanged, so prior full browser/container evidence
remains applicable; no new full-stack performance claim is made. Live CI/provider
calls, cloud creation, database writes and public activation remain unperformed.

## Review Triage Log

Blind review and a targeted follow-up completed. All actionable findings fixed:

| Finding | Verdict and evidence | Correction |
| --- | --- | --- |
| Required environment reviewers prevent automatic main release | medium; whole job waits on environment approval | Runbook now uses protected-main review, initial enablement approval and no required per-release reviewer for automatic delivery |
| CI loses artifacts on partial failure | high; upload used default success predicate | Always upload available digests, provider result and frontend; success marker remains contingent on verification |
| Workflow rerun rebuilds instead of exact retry | medium; ci-build uses --pull | Explicitly document rerun as a new candidate; preserve artifacts and provide frontend-only retry plus original-manifest host coordinator commands |
| Netlify target checked after mutation | high; presence-only input validation | Preflight checks provider site/domain against intended production origin before host/publish effects; recorder rechecks |
| Success misses external API path | high; prior host probe uses loopback resolve | CI probes public HTTPS directory URL/status/exact-origin CORS before success |
| Generic verification failure lacks useful category | medium; all failures previously same string | Safe error codes for target, identity, API/CORS, HTTP authorization, network and malformed data; no payload/token logging |
| Recovery loses Netlify headers | medium; artifact lacked netlify.toml | Include exact netlify.toml beside preserved output for recovery publish |
| Manual recovery races automatic releases | high; manual Netlify bypasses CI concurrency | Require deployment hold, drain active/queued/waiting runs without cancelling active migration, verify/reconcile then restore auto delivery |

No findings deferred. No production resources created, no remote push, no credentials
stored in source. Next operational step is securely configuring provider access and
SSH inputs to produce a concrete single-host Terraform plan for approval.
