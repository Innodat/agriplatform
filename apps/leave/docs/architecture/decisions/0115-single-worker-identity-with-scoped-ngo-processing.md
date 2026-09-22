# ADR-0115: Single Worker Identity with Scoped NGO Processing

**Status:** Accepted  
**Date:** 2026-09-22  
**Complements:** ADR-0114 and platform ADR-0017/0018

## Decision

Use one Leave-worker service identity capable of processing authorized work for
multiple NGOs. Do not create a separate worker database account or access key for
each NGO. The worker uses restricted owner-specific credentials and job authority;
service identity and NGO transaction scope are distinct concepts.

A narrowly authorized queue discovery/claim operation returns the metadata needed
to claim due work, including its recorded NGO ownership. It does not provide general
cross-NGO access to employee records. Select the precise database mechanism in the
implementation story and verify its restricted authority under real runtime roles.

For each claimed item, establish verified service identity and that item's recorded
NGO context for every protected transaction. Derive scope from authoritative queue
ownership, not arbitrary payload fields or client-selected identifiers. Verify the
item belongs to the NGO under which it is processed. Transaction-local context ends
on commit/rollback and must not leak through pooled connections to another item.

NGO context scopes permitted access; it is not itself authorization. The worker is a
trusted backend component with bounded job authority, not a database administrator or
a broadly privileged browser of tenant business records. Preserve the initiating user
separately when relevant; never impersonate that person for service execution.

## Impact and verification

- Acceptance: interleaved work for two NGOs, rollback and connection reuse, mismatched
  queue ownership, missing context, restricted cross-NGO discovery and denial of
  unrelated business-record access; current claim checks remain binding.
- Scaffold: reuse proven restricted-role and transaction-context patterns; do not
  generate per-NGO worker secrets or a global cross-application queue reader.
- Shared UI: no NGO setup or credential field required.
- Agent context: existing tenant/actor rules suffice.
- Documentation: requirements and tracker synchronized.
- ADR: applies [platform context rules](../../../../../platform/docs/architecture/decisions/0018-transaction-scoped-tenant-context.md)
  and [restricted runtime authority](../../../../../platform/docs/architecture/decisions/0017-runtime-and-migration-database-authority.md);
  accepted originals unchanged.
- Planning only; no credentials, database grants or queue implementation created.
