# ADR-0005: Signed Direct-to-Storage Transfers

**Status:** Accepted  
**Date:** 2026-09-01  
**Scope:** Content upload and download data path

## Context

Proxying file bytes through application or content APIs consumes API memory,
bandwidth, connections, and scaling capacity. Storage providers already support
short-lived signed operations while the platform still needs control over who may
initiate and finalize them.

## Decision

FastAPI is the content control plane, not the normal file-byte data path. The client
requests an authorized upload session, transfers bytes directly to the configured
private storage provider, and calls FastAPI to verify/finalize. Reads use short-lived
operation-specific URLs issued only after domain and content authorization.

## Alternatives considered

- Proxy every upload and download through FastAPI
- Expose permanent provider URLs
- Allow clients to create provider paths or credentials directly

## Consequences

- APIs scale independently of file volume.
- Signed URLs must be short-lived, scoped, unguessable, and never logged in full.
- Finalization, expiry cleanup, MIME/size verification, and idempotency are required.
- Server-proxied transfer remains an exception for future compliance needs.

## Revisit when

A compliance, transformation, malware-inspection, or provider requirement requires
server-side streaming for a particular content class.

