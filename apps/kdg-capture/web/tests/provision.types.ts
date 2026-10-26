import {loadProvision,type ProvisionResult,type PendingProvision,type ProvisionOptions} from '../src/provision';
import {createProvisionEntry} from '../src/provision-entry';
import type {Session} from '../src/entry';
import type {AuthEntryOptions} from '../src/auth-entry';
declare const session:Session,pending:PendingProvision,options:ProvisionOptions,auth:AuthEntryOptions;
const result:Promise<ProvisionResult>=loadProvision(session,pending,options);
const entry=createProvisionEntry(auth),throughAuth:Promise<ProvisionResult>=entry.load(pending);
// @ts-expect-error setup has no received account selector
entry.load({org_id:'org'});
// @ts-expect-error capability observations remain readonly
pending.account_id='replacement';
// @ts-expect-error acquireExecution stays private
entry.acquireExecution();
// @ts-expect-error setup cannot promise saved local data
const wrong:ProvisionResult={kind:'saved_locally'};
void [result,throughAuth,wrong];
