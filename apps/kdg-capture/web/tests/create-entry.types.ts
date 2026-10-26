import {createCreateEntry} from '../src/create-entry';
import type {CreateCommand} from '../../contracts/create-generated/types.gen';
declare const entry:ReturnType<typeof createCreateEntry>;declare const command:CreateCommand;
// @ts-expect-error leases hidden
entry.acquireExecution();
// @ts-expect-error org required
entry.create({account_id:'a',command});
async function consume(){const result=await entry.create({account_id:'a',org_id:'o',command});if(result.kind==='committed'){
// @ts-expect-error immutable receipt
result.receipt.result.revision='2';
}if(result.kind==='error'){
// @ts-expect-error no conflict revision on create
result.current_revision;
}}void consume;
