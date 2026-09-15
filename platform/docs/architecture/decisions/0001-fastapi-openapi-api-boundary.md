# ADR-0001: FastAPI/OpenAPI API Boundary

**Status:** Accepted  
**Date:** 2026-09-01  
**Scope:** Platform and generated applications

## Context

Earlier applications use direct Supabase data access, while the current platform
direction requires a consistent place for authorization, orchestration, auditing,
domain validation, and stable client contracts.

## Decision

Application web clients call FastAPI for business reads and commands. Pydantic
models and FastAPI OpenAPI define the public contract, from which strict TypeScript
clients are generated or validated. Browser-side Supabase access is limited to
authentication and explicitly approved realtime scenarios.

## Alternatives considered

- Direct PostgREST/Supabase access for all application data
- Hand-maintained TypeScript and Python contracts
- GraphQL as the default platform boundary

## Consequences

- Domain rules and authorization have a server-side boundary.
- Database schemas remain persistence details rather than frontend contracts.
- OpenAPI generation and compatibility checks become required CI work.
- A network service is required for application functionality.
- Builder app and service templates must include this convention.

## Revisit when

A proven platform requirement cannot be served effectively through HTTP/OpenAPI,
or another contract technology offers a measured platform-wide benefit.

