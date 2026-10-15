# ENV planned base-image identity qualification — 2026-10-15

This bounded ENV increment binds four planned KDG base images to retained registry
manifest bytes. The [Build record](../../_bmad-output/implementation-artifacts/spec-env-base-image-identities.md)
tracks acceptance and review under the existing
[environment contract](../docs/architecture/contracts/scaffold-environment-and-generation.md).
Public collection, immutable repeat and independent review are complete.
Runtime readiness remains false.

## Selection and boundaries

Supabase CLI2.120.0's pinned source commit is
`753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4`. Its
[service Dockerfile](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/shared/services/Dockerfile)
and [startup plan](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/commands/start/start.gates.ts)
identify the planned PostgreSQL17, Kong, Auth and PostgREST base versions.
The exact selection is [image-pins.json](image-pins.json).

| Publisher reference | Selected metadata registry |
| --- | --- |
| supabase/postgres:17.11.0.004 | public.ecr.aws/supabase/postgres |
| library/kong:2.8.1 | public.ecr.aws/supabase/kong |
| supabase/gotrue:v2.197.0 | public.ecr.aws/supabase/gotrue |
| postgrest/postgrest:v16.4 | public.ecr.aws/supabase/postgrest |

The collector admits only this primary ECR registry. It does not equate mirror
digests or implement a startup resolver. The source's legacy backend, slim disabled
and absent dotenv/linked-version overrides describe this selection; actual runtime
enforcement remains undelivered. The CLI services catalogue omits Kong and does not
prove startup/helper completeness. Configuration PostgreSQL17 is not evidence of
compatibility with a live deployment database.

Initial public metadata probes found all four tags. ECR returns an anonymous `aws`
authentication challenge and omits Docker-Content-Digest on these responses. The
collector therefore must verify computed raw SHA256 through digest-addressed reads,
with separately bound Linux/amd64 child metadata. Tokens remain memory-only.
No layer/config blobs, real Docker calls, startup, migration or account action is
part of this qualification.

## Acceptance and executed proof

The preimplementation acceptance command
`python3 -m unittest discover -s platform/deployment/tests -p test_images.py`
failed because `images.py` was absent. Its public missing-preparation assertion now
passes with safe JSON, exit2 and no stderr. Focused metadata/persistence tests were
added with implementation. The actual CLI smoke then refused `cli_state_not_unlinked`:
the CLI creates an empty `.temp/cli-latest` and private telemetry state even with its
update/telemetry flags. A regression test reproduced the refusal before the fix.
Only that bounded generated version marker is now admitted; project links, version
overrides, dotenv, config mutation and links still refuse. Private telemetry is
discarded with temporary state and never copied into evidence.

The collector's actual direct smoke retained eight manifests under ignored
`.local/base-image-proof/registry-smoke-1`, with explicit direct-function scope.
The subsequent public command published the qualified receipt:

```sh
python3 platform/deployment/images.py qualify \
  --target platform/deployment/environments/kdg-local.json \
  --run-id 0cc4bc48-505e-41c1-8876-25b2d49b5694
```

The pre-review collection and repeat both exit0 with `base_identities_ready=true` and
`runtime_ready=false`. Evidence is under ignored
`.local/kdg-base-images/0cc4bc48-505e-41c1-8876-25b2d49b5694`.
The repeat preserves all ten files' bytes, inodes, nanosecond mtimes and0600 modes;
the directory is0700. Snapshot evidence is `.local/base-image-proof/repeat-1.json`.
Synthetic tests independently make any repeat registry call or CLI catalogue capture
fail. Existing tool qualification reruns without installing or changing its receipt.

| Image | Retained index SHA256 | Linux/amd64 child SHA256 |
| --- | --- | --- |
| postgres | `6058a6759ab9268cff8ee70641d61f1bd75953316281b76427cf5a6b4db2eafc` | `f2a84af37797675f0b27e27ea1fad2ebcd913ebf7ad60be05d7df0bcbd29e4b5` |
| kong | `1b53405d8680a09d6f44494b7990bf7da2ea43f84a258c59717d4539abf09f6d` | `e21b0b793879ab96720ed4188f9441260273f4bf775bcbff8d435e019ffb759a` |
| gotrue | `1736a63078f5922b198c4cbe50f80ab9a2d3b54fe8b7b6cfb2e9dc5dbbc12c6b` | `839f529492d116b4e8b7777c953a27c381d34c15a744b1bcefde5eefaa1f9f9f` |
| postgrest | `d155c6718ed9a9f990d159a2ab7c0a3f16944dbb6d0a0344557421042acfe0df` | `bee9e1efe9d90d8f6be359f756e039dbb6e1972474bc271b7c49c5a495911a41` |

Pre-review receipt SHA256: `cdaabf20e5a760e17d720770c4c87e7166146b9cc82ae13a5cb8f58d341d5117`.
Selection SHA256: `4a6aaa4ba69c1add850cd014dca12801625a8b73c61d29b2aa59048632f1c293`.
Tool receipt SHA256 remains
`4efad618046ecda6459da9680b23e9cd47375181a059b33f6838ad8acde6ecc2`.
The receipt binds the exact preparation, target/config and local source identities;
upstream identity is the pinned commit and URLs, without separately retained source bytes.

| Requirement / matrix row | Executed tests in tests/test_images.py |
| --- | --- |
| Four exact publisher pins, closed registry and CLI catalogue | exact_catalogue; unlinked_cli; collect_only_eight_exact_manifest_requests; actual public qualification |
| Raw digest/media/schema/platform and child binding | redirect_status_digest_header; absent_digest_header; invalid_schema_platform_child_and_config_shapes |
| Exact auth realm/scope, tokens never retained, no layers/daemon | auth_token_memory_only; anonymous_tokens_never_persist; collect_only_eight; cli_environment_private_socket |
| Bounded body/header/DNS/command/deadline behavior | https_worker_rejects_oversize; worker_bounds_dns; bounded_cli_execution |
| Changed target/preparation/source/payload; no install/repair | changed_target_preparation; missing_receipts; input_mutation; payload_inode_replacement |
| Immutable repeat, modes/links/extra/partial evidence | protected_complete_repeat; tamper_modes_symlink_extra_hardlink; partial_file_write |
| Concurrent writer, replaced directory, interruption | concurrent_writer; replaced_output_inode; timeout_and_interrupted_publication |
| CLI-generated cache versus linked/version overrides | cli_generated_latest_marker; actual refusal and corrected public collection |

`python3 -m unittest discover -s platform/deployment/tests -p test_images.py -v`
passes25 tests in1.700s. The affected owner command
`python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`
passes207 tests in20.902s. The initial sandbox run could not create synthetic sockets;
the permitted retry passes without changed expectations. A sandbox public repeat also
refused the existing tool subprocess; the permitted repeat passes with unchanged files.
`git diff --check` passes. No root npm wrapper or image execution counts as verification.

## Independent review and final qualification

Three independent reviewers produced13 finding instances; all were fixed, none deferred.
The Build record preserves every verdict and reproduction. Exact inventory bytes and
directory/ancestor protection are rechecked before completion. CLI output uses bounded
pipes rather than temporary-file polling; a continuous writer proves at most limit+1
bytes are captured and its process group exits. Controlled DNS/header/body stalls pass
through the actual HTTPS worker and leave no active worker. Nonempty platform feature
requirements refuse. Distinct per-image fixtures now bind each exact path and receipt
identity; real owner-preflight tests exercise success, refusal, changed results/receipt
bytes/inodes and private arguments/environment. The hardlink test reaches the single-link
guard through a link outside the evidence directory. Public acceptance uses a fresh UUID.

Eighteen publication fault points cover pending creation, link/unlink, file/directory
synchronization, final validation and foreign receipts/pending files/locks. Failed fresh
publication retains a blocker even if receipt.json was already linked; subsequent
qualification refuses without adoption or repair. Failed lock-release synchronization
restores only an absent blocker. Foreign evidence is preserved. A receipt file by itself
is not readiness. Preexisting pending files and stale locks remain unqualified.

Review changes invalidate the earlier source-bound receipt, which is preserved.
Final proof uses a deliberately fresh run, with the same target and approved tools:

```sh
python3 platform/deployment/dev.py prepare \
  --target platform/deployment/environments/kdg-local.json \
  --run-id b3b805d5-adc6-4168-a79c-5945547d3320
python3 platform/deployment/toolchain.py qualify \
  --target platform/deployment/environments/kdg-local.json \
  --run-id b3b805d5-adc6-4168-a79c-5945547d3320
python3 platform/deployment/images.py qualify \
  --target platform/deployment/environments/kdg-local.json \
  --run-id b3b805d5-adc6-4168-a79c-5945547d3320
```

Preparation and tool qualification pass using the existing verified archive cache;
no owner lock or installed checkout package is changed. Final public image collection
and repeat pass, retaining the same four index/child identities listed above. All ten
files preserve bytes, inodes, mtimes and modes; ignored snapshot evidence is
`.local/base-image-proof/final-before.json` and `final-repeat.json`.
The33 focused tests pass in3.207s after review. The final affected owner command
`python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`
passes215 tests in23.190s. Repeating the earlier0cc run now returns exit2,
`evidence_binding_changed`, with all ten files unchanged against its pre-review
snapshot. Scoped whitespace and four-document local-link checks pass.

Final source SHA256:
`08228672d0f535df35fd86b001e9d04fa59307b97aecb304324b1d98c3bfa431`.
Final test SHA256:
`437ec6a6e46fa59aed4900bb07526d15bdb6f8a9f7f70ca2faef4278a9ee1272`.
Final tool receipt SHA256:
`cd51c5037f1e3a59e3c7973619f15956428dbfbcf832bdc8fa3de16108c2af9a`.
Final image receipt SHA256:
`a5c87518beb3333d163452adce3912afb63c54f1362f1f765b8d660fab94ecb3`.

## Five impacts and remaining gates

- Scaffold: ENV evidence only; existing P1/SERVICE generator/schema/template/client
  owners retain implementation. No generated output or reusable runtime pattern.
- Shared UI: no change.
- Agent context: existing root instructions suffice; owner commands belong in the
  [runbook](DEVELOPMENT.md).
- Documentation: this evidence, owner runbook, Build record and KDG navigation.
- ADR: existing ownership, dependency, release and logging decisions apply; no
  accepted decision changes.

Docker>=28, an isolated runtime adapter, complete startup/bootstrap image inventory,
digest binding at startup, deployment PostgreSQL compatibility, owner migrations,
P1/SERVICE, Identity/Access/WRITE, Entra and installed-device evidence remain open.
No production migration, infrastructure, access/account, deployment, Leave/KDG domain
or real-data pilot work is authorized by this evidence.
