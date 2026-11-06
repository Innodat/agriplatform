# Browser JSON cache

Dependency-free, opt-in corpus JSON reuse, proven by the PtS reader. This package
stores no credentials and makes no access decision. An application must supply a
fetch callback that checks current server authorization on every read, including
conditional requests. Stored bytes become visible only after a successful response.
There is no offline fallback or permission cache.

`createJsonCache({app, api, account, format, storage, validate})` scopes entries by
application, API origin/base, verified account, format version and exact request
path/query. Select eligible routes explicitly. `validate(value, path)` checks the
application's payload shape before storing or restoring it. The envelope also checks
scope, format, validator and path. Corrupt or unavailable storage is a miss; quota
failure leaves the response available in memory. Defaults bound all persisted entries
for the app to four entries and 4,000,000 estimated UTF-16 bytes, including envelopes.
Oversized entries are not cached. Applications can choose tighter limits.

`cache.read(path, fetchAuthorized, current)` supplies the stored validator to the
callback, uses a current authorized 304 without parsing a body, or replaces it with
validated JSON from a successful response. A 304 without usable bytes triggers one
unconditional request. Denial/outage never restores persisted bytes. The callback
owns authentication refresh, status mapping and current access. `current()` must
reject account/view/session replacement and cancellation.

Wrap the entire executing read in `withDeadline(signal => ..., {signal, timeoutMs})`.
The default 15-second total deadline covers fetch, authentication refresh and body
parsing; cancellation/deadline rejection also works if body work ignores abort.
Always pass that signal to fetch and include its state in `current()` so late work
cannot store a result. Rejected/late promises remain observed.

`cache.clear()` invalidates operation guards and removes this app's persisted
entries across accounts/formats, plus this instance's memory. It must run on
sign-out, account/session replacement and confirmed authorization loss. Storage
removal is best effort when browser storage itself is unavailable. Applications
still reject old responses and require current authorization after reload; this
package cannot recall already delivered bytes. Navigation/view clearing is a
separate application action and need not delete cached corpus entries.

Do not select private files, downloads, exports, signed URLs, tokens, authentication
or authorization results. Cache invalidation never replaces private-file custody or
session cleanup. Validators must include semantic representation/projection version,
account scope and stable content/rights/source evidence; omit only intentionally
volatile display metadata such as export-generation timestamps. Keep HTTP responses
`no-store` so proxies and browser HTTP caches cannot bypass authorization.

Run `npm test --workspace @platform/browser-cache` on Node 24. The package-local
TypeScript configuration prevents inheriting the repository's stale root target.
See [platform conventions](../docs/development/browser-caching.md) and the PtS
consumer's [verification](../../apps/pts/docs/VERIFICATION.md).
