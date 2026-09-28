---
title: 'Boabab WireGuard administrator and CI access'
type: 'chore'
created: '2026-09-28'
status: 'done'
route: 'dispatch'
baseline_commit: '48e4b3c442f94fa53825fdb9387127d726ea21ba'
---

<frozen-after-approval>

## Intent

The user explicitly selected WireGuard instead of Tailscale. Keep production on the
existing Hetzner server, rename it `boabab` in place, and support changing administrator
and GitHub-runner IPs through private SSH. Give each device/person and CI distinct
VPN credentials; preserve SSH authentication/host verification and individual accounts.
Provide repeatable onboarding/removal tooling and CI connectivity. The Mac Mini and
its Tailscale network remain separate. Existing approved database bootstrap remains
pending; public app activation, imports and account invitations are outside this item.

## Boundaries & Constraints

Always preserve existing server ID, disks, public IPs, Terraform addresses, cloud-init,
release ordering, migration lock/recovery and strict host verification. Route only the
server private /32 over WireGuard; no internet exit node, forwarding or new server.
Use a single public UDP51820 endpoint on the existing host. Keep restricted public SSH
until operator and CI private paths are verified. Require an explicit assertion for
public SSH removal. Secrets never enter tracked files, logs, Terraform or artifacts.
Human devices generate their own private keys; server tooling consumes public keys.
CI uses separate secrets, serialized deployments, temporary runner config and cleanup.
Never silently grant new humans sudo, use a shared human VPN key, or change Mac Mini.

## I/O & Edge-Case Matrix

| State | Expected behavior |
| --- | --- |
| Existing Terraform defaults | Preserve historical name and restricted SSH |
| server_name=boabab, WireGuard enabled | In-place name; TCP443 and UDP51820; restricted TCP22 retained |
| Public SSH disabled without verified private access | Reject plan |
| Missing/malformed CI VPN inputs or host mismatch | Fail before remote mutations; no secret values in errors |
| CI setup/deployment fails | Clean up only owned VPN interface/config with always-run cleanup |
| Add existing identical peer | Safe no-op; preserve server key and other peers |
| Conflicting/invalid peer identity, address or public key | Reject without changing config |
| Remove one registered peer | Revoke only that peer; persist across restart |

</frozen-after-approval>

## Code Map

- `terraform/main.tf`, `terraform/tests/*.tftest.hcl`: existing server-name override,
  public-SSH gate and registered-key tests. cloud-init MUST remain unchanged.
- `.github/workflows/production.yml`: main-only release with concurrency lock, tests,
  builds, owner migrations and publication. Add VPN setup immediately before remote
  deployment and always-run teardown; never expose secrets to untrusted PR runs.
- `check-ci-inputs.py`, `ci-deploy.sh`: target/secrets preflight and strict OpenSSH.
  Existing host-release requires root-capable deployment; do not invent a limited
  account that cannot execute it. Document CI authority honestly.
- `wireguard/` (new): validated runner setup/teardown and server peer-management CLI;
  shell out with argv, bounded waits, safe errors. Keep private key output suppressed.
- `tests/`: unittest contract and behavioral tests; use command fakes/temp files for
  network/root actions. Integration against actual host is root operator's next step.
- README and this delivery record: operator steps and configuration. PRODUCTION_STATUS
  and RELEASE_PREPARATION contain preexisting session edits; preserve them.

## Tasks & Acceptance

- [x] Terraform: enable optional UDP51820 ingress, retain default behavior and name,
  expand tests for rename-only, exact rules, safe SSH removal and unchanged user_data.
- [x] Add CI WireGuard input validation/setup/teardown plus workflow integration;
  use a dedicated server private IPv4 /32 and private client IPv4 /32, distinct;
  endpoint public IPv4:51820, strict key validation and least routing. No shell eval.
- [x] Add server peer onboarding/removal CLI for an existing protected WireGuard
  config: lock, validate registry, atomic updates, preserve secrets, safe replay,
  sync running interface and recover from errors. Unit tests simulate commands.
- [x] Document server setup, key generation, single-device/CI profiles, SSH per-user
  provisioning/removal, separate VPN vs Unix privilege, and console rollback.
- [x] Run relevant tests, review and record results. Track hosted CI activation separately.

Given valid CI inputs, setup connects only the configured private deployment host,
then the existing migration/deployment flow runs, and teardown always removes runner
secrets. Given a new team member, the guide creates a separate unprivileged SSH account
with their public key and a separate WireGuard peer; removal revokes both access layers.

## Implementation Notes

User renegotiated frozen intent from Tailscale to WireGuard on 2026-09-28. Earlier
Tailscale install/rename was never applied. Prior mocked tests passed 9 cases; blind
review requested rename-only and exact-firewall assertions and actionable console
recovery; implement those here. Repository edits are reversible, the user authorized
network setup/name change and requested implementation, so no repeated spec approval.
Shared deployment scaffold improves in place; no shared UI or agent-context changes.
No accepted ADR is modified; migration/release security contracts remain applicable.
Implementation subagent must edit repository artifacts only, not provider state or
ignored operational files, and must not commit/push. Root handles approved remote ops.

## Verification

Run smallest failing acceptance first, then Python deployment unittest suite and mocked
Terraform tests. Record exact commands/results. Local/provider network smoke remains
separate evidence, never infer it from mocks.

### Repository implementation evidence (2026-09-28)

- Added `wireguard/common.py`, `runner.py`, `peers.py`, operator guide and
  `tests/test_wireguard.py`. Runner validates canonical private /32s, public
  IPv4:51820, keys and deployment-host binding; creates one owned interface at
  MTU1280 and one server /32 route; verifies strict SSH before remote writes and
  erases secret files even when interface deletion fails. Peer identities live
  inside the root-protected server config, so registry/config update atomically.
- Server Interface Address is a private /24 for connected return routing; clients
  and per-peer AllowedIPs remain /32. Registry rejects out-of-subnet, network,
  broadcast, duplicate, unregistered or conflicting peers. Bounded flock and
  syncconf preserve other peers/server key; failed writes/sync trigger explicit
  restoration/recovery diagnostics. Firewall guidance denies VPN forwarding and
  non-SSH input without breaking Docker forwarding.
- Production CI adds five dedicated WireGuard secrets, preflight, setup directly
  before existing deployment and always-run teardown. Deployment SSH now uses
  private temporary files and an explicit trusted-host file. Main-only guard,
  concurrency, migration ordering/locks and publication gates are preserved.
- Terraform adds optional `wireguard_enabled=false` and IPv4 UDP51820 only.
  Cloud-init, resource addresses and public-net settings are unchanged. Existing
  restricted public SSH and historical-name defaults remain. No provider state,
  ignored operational file, database, activation, commit or push was changed by
  the implementation worker.
- Impact decisions: shared deployment tooling improves in place; future scaffold
  should reuse it, but builder generation is still absent. Shared UI and agent
  context: no change. Documentation: main deployment README and operator guide.
  ADRs: no accepted ADR changed; no schema change, existing release/migration
  coordination and sensitive-log contracts retained.

| Acceptance | Evidence |
| --- | --- |
| Exact ingress/defaults/rename/SSH removal gate | `terraform test`: 13 mocked cases |
| Invalid inputs and least routing | `Inputs`, `RunnerBehavior` tests |
| Strict SSH failure/cleanup and ownership | `RunnerBehavior` tests |
| Replay/conflicts/removal/persistent rollback | `PeerRegistry`, `PeerPersistence` tests |
| No command-output secret leaks | `SafeCommands` test |
| Main-only serialized release and always cleanup | Existing production tests and `WorkflowContract` |

Commands and results:

- First acceptance: `python3 -m unittest discover -s platform/deployment/tests -p test_wireguard.py`
  failed as expected with missing `common` module before implementation; final run
  passed **19 tests**.
- `python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`:
  **53 passed**.
- `terraform -chdir=platform/deployment/terraform test`: sandbox provider startup
  failed; approved retry outside sandbox passed **13 mocked tests**. No provider
  resources were provisioned by this command.
- `terraform -chdir=platform/deployment/terraform fmt -check`: passed.
- `node --test platform/deployment/tests/release.test.mjs`: passed, **1 suite/file**.
- `python3 platform/deployment/release.py check`: manifest contracts valid.
- `bash -n platform/deployment/ci-deploy.sh` and `git diff --check`: passed.

Root workflow review and actual host/operator/CI connectivity evidence remain
separate. Public SSH removal must wait for both private paths and the explicit
operator assertion. Mocked tests do not establish production readiness.

## Review triage and final verification (2026-09-28)

| Finding | Disposition and evidence |
| --- | --- |
| Blind 1 / edge 1: both public SSH and WireGuard could be disabled | Fixed: Terraform requires enabled WireGuard as well as verified private access before public SSH removal; rejection test passes. |
| Blind 2: no connectivity-only hosted check | Fixed: manual main-only production-environment workflow, shared deployment concurrency, strict SSH `true`, always cleanup. Hosted execution remains pending GitHub configuration and controlled publication. |
| Blind 3: incomplete persistent firewall instructions | Fixed: exact dedicated nft helper/service/drop-in and restart dependency recovery documented. Live dedicated table preserves Docker rules. |
| Blind 4: human SSH forwarding privileges | Fixed: per-human no-forwarding key options documented while preserving interactive terminal access. Existing administrator authority is unchanged. CI key uses source restriction plus `restrict`. |
| Blind 5: client outside server subnet | Fixed: usable same-/24 validation and regression coverage. |
| Blind 6: failed interface deletion leaves tunnel live | Fixed: ownership-checked link-down/route-removal fallback; secret files removed, retry evidence retained, incomplete cleanup reported. |
| Blind 7: SSH transport can hang | Fixed: bounded keepalives and explicit lost-session migration reconciliation guidance. |
| Blind 8: mock-only network evidence | Operator live evidence added: handshake, strict SSH, 4 MiB each direction with matching SHA256, and service restart/reconnection. GitHub-hosted tunnel and end-to-end revoked-client connectivity still pending; no claim of those tests. |
| Blind 9 / verification 1: protection guards bypassed in tests | Fixed: actual mode/symlink guards exercised, owner metadata mocked only for UID cases. |
| Blind 10: rotation guide missing | Fixed: coordinated VPN/SSH/CI secret rotation using an independent working administrator path. |
| Verification 2: rollback payload not asserted | Fixed: test checks original restored syncconf content. |
| Live check: MTU1280 stalled SSH after banners | Fixed: default IPv4-only profiles use MTU1200; regression failed first, then passed. No cryptographic downgrade. |

Final commands: `python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`
passed **61 tests**; `terraform -chdir=platform/deployment/terraform test` passed
**14 mocked tests**; `node --test platform/deployment/tests/release.test.mjs`,
`python3 platform/deployment/release.py check`, shell syntax and `git diff --check`
passed. The WireGuard-specific suite now has **27 tests**.

Authorized live changes: existing Hetzner server renamed in place to boabab,
UDP51820 opened, restricted public TCP22 retained, dedicated WireGuard service and
SSH-only/no-forwarding table installed. Private client route is only 10.77.80.1/32.
Operator `ssh boabab` preserves the independently verified original host key.
The user applied the local persistent MTU update. Separate CI public keys are
registered; nine CI inputs are prepared in an ignored mode0600 file, not uploaded.
No Mac Mini/Tailscale change, server replacement, DNS change, Git push or public
application activation occurred. Hosted CI verification must precede public SSH removal.


## Hosted connectivity follow-up (2026-09-28)

Nine inputs are now uploaded to the main-only Production environment. Only the
connectivity workflow and helpers were published, with Netlify native builds paused.
Initial run 36477990203 passed strict SSH but correctly refused cleanup because
Ubuntu did not install the ownership alias supplied to link-add. A real isolated
Ubuntu namespace reproduced the missing alias; the regression fixture was corrected
and failed before implementation. Setup now explicitly sets ownership before keys
or link activation. Existing unowned-interface refusal and failure cleanup remain.

All 78 deployment Python tests passed; real namespace teardown verified interface
and secret removal plus repeat cleanup. Hosted run
[36480376365](https://github.com/Innodat/agriplatform/actions/runs/36480376365) passed
setup and cleanup at `4cffad16ddf4dcb1bd658a0093c67431072dad7e`.
This is a correction to the existing shared release helper: no scaffold, shared UI,
agent-context or ADR change; deployment status/evidence updated in this item.
Public SSH removal and application activation have not occurred.
