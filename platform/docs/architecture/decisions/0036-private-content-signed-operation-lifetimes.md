# ADR-0036: Private Content Signed-Operation Lifetimes

**Status:** Accepted  
**Date:** 2026-09-23  
**Scope:** Shared private content upload/read capabilities

## Decision

Default private document read/download capabilities to 5 minutes and upload capabilities
to 15 minutes from issuance. These are bounded technical configuration defaults, not
Leave administrator settings or document retention periods. Issue each capability only
after applicable current domain/content authorization and enabled safety checks.

When a capability expires, obtain a new one after checking current access again, retaining
the existing upload/attachment workflow where it remains recoverable. Do not force a new
leave form or create duplicate content merely to renew a signed operation. A provider
may require restarting file transfer; preserve form input and explain that accurately.
Renewal must not bypass scope, expiry, size/type or other content restrictions.

Expiry prevents subsequent use as enforced by the storage provider; it does not delete
the document, revoke an already downloaded copy or guarantee immediate cancellation of
a transfer that began before expiry. Verify the concrete Azure Blob/Supabase Storage
adapter behavior for before/at/after expiry, in-flight transfers and clock tolerance.
Do not promise immediate revocation of already issued signed URLs. Keep them out of
logs and ordinary persisted business fields under platform privacy/transfer rules.

## Impact and verification

- Acceptance: configured default lifetimes, unauthorized issuance denied, fresh access
  checks on renewal, expiration and provider-specific in-flight behavior, preserved
  form/operation identity and no signed-URL leakage.
- Scaffold/content service: central technical configuration and provider contract checks;
  generated application callers reuse content capability APIs, not duplicate signing.
- Shared UI: existing document retry and attachment recovery patterns suffice.
- Agent context: existing private-transfer/privacy guidance suffices.
- Documentation: shared guidance and Leave requirements/tracker record the selected
  architecture-gate defaults; provider verification remains required before pilot.
- ADR: complements 0005, 0023 and 0030; accepted originals unchanged.
- Planning only; no capabilities issued, providers configured or runtime TTLs changed.
