# Final architecture technology review

Reviewed 2026-10-14 against the current working tree: `ARCHITECTURE-SPINE.md`,
`contracts.md`, PtS package/lock sources, `services/access/main.py`, the canonical
Identity/Access contract and builder documentation. No installs, execution, selected
KDG pins, application changes or shared-contract changes occurred.

## Findings

| Level | Location | Finding and consequence | Required clarification |
| --- | --- | --- | --- |
| High — scope consistency | `contracts.md`, Access capability matrix, create.assigned/create.all rows | Both rows impose an unconditional active-child check. Engineering closure §Prior child eligibility instead accepts a previously provisioned child despite ordinary inactivity under current authority/assignment. An implementation following the capability matrix can reject valid queued observations that the later contract explicitly accepts. | Qualify both create rows: fresh eligibility requires active status; sync may use the protected prior-eligibility reference under the later rule. Keep current membership, create permission and applicable assignment checks binding. |
| Medium — validation compatibility | `contracts.md`, §Wire values and validation, Unicode handling | Valid Unicode can contain U+0000. JCS can encode that value, but PostgreSQL JSONB and text cannot store it. Rejecting only invalid Unicode leaves a command that passes the described validation/canonicalization yet fails persistence. | Explicitly reject U+0000 in persisted text/definitions/answers with a safe typed validation result before save success. Prove local/API consistency and a 422 response fixture; preserve rejected input rather than silently removing characters. |

PostgreSQL documents the JSONB/text NUL restriction and database-encoding constraints.
This is an ingress rule for the existing storage choice, not a reason to replace JSONB.
[PostgreSQL JSON types](https://www.postgresql.org/docs/current/datatype-json.html)

The older deactivation paragraphs mention evidence that cannot prove pre-deactivation
Save. They do not explicitly require a Save-time cutoff, but should point directly to
the new rule: the eligibility reference proves prior online setup, deliberately **not**
pre-deactivation Save timing. Avoid strengthening that into an impossible offline
timestamp proof during story implementation. The early POST route seed also omits
`child_eligibility_ref`; label it abbreviated or include that field so exact create DTOs
are taken from engineering closure.

No critical finding identified. The first finding is a stale scope rule; the second is
a concrete storage-validation edge case. Neither requires a new runtime service.

## Verified technology claims

- JCS/RFC8785 describes deterministic JSON serialization with recursive property sorting,
  preserved array order and unchanged string content. It requires duplicate-key rejection,
  valid Unicode and appropriate numeric representations. Large revisions as strings and
  conformance fixtures are consistent with the RFC. Python key sorting alone is correctly
  identified as insufficient. The RFC is Informational; the plan does not claim standards-track
  status. [RFC8785](https://www.rfc-editor.org/rfc/rfc8785)
- Canonicalization is fixed separately from the owner-gated fingerprint algorithm/key
  lifecycle. The documents correctly avoid claiming that canonicalization or a digest
  encrypts predictable child-behavior answers. No hash choice or cryptographic package
  becomes a selected KDG dependency through this review.
- `apps/pts/web/package.json` ranges and lockfile versions match the spine: React 19.3.0,
  Vite 7.3.6, TypeScript 5.9.3, Supabase JS 2.117.1 and Playwright 1.63.0. Vite's locked
  Node engine is `^20.19.0 || >=22.12.0`; Supabase's is `>=22.0.0`, producing the documented
  combined floor. These are repository evidence, not selected KDG pins or executed compatibility.
- FastAPI/Pydantic/SQLAlchemy/Psycopg/Alembic lineage exists in PtS requirements. Existing
  shared UI and Expense package differences still require a coherent first-consumer pin
  decision. No claim of a working KDG manifest, service worker or local database is made.
- Actual Access source still exposes `/v1/check` with the restricted legacy PtS permissions;
  the canonical v2 contract states it is unimplemented. Builder documentation still labels
  the CLI a placeholder. The architecture explicitly gates current KDG checks, concrete
  operator trust and generator inputs; its target-system diagram is not runtime evidence.
- IndexedDB transaction completion, strict durability as a hint, shell-only service-worker
  caching, foreground retries and tested schema/update handling retain the source-backed
  direction in the earlier [technology review](review-technology.md). Browser deletion,
  eviction and physical-device behavior remain practical limitations and delivery evidence
  requirements, rather than promised runtime guarantees.

## Disposition

The retained stack still fits. Resolve the scoped wording and NUL validation before the
affected story's Build gate. Exact package/browser/runtime compatibility, fingerprint
sensitivity/key lifecycle, shared Identity/Access representations, operator bindings and
real installed Android/iPhone proof remain explicit owner or delivery gates. This review
does not establish application or production readiness.
