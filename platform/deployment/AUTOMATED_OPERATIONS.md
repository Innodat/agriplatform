---
title: Unattended certificate renewal and temporary registry access
type: feature
created: 2026-09-28
status: done
route: dispatch
baseline_commit: 066e02638d9c8a52a8b0fc2cbc4def9d91f35982
review_loop_iteration: 1
context:
  - platform/docs/architecture/decisions/0020-safe-schema-changes-and-release-recovery.md
  - platform/docs/architecture/decisions/0023-structured-operational-logs-and-sensitive-data.md
---

<frozen-after-approval reason="user authorized autonomous reversible implementation; live changes separately gated">

## Intent

The owner requests automatic certificate renewal to avoid expiry outages, and
continuation of container-registry setup for first production release. Remove manual
DNS renewal and permanent registry credentials from the normal operating path.
Implement and test the tooling now; prepare concrete live installation/firewall
changes for approval before executing them. Do not publish the full application.

## Boundaries & Constraints

Always preserve API routes, image digests, service configuration and authorization.
Renew using Certbot standalone HTTP-01 on TCP80 with a timer and deployment hook;
public API traffic remains HTTPS443. Keep port80 optional/default-off in Terraform.
Use the existing per-environment deployment lock when installing TLS or changing
APISIX. Validate hostname, >24h validity, certificate/key match and trusted chain.
No migrations, imports or API restarts during TLS renewal. Before first activation,
install verified copies only. After activation update the gateway, verify the served
certificate and a real API route, retain recovery configuration and record outcome.
Never log private keys, tokens or generated APISIX content. Never write plaintext
credentials into git, argv or artifacts. No live firewall/account/deploy changes by
implementation worker. No dummy approval evidence or claims of hosted tests.
Registry authentication uses the workflow's temporary GITHUB_TOKEN over strict SSH
stdin, isolated root-only Docker config, bounded login and cleanup on failures.
Preserve existing Docker credentials; no permanent PAT or new user credential needed.

## I/O & Edge-Case Matrix

| Scenario | Expected |
| --- | --- |
| Valid renewed cert, no active release | Install private copies; do not start containers; record pending gateway activation |
| Valid cert, active release | Lock, prepare new protected gateway configuration, activate gateway only, verify live fingerprint/route, update current pointer and evidence |
| Invalid/wrong cert or busy release lock | Fail closed without replacing active configuration; retry support and bounded waits |
| Gateway activation/verification failure | Attempt recovery to prior gateway/config/certificate; report failure and recovery result without secrets |
| Repeated hook/reboot after successful install | Safe idempotent result; scheduled renewal and retry remain configured |
| Registry login or deployment failure | Nonzero result, temporary Docker config removed, original credentials unaffected |
| Missing/invalid registry inputs | No deployment; error contains no sensitive values |
| Default / enabled ACME firewall input | No port80 by default / only additional TCP80 rule; host and other rules unchanged |

</frozen-after-approval>

## Code Map

- `platform/deployment/host-release.py`: current.json contains sha/images/compose/evidence;
  release.lock uses flock. Pipeline pulls immutable images before ordered migrations.
- `platform/deployment/render_gateway.py`: JSON-subset apisix.yaml ends #END, contains
  TLS key; individual bind-mounted files require new configuration directory and
  gateway recreation. Compose service gateway has dependencies; use --no-deps.
- `platform/deployment/ci-deploy.sh`: strict SSH upload and host-release execution.
- `.github/workflows/production.yml`: registry push uses automatic GITHUB_TOKEN;
  deployment step currently has no registry authentication on host.
- `platform/deployment/terraform/main.tf` and tests: preserve existing resources and
  all firewall defaults; add opt-in ACME TCP80. Cloud-init must not change.
- `platform/deployment/README.md`: manual renewal and permanent host login guidance
  must describe new automation and remaining operational install steps instead.
- Installed cert lives in /etc/letsencrypt/live/api.scribeswell.com; copies in
  /etc/agriplatform/tls/production. Target config /etc/agriplatform/production.json.
  No live app containers or bootstrap approval yet. Existing live public SSH stays.

## Tasks & Acceptance

- [x] Add focused tests first, observe acceptance failure, implement TLS hook and
  operational timer/service/deploy-hook templates under platform/deployment/tls/.
  Provide bounded retries for hook failure even when Certbot already renewed lineage:
  successful issuance alone must not leave gateway on old cert indefinitely.
- [x] Implement temporary registry deployment wrapper; wire into CI and strict SSH
  transport with no token interpolation in remote command. Add scoped failures/tests.
- [x] Add optional ACME firewall input and mocked tests without applying Terraform.
- [x] Document installation/reconfigure dry-run/renewal retry, safe rollback and
  expiry checks. Health/expiry checks must report failure; do not claim outbound alert
  delivery without a configured destination. No recurring added paid service.
- [x] Record scaffold/shared UI/context/docs/ADR impact decisions and verification.

Given a renewed certificate, the serving gateway must adopt it automatically;
no Certbot-only success claim suffices. Given temporary CI credentials, all host
image pulls use them for that invocation only; all exit paths clean them up. Given
failure, retain actionable safe evidence and previous release compatibility. Local
unit and container/gateway tests must support these claims before live approval.

## Implementation Notes

Local-only delivery authorized by user's autonomous-work instructions. Both requested
operations are grouped as first-release reliability; no separate product feature or
new runtime application. No pending user design choice. Live configuration is a
separate approval after concrete guarded plan and local tests. Implementation agent
must not commit, push or perform remote operations.

## Verification

Run focused new Python tests, full platform deployment Python suite, affected gateway
smoke where useful, shell syntax and Terraform mocked validation. Record exact results
and limitations. No real registry pull claimed until hosted execution establishes it.

### Implementation evidence (local, pass 1; superseded by pass 2 below)

- TLS hook: `tls/renew.py`; systemd service/timer and Certbot deploy hook under
  `tls/`. Preserves current Compose/API service configuration and immutable image
  references; replaces gateway TLS material and bind paths only. No schema changes,
  startup migrations or previous application contract changes. Recovery recreates
  the prior gateway and verifies its served certificate/route; no database reversal.
- Registry: `registry-deploy.py`, `ci-deploy.sh`, production workflow. Temporary
  workflow token is transported through strict SSH stdin, never remote argv. Isolated
  root-only `/run` Docker configuration applies to every child image pull and is
  cleaned after success, login/deployment failure, and handled termination signals.
- ACME: `acme_http_enabled` defaults false; mocked tests confirm one additional
  TCP80 rule when enabled and unchanged cloud-init/host configuration.
- Scaffold impact: shared release tooling updated in place; no application generator
  exists to update. Shared UI: none, operational behavior only. Agent context: existing
  ADR-0020/0023 instructions cover this work; no additional agent policy required.
  Documentation: README installation/reconfiguration, retry, expiry and recovery
  guidance updated. ADR impact: implements accepted 0020/0023, no decision changed.

Requirement-to-test traceability and observed results:

- `python3 -m unittest discover -s platform/deployment/tests -p test_tls_renewal.py`:
  initially failed because the hook did not exist; now 5 pass (pending install,
  active config preservation, recovery, busy lock, real OpenSSL hostname/key/trust/
  expiry validation).
- `python3 -m unittest discover -s platform/deployment/tests -p test_registry_auth.py`:
  initially failed because wrapper did not exist; now 5 pass (login/deploy failure,
  success cleanup, existing credentials, invalid transport input).
- `python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`:
  89 passed.
- `terraform -chdir=platform/deployment/terraform test -filter=tests/acme.tftest.hcl`:
  enabled-rule test initially failed with missing variable/rule. Full
  `terraform -chdir=platform/deployment/terraform test`: 16 passed (mocked provider;
  local socket requires execution outside sandbox). `terraform ... validate`: passed.
- `node --test platform/deployment/tests/*.test.mjs`: 13 passed outside sandbox.
- `bash -n platform/deployment/ci-deploy.sh platform/deployment/tls/deploy-hook.sh`:
  passed. Python compilation of wrapper, hook and gateway smoke: passed.
- `python3 platform/deployment/tests/gateway_smoke.py`: enhanced to perform real
  gateway recreation, served fingerprint/route verification, idempotence, and assert
  API container IDs unchanged. Currently blocked by installed Compose 2.28.1; raw
  env files require >=2.30.0. No integration success claimed yet.

No live firewall/account/deployment operations, hosted registry pulls or ACME
issuance performed by the implementation worker. Live installation remains gated.

### Re-derived implementation evidence (pass 2)

All frontmatter context files were loaded before work. The five tracked delivery
files were restored to the stated baseline, then the reviewed KEEP constraints were
reapplied around a newly derived recovery model. The first focused TLS run failed
because the new hook was absent. A focused pending-intent host test also failed
before the release guard was added.

- TLS now extracts the first leaf through OpenSSL, compares the entire cert/key
  material, and emits stable nonsecret error codes. Protected fsynced intent and
  pair backups precede mutation; successful adoption or verified recovery clears
  intent. Restart reconciliation restores the previous gateway/copies/pointer before
  retrying; host-release blocks pulls, migrations and activation until reconciliation.
- Cooperative TERM/HUP/INT drains the bounded command and enters recovery. Primary
  budget is 180 seconds, reserved recovery is 120, systemd overall deadline is 600
  and graceful-stop margin is 240. No schema or application contract changes.
- Registry cancellation drains the detached, per-stage-bounded coordinator while
  retaining its lock and temporary Docker config; cleanup occurs only after it exits.
  Compose-version and final release-route subprocess waits now have explicit bounds.
- Existing scaffold/UI/context/docs/ADR impact decisions above remain applicable.

Exact final verification:

- `python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`: **96
  passed**, outside the sandbox because production-verifier tests bind loopback TLS.
  Includes 12 TLS cases (multi-PEM unpadded leaf, real trusted TLS/fingerprint/route
  failures, chain-only identity, exact recovery pointer/config, paired-copy rollback,
  actual SIGTERM, retained failed-recovery intent and later reconciliation), 4 registry
  cases (success/failure cleanup, invalid transport, actual process-group cancellation
  with lock/config retained until child drain), and 8 host cases including pending
  intent blocking all release effects.
- `DOCKER_CONFIG=/tmp/boabab-compose python3 platform/deployment/tests/gateway_smoke.py
  > /tmp/boabab-auto-gateway.log 2>&1`: **passed**. Uses actual APISIX, production
  verifier, actual gid636/mode0640 files via a disposable root chown helper,
  multi-PEM adoption, same-leaf chain rotation, idempotence, failed candidate producing
  real HTTP404 and verified previous gateway recovery; current pointer/copies and API
  container IDs retained. No production verifier replacement or widened secret modes.
- `terraform -chdir=platform/deployment/terraform test`: **16 passed**, mocked provider;
  no apply. The first-pass optional-port failure and validation results remain valid.
- `bash -n platform/deployment/ci-deploy.sh platform/deployment/tls/deploy-hook.sh`:
  **passed**. Python compilation of hook, wrapper, host-release, render_gateway and
  gateway smoke: **passed**.

No hosted registry pull, live ACME issuance, remote account/firewall/deployment action,
commit or push was performed by the implementation worker. Live installation remains
separately gated. Hard SIGKILL/host loss cannot run in-process cleanup; protected TLS
intent enables reconciliation, and registry credentials are isolated under volatile
root-only `/run`. Safe coordinator drain is verified for handled cancellation signals.

## Review Triage Log

## Spec Change Log


### Review pass 1

| Finding | Verdict and evidence | Route |
| --- | --- | --- |
| Blind1 leaf/fullchain parsing | High: PEM_cert_to_DER_cert receives all PEM blocks; runtime assumes single leaf. Real unpadded leaf must be covered. | bad_spec |
| Blind2 TLS termination/budget | High: no handler or pre-mutation evidence, possible activation+recovery exceeds systemd600s. | bad_spec |
| Blind3 registry cancellation | High: subprocess.run unwinding kills coordinator; Docker migration container lifetime is independent of SSH process. | bad_spec |
| Blind4 paired copies | Medium: second atomic write can fail after first; preactivation has no restoration. | bad_spec |
| Blind5 changed chain/same leaf | Medium: fingerprint equality skips gateway update despite fullchain change. | bad_spec |
| Blind6 safe diagnostics | Medium: validation errors share phase only, hampering unattended failure diagnosis. | patch, included in re-derivation |
| Blind7 gateway acceptance | High: smoke not yet executed and substitutes production verification/permissions. | bad_spec |
| Edge1 fullchain | High: same verified root cause as Blind1. | bad_spec |
| Edge2 termination | High: same verified root cause as Blind2. | bad_spec |
| Edge3 cancellation | High: same verified root cause as Blind3. | bad_spec |
| Verification1 production verifier | High: mocks mean deleting real fingerprint/route checks would not fail tests. | bad_spec |
| Verification2 recovery observation | High: call-count assertion passes even with wrong recovery config. | bad_spec |

### Re-derivation guidance (pass 1)

The plan omitted necessary interruption and chain cases. Add real multi-PEM leaf
fingerprint extraction (OpenSSL first leaf), full TLS material comparison so chain
changes adopt even with identical leaf, and stable nonsecret failure identifiers.
Persist operation intent before gateway mutation. Handle TERM/HUP cooperatively,
reserve explicit bounded time for recovery within the service deadline, and test
interruption. Paired installed copies need recovery if either write fails; include
interruption evidence and safe retry rather than falsely claiming an atomic pair.
Registry-wrapper cancellation must not kill a coordinator while its Docker migration
continues after the lock disappears: drain an already-running bounded coordinator
or implement coordinated safe shutdown; keep credentials until its last pull and
then clean. Test actual process cancellation semantics (no production DB needed).
Test production TLS verification with local TLS endpoint (valid/mismatch/route failure),
and real gateway failed-candidate recovery, current pointer and API identity retention.
Isolated modern Compose is available at /tmp/boabab-compose (DOCKER_CONFIG).
KEEP existing narrow opt-in firewall, token-only-stdin transport, private credential
isolation, no-deps gateway activation, target lock, pending-first-activation behavior,
trust validation and previous-config preservation. Restore tracked delivery files to
baseline, preserve this spec and review evidence, then re-derive coherently from here.


### Review pass 2 triage

| Finding | Verdict/evidence | Disposition |
| --- | --- | --- |
| Blind1 expired previous certificate | Medium: recovery deliberately fails closed when prior TLS cannot be verified; valid lineage is not automatically adopted through unresolved intent. Operator recovery must cover this case. | Patch complete operator reconciliation; retain fail-closed policy, no unconditional automatic recovery claim |
| Blind2 evidence-write failure | High: save before restoration can throw and suppress recovery. | Patch best-effort diagnostics around mandatory restoration |
| Blind3 timed-out Docker client | Maybe-false: daemon work may outlive client, but persistent competing daemon mutation and resulting bad state need fault-injection evidence; both production gateway candidates preserve routes/images. | Document uncertain daemon state/manual reconciliation; no guaranteed recovery claim for daemon failure |
| Blind4 redundant backups | Medium: matching material still creates backup/mutation transaction every15m. | Patch no-op copy check, remove completed backups, bound unreferenced routine evidence |
| Blind5 unresolved application release | High: host-release may mutate services then fail before pointer update; existing failure path demonstrates stale pointer. | Patch durable activation marker and TLS refusal |
| Blind6 user-scoped Compose | Medium: isolated config hides user plugin; actual boabab uses system-wide plugin but developer setups can differ. | Patch explicit prerequisite/check and docs/test; do not inherit credentials/plugins |
| Blind7 unbounded renderer commands | Medium: coordinator drain can hang in renderer subprocess lacking deadline. | Patch finite subprocess deadlines |
| Blind8 recovery error codes | Medium: suppression loses diagnostic category. | Patch safe selected recovery_code fields |
| Blind9 incomplete manual recovery | Medium: compose-only restoration does not reconcile pair/pointer/intent. | Patch full locked procedure, including expired old certificate path |
| Edge1 diagnostic failure | High: same root cause as Blind2. | Same patch |
| Edge2 expired previous | Medium: same root cause as Blind1. | Same operator reconciliation patch |
| Verification1 credential framing | High: reversing shell frame or main reads escaped existing tests. | Patch complete transport/entry-point subprocess test |

No new product choices or public API are needed for these patches. Live approval
remains separate from tested local implementation. Spec's explicit recovery and
failure-reporting requirements remain authoritative; outage/daemon failures must not
be advertised as guaranteed automatic healing. The potential Docker-daemon race is
unverified; retain evidence and require reconciliation if daemon state is uncertain.


### Final verification and operational handoff (2026-09-29)

Review pass 2 patches completed: diagnostic failures cannot skip restoration; no-op
checks avoid redundant private-key backups; routine evidence is bounded; application
activation intent blocks unsafe TLS adoption; renderer subprocess deadlines and safe
recovery codes are preserved; isolated Compose prerequisite and full shell-to-wrapper
credential framing are tested. Complete locked recovery is documented, including an
expired previous certificate. Docker daemon timeout fault injection remains deferred
with uncertainty retained for operator reconciliation; no guaranteed recovery claim.

- `python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`: 105 passed.
- `node --test platform/deployment/tests/*.test.mjs`: 13 passed.
- `terraform -chdir=platform/deployment/terraform test`: 16 passed.
- `DOCKER_CONFIG=/tmp/boabab-compose python3 platform/deployment/tests/gateway_smoke.py`: passed; real trusted TLS verifier, chain-only rotation, failed-candidate recovery, unchanged APIs and existing security checks.
- Shell syntax and `git diff --check`: passed.

User requested automatic renewal; explicit execution approvals covered TCP80-only
firewall addition and installation of four reviewed operational files. Saved plan
applied without server replacement or additional paid service. Certbot reconfigure
staging validation FAILED because both authoritative ns1.dyna-ns.net and
ns2.dyna-ns.net return SERVFAIL for api.scribeswell.com. Google and Cloudflare
resolvers confirm failure; Google checking-disabled also fails and parent has no DS,
so this is not established as a DNSSEC validation problem. Existing live certificate
remains valid through 2026-12-27; automatic issuance must not be claimed until DNS
recovers and reconfigure plus renewal/deploy-hook dry-run passes. No apps activated,
production data imported, or frontend published. Hosted GHCR pull remains unverified
until the separately approved first application release.

The installed adoption/expiry service was started successfully (ExecMainStatus=0,
`pending_gateway_activation`); its 15-minute timer is enabled and active. Existing
Certbot timer is also enabled/active, but lineage remains manual because reconfigure
correctly refused to persist settings after the failed challenge. This is partial
operational setup, not verified unattended issuance.
