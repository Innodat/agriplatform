# Final architecture rubric and input reconciliation

2026-10-14. Independent installed BMAD architecture Reviewer Gate; good-spine rubric
and reconciliation against current PRD/EXPERIENCE, final engineering closure in
contracts.md and final-planning-validation.md. Only this report was written. No
implementation, dependency installation, application tests or physical-device checks.

## Verdict

The feature-level spine fixes the consequential divergence points and preserves the
latest approved product boundaries. No critical/high finding. Planning coverage can
pass while implementation readiness remains failed on the explicitly identified shared
owner and engineering gates; that distinction is correctly retained.

Open findings: **0 critical, 0 high, 1 medium, 1 low**.

## Findings

**Medium — Deferred/Open paragraph ambiguously groups already approved product choices
with genuine open decisions.** ARCHITECTURE-SPINE.md, Deferred and Open Decisions,
says “Administrator create-all, own history after unassignment, phone-local today,
30-day download and saving classification was revised …”. The current PRD A-1–6
explicitly resolves those policies, including own-only 30-day downloads. The paragraph
does not cleanly tell a downstream consumer which decisions remain open. *Autofix:*
separate genuine shared schema/generator/operator/fingerprint and pilot gates from a
short list of approved app policies. Do not reopen approved requirements or claim their
implementations exist.

**Low — Intermediate-scale content gate retains the former range.** PRD O-3 says
“1–4 descriptions” remain open, although current FR-5 and engineering closure define
1 = Goed and 5 = Nie goed nie. The actual undecided intermediate descriptions are
**2–4**. *Autofix:* narrow O-3 to 2–4; keep all five numbered choices and numeric
labels available without clinical interpretations.

## Good-spine rubric

| Criterion | Assessment |
| --- | --- |
| Real divergence points | Covered: service ownership, current authority, fixed org, version identity, atomic local save, ordered retries, current revisions, local partitions, updates and release coordination. |
| Enforceable rules | AD rules identify transaction/command/partition boundaries, fail-closed checks and observable acknowledgement conditions. Exact implementation models remain story inputs. |
| Deferred work cannot silently diverge | Shared account/actor/membership union, trusted operator/target, generator and fingerprint sensitivity are explicit pre-Build gates rather than permissive defaults. Improve the approved/open paragraph as above. |
| Brownfield consistency | Existing Auth/Access/Identity/runtime HTTP boundaries and builder owner are retained. Accepted designs and template/package evidence are explicitly distinguished from working KDG functionality. No People or parallel generator dependency. |
| Technology accuracy | Spine names source package/lock reuse evidence and supported Node floor as evidence, not selected KDG pins. Native browser storage/shell technology is a design choice, not proof of device durability. No new current-product claim was introduced by this review. |
| Spec capability coverage | Requirements map covers FR-1–18 and NFR-1–5; final validation maps approved stories without making integrated pilot proof substitute for feature implementation. |
| Inherited invariant integrity | Current server authority, owner-local short transactions/audit, release migration safety, sensitive logging exclusion and structural tenant integrity remain binding. Offline observations never authorize server writes. |
| Operational/environment dimension | Owned migration/runtime/operator separation, targeted synthetic setup, nonproduction HTTPS devices, deployment origin/package gates and pilot privacy/retention/recovery are explicit. No production action authorized. |

## Approved-scope reconciliation

- **Five numbered choices 1–5:** PRD FR-5, EXPERIENCE rating behavior and engineering
  validation agree; 0/6/fractions are rejected. No six-option current form is implied.
- **Explicit observation Save:** unsaved entry/hidden buffers stay in memory; completed
  captures and pending commands commit together. Questionnaire working copies and immutable
  publishing remain separate legitimate configuration lifecycle.
- **Own-only offline, online all-record administration:** AD-7 and final scope amendment
  issue no offline all-read/all-edit; only own responses persist. Administrator create-all
  produces their own capture and does not confer access to another author's device work.
- **Administrator conflicts:** online attempted answers/reviewed base stay in memory;
  no conflict-input server draft, recovery table or resumed admin proposal is required.
  Saved own phone proposals retain their distinct durable resolution behavior.
- **Deactivation:** engineering closure uses a KDG-owned opaque prior-eligibility reference
  from the existing provisioning path; current access/assignment is still checked. It
  explicitly supports stale eligible setup without falsely proving pre-deactivation Save.
  Shared membership-instance and reference retention decisions remain gated.
- **Update first:** no successful queue-drain requirement; settle active work safely,
  wait for unsaved-form Save/Cancel, preserve unknown operation identities, activate,
  then sync. Version handlers/adapters are required only for actual changed formats.

## Narrow engineering seed and readiness limits

Final contracts specify exact command field sets, UUID/revision/date representations,
bounded answers/definitions, safe committed/no-op/unresolved outcomes, scoped cursors,
canonical submitted meaning, eligibility-reference ownership and independent version
behavior. These are sufficiently narrow app build inputs, not a second runtime engine
or generated OpenAPI claim. OpenAPI/Pydantic/generated TypeScript becomes model authority
during implementation.

Canonical encoding does not decide digest confidentiality: predictable child answers
justify the still-open security/write-owner hash-versus-keyed-hash assessment. Shared
scope/target/operator/generation gates remain unresolved and prevent ready-for-development
status. Khula lawful-processing/device/retention policies and real Android/iPhone/release
proof gate later pilot activation. Neither story approval nor this rubric authorizes Build.
