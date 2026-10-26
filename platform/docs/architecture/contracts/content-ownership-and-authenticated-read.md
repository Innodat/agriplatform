# Content ownership and authenticated read contract

**Status:** Minimum technical design and delivery decomposition proposal; not implementation-ready
**Date:** 2026-10-06
**Authority:** [ADR-0054](../decisions/0054-application-authorized-content-and-enforced-ownership.md),
[ADR-0055](../decisions/0055-authenticated-private-downloads-by-default.md),
[ADR-0038](../decisions/0038-finalized-content-byte-identity.md).

## Minimum persisted metadata

| Information | Contract |
| --- | --- |
| Content identity | Preserve the existing content ID's meaning. The current composite org/id key is not proof IDs are globally unique; inventory collisions before selecting the new key or mapping. No identity can resolve to different replacement bytes. |
| Owning application | Exactly one stable registered application ID, established by trusted creation/adoption and checked against authenticated service policy. No allowed-applications list. |
| Resource ownership | Closed variant: application (no org/account), organization (required org ID, no account owner), or account (required account ID, no org). Enforce the variant structurally, not merely in Python. Uploader is separate attribution, not a second owner. |
| Provider locator | Content-owned provider/bucket/object/version reference. Never supplied by browser or interpreted as user authority. Existing paths may remain opaque locators if verified against the adopted identity. No mandatory new bucket per scope. |
| Verified content | Existing digest, byte size, media type, verification/readiness and fixed provider byte/version binding. A checksum against a mutable key alone is insufficient. |
| Attribution/lifecycle | Server-controlled creation/change evidence, verified service executor and separately asserted initiator; preserve existing audit provenance. Keep required retention, safety and association/cleanup state in the owning contract. |

Ownership metadata cannot be reassigned through ordinary read/update requests. A migration
maps verified legacy objects once through an explicit adoption procedure; runtime cannot
use that procedure to transfer files. Keep domain associations in the application, not a
new shared request/employee table inside Content. No generic record-level ACL engine.

This specifies required information, not DDL. A new constrained ownership relation or
replacement schema must preserve actual RLS/privilege enforcement for all three variants;
merely making existing org_id nullable is not acceptable. Provider credentials remain
server-only. Deduplication must be confined to exact owning app/resource scope; equal
hashes across apps or accounts must not reveal existence or merge ownership.

## Application-to-Content read boundary

The application authenticates each file request, resolves its permitted domain association
and verifies current user/resource rights. Its server-only Content request names the exact
content identity and expected typed ownership context, with operation/trace and bounded
initiator evidence. Content derives calling service/application authority from credentials;
requested owner/context is a comparison, not permission. Content checks stored scope,
allowed operation, readiness, safety and lifecycle before opening the stored provider locator.

Content streams bytes to the application; the application streams to the authenticated
browser. No URL/token redirect or storage locator is returned to the browser. Provider
access stays in Content. Both hops close resources on failure/disconnect and propagate
backpressure; no open database transaction during transfer and no whole-file buffering.
Neither layer exposes an arbitrary URL-fetch endpoint or accepts browser provider paths.

Before response headers, failures use safe typed errors without ownership/existence leaks.
After bytes start, terminate an incomplete stream on upstream failure; do not append JSON
to file bytes, label it complete or silently restart another full transfer. Client retry
is a new authorized read, not a consequential-write replay. Evidence distinguishes an
accepted/read-started operation from verified transfer completion; do not claim the user
saved the file. A downstream disconnect does not establish successful delivery.

GET, HEAD and any supported single-range/resume requests use the same authorization and
ownership boundary. Do not expose size/type metadata to unauthorized HEAD callers. Exact
range/conditional handling, safe Content-Disposition/Content-Type/length headers and
preview behavior remain to specify against the actual browser/proxy stack. Private
no-store responses at both hops must prevent unauthenticated cached delivery. Do not
forward provider redirects or arbitrary headers. Signed direct uploads are unchanged.

## Concrete existing-schema constraints

[Current objects migration](../../../../services/content-service/migrations/versions/0001_initial.py)
uses `(org_id,id)` keys, per-org digest uniqueness and org RLS. The
[identity trigger](../../../../services/content-service/migrations/versions/0002_immutable.py)
forbids changing org/ID/digest/size/type. The
[audit migration](../../../../services/content-service/migrations/versions/0003_audit.py)
uses the same composite scope and FK. Adoption must preserve all three consistently;
it cannot be an unchecked UPDATE of org_id. The existing
[provider](../../../../services/content-service/provider.py) returns signed read URLs;
its verification stream is not an implemented browser download adapter.

Inventory selected source partitions/objects/events/associations and verified sealed
locators before mapping them to PtS application ownership. Do not adopt every legacy
organization's objects as PtS. Unknown owner, duplicate identifier, inconsistent byte
identity or unexpected association blocks adoption for explicit resolution. Historical
events retain their original scope/actor evidence alongside the adoption mapping; do
not rewrite history to imply it always used application scope.

Preserve existing verified bytes and source associations without copying per account.
Rehearse clean/adopt/mismatch/failure and recovery on synthetic fixtures; use ADR-0020
maintenance if incompatible. No application startup migrations, automatic destructive
rollback or production data changes. The real deployed inventory remains unverified.

## Delivery boundaries — approved 2026-10-06

1. **E1-CONTENT-READ:** Content-owned ownership/adoption and authenticated streaming.
   Depends on ENV, established Identity actor/service conventions and the resolved
   Content schema/credential/proxy contracts. Can prove its service boundary with a
   restricted synthetic caller; it does not depend on future PtS UI or Leave E4.
   Supplies owner-scope/metadata/restricted-role/byte-identity/streaming/failure evidence.
2. **E1-PTS-ADOPT:** PtS's individual access and existing corpus paths consume completed
   ACCESS-B and CONTENT-READ. Includes browser/API/read/export/documents, owner-local
   corpus migration/import configuration, current launcher client integration and
   coordinated activation/recovery. Therefore follows DISCOVERY and LAUNCHER as well.
   Proves zero-membership real-stack reads, preserved corpus/source associations and
   independent operation grants without a future Leave dependency.

User approved placing CONTENT-READ and PTS-ADOPT after LAUNCHER and before WRITE/REF,
preserving the existing relative order. The current sequence now contains 23 items. Their exact DDL, transfer limits, preview
transport and executable checks still determine final sizing; split further only if
concrete implementation scope requires it. No new epic or future PtS org feature.

## Remaining gates and impacts

Select actual ownership DDL/RLS and collision mapping, actor/credential bootstrap,
typed read metadata/errors and limits, browser auth/preview mechanism, ranges/conditionals,
transfer/concurrency budgets and deployed proxy timeouts. Exercise provider reads against
fixed byte identity and verify large existing PtS source files without whole-file buffering.
Existing 10 MB Leave attachment limits must not accidentally replace PtS's larger source
support. Upload/finalization/cleanup regressions remain mandatory with shared schema changes.

Scaffold: promote proven server stream and typed ownership/error clients with tests;
shared UI uses existing download/preview feedback, no technical ownership picker.
Agent context already links ADR-0054/0055; docs and owner runbooks/traceability update in
the same items. Accepted ADRs unchanged. No application implementation or runtime results.

## Browser transport proposal — 2026-10-07

**For discussion; not a selected auth implementation or deployment change.** Existing
PtS web request() attaches a bearer through fetch; its deployment manifest exposes a
same-origin /pts proxy. Native links/PDF resource requests do not inherit the custom
Authorization header from that helper. A protected URL alone is insufficient for the
normal browser download/open flow.

Recommend an application-specific Secure, HttpOnly cookie for authenticated file requests,
bound to the existing account/session. No second sign-in and no token in download URLs.
The cookie is authentication transport, not a file permission grant: the API must still
verify current session/account and domain authority on every file/HEAD/range request.
Do not issue a standalone download ticket that keeps working independently of current
account authorization. Content retains its restricted service boundary.

Prefer host-only scope and an appropriate SameSite policy; do not share a domain cookie
across all Boabab apps. Cookie-backed reads require origin/fetch-metadata and CSRF policy
appropriate to their endpoints, plus anti-cache rules; HttpOnly alone is not an
anti-CSRF mechanism or protection from a compromised app. Session establishment/update
must authenticate the existing bearer and reject spoofed or cross-site establishment.
Logout/account switch must clear/revoke the file-auth context; old PDF tabs must not read
under a former account. Expired context denies the new request and provides a recoverable
return through the app; no signed URL fallback or silent account switch.

The exact adapter remains a readiness choice: supported existing server-auth integration
versus a minimal server-managed file-session binding, token validation/renewal/revocation,
cookie attributes and endpoints. Do not silently build a second refresh-token system or
convert every business API to cookies as part of a download story. Do not promise native
viewer renewal behavior until the browser integration is tested.

Alternative considered: bearer fetch followed by a Blob URL. This can serve bounded
small downloads, but does not by itself provide a native streamed download/range flow
for the existing large PtS source files. Do not make full-file JavaScript buffering or
browser-specific filesystem APIs the general requirement across supported browsers.
No client-side viewer/library is selected without a demonstrated need.

### Hosting feasibility gate

Netlify documents a 26-second proxy rewrite timeout. Existing larger PtS source transfers
therefore cannot be assumed safe through that path. Verify whether the actual limit and
route permit supported transfers, including slow clients and range/resume. If unsuitable,
select a route to the existing app API host that supports bounded authenticated streaming,
with the correct origin/cookie/TLS policy; this may require deployment routing changes.
No hostname/proxy replacement or production modification is approved by this proposal.
Never weaken authentication or issue a bearer storage link to work around a timeout.

Sources checked 2026-10-07:
- [MDN Fetch credentials](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)
- [MDN Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie)
- [Netlify proxy configuration limits](https://www.netlify.com/knowledge-base/how-to-configure-redirects-headers-and-env-vars-in-netlifyto/)

PTS-ADOPT owns browser cookie/session integration and deployed-route proof; CONTENT-READ
owns upstream streaming contract. Both require explicit timeout/size/concurrency/range
bounds and disconnect tests before delivery readiness. The 23-item sequence remains;
this proposal introduces no auth code, cookie/session store or infrastructure change.

## Direct application download ingress — direction accepted 2026-10-07

The user approved resolving hosting limits before delivery rather than waiting for
production failures. Use a dedicated application download origin routed directly to the
existing backend gateway, bypassing Netlify for private file bytes. Netlify can continue
serving static frontends. This approves routing direction and the secure-cookie approach,
not DNS ownership, a deployed hostname or a new standalone download service.

Concrete target proposal for planning:

| Frontend | Download origin | Gateway destination |
| --- | --- | --- |
| `https://pts.boabab.com` | `https://files.pts.boabab.com` | Existing PtS API's authenticated document endpoints |
| `https://leave.boabab.com` | `https://files.leave.boabab.com` | Leave API's authenticated attachment endpoints when E4 is delivered |

Proposed names require DNS/certificate feasibility validation before configuration.
No Scribeswell file origin is needed for its current public reader. Future personal
files would use their own approved app-specific origin/contract.

Browser → app-specific download origin → existing gateway → owning application API →
private Content service → storage. The returning stream follows that path back. Content
and storage credentials remain private; no direct public Content route or signed browser
read URL. This is an alternate ingress to the same owning API, not another policy engine.

### Cookie and route binding

Establish file authentication using an authenticated browser request to the download
origin. Its narrowly exposed session endpoint must validate the existing login and exact
frontend Origin; allow credentialed CORS only for that app's configured frontend. Cookies
are Secure/HttpOnly and host-only on the download origin, with explicit SameSite policy;
no parent-domain cookie shared across apps. The sibling HTTPS origin is cross-origin but
same-site in the planned Boabab layout; do not confuse SameSite with an Origin allowlist
or CSRF defense. Native file navigation then uses that host's cookie, without a URL token.

The concrete session binding/renewal/lifetime/CSRF mechanism is still a contract to select;
no independent refresh-token store is assumed. Logout/account switch must revoke/clear
that origin's context and deny stale-account use. Credentialed session establishment and
cleanup need exact method/route allowlists; current PtS GET/OPTIONS-only exposure does
not already implement them. Ordinary document GET/HEAD/range checks remain current and
read-only; supported native viewer behavior must be verified, not inferred from fetch.

### Existing gateway gaps to implement in the owning renderer

[render_gateway.py](../../../deployment/render_gateway.py) currently renders one public
API hostname and one frontend CORS origin, common upstream connect/send/read settings
of 5/30/30 seconds, and no per-download buffering configuration. Its TLS validation also
checks the single supplied API hostname. These source settings are not live inspection
or proof of actual total/idle streaming limits.

Extend owner manifests/renderer and generated-output tests for per-app download hosts,
TLS coverage, narrow session/file methods and credentialed origins, explicit response
buffering/temporary-file policy, independent transfer limits and deployment/drain behavior.
Never hand-edit generated gateway output. Read/send timeout semantics, API server/provider
limits and total stream deadline must be defined at each hop; merely increasing a timeout
does not prove bounded memory or correct cancellation. Keep ordinary API budgets intact.
No broad wildcard CORS/host routes or blanket public Content exposure.

### Required evidence before activation

- Resolve route/certificate and origin/auth adapter before PTS-ADOPT implementation
  readiness. During authorized delivery, verify the actual gateway path before release.
- Use a synthetic 128 MiB file matching current Content's upper size bound and existing
  PtS large-source support. Throttle delivery to approximately 1 MiB/s to produce a
  roughly two-minute transfer, clearly exceeding 26 seconds. These are test inputs,
  not performance promises. Verify complete byte identity and bounded per-process memory
  without storing the whole response in the app or gateway. Final concurrency/resource
  bounds remain to select against the deployment capacity.
- Verify initial response delay, idle pause, total deadline, disconnect, upstream failure,
  graceful deployment interruption and supported range/resume. Test both successful long
  transfer and intentional bounded failure; an indefinitely open stream is not success.
- Verify copied route without authentication, wrong account, revocation before a new
  range/HEAD request, cookie expiry/logout/switch, wrong origin and cross-app cookie
  isolation. Verify no unauthenticated CDN/proxy response or storage URL exposure.
- Exercise real desktop and mobile download/open paths in the agreed browser coverage;
  a command-line stream proves neither cookie handling nor PDF viewer behavior.

Use isolated/nonproduction fixtures before activation; no production mutation or DNS/TLS
installation is authorized by this plan. Failure to prove the routed stream blocks the
private-download release. Do not defer to incident handling or restore signed read URLs
as a fallback. PTS-ADOPT owns route/browser integration; CONTENT-READ owns upstream stream
behavior. Deployment owner supplies reusable manifest/renderer and recovery evidence.

## File-authentication lifecycle proposal — 2026-10-08

**Behavior approved by the user, 2026-10-08; implementation mechanism remains open.**
Reuse the existing Supabase sign-in and its refresh owner. File
authentication is a transport binding for native browser requests, not another login,
independent identity provider or long-lived refresh-token system.

| Event | Proposed behavior |
| --- | --- |
| First private file open | The signed-in app establishes file-origin authentication through the exact-origin, bearer-authenticated setup request. Resolve the account/session server-side; never accept user/actor identity from the body. Ordinary opening requires no additional login. |
| Normal renewal | Existing app auth renews its token; a same-account/session update refreshes file authentication. It cannot extend access past the underlying verified session/token validity. No second refresh token stored or independently renewed by the file adapter. |
| New file/HEAD/range request | Verify current authentication, account/app/capability and domain association, then Content service/ownership checks. Cookie presence alone never grants access. |
| Expired file authentication | Refuse new bytes. While the app is open, renew through existing auth and retry a safe read for the same account; if native viewer recovery cannot occur transparently, return through the app to reopen. Never redirect a binary/range response to a login HTML page and call it a successful file. |
| Logout | Stop browser requests and invalidate/clear file-origin authentication as part of the existing logout path. Existing auth performs its configured session sign-out. Do not claim file logout succeeded if its server-side cleanup failed; no signed URL fallback. |
| Account switch | Invalidate old file context and clear old UI state before enabling the new account's file actions. Delayed old establishment/renewal responses must not reinstate the old account. Existing preview contexts must not silently change account. |
| File-origin/auth service unavailable | Explain temporary failure and retry through the app; do not use stale positive authorization or expose storage URLs. |

### Minimal adapter direction and explicit security gaps

Prefer a server-issued HttpOnly transport of the existing short-lived access credential
if it can satisfy the above, rather than immediately adding a second session database.
Such a cookie may carry the existing access token after server verification; it never
contains a refresh token. Its expiration cannot outlive that token. An opaque
server-managed binding is an alternative only if concrete logout/account-switch/viewer
requirements require it; do not implement both mechanisms or a generic session framework.
The exact storage mechanism is not selected by this behavior proposal.

Signature/expiry checks alone are insufficient to claim immediate session revocation.
Supabase documents that revoked-session access JWTs remain valid until expiry. Its
server-side guide distinguishes remote user verification from local claims validation.
Use the existing current-authentication owner to verify supported revocation behavior
and test it with real provider sessions, including an old token attempting file-context
establishment after logout. Do not let a cleared cookie be recreated from revoked-session
authority, or promise immediate revocation based only on auth.signOut() returning.
Exact enforcement adapter/propagation bounds must be settled before readiness; no broad
Auth-table credentials are granted to every application to solve this.

Cookie writes are shared across tabs and response arrival is asynchronous. A frontend
promise cancellation alone does not prove an old Set-Cookie response cannot win. Specify
and test ordering for delayed setup/renewal versus logout/switch, with current-session
validation on every read. Bound old viewer context to the initiating account so a new
cookie cannot silently turn an old preview into a different account's view. Any context
reference in a route is non-authorizing and contains no token or sensitive form data;
exact representation remains an integration contract. The current app's UI account epoch
is useful but does not by itself protect a native viewer or server cookie mutation.

An already-started stream follows its declared transfer/in-flight rules; this proposal
cannot recall bytes or guarantee instant cancellation. New requests, including resume,
authenticate again. Do not restart partial downloads invisibly as new full transfers.
A closed original app tab does not make a PDF viewer a second token-refresh owner; it
may need reopening from the app after authentication expires.

Source verification, 2026-10-08:
[Supabase sign-out](https://supabase.com/docs/guides/auth/signout),
[sessions](https://supabase.com/docs/guides/auth/sessions),
[server-side auth guidance](https://supabase.com/docs/guides/auth/server-side/advanced-guide).
These are provider behavior references, not evidence the repository integration passes.

PTS-ADOPT owns lifecycle/browser integration with existing Access/auth boundaries;
CONTENT-READ does not own browser sessions. Exact cookie/CSRF attributes, response races,
provider revocation and supported viewer transport remain concrete readiness inputs.
No timeout value, schema, cookie, token store or application implementation changed here.


## Download and preview behavior — proposed 2026-10-08

**Accepted with browser/application boundary clarification, 2026-10-08.**
These are technical acceptance criteria for the existing download integration. The
browser owns its download UI, PDF viewer and resume offering; our endpoints supply
authorized streaming, suitable Content-Type/Content-Disposition/length headers and
partial-read support. Application UI owns Open/Download actions and relevant errors.
Browser tests establish interoperability, not a custom viewer or download manager.

This refines ADR-0038/0055 within CONTENT-READ and PTS-ADOPT; it does not add a story
or expand Leave E1 into attachments. Leave E4 consumes the proven shared behavior.

- **Ordinary download:** use the browser's download flow, with a safe filename and
  accurate type/length. Stream the exact finalized bytes with bounded buffers through
  the approved direct gateway path; no full-file JavaScript buffering requirement.
- **Preview:** use the browser's native PDF viewer where supported. Keep a Download
  action available; do not promise identical mobile/desktop viewer behavior or build a
  custom viewer. Other formats download unless explicitly approved for inline viewing;
  uploaded active HTML/SVG must not execute as trusted application content.
- **Partial reads:** support one byte range per request, including open-ended and suffix
  ranges, for ordinary PDF navigation and resumable downloads. Every request follows
  the same current authorization checks before exposing bytes or size metadata.
  Browser resume availability is not guaranteed; a user can restart through the app.
- **Stable identity:** bind all full/partial reads to the same finalized content identity
  and representation. A replacement gets a new identity. Use a strong representation
  validator for safe conditional resume; never splice bytes from different versions.
- **Failure:** before streaming, present a safe error with retry through the app.
  After streaming starts, abort an incomplete response on failure; no appended error
  text, false completion notification or invisible restart of the whole file. A retry
  is a newly authorized read. Stop upstream work when the downstream disconnects.
- **Privacy:** preserve private no-store responses, safe response headers and no provider
  URL exposure. Resume/preview is not an exception to logout, account isolation or
  current permission checks. Already received bytes cannot be recalled.

Acceptance examples: authorized PDF navigation requests the correct byte intervals;
interrupted download resumes only against the same representation while access remains
valid; revoked access denies the next partial read; provider failure produces a detectable
incomplete transfer; cancel closes upstream resources; non-previewable content downloads.
Verify these with the existing 128 MiB throttled fixture and supported real browsers.

HTTP implementation follows [RFC 9110 range and conditional request semantics](https://www.rfc-editor.org/rfc/rfc9110.html#name-range-requests).
Before readiness, specify the exact 200/206/416, HEAD and If-Range behavior, malformed and
multiple-range policy, safe header allowlist, representation validator, and explicit
per-hop transfer/concurrency budgets. This behavior proposal does not claim those wire
contracts or browser tests are complete. Multi-range response generation is not proposed.

Scaffold impact: reusable stream adapter and contract fixtures with the first consumer.
Shared UI: existing Open/Download and safe retry feedback; no new download manager.
Agent context and ADR impacts: existing ADR-0038/0054/0055 instructions suffice; no change
to accepted decisions. Documentation and test traceability remain with the owning stories.

## Leave E5 association reference and target extension — 2026-10-25

E4 remains the attachment association/protection owner. These selected types bind E5
submission/on-behalf/correction consumers; they do not create a second upload/cleanup
pipeline, browser Content control plane or request table in Content.

Select an E4 confirmed association reference `{association_id, expected_revision}`:
association_id is an actual Leave-owned UUID; revision is a positive canonical decimal
string. E5 `attachment_refs` is a duplicate-free array of these references, at most three,
not raw content IDs, provider paths or browser claims of safety/readiness. The actual
E4 server association resolves immutable content identity and verified byte/version/size/
type/ownership/readiness. Enforce accepted three-file/20 MB total/10 MB per-file and type
rules using verified owner metadata. E4's actual allowed media types remain its source.

The actual E4 Leave association target is a closed union:

| Target | Exact owner scope / lifecycle |
| --- | --- |
| `draft` | org/employment/actual draft ID and current editable lifecycle; existing 4.4 contract |
| `on_behalf_input` | org/target employment and server-issued E4 attachment context ID, bound to initiating authorized account/actor and explicit on-behalf target scope |
| `request_correction` | org/employment/request/base cycle/actual open correction ID; current employee correction authority and revision/lifecycle |
| `request_cycle` | org/employment/request/actual submitted cycle; retained actual association evidence and current authorized history read |

E4 creates only its existing first-use draft branch in 4.4. Actual 5.12-A/B adds the
on-behalf branch with the E4 owner; actual 5.20-A/B adds correction and consumes existing
submitted association history. If a staging context is required before an on-behalf request
exists, it stores only attachment target/initiator/protection/lifecycle—not another employee
draft, on-behalf form payload or generic admin draft system. Its exact association/protection
storage reuses actual E4 lifecycle primitives and is sized with that first consumer.

Current on-behalf/attach scope is checked at context creation and each association/use;
source target change cannot retarget prior context/files silently. Correction refs are
bound to their actual request/base cycle; closed input cannot accept a late association.
Existing files retained on a prior submitted cycle are not editable prior-cycle state.
Any authorized reuse adds the actual new-cycle association to the same immutable content;
no re-upload, byte mutation or Content ownership transfer. Actual E4 reuse policy and
current source/retention checks still apply.

On own submit, enumerate the actual confirmed editable-draft associations on the server;
a second client list cannot replace saved draft truth. On-behalf/resubmit references must
match their actual editable context and reviewed selection. The local submitted cycle's
exact association list/linkage and input closure commit with the owning request operation.
Required Content readiness/protection observations occur outside local business locks;
E4's existing in-flight lifecycle fence prevents cleanup racing the protected local commit.
Do not create the cycle then "fix up" unprotected file links in a second transaction.

Original confirmation/submission retries reuse operation/content/association identity and
E4 protection evidence. Unknown outcomes are not proof of abandonment. Reclaim only after
E4's authoritative association reconciliation and bounded in-flight protection; no blind
TTL deletion or late recreation after release. Losing E5 receipt response does not require
another upload. Medical provision/readiness status is independent of sensitive metadata/
byte permission; ordinary approver/manager/temp scope alone still cannot read those files.
Retained cycle/history reads use current app/document permission, authenticated app routes
and Content ownership checks under P-0054/0055, never exposed bearer read URLs.

Actual E4/Leave consumer acceptance covers wrong org/target/initiator, stale association,
duplicate refs, simultaneous file-size limits, cleanup-versus-submit, late closed-correction
confirmation, lost on-behalf submit response and authorized same-content cycle reuse.
Reference 4.4/4.13 association/byte/cleanup tests; actual 5.12/20/32-H add producer composition
without implementing another pipeline. Full E4 timeout/storage/OpenAPI test artifact
closure remains its first-consumer/G6 work, not proof from this typed extension. No runtime
code, tests, migrations, grant changes or implementation/readiness authorization.

## Concrete native-file authentication adapter — technical planning candidate 2026-10-25

This selects one minimal model for the consolidated review, replacing the earlier open
JWT-cookie-versus-opaque-session alternative. It extends the existing sign-in/refresh/
logout owner; it does not introduce a second refresh token or whole-application cookie
conversion. PTS-ADOPT implements the first browser consumer; Leave 4.7 reuses it.

Use the existing verified short-lived access JWT in a file-origin Secure, HttpOnly,
host-only cookie. Never store a refresh token there. Cookie expiration is no later than
the access-token expiration. The file origin is the application's direct API origin,
with HTTPS, an exact origin allowlist and credentialed CORS only for its owning web UI.
Use SameSite=Lax for the selected same-site web/API deployment; a cross-site deployment
is unsupported until its explicit cookie/CSRF transport is qualified. Do not silently
relax attributes to make a different hosting layout work.

Setup/renewal is an exact-origin POST authenticated by the existing access bearer. It
verifies issuer/audience/signature/expiry, account and current provider session before
setting the cookie. Unknown origins, ambient-cookie-only setup and body-supplied user
identity are rejected. No bearer appears in a URL, link or context reference. File GET/
HEAD/range routes cannot mutate authentication or renew it independently.

Each native preview/download route contains an opaque non-authorizing context ID. Its
short-lived server record binds the verified account, Auth session ID, application,
resource reference, permitted presentation and expiration. Every file request compares
that account/session with its current cookie, then repeats current Access, domain and
Content checks. The context is never sufficient authority. A different account's new
cookie therefore cannot turn an already-open old PDF viewer into that account's view.
Context records contain no draft text or provider credential, expire with their session
binding and can be invalidated by the existing logout path. Renewal for the same verified
session may extend the context to the new short-lived token's expiration.

### Current-session enforcement and delayed responses

Identity supplies a narrow restricted-service current-session check. It validates the
forwarded access credential and current account, then checks that its verified subject
and `session_id` still identify the same live provider session. Keep this provider access
inside Identity's narrowly privileged routine/adapter; application runtime roles receive
no general Auth-table SELECT or provider administration key. No positive session cache
may survive logout between new file requests. A two-second check deadline fails closed
as temporarily unavailable; denial and inability to verify remain distinct typed outcomes.
No business lock is held while checking Identity or Access.

Supabase documents that sign-out removes the affected session rows while already-issued
JWTs can remain valid until expiry, and explicitly describes checking the JWT's session
ID against `auth.sessions`. This supports the selected server check; it does not prove
our integration. See [Supabase sessions](https://supabase.com/docs/guides/auth/sessions)
and [sign-out](https://supabase.com/docs/reference/javascript/auth-signout), consulted
2026-10-25. The routine, app adapter and following race behavior are our design inference
and require actual provider acceptance during delivery.

Account switching must complete the existing provider's local-session sign-out for the
old account before enabling the new account's file context. This revokes that session,
not every other device. Logout also invalidates its file contexts and clears the cookie.
If remote sign-out or context invalidation cannot be confirmed, do not claim logout/
switch completed or enable a replacement file context; preserve the established recovery
path. Existing app auth remains the only owner of provider sign-out and refresh.

A delayed old setup/renewal response may physically arrive after logout or switch and
write an old cookie. Signature validation or a frontend epoch cannot prevent that. The
new request's live-session check rejects the revoked old session even then. That response
cannot create a live session/context or restore old authority. An old cookie can cause a
safe temporary authentication failure for the new account; the app re-establishes its
current same-session cookie and reopens the authorized file. Do not promise ordering of
Set-Cookie responses or silently retry an unsafe action. Old-context/new-cookie and
new-context/old-cookie combinations both fail their account/session comparison.

Already-started streams retain their declared bounds; this cannot recall delivered bytes.
A new range/resume always authenticates again. If the originating app has closed and its
credential expires, the native viewer returns through the app to reopen; it never becomes
a refresh owner or receives login HTML disguised as PDF bytes.

### First-consumer implementation and acceptance ownership

- E1-ID-B adds the narrow current-session adapter/routine and tests credential subject/
  session matching, revoked/unknown sessions, denial versus outage and restricted grants.
  It reuses the actual Identity owner and its controlled migration/operator infrastructure.
- E1-PTS-ADOPT owns cookie setup/renewal, same-site origin configuration, current-session
  consumption, context binding, existing logout/account-switch integration and native
  browser proof. E1-CONTENT-READ remains a service-to-service bytes/ownership boundary.
- 4.7 consumes that proven transport and adds actual Leave resource/document authority;
  it does not implement another session checker or provider login.

Acceptance must delay a real old setup response across successful logout and account
switch, attempt setup with the old JWT after revocation, reuse an old viewer under a new
account and issue new GET/HEAD/range requests after membership/capability changes. Verify
all denial/outage cases before bytes/metadata escape, and exercise expiry with the app tab
closed. Provider mocks and UI epochs do not prove those cases. Actual browser cookie,
Entra/Supabase sessions, deployed origins and ingress remain delivery evidence at these
owners; writing this candidate does not execute or claim that evidence.

Scaffold: promote the proven session-check/cookie/context client and fixtures once, keep
origin/configuration and generated errors synchronized. Shared UI: reuse file-open/error/
re-authentication return behavior. Agent context: existing current-authority/privacy rules
suffice. Documentation: exact credential role, route/configuration, browser races and
recovery evidence. Accepted ADRs unchanged; no private signed-read URL fallback.

### Initial ingress and stream budgets — technical planning candidate 2026-10-25

For the already-approved app-specific direct file ingress, select a 5-second connect
budget, 30-second upstream idle budget, 60-second gateway idle budget and 15-minute
whole-response ceiling. The gateway path must support streaming/backpressure and disable
response buffering/caching for these private routes; no Netlify proxy rewrite carries
file bytes. Generator-owned gateway configuration and the actual application manifest
must agree. A provider failure cannot be hidden by a longer downstream timeout.

Use 1 MiB application buffers, at most 16 concurrent streams per API instance and at
most two per verified account; reject excess before headers with the standard typed
capacity response and Retry-After. These are initial qualification budgets, not a new
128 MiB business file limit. Test a representative 128 MiB PtS source at 1 MiB/s, slow
clients, disconnect, 17th-stream capacity, two-account isolation and recovery after a
partial transfer. Leave retains its smaller attachment limits. Record peak process
memory/connection occupancy under that workload; buffers alone are not a total RSS claim.

Support authorized GET, HEAD and one byte range, including bounded/open-ended/suffix
forms. A range is always against the same finalized representation with stable opaque
ETag, correct 206/Content-Range and length. Unsatisfiable ranges return 416 after current
authorization; reject unsupported multiple ranges before bytes. HEAD uses the same
metadata authority and sends no body. Standard If-Range behavior must be covered with
the native viewer; a representation mismatch cannot splice bytes from another object.
Return safe allowlisted type/disposition/length/range/cache headers only, sanitize display
filenames, and use private no-store plus gateway cache bypass on successful and failed
private responses. After headers, abort incomplete bytes instead of appending an error.

These values are build/qualification inputs for CONTENT-READ and PTS-ADOPT/4.7, not
claims that current deployment configuration or provider limits already satisfy them.
A failing actual target must be corrected compatibly before activation. Hosted manifest,
DNS/certificate/secret values are bound by the authorized release rather than invented
in planning; selected route direction is already approved.

## Consolidated adoption — accepted 2026-10-26

The user explicitly approved the completed consolidated planning package. The reviewed
choices and bounds in this contract are adopted under [the acceptance decision](../decisions/0064-approved-onboarding-continuity-and-content-contracts.md).
Earlier candidate/pending-review wording is historical and superseded for these choices.
Actual implementation and provider/database/browser/recovery proof remain delivery work.
The user requires a new Codex session before implementation; no runtime action here.
