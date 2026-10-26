import {createCapture,type PendingCreate} from '../src/create';
import type {CreateCommand,CreateCaptureData} from '../../contracts/create-generated/types.gen';
declare const pending:PendingCreate;declare const command:CreateCommand;
const wire:CreateCaptureData={url:'/api/v1/captures',body:command};
// @ts-expect-error required owner fence
createCapture({account_id:'a',access_token:'t'},pending,{});
// @ts-expect-error capture identity is required
const missing:CreateCommand={operation_id:'o',command_version:1,child_id:'c',questionnaire_version_id:'q',observation_date:'2026-10-26',captured_at:'time',child_eligibility_ref:'r',answers:{}};
// @ts-expect-error no query selectors
const selectors:CreateCaptureData={...wire,query:{org_id:'o'}};
// @ts-expect-error version closed
const version:CreateCommand={...command,command_version:2};
void [missing,selectors,version];
