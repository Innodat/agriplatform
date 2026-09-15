# ADR-0003: Application Silo Architecture

**Status:** Accepted  
**Date:** 2026-09-01  
**Scope:** Repository and runtime architecture

## Context

The platform must support independently understandable applications while sharing
identity, design conventions, discovery, content, notifications, and scaffolding.
Uncontrolled runtime imports between apps and platform packages would couple
releases and turn common code into an indistinct domain layer.

## Decision

Each `apps/<app>` silo owns its backend, web client, database migrations, domain
documentation, tools, and changelog. Cross-app runtime capabilities live under
`services/` and are called through versioned contracts. Platform packages contain
generic build-time UI, clients, scaffolding, and conventions—not application domain
logic.

## Alternatives considered

- One modular monolith containing all domains
- Independent repositories immediately
- A shared backend imported by every application at runtime

## Consequences

- Domain ownership and future repository extraction remain clear.
- Some code duplication is acceptable until a genuinely reusable pattern is proven.
- Shared runtime behavior requires service contracts and operational ownership.
- Applications must not promote speculative domain abstractions into the platform.

## Revisit when

Operational evidence shows that the current boundary creates disproportionate
deployment overhead or prevents required cross-domain transactions.

