# Strict organization grant assignment input — 2026-10-21

This bounded ACCESS-A prerequisite prepares `grant.assign` as immutable redacted input
through the existing Access parser. It performs no lookup, membership validation or
write. Exact organization scope and account/member binding are required; no app_id or
grant_id is supplied for assignment. Permission association and current membership
remain later protected execution checks. Grant revocation and account grants are separate.

## Acceptance and verification

Characterization148 passed before implementation. New valid-create acceptance failed
as access_operator_input_invalid before production edits. Existing adapter fallback and
CLI/worker allowlists still refuse assignment before any target/connection/dispatch.
The first focused run48 passed/2 failed due to a test expecting the wrong worker error;
inspection established existing bare ValueError refusal, and only that expectation was
corrected. Original logs remain under
`platform/deployment/.local/access-grant-assign-input-20261021/`.

Canonical Python P is
`platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python`.
From repository root, commands use PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 P -I -B -m pytest
with -p no:cacheprovider (the exact shell bindings and final commands are below):

- Characterization: test_access_operator_input.py, test_application_enable_input.py,
  test_organization_application_input.py (148 passed).
- Acceptance RED: test_grant_assign_input.py::test_exact_frozen_redacted_variants -x -q
  (one expected failure before implementation).
- Focused: new grant suite plus the three characterization suites.
- Affected regression: services/access/tests apps/pts/tests/test_release.py
  platform/deployment/tests/test_migrate_adapter.py -q.
- Both composition dry runs: P -B tools/py/run_compose_supabase.py --check-only;
  P -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only.

Pre-review focused198 passed4.08s; affected regression1398 passed93.41s. Both composition
modes exited0. Independent review resolution is recorded below.

## Requirement to test evidence

All methods below are in tests/test_grant_assign_input.py:

| Requirement | Test |
| --- | --- |
| Both variants, exact supplied fields and strings, immutable/redacted records | test_exact_frozen_redacted_variants |
| Exclusive absence/revision by presence, no coercion | test_expected_state_is_exclusive_by_presence; test_invalid_values_and_scope_never_coerce |
| Nonnil exact organization/account UUID and positive bigint member/revision | test_invalid_values_and_scope_never_coerce; max/above-JS-safe success matrix |
| Literal ASCII permission1–200, controls/DEL preserved; NUL/Unicode refused | exact variant matrix; invalid values; shared strict decoder |
| No fallback scope or caller actor/app/grant fields; closed shapes/duplicates | test_invalid_values_and_scope_never_coerce; test_closed_fields_and_duplicate_aliases |
| Closed version1 envelope, provenance, strict decoder,65536-byte bound | test_shared_strict_decoder_envelope_and_provenance |
| Unsupported execution/recovery before I/O; Identity refuses | test_execution_and_lookup_refuse_before_all_effects, direct/CLI/both worker routes with traps |
| Existing commands/consumers unchanged | focused characterization and affected regression |

## Five impacts and preserved scope

Scaffold: existing owner input seam gains typed assignment variants; no generator,
parallel parser framework or service. Shared UI: none. Agent context: no rule change.
Documentation: this evidence, mutable substrate command examples and KDG handoffs.
ADR: existing scope/release/attribution/logging decisions suffice; no ADR edited.
Shared client/generator owners and dependency baseline (including TS7.0.2) stay unchanged.

No DB/Docker startup, migrations, roles/secrets, runtime configuration, real grants,
provider/account changes, activation, deployment, production/pilot, Leave/editor, reset/
prune or push occurred. Historical native proofs stay tied to their sources. Existing
private-bootstrap portability remains a follow-up, with no new deferral implied here.
Root preservation snapshot /tmp/grant-assign-input-preservation.json binds baseline,
concurrent14 tracked/43 untracked files,50 protected historical/reference sources and
the mutable Access parser baseline. The inherited history group contains51 entries;
only access_operator_input.py is an explicitly owned mutable source in this delivery.
Its original hash remains in the untouched preservation snapshot.


Exact final commands (P as above; F=platform/deployment/.local/access-grant-assign-input-20261021):

```sh
cd /home/ck/repos/innodat/agriplatform
P=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
F=platform/deployment/.local/access-grant-assign-input-20261021
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $P -I -B -m pytest services/access/tests/test_grant_assign_input.py services/access/tests/test_access_operator_input.py services/access/tests/test_application_enable_input.py services/access/tests/test_organization_application_input.py -q -p no:cacheprovider > "$F/focused-reviewed-final.log" 2>&1
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $P -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider > "$F/regression-reviewed.log" 2>&1
$P -B tools/py/run_compose_supabase.py --check-only > "$F/compose-default.log" 2>&1
$P -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only > "$F/compose-owned.log" 2>&1
```

Both documented create/update contract examples parse successfully. Verified source hashes
are retained in verified-source.json. Final preservation/commit custody is recorded in
root-final-evidence.json; it excludes submitted values/secrets. No old runtime proof is
relabeled as qualification of this parser source.


## Independent review

The oneshot route uses one context-free blind reviewer; edge/verification lenses are
not part of this small route. Six findings were checked and patched: clarify a fresh
operation ID for a later update, supply otherwise-valid Access lookup arguments, exercise
the four-element Identity worker, prove leading/trailing/whitespace-only permissions,
complete final results, and provide executable working-directory/interpreter bindings.
No finding changes approved intent or introduces a deferred issue. Parser production
bytes did not change during review; only tests and documentation were strengthened.


Review-patch focused verification:234 passed0.58s. The first reviewed run232 passed/
2 failed because the test embedded a submitted literal on the raising caller source
line; traceback source rendering included that literal. Moving arguments to a local
variable isolates exception-data redaction without weakening assertions or changing
production code. focused-reviewed.log retains that failure. Final reviewed regression:1434 passed36.85s, no skips. Both composition modes
passed on unchanged production sources. All109 current source bindings and both
contract examples pass final audit; all50 protected sources,14 concurrent tracked
and43 pre-existing untracked files remain byte-identical. Frozen intent is unchanged.
The local commit contains only this delivery’s seven files; no push.
