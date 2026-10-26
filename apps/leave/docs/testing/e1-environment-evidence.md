# E1-ENV execution evidence

2026-10-26. **Status: in progress; no runtime foundation acceptance claimed.**
Authoritative criteria remain E1-ENV in the approved epics and the existing environment
contract. Planning approval and existing shared-owner evidence are not Leave delivery.

## Implemented candidate

The existing thin native Supabase CLI route now supports a closed Leave disposable
target, separate ports/namespace and a bounded environment-only setup/smoke fixture.
The fixture provisions synthetic local Auth accounts and a dedicated two-organization
SQL schema with distinct setup/runtime logins. Its smoke command checks real password
sign-in, organization row isolation, wrong-password denial, runtime DDL denial and
owner-role escalation denial. These runtime checks have not yet executed successfully.

The implementation agent observed Leave-target acceptance fail with `schema_mismatch`
before implementation, then pass. Focused native/foundation verification after the
subnet correction passed 27 tests in 71.984 seconds. Parent verification is retained
under `.local/leave-env-20261026`; an earlier parent run overlapped the subnet edits
and failed with mixed-source schema/subnet expectations. Its result is preserved;
Stable-source parent verification subsequently passed all 65 tests in 14.688 seconds:
`PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_native_cli test_leave_foundation test_dev test_docker_gate`.
Receipt: `.local/leave-env-20261026/tests-110131629975.json`; stdout/stderr are retained
alongside it. Leave sprint validation and scoped `git diff --check` also passed.

## Actual startup findings

Fresh Leave preparation succeeded for run `fecc1ff1-716a-47f8-b732-bb155bc10f3b`.
Startup did not reach Supabase service creation. Initial sandbox Docker access was
denied; permitted tracing subsequently isolated failure at Docker network creation.
The daemon reported `all predefined address pools have been fully subnetted`.
There was no observed port conflict. Existing networks were neither removed nor pruned.

Docker/host route inspection showed no 10.x subnet. A candidate explicit Leave test
subnet `10.254.26.0/24` was added with creation and IPAM-inspection tests. The original
prepared run is retained and no longer matches the changed target; it must not be
silently adopted. A fixed test subnet supports one retained network at a time; this
is not unlimited fresh-run/parallel-CI qualification.

The user questioned creating a separate development stack. Recommendation: share
the existing KDG development stack for integration with common Identity/Access,
and reserve disposable instances for destructive/reset/migration-failure acceptance.
Further separate Leave startup is held while reconciling this topology. Read-only
inspection confirmed the documented KDG run `99b7231c-0a5b-4bdb-98e8-3329564c526a`
still matches its protected native target/config marker on database port 55482.
No KDG startup, fixture write, reset, schema change or account mutation was performed.

## Remaining acceptance

- Reconcile shared development versus disposable acceptance target ownership and
  commands before changing either retained environment.
- Demonstrate actual synthetic Auth and restricted SQL smoke, setup failure blocking,
  repeatability and normal data-retaining stop against the chosen disposable fixture.
- Finish supported tool/dependency and affected npm workspace adoption evidence;
  preserve independent app deployment and Python owner locks.
- Generated-reference/Leave consumers, Entra callback and browser/device qualification
  remain their separate consuming-story gates.

`python3 tools/py/run_compose_supabase.py --check-only` passed; it applied no SQL.
Leave sprint tracking marks Epic 1/E1-ENV in progress, with no delivery completion.

## Impact decisions

Scaffold: extend the existing native environment owner; no competing orchestrator.
Shared UI: none. Agent context: existing safety/ownership rules suffice; no rule edits.
Documentation: this evidence, execution record and tracker. ADR: existing accepted
decisions unchanged; topology reconciliation belongs in the mutable environment contract.
No commits, production/provider operations, real grants or customer data changes.
