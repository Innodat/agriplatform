# Verification reviewer findings — retained before correction

## Deferred account-observation expiry is not behaviorally verified

Changed surface: Access17 extends the deferred `require_command_event` check to
`account_grant.assign`. The qualifier immediately commits; the private supplement waits
before mutation and is rejected by the earlier freshness check. Searches of account-grant
symbols and observation/commit tests found no successful function return followed by
expired COMMIT. Removing the deferred extension would leave checked assertions passing.
Add the explicit transaction, expired commit, unchanged grant/outcome/event and exact retry
proof to the native qualifier. Disposition: patch.

## Receipt lookup does not verify mismatched selectors under valid authority

Changed surface: `account_grant_outcome` compares stored account/permission/revoke UUID.
The wrong-account native test denies at authority first; CLI revoke recovery supplies the
correct UUID, and unit tests only reject malformed selector shapes before I/O. Symbol and
import searches found no authorized wrong valid UUID at the adapter/database boundary.
Removing the stored revoke UUID comparison leaves checked assertions passing. Add exact
authorized wrong-grant denial followed by correct selector recovery. Disposition: patch.

Both findings were received before triage. Individual V1/V2 rows and completed corrections
are recorded in the execution spec; V1 shares the B9 deferred-boundary correction.
