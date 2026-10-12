# ADR-0055: Authenticated Private Downloads by Default

**Status:** Accepted — user direction 2026-10-06; implementation contracts pending
**Date:** 2026-10-06
**Scope:** Private content reads in applications and shared Content
**Partially supersedes:** [ADR-0005](./0005-direct-to-storage-uploads.md) and
[ADR-0054](./0054-application-authorized-content-and-enforced-ownership.md) for the
normal private download data path; [ADR-0036](./0036-private-content-signed-operation-lifetimes.md)
only insofar as a five-minute browser read URL was the default private read mechanism.
Accepted predecessors remain unchanged. Direct signed uploads remain unchanged.

## Decision

Private file reads require authenticated current authorization on each HTTP file
request by default. The owning application API authenticates the user and checks
current capability, organization/account context where applicable and domain/resource
permission. It resolves the file association and streams through authenticated Content,
which enforces the service identity, stored application/resource ownership, readiness,
safety and finalized content identity under ADR-0054/0038. Content alone owns provider
access. Do not redirect the browser to a bearer storage URL or disclose one in metadata,
headers, errors or frontend state. No application callback or new authorization service.

The browser's download URL identifies a protected application route; knowledge of it
does not authorize another caller. Use the application's supported authenticated request
mechanism, never tokens in URLs. File bytes flow storage → Content → application →
browser, streamed with bounded buffers rather than loading whole files into API memory.
Define session/bearer handling for browser downloads and previews before delivery; a
native browser/PDF request must not silently fall back to a shareable storage link.

Each new GET, HEAD or supported range/resume request checks current access. Reject
unsupported methods/ranges safely. No shared/public cache may serve private bytes without
those checks; use private no-store responses and verify proxy/CDN/preview behavior.
Already-delivered bytes cannot be recalled. Revocation affects new requests; this does
not promise instantaneous cancellation of an already authorized stream. Define bounded
transfer duration, timeouts, cancellation and disconnect behavior explicitly under the
in-flight authorization policy. Do not hold database transactions/locks while streaming.

## Future sharing

Do not implement optional share links or an administrative sharing switch now. When a
real workflow needs access without sign-in, design it as explicit scope: who may issue
links, permitted file/audience/actions, lifetime, revocation, disclosure and audit, plus
provider/cache enforcement. No automatic signed-URL fallback when authentication or a
stream fails. ADR-0036 remains applicable to any retained explicitly approved signed
operations; it does not itself enable browser sharing for private documents.

Uploads retain short-lived direct-to-storage operations and current finalization,
association/cleanup and byte-identity safeguards. Download changes do not solve or waive
the existing provider-enforced upload-lifetime gate.

## Acceptance and impacts

- Authorized PtS/Leave users receive permitted bytes via authenticated routes; copied
  routes deny unauthorized accounts. No membership is added to individual PtS reads.
- Revoked access is rejected on the next request, including range/resume; unrelated
  content IDs, wrong app/scope and metadata/HEAD requests cannot bypass protection.
- Test browser preview/download authentication, proxy cache behavior, client disconnect,
  upstream failure, large-file bounded memory/backpressure and clean resource closure.
  After bytes start, failures cannot be reported as a successful complete file or retried
  invisibly by issuing a public capability; define client recovery accurately.
- Preserve exact finalized bytes and relevant size/type/range semantics; do not trust
  arbitrary browser-provided provider URLs. No provider secrets/read URLs in browser or
  logs. Authorization observations and Content service/initiator attribution remain.
- PtS adoption owns the first existing-source-document streaming consumer. Leave E4
  reuses the verified Content client/streaming path with its medical/domain tests.
- Scaffold and shared UI: proven authenticated download/preview adapters, safe headers,
  bounded streaming and contract fixtures. Agent context/docs/tracker reference this
  decision; no separate feature engine or mandated bucket layout.

Exact streaming wire, file limits/timeouts, browser auth integration, deployment proxy
constraints and Content metadata migration remain pre-story inputs. No application code,
provider configuration, production access or readiness pass is authorized by this ADR.
