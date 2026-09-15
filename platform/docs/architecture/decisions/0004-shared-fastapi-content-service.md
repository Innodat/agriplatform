# ADR-0004: Shared FastAPI Content Service

**Status:** Accepted  
**Date:** 2026-09-01  
**Scope:** Cross-application content control plane

## Context

The receipt prototype implements content metadata and provider operations through
Supabase Edge Functions. Future applications need consistent tenant isolation,
provider selection, signed operations, auditing, retention, safety states, and
authorization integration. The prototype is not in production and needs no consumer
migration.

## Decision

Create `services/content-service` as a shared FastAPI runtime service. It owns
content metadata, tenant-specific provider resolution, provider adapters, upload
sessions, finalization, read capabilities, retention operations, and content
operation audit events. Domain applications own their content associations and
decide whether a caller may access a domain document.

## Alternatives considered

- Continue with Supabase Edge Functions
- Implement content independently in every application backend
- Put the service inside the Leave silo

## Consequences

- Content behavior becomes reusable and independently testable.
- Domain authorization and content authorization require a clear capability/API
  handshake.
- Azure Blob and Supabase Storage remain replaceable adapters.
- The non-production Edge Function prototype can be retired after parity tests.
- Sensitive files remain private and platform admins gain no implicit read access.

## Revisit when

The service boundary creates unacceptable latency or a storage provider mandates a
materially different architecture.

