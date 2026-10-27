/** Current Access decisions are observations; every protected action checks again. */
import type {CheckV2CheckPostResponses, OrganizationContext, CapabilityError, OrganizationsDiscovery, ApplicationsDiscovery} from './generated/types.gen';
export type Decision = CheckV2CheckPostResponses[200];
export type Scope = {kind: 'account'} | {kind: 'organization'; org_id: string};
export type Expected = {account_id: string; permission: string; authorization_scope: Scope;
  resource: 'account' | 'own' | 'organization'};
export type AccessFailure = 'authenticate' | 'denied' | 'setup' | 'invalid' | 'unavailable';
export class AccessDependencyFailure extends Error {
  constructor(public readonly outcome: AccessFailure = 'unavailable') { super('access_dependency_failure'); }
}
type ObjectValue = Record<string, unknown>;
const object = (v: unknown): v is ObjectValue => v !== null && typeof v === 'object' && !Array.isArray(v);
const uuid = (v: unknown): v is string => typeof v === 'string' && /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(v) && v !== '00000000-0000-0000-0000-000000000000';
const utc = (v: unknown): v is string => typeof v === 'string' && /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|\+00:00)$/.test(v)
  && Number.isFinite(Date.parse(v)) && new Date(v).toISOString().slice(0, 19) === v.slice(0, 19);
const member = (v: unknown): v is string => typeof v === 'string' && /^[1-9][0-9]{0,18}$/.test(v) && BigInt(v) <= 9223372036854775807n;
const same = (a: unknown, b: string) => typeof a === 'string' && a.toLowerCase() === b.toLowerCase();
function exact(v: ObjectValue, keys: readonly string[]): boolean {
  return Object.keys(v).length === keys.length && keys.every(key => Object.hasOwn(v, key));
}
function scope(v: unknown, expected: Scope): boolean {
  return object(v) && v.kind === expected.kind && (expected.kind === 'account'
    ? exact(v, ['kind']) : exact(v, ['kind', 'org_id']) && uuid(v.org_id) && same(v.org_id, expected.org_id));
}
function requireValid(condition: unknown): asserts condition {
  if (!condition) throw new AccessDependencyFailure();
}
const common = ['account_id', 'actor_id', 'permission', 'authorization_scope', 'decision_id', 'checked_at'];
export function validateDecision(value: unknown, expected: Expected): Decision {
  requireValid(object(value));
  requireValid(uuid(expected.account_id) && uuid(value.account_id) && same(value.account_id, expected.account_id)
    && uuid(value.actor_id) && uuid(value.decision_id) && utc(value.checked_at)
    && value.permission === expected.permission && scope(value.authorization_scope, expected.authorization_scope));
  if (expected.authorization_scope.kind === 'account') {
    requireValid(expected.resource === 'account' && exact(value, common));
  } else {
    requireValid(member(value.membership_id));
    if (expected.resource === 'own') {
      requireValid(exact(value, [...common, 'membership_id', 'person_id', 'resource_scope'])
        && uuid(value.person_id) && object(value.resource_scope)
        && exact(value.resource_scope, ['kind', 'person_id']) && value.resource_scope.kind === 'own'
        && same(value.resource_scope.person_id, value.person_id));
    } else {
      requireValid(expected.resource === 'organization' && exact(value, [...common, 'membership_id', 'resource_scope'])
        && scope(value.resource_scope, expected.authorization_scope));
    }
  }
  return value as Decision;
}
export function validateOrganizationContext(value: unknown, account: string, org: string): OrganizationContext {
  requireValid(object(value) && exact(value, ['account_id', 'actor_id', 'org_id', 'membership_id', 'person_id', 'observation_id', 'checked_at']));
  requireValid(uuid(value.account_id) && same(value.account_id, account) && uuid(value.org_id) && same(value.org_id, org)
    && uuid(value.actor_id) && member(value.membership_id) && (value.person_id === null || uuid(value.person_id))
    && uuid(value.observation_id) && utc(value.checked_at));
  return value as OrganizationContext;
}
const errors: Record<CapabilityError['error_id'] | 'internal_error', [number, AccessFailure]> = {
  authentication_required: [401, 'authenticate'], service_access_denied: [403, 'unavailable'],
  access_denied: [403, 'denied'], validation_failed: [422, 'invalid'],
  'identity.actor_setup_required': [409, 'setup'], 'identity.person_link_required': [409, 'setup'],
  'identity.verification_required': [403, 'setup'], authorization_unavailable: [503, 'unavailable'],
  internal_error: [500, 'unavailable'],
};
export function accessFailure(status: number, value: unknown): AccessFailure {
  if (!object(value) || !exact(value, ['error_id', 'error', 'details']) || typeof value.error_id !== 'string'
    || typeof value.error !== 'string' || !object(value.details) || !exact(value.details, [])) return 'unavailable';
  const entry = Object.hasOwn(errors, value.error_id) ? errors[value.error_id as keyof typeof errors] : undefined;
  return entry && entry[0] === status ? entry[1] : 'unavailable';
}

/** Position only; never forward a discovery observation instead of a current check. */
export function validateOrganizations(value: unknown, pageSize = 100, afterOrgId?: string): OrganizationsDiscovery {
  requireValid(Number.isInteger(pageSize) && pageSize >= 1 && pageSize <= 100 && (afterOrgId === undefined || uuid(afterOrgId)));
  requireValid(object(value) && exact(value, ['organizations', 'next_cursor']) && Array.isArray(value.organizations)
    && value.organizations.length <= pageSize);
  let previous = afterOrgId?.toLowerCase() ?? '';
  for (const item of value.organizations) {
    requireValid(object(item) && exact(item, ['org_id', 'name', 'membership_id']) && uuid(item.org_id)
      && item.org_id.toLowerCase() > previous && typeof item.name === 'string' && member(item.membership_id));
    previous = item.org_id.toLowerCase();
  }
  if (value.next_cursor !== null) {
    requireValid(value.organizations.length === pageSize && typeof value.next_cursor === 'string'
      && /^[A-Za-z0-9_-]{48}$/.test(value.next_cursor));
    let decoded = '';
    try { decoded = atob(value.next_cursor.replace(/-/g, '+').replace(/_/g, '/')); } catch { throw new AccessDependencyFailure(); }
    requireValid(uuid(decoded) && decoded === previous && decoded === decoded.toLowerCase()
      && btoa(decoded).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '') === value.next_cursor);
  }
  return value as OrganizationsDiscovery;
}

export function validateApplications(value: unknown): ApplicationsDiscovery {
  requireValid(object(value) && exact(value, ['applications', 'checked_at']) && utc(value.checked_at)
    && Array.isArray(value.applications) && value.applications.length <= 128);
  let previous = '';
  for (const item of value.applications) {
    requireValid(object(item) && exact(item, ['app_id', 'eligible_scope_kinds']) && typeof item.app_id === 'string'
      && /^[a-z][a-z0-9_]{1,63}$/.test(item.app_id) && item.app_id > previous && Array.isArray(item.eligible_scope_kinds));
    const scopes = JSON.stringify(item.eligible_scope_kinds);
    requireValid(scopes === '["account"]' || scopes === '["organization"]' || scopes === '["account","organization"]');
    previous = item.app_id;
  }
  return value as ApplicationsDiscovery;
}
