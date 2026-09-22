# ADR-0024: Durable Delivery Retries and Audited Recovery

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** Application and shared-service durable delivery

## Decision

Retry temporary handover/delivery failures with increasing delays and bounded policy.
Classify failures requiring correction separately and stop futile automatic retries.
When retry limits are reached, retain the failed item and its attempt history, expose
failure status and alert technical operations. Never silently discard required work.
Exact classification, delay and limit values belong to the owning delivery contract.

After repair, an authorized technical operator may request retry through an audited
operational command. This requests normal worker processing, rather than bypassing
receiver checks or sending directly. Preserve original event identity for the same
payload/intended effect and reuse duplicate-safe receiver handling. A changed payload
must follow the existing new-event/correction contract, never silently reuse identity
with different content. Recover with knowledge of possible prior remote acceptance.

The recovery operation checks current target state and coordination so it cannot
steal active work or requeue an already completed item blindly. Audit authenticated
operator identity, NGO/owner, target item, reason, operation identity, timestamp and
outcome. Do not trust an operator name supplied as a free-form flag as authentication.
Use scoped application/service authority and tenant checks, never default database
administrator credentials or cross-application table access.

Recovery does not repeat or roll back the originating business action. Where a
handover has already succeeded, downstream delivery failure belongs to the receiving
service and its recovery path, not to blind replay by the original producer.

For MVP, an operational command and runbook suffice; no dedicated support UI is
required. Its execution transport and packaging remain a separate decision. Keep
business notifications separate from technical alerting and apply ADR-0023 privacy.

## Impact and verification

- Acceptance: temporary/permanent failure paths, retry exhaustion retains evidence,
  scoped authorized recovery, concurrent attempt safety, duplicate-safe replay after
  uncertain acceptance, audit attribution and no repeat of the originating action.
- Scaffold: prove reusable retry/recovery mechanics before promotion; owning services
  retain payload meaning and failure classification.
- Shared UI: existing user action state remains; no technical queue in business UI.
- Agent context: current identity, silo and sensitive logging guidance suffice.
- Documentation: shared scaffold guidance and Leave requirements/tracker link here.
- ADR: complements 0006, 0012, 0017, 0018 and 0023; accepted originals unchanged.
- Planning only; no executable support command, retry code or production change.
