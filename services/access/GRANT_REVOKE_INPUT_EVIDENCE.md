# Strict organization grant revocation input —2026-10-22

This bounded ACCESS-A increment prepares the missing grant.revoke pure input contract
before its protected writer. It grants no authority, checks no live account/member and
performs no database or external I/O. Access13 grant.assign remains delivered; revoke
execution, receipt lookup, effective readers and coordinated consumers remain gated.
No native startup, resource operation, production/real-account change or dependency
update occurred. Existing TypeScript7.0.2 baseline and owner assignments remain intact.

## Contract and example

Organization scope and payload keys are exact: grant_id, account_id, membership_id,
permission, expected_revision. Grant ID is retained opaque text: empty, Unicode,
whitespace and UUID-looking text are preserved, never normalized or cast. The shared
UTF-8/forbidden-text decoder and65536-byte body limit still apply. Account/org require
nonnil canonical-shape UUID strings (existing spelling preserved); member/revision are
positive decimal strings through signed bigint maximum. Permission retains the existing
literal ASCII1–200 policy. There is no expected_absent, app_id or actor override.

```json
{
  "schema_version": 1,
  "operation_id": "a1234567-1234-4234-8234-123456789abc",
  "command": "grant.revoke",
  "scope": {"kind": "organization", "org_id": "b2345678-2345-4345-8345-23456789abcd"},
  "payload": {
    "grant_id": "retained:opaque grant",
    "account_id": "c3456789-3456-4345-8345-3456789abcde",
    "membership_id": "7",
    "permission": "kdg_capture.read.own",
    "expected_revision": "2"
  },
  "reason_code": "synthetic_fixture",
  "evidence_ref": "setup:fixture/1"
}
```

The future writer must target that original exact binding/revision, never look up a
replacement membership. This parser does not establish that the binding exists or is
eligible. A changed/new action needs a fresh operation ID; identical retry keeps its
original stable input. No executable revoke CLI recipe is offered before the writer.

## Requirement-to-test evidence

All cases are in services/access/tests/test_grant_revoke_input.py:

| Requirement | Verification |
| --- | --- |
| Exact opaque ID/account/member/permission/revision, frozen redaction | test_exact_binding_is_preserved_frozen_and_redacted |
| No coercion, nil UUID/invalid bigint/non-ASCII denial | test_typed_identifiers_and_expected_revision_never_coerce |
| Closed keys, missing fields, duplicates/escaped aliases, no expected_absent | test_closed_fields_missing_duplicate_and_escaped_aliases |
| Strict decoder/envelope/provenance/forbidden text/body limit | test_decoder_envelope_provenance_and_forbidden_grant_text and raw UTF-8 multibyte exact65536/65537-byte payload test |
| No runtime capability or I/O from valid parsed input | test_valid_revocation_refuses_every_execution_boundary_before_io |

Acceptance RED preceded production edits: valid binding rejected as
access_operator_input_invalid; focused run exit1 with1 expected failure in0.06s.
The production edit adds only the existing Access parser's typed records/union/branch;
existing adapter final type guard, CLI/worker allowlists and Identity parser stay closed.
Focused tests now pass. Exact commands/results and review completion follow below.

## Delivery impacts

Scaffold: extend existing Access owner pure-input seam; no generator/service/framework.
Shared UI: none. Agent context: existing instructions suffice, unchanged. Documentation:
this evidence, bounded spec and mutable substrate/KDG handoffs. ADR: existing ownership,
release safety, logging/attribution and exact-binding decisions apply; none edited.
Deployment: no lifecycle/config/schema/privilege change. Prior native proof remains its
historical source-bound record; this pure-input increment claims no new native proof.

## Verification commands

```sh
PYTHON=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PYTHON" -I -B -m pytest services/access/tests/test_grant_revoke_input.py -q -p no:cacheprovider
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PYTHON" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider
"$PYTHON" -B tools/py/run_compose_supabase.py --check-only
"$PYTHON" -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only
```

Preservation snapshot /tmp/grant-revoke-input-preservation.json records full baseline
be6b9bf0fd6e1744ad7c20e48ea870dd8d3a3a47,202 protected existing Access files, mutable parser
and concurrent starting bytes. Final audit must preserve them and the frozen intent;
only this increment's exact paths may enter the local commit. No push/reset/prune.


Focused126 PASS0.37s; affected regression1645 PASS44.46s; both composition checks
exit0. The documented JSON example parses through the actual owner parser. Logs are
/tmp/grant-revoke-input-{red,focused,regression,compose-default,compose-owned}.log.
These are pre-review results; corrected-source verification follows below.


## Review corrections and durable custody

The configured oneshot blind review returned5 findings. The spec records an individual
verdict/evidence for all5 before grouping. Four direct test/evidence corrections were
accepted: raw UTF-8/multibyte byte boundaries, distinct sensitive grant-ID refusal output,
empty/Unicode/long-ID refusal parameters and durable custody digests. The proposed new
shared test helper was rejected: existing adjacent suites use these assertions, pytest
restores monkeypatch state, and incompatible signatures fail loudly; no silent failure
or concrete invariant break was demonstrated. No deferral or new generic infrastructure.
Production parser bytes did not change after review. Focused130 PASS0.41s.

Completed preservation: all202 baseline Access files other than the one intentionally
modified parser match the baseline commit and starting bytes. The inventory is durable
and reconstructible: list tracked services/access files at the full baseline commit,
exclude services/access/access_operator_input.py, map each path to SHA256 of its blob,
serialize with json.dumps(sort_keys=True,separators=(',',':')).encode(), then SHA256.
The same inventory was verified against current worktree bytes. Frozen intent and
parser digests below bind this delivery without relying on /tmp persistence.

```json
{
  "baseline_commit": "be6b9bf0fd6e1744ad7c20e48ea870dd8d3a3a47",
  "protected_access_file_count": 202,
  "protected_inventory_sha256": "6fca99fd9229393463f6beced8bf9e3573819df87221871e5ae3d5f50f18d9e9",
  "parser_before_sha256": "e2fbbe9e691b337ee9a5538b3fb9fdb0c927b39a521678a95ea546da3c38ab31",
  "parser_after_sha256": "532a709b8a34bbb36c5b462bd9c30bc54727e3a2448c4d0f7ccc44c8f689b288",
  "frozen_intent_sha256": "1b91b7761b63474fd4c3233c4643cac3edca13d39752a344b50b1949e866b30b"
}
```

Temporary full logs are supporting diagnostics; repository-recorded commands, outcomes,
source/inventory digests and log digests below retain the verification receipt after
workspace cleanup. The completed local commit retains the actual source/tests and example.


Final affected regression1649 PASS39.12s. Both composition modes exited0 against the
same final production parser bytes; review changed only tests/documentation. Documented
example parses. No native startup or Docker/resource operation was performed.

Verification log SHA256 receipts:

```json
{
  "grant-revoke-input-compose-default.log": "717595e678ccf63899c5205c751ac89f675a1bb9c150c02c28dd7a693452dcf7",
  "grant-revoke-input-compose-owned.log": "b474dc31d67f2d4e6745b6f9bb3602aa6a62c732910d0d252cc6d1a51bce5dc7",
  "grant-revoke-input-focused-final.log": "bad06f35238296c2857f853176791fbccf3d579f02ced66e62861fa5ecbd78a4",
  "grant-revoke-input-focused.log": "6f93c70d9564ffa0e59814a74a6daefa5c3e9240262bde35c59b86c19dcbce28",
  "grant-revoke-input-red.log": "a0726543dbceed90cabc3a30bc13678c869efd6da4969393713714f0eccf4b38",
  "grant-revoke-input-regression-final.log": "6ff67c82c777733810a23f367f3bdba05e618e6b7b41c19e457688c07a31edb7",
  "grant-revoke-input-regression.log": "188f59b8b1046e783f33f62286800982452099326feba083f10e3c0395630ec9"
}
```

Final frozen-intent and preservation audit passed. All14 originally modified tracked
concurrent files retain their starting bytes; originally observed untracked documents
and any independently added files remain excluded from this delivery. Only six explicit
owned paths are committed; the202-file protected Access inventory above is unchanged.
The final scoped commit is recorded separately after creation; no push.
