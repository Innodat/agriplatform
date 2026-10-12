# ADR-0059: Schema-Validated Application Scaffold Configuration

**Status:** Accepted — user direction 2026-10-12; schema/generator/readiness pending
**Date:** 2026-10-12
**Scope:** Build-time application/service scaffold inputs and proven pattern adoption
**Refines:** [ADR-0007](./0007-continuous-scaffold-evolution.md) and
[ADR-0010](./0010-bmad-as-delivery-workflow.md); accepted predecessors unchanged.

## Decision

Use a thin version-controlled JSON scaffold configuration validated by a versioned schema.
Populate approved engineering choices incrementally during existing BMAD planning and
maintain them with consuming stories. Specs/ADRs/UX remain authoritative product/design
sources; the configuration references them rather than becoming a second requirements
language, source of actual user grants or alternate delivery workflow.

Record selected proven patterns, owner/scope/contract references, surface presentation,
saving/history decisions and requirement/story/test links as applicable. Keep inline/
drawer/page presentation separate from request-draft, explicit-form and immediate-
preference saving semantics under ADR-0051. History declarations use owner/action-specific
policies under ADR-0025, not a convenience switch disabling consequential evidence.
Owned table/API shapes reference their model/migration/OpenAPI authority; do not duplicate
column definitions or infer public APIs/permissions automatically from tables.

Generator/schema checks constrain supported choices and preserve declared custom extension
modules. Behavioral acceptance/contract/generated-output tests prove required shared
patterns work; a config assertion alone is not enforcement. Document justified extensions
and their evidence within the same story; changes to accepted architecture require a linked
superseding ADR. AI may propose choices and maintain metadata but cannot override current
scope/auth/transaction/attribution rules through defaults or untested pattern claims.

Start with P1/SERVICE's concrete minimum input and WRITE/REF proofs; expand schema/pattern
catalogue with the first consuming implemented/proven feature. No universal runtime app,
form or workflow engine, developer portal or upfront hypothetical pattern library. Existing
deployment manifests remain their own authoritative inputs; reference stable IDs and check
alignment instead of duplicating them. Exact schema/path/version/generation compatibility
and commands must be settled before affected story readiness.

## Impact and verification

Scaffold owns versioned input validation, proven generation and required fixtures; shared UI
promotes supported pattern composition with first consumers. Generated agent guidance
records selected patterns/extension points where useful. Owner docs/configuration/tests
update in the same delivery item; no parallel BMAD lifecycle. Reference app verifies pattern
composition and actual apps retain domain acceptance. Required checks include unsupported/
invalid declarations, source/contract consistency, regeneration preserving custom behavior
and real output install/type-check/build/contract/browser paths. No implemented schema,
generator, application code or implementation-readiness pass is claimed here.
