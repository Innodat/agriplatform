/** Public reader context only; no caller-selected destination or private state. */
import {parseReaderURL, readerSearch} from './reader-layout';
const books = new Set('Gen Exod Lev Num Deut Josh Judg Ruth 1Sam 2Sam 1Kgs 2Kgs 1Chr 2Chr Ezra Neh Esth Job Ps Prov Eccl Song Isa Jer Lam Ezek Dan Hos Joel Amos Obad Jonah Mic Nah Hab Zeph Hag Zech Mal'.split(' '));
export function publicAccountReturn() {
  const destination = new URL(location.origin);
  destination.pathname = new URL(import.meta.env.BASE_URL, location.origin).pathname;
 const input = new URLSearchParams(location.search);
 if (input.has('reader')) {
   const layout = parseReaderURL(input);
   if (!layout.invalid) destination.search = readerSearch('', layout.refs, layout.active);
   return destination.href;
 }
  for (const key of ['book', 'chapter', 'verse', 'compareBook', 'compareChapter', 'compareVerse']) {
    const values = input.getAll(key);
    if (values.length !== 1) continue;
    const value = values[0];
    const valid = key.endsWith('Book') || key === 'book'
      ? books.has(value)
      : /^[1-9]\d{0,2}$/.test(value) && Number(value) <= (key.toLowerCase().includes('verse') ? 176 : 150);
    if (valid) destination.searchParams.set(key, value);
  }
  return destination.href;
}

export function accountError(error: unknown, mode: 'signin' | 'signup') {
  const code = (error as { code?: string })?.code;
  if (code === 'signup_disabled') return 'Account creation is currently unavailable. You can still sign in or continue reading.';
  if (code === 'weak_password') return 'Choose a stronger password, then try again.';
  if (code === 'email_address_invalid' || code === 'validation_failed') return 'Check your email address, then try again.';
  if (code === 'over_email_send_rate_limit' || code === 'over_request_rate_limit') return 'Too many attempts. Please wait a little and try again.';
  if (code === 'email_not_confirmed') return 'Confirm your email using your confirmation link, then sign in.';
  if (mode === 'signin' && code === 'invalid_credentials') return 'Check your email and password, then try again.';
  return mode === 'signup' ? 'We could not complete your account request. Check your connection and try again.' : 'We could not sign you in. Check your connection and try again.';
}

/** Only booleans survive startup inspection; credentials remain SDK-owned. */
const callbackKeys = ['error', 'error_code', 'error_description', 'code', 'access_token', 'refresh_token', 'expires_in', 'expires_at', 'token_type', 'type', 'provider_token', 'provider_refresh_token'];
export function hasAccountCallback() {
  const url = new URL(location.href), fragment = new URLSearchParams(url.hash.slice(1));
  return callbackKeys.some(key => url.searchParams.has(key) || fragment.has(key));
}
/** Project a copy without consuming SDK-owned callback data or changing the native entry. */
export function projectAccountCallback(input: URL) {
  const url = new URL(input.href), fragment = new URLSearchParams(url.hash.slice(1));
  let fragmentChanged = false;
  for (const key of callbackKeys) {
    // URLSearchParams mutations normalize the query even when the key is absent.
    // Leave ordinary malformed provenance byte-for-byte intact.
    if (url.searchParams.has(key)) url.searchParams.delete(key);
    if (fragment.has(key)) {fragment.delete(key); fragmentChanged = true;}
  }
  if (fragmentChanged) url.hash = fragment.toString();
  return url;
}
export function scrubAccountCallback() {
  const url = projectAccountCallback(new URL(location.href));
  history.replaceState(history.state, '', url.pathname + url.search + url.hash);
}
/** Reject explicit errors and incomplete implicit callbacks before SDK initialization. */
export function consumeCallbackError() {
  if (!hasAccountCallback()) return false;
  const url = new URL(location.href), fragment = new URLSearchParams(url.hash.slice(1));
  const value = (key: string) => fragment.get(key) ?? url.searchParams.get(key);
  const invalid = ['error', 'error_code', 'error_description'].some(key => fragment.has(key) || url.searchParams.has(key))
    || ['access_token', 'refresh_token', 'expires_in', 'token_type'].some(key => !value(key));
  if (invalid) scrubAccountCallback();
  return invalid;
}
