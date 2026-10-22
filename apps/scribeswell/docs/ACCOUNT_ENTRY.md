# Standalone account entry

The product contract is [Studies account access](../../../_bmad-output/specs/spec-scribeswell-studies/account-access.md#standalone-auth-consumer-contract--bounded-delivery).
This delivery adds its standalone Auth consumer; it does not deliver Studies
enrollment, private notes or sharing. The [BMAD delivery record](../../../_bmad-output/implementation-artifacts/spec-scribeswell-standalone-account-entry.md)
contains exact test commands and results.

From the anonymous reader header, choose Sign in or Create account without opening
a study. Registration uses the same Supabase Auth account and shared `pts-auth`
session as existing sign-in. Cancel or Continue reading retains the public reader.
Without a returned session, the form offers neutral confirmation guidance; it does
not claim that an account was created, an email arrived or the address was verified.
An Auth session creates no Studies grant, study or invitation acceptance.

Signup returns only to the same-origin reader application root with validated
public passage parameters. Root and nested reader hosting use the configured
application base. Arbitrary redirect targets, private context and credentials are
excluded from return metadata. Confirmation tokens are handled by the existing
Auth SDK. Invalid links produce safe guidance while public reading remains usable.
Incomplete and provider-rejected callbacks also produce the notice and remove all
supported callback credentials. The startup adapter preserves an unrelated valid
session without restoring old storage; ordinary session rejection and concurrent
sign-out keep their existing semantics.
Return validation bounds book IDs and numeric syntax; actual passage availability
remains the existing reader/API's responsibility. The future Studies reference
catalogue is not implemented by this auth slice.

Provider request failures use safe code-based messages. Requests have a 15-second
network bound; retries are explicit. Closing a pending form does not cancel an
already accepted registration or promise rollback. Reopening starts a fresh form.
An accepted late response can still establish the shared Auth session and close an
open auth form. Modal isolation includes header/reader controls; pending requests
have accessible busy/progress feedback.

## Activation remains gated

Current owner configuration disables public signup. The checked-in
[Supabase config](../../../supabase/config.toml) also has email confirmation off,
and the [deployment profile generator](../../../platform/deployment/dev.py)
intentionally disables signup. This slice changes neither file nor live settings.

Before enabling live registration, the authentication/deployment owner must qualify
signup enablement, required address confirmation, exact reader callback allowlist,
confirmation email delivery and valid/expired/repeated-link behavior against the
actual project. Preserve existing account/session and public-reading compatibility.
The separate KDG session owns Access contracts and implementation; account creation
alone supplies no capability or resource authority. App-factory delivery belongs to
its separate platform session.

Browser tests intercept the provider HTTP boundary. They qualify the consumer UI,
SDK integration and public return handling; they do not prove real mail delivery,
Identity profile adoption, verified Studies access or full ST-36 completion. No
provider request, migration or deployment is needed for those fixture tests.

## Reuse and ownership impacts

- Scaffold: no generator change; keep the app-factory owner's work independent.
- Shared UI: the existing dialog remains app-local. Reusable focus/error behavior
  needs another proven consumer before a shared authentication abstraction.
- Agent context: existing owner/session rules suffice; no root instruction change.
- Documentation: canonical Studies contract plus this runtime/activation record.
- ADRs: existing authentication, API-boundary and session-recovery decisions apply;
  accepted decisions are unchanged. No schema migration is introduced.
