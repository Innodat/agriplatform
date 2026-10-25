import {createRecoveryEntry} from '../src/recovery-entry';
import type {ExecutionLease} from '../src/auth/lifecycle';
declare const entry:ReturnType<typeof createRecoveryEntry>;
declare const lease:ExecutionLease<{account:string}>;
const id:string=lease.session.account_id;
const current:boolean=lease.isCurrent();
const account:string=lease.context.account;
// @ts-expect-error owner lease is not exposed by the consuming entry
entry.acquireExecution();
// @ts-expect-error shared leases are read-only
lease.session.access_token='replacement';
// @ts-expect-error scope and original discriminator are required
entry.recover({operation_id:id});
void [current,account];
