// Compile-only consumer proof against generated owner types. No HTTP credentials.
import type {AccountDecision, EnrollmentAck, StudiesError} from '../contracts/generated/types.gen';
type Equal<A, B> = (<T>() => T extends A ? 1 : 2) extends (<T>() => T extends B ? 1 : 2) ? true : false;
type Assert<T extends true> = T;
export type AccountFields = Assert<Equal<keyof AccountDecision,
  'account_id' | 'actor_id' | 'permission' | 'authorization_scope' | 'decision_id' | 'checked_at'>>;
export type PersonalScope = Assert<Equal<AccountDecision['authorization_scope'], {kind: 'account'}>>;
export type FixedPermission = Assert<Equal<EnrollmentAck['result']['permission'], 'scribeswell.studies.use'>>;
export type ClosedDisposition = Assert<Equal<EnrollmentAck['result']['disposition'], 'created' | 'unchanged'>>;
export type ClosedErrors = Assert<Equal<StudiesError['error_id'],
  'authentication_required' | 'service_access_denied' | 'access_denied' | 'identity.verification_required' |
  'validation_failed' | 'authorization_unavailable' | 'identity.setup_unavailable' | 'dependency_unavailable'>>;
