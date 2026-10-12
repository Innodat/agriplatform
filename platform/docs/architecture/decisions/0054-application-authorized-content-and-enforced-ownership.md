# ADR-0054: Application-Authorized Content and Enforced Ownership

**Status:** Accepted — user agreement 2026-10-06; implementation contracts pending
**Date:** 2026-10-06
**Scope:** Shared Content control plane and consuming application APIs
**Refines:** [ADR-0004](./0004-shared-fastapi-content-service.md),
[ADR-0005](./0005-direct-to-storage-uploads.md),
[ADR-0053](./0053-capability-scoped-access-in-mixed-scope-applications.md).
Accepted predecessors remain unchanged.

## Decision

Route user content control-plane requests through the owning application's API.
That API authenticates the user, checks current applicable capabilities and resource
permissions, resolves its domain association and calls Content through a restricted
service identity. Content enforces that service's permitted operations and the file's
recorded ownership/scope, readiness, safety and lifecycle before releasing a capability.
Browser transfers file bytes directly using the resulting short-lived signed operation;
application APIs need not proxy bytes. No application callback or additional authorization
service is required for this default handshake.

Each content identity has one owning application and a typed resource ownership scope:

| Scope | Required ownership |
| --- | --- |
| Application | Owning application; shared application resource |
| Organization | Owning application and organization ID |
| Account | Owning application and account ID |

These are enforced metadata, not merely diagnostic log fields. The authenticated service
identity maps server-side to allowed application/operations and any configured narrower
scope restrictions. Never accept a caller-supplied application ID as authority. Creation
validates ownership within this policy and persists it; reads compare requested context
against stored metadata. Unknown/wrong application, mismatched scope and unauthorized
operations fail without issuing a signed URL or leaking protected metadata.

Do not infer ownership from the initiating user, uploader, URL prefix or capability's
scope. A PtS account capability can authorize an application-owned corpus document.
A Leave approver may read an organization-owned file uploaded by a different person
only after Leave's domain checks. Personal files use account ownership where appropriate.
Uploader/initiator attribution is separate from ownership. One owner per file is the
default; no generic allowed-applications list or cross-app sharing is introduced.

The application derives authorized resource scope and content identity from trusted
records, never merely forwards arbitrary browser values. It owns request-specific
rules such as assigned approver, employee ownership and medical-document permission.
Content does not duplicate these rules or call the application back to reconstruct them.
A bare user token does not permit direct browser access to private Content control-plane
operations. Import/worker authority is separately restricted from application readers.

## Trust and evidence

Content trusts the authenticated owning API's assertion that the user/domain operation
is authorized; its ownership checks constrain that trust to the service's permitted
application/resource scope. They do not independently prove that user authorization.
A compromised application API may misuse files within that scope. No claim of protection
against its own trusted service is made; do not invent per-organization credentials or
signed assertion infrastructure without a separate demonstrated need.

Record verified executing service and separately application-asserted initiator plus
operation/trace references under ADR-0025. Content must not describe forwarded actor
fields as independently authenticated end-user proof. Exact actor validation, typed
request/result bounds and service-policy provisioning remain pre-story contracts.
Keep credentials, sensitive content and full signed URLs out of operational logs.

Retain ADR-0030 association/cleanup coordination, ADR-0036 provider-enforced signed
lifetimes and ADR-0038 fixed verified byte identity. No ownership change may repoint a
content ID at different bytes. Already-issued signed URLs remain subject to their expiry;
new checks do not claim to recall downloaded bytes or immediately revoke issued URLs.
Resource disposal and sensitive metadata access keep their existing domain safeguards.

## Acceptance and delivery

- Authorized PtS account with no memberships obtains only its permitted corpus document
  through PtS. Read/export alone does not imply document permission.
- Leave denies missing medical permission or unrelated request before Content issuance.
  Authorized approver access does not require being the uploader.
- Content rejects a Leave credential requesting a PtS-owned file, mismatched declared
  organization/account, unsupported operation, bare browser bearer and forged owner field.
- Application-owned, organization-owned and account-owned scope constraints are tested
  independently; pool reuse/missing context cannot broaden reads. No blanket nullable-org
  RLS or provider path supplied by a browser.
- Service-only Content tests prove ownership/readiness/lifecycle checks; application API
  tests prove current user/resource permissions. Integration proves their composition.
- PtS/Content adopt this boundary together through ADR-0052's controlled transition;
  no permanent old double-user-check contract. Existing checks remain until replacement
  activation. Leave E4 uses the same platform handshake and its own domain tests.

Scaffold: server-side Content client and safe upload/read/finalization adapters, with
browser-to-app control-plane calls and direct signed byte transfer. Shared UI need not
expose technical ownership details. Update agent context, architecture, consumer contracts
and delivery evidence together. Physical bucket layout, owner DDL, existing object mapping,
association protocol and service-policy details remain readiness inputs; no mandatory
bucket per application/organization/account. No code, credentials, migrations or deployment.
