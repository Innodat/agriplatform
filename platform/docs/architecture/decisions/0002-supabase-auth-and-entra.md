# ADR-0002: Supabase Auth with Microsoft Entra ID

**Status:** Accepted  
**Date:** 2026-09-01  
**Scope:** Platform identity for MVP

## Context

The platform already references `auth.users`, adds tenant/membership claims through
Supabase JWT hooks, and enforces PostgreSQL RLS from those claims. Microsoft Entra
ID is the intended workforce identity provider. Replacing identity infrastructure
now would require broad migration without resolving an MVP blocker.

## Decision

Retain Supabase Auth and federate Microsoft Entra ID for MVP. Authentication alone
does not grant NGO access: an active, authorized organization membership is also
required. Application code consumes a provider-neutral current-user/context model
rather than Supabase user objects outside the identity boundary.

## Alternatives considered

- ZITADEL as the central identity broker
- Self-hosted Keycloak
- Direct Entra integration in every application

## Consequences

- Existing JWT hooks, foreign keys, and RLS remain usable.
- One identity can have memberships and roles in several NGOs.
- Tenant switching requires refreshed server-verified membership context.
- Account linking and invitations must not rely on email alone.
- The neutral identity contract preserves a later migration path.

## Revisit when

Tenant-managed identity providers, complex B2B federation, identity independence
from Supabase, or delegated identity administration becomes committed scope.

