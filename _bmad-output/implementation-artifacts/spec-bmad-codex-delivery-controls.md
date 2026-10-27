---
title: 'Lightweight BMAD Codex model-selection trial'
type: 'chore'
created: '2026-10-27'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
baseline_commit: '124efa97546e5f5ab93eee3e2341451701fda425'
context: []
---

<frozen-after-approval reason="user approved narrower rollout on 2026-10-27">

## Intent

Try simple model selection during direct BMAD delivery: Sol High by default, Terra
Medium for bounded delegated work, no forced review-finding quotas, and concise
session checkpoints. Use existing BMAD verification and collect basic observations.
Defer the custom evidence/session helper, Codex hooks, automatic enforcement and
builder CLI integration. Preserve Leave's existing CONTENT-READ checkpoint without
resuming product delivery in this setup task.

## Boundaries & Constraints

Use supported sparse team overrides; never edit generated skill files. Apply model
and effort explicitly at delegated launch. Preserve installed same-capability review,
oneshot inline implementation and existing approval/test/release rules. Missing or
uncertain classification defaults to Sol High. Do not claim cost or speed savings
without measurements. No global model defaults, custom runtime, new approval gates,
automatic session replacement, production changes or unrelated worktree edits.

</frozen-after-approval>

## Implementation Notes

The user explicitly narrowed and approved scope after the original full-integration
spec. Its original spec, proposal, helper and tests are preserved privately under
`../../.local/bmad-codex-deferred-20261027/`; they are not installed or part of this
rollout. The approved narrowing replaces the earlier frozen contract, rather than
claiming the deferred machine-gate requirements were implemented.

Current scope is a small configuration/documentation change with no remaining intent
gaps or irreversible actions, so the BMAD route is now oneshot. Parent implements
inline and runs one context-free review at inherited session capability. The prior
worktree was already dirty; only the listed new files belong to this change.

Impact: scaffold — no change; shared UI — none; agent context — short policy loaded
only by build workflows; documentation — one policy/usage page and this evidence;
ADR — none, existing governance unchanged; database — none.

## Tasks & Acceptance

- [x] `../../platform/docs/development/bmad-codex-usage.md`: short policy for selection, existing evidence, session boundaries and lightweight observation.
- [x] `../../_bmad/custom/bmad-build.toml`, `bmad-build-auto.toml`: explicit implementation handoff; policy reference; quota-free blind review. Retain other review layers and ordinary BMAD controls.
- [x] Given either build workflow, when resolved/rendered, then the new handoff selects explicit model/effort with Sol High default, retained review layers have no quota regression, and no helper/hook dependency is present.
- [x] Given a bounded read-only Leave task, when dispatched on Terra Medium, then a cited concise result returns without changing implementation status or activating fixtures.
- [x] Given verification, when reporting results, then distinguish resolver/render/live-agent proof from unmeasured cost or speed savings.

## Spec Change Log

- 2026-10-27: User approved narrower rollout; defer helper/hooks/enforcement. Preserve original work privately. Replaced intent/tasks with the approved trial and selected oneshot route.

## Review Triage Log

One context-free reviewer at inherited coordinator capability ran the installed
quota-free oneshot recipe. Result: no supported findings. The reviewer independently
checked actual resolver behavior and preserved review layers. No full dispatch layers
are disabled; no findings were silently dropped. Live-agent proof belongs to the
separate Terra trial, not this independent configuration review.

## Verification

Baseline: actual resolver returned empty persistent facts, inherited-only implementation
handoff and a mandatory finding floor before override installation.

Resolve both workflows via `_bmad/scripts/resolve_customization.py`, render both via
SKILL entry points, inspect preserved layers/settings and absent helper dependencies,
and execute one bounded read-only Terra Medium task. No product suite or persistent
custom tests are needed for this configuration-only change.

## Trial observations — 2026-10-27

- Selected and launched `gpt-6.1-terra`, reasoning `medium`, with no inherited conversation,
  for a read-only summary of the existing CONTENT-READ checkpoint and policy. A result
  returned with source/line references, correctly preserving in-review status, B1/B5/B8
  engineering-spec loopback priority and the DISCOVERY hold. Parent checked these claims
  against the checkpoint. No edits, fixtures or product implementation were requested.
- The model/effort values were explicit launch settings. The tool did not expose separate
  billed usage, actual routed-model metadata or isolated model execution time; those
  remain unknown. This proves the bounded delegation path works here, not cost savings.
- Both actual resolver runs passed; interactive review layers remain blind-hunter,
  edge-case-hunter and verification-gap; auto additionally retains intent-alignment.
  Only blind-hunter/oneshot quota wording changed. No custom completion hook or helper
  dependency resolved.
- Both actual render commands passed. Interactive snapshot:
  `../../_bmad/render/bmad-build/agriplatform-cc7e2d5786a0/bb796ada00c906bb038e/`.
  Auto snapshot:
  `../../_bmad/render/bmad-build-auto/agriplatform-cc7e2d5786a0/8c59913412a02ef5ee19/`.
  Rendered handoffs contain both explicit model settings, rendered reviews permit zero
  supported findings, and both activation sections reference the short shared policy.
- Commands: `uv run --no-cache _bmad/scripts/resolve_customization.py --skill
  /home/ck/repos/innodat/agriplatform/.agents/skills/<skill> --project-root
  /home/ck/repos/innodat/agriplatform --key workflow`, for `bmad-build` and `bmad-build-auto`;
  `uv run --no-cache _bmad/scripts/render_skill.py --project-root
  /home/ck/repos/innodat/agriplatform --skill
  /home/ck/repos/innodat/agriplatform/.agents/skills/<skill>`, for both skills.
  Resolver output was checked for explicit settings, required layer preservation,
  empty completion callbacks and no `controls.py` reference.
- No product acceptance suite ran: this rollout changes only configuration/documentation.
  No custom helper tests or hook trust are presented as trial evidence. All such work is
  deferred, and the existing Leave checkpoint remains the resumption source.
