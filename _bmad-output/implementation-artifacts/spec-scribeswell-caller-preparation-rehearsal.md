---
title: 'Rehearse isolated Scribeswell caller mapping preparation'
type: 'chore'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
baseline_commit: '301930746f59b9e171dab485afc20aba890d4aa5'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The agreed caller handoff specifies an atomic disabled four-row preparation, but existing native fixtures install enabled rows using administrator autocommit. They do not rehearse that preparation protocol or local COMMIT reconciliation.

**Approach:** Add a test-only rehearsal using a new disposable PostgreSQL17 cluster, real restricted migrator/operator connections and existing immutable migrations/profile validation. Prove disabled initial mappings, exact no-op reuse, rejection of partial/conflicting states, rollback, serialization and bounded waits, plus distinct committed/unchanged/unknown/conflicting observations after deliberately lost acknowledgements. Retain session/run observations with a distinct synthetic preparation actor; make no live Identity/session-authentication claim. No production runner, external evidence verifier, owner implementation, migration edits, activation, importer transition or publication. Preserve standalone signup, UX and concurrent owner work.

</frozen-after-approval>

## Implementation Notes

- BMAD step02 investigation: no human intent gaps, no irreversible external effects; small test-only slice. Dedicated task-owned disposable cluster only; never existing Supabase/other containers. Existing dirty tree preservation already authorized.
- Code map: `tests/test_corpus_publication.py:controller_database` supplies migrated empty controller; avoid enabled fixture. `migrations/baseline.py:_checked_authority_ledger` verifies actual migrator/ledger and acquires existing migration lock. `tests/test_prepared_controller_profile.py:direct/native/state` provides replay and preservation observations. `generate_reference.py:prepared_fixture` guards isolated local PG17/absent roles. Do not change migration/Identity/profile implementations.
- Planned files: `tests/caller_preparation_rehearsal.py` test-only staging/state helpers; `tests/test_caller_preparation_rehearsal.py` native protocol evidence; app caller-preparation docs and this delivery record. Canonical evidence derived through bmad-spec after verification.
- Acceptance: Given empty migrated state, when actual migrator writes under migration then principal/authority locks in one RC transaction, then all four disabled revision1 rows commit with explicit synthetic preparer attribution, unchanged corpus/fence/history and successful prepared native replay. Given exact existing rows, repeated preparation writes nothing. Given partial/conflicting state or insert failure, no partial effect commits. Given two preparers/blocked lock, observe actual backend blocking and bounded failure or serialized exact reuse. Given lost local acknowledgement, establish session ended then compare full protected states, keeping committed, unchanged-before, conflict and unverified-active cases distinct; no automatic retry or invented outcome lookup.
- Impacts: no scaffold/shared-UI/agent-context/ADR changes: synthetic native qualification is app-specific, no reusable production pattern proven. Documentation records precise qualification limits. No runtime behavior is introduced, so observed acceptance failure concerns the new rehearsal protocol, not an implemented production preparation runner.
- Initial actual acceptance run reached NotImplementedError before implementing the test-only protocol (1failed; separate FK teardown error corrected by including the referenced outcome table in disposable cleanup). The first sandboxed attempt could not connect; it is environment failure, not an acceptance red. Corrected initial case passed1/3.68s. Native expansion passed22/6.87s.
- Added actual DBAPI AUTOCOMMIT with logical SQLAlchemy begin test: observed1failed4.39s (NoActiveSqlTransaction instead of deliberate early refusal); added DBAPI autocommit guard before any SQL. This fixes only the new test helper; no production implementation changed. Added actual SET ROLE impersonation denial and actual transaction lock/server timestamp assertions. Statement1500ms/lock500ms/idle3000ms fixture bounds are not a total/COMMIT supervisor deadline claim.
- First affected run: exact command `SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32769/postgres /tmp/scribeswell-host-tests-312/bin/python -m pytest apps/scribeswell/tests/test_caller_preparation_rehearsal.py apps/scribeswell/tests/test_prepared_controller_profile.py apps/scribeswell/tests/test_controller_history_profile.py -q` yielded223passed/1failed168.02s. Unchanged full-history capacity case reached PostgreSQL statement_timeout while validating20000 commands, confirmed from owned fixture server log. No expected result or production deadline changed. Isolated rehearsal plus that exact capacity case subsequently passed26/53.24s. An accidentally concurrent second rehearsal invocation refused all25 at the existing absent-roles guard before mutation; final runs are sequential. `python3 tools/py/run_compose_supabase.py --check-only` passes with no writes.

## Review Triage Log

- R1 medium/patch: client close does not guarantee backend removal; verified reachability in real async shutdown. Replace immediate absence assumption with bounded polling, retain unknown/no writes if termination unverified.
- R2 medium/patch: native replay checks excluded complete mapping rows; capture/compare protected full mapping snapshots including revisions/timestamps/attribution before and after replay.
- R3 medium/patch: revision conflict alone did not qualify partial/mixed reconciliation; add ended-session missing-authority and extra-authority states, both conflict without repair.
- R4 medium/patch: only authority table timeout was tested; parameterize held migration advisory, principal and authority locks, require bounded55P03 and unchanged mappings.
- R5 medium/patch: lost-ack attempt lacked its own actor/session/run record; retain actual PID/session/current login/database, synthetic distinct preparer, run/preparation reference and before/intended state together for reconciliation.
- R6 medium/patch: operator denial covered begin/execute only; test begin/recover/seal via execute and lookup under disabled current authority. No live session-attribution or Identity verification claim. All six findings addressed, none deferred.

- Final same affected command after review corrections: **228passed/no skips127.55s**, comprising29new and199retained cases; earlier capacity timeout and successful isolated26case rerun remain above. No production code, accepted ADR, Identity contract or applied revision changed. All six findings resolved, none deferred. AST, scoped local links/heading fragments/whitespace/test-name traceability, canonical11CAP/38ST/20companions and composition check-only pass. Original dirty AGENTS/README and all captured Scribeswell migration/Identity sources unchanged; concurrent owner changes excluded.
