import {validateDecision, validateOrganizationContext, accessFailure, AccessDependencyFailure} from '../contracts/adapter';
import type {Expected} from '../contracts/adapter';
const account = '11111111-1111-4111-8111-111111111111';
const actor = '22222222-2222-4222-8222-222222222222';
const org = '33333333-3333-4333-8333-333333333333';
const person = '44444444-4444-4444-8444-444444444444';
const base = {account_id: account, actor_id: actor, permission: 'pts.poetry.read', authorization_scope: {kind: 'account'}, decision_id: actor, checked_at: '2026-10-27T12:00:00Z'};
const expected: Expected = {account_id: account, permission: 'pts.poetry.read', authorization_scope: {kind: 'account'}, resource: 'account'};
const assert = (v: unknown) => {if (!v) throw Error('capability_adapter_assertion');};
const refuses = (value: unknown, e = expected) => {try {validateDecision(value, e);} catch (error) {assert(error instanceof AccessDependencyFailure); return;} throw Error('unsafe_decision_accepted');};
validateDecision(base, expected);
for (const value of [{...base, person_id: null}, {...base, account_id: actor}, {...base, actor_id: ''}, {...base, permission: 'pts.poetry.export'}, {...base, authorization_scope: {kind: 'account', org_id: org}}, {...base, checked_at: '2026-10-27T12:00:00+02:00'}]) refuses(value);
const ownExpected: Expected = {account_id: account, permission: 'leave.request.own.read', authorization_scope: {kind: 'organization', org_id: org}, resource: 'own'};
const own = {...base, permission: ownExpected.permission, authorization_scope: ownExpected.authorization_scope, membership_id: '19', person_id: person, resource_scope: {kind: 'own', person_id: person}};
validateDecision(own, ownExpected);
for (const value of [{...own, membership_id: 19}, {...own, membership_id: '9223372036854775808'}, {...own, resource_scope: {kind: 'own', person_id: actor}}, {...own, authorization_scope: {kind: 'organization', org_id: actor}}]) refuses(value, ownExpected);
validateOrganizationContext({account_id: account, actor_id: actor, org_id: org, membership_id: '19', person_id: null, observation_id: actor, checked_at: base.checked_at}, account, org);
assert(accessFailure(403, {error_id: 'service_access_denied', error: 'safe', details: {}}) === 'unavailable');
assert(accessFailure(403, {error_id: 'access_denied', error: 'safe', details: {}}) === 'denied');
assert(accessFailure(503, {error_id: 'access_denied', error: 'safe', details: {}}) === 'unavailable');
assert(accessFailure(403, {error_id: '__proto__', error: 'safe', details: {}}) === 'unavailable');
const context = {account_id: account, actor_id: actor, org_id: org, membership_id: '19', person_id: null, observation_id: actor, checked_at: base.checked_at};
for (const value of [{...context, account_id: actor}, {...context, org_id: actor}]) {
  let rejected = false;
  try { validateOrganizationContext(value, account, org); } catch (error) { assert(error instanceof AccessDependencyFailure); rejected = true; }
  assert(rejected);
}
assert(accessFailure(403, {detail: {code: 'service_access_denied'}}) === 'unavailable');
