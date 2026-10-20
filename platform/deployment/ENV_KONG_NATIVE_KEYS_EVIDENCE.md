# ENV fixed public native key evidence

Status: bounded public-fixture increment complete; six review findings addressed. Baseline `109649872a29856cd2b35fffac3f56977b5e7af2` plus
explicit owned worktree changes. This is not an unmodified-baseline test claim.

## Scope and requirement-to-test evidence

The existing Kong fixture now uses four fixed public publisher defaults rather than
recognizable placeholder markers. Runtime changes only KONG_KEYS, with no signing
function, caller credential input, new dependency/generator/service or additional
Docker authority. All14 public TypeScript snapshot bytes and sources.json remain
unchanged. The selected target has no auth key overrides/signing_keys_path; retained
local-config-values.ts selects HS256 in that branch. Defaults.ts provides the public
JWT secret and opaque sb_secret/sb_publishable values. go-jwt.ts fixes issuer
supabase-demo, roles anon/service_role, exp1983812996, algHS256/typJWT and exact compact
claim order. This proves fixed source-fixture bytes, not complete native CLI resolution,
asymmetric/custom-key support, functional Auth, a sign-in or actual gateway routing.

| Requirement | Test selector |
| --- | --- |
| Exact four public default values and both gateway substitutions | test_create_profile.KongSourceIntent.test_public_native_defaults_match_independent_tokens_and_gateway_bytes |
| No signing-file/credential override in selected target; Auth signing-secret agreement; ambient inputs ignored | test_create_profile.KongSourceIntent.test_native_defaults_are_the_selected_no_override_branch |
| Each altered key transfer refuses safely | test_create_profile.KongSourceIntent.test_each_altered_native_key_transfer_is_refused_without_values |
| Complete request/environment/source-renderer/archive oracle and malicious leaves | test_create_profile.KongSourceIntent and existing KongDisposableProfile |
| Existing owner lifecycle, hostile observations and no-replay/custody rules | test_pinned_execution.KongExecutionOwner |
| Actual private Unix process/public qualifier retains lifecycle facts and no key output | selected test_resources.ExecutionSupervisor Kong controls |

Acceptance RED is a safe-message equality failure against the new independent HMAC
oracle before runtime edits; the known old placeholder expectations are deliberately
replaced, not discarded to hide an unexplained failure. The production tuple is
literal public source authority; the test oracle independently constructs/verifies
the exact HMAC bytes using stdlib, and the pinned Node execution separately agrees.

## Independent pinned-source execution

The existing Node26.11.1 payload from ad277eef-a10e-4aac-bb82-5743653fb2e0 is reused
only for offline public-source conformance. The existing toolchain.payload_fingerprint
matches its retained receipt; the initial proof records executable SHA256 and checks
version before execution, then unchanged executable/receipt bytes afterward. The
review-hardened v2 proof below additionally enforces both known hashes before use. No old startup receipt is repaired or
requalified for this changed runtime source. Node SHA256
`5a7b8a3cf5ccb57d297519754fd73238f64cf560afd0ef19a2f9bf7384cbb657`;
tool receipt SHA256 `e67296059f4af98ec18ff600cf137e95b40261be542d3e30133832650823c86a`.
The exact retained go-jwt.ts HS256 block, with its unchanged node:crypto import, is
executed as TypeScript by pinned Node, outside delivery runtime. Its two role results
match the independent Python HMAC oracle. No token output enters command diagnostics;
public-source-vectors.json is fixed decoded public authority, not captured runtime
transfer input. source-proof.json records PASS1.702s, source/fragment/executable
bindings and narrow scope. Fragment SHA256
`38c4517ff8b90bad7394a3274efc4882c18f38caa5b26dd292b563c7e4aa926d`.

## Serial verification history

All unittest commands use prefix
`PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v`.
Each retained tag has .txt, -result.json, -sources.json and -semantics.json files
under .local/kong-native-keys/. Manifests bind48 source/test/fixture files before
and after each call. Original failures are preserved.

- `acceptance-red`: selectors `test_create_profile.KongSourceIntent.test_public_native_defaults_match_independent_tokens_and_gateway_bytes`; exit1, 0.099s. Manifest SHA256 `7d2fdc1d02122cb04977ceb2890c6af64423b4c3f82ccc59da53b2b80ac88c15`; log SHA256 `ff73b6f925224c497b0c7ad1037cd6be2a2617d2d8b0a19b136cf845cd335da8`.
- `focused-green`: selectors `test_create_profile.KongSourceIntent`; exit1, 0.36s. Manifest SHA256 `399c8b60c1e026628ac4b026041c117518e91ddf1c93f575d138b1b638aa7ffc`; log SHA256 `e68712fd66dac3e0bac861cd19f482c7ce9d57252f3cc35673c8203a6e5adb8c`.

The first focused call has6 passing methods and1 fixture error: auth_environment
requires origins, absent from boundary_fixture. The test now supplies the approved
target origins, matching startup's existing fixture construction. This is a test
fixture correction, not a product failure or changed expected result. The acceptance
RED remains valid and separate. No deadline, request bound or exception policy changes.

## Impact decisions and gates

Scaffold: existing ENV fixed fixture and retained owner tests only; no generator,
recipe/schema/client owner transfer or consuming scaffold claim. Shared UI: none.
Agent context: existing safeguards suffice; no root policy change. Documentation:
this evidence, source derivation notes, DEVELOPMENT and KDG handoff/memlog update.
ADR: existing isolation/release/logging decisions apply; no accepted ADR change or
new decision needed. Approved dependency baseline/TS7.0.2, ports and images unchanged.

No host Docker access, actual startup, account/access changes, migrations, deployment,
provisioning or real-data use in this increment. Prior actual Kong qualification is
historical on the placeholder-key source frame. Future actual startup requires fresh
source-bound prerequisites. runtime_ready/fresh_setup_completed, full ENV, consuming
scaffold and dependent Identity/Access/WRITE/server KDG stay gated. Remaining next
work includes GoTrue service setup/profile/custody/functional routing and remaining
ENV services; owner boundaries remain intact. Older failures/investigations/locks and
all concurrent work are preserved; successful conformance does not resolve them.


The first affected55-method call (`focused-final`) exits1 in57.487s: three test
errors because KongDisposableProfile reused source_oracle without the new helper
alias, and one socketpair write raises sandbox PermissionError. Add the companion
oracle alias to the existing fixture-sharing pattern and rerun unchanged lifecycle
behavior with authorized private Unix access. These failures are retained; neither
expected results nor product behavior/deadlines change for them. Manifest SHA256
`6745051e57f9a923e19dcffae650fbe841ac16e7a5885948b69b2b3cbbe1f375`; log SHA256 `fc520b77d0c9d80459c9d2d3f0832715cc7d47bb46a828b81ed2b61a75f9a60c`.


Affected verification: `test_create_profile test_startup_lifecycle` passes55 methods
(exit0,56.021s), no skips,48 unchanged bindings. Manifest SHA256
`57c7dad912adc37dff71f41d7e5b49655f77e1fff7564883190e192ae0d33e2a`; log SHA256 `7c8eca8367117d9d4b918d111932efbd21f968905a00881155069840b57084c1`.
This includes the complete independent source/disposable/image/archive profile,
all native key/override negatives, structural mutations and lifecycle library tests.

## Reproduce the pinned-source comparison

The complete hardened session-only proof-v2 script follows (SHA256
`d3099768b2b0fc8273f93a9297d67f94ceca4e41abc3247a21ff2a640eaf0300`). Save to a new
ignored local evidence directory and invoke from repository root with `python3
<saved-script.py>`. It uses the retained qualified Node payload identified above;
keep that payload/receipt until replacement conformance evidence exists. Existing
output files remain untouched. This executes one exact source fragment and compares
public fixtures; it is neither delivery tooling nor a runtime signer. The historical
tool receipt is used for artifact identity only, never to authorize new-source startup.

```python
from pathlib import Path
import base64, hashlib, hmac, json, re, subprocess, sys, time
root = Path.cwd()
sys.path.insert(0, str(root/'platform/deployment'))
import toolchain
import create_profile
p = Path(__file__).resolve().parent
out = p/'source-proof-v2.json'
assert not out.exists()
payload = root/'platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload'
receipt_path = payload.parent/'receipt.json'
receipt_raw = receipt_path.read_bytes()
assert hashlib.sha256(receipt_raw).hexdigest() == 'e67296059f4af98ec18ff600cf137e95b40261be542d3e30133832650823c86a'
receipt = json.loads(receipt_raw)
node = payload/'node/bin/node'
node_hash = hashlib.sha256(node.read_bytes()).hexdigest()
assert node_hash == '5a7b8a3cf5ccb57d297519754fd73238f64cf560afd0ef19a2f9bf7384cbb657'
started = time.monotonic()
assert toolchain.payload_fingerprint(payload) == receipt['payload']
source = root/'platform/deployment/fixtures/supabase-kong-source'
manifest_raw = (source/'sources.json').read_bytes()
assert hashlib.sha256(manifest_raw).hexdigest() == '054cb89c47d19e55b46eeb5d0c9b4b81d04316ede0facb437c4628ff09b08da1'
manifest = json.loads(manifest_raw)
snapshots, bindings = {}, {}
for name in ('Defaults.ts', 'go-jwt.ts', 'local-config-values.ts'):
    raw = (source/name).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    rows = [v for k,v in manifest.items() if k.rsplit('/',1)[-1] == name]
    assert len(rows) == 1 and rows[0]['sha256'] == digest
    assert receipt['binding']['preparation_sources']['platform/deployment/fixtures/supabase-kong-source/'+name] == digest
    snapshots[name], bindings[name] = raw, digest
def constant(name):
    return json.loads(re.search(r'export const '+name+r' = ("[^"\n]+");', snapshots['Defaults.ts'].decode())[1])
secret = constant('DEFAULT_LOCAL_JWT_SECRET')
def encode(raw): return base64.urlsafe_b64encode(raw).rstrip(b'=')
def token(role):
    data = encode(b'{"alg":"HS256","typ":"JWT"}') + b'.' + encode(json.dumps(
        {'iss':'supabase-demo','role':role,'exp':1983812996},separators=(',',':')).encode())
    return (data+b'.'+encode(hmac.digest(secret.encode(),data,'sha256'))).decode()
expected = (constant('DEFAULT_LOCAL_SECRET_KEY'),token('service_role'),constant('DEFAULT_LOCAL_PUBLISHABLE_KEY'),token('anon'))
runtime_hash = hashlib.sha256(Path(create_profile.__file__).read_bytes()).hexdigest()
assert create_profile.KONG_KEYS == expected, 'delivered tuple differs from independent HMAC/public defaults'
text = snapshots['go-jwt.ts'].decode()
fragment = 'const GO_JWT_ISSUER =' + text.split('const GO_JWT_ISSUER =',1)[1].split('/** Asymmetric-JWT',1)[0]
script = (text.splitlines()[0]+'\n'+fragment+'\nconsole.log(JSON.stringify([generateGoJwt('
          +json.dumps(secret)+', "service_role"),generateGoJwt('+json.dumps(secret)+', "anon")]));\n')
script_path = p/'public-signer-proof-v2.ts'
with script_path.open('x') as stream: stream.write(script)
environment = {'PATH':'/usr/bin:/bin','LC_ALL':'C.UTF-8','NODE_NO_WARNINGS':'1'}
version = subprocess.run([str(node),'--version'],env=environment,capture_output=True,timeout=10,check=True).stdout.decode().strip()
assert version == 'v26.11.1'
proof = subprocess.run([str(node),str(script_path)],env=environment,capture_output=True,timeout=10)
assert proof.returncode == 0, 'public signer execution failed'
assert json.loads(proof.stdout) == [expected[1],expected[3]], 'publisher signer differs from HMAC/runtime tuple'
assert all((source/name).read_bytes() == raw for name,raw in snapshots.items())
assert (source/'sources.json').read_bytes() == manifest_raw
assert hashlib.sha256(node.read_bytes()).hexdigest() == node_hash and receipt_path.read_bytes() == receipt_raw
assert hashlib.sha256(Path(create_profile.__file__).read_bytes()).hexdigest() == runtime_hash
result = {'ok':True,'scope':'exact extracted HS256 function; not whole CLI or Auth qualification',
          'node_version':version,'node_sha256':node_hash,'known_artifact_hashes_checked_before_execution':True,
          'tool_receipt_sha256':hashlib.sha256(receipt_raw).hexdigest(),'payload_fingerprint_verified':True,
          'source_sha256':bindings,'source_bytes_used_from_verified_snapshots':True,'sources_unchanged_after':True,
          'runtime_source_sha256':runtime_hash,'runtime_tuple_matches':True,
          'extracted_script_sha256':hashlib.sha256(script.encode()).hexdigest(),
          'two_roles_match_independent_hmac':True,'elapsed_seconds':round(time.monotonic()-started,3)}
with out.open('x') as stream: stream.write(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
```


Owner verification: `test_pinned_execution.KongExecutionOwner` passes20 methods,
including all expanded default/hostile phase cases (exit0,185.994s), no skips,
48 unchanged bindings. Manifest SHA256 `57c7dad912adc37dff71f41d7e5b49655f77e1fff7564883190e192ae0d33e2a`;
log SHA256 `fda5e7202aab5f7713fe1114647fbdc86eb4648d37c56b13f0ab1931ba92b86d`. This is the same source frame as affected55,
not a cumulative result across different runtime bytes. Source AST comparison against
baseline finds only assignment KONG_KEYS changed; all27 function bodies and the
rest of the module AST are identical. runtime-delta.json records that bounded delta.


Process verification selectors: `test_resources.ExecutionSupervisor.test_kong_execution_process_ordered_lifecycle_and_post_cleanup_fact test_resources.ExecutionSupervisor.test_kong_execution_process_observed_container_projection test_resources.ExecutionSupervisor.test_kong_boundary_process_source_intent_and_cleanup test_resources.ExecutionSupervisor.test_kong_boundary_process_altered_transfer_and_cleanup_failure_no_fact`
pass4 methods/five scenarios (exit0,107.841s), no skips. Manifest SHA256
`57c7dad912adc37dff71f41d7e5b49655f77e1fff7564883190e192ae0d33e2a`; log SHA256 `daabcb563897cb79cd78015690377948147c9f1d331c33cf32a871dc93189f55`.
Canonical and observed-projection lifecycle controls, public boundary success,
altered-transfer refusal and cleanup-failure no-fact cases all pass. Native public
key values are checked absent from both selected stdout/stderr and public qualifier
JSON. All79 selected methods (55 affected,20 owner,4 process) pass on one unchanged
48-file source frame. This is selected verification, not a full deployment-suite run.

Pre-review preservation audit:412 protected source/concurrent/historical/receipt/state
files unchanged; initial48 source delta is exactly create_profile.py and the two test
modules, with the other45 unchanged; index unchanged. No fresh Docker inventory is
claimed because host Docker was not accessed. Audit scope and full paths are retained
in checkpoint.json and verification-summary.json.

| Selected artifact (.local/kong-native-keys/) | SHA256 |
| --- | --- |
| checkpoint.json | 2251fed231e24ae759f5774a1d4ea685295b2c59d5235fdd1efb8c84a07df516 |
| acceptance-red-sources.json | 7d2fdc1d02122cb04977ceb2890c6af64423b4c3f82ccc59da53b2b80ac88c15 |
| affected-green-sources.json | 57c7dad912adc37dff71f41d7e5b49655f77e1fff7564883190e192ae0d33e2a |
| owner-green-sources.json | 57c7dad912adc37dff71f41d7e5b49655f77e1fff7564883190e192ae0d33e2a |
| process-green-sources.json | 57c7dad912adc37dff71f41d7e5b49655f77e1fff7564883190e192ae0d33e2a |
| source-proof.json | 882bb9ff35d5abd36022c370990f6b7206dc390a4b1fb5c59e8e2e233d0dd437 |
| runtime-delta.json | 23b0b0413483290f3fdd55f8cd05e748d75c7199bfda76946f345aa4549952bf |


## Independent review and hardened proof

One-shot blind-hunter review only; other layers skipped. Six findings are patched,
none newly deferred; individual verdicts/evidence are in the Build triage.
The initial proof script/result and public vectors remain unchanged. Its script
SHA256 is `2b1874258f525910056439a88bd24e8b8ad836bcaa4cdef1560ec1a637949a4a`; v2 supersedes its
standalone reproduction guarantees without erasing that original result.

Hardened `python3 platform/deployment/.local/kong-native-keys/source-proof-v2.py`
passes1.660s. It checks the known executable/receipt/manifest hashes before Node use,
verifies the full payload, derives script and independent HMAC expectations from
verified in-memory source snapshots, compares the delivered KONG_KEYS tuple, and
rechecks source/manifest/runtime/executable/receipt bytes after. No whole CLI/Auth
conformance is claimed. The fragment remains identical to the initial proof; runtime
SHA256 `23ce905165a832b8dcaf0d8fba6d5f1a3fc46d360c9e15bae076e16c3a7fa50f`.
Source-proof-v2 result SHA256 `fc2f91b6642fbafc56a41b54d3bcdebca01fbe3b194be20e9de398684baf56dc`.

The reviewer exposed a positive-boundary stderr test-capture gap. A contained injected
public fixture key reproduces it before the capture fix: `review-stderr-red`, exit1,
16.592s, AssertionError not raised. The outer test buffer prevents that injected value
from entering diagnostics. Its source manifest SHA256
`0f45c1d73c653cff3c2963f32f969ff411933d54fc428b8ba30a0cdd880a6212`;
log SHA256 `6c684cae666aadadb7bc236ee2a3e8bd5c1fe0cd863b2c4325d649166f534fc7`.
All Kong process scenarios now capture both streams, including the positive boundary.
The override matrix tests seven variables individually plus the combined case with
an isolated environment. Key mutation coverage now alters every occurrence, one at
a time, including later bearer/query positions, and retains safe error checks.


## Final acceptance — 2026-10-20

Final command (same unittest prefix above):
`test_create_profile.KongSourceIntent test_resources.ExecutionSupervisor.test_kong_boundary_process_source_intent_and_cleanup test_resources.ExecutionSupervisor.test_kong_boundary_process_positive_stderr_is_checked_for_keys`
passes9 methods (exit0,38.528s),48 unchanged source/fixture/test bindings.
Manifest SHA256 `1b7e524d9d813c916d813d68a686f52bee42cfd53e450695199986dc3637f60b`;
log SHA256 `fef76e1f8e9281c5aa0730071bfc44390a8c111cd4730f2a3f4f065297de6b63`.
Pre-review79 selected methods pass on their one recorded frame; final9 pass on the
review frame, bringing the cumulative distinct selected method count to80. Only two
test modules differ between these frames; runtime and the other46 bindings are
identical. This is not a claim that all80 were rerun on final helper bytes or a full
suite result. Review adds no runtime change. All six findings are patched, none newly
deferred. Prior investigations and failed/incomplete evidence remain preserved.

Final preservation audit passes412 protected files,48 current bindings and index;
the initial source delta remains exactly the fixture owner and two test modules.
No host Docker/resources were accessed; no inventory-equivalence claim is made for
concurrent Docker use. Actual new-key startup/native CLI/full Auth and consuming
scaffold proof remain open. Existing owners retain the next GoTrue profile/setup/
custody/routing and ENV work, with fresh startup prerequisites on current source.
