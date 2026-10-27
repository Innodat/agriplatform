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

Live registration remains gated. The checked-in
[Supabase config](../../../supabase/config.toml) has email confirmation off.
The [deployment profile generator](../../../platform/deployment/dev.py) enables
signup, required confirmation, a120-second local OTP and captured local SMTP only
for the dedicated disposable `scribeswell-local` qualification target. KDG/Leave
profiles remain byte-identical. This local profile does not enable a deployed
project or define production OTP/mail policy.

Before enabling live registration, the authentication/deployment owner must qualify
signup enablement, required address confirmation, exact reader callback allowlist,
confirmation email delivery and valid/expired/repeated-link behavior against the
actual project. Preserve existing account/session and public-reading compatibility.
The separate KDG session owns Access contracts and implementation; account creation
alone supplies no capability or resource authority. App-factory delivery belongs to
its separate platform session.

Earlier consumer browser tests intercept the provider HTTP boundary. They qualify the consumer UI,
SDK integration and public return handling; they do not prove real mail delivery,
Identity profile adoption, verified Studies access or full ST-36 completion. No
provider request, migration or deployment is needed for those fixture tests.

The separate [real-signup qualification](../../../_bmad-output/implementation-artifacts/spec-scribeswell-real-signup-qualification.md)
adds an explicit local native entrypoint,
`apps/scribeswell/tools/py/qualify_studies_signup.py`. It runs the entire existing
owner qualification, then genuine browser signup, local mailbox confirmation,
explicit enrollment and separate study creation, followed by consumed/elapsed
expired-link checks in fresh contexts. Its focused helper tests are not actual
provider/mail proof; the parent native execution and dated
[evidence record](STUDIES_OWNER_INTEGRATION_EVIDENCE.md) report that separately.
Only synthetic recipients are permitted; no external delivery/relay is configured.
Confirmation alone supplies neither an actor binding nor a Studies capability.

## Reuse and ownership impacts

- Scaffold: no application scaffolding change; the deployment renderer adds only the dedicated local qualification profile.
- Shared UI: the existing dialog remains app-local. Reusable focus/error behavior
  needs another proven consumer before a shared authentication abstraction.
- Agent context: existing owner/session rules suffice; no root instruction change.
- Documentation: canonical Studies contract plus this runtime/activation record.
- ADRs: existing authentication, API-boundary and session-recovery decisions apply;
  accepted decisions are unchanged. No schema migration is introduced.


The [2026-10-27 real native signup proof](STUDIES_OWNER_INTEGRATION_EVIDENCE.md#real-signup-native-proof--2026-10-27)
now passes using real UI-created accounts and captured local email, including valid,
consumed and genuinely expired links, independent SQL and explicit enrollment.
This closes the local signup qualification gate. Production email delivery and
registration activation still require the owning deployment environment.
