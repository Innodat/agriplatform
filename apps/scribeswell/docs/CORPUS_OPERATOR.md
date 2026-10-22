# Supervised corpus invocation

`backend/corpus_operator.py` wraps the dormant [transactional controller](CORPUS_CONTROLLER.md)
with a fixed 60-second operation budget measured from admission. It is an app-local
Python API, with no CLI, HTTP/runtime wiring, credential discovery or provisioning.

With `apps/scribeswell/backend` on the import path:

```python
from corpus_operator import OperatorTarget, execute_command, lookup_outcome

target = OperatorTarget('supabase', explicit_operator_database_url,
                        'https://explicit-project.supabase.co')
receipt = execute_command(target, original_command_bytes, complete_source_bytes)
original_receipt = lookup_outcome(target, original_command_bytes)
```

The frozen target suppresses its repr. Its three explicit fields are `kind`,
`database_url` and `binding`. `supabase` binds the HTTPS project URL to the exact
operator database URL using the platform pure target contract; require TLS and
exact `scribeswell_corpus_operator` project/role identity. `local_disposable`
binds a declared exact database name to literal `127.0.0.1` or `::1` and the exact
operator username. `localhost`, arbitrary hosts, options, unknown kinds and
mismatched identities fail before spawning. Supabase hosts must be single valid
DNS names; literal or encoded multi-host delimiters are rejected. URL settings
remain subject to the existing app URL validator; connect timeout is explicitly
bounded to five seconds.
Accepted scheme spellings normalize to the lowercase `postgresql` libpq scheme.
There is no timeout override.

A local declaration does not establish disposable custody. Only use independently
owned disposable fixtures for qualification; neither the target nor a UUID verifies
Identity attribution, preparation evidence, current authority or readiness. Real
caller/actor preparation remains a separate controlled gate. No actor, role, grant,
DDL, migration profile, importer or enforcement configuration is changed by this API.

## Isolation, receipts and uncertainty

The parent parses the original closed bounded command and validates the target.
Full source qualification runs in an isolated Python child, before connecting, and
the existing transactional adapter requalifies it before SQL. This places source
work, connection, transport, SQL and COMMIT inside supervision. The child independently
revalidates target and command. Credential-bearing target and source bytes travel
only over private stdin; argv contains only fixed bootstrap code and the app path.
The child receives only a fixed locale environment: ambient PG, Python, Scribeswell
and other credential settings are absent. Python `-I` excludes user site, current
directory and Python environment imports. Stderr is discarded. At the connection
boundary, `sslcertmode=disable` prevents client-certificate use, `gssencmode=disable`
prevents GSS transport and `require_auth=password,md5,scram-sha-256` limits server
challenges to explicit password authentication; `passfile=/dev/null` prevents
per-user password-file discovery. These [PostgreSQL 17 libpq settings](https://www.postgresql.org/docs/17/libpq-connect.html)
preserve the target's validated TLS mode. Server certificate trust remains the TLS
implementation's responsibility; these controls disable implicit client credentials.

The parent multiplexes nonblocking input/output in bounded chunks and caps responses
at 4096 bytes while reading. Source qualification and connection/SQL/COMMIT waits
inside the child are supervised against the work deadline at 58 seconds. Admission
checks, bounded serialization and `Popen` startup are synchronous and charged to the
same monotonic deadline; they are not independently preemptible waits. An exhausted
admission budget prevents spawning. A startup overrun triggers cleanup when control
returns. This is not a hard real-time guarantee over synchronous execution or OS
scheduling.

Timeout or invalid transport triggers a kill of the direct child if still running,
with a bounded reap wait of at most two seconds and the remaining total budget.
Cleanup never calls an unbounded final `communicate()` or drains additional output.
The trusted worker creates no descendants; cleanup supervises only its direct child,
not a process tree. Fixed structured operational warnings distinguish a confirmed
forced termination/reap (`forced_termination_reaped`) from an expired reap wait
(`termination_unverified`). The latter records unverified termination, never a
successful reap claim. Both paths keep the public result `unknown_outcome`. No
automatic retry is issued.

Only a successful worker COMMIT, valid response and parent validation against the
original command return the existing frozen `CommandReceipt`. Matching operation,
command/source, receipt shape/types, generation/state and attempt relationships are
checked again. Safe controller denial/conflict identifiers and existing safe source
validation identifiers are preserved. Nonzero exit, stalled transport, lost,
malformed, duplicate-key, oversized or forged responses yield
`corpus_publication.unknown_outcome`. Exceptions expose no driver text, submitted
payload, URL or credential context.

On uncertainty retain the **same original operation and command bytes** and invoke
`lookup_outcome` explicitly under current authority. Lookup requires no source
bytes and returns the original receipt or `None`. `None` means unresolved; it does
not prove rollback. Never create a blind new operation, repeat a transition
automatically or infer that a previous generation reopened. Revoked authority still
denies lookup of historical receipts.

## Qualification and remaining gates

The focused suite is `tests/test_corpus_operator.py`, using the existing controller's
owned disposable PostgreSQL 17 fixture, restricted operator login and synthetic
actor custody. It proves begin/recover/seal, exact original lookup and history,
unchanged corpus rows/source bytes, actual COMMIT with deliberately lost response
followed by durable reconciliation, and denial after authority revocation. Transport
cases cover explicit target negatives, child-side revalidation before connecting,
malformed/forged/oversized IPC, blocked stdin/stdout, source qualification within the
supervised deadline, fault-injected stalls at connection and transaction-COMMIT
entry, confirmed or unverified direct-child cleanup, safe source failures, private-protocol rejection
before connect, exact libpq credential restrictions, and hostile ambient settings.
Real competing-begin conflict and disabled-enforcement failures preserve their safe
codes and leave protected state unchanged. Fixtures must run sequentially on one
cluster; skipped database cases are not acceptance evidence.

Use the Python 3.12 environment and owned fixture setup in [MIGRATIONS.md](MIGRATIONS.md#reproduce-local-qualification):

```sh
python -m pytest apps/scribeswell/tests/test_corpus_operator.py -q
python -m pytest apps/scribeswell/tests/test_corpus_publication.py apps/scribeswell/tests/test_corpus_publication_input.py -q
python -m pytest apps/scribeswell/tests -q
```

The [supervisor delivery record](../../../_bmad-output/implementation-artifacts/spec-scribeswell-supervised-corpus-invocation.md)
records exact commands/results and requirement traceability. This qualifies bounded
invocation only. Production Identity/caller custody, least-privilege active release
profile, coordinated writer/importer adoption, sealed full audit, publication and
reader proof remain open. Existing dormant migration references and false enforcement
defaults remain authoritative. There is no live readiness claim.

Impact decisions: app documentation changes; scaffold, shared UI, agent context and
accepted ADRs require no changes or promotion. Existing owner adapter/parser/source
qualifier and pure platform target contract are reused. The API remains app-local
until reuse is proven.
