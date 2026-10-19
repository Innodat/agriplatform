# ENV actual owned Kong qualification — refused

Source: `491d7c685fd4c6e4294bf04f5a3373d59b895d33`, run `0840dd32-0342-4138-a454-683dc10bb022`,
Docker Engine29.9.1. The actual Kong qualification **failed**. The qualifier establishes
no gateway health or normal lifecycle shutdown/disposal, complete Supabase stack,
runtime readiness or fresh-setup completion. The bounded verification attempt and read-only diagnosis are recorded
here; the ENV delivery gate remains open.

## Commands and results

Existing commands ran serially from the repository root, with authorized host socket
access. The same fresh target/run and unchanged source were used throughout.

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id 0840dd32-0342-4138-a454-683dc10bb022
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id 0840dd32-0342-4138-a454-683dc10bb022
python3 platform/deployment/images.py qualify --target platform/deployment/environments/kdg-local.json --run-id 0840dd32-0342-4138-a454-683dc10bb022
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id 0840dd32-0342-4138-a454-683dc10bb022 --control pinned-cli-postgres-kong-execution
```

| Command | Exit | Measured total seconds | Result |
| --- | --- | --- | --- |
| prepare | 0 | 0.067 | prepared |
| toolchain qualify | 0 | 19.063 | toolchain_qualified |
| images qualify | 0 | 34.738 | base_images_qualified |
| Kong execution control | 2 | 64.417 | startup / unsafe_create |

Durations include each child command through exit and were measured with a monotonic
clock by the local evidence wrapper. stdout/stderr and exact argv/exit/duration/digests
are retained under `.local/kong-actual/`; commands.json binds all four attempts.
All four stderr files are empty. Operational diagnostic/inventory/audit/cleanup helper
invocations and observed exits are in operational-commands.json. Their total durations
were not retained and are explicitly null; qualification-command durations above are
measured. The Docker-version inline operation has a clearly labeled normalized
reproducible equivalent rather than a claim of literal original shell text. The
execution context records cwd, host/sandbox socket access and Python/platform version;
environment variables were not captured. Earlier inspection helper versions were
superseded; their exact source bytes are unavailable, and no full replay claim is made. No execution retry, receipt repair, deadline change,
ordinary compatibility control or dependent implementation followed the refusal.
The failed qualifier emits only ok=false, stage=startup, code=unsafe_create and
runtime_ready=false. It emits no completed lifecycle/cleanup facts; absence of a
fresh_setup_completed field is not a success. Prior synthetic tests are in
[implementation evidence](ENV_KONG_EXECUTION_EVIDENCE.md), not substitutes for this result.

## Read-only diagnosis and requirement-to-test evidence

Three read-only inspections used explicit GET requests through Docker API1.48 on the
newly retained resource identities. Config environment/command content and logs were
neither printed nor saved. The final safe projection and comparison are retained in
inspection-diagnostic.json; earlier intermediate projections were superseded by this
final projection. The final inspection helper is retained as the method record. Its live GETs cannot
now replay the removed resources; no complete offline response fixture was retained.
Only the safe final projection/comparisons and source-line trace survive. It does not
supply authority to the supervisor, and uses the observed workdir only diagnostically.

| Obligation | Observation / result |
| --- | --- |
| Existing preparation/toolchain/image prerequisites | All three pass with13 source-bound prerequisite files retained |
| Exact effective Kong Config | Offline call to unchanged validate_kong_container rejects at create_profile.py:445; Config.OnBuild is absent while image-derived expectation contains null. Other expected Config values compare equal; no extra Config keys |
| Identified nonempty proc protection paths | After inserting only null OnBuild into a diagnostic copy, unchanged validator rejects at line472. MaskedPaths has identical members in different order, with no missing/extra path; ReadonlyPaths matches exactly |
| Localize the created-state rejection | A second diagnostic copy with null OnBuild and the expected ordering of the identical protection members passes the unchanged validator. This is an in-memory counterfactual, not current custody or actual execution proof |
| No creation/start replay or unsafe disposal after refusal | No resource execution was repeated; Kong was created/unstarted and PostgreSQL running at the failure snapshot. All four new resources were preserved until separate exact recovery-cleanup approval |
| Preserve unrelated resources | The after-failure snapshot adds exactly two run container IDs, one run volume name and one run network ID; no initial identifier disappeared |
| No dependent readiness claim | Actual Kong lifecycle and ordinary compatibility remain unqualified; runtime readiness remains false |

The diagnostic does not qualify running-state port projection, archive transfer,
health, shutdown, cleanup or Auth routing. Next correction must characterize the
observed omission and order variation before changing the existing validator, retain
rejection of non-null OnBuild and missing/extra/duplicate protections, and use a new
source-bound run for actual qualification. Native keys/functional Auth routing,
remaining services and consuming scaffold proof remain later ENV obligations.

## Failure preservation and approved cleanup

Initial/after-failure inventories: containers242→244, volumes281→282, networks14→15.
All original container/network IDs and volume names remain. The four resources retained after failure, then removed under that approval, were:

- Created Kong `1f1c43e8079f7e1246889acd1a459a9397ca65048a6fe6b288795004c32f2721`.
- Running PostgreSQL `a3c6a1600901883bd52411e7b288bcd3ec03f373e87741ca40d7482d5478ee06`.
- Volume `supabase_db_agriplatform-kdg-CEDdMgNCQTikVGg9wQuwIg`.
- Bridge `8e4d7ea2574f477ecb3d6a0290fce5b61f2d132ad48552fcfee94a34670b8be2`.

retained-resources.json and retained-resource-references.json record selected image
identities, exact run labels, mount/network references and states without payloads.
The user explicitly approved this exact four-resource cleanup. The retained helper
rechecked IDs, image identities, labels, states, mount/network references and all
container volume/network users, then removed unstarted Kong, stopped PG normally
(exit0), and removed PG, volume and bridge without force. Each removal was followed
by404 confirmation. cleanup-journal.json retains exact requests/status/durations;
cleanup-result.json records completion. This is separately authorized recovery cleanup,
not the qualifier's normal-cleanup success or recovered lifecycle custody.

Final inventory contains247 containers/287 volumes/14 networks. All original container/network IDs and volume names
remain; the four approved run resources are absent. Five other container IDs and six
other volume names appeared concurrently and were not touched. Do not interpret the
final inventory as identical to the initial inventory. Older uncertain resources and
all receipts/diagnostics are preserved. Container/network names were not inventoried;
this comparison does not detect renames.

Checkpoint audit confirms199 protected concurrent/historical/evidence files,47 source/
test/authority bindings, original empty index and13 new prerequisite bindings unchanged.
Identity equality is not a claim of unchanged internal content or uninterrupted unrelated
workloads. All source/runtime files remain unchanged from the recorded commit.

## Impact decisions

Verification attempt and diagnosis are complete; the actual Kong qualification remains
failed. No runtime correction is included in this verification-only delivery.

Scaffold: verification of existing deployment tooling only; actual consuming generator
proof stays open. Shared UI: no surface change. Agent context: no new policy or root
instruction change. Documentation: this evidence, runbook and KDG handoff/memlog record
the failed gate and precise next correction. ADR: existing isolation, release/custody
and safe diagnostic decisions apply; no accepted ADR amended or new ADR needed.
TS7.0.2, selected image/CLI pins and mail15484 remain unchanged. No production,
account/access, infrastructure provisioning, deployment, real-data or full-suite claim.

## Review closeout

One-shot blind review completed with five findings, all patched: inventory claims are
limited to container/network IDs and volume names; cleanup chronology is current;
memlog distinguishes refusal preservation from later approved removal; inspection
replay limitations are explicit; operational helper invocations/outcomes and their
measurement limitations are recorded. No new review deferral. Existing timing
investigations remain unresolved in the preceding implementation record.

## Evidence digests

The local evidence-bindings.json binds all 33 underlying evidence/helper files.

| Artifact | SHA256 |
| --- | --- |
| evidence-bindings.json | 2ddcb82e999079114aef21ce78384d73a74ffa15b22b6cb1ca920e736eb0aec1 |
| checkpoint.json | 7e211cc8700efe2dd69820be0bae7e0ae34c639b6c1f038a5288625e7508136e |
| commands.json | 2b8ca4806d9b3a37263cf93991f9c8f7ee3cf0f83ac77bd3fbe5fabd90f4af4f |
| operational-commands.json | 337cad875be1519c12a6777a414a331bf937b8d102e7b4eac1803a1947dd3bc6 |
| inspection-diagnostic.json | 1bcc734760b828307da482c3ed1001e93431fccbcffd73d3da6eed0002079fd8 |
| retained-resources.json | 4869de557fcee4ef493df6f8a97f7d9ca06eac6bf77c256c03ea4d3cbef8fb79 |
| retained-resource-references.json | 0b9ee22a65d70abcecaf98b2d3563dfc682d3f51e0851e7f522c36b3d4562405 |
| cleanup-approval.json | bc62ff8875e0b830dc9e177a598a6ab2e1fa8873122a6f31a5ab5bff8b901e99 |
| cleanup-journal.json | cd5953d7838d60e3159c5f38e1460e09062cebd3fb40e9777895c529f866e1ab |
| cleanup-result.json | 0d55a66a73d3034afe64a92fe24dc473c289d76d19836931bc8183b6c3135071 |
| new-receipt-bindings.json | 7999ddd0519b9798848a375b69fa28ad435811930071cd297d4fa31f37a75b0b |
| verification-summary.json | b9c673a3bbfeecbb52710432cb8b254590773481875af866f8ba9eba982ab765 |
