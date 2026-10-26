# Supervised publication implementation evidence

Implementation slice2026-10-26; parent owns review, checkpoint and status. No native
SQL, owner calls, migrations, grants, network fault proof or readiness claim.

The contract in CORPUS_CALLER_PREPARATION.md was written before implementation.
Application ATDD command:
`/tmp/scribeswell-implementation-python/bin/python -m pytest -q apps/scribeswell/tests/test_corpus_operator_publish.py`
first failed1test0.10s with missing `corpus_operator.lookup_publication`; implementation
then passed1test0.09s. Expanded focused verification passed28tests1.89s; adding explicit execute/lookup child dispatch coverage then passed29tests1.98s. No other
observed test failures occurred in this slice.

Final affected verification used the exact executable above, `-m pytest -q`, both
`apps/scribeswell/tests/test_corpus_operator_publish.py` and
`apps/scribeswell/tests/test_corpus_publish.py`, then these explicit nodes from
`apps/scribeswell/tests/test_corpus_operator.py` (prefix each with that path and `::`):

```
test_invalid_target_never_spawns
test_explicit_target_shapes_and_suppressed_frozen_repr
test_invalid_input_never_spawns
test_bad_child_response_never_success
test_forged_receipt_validated_against_original
test_stalled_child_bounded_killed_and_reaped
test_ambient_credentials_scrubbed_and_stdin_only
test_child_revalidates_target_and_source_before_connect
test_full_source_qualification_is_inside_deadline
test_source_failure_is_safe_and_target_never_connected
test_fixed_budget_and_no_public_override
test_invalid_pooler_single_host_binding_never_spawns
test_validated_scheme_is_usable_libpq_conninfo
test_worker_connect_disables_ambient_authentication_sources
test_unverified_reap_warns_safely_with_bounded_cleanup
test_exhausted_admission_budget_never_spawns
test_private_protocol_rejects_invalid_requests_before_connect
```

Result:128passed4.97s, then final129passed4.91s after adding explicit child execute dispatch coverage; no skips. The launching Python removed all environment keys
starting PG or SUPABASE, or containing DATABASE or NATIVE. Native test modules were
not selected. The new native test was checked only with `ast.parse`; valid, never
imported, collected or executed. It deliberately discards stdout after the actual
publisher returns, then requires independent committed-outcome visibility, original
lookup/retry, historical no-reactivation and current-authority denial. This is an
authored final-integration gate; deliberate stdout discard is not network-loss proof.

Traceability: new original lookup/receipt and identity tests cover retained
operation/seal/source reconciliation. New child validation, actual source failure,
restricted connection and environment tests cover child-only qualification and
explicit authority. New actual child overflow/late/qualification timeout tests plus
existing controller cleanup/backpressure/reaping tests cover shared containment.
Existing explicit version1 protocol/grammar tests establish compatibility.

Snapshots: SHA-256 HEAD/after pairs are retained in
[implementation-source-snapshots.json](testing/evidence/supervised-publication/implementation-source-snapshots.json). HEAD is a repository source
comparison, not a claimed pre-edit working-tree observation. Publisher, source parser,
source evidence, closed auditor and existing operator/publisher tests match HEAD
exactly. Only supervisor, caller contract, new application tests and authored native
case changed for this slice. The wider working tree contains unrelated existing work.

Impact decisions: scaffold none (app-only controlled pattern); shared UI none;
agent context none; documentation caller contract plus this evidence; ADR none
(no accepted decision changed). No platform promotion, canonical spec/memory edit,
staging or commit. Native transport/receipt/permission qualification, maximum real
manifest timing and final combined integration remain open.


## Review correction evidence

Publication-only safe failures now also retain `corpus_mismatch` and
`deadline_exceeded`; controller version1 allowlist/grammar is unchanged. The new
worker/parent assertions first failed all4cases0.31s with `unknown_outcome`:
[raw red output](testing/evidence/supervised-publication/review-error-red.txt).
Successful synthetic publication and lookup receipts now traverse the actual
isolated worker dispatch, serialization, pipe transport and parent validation.
Admission covers wrong/oversized source, oversized command and a valid nonseal
without spawning; valid JSON with mismatched original checksum rejects exactly
`input_invalid` before connection. Repeated source qualification is unchanged.

Only the edited publication test file ran during this correction:44passed3.71s.
[Raw final output](testing/evidence/supervised-publication/review-focused-final.txt)
records the complete argv and environment filter. Reproduce from repository root:

```
python3 apps/scribeswell/docs/testing/evidence/supervised-publication/run-focused.py
```

The [runnable recipe](testing/evidence/supervised-publication/run-focused.py)
contains the full environment-filter implementation. Explicit node arguments can
reproduce the review red selection against its pre-fix source; current source passes.
[Review source hashes](testing/evidence/supervised-publication/review-source-snapshots.json)
are exact SHA-256 values after correction, with the observed Git HEAD. Preserved
implementation HEAD/after hashes were copied from the earlier temporary record;
they do not establish a pre-edit working-tree snapshot. Original implementation red
and129-test final raw logs were not retained, so their earlier summaries remain
historical reported results, not newly manufactured raw evidence. No broad rerun,
native collection, SQL, owner operation or canonical delivery artifact edit occurred.


Parent independently ran the complete affected selection after review corrections:
144passed5.32s, runner5.95s. Elevenselected runtime/test/contract source hashes match
before/after. Exact full argv/result, raw application output and source pairs are
retained in evidence/supervised-publication/parent-{results,before,after}.json and
parent-application.log. Eight individual review/parent findings were triaged; known
safe failures and missing application/evidence coverage corrected. Repeated source
qualification has no demonstrated deadline defect yet and remains a final native
real-source/capacity timing gate. Native test was not collected/run in this slice.
