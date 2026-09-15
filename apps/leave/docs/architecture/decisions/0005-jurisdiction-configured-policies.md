# ADR-0005: Configurable Jurisdiction-Aware Policies

**Status:** Accepted  
**Date:** 2026-09-01  
**Scope:** Multi-country Leave configuration

## Context

One NGO may employ people in several countries. Entitlements, holidays, schedules,
documentation, retention, and other employment requirements may vary by country or
region. Encoding every jurisdiction's legislation and tracking legal changes is
beyond MVP scope and would create an unreliable compliance claim.

## Decision

Model jurisdiction, location, calendar, schedule, policy assignment, and effective
dates below NGO level. Provide configurable policies and seedable examples, but do
not implement a statutory legal-rules engine or claim automatic legal compliance.
Each NGO must review its settings and retention schedule for applicable law.

## Alternatives considered

- One jurisdiction per NGO
- Hard-coded country implementations
- Ignore jurisdiction until a later schema change

## Consequences

- Multi-country employees are supported without redesigning core relationships.
- Policy templates can be added later without changing the engine.
- Product copy and documentation must not present defaults as legal advice.
- Jurisdiction and effective-date combinations require test coverage.

