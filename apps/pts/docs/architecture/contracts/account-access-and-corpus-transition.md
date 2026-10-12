# PtS account access and corpus transition

> **Private-read update:** [ADR-0055](../../../../../platform/docs/architecture/decisions/0055-authenticated-private-downloads-by-default.md)
> supersedes signed browser-read proposals below: each private file request authenticates
> through PtS, with bounded streaming from Content. No storage URL exposed to the browser.
> Signed uploads and immutable byte identity remain. Streaming auth/range/cache/deployment
> contracts are now prerequisites for PtS adoption; no sharing feature is added.

**Status:** Ownership/access direction, delivery split and PtS adoption criteria approved 2026-10-07; not implementation-ready
**Date:** 2026-10-06
**Authority:** [Platform ADR-0052](../../../../../platform/docs/architecture/decisions/0052-pts-account-scoped-access-and-coordinated-adoption.md),
[ADR-0053](../../../../../platform/docs/architecture/decisions/0053-capability-scoped-access-in-mixed-scope-applications.md)
and the [current owner design](../../ARCHITECTURE.md).
Historical frozen SPEC records its original delivery, not this new access target.

## Current working-tree evidence

| Path | Existing behavior | Required transition |
| --- | --- | --- |
| [Browser](../../../web/src/main.tsx), [auth return](../../../web/src/auth.ts), [login](../../../web/src/LoginForm.tsx) | Waits for org, derives it from URL/Directory, sends X-Org-ID and carries org through navigation; organization-specific login guidance. | Account entry without org selection/header/return prerequisite. Preserve same-account return and clearing prior-account data. Remove organization wording from current individual paths. |
| [API](../../../backend/main.py) | All protected dependencies require X-Org-ID and pass it to repositories. Read, export and documents use separate capabilities. | Check registered account variant; resolve collection context on the server. Keep exact operation permissions and request/resource checks. |
| [Access/Content clients](../../../backend/clients.py) | Uses /v1/check with org; validates returned org; Content request sends org and user token. | Typed account decision plus explicit application resource binding; no borrowed membership or optional-org shortcut. |
| [Database](../../../backend/db.py), [owned migration](../../../migrations/versions/0001_initial.py) | org_id keys/FKs, app.org_id context and forced RLS; restricted runtime/import roles. | Define application-owned collection keys and equivalent restricted read/import boundaries before DDL; no blanket RLS removal. |
| [Content control plane](../../../../../services/content-service/main.py) | PtS service caller; repeats pts.poetry.documents check via org-based Access; object/read audit and provider paths use org; imports restricted to configured org. | Bind permitted PtS application corpus and object identity separately from account admission. PtS owns current user capability checks; Content enforces caller/ownership, readiness and audit under ADR-0054. Import authority remains separate from readers. |
| [Importer](../../../tools/import_library.py), [source upload](../../../tools/upload_sources.py) | Imports corpus into org partition and links source documents to Content IDs. | Move owner setup/import configuration to declared corpus scope; no per-user import/copy or automatic broadening to other content. |

This is source inspection, not a live database inventory, security certification or
proof that deployed state matches these files. No runtime tests were executed.

## Agreed target boundary

The current poetry corpus is an application-owned shared collection, not an individual's
private data and not an organization tenant. Each authorized account sees the collection
permitted by its exact capability:

- `pts.poetry.read`: collection, poems and permitted source metadata.
- `pts.poetry.export`: existing filtered text/JSON export action.
- `pts.poetry.documents`: existing source-document link/read action.

These capabilities remain separate. No manage/export/documents-to-read inference is
introduced. App entry uses the already selected read capability. Existing source rights,
notices and content restrictions remain; this is no new permission to publish a corpus.
No new per-poem ACL, multiple-corpus product, subscription model or copying per account.
Future organization-owned PtS features use their own resources/capabilities and cannot
be reached using these account grants.

PtS resolves its corpus and document association server-side. A user-provided org,
content UUID or legacy URL must not select another application's/organization's content.
Under [ADR-0054](../../../../../platform/docs/architecture/decisions/0054-application-authorized-content-and-enforced-ownership.md),
PtS checks the current individual document capability and actual source association.
Content authenticates the PtS service and enforces stored PtS application ownership,
resource scope, readiness and lifecycle before issuance. No callback to PtS or duplicate
end-user capability check inside Content is required. Application authorization and
Content enforcement need separate and integrated tests. Content never reads PtS tables;
it trusts the narrow owning-service assertion within its enforced ownership boundary.
Exact service policy, typed assertion/attribution and resource mapping remain contracts.

Storage context and permission scope are different. Target the corpus explicitly in
owned persistence. Existing provider keys may stay unchanged if treated only as opaque,
server-owned locators under the correct content identity; an old UUID path segment must
not require identity membership or become a synthetic organization. This proposal does
not select the final DDL/backfill/key mapping, or permit old org-context checks to remain
as the account admission model.

## Required transition and acceptance evidence

1. Inventory actual PtS data partitions, associations, Content IDs, finalized versions,
   provider locators, readers/importers and supported deployment commands before selecting
   migration. Verify the declared corpus; never merge every old org partition implicitly.
2. Design owner-local migrations and typed account/corpus contracts, with restricted
   runtime/import/migrator privileges and a coordinated activation/recovery plan.
   Use planned maintenance if required. No automatic destructive downgrade.
3. Preserve poem/source/rights/witness relationships, import history, source document
   associations and finalized byte identity. Read-only means no personal document
   migration; it does not mean existing corpus assets can be discarded or repointed.
4. Prove zero-membership individual read/export/document paths against real services;
   separately exercise revoked/absent capability, wrong service, unrelated Content ID,
   not-ready content, provider outage, cross-account state and obsolete org parameters.
   No unsupported org selector may silently broaden resource access.
5. Prove source links and existing corpus outputs remain correct, repeated imports retain
   their accepted conflict/idempotence behavior and actual restricted DB roles prevent
   unrelated-scope access. Authenticated per-request streaming under ADR-0055 and platform ADR-0038 race/replay
   guarantees remain binding; this planning pass supplies no provider evidence.
6. Rehearse coordinated PtS/Access/Content/Directory/client switch and failure recovery
   on synthetic data. Remove unused legacy paths only after consumer inventory; do not
   require a permanent v1 compatibility layer or change production during planning.

## Delivery impact

Access A/B own grant/check mechanisms, not the entire PtS application transition.
The approved E1-PTS-ADOPT item consumes completed ACCESS-B, CONTENT-READ and
DISCOVERY/LAUNCHER. CONTENT-READ then PTS-ADOPT follow LAUNCHER and precede WRITE/REF
in the approved 23-item sequence. Detailed story criteria and remaining contracts are
separate readiness inputs. PtS adoption must
not require a future Leave attachment UI; shared Content changes still need their own
contract/provider evidence and regression checks for organization consumers.

Scaffold: explicit account authorization and owner-resource adapter fixtures, optional
organization UI; no universal corpus engine. Shared UI: reuse current auth/launcher
states. Agent context: existing ADR-0052/0053 guidance suffices. Documentation: this
owner contract, architecture link and Leave dependency tracking. Accepted ADRs unchanged;
ADR-0054 now selects the shared authorization/ownership boundary; physical mapping remains open.
No application code, migration, live access or implementation readiness approval.


Minimum metadata and read contract — 2026-10-06: see the [Content-owned design](../../../../../platform/docs/architecture/contracts/content-ownership-and-authenticated-read.md).
It records ownership variants, byte identity, provider locator and accurate attribution;
legacy composite keys/triggers/audit require coordinated mapping. Approved CONTENT-READ
then PTS-ADOPT items separate shared enforcement from application integration. Both
follow launcher integration in the approved sequence; no earlier placement is binding.


Acceptance clarification — approved 2026-10-07: read/export/document capabilities may
be assigned together to the current cohort, with no new roles/UI implied. Authenticated
private downloads apply to stored source files. Preservation retains the existing poems,
citations/source associations and import/conflict history; it adds no new user-facing
history feature. Exact commands/schema/transport and implementation readiness stay open.


## Concrete adoption mapping — proposed 2026-10-08

**Approach approved by the user, 2026-10-08; inventory, DDL and rehearsal remain pending.**

Refines the approved preservation requirement; exact DDL remains a readiness input.
Use a reviewed migration input/evidence file, not a new user-facing management feature.
For each selected stored source object, record:

- Legacy Content key (organization ID plus content ID) and PtS source association.
- Target owning application `pts`, resource scope `application`, and target Content ID.
- Verified finalized provider version/locator, digest and byte size, held in restricted
  migration evidence rather than exposed in browser responses or routine logs.
- Mapping result and migration/release reference, preserving historical attribution.

Retain the existing content ID where verified unambiguous. If globally colliding IDs
require remapping under the selected schema, record an explicit old composite-key to new
ID mapping and update owner-local associations together. Do not guess or silently merge
objects, and do not automatically move every old organization partition into PtS.
Existing provider paths may remain unchanged as opaque locators when they still bind the
same verified bytes. This changes ownership metadata, not document contents or per-user
copies. User account recreation is independent of preserving the corpus.

Before activation, reconcile selected source/association counts and exact object mappings,
verify representative reads and all adopted byte bindings, and reject unknown ownership,
missing objects or mismatched identities. Rehearse the owned migrations and recovery on
isolated fixtures first. A read-only deployed inventory is still needed in the authorized
implementation work; this proposal does not claim it has been performed.

CONTENT-READ owns Content constraints and migration mapping; PTS-ADOPT owns collection
selection, PtS associations/import configuration and coordinated activation. Each owner
uses its own migration; no cross-service runtime table access. Existing release-safety
rules apply. No new story, UI, actor model or accepted ADR change is required. Scaffold
impact is reusable migration/evidence validation only where proven domain-neutral;
PtS corpus selection remains application-specific. Documentation links this mapping from
existing adoption criteria; agent-context guidance already covers ownership/release safety.
