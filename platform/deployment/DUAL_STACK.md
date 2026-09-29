---
title: Enable scoped dual-stack networking for production services
type: bugfix
created: 2026-09-29
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 3ac7ec0b7a7217fea66d4139fba1a0f5bd546784
context: []
---

<frozen-after-approval reason="Owner authorizes autonomous reversible release preparation">

## Intent

Generated Compose must give registered services outbound IPv4 and IPv6 so the
restricted direct Supabase database URLs work from containers. The current implicit
IPv4-only network fails on boabab while Auth HTTPS succeeds. A disposable dual-stack
network on the same host passed the same read-only database check in 0.31 seconds.
Preserve private service isolation, the sole gateway443 publication, existing
routes/CORS/env handling and coordinated release gates. Do not restart Docker,
change global daemon/firewall settings, use host networking for application runtime,
change database endpoints/credentials or activate the release as part of this fix.

</frozen-after-approval>

## Implementation Notes

Small reversible change: declare enable_ipv6 on the generated project default
network in render_gateway.py; IPv4 remains enabled by default. Add an acceptance
assertion against rendered Compose, then run deployment contracts and real gateway
smoke. Document host IPv6 egress prerequisite and existing-network replacement
requirement (no live stack exists on boabab). No new public API, UI, scaffold or
agent-context changes; accepted ADRs remain unchanged. Deployment tooling owns
this generic network requirement. Official Docker docs confirm automatic ULA
allocation when no IPv6 pool is configured; no fixed global subnet is needed.
https://docs.docker.com/engine/daemon/ipv6/


## Code Map

- platform/deployment/render_gateway.py:render writes implicit project default
  network. Declare its IPv6 support, retain normal IPv4 and isolated bridges.
- platform/deployment/host-release.py:deploy runs migrators explicitly on bridge
  before Compose activation. Use a unique owned disposable dual-stack bridge for
  each migration job and bounded cleanup; no host networking or global changes.
- platform/deployment/tests/test_gateway.py: renderer contracts; gateway_smoke.py
  actually starts rendered Compose and verifies routing/isolation/TLS.
- platform/deployment/tests/test_host.py: coordinator lifecycle mocks including
  migration failure, timeout, safe evidence and blocked activation.
- platform/deployment/README.md: explain Linux host IPv6 egress prerequisite and
  ordinary deployment behaviour. Existing IPv4-only networks need a planned
  replacement; do not silently recreate a network carrying a running release.

## Tasks & Acceptance

- [x] Add failing renderer and migration-network contracts before implementation.
- [x] Render a project-scoped dual-stack network; keep only gateway443 published.
- [x] Give migration jobs an owned temporary dual-stack network; create before job,
  remove after exit and bounded stop on timeout. Creation/cleanup failures block
  activation and preserve safe evidence. Never remove pre-existing networks.
- [x] Document network requirements/recovery and record scaffold/UI/context/ADR
  impact (none beyond generic deployment tooling/docs, accepted ADRs unchanged).
- [x] Run deployment Python suite and actual local gateway smoke; retain external
  read-only evidence showing default bridge DB failure vs dual-stack success.

Given rendered services, when deployed on a host with IPv6 egress, then the project
network permits both protocols and existing gateway routes/isolation are preserved.
Given a migration job, when it runs, then its network supports the same DB address
family before API activation. Given creation, migration, timeout or cleanup failure,
when release exits, then activation stays blocked and safe outcome evidence remains.
Given an owned successful job, when complete, then its temporary network is removed.

## Verification

Observe focused failing tests first, then run affected tests and full deployment
Python suite. Run real local gateway smoke outside sandbox if required; do not
claim real external connectivity from a mock. Root has separately observed real
boabab default bridge database failure and disposable dual-stack connection success
in0.31s. Both had Auth HTTPS connectivity; both test containers/network cleaned.
No production config/deployment mutation is authorized inside implementation.

## Spec Change Log

Investigation before code changes found migrators also hardcode IPv4-only bridge.
Expanded non-frozen code map/tasks and changed route to dispatch for their bounded
network lifecycle. This is the same release connectivity requirement, no product
choice. Owner authorization covers reversible implementation; public release remains
separate. Implementation agent must not commit/push or run remote operations.

Root release check also found an existing CI discovery gap: production.yml invokes
unittest but test_target_contract.py used pytest free functions. The exact unittest
discovery command ran0 tests before a mechanical conversion to TestCase/subTest;
it now runs2 methods containing the same10 cases successfully, without a pytest
runtime dependency. No target validation semantics changed.

## Review Triage Log

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| Blind 1: existing IPv4-only network preflight | low | Existing networks require explicit planned replacement, documented without automatic deletion; Compose errors block activation and preserve prior state. No live stack exists on boabab. Reject additional inspection branches for this uncommon operator migration; existing release recovery gate remains. |
| Blind 2: Docker automatic IPv6 allocation prerequisite | medium | README currently names only Compose minimum; older Engines can fail network creation. Patch the documented Engine prerequisite; network creation already fails closed before migrations, so a second enforced version gate is unnecessary. |
| Blind 3: smoke does not prove outbound database traffic | false | Smoke claims address allocation/routing/isolation only. Separate actual boabab readonly test used the same image and restricted database URL: default bridge failed, disposable dual-stack succeeded in0.31s; both reached Auth. Its safe report and script are retained privately. No production credentials belong in general CI smoke. |
| Blind 4: next release not gated after uncertain migrator stop | medium | Pre-existing timeout lifecycle allowed subsequent attempts without a durable migration-pending marker; new networks preserve this existing operator reconciliation contract. Defer general migration reconciliation gate, including interruption recovery, to release coordinator hardening. |
| Blind 5: cleanup timeout and absent evidence untested | medium | Current lifecycle fixture covers cleanup RuntimeError and malformed evidence, but not cleanup timeout or absent evidence. Patch fixture and persisted outcome assertions. |
| Edge 1: evidence write failure skips cleanup | medium | save() precedes network removal in finally, so an IO error prevents owned network cleanup. Patch with nested try/finally ensuring cleanup and timeout stop still run despite evidence write failures, add characterization of both failures. |
| Verification 1: timeout warning/stop result assertions missing | medium | Fixture exercises both stop outcomes but does not assert evidence values. Patch assertions as recommended. |

## Final Verification

- Initial renderer/migration contracts failed before implementation; evidence-save
  failure regressions also failed before their corrections.
- `python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`:
  110 tests passed after final patches (`/tmp/dual-stack-final-tests.log`).
- `DOCKER_CONFIG=/tmp/boabab-compose python3 platform/deployment/tests/gateway_smoke.py`:
  passed using existing Compose2.39.4; real dual-stack allocations, private ports,
  routing, CORS and TLS/recovery verified; fixture containers/network removed.
  Renderer/smoke unchanged by final host cleanup patches.
- `git diff --check`: passed.
- Three review layers completed; recovery fixes and assertions applied. Persistent
  retry gating for pre-existing uncertain migration outcomes deferred separately.
- No production activation, global Docker modification or push.
