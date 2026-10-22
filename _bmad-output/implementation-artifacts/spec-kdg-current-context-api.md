---
title: KDG current fixed-organization context API
type: feature
created: 2026-10-22
status: done
route: oneshot
review_loop_iteration: 0
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Deliver the first bounded KDG API consumer, the independently deliverable API portion
of approved Story 1.1: selector-free GET /api/v1/context. Forward the user bearer and
restricted KDG credential to the current Access /v2/check HTTP contract for exactly
kdg_capture.capture.read.own in the configured organization. Access verifies bearer
identity; KDG validates returned account/resource, actor, organization, permission,
membership and decision/time evidence before returning the typed current context.
All outcomes are private/no-store. Missing authentication, confirmed denial, actor
setup, malformed authority and unavailable verification have distinct safe outcomes.
No cached authority, extra permission or offline lease is established.

Use behavioral HTTP ATDD before implementation and focused TDD for negative contracts.
Preserve concurrent changes, historical evidence, Docker resources and approved pins,
including TypeScript 7.0.2. Synthetic local/CI only. No domain writes, browser sign-in,
Leave/editor, real accounts/access, provisioning, deployment/pilot, cleanup or fingerprint/
HMAC work. This completes an API prerequisite, not Story 1.1 or capture persistence.
</frozen-after-approval>

## Implementation Notes

- bmad-help catalog + current readiness/epics select [BD] bmad-build for the API entry
  dependency before Story 1.2 persistence. KDG was docs-only. Story 1.2 retains separate
  operator command identity rules; capture ADR-0061 does not convert them.
- No intent gap or irreversible operation. Small read-only consumer: owner API, focused
  tests, exported OpenAPI/generated TypeScript and evidence. No sprint key: this is a
  bounded prerequisite, not complete epic story implementation.
- Reuse builder HTTP/error/export seeds and existing platform/api-client generator;
  do not import Access/Identity server implementation or invent shared authority.
- Existing dirty tree is explicitly authorized concurrent work. Baseline tracked-byte
  custody and full Git ID are captured in /tmp/kdg-context-preservation.json.
- Acceptance: Given a valid bearer/current exact Access decision, when /context is
  requested, then return verified context with no-store. Given changed authority,
  when requested again, then recheck and deny. Given selectors or invalid authority,
  then refuse without data leakage. Given slow/unavailable dependencies, then bound
  execution and return safe unavailability; no logs contain credentials/payloads.
- Behavioral RED: health-only /context404 before implementation. First36 focused checks
  passed; subsequent schema RED45pass/1fail missing UUID format preceded metadata fix.
- Independent owner lock resolved/installed frozen/offline from existing approved cache;
  existing published/root/Access locks untouched. Existing HTTP adapter is generated
  unchanged. Client generation uses byte-identical retained installed tool sources;
  application compiler remains TypeScript7.0.2.
- Review-stage unexpected-error test observed54pass/1fail missing500 schema, then added
  response metadata and regenerated. Runtime already returned safe500/no-store.
- Review correction matrix observed9fail/61pass before patches, then70pass. Inbound
  stall, streamed-body deadline/close and freshness boundaries were added as gap proof;
  those passed before patches and are not misrepresented as failing behavior.

## Review Triage Log

Configured oneshot Blind Hunter completed; other lenses were not configured. Each
finding was checked against current source and treated individually. No review deferral.

| Finding | Verdict / evidence / disposition |
| --- | --- |
| Case-sensitive bearer scheme | medium; lower/upper schemes observed401; normalize valid schemes to Bearer for current Access; patched |
| Invalid origin port accepted | medium; three invalid-port construction tests failed; explicit parsed port/empty-port validation; patched |
| Compression before response-size check | medium; encoded stream read witness failed; request identity encoding/refuse encoded headers before iteration; patched |
| Loose RFC3339 parsing | medium; compact/hour-only current timestamps observed200; exact UTC grammar before date parsing; patched |
| Schema weaker than nil/bigint runtime guards | low; absent not/numeric-bound pattern proved; exported nonnil restriction and exact decimal-bound pattern; patched |
| Missing stalled inbound receipt test | medium verification gap; shortened request deadline now proves503/no Access call; existing code passed, test patched |
| Missing streamed response deadline/close test | medium verification gap; delayed chunks now prove single deadline and close; existing code passed, test patched |
| Missing exact freshness boundaries | low verification gap; frozen-clock plus/minus1s and1.000001s cases prove current bounds; tests patched |
| Provenance only in temporary/ignored directories | medium verification gap; versioned non-sensitive custody/results manifest and evidence excerpts added; patched |

- Final reviewed proof:70 KDG tests1.51s,130 affected Access/KDG tests3.05s;
  OpenAPI/client checks and strict TypeScript7.0.2 pass. Existing builder installer
  replay preserves owner source and generated adapter. Composition check-only passes.
- Concurrent branch advanced during delivery; external Leave/Scribeswell changes
  observed and excluded, never restored or staged. Relevant protected hashes and the
  original handoff tail remain preserved; durable custody is in owner evidence.
