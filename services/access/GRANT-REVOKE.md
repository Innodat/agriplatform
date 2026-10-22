# Protected organization grant revocation

Access0014 adds `grant.revoke` after immutable Access0013 through the controlled
Access migration route. Migrate and verify before operator activation; failures block
activation and roll back the local transaction. Preserve applied migrations and use
forward recovery, never destructive downgrade. Existing bootstrap portability and
logical-restore limits remain; this proof does not establish portable CI or restore.

Use the protected Access target and existing CLI with `--owner access`. The version1
envelope has organization scope and payload `grant_id`, `account_id`, `membership_id`,
`permission`, `expected_revision`. IDs/revisions preserve exact retained spelling;
account/organization UUIDs canonicalize. Grant IDs are opaque, including empty strings
and Unicode. Input remains bounded to65536 UTF-8 bytes. Access14 permits only revoke
results up to65556 UTF-8 database bytes; prior command results retain8192. The typed
receipt shape stays closed, and revoke CLI output is bounded to262144 bytes for JSON
Unicode escaping. Reason/evidence use the existing
strict parser. No app selector or replacement membership is accepted.

Authority is current original-session `grant.revoke` organization/app/account policy.
Null policy app/account means all; assignment and platform authority confer nothing.
App resolves only from registered organization permission. The shared grant coordination
lock serializes assignment and revoke, with command-specific retry locks and fingerprints.
Only contention on the retry lock maps to busy. Authority is checked again after waits.

Exact org/grant/account/member/permission/revision must match even when already revoked.
Active revocation preserves the binding and creation fields, increments revision once,
and commits server executor/time, `access.organization_grant_revoked` compact before/after
member/revoked/revision event and typed receipt atomically. Matching revoked state records
unchanged receipt only. Overflow conflicts only for changed writes. Revoke makes no Identity
observation: retired/rejoined/deleted targets retain removable historical grants; removal
never grants anything to a replacement. Assignment's verification and five-second deferred
safeguards remain unchanged.

On lost response recover the same operation with `outcome --command grant.revoke
--operation-id UUID --org-id UUID --grant-id OPAQUE --account-id UUID --membership-id
DECIMAL --permission LITERAL`. For leading dash IDs use `--grant-id=OPAQUE`; empty IDs use
`--grant-id=`. Current exact authority is required. The receipt describes historical
completion, not current authority; unresolved is not permission for a fresh duplicate.
Same operation with changed fingerprint conflicts. Never prune evidence or reset fixtures.

Run the prepared Python with `services/access/tests/qualify_grant_revoke.py --all` and
separately `--verify-retained`, setting `ACCESS_QUALIFICATION_DIR` to a fresh source-bound
synthetic proof frame prepared by the existing root bootstrap. Native tests use restricted
operators and actual commits, preserve earlier frames and bind all consumed sources/logs.
No effective reader, ACCESS-B, account grant, consumer, production account or deployment is
activated. Scaffold impact extends existing owner fixtures; no shared UI/context/ADR change.
Owner evidence and mutable delivery contracts record exact results and remaining limits.
