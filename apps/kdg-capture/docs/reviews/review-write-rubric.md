# Owned WRITE and secret execution rubric review

2026-10-14. Independent bmad-architecture rubric/reconciliation gate.

**Verdict: PASS for the selected WRITE planning baseline.** No critical/high or
medium semantic blocker was found. Implementation readiness reporting must retain
the explicit delivery/release proof gates; this review does not authorize execution.

## Scope and reconciliation

Reviewed `owned-write-and-secret-execution.md` against the app-owned capture command,
receipt, no-op, unresolved outcome, canonical envelope and prior-child eligibility
decisions; the selected Identity/Access substrate; and KDG's initial HMAC disposition.
No code, tests, roles, secret files, schemas or deployment were created or inspected
as an installed target. The sole owner acknowledgement and approved product scope
remain settled.

## Rubric assessment

| Criterion | Assessment |
| --- | --- |
| Outcome identity | PASS. User outcome uniqueness is org/account/command/operation; owner operators use scope/executor without a fabricated account. Internal row ID and caller operation ID are distinct. Unsupported retained versions never become absent actions. |
| App receipt/no-op/unknown semantics | PASS. The original compact capture ID/revision is returned even after later edits. No-op keeps revision and records no fake transition. Failed/rejected operations do not become success/placeholder rows. Lookup permission derives from stored resource/command, not a query discriminator. |
| Atomic local mutation/evidence | PASS. Outcome-key transaction lock precedes effects; different operation keys still encounter local revision/structural guards. Business state, history and successful receipt commit together. Full rollback includes evidence/receipt failures. A lost transport acknowledgement remains uncertain and preserves original identity. |
| Short transaction boundary | PASS. Current external authority/observations precede business locks; network rechecks release locks. Monotonic total budget and capped lock/statement waits are declared. Locks are transaction-scoped, pooled context is cleared, and busy responses do not imply a new action or guaranteed rollback. |
| Current domain validation | PASS. Replay rechecks current command/resource authority; new effects validate assignment/member-bound eligibility/version/lifecycle and exact revision. No old membership substitution, guessed pre-deactivation Save time or changed definition is introduced. App-owned prior-child reference policy remains authoritative. |
| Ownership and immutable evidence | PASS. Each owner has its own tables. Identity/Access events contain bounded typed transitions; sensitive KDG revision snapshots remain protected app business history. No generic full-row/answer audit dump, central audit/write service or Leave draft evidence expansion appears. |
| Actual-role contract | PASS at planning altitude. Runtime/operator/migrator credentials are distinct, forced RLS scopes own/all modes, and immutable tables reject alternate mutation. Context settings are honestly described as trusted backend assertions rather than independent credential-compromise protection. |
| Error/recovery bounds | PASS. Only identified constraint/lock failures receive typed mappings; unknown errors remain safe and uncertain. Bounded automatic lookup/retry does not run after a definitive deny/validation/conflict or unblock dependent edits prematurely. |
| Fingerprint/key contract | PASS. Full HMAC-SHA-256/JCS bytes, maintained comparison/library, strict JSON validation, decimal bigints and unchanged valid text match app meaning. Per-environment owner-bound file metadata, actual runtime UID/mode and separate backup input are concrete selections. No browser/DB/image/startup/fallback key is introduced. |
| Rotation/restore | PASS. Existing outcome version/algorithm/key selects replay verification; old keys survive supported rotation/rollback and restorability. Missing material blocks execution while existing authorized lookup can still expose its compact receipt. Real restore evidence precedes activation. |
| Planning versus runtime | PASS. Actual role/race/rollback/pool/JCS/rotation/recovery proof is allocated to existing owners and consuming tests. Exact encrypted archive/backend identity remains an explicit release input, not a fabricated installed system or an instruction to provision during planning. |

## Nonblocking delivery observations

### W1 — Preserve the lookup versus mutation-key distinction in acceptance

Missing a retained verification key must refuse payload replay/re-execution; it does
not turn an already committed authorized compact lookup into `unresolved`. The HMAC
disposition explicitly preserves this distinction, and the WRITE contract inherits
it. Include the paired receipt-lookup versus mutation-replay case when implementing
the selected helper. No new recovery workflow or permission relaxation is needed.

### W2 — Implement archive/restore only from the declared release inputs

The key mount/UID/permissions and manifest fields are selected; actual encrypted
archive/backend/decryption authority, target image identity and restore transcript
remain release inputs. They cannot be inferred from a schema check or a synthetic key
fixture. Preserve matching data+key restore and prior retained retry/mismatch proof
before real-data activation. This is existing recovery acceptance, not missing product
discovery or permission to deploy.

## Scope conclusion

The last WRITE choices are concrete enough to converge independent helper, database,
app consumer and secret-config builders. The contract preserves explicit observation
Save, app-local eligibility/history and truthful queue recovery; it adds no unfinished
observation persistence, administrative conflict draft, outbox/worker, universal offline
framework, key service or changed Leave ordinary draft audit policy. Continue the
planning readiness reconciliation while keeping actual delivery separately authorized.
