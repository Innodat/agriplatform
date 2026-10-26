# Leave planning — final consolidated review

**APPROVED — 2026-10-26:** The user explicitly approved this completed package.
Platform ADR-0064 and Leave ADR-0171 record adoption. CE complete; SP planning-readiness
PASS. Implementation held for a new Codex session at the user's request.
The proposal wording below is the unchanged text that was approved.

**Date:** 2026-10-26. **Status:** Planning complete as a candidate; ready for your one review.

E5 planning is finished. You do not need to reread its stories. Your accepted E6 choices,
E7 and E8 stay in place. The full planning check is complete; the remaining review is of
the following technical choices together.

## Choices proposed for approval

| Area | Proposed choice |
| --- | --- |
| Invitation safety | Invitations last seven days. Resend replaces the old link. After sign-in, a new recipient verifies a fresh code sent to the invited mailbox; known recipients must use the exact invited account. Prepared access lasts thirty days and activates only after verified onboarding and current role/authority checks. No automatic employment or default roles. |
| Organization administration | Keep at least one active owner and one explicitly authorized Organization Administrator. Block ordinary self-removal; another authorized administrator handles removal after continuity is secured. Membership and role changes share one local guard in their existing service. |
| Working time and holidays | Default net hours stay simple. Advanced timetables subtract breaks/clock closures once. A clock-based holiday needs an actual timetable; duration reductions work with net hours. Use nominal local-clock quotas across daylight-saving changes, so a 01:00–04:00 timetable stays three hours on either transition. Preserve exact halves: a half of 435 minutes is 217.5 minutes. |
| Private documents | Authenticate each private download through the owning application and stream from Content. Seal verified upload bytes and protect pending/saved references through retries and cleanup. |
| Medical-document retention | Propose a 24-calendar-month default, configured 1–1,200 months, jurisdiction override before organization/default and the longest applicable jurisdiction period. Keep recorded closed-document deadlines; changed settings apply prospectively. Saving settings never deletes documents. |
| Shared foundations | Keep Identity, Access, People, Content and notification ownership. Use assisted verified Entra tenant setup with automatic enrollment initially off, and Identity-owned account language preferences. Prove reusable scaffold/UI patterns with their first consumers. |
| Delivery boundaries | Keep 310 bounded items in their existing dependency order. E4 has six actual shared/Leave child boundaries with original parents retained for traceability. Keep the 28 explicit acceptance additions across fifteen existing items; original criteria remain intact. |

These choices are candidates for this review; they have not been silently marked approved.
The detailed contracts cover limits, conflicts, expiry, concurrency, attribution and recovery.
They do not require another guided reading of all the stories.

## Completed checks and implementation boundary

All five source documents and their 1,219 body units plus 48 YAML records have been
reconciled. The independent earlier-story check covers 115 leaves and 837 Given blocks;
E5's original 230 criteria are preserved. The whole delivery graph has 310 items,
1,564 dependency edges and 66 acyclic layers. Final contract bindings resolve the three
remaining planning inputs without adding a story or changing an acceptance criterion.

The [readiness assessment](implementation-readiness.md) records one remaining concern:
approval of this consolidated candidate. No additional technical planning gap was found
in the final pass. Approval settles the planning choices; formal BMAD readiness and
implementation authorization are recorded afterward. The first Leave slice remains
sign in → select organization → create/resume → autosave → close → reopen.

Only planning documents changed. No application implementation, email, import, live
grant/provider change, migration, deployment or commit was performed. Document checks
are not claimed as runtime/provider/browser tests.

## Supporting evidence

- [Current whole-product validation](whole-product-validation.md)
- [Final contract decisions and affected story bindings](final-contract-reconciliation.md)
- [Implementation readiness assessment](implementation-readiness.md)
- [Independent criterion reconciliation](early-criterion-reconciliation.md)
- [Delivery items and dependencies](whole-product-delivery-register.md)
- [Early item sizing](early-story-size-assessment.md) and [E4 boundaries](e4-owner-boundary-assessment.md)
- [Invitation protocol](../../platform/docs/architecture/contracts/organization-invitation-and-prepared-access.md)
- [Administrator continuity](../../platform/docs/architecture/contracts/organization-administrator-continuity.md)
- [Work/calendar precision](../../apps/leave/docs/architecture/contracts/work-calendar-and-minute-precision.md)
- [Document retention](../../apps/leave/docs/architecture/contracts/document-retention.md)
- [Content association](../../platform/docs/architecture/contracts/content-association-and-reclamation.md)
- [Authenticated downloads](../../platform/docs/architecture/contracts/content-ownership-and-authenticated-read.md)
- [Trusted Entra setup](../../platform/docs/architecture/contracts/trusted-entra-organization-enrollment.md)
