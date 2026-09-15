# ADR-0006: Domain-Aware Sensitive Attachment Access

**Status:** Accepted  
**Date:** 2026-09-01  
**Scope:** Leave supporting documents

## Context

Medical certificates and family-responsibility evidence contain more sensitive data
than ordinary absence records. The Content Service can control storage operations
but does not understand which Leave actors need a particular document.

## Decision

Leave owns attachment associations, privacy classification, and resource-level read
authorization. A caller needs both Leave-domain permission and a short-lived Content
Service read capability. `leave.document.sensitive.read` is separate from general
Leave, organization, or platform administration.

MVP limits are 10 MB per file, 3 files and 20 MB per request, accepting PDF, JPEG,
and PNG. Malware scanning is deferred but the content-safety state is extensible.
Medical documents default to two years' retention after request closure, configurable
by NGO/jurisdiction and subject to legal/privacy review.

## Alternatives considered

- Allow every approver or administrator to read attachments
- Store files directly in the Leave database
- Let Content Service infer Leave permissions

## Consequences

- Calendars, notifications, and ordinary absence views do not expose documents or
  unnecessary health details.
- Sensitive reads and disposal are audited.
- MIME sniffing, size verification, private storage, and signed URLs remain required
  even without MVP malware scanning.

## Related platform decisions

- [Shared FastAPI Content Service](../../../../../platform/docs/architecture/decisions/0004-shared-fastapi-content-service.md)
- [Signed direct-to-storage transfers](../../../../../platform/docs/architecture/decisions/0005-direct-to-storage-uploads.md)

