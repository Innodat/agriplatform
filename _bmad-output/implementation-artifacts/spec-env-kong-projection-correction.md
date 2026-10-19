---
title: 'ENV observed Kong container projection correction'
type: 'bugfix'
created: '2026-10-19'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
---

<frozen-after-approval reason="standing bounded ENV implementation and disposable qualification approval">

## Intent

Correct the existing Kong effective-container validator for the two differences
observed in actual Docker API1.48: omitted null Config.OnBuild and reordered identical
proc-protection members. Preserve exact nonempty protections, reject duplicates and
wrong types/non-null OnBuild, and keep image validation, create/transport authority,
all deadlines and custody rules unchanged. Observe owner/process acceptance failure,
apply focused TDD, then qualify a fresh source-bound disposable local run and ordinary
compatibility through existing commands. Preserve concurrent work and all historical
receipts/resources. Record requirements/tests and scaffold/UI/context/docs/ADR impacts;
full runtime readiness and dependent work remain gated.

</frozen-after-approval>

## Implementation Notes

- bmad-help selects the actual observed projection blocker; bmad-build one-shot:
  small existing-validator/test correction, no intent gap/new public API or additional
  irreversible effect beyond already authorized disposable local verification.
- Reuse create_profile.validate_kong_container, KongExecutionOwner returned-inspect
  seam and ExecutionSupervisor private process positive control. Keep canonical
  install_kong_peer and image Config fixture unchanged; no other missing-null field
  receives generalized admission. Protection order is immaterial, membership is exact.
- ATDD/focused TDD first; affected tests then fresh prepare/toolchain/images and
  public Kong qualifier, ordinary control only after success. Stop on actual refusal,
  preserve resources; no recovery removal without exact separate approval.
- Standing dirty-tree preservation approval applies. Checkpoint and source-bound
  results live in platform/deployment/.local/kong-projection-correction/.

- Fresh actual run reaches running Kong after the original two corrections, then
  rejects the post-start null OomKillDisable projection. Source trace identifies
  HostConfig scalar-default comparison; an in-memory false-default simulation is
  diagnostic only. No actual retry or ordinary control follows this refusal.
- Investigate this newly exposed post-start default within the same existing-owner
  qualification goal. No request, public API, deadline or custody change is proposed.
  Exact failed-run cleanup was pending at that checkpoint; explicit approval and
  verified cleanup have since completed. Keep the
  original frozen intent intact and record any further correction separately.

- Original two corrections complete:16 owner,133 affected contract and3 private
  process methods pass on the same47 bindings. Fresh prepare/toolchain/images pass;
  actual Kong refuses unsafe_create77.3s at post-start OomKillDisable=null. No OOM code
  change, ordinary control or resource execution retry. Actual acceptance remains open.
 235 protected files/index/13 new receipts remain unchanged. Requirement-to-test,
  exact commands/results and five impacts are in ENV_KONG_PROJECTION_EVIDENCE.md.

## Review Triage Log

- B1 medium, patch: new negative mutations refused at created state. Added hostile
  projections first appearing at running/exited, proving lost custody blocks later
  PG stop/Kong disposal and cleanup success, with no cleanup observations replayed.
- B2 medium, patch: accepted normalizations were separate from hostile content.
  The late-state matrix combines omitted OnBuild/sorted protections with non-null
  OnBuild, same-length missing/extra protection replacement, unknown Config and
  changed host memory; all reject and preserve the remaining resources.
- B3 medium, patch in part: absent protection keys are already covered by selected
  test_effective_protections_ports_and_endpoint_options_are_closed while running
  (masked-absent/readonly-absent), disproving that portion. Added same-cardinality
  replacement and complete tuple/set/dict projections to guard membership/type checks.
- B4 medium, patch: mutable master links weakened source evidence. Resolved Moby
  v28.0.0 to af898abe44662d9554fb15ee4d4a7307f1b8e315, inspected both raw files and
  pinned permalinks/symbols with hashes. Not attributed to exact29.9.1 or host capability.
- B5 medium, patch: full actual response was not retained for offline replay. Added
  sanitized selected-field observation fixture and canonical synthetic reconstruction
  that reproduces current null-OOM refusal, clearly distinguishing captured fields
  from synthetic identities/Config. No OOM policy or runtime change in review.

All five findings individually triaged; no new review deferral. Final3 review methods
pass on48 bindings.154 distinct IDs pass across recorded frames, not all rerun on final
bytes. Exact cleanup was explicitly approved and completed with both exits0/no force/
four404 checks; initial container/network IDs and volume names restored. Actual Kong
qualification and remaining ENV/scaffold/dependent work remain open.
