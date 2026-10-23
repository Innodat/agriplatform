---
title: 'KDG numeric email-code template contract qualification'
type: 'feature'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Qualify a reusable, unactivated numeric-email-code template/configuration candidate for KDG's approved existing-account Supabase Auth flow. Add a neutral template and explicit six-digit/3600-second/60-second resend configuration fragment, then prove offline that it maps to the pinned CLI2.120.0 GoTrue template URL and Kong mount, without changing native preparation or any running service. Keep automatic signup, anonymous access and manual linking disabled; current API admission remains separate. Numeric templates use only the Token variable, no sign-in links or external resources. Record boundaries for non-delivery, expired/used codes, resend and session recovery; do not invent actual Auth behavior from simulation.

Keep all work synthetic local/CI, test-first, reversible and source-bound. Preserve concurrent work, historical evidence/configuration, Docker resources and approved dependencies including TypeScript7.0.2. No real email/account/access, provisioning, production, deployment/pilot, Leave/editor, cleanup or fingerprints/HMAC. Put generic artifacts and qualification tests under the platform owner and reference them from scaffold guidance rather than duplicating per-app tests. No automatic template adoption by generated applications or native ENV runs.

</frozen-after-approval>

## Implementation Notes

- bmad-help selected [BD] Build after completed email-code entry delivery d0b942c396be9e252d096cb64188fb24a2e1b42b. Freeform prerequisite, not full Story1.1. User authorized continuation with concurrent-change preservation, satisfying dirty-tree scope; snapshot /tmp/kdg-email-template-preservation.json records the baseline. No need to reapprove existing scope.
- Investigation: exact retained CLI source fixtures/supabase-gotrue-source/gotrue.service.ts maps email.template ids, OTP length/expiry and max frequency; fixtures/supabase-kong-source/kong.service.ts builds read/write template bind intent. Existing test_gotrue_source.py supplies offline relocated-import source execution with selected tool artifact. Keep historical selected-input/public-environment and dev.configuration unchanged. Official Supabase passwordless/local-template docs establish magic_link and Token semantics; CLI accepts arbitrary template IDs and alone cannot establish Auth support.
- Plan: test_email_code_contract.py acceptance RED for missing template/config, focused source/mapping tests, then platform/deployment/fixtures/email-code-v1/config.toml and sign-in.html. Fragment is not standalone config or active ENV input. Add fixture README, KDG EMAIL_TEMPLATE_CONTRACT_EVIDENCE and receipt, prepended next-session handoff, scaffold application README reference. Skip generic application code changes; existing lifecycle/SDK recovery proof stays immutable.
- Acceptance: given the candidate, offline inspection finds code-only content and closed existing-account policy; given pinned builder sources and qualified Node artifact, mapping uses MAGIC_LINK template/subject, six digits,3600s expiry,60s server resend intent and matching Kong path; given default native preparation, template/mail remain unactivated. Missing artifact must fail acceptance; source mismatch fails before builder execution. Server rendering, SMTP transport, token expiry/single-use/resend execution and real sign-in are explicitly not proved here.
- Impacts: scaffold guidance references shared opt-in platform artifact/test, no generic default Auth choice or ownership inventory change; shared UI not applicable (email artifact only); agent context unchanged; documentation/evidence required; accepted ADRs unchanged, applies0023/0032. No intent gaps, irreversible actions or new runtime public API; small oneshot route.
- Investigation correction before artifact implementation: CLI auth.email.enable_signup maps to GOTRUE_EXTERNAL_EMAIL_ENABLED, while auth.enable_signup controls GOTRUE_DISABLE_SIGNUP. Pinned Auth4eee58f296d9698a1c2c0ae14d7a0b379c7622d3 MagicLink explicitly rejects email-provider-off requests. Candidate must set email.enable_signup=true with global signup=false and existing client shouldCreateUser:false, preserving the approved no-account-creation intent. This does not change inactive native config or historical closed profiles. No human-visible method/policy change or irreversible work.
- ATDD RED observed missing template/config acceptance before creation; focused content/policy checks GREEN. Publisher source execution verifies template/subject URL,6 digits,3600s, normalized1m0s frequency, signup disabled, email enabled, anonymous/manual linking disabled and matching mount intent. Full tests use selected Node26.11.1/Python3.15, no installs or Docker.
- Review Blind Hunter only; other layers not configured. Five findings accepted and patched, no deferrals. Follow-up static inspection confirms fixes; one strict-mode wording inconsistency in KDG evidence was corrected. Reviewer did not rerun tests. Final counts/exact commands/log and source hashes are in apps/kdg-capture/docs/evidence/email-template-contract-20261023.json.
- No application runtime or generated Auth code changed, so prior SDK/browser138/42 evidence remains historical and hash-preserved rather than claimed rerun. Builder68 and affected native/config/source tests cover the changed guidance/candidate. No full fresh app generation needed for a guidance-only renderer change. Native closed profile and root dependency locks unchanged.

## Review Triage Log

1. medium — patch: ordinary discovery could skip publisher proof and exit zero. Added explicit KDG_EMAIL_CODE_REQUIRE_PUBLISHER=1 qualification mode; missing selector now fails with zero skips. Before-fix single publisher invocation skipped despite required flag; final negative control confirms refusal. Optional discovery remains documented.
2. medium — patch: output assertions omitted anonymous/manual-link restrictions. Both publisher output keys are explicitly false in final mapping check.
3. medium — patch: native-preservation test did not protect email provider-off state. Added explicit auth.email.enable_signup=false assertion; no native generator/config change.
4. medium — patch: text extraction included title/head. A title-only-token mutant observed RED; body-only text plus document-parent/count assertions now reject it, final counterexample GREEN.
5. low — patch: missing prose spaces obscured versions/timing. Corrected new fixture/KDG guidance and handoff spacing, preserved historical suffix. Follow-up strict-mode evidence wording aligned with actual behavior.
