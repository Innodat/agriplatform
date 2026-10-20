---
title: 'ENV Kong public native key fixture'
type: 'feature'
created: '2026-10-20'
status: 'done'
route: 'oneshot'
review_loop_iteration: 1
---

<frozen-after-approval reason="standing bounded ENV implementation and synthetic verification approval">

## Intent

Replace the existing closed Kong fixture's four placeholder markers with the pinned
publisher's public local-development default opaque keys and exact default HS256
anon/service_role tokens. Given the approved no-override/no-signing-file synthetic
target, its rendered bearer/query substitutions must match those public defaults;
wrong transfer bytes and caller overrides still refuse without exposing values.
Prove the fixed tokens against independent HMAC verification and the retained pinned
publisher signer executed with the already qualified Node artifact. Keep keys fixed
and public: no generic signer, credential input, production key path or new service.
Keep create/transport/image/custody/deadline and readiness gates unchanged. Observe
acceptance RED first, focused TDD and affected owner/process checks; record source
frames and scaffold/UI/context/docs/ADR impacts. Preserve prior receipts/resources
and concurrent work. No actual Docker execution or functional Auth claim is part of
this fixture increment; new source-bound prerequisites precede future actual startup.

</frozen-after-approval>

## Implementation Notes

- bmad-help selects the remaining native-key prerequisite after actual Kong lifecycle
  PASS. bmad-build one-shot: fixed existing fixture/two test modules/documentation,
  no new caller API, intent gaps or irreversible effects. Standing dirty-tree
  preservation approval applies; all concurrent untracked work remains untouched.
- Reuse create_profile.KONG_KEYS and kong_transfer_files; retained Defaults.ts,
  go-jwt.ts and local-config-values.ts settle the public key/HS256/default branch.
  Snapshot bytes/manifest and all runtime controls remain unchanged. No generator.
- Independent public source signer proof reuses Node26.11.1 from ad277eef's verified
  payload, with full payload fingerprint checked. This does not requalify that old
  source-bound startup receipt for new source or prove the complete publisher CLI.
- Protected/source/index checkpoint and serial exact-command evidence live under
  platform/deployment/.local/kong-native-keys/.

- Acceptance RED is the new public key/transfer oracle mismatch before runtime edits.
  Fixed tuple values are then copied from independently verified public authority,
  with no runtime signing logic. Existing independent source renderer uses the HMAC
  oracle; no template/archive/transport or original source snapshot is changed.
- Initial tests exposed missing origins and a shared oracle alias in fixture setup;
  fixed test-only inputs/reuse. The first affected socketpair write lacked sandbox
  permission; authorized Unix-peer rerun is separate. All original logs remain.
- Offline pinned Node proof verifies payload fingerprint and both public role tokens
  against independent HMAC, with executable/source hashes and no token diagnostics.

- All79 selected methods pass on one unchanged48-file source frame:55 profile/
  lifecycle,20 Kong owner and4 process methods/five scenarios. Native values stay
  absent from process/qualifier output. No host Docker or full-suite claim.
- Source AST audit confirms only KONG_KEYS changes at runtime; all27 functions and
  the rest of the module are unchanged.412 protected files/index and the other45
  initial source bindings remain unchanged. Five impacts and limitations recorded.


## Review Triage Log

- Finding1 — medium, patch: standalone proof trusted a colocated receipt and only
  recorded executable hash. Hardened v2 enforces known receipt/executable/manifest
  hashes before execution, then verifies payload fingerprint and unchanged bytes.
- Finding2 — medium, patch: verified source files were reread for execution/oracle.
  V2 uses verified immutable in-memory source bytes, then rechecks source/manifest
  bytes after execution. Old script/result preserved; no artifact is repaired.
- Finding3 — medium, patch: auth-kong-positive bypassed stderr capture. Contained
  key-injection regression reproduces missing assertion before fix; capture both
  streams for all Kong scenarios, retaining safe diagnostics and result semantics.
- Finding4 — low, patch: combined environment sentinel coverage lacked independent
  cases. Test each of seven overrides separately and together in isolated environments.
- Finding5 — low, patch: transfer mutation replaced first key occurrence only. Test
  every occurrence independently, including later bearer/query positions.
- Finding6 — low, patch: standalone proof linked source signer to oracle only; the
  separate acceptance test linked runtime. V2 also compares delivered KONG_KEYS and
  binds/rechecks runtime source, making standalone reproduction complete in scope.


## Final Verification

All six findings patched, none newly deferred. Hardened source proof PASS1.660s;
contained stderr acceptance RED observed before capture fix. Final9 methods
PASS38.528s on48 unchanged bindings;80 distinct selected methods pass across frames,
not all rerun on final helpers. Only two test modules change after the pre-review
79-method frame; runtime/other46 bindings stay identical.412 protected files/index
and initial source delta pass final audit. No host Docker/actual new-key/full-suite
claim. Existing runtime/scaffold/dependent and authorization gates remain intact.
