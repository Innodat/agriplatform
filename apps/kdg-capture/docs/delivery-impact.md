# Shared pattern and stewardship impact decisions

Proposal for coordinated delivery, not authorization to modify shared owners. This KDG
session coordinates; existing component owners retain implementation/contract authority.
Scaffold inputs under ADR-0059 reference these proven choices only after a real versioned
schema/generator exists. Do not invent a second config language or claim JSON metadata
proves behavior. Questionnaire JSON and scaffold configuration are separate concerns.

| Consuming area | Smallest useful shared promotion | Application-specific boundary | Evidence |
| --- | --- | --- | --- |
| Auth/organization admission | Typed scope-aware Access client, safe errors, optional fixed-org navigation, same-user return | Khula-only policy, two KDG roles, own/all capture scope and assignments | P-AUTH/P-ACCESS/P-SESSION, A01/A02/A14–16 |
| App generation/owned write | Existing generator's minimum API/web/test/owned migration layout, neutral shadcn theme, restricted transaction context and operation/revision pattern | KDG schema, JSON validation, child/date multiplicity and author/editor rules | P-SCAFFOLD/P-WRITE, A02/A03/A09/A21/A22 |
| Install/offline shell | Opt-in manifest identity/scope/icons and shell-only service worker, deferred update hook | KDG names, capture/admin routes and domain setup | A04/A17, physical PWA proof |
| Local persistence | Thin IndexedDB transaction/schema-version/partition utilities and old/new fixtures | KDG completed captures/operations/snapshots/retention | P-OFFLINE, A07/A10/A14/A17/A18 |
| Sync mechanics | Durable queue envelope, ordered claim/recovery, bounded retry and foreground triggers; no generic workflow engine | Capture commands, assignment denial, exact version validation and conflict decisions | P-OFFLINE/P-ERROR, A09–12/A16/A20 |
| Status UX | Accessible text/icon local saved, remote acknowledged, pending/attention, inline retry and safe exit/update notices | Afrikaans wording, capture validity, child/question detail controls | P-STATUS, A05/A08/A19 |
| Offline test utilities | Disconnect/reopen/resume, fake clock, lost response, quota/migration/update fixtures | Child/role/version/answers acceptance scenarios stay KDG-owned | P-DEVICE plus A04–A22 |
| Survey renderer/editor | Initially app-local schema validator, rating/boolean/text renderer, stable version adapter | Questionnaire semantics and child observations | A05/A12/A13; promote Survey-domain component only after second demonstrated consumer |

Every delivery story records the following impacts and updates reusable artifacts in
that same item when applicable:

- **Scaffold:** add proven neutral mechanism to owning templates/validated recipe/tests;
  or explicitly record No scaffold change — application-specific.
- **Shared UI:** promote only proven domain-neutral components through platform owner;
  app-specific renderer/child controls remain in KDG. Do not duplicate a role editor.
- **Agent instructions:** KDG guidance should state fixed org, account-based authors,
  original versions, local/server distinction and actual verified commands. Root AGENTS
  changes require coordinated ownership; no root instruction is changed during planning.
- **Documentation:** maintain this app's PRD/UX/contracts/test evidence and owner runbooks;
  update owning generator/pattern/consumer guidance when implementation is proven.
- **Contract:** Pydantic/OpenAPI and generated clients change together; shared KDG Access
  variant and service registry are coordinated owner changes, not silently app-local types.
- **ADR:** accepted platform decisions remain unchanged. App decision records may accept
  JSON/offline conventions after review; only conflicts with accepted platform direction
  require a linked superseding platform ADR. No new general Survey service or offline engine.

The early phone proof can establish KDG's first-consumer PWA pattern before Leave is
implemented. It does not replace Leave's reference/write/scaffold requirements or
recreate a second maintained platform verification application.

Saving amendment, 2026-10-13: observations use explicit Save only; do not promote
unfinished-entry recovery/draft machinery through KDG. Questionnaire configuration
drafts, saved capture conflicts and pending-operation recovery remain required.

Offline simplification, 2026-10-14: platform-owned first-consumer patterns cover bounded
local transaction/schema migration, account/org isolation, queue/idempotency/retry,
revision/conflict primitives, status, PWA updates and test utilities. No general local
history table/engine or new runtime offline service. KDG retains current observations,
required questionnaire definitions, pending snapshots and conflicts; simple attribution
uses existing server-managed fields. Shared changes require the pending Leave handoff.
