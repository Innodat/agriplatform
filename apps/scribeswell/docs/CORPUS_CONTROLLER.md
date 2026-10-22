# Dormant transactional corpus controller

Owned revision `scribeswell_0003` implements begin, recover and seal, protected
executor/source-command mappings, attributed attempt history and durable original
outcomes. It extends the [writer fence](CORPUS_WRITER_FENCE.md) and consumes the
[strict input qualifier](CORPUS_PUBLICATION_INPUT.md). The
[canonical owner contract](../../../_bmad-output/specs/spec-scribeswell-studies/corpus-publication.md#dormant-executable-controller-contract)
owns exact records, envelopes and transition rules.

The shipped migration creates no caller, actor, principal, authority, attempt or
outcome and keeps enforcement false. Functions and tables remain owner-only.
Existing corpus data/grants, importer and public API retain their behavior. Tests
alone prepare the absent restricted `scribeswell_corpus_operator` role and synthetic
actor custody, grant exact function access and enable the fence. These are disposable
qualification changes, not production provisioning or verified Identity evidence.

## Python and SQL entry points

With `apps/scribeswell/backend` on the import path, `corpus_publication` exposes:

```python
from corpus_publication import execute_command, lookup_outcome

# connection is an already prepared, idle, caller-owned psycopg connection.
# raw is the strict command envelope; source_raw is the complete raw artifact.
receipt = execute_command(connection, raw, source_raw)
original = lookup_outcome(connection, raw)
assert original == receipt
```

The adapter reads no credentials/environment, creates no connection and exposes no
CLI/HTTP or actor preparation. It always qualifies the complete source bytes before
opening the write transaction. Lookup parses the original envelope without requiring
source bytes, then checks current exact command/source authority. Supplying a manually
constructed PreparedCommand cannot bypass qualification.

Use an idle writable connection compatible with READ COMMITTED. One transaction uses
bound JSONB parameters, statement timeout `5s`, lock timeout `2s` and idle transaction timeout `5s`.
Receipt validation occurs inside the transaction and a result returns only after
successful transaction exit. The frozen `CommandReceipt` contains version `1`, operation,
command, source, actual executor actor, attempt, decimal-string generation and state
updating/closed. Lookup returns the same receipt or None; a function return inside an
uncommitted caller transaction is not completion proof.

Native `scribeswell.execute_corpus_command(jsonb)` and
`scribeswell.lookup_corpus_command_outcome(jsonb)` independently validate the closed
semantic fields and bound the JSONB text representation to 65536 bytes. Original
byte-level duplicate/encoding checks belong to the strict parser.
They require writable READ COMMITTED, the actual restricted operator session login
and current protected principal plus exact source/command authority. Role flags and
memberships are checked; GUCs, supplied actor IDs and SET ROLE do not select an executor.
Direct routine grants do not grant table reads/DML, owner assumption or more commands.

## Transactions, retries and custody

Principal and authority shares serialize revocation, followed by the operation retry
lock. Existing same-operation input returns its original stored outcome after current
authority checks; changed semantic fields or a rebound executor conflict. Outcomes
compare the validated JSONB envelope, without a fingerprint protocol. Replaying an old
begin/seal/recovery never changes current state. Immutable outcomes retain the original
executor and principal/authority revisions.

A new transition requires enabled fencing. Control-before-epoch locking and a single
corpus serialization lock prevent competing initial attempts. Begin creates generation `1`
only when no epoch exists. Recover requires the exact predecessor source/attempt/
generation, retires it and allocates a fresh attempt at the next generation; overflow
and cross-source/stale requests fail. Seal requires the exact updating tuple and input
identity and closes it after active writer locks release. Bound stale writers fail
thereafter. No transaction spans source parsing, Identity/network waits or full audit.
Epoch, attempt history and outcome commit together or roll back together.

Preparation must externally verify a stable classified service actor through Identity
ownership before deliberately mapping the actual operator login. The local UUID/key/
evidence reference is custody, not verification. No new Identity projection, table read,
Auth account or Access grant exists here. Human initiator attribution is absent unless
a later trusted integration supplies its separately verified contract; current payloads
accept no override. Protected local tables enforce key, scope, identity, lifecycle and
attribution invariants; ordinary roles cannot mutate them directly.

## Failures and release gates

`PublicationError` exposes only stable `corpus_publication.access_denied`,
`input_invalid`, `conflict`, `unavailable` or `unknown_outcome`; no raw driver text or
submitted payload escapes through exception chaining. Existing parser/source failures
retain their safe identifiers. Native fixed SQLSTATEs distinguish denial `42501`,
invalid `22023`, conflict `P0001` and unavailable `55000`. Never branch on localized prose.

On a lost/uncertain COMMIT response, retain the same operation and original input and
perform current-authorized lookup. Missing receipt stays unresolved; do not infer
rollback, create a fresh blind operation or reopen prior state. SQL wait bounds do not
bound client transport or COMMIT. The app-local
[supervised invocation API](CORPUS_OPERATOR.md) now bounds source qualification,
connection, transport and COMMIT in an isolated child and qualifies
explicit same-operation reconciliation. This connection adapter still exposes no
general command runner.

[Migration verification](MIGRATIONS.md) preserves independently pinned `0001`/`0002`
references and adds a separately generated `0003` reference. Default and host replay remain deliberately dormant-only. The explicit native
[prepared-controller profile](PREPARED_CONTROLLER_PROFILE.md) additionally checks a
prepared operator while enforcement stays false and history empty, matching local
custody without claiming Identity verification. It changes no grants or state.
Enabling enforcement or recording history remains outside either replay profile;
this is not active-state release qualification. Real actor/caller preparation,
least-privilege operational release profile, target adoption and writer/importer
transition remain gates. The [outer supervisor](CORPUS_OPERATOR.md) is fixture-qualified;
its existence does not prepare a live caller or qualify an active release. Closed
writes are not a sealed full audit,
ready manifest, reader proof or private Studies implementation. Access remains with
its separate owner session. No production action or image build is implied.

## Verification and impacts

Use the Python 3.12 setup and fresh disposable PostgreSQL 17 fixture described in
[MIGRATIONS.md](MIGRATIONS.md#reproduce-local-qualification). Run suites sequentially:

```sh
python -m pytest apps/scribeswell/tests/test_corpus_publication.py -q
python -m pytest apps/scribeswell/tests/test_owned_migrations.py -q
python -m pytest apps/scribeswell/tests -q
```

The [delivery record](../../../_bmad-output/implementation-artifacts/spec-scribeswell-dormant-corpus-controller.md)
records actual red/green commands, requirement-to-test mapping, independent reviews,
reference reproduction and final regression. Skipped database cases do not qualify
this controller. Scaffold/shared UI/agent-context need no changes or promotion;
existing owner migration/release tooling is reused. App documentation changes and
canonical handoff accompany the delivery; accepted ADRs remain unchanged.
