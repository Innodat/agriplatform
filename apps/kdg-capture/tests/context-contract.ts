import type { CurrentContextResponse, CurrentContextData } from '../contracts/generated/index';

declare const context: CurrentContextResponse;
const member: string = context.membership_id;
const own: 'own_account' = context.resource_scope.kind;
const permission: 'kdg_capture.capture.read.own' = context.permission;
const request: CurrentContextData = { url: '/api/v1/context' };
// @ts-expect-error Revisions/member identifiers must not become JS numbers.
const unsafeMember: number = context.membership_id;
// @ts-expect-error Entry does not establish organization-wide read authority.
const all: 'kdg_capture.capture.read.all' = context.permission;
// @ts-expect-error This API has no organization/account query selectors.
const selector: CurrentContextData = { url: '/api/v1/context', query: {org_id: 'other'} };
void [member, own, permission, request, unsafeMember, all, selector];
