# ADR-0007: Continuous Scaffold Evolution

**Status:** Accepted  
**Date:** 2026-09-01  
**Scope:** Builder CLI, templates, shared UI, and delivery process

## Context

The Leave application is intended to establish the platform as well as deliver a
product. Updating scaffolding only after Leave is complete would lose implementation
context, allow templates to drift, and make later applications repeat solved work.
Promoting every first implementation, however, would pollute templates with domain
assumptions.

## Decision

Every feature completes a scaffold-impact review. Proven domain-neutral mechanisms
are added to application/service templates in the same delivery item, with generator
tests, validation, documentation, changelog, and migration guidance. Application-
specific work records `No scaffold change — application-specific`.

Shared shadcn components follow the same prove-then-promote rule. Generated sample
apps/services are verified in CI through install, type-check, tests, build, and
health/startup checks.

## Alternatives considered

- Update templates at the end of the project
- Put every Leave pattern into the builder immediately
- Maintain examples without executable generation tests

## Consequences

- The next app begins with current, tested conventions.
- Feature completion includes platform stewardship work.
- Templates contain stable mechanisms and extension points, not Leave entities.
- Existing apps receive migration notes instead of forced mechanical rewrites.

## Revisit when

Generation-test cost becomes disproportionate or evidence supports a different
promotion threshold.

