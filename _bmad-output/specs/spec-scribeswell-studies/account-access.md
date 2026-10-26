# Account-access contract design

Derived from the feature decision log. **Status: personal enrollment/current checking delivered by the Access/Identity owner; recipient/invitation protocols remain proposed.** Implements D-1/Q-1 under architecture AD-1/AD-2. Scribeswell now consumes ordinary personal enrollment/checking in its opt-in notes runtime; production and live owner/provider qualification remain open.

## Owning contracts and required extension

[Application admission](../../../platform/docs/architecture/contracts/application-admission-and-discovery.md) owns capability registration, account grants, caller policy and current checks. [Identity/Access execution](../../../platform/docs/architecture/contracts/identity-access-execution-substrate.md) owns actor evidence, restricted projections and command authority. Existing operator-only `account_grant.assign` and `account_actor.ensure` do not authorize a browser or Scribeswell runtime to provision either record. Existing org-only `/v1/check` is insufficient.

The agreed mechanism uses a narrowly authorized Access enrollment operation for this feature. It uses one fixed registered account-scoped studies-use capability, never a caller-selected capability, account, actor or organization. The [owner contract](../../../platform/docs/architecture/contracts/scribeswell-study-enrollment.md) and adopted [runbook](../../../services/access/STUDIES-ENROLLMENT.md) own the delivered enrollment/current-check wire, identity preparation, errors and bounds. Consume them over HTTP; Scribeswell needs no second Identity adapter. Recipient resolve/verify, address normalization and invitation qualification remain proposed. Decision236 supersedes earlier implementation-gap statements for ordinary enrollment/checking only.

## Independent account creation

The public reader offers standalone Sign in / Create account entry without requiring
any study selection or personal action. Reuse the existing authentication owner,
account identity and supported verification flow, not an application-specific account
registry. Registration and account sign-in remain distinct from Studies enrollment;
completion alone creates no study, accepts no invitation and provisions no Studies
capability. The reader can return to public reading after creating an account.

The inspected baseline [Topbar](../../../apps/scribeswell/web/src/components/layout/Topbar.tsx)
opens [SignInDialog](../../../apps/scribeswell/web/src/components/auth/SignInDialog.tsx)
independently; it previously supported password sign-in only. The bounded standalone
consumer contract below resolves that entry's integration choices. A future signup
started by a Studies action must additionally restore its validated protected
context after current authority checks; standalone signup restores public reading.

### Standalone Auth consumer contract — bounded delivery

Use the existing Supabase Auth client/project and `pts-auth` session key. Explicit
Create account invokes SDK `auth.signUp({email,password,options:{emailRedirectTo}})`;
Sign in retains `auth.signInWithPassword`. Browser business-data access does not
change. The Auth provider owns registration, email verification and session issuance.
Neither a returned user object nor a confirmation notice proves verified identity
or Studies authority.

| Provider outcome / reader action | Consumer obligation |
| --- | --- |
| Signup success without session, including obfuscated existing account | Clear password and show neutral check-email guidance; do not claim creation, delivery or verification. Offer Sign in and Continue reading. |
| Provider session returned / valid signup callback | Let the existing shared-session listener establish session; remain in public reading. No app grant, actor, study or invitation operation follows. |
| Disabled signup, weak password, invalid email, rate limit, unconfirmed login or invalid credentials | Map typed provider codes to safe actionable inline messages; never display/log raw provider text. |
| Thrown/network/unknown failure | Settle pending UI with safe Retry guidance; bound provider fetch to 15 seconds, with no automatic application retry. Cancellation cannot promise rollback. |
| Close, Escape or mode switch | Retain public reader/analysis context, clear secrets on fresh entry and isolate late dialog results. Keep modal focus contained; return focus to the entry trigger. |
| Invalid/expired, incomplete or provider-rejected callback | Show safe dismissible sign-in guidance, observe SDK initialization failure and scrub the complete callback parameter set. Keep public reading/current valid session usable; never expose the callback description or restore old session storage. |

Construct `emailRedirectTo` from the current origin and fixed configured reader
application root (including nested `/scribeswell/` hosting). Carry only validated
public `book/chapter/verse` and comparison keys; omit duplicated, malformed or
oversize values and arbitrary return targets, private context and fragments. Never
derive a redirect origin/path from a query parameter. Existing implicit Auth callback
handling remains SDK-owned; credentials are not copied into return metadata or logs.
The adopted four-passage contract now defines the bounded new `reader` return
extension: reuse its closed codec for complete public references/index only;
reject invalid supplied new input without legacy blending. Its intercepted signup
qualification is recorded in event353; event377 additionally qualifies the shared
callback projection against malformed-tab credential resurrection. This is browser
consumer proof only. Private return context and
live provider activation remain separately gated.
Keep only callback-presence booleans during startup. Qualify SDK callback rejection
without letting it erase an unrelated current session; any transport adaptation is
limited to that startup verification window. Ordinary user/session rejection and
concurrent sign-out retain owner semantics. Scrub access/refresh/provider tokens,
code, expiry/type and error fields on completion, including mixed error/token URLs.
This slice bounds syntax using the existing 39 public OSIS book IDs, positive
decimal chapter values up to 150 and verse values up to 176. It does not introduce
the D-2 versification catalogue or claim those maxima are valid for every book;
the existing reader/API still validates actual available passages.

This consumer contract can be implemented and tested without Access enrollment or
app-factory work. Its owning configuration currently disables public signup:
[checked-in config](../../../supabase/config.toml) and the
[deployment generator](../../../platform/deployment/dev.py) are evidence, not files
to change in this slice. Live activation still requires owner-controlled signup
enablement, required email confirmation, exact allowed reader callback URLs and
real mail/verification/expired-link qualification. Provider errors remain truthful
when those prerequisites are absent. Browser provider fixtures prove the consumer
only; they cannot close full ST-36, protected-context restoration or D-1.

Modal background isolation includes the header and reader, with prior inert states
restored on close. Pending explicit Auth requests expose form busy state and a safe
live status; successful late Auth completion still establishes the real shared
session after cancellation/mode switch. Cancellation is not a provider rollback.

SDK references checked for this contract: [signUp](https://supabase.com/docs/reference/javascript/auth-signup),
[implicit callback](https://supabase.com/docs/guides/auth/sessions/implicit-flow) and
[redirect allowlist](https://supabase.com/docs/guides/auth/redirect-urls). Installed
SDK/lockfile remain implementation version authority; no provider upgrade selected.

## Entry and enrollment

1. Anonymous Bible reading remains public. The first deliberate study action offers the same standalone sign-in/account-creation experience and returns the same verified reader to that action's context. Returning does not accept an invitation, share or delete content automatically.
2. Scribeswell calls Access with its restricted service identity and the current end-user bearer. Access verifies allowed caller/operation, current account, required verification and global protected-app availability. Browser JWT roles/email strings are not evidence of current eligibility. No organization, employment or PtS prerequisite is introduced.
3. Enrollment is constrained to that current account and fixed capability. Access owns any initial assignment through a dedicated restricted command path; it does not grant Scribeswell generic assignment/operator privilege. Concurrent identical first use creates at most one grant and one initial-assignment event.
4. Actor resolution/setup stays Identity-owned through the Access integration boundary. If a valid account lacks its actor mapping, only a separately authorized, idempotent Identity setup path may establish it. No reader-selected actor, synthetic Auth account, cross-owner write or assumption that the delivered operator CLI is a runtime API. Until owner setup is available, fail truthfully without claiming enrollment completed.
5. Current account and app eligibility are verified before local write locks. Local assignment rechecks retained grant state and registered policy atomically; restarting execution requires fresh external evidence within owner-defined bounds. Do not promise atomic remote revocation.

| Current state | Enrollment result |
| --- | --- |
| Eligible verified account, no retained grant | Create the fixed account grant through the restricted owner command. |
| Eligible account, active grant | Return unchanged; no duplicate assignment or audit event. |
| Retained revoked grant or current suspension | Deny; no automatic regrant on sign-in, enrollment retry or app re-enable. |
| Globally disabled protected app | Deny protected use without deleting writing/grants or disabling public reading. |
| Missing/invalid authentication or verification | Require the appropriate sign-in/verification; no grant. |
| Identity, Access or required setup unavailable | Report unavailable with retry; do not call this a revocation or grant access. |

Enrollment retries reconcile a committed outcome without re-executing assignment. Current access is rechecked before protected use, so an old successful receipt cannot restore or authorize a now-revoked grant. Later deliberate regrant remains an authorized owner operation. Recreated accounts have a new identity and inherit no old studies, shares or grants by matching email/person.

## Protected actions after enrollment

- Each protected request requires current account-capability authorization and Scribeswell's current resource/visibility rules. The account capability alone grants no access to another person's study. Study ownership controls editing and sharing; accepted resource shares grant view access only; private responses remain owner-only.
- Scribeswell trusts only the approved Access decision contract for account/actor, exact capability and scope evidence. It never accepts caller-supplied overrides. Evidence has a bounded executing-operation scope, not reusable indefinite authority. Identity claims are not permission claims.
- A fixed studies-use capability gates ordinary personal study functionality, including accepting an invitation; exact resource checks distinguish read, edit, copy, delete and share. No administrative capability or PtS/Leave authority is implied.
- Invitations retain their own recipient binding and explicit acceptance. Neither enrollment, sign-in, notification reading nor email-link possession accepts one. Pending target email is not an account linkage. Proposed recipient-proof wire is in the owner draft; provider qualification and expiry/reissue/accept/revoke concurrency remain D-1 delivery evidence.
- Launcher visibility remains governed by existing PtS access. This account grant does not add Scribeswell to a launch menu or create reverse PtS access.

## Recipient continuity — agreed policy

An invitation must reach the intended verified account without making an email
address a permanent identity or granting access from a forwarded link.

- Pending invitations require Identity/Access-owned evidence of the current
  intended verified address. A previously account-bound invitation cannot be
  reassigned by matching another account's email. Wrong-account handling offers
  the existing Switch account path; verification never accepts automatically.
- Accepted view access belongs to the stable account. That same account changing
  its verified email keeps its accepted library entry, subject to current access
  and explicit owner removal.
- Deleting/recreating an account or reusing its email never inherits its shares,
  studies or private responses. The owner must explicitly invite the new account.

The owner draft proposes pre-registration target resolution, account-bound proof
and local atomic acceptance. Provider-qualified email normalization, physical
privileges and binding/concurrent-claim evidence remain D-1 closure items. No
email-only account linkage or proof of implementation is introduced.

## Closure evidence

Use ST-01/ST-02/ST-17/ST-23/ST-26/ST-29/ST-36 and owner contract tests to prove zero-organization first use; repeated/concurrent enrollment; revoked grant plus old enrollment retry; app disable/re-enable; suspension and unavailable identity; missing actor setup; wrong service/target/capability; account recreation; forwarded/changed-email invitation; and access loss between enrollment and the next resource action.

D-1 closes only after the owner adopts the exact capability, enrollment and check schemas, restricted caller/command/Identity setup policy, safe error variants, execution/evidence and replay-retention bounds, verified-recipient proof and compatibility/release design. No grant, route, migration or new authentication provider is delivered here.

## Runtime qualification target and owner progress

Inspection of [services/access/main.py](../../../services/access/main.py) confirms
that the live provider call currently returns only an account UUID. It does not
supply the verified-address/recipient evidence proposed by the owner contract.
Its `/v1/check` requires `org_id` and allows only PtS permissions/callers. Neither
that adapter nor the legacy check can serve as proof of Studies eligibility.

Final-session reconciliation: separate KDG work now adds an organization-scoped
`/v2/check` in [organization_check.py](../../../services/access/organization_check.py).
Its request requires `OrganizationScope`; endpoint-name availability alone is not
the Studies account variant, enrollment or recipient protocol. Consume the exact
owner variants and qualification when delivered; do not supply a synthetic
organization or implement an alternative Access path. The legacy inspection above
records the starting baseline, not a claim that KDG made no subsequent progress.

The separate KDG platform implementation session owns Access delivery. This
Scribeswell session must reconcile its proposed requirements with the owner’s
delivered contract and evidence rather than implement a competing Access path.
D-1 closure must bind that reconciled contract to a current-account-only provider
adapter, restricted actor-preparation privileges, canonical account check and
exact shared error/evidence bounds. Qualify live-account verification independently
from email-recipient resolution: private self-study needs no recipient lookup,
while sharing must additionally qualify the full recipient protocol. Both remain
part of this feature; implementation sequencing grants no exemption from their
owning contracts or evidence requirements.


First-note dependency closure (decisions231–232): the adopted
[personal-notes contract](../../../apps/scribeswell/docs/PERSONAL_NOTES_V1.md#exact-access-owner-handoff)
records exact current-account/durable-actor, typed account Studies admission,
self-service enrollment and standalone signup activation dependencies. Access
commit f02bf84b1a3d3281fb06e91aba01f0057216511c supplies the personal owner contract
and qualified native implementation. App wire tests still do not grant authority.
Own notes need no recipient/notification lookup; sharing still does. No competing
Access or synthetic organization path is authorized.


## Bounded ordinary-note implementation

The app now consumes the delivered Access owner through a bounded server-only HTTP adapter and explicit browser enrollment proxy. Registration/public reading never enroll; no synthetic organization or competing Identity/Access implementation is introduced. Synthetic HTTP fixtures verify consumer binding, not live owner/provider readiness. Production consumer activation and recipient/invitation delivery remain gated; standalone signup is preserved. See the [delivery evidence](../../implementation-artifacts/spec-scribeswell-personal-notes-runtime.md) for exact tests and limitations.

Event247 adds [actual local owner integration evidence](../../../apps/scribeswell/docs/STUDIES_OWNER_INTEGRATION_EVIDENCE.md): fresh provider-admin-created synthetic accounts use real verification callbacks and the actual Identity profile hook in the same native database. Checking before enrollment returns the delivered missing-actor503 and creates no actor, membership, grant or study. Explicit enrollment then supports create/write/reload without organization or PtS prerequisites; current app disable denies subsequent protected actions and retries. This qualifies HTTP/domain integration through supported real-database dependency injection. Standalone signup remains required and unqualified because the wrapper disables it; no default startup/readiness or production activation follows. Event250 records all13 review findings addressed without deferral and the final patched-source native pass.
