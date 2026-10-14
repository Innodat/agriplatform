# WRITE technology and secret-execution review

2026-10-14. Required architecture technology/source gate for
platform/docs/architecture/contracts/owned-write-and-secret-execution.md. Reviewed
official PostgreSQL/Python/Docker documentation and the selected JCS publisher source.
No database, SQL, dependency installation, secret or deployment operation performed.

**Verdict: PASS with one concrete secret-directory clarification before planning
closure.** Transaction/outcome/JCS/HMAC selections fit the named technology. Runtime
immutability, key isolation and restore remain acceptance evidence, not proven by this
document.

## Finding T1 — distinguish protected host ancestor from mounted readable leaf

The secret section requires mode0400 key files owned by UID10001 and directory0700,
then describes a root-owned host secret source. It does not unambiguously state who
owns the mounted directory. If that directory is root-owned0700, UID10001 cannot
traverse it even when its files are owned by UID10001. A read-only bind mount controls
writes but does not automatically fix directory search permissions.

Specify a root-only host ancestor managed by the operator, with the mounted leaf
directory and files owned by the actual runtime UID (0700/0400), provisioned by root
and mounted read-only; or specify an explicit supported UID mapping alternative.
Check this with actual container UID/namespace/mount tests in ENV. Do not weaken to
world-readable files or assume root privileges in the API.
[Linux pathname permissions](https://man7.org/linux/man-pages/man7/path_resolution.7.html),
[Docker bind mounts](https://docs.docker.com/engine/storage/bind-mounts/).

## Verified technology choices

- PostgreSQL transaction advisory locks automatically release at transaction end;
  session locks do not follow rollback semantics. The explicit per-key transaction
  lock, exact unique outcome key, short transaction and deterministic domain-lock
  order fit the desired serialization. A hash collision adds contention without
  equating two outcome identities. Advisory locking is cooperative, so uniqueness
  and domain/immutable guards remain essential for alternate write paths.
  [Explicit locking](https://www.postgresql.org/docs/current/explicit-locking.html).
- lock_timeout limits each acquisition attempt, while statement_timeout limits the
  statement; neither is by itself the ten-second whole execution budget. The
  contract correctly requires a server-monotonic overall budget and remaining-time
  caps, and narrowly maps only the outcome-key wait to operation_busy. Delivery must
  prove rollback before duplicate recovery and transaction-local context/pool cleanup.
  [Client defaults](https://www.postgresql.org/docs/current/runtime-config-client.html).
- NULLS NOT DISTINCT supports platform-scope nullable-key uniqueness on PostgreSQL
  >=15. The existing qualified-target floor applies. INSERT/SELECT-only privileges,
  restricted non-owner roles and database guards can preserve immutable outcomes and
  history. They do not make records immutable against a database owner/superuser;
  no such claim is made. Alternate-write tests must include UPDATE/DELETE and denied
  TRUNCATE; PostgreSQL permits dedicated TRUNCATE statement triggers when a guard is
  used. [Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html),
  [CREATE TRIGGER](https://www.postgresql.org/docs/current/sql-createtrigger.html).
- rfc8785 0.1.4 is a pure-Python publisher release with dependencies=[] and Python
  >=3.8. Its source metadata supports the no-runtime-dependency claim; actual
  Python3.15 conformance remains delivery proof. Parse/shape checks must reject
  duplicate keys before a parser discards them; the contract explicitly places
  rejection before canonicalization. JCS UTF-16 ordering, Unicode preservation and
  numeric fixtures remain necessary.
  [Publisher v0.1.4 metadata](https://github.com/trailofbits/rfc8785.py/blob/v0.1.4/pyproject.toml),
  [RFC8785](https://www.rfc-editor.org/rfc/rfc8785).
- Python3.15 hmac/hashlib SHA-256 and compare_digest provide the selected maintained
  primitives. Fixed 32-byte digest storage/comparison and independent key IDs avoid
  custom cryptography and preserve original-key retry interpretation. The design
  correctly distinguishes keyed verification from encryption or authorization.
  [Python3.15 HMAC](https://docs.python.org/3.15/library/hmac.html).

## Planning versus evidence

Exact secret path/schema/UID/modes and separate archive manifest are proposed execution
inputs. A read-only mount plus namespace/regular-file validation is a reasonable
mechanism once T1 is clarified; it does not establish actual mount isolation. Explicit
root/operator access is part of trusted provisioning/restore, so “only runtime reads”
is understood as the ordinary application-consumer boundary, not exclusion of recovery
operators.

Separate encrypted key archive/decryption authority and coordinated matching data/key
restore support the database-only threat boundary. The contract explicitly leaves
archive/backend/encryption identity and restore transcript as release inputs. No
installed backup or managed key service is inferred. Missing keys/version material
remain fail-closed; no fresh execution/fallback digest is introduced. Newest-stable
TypeScript/Node/Python planning selections are unchanged.

## Resolution recheck — 2026-10-14

**Final verdict: PASS. T1 resolved; no remaining technology planning finding.**
The current contract explicitly separates the root-owned0700 host ancestor,
staging and archive from the UID/GID10001-owned0700 mounted leaf and
UID/GID10001-owned0400 key files. It requires traversal through container
/run/secrets and rejects a root-owned0700 mounted leaf. This fits ordinary Linux
directory search permissions and Docker read-only bind-mount semantics: runtime
ownership permits reads/traversal, while the read-only projection prevents runtime
writes and the separate host ancestor protects operator staging. No root API,
world-readable key or automatic UID-remapping assumption is introduced. The Linux
and Docker primary sources cited under T1 support this resolution; no changed
technology fact requires another source lookup.

The physical integrity changes also fit PostgreSQL: Identity actor references use
local RESTRICT FKs with actor creation before dependent rows; KDG revision linkage
uses a matching referenced composite UNIQUE key and local composite FK, with outcome
inserted before dependent evidence in one transaction. These enforce the declared
actor/executor/operation and original-owner linkage without cross-owner FKs.
Restarted authority checks retain the original whole-execution budget rather than
resetting the deadline. The previously verified transaction and timeout technology
choices remain applicable.

PASS closes technology planning only. Delivery still must demonstrate actual
UID/namespace/mount readability and write isolation, local FK rejection, rollback,
deadline enforcement, JCS compatibility and coordinated secret/data restore through
the contract's acceptance fixtures. No package, SQL, code, secret or deployment
operation was performed for this recheck.
