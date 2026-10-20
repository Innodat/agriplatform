# ENV GoTrue closed service profile evidence

Status: bounded profile complete; independent review and selected verification complete.
Baseline `2e434d7f2bd47de8c197c46ed1b1b0b629c45a3f` plus explicit owned changes;
this is not an unmodified-baseline test claim.

## Scope and source authority

The existing create_profile.py now separates long-running GoTrue service intent from
its unchanged six-variable gotrue migrate job. The selected publisher builder emits58
entries for the explicit approved target input. Six retained TypeScript files are
verbatim at CLI2.120.0 commit753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4;
fixtures/supabase-gotrue-source/sources.json records original URLs/hashes. Publisher
unit/schema sources inform the fixed selected-input.json; their fetched complete
bytes remain ignored evidence with recorded hashes. This is not execution of the
complete native CLI config resolver or all provider/slim/custom branches.

The public environment fixture is builder output for no SMTP/Mailpit/templates/
hooks/providers, disabled signup/email/SMS/anonymous/manual linking and no signing-file
override. Only its internal PostgreSQL host varies with the structurally validated
per-run project. Known image repository/digest syntax, observed Linux/amd64 identity,
target ID/origins/callback arrays, workdir and network shape are checked. These are
profile input checks, not actual image inspection or resource custody. Trusted owner
selection, effective Config and execution identity must still be checked before any
future admission. Existing Auth image/job/lifecycle owners retain that work.

The source profile exposes9999 only, no host publish/mounts, auth alias, wget health
10s/2s/3 and source unless-stopped restart intent. It inherits image Cmd/Entrypoint;
no actual inheritance proof or safe disposable execution profile is claimed. The
ordinary classifier refuses the create request; no scoped admission is added.
No GoTrue request is exchanged, no service started, and no account/migration/functional
Auth or new runtime readiness follows. Existing safety owners remain unchanged.

## Requirements and acceptance

| Requirement | Selector / proof |
| --- | --- |
| Full service environment distinct from migration job | GotrueServiceProfile.test_long_running_environment_is_distinct_from_the_migration_job |
| Complete independent env/argv/API oracle, no publish/mounts, classifier refusal | GotrueServiceProfile.test_complete_source_profile_stays_network_only_and_classifier_refused |
| Every leaf value/type and top-level missing/extra input refuses safely | GotrueServiceProfile.test_all_intent_leaves_missing_extra_and_wrong_types_refuse_safely |
| Wrong context/platform/selection shapes refuse | GotrueServiceProfile.test_invalid_context_and_foreign_image_refuse |
| Ambient and returned-map mutations cannot alter fixed authority | GotrueServiceProfile.test_ambient_values_and_returned_mutation_cannot_change_profile |
| Native pure selected env/container/argv builders agree with delivered env/argv | verify-public-profile.py, complete script below |
| Source files copied/bound into public preparation and existing owner/process regressions | test_dev, test_docker_gate and existing selected Kong process controls |

GotrueServiceProfile uses test_create_profile. Unittest prefix for all recorded calls:
`PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v`.
Each tag retains .txt, -result.json, -sources.json and -semantics.json under
.local/gotrue-profile/. Sources are bound before/after each call; tests run serially.

- `acceptance-red`: `test_create_profile.GotrueServiceProfile.test_long_running_environment_is_distinct_from_the_migration_job`; exit1, 0.094s. Source bindings48, manifest SHA256 `189081f42f3ddda4c34ef77695bd2e2a36007b20f001de929ef0b04817db0878`; log SHA256 `1017e06bee17bea4162b1ee9a4135d13ecdccd25fb546edd58e9fdc144626e19`.
- `focused-green`: `test_create_profile.GotrueServiceProfile`; exit1, 0.567s. Source bindings55, manifest SHA256 `a47a0082a14ff9dea99b0cffaa82810b2cc940de0ad4af1cb3f92bef0ba049eb`; log SHA256 `5b6431f2d1831a499ced9aba9298330450e8fd70fba4b018fed6040f577fd663`.
- `focused-final`: `test_create_profile.GotrueServiceProfile`; exit0, 0.764s. Source bindings55, manifest SHA256 `8e90e4df32cd78240318aa66563c61a8d4d3218289a60baccef9719acb1451e6`; log SHA256 `cc5dfd59e3bd95ed912f1a92817e0b6543aac661a2a60d8474179fca5564a6fb`.
- `affected-green`: `test_create_profile test_dev test_docker_gate`; exit0, 21.907s. Source bindings55, manifest SHA256 `8e90e4df32cd78240318aa66563c61a8d4d3218289a60baccef9719acb1451e6`; log SHA256 `3361647c254bd7f5af963695379f366ffd22e29756777694703eacc8a1cd72f1`.
- `process-green`: `test_resources.ExecutionSupervisor.test_kong_execution_process_ordered_lifecycle_and_post_cleanup_fact test_resources.ExecutionSupervisor.test_kong_boundary_process_source_intent_and_cleanup`; exit0, 55.52s. Source bindings55, manifest SHA256 `8e90e4df32cd78240318aa66563c61a8d4d3218289a60baccef9719acb1451e6`; log SHA256 `3f49590951a60eaf91f102bfbbc6e65466cddcf3d1e9b19a34c9d37617e92840`.

Acceptance RED precedes runtime implementation: existing migration environment fails
the complete-service comparison. The fallback in that test deliberately witnesses
the old six-variable behavior when the new constructor is absent; after delivery it
uses the service constructor and still independently asserts migration stays at six.
The first focused run correctly refuses the fixture's placeholder network ID. Giving
the service fixture the Docker-shaped synthetic64-hex ID used by existing Kong tests
fixes test setup; no validator, expected environment or deadline was weakened.

Initial75 affected and2 process methods all pass on the same55-file frame. Complete
container/argv source conformance then adds the two exact Docker naming/slim helper
snapshots to source bindings, producing the final57-file frame. The prior manifest
is preserved in .local/gotrue-profile/sources-initial.json, and all earlier results
remain tied to their original frames. Later review-frame results are recorded below.

## Independent pinned-source conformance

Initial pure environment derivation PASS1.779s: source-proof.json. The complete
`python3 platform/deployment/.local/gotrue-profile/verify-public-profile.py` passes
3.709s: source-proof-complete.json. It executes pure selected environment, container
spec and argv mapper bodies under the retained Node26.11.1 artifact, checking known
Node/receipt hashes and full payload fingerprint. Runtime is never TypeScript-driven.
The current-source owner still requires fresh prerequisites for future actual startup;
this old tool receipt establishes artifact identity only, not new-source qualification.

Only module imports are relocated to the retained pure dependencies. The selected
slim predicate is extracted verbatim; false/legacy is the only qualified branch.
Linux extra-host and mandatory labels are applied explicitly following retained
container-lifecycle.ts. Native env and full create argv equal delivered constructors;
source service has no publish/mounts/entrypoint/cmd. This does not capture Docker API
wire requests, execute Docker, resolve the whole CLI config or prove Auth startup.
Verified source buffers feed execution and all retained source/manifest/input/Node/
receipt bytes are rechecked. Public fixture/JWK values never enter diagnostic output;
only selected counts, source/artifact identities and booleans are recorded.

Complete verification script (save in a fresh ignored evidence directory and run
from repository root with python3; existing outputs remain untouched). It requires
the retained qualified Node payload noted in the script. No generated repository
file is written by this verification command.

```python
from pathlib import Path
import hashlib,json,re,subprocess,sys,tempfile,time
root=Path.cwd();sys.path[:0]=[str(root/'platform/deployment'),str(root/'platform/deployment/tests')]
import toolchain,create_profile
from create_profile_fixtures import boundary_fixture,target_fixture
p=Path(__file__).resolve().parent;out=p/'source-proof-complete.json';assert not out.exists()
payload=root/'platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload'
receipt_path=payload.parent/'receipt.json';receipt=receipt_path.read_bytes();node=payload/'node/bin/node'
h=lambda raw:hashlib.sha256(raw).hexdigest()
assert h(receipt)=='e67296059f4af98ec18ff600cf137e95b40261be542d3e30133832650823c86a'
assert h(node.read_bytes())=='5a7b8a3cf5ccb57d297519754fd73238f64cf560afd0ef19a2f9bf7384cbb657'
start=time.monotonic();assert toolchain.payload_fingerprint(payload)==json.loads(receipt)['payload']
source=root/'platform/deployment/fixtures/supabase-gotrue-source'
manifest_raw=(source/'sources.json').read_bytes();assert h(manifest_raw)=='42db3a50316b5aa434860f5d9dd87d682f20defd54751b85a0f8bc363283384c'
manifest=json.loads(manifest_raw);raws={f.name:f.read_bytes() for f in source.iterdir() if f.suffix=='.ts'}
for name,raw in raws.items(): assert h(raw)==manifest[name]['sha256']
inputs_raw=(source/'selected-input.json').read_bytes();authority_raw=(source/'public-environment.json').read_bytes()
assert h(authority_raw)=='29a7f4067b053c16525c5e8025eb0cb00b6e1fc42c4403ad51aeb9c8b7e7ef46'
authority=json.loads(authority_raw);inputs=json.loads(inputs_raw)
old=root/'platform/deployment/fixtures/supabase-kong-source';old_raw=(old/'sources.json').read_bytes()
assert h(old_raw)=='054cb89c47d19e55b46eeb5d0c9b4b81d04316ede0facb437c4628ff09b08da1'
old_manifest=json.loads(old_raw);extra={name:(old/name).read_bytes() for name in ('Defaults.ts','docker-create-args.ts')}
for name,raw in extra.items(): assert h(raw)==next(v['sha256'] for k,v in old_manifest.items() if k.rsplit('/',1)[-1]==name)
fixture=boundary_fixture();target=target_fixture();fixture['network']['Id']='b'*64
fixture.update(origins=target['origins'],callback_urls=target['callback_urls'])
reference=next(v for k,v in fixture['selection_plan'].items() if '/supabase/gotrue:' in k)
def strip_imports(text):return re.sub(r'^import\b[\s\S]*?;\s*\n','',text,flags=re.M)
slim=raws['slim-images.ts'].decode()
selected_slim=re.search(r'const SLIM_IMAGE_PREFIX = [^;]+;',slim)[0]+'\n'
for name in ('isSlimImageRef','usesSlimImageRuntime'):
    selected_slim+=re.search(r'export function '+name+r'\([^\n]+\{\n[\s\S]*?^\}',slim,re.M)[0]+'\n'
prefix=('import { formatGoDuration,parseGoDuration } from "./go-duration.ts";\n'
        'import { DEFAULT_SIGNING_KEY } from "./Defaults.ts";\n'
        'import { passwordRequirementsToChar } from "./password-requirements.ts";\n'
        'import { startInternalDbUrl,startInternalDbPassword } from "./internal-db-connection.ts";\n'
        'import { serviceContainerName } from "./docker-ids.ts";\n'
        'import { usesSlimImageRuntime } from "./slim-selected.ts";\n')
wrapper={'slim':False,'image':reference,'projectId':fixture['project'],'networkId':'b'*64,
         'dbUrl':'postgresql://postgres:postgres@127.0.0.1:55482/postgres'}
with tempfile.TemporaryDirectory(prefix='gotrue-public-proof-') as directory:
    work=Path(directory)
    for name,raw in {**raws,**extra}.items():(work/name).write_bytes(raw)
    (work/'builder.ts').write_text(prefix+strip_imports(raws['gotrue.service.ts'].decode()))
    (work/'slim-selected.ts').write_text(selected_slim)
    (work/'args.ts').write_text(strip_imports(extra['docker-create-args.ts'].decode()))
    main=('import {buildGotrueEnv,buildGotrueContainerSpec} from "./builder.ts";\n'
          'import {buildStartContainerCreateArgs} from "./args.ts";\n'
          'const input='+json.dumps(inputs)+';\nconst context='+json.dumps(wrapper)+';\n'
          'const {dbHost,dbPassword,...env}=input;\n'
          'const spec=buildGotrueContainerSpec({...context,env});\n'
          'spec.extraHosts=["host.docker.internal:host-gateway"];\n'
          'spec.labels={"com.supabase.cli.project":context.projectId,"com.docker.compose.project":context.projectId,'
          '"com.supabase.cli.workdir":"/private"};\n'
          'console.log(JSON.stringify({environment:buildGotrueEnv(input),spec,args:buildStartContainerCreateArgs(spec)}));\n')
    (work/'main.ts').write_text(main)
    result=subprocess.run([str(node),str(work/'main.ts')],env={'PATH':'/usr/bin:/bin','NODE_NO_WARNINGS':'1'},capture_output=True,timeout=10)
    assert result.returncode==0,'pinned pure GoTrue profile proof failed'
    value=json.loads(result.stdout)
assert value['environment']==authority['environment'],'publisher environment differs from public fixture'
assert value['environment']==create_profile.gotrue_service_environment(fixture),'runtime environment differs from publisher'
assert value['args']==create_profile.gotrue_service_request(fixture),'runtime argv differs from publisher'
assert value['spec']['binds']==[] and value['spec'].get('ports',[])==[]
assert 'entrypoint' not in value['spec'] and 'cmd' not in value['spec']
assert all((source/name).read_bytes()==raw for name,raw in raws.items())
assert all((old/name).read_bytes()==raw for name,raw in extra.items())
assert (source/'sources.json').read_bytes()==manifest_raw and (old/'sources.json').read_bytes()==old_raw
assert (source/'selected-input.json').read_bytes()==inputs_raw and (source/'public-environment.json').read_bytes()==authority_raw
assert receipt_path.read_bytes()==receipt and h(node.read_bytes())=='5a7b8a3cf5ccb57d297519754fd73238f64cf560afd0ef19a2f9bf7384cbb657'
summary={'ok':True,'scope':'pure selected env/container/argv builders with relocated imports; not full CLI or Docker API capture',
         'sources_sha256':{name:h(raw) for name,raw in {**raws,**extra}.items()},'input_sha256':h(inputs_raw),
         'environment_count':len(value['environment']),'runtime_env_and_argv_match':True,
         'network_only_and_no_mounts':True,'payload_fingerprint_verified':True,'elapsed_seconds':round(time.monotonic()-start,3)}
with out.open('x') as stream:stream.write(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))
```

## Five impact decisions and gates

Scaffold: existing ENV profile/fixture/source-custody owners updated; no separate
builder, recipe/client/schema ownership transfer or consuming scaffold claim. Shared
UI: none. Agent context: existing safeguards suffice; no root policy change.
Documentation: this record, source derivation README, DEVELOPMENT and KDG handoff/
memlog carry exact results and remaining gates. ADR: existing isolation/logging/release
requirements apply; no new decision or accepted ADR change. TypeScript7.0.2, selected
CLI/images/ports/mail15484 remain unchanged.

No host Docker access, service start, migration, account/access change, deployment,
infrastructure provisioning or real data. Runtime/fresh setup remain false; owned
GoTrue boundary/custody/effective-image and safe disposal, vendor migration behavior,
functional Auth/routing, remaining ENV services and consuming scaffold proof remain
open before Identity/Access/WRITE/server KDG. No Leave/editor work. Prior receipts,
uncertain resources, locks, failures/investigations and concurrent work stay preserved.


## Final-frame timeout retained

The combined final-regression call runs77 methods on57 unchanged bindings, exits1
in71.870s.76 pass; existing ordered Kong process control returns docker/docker_timeout,
owner_failure scope=fresh/check=already_expired/elapsed_ms43. Manifest SHA256
`45d1f4b3a764b1496f91de9ae8ec0be949f10ac674c80f466a9ff03e186fbd09`;
log SHA256 `4ffc0e149372dfe3ebc49df299647e0da5c938a395e552af3ca573f3aca64d97`.
This does not mean the whole budget was43ms. The failed observation began after its
active deadline, and43ms measures that final observation only. The JSON does not
identify which5/120/15/10-second phase exhausted its budget.

A separate unchanged-case in-memory diagnostic (`python3
platform/deployment/.local/gotrue-profile/diagnose-process.py`) passes23.895s while
preserving real checks, clocks, bounds and results. It records4,091 source snapshots
(9.364s aggregate) and2,065 evidence-file snapshots(5.666s); these wrappers may nest
and add overhead, so durations must not be summed as exclusive phase time. No fresh
observation enters expired in that run. Only safe counts/timings/selected frame names
are recorded; no payload/config/key values. Log SHA256
`74af9d3241e955b6d6cc24005e89b5ed8a5e9db6e49c5f8534aab0de801484e6`.
The exact original exhausted phase, source-inventory cost attribution and other load
remain unverified. A diagnostic or ordinary repeat pass cannot explain that failure.
No expected result, deadline, custody check or source read is changed to dismiss it.
Earlier timing investigations and this original failure remain open/preserved.


## Review follow-up and repeatable conformance

The checked-in `tests/test_gotrue_source.py` supersedes the UUID-specific script above
as the repeatable selected publisher comparison. The historical script/log remains
unchanged as evidence of that earlier frame. Required command (explicit current
artifact selection, no default skip counted):

```sh
KDG_PROFILE_TOOLCHAIN_RUN_ID=ad277eef-a10e-4aac-bb82-5743653fb2e0 PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_gotrue_source
```

The source README documents fresh prepare/toolchain qualify using the existing
owners and a new UUID, manifest-verified retrieval of derivation source, every
selected input override and upstream notice provenance. The test independently pins
selected-input.json, verifies container-lifecycle.ts against the existing source
manifest, and clearly treats Linux extra-host/labels as manually supplied context.
This is builder conformance, not executed Effect lifecycle or native API capture.
An explicit retained artifact verifies exact known Node bytes and full payload
fingerprint only; it does not update receipts or establish fresh runtime prerequisites.
Without explicit configuration the test skips; that is never passing conformance.

Additional requirement traceability:

| Requirement / review improvement | Test selector in test_create_profile.GotrueServiceProfile unless stated |
| --- | --- |
| One detached authority/pin frame per validation | test_validation_reads_one_authority_and_pin_frame |
| Every nested missing node and extra container element, including empty containers | test_nested_missing_extra_and_empty_containers_refuse |
| Foreign repository, malformed digest, missing tag/observation | test_foreign_repository_digest_and_missing_selection_refuse |
| Valid per-run project/workdir/network changes with fixed external URLs | test_second_valid_context_changes_only_run_operands |
| Changed authority bytes refuse all constructors/validator without disclosure | test_changed_authority_bytes_refuse_without_input_disclosure |
| Checked-in independent publisher environment/spec/argv execution | test_gotrue_source.GotruePublisherConformance.test_selected_publisher_environment_container_and_argv |

The single-frame read-count characterization fails before the refactor, then all ten
focused profile methods pass. All27 pre-existing create_profile functions retain
AST-identical behavior; only this item's service-profile functions are added/changed.
No classifier admission, transport, source-inventory check or deadline is relaxed.

A restricted-sandbox affected-suite attempt (`review-final`) runs81 methods, exits1:
15 failures and2 errors after socket creation is denied (PermissionError/port_unavailable).
Its log and bindings are retained. It is repeated with authorized private local sockets,
without changing source or expectations. That environmental failure is distinct from
the earlier unchanged Kong timeout; neither is erased by later passes.

Review-stage exact results (same unittest prefix as above; explicit artifact variable
set for conformance/affected calls):

- `review-frame-red`: `test_create_profile.GotrueServiceProfile.test_validation_reads_one_authority_and_pin_frame`; exit1, 0.148s; 57 bindings; manifest SHA256 `aab2d16ed8e89e917d025b2ac7a1bc35c2b62d1a76c8f27696525b428ee5e6f8`; log SHA256 `c22f50492adcf43bf49d25e6b16bd5b1d6dcaf93dabd097a4fd5ed3245b2ef77`. Sources unchanged: True.
- `review-focused`: `test_create_profile.GotrueServiceProfile`; exit0, 0.456s; 57 bindings; manifest SHA256 `6ecfcd75150e7224aede551beb9189c282d75cc43f74795caf3148196c3a4f01`; log SHA256 `8aafe402d96e9025febf9c148ec68be0c92f6635b3307875f33f42cf433174b9`. Sources unchanged: True.
- `review-conformance`: `test_gotrue_source`; exit0, 1.897s; 58 bindings; manifest SHA256 `70cb76c7533f10404d24d5f046814bf97a14c645bb087720bf461ba171570d05`; log SHA256 `4afeb75201c9755533ad3db53391f851f75756e24a0c0373bbe5f62e91ee806b`. Sources unchanged: True.
- `review-final`: `test_create_profile test_dev test_docker_gate test_gotrue_source`; exit1, 26.888s; 58 bindings; manifest SHA256 `8de002044cdda9f62dc632c1fdfb02a5563a1a944086e62b08060aeb6a4bf360`; log SHA256 `3ec7d3ac57d2030e25a6483314c146982830de871f6947f785aff8651ecabb43`. Sources unchanged: True.
- `review-affected-authorized`: `test_create_profile test_dev test_docker_gate test_gotrue_source`; exit0, 29.615s; 58 bindings; manifest SHA256 `8de002044cdda9f62dc632c1fdfb02a5563a1a944086e62b08060aeb6a4bf360`; log SHA256 `a5298dd760a9590b696566ff9c222d2f20da165b555012cdeed2415d252549e2`. Sources unchanged: True.

- `review-process`: `test_resources.ExecutionSupervisor.test_kong_execution_process_ordered_lifecycle_and_post_cleanup_fact test_resources.ExecutionSupervisor.test_kong_boundary_process_source_intent_and_cleanup`; exit0, 53.648s; 58 bindings; manifest SHA256 `8de002044cdda9f62dc632c1fdfb02a5563a1a944086e62b08060aeb6a4bf360`; log SHA256 `9de170d4dd4c09f8b37512962f2cf367a268c877174293475884f0b70ed68c40`. Sources unchanged: True.

Final83 distinct selected methods pass across two calls on the same58-file frame:
81 affected (including the explicitly configured publisher comparison) and2 existing
Kong process controls. This is not one combined83-method/full-suite run and does not
explain the earlier failed timeout. Review triages all ten findings as patched; none
newly deferred. The preserved original timeout remains an open diagnostic concern.

Preservation audit:458 protected prior/concurrent files unchanged; original index
unchanged before scoped staging; all58 final source/test bindings unchanged. AST
comparison against the canonical baseline confirms all27 previous create_profile
functions unchanged, with8 service-profile functions added. Runtime delta evidence is
.local/gotrue-profile/runtime-delta-review.json; audit is verification-summary.json.
No host Docker inventory/access or resource-identity equivalence is claimed. Existing
receipts, tool payloads, locks and resources are preserved.
