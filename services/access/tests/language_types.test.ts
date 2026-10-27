// Compile-only consumer proof against installer-generated owner wire types.
import type {LanguagePreference, WriteV2MePreferencesLanguagePutData} from '../contracts/generated/types.gen';
type Equal<A, B> = (<T>() => T extends A ? 1 : 2) extends (<T>() => T extends B ? 1 : 2) ? true : false;
type Assert<T extends true> = T;
export type ClosedLocale = Assert<Equal<LanguagePreference['preferred_locale'], 'en' | 'pt'>>;
export type DecimalRevision = Assert<Equal<LanguagePreference['revision'], string>>;
export type PreferenceFields = Assert<Equal<keyof LanguagePreference, 'preferred_locale' | 'revision'>>;
export type ClosedInput = Assert<Equal<keyof NonNullable<WriteV2MePreferencesLanguagePutData['body']>, 'operation_id' | 'expected_revision' | 'preferred_locale'>>;

import type {PreferenceErrorDetails, WriteV2MePreferencesLanguagePutErrors} from '../contracts/generated/types.gen';
export type ClosedPreferenceErrors = Assert<Equal<PreferenceErrorDetails['code'],
  'authentication_required' | 'access_denied' | 'identity.actor_setup_required' |
  'identity.preference_revision_conflict' | 'identity.preference_operation_conflict' |
  'identity.preference_invalid' | 'identity.preference_unavailable'>>;
export type ConflictHasTypedCode = Assert<Equal<WriteV2MePreferencesLanguagePutErrors[409]['detail']['code'], PreferenceErrorDetails['code']>>;
export function recoverPreference(error: WriteV2MePreferencesLanguagePutErrors[409]): string {
  switch (error.detail.code) {
    case 'identity.preference_revision_conflict': return 'reload';
    case 'identity.preference_operation_conflict': return 'reconcile-operation';
    case 'identity.actor_setup_required': return 'setup';
    case 'authentication_required': return 'authenticate';
    case 'access_denied': return 'denied';
    case 'identity.preference_invalid': return 'correct-input';
    case 'identity.preference_unavailable': return 'retry';
    default: { const exhaustive: never = error.detail.code; return exhaustive; }
  }
}
