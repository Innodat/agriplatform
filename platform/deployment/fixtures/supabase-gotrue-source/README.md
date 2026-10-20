# Closed GoTrue service profile authority

The six TypeScript files are exact public snapshots from Supabase CLI2.120.0,
commit753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4. sources.json records original paths,
URLs and SHA256. Preserve upstream bytes; changes require a reviewed profile update.
The manifest also identifies publisher unit/schema sources used to derive the
explicit selected input. Those complete fetched sources remain in ignored evidence;
they are not required by runtime or the reproducible pure-builder comparison.

selected-input.json is fixed public resolved input for the approved kdg-local target:
signup/email/SMS/anonymous/manual linking disabled, no SMTP/Mailpit/custom templates,
hooks/providers or signing-file override. Remaining values are the publisher's
documented unit/default-schema values. It is not a configuration schema, user input
or complete CLI configuration-resolution proof. public-environment.json contains
the pure publisher builder's58 resulting entries, including public local JWT/JWK
authority. It is reference data, not a captured live environment or user credential.
Only the internal PostgreSQL host varies with the validated per-run project.

create_profile.py supplies the separate source create argv and API intent. The
publisher builder and argv mapper are independently executed with verified pinned
Node26.11.1, relocated imports and the selected legacy/non-slim branch. Docker naming,
duration, password, internal DB and default-key helpers retain their exact source.
Linux extra-host and standard lifecycle labels are applied explicitly, following
the already retained container-lifecycle.ts source. No Docker command is dispatched.
See [evidence](../../ENV_GOTRUE_PROFILE_EVIDENCE.md) for complete reproduction and hashes.

The intended service exposes9999 only on its Docker network, uses auth alias,
no mounts or host publish, and wget health10s/2s/3 retries. The source restart policy
remains unless-stopped as intent only. Cmd/Entrypoint inherit image defaults; actual
effective image/container settings and disposal require a separately bounded owned
execution profile. This does not authorize creation or startup. The ordinary Docker
classifier still refuses the GoTrue service request, even on a persistent session.
The existing six-variable gotrue migrate job is unchanged and remains separate.

No actual GoTrue startup, vendor/app migration behavior, functional authentication,
account setup, provider callback or full environment/scaffold readiness is claimed.
Existing runtime/custody/release/logging/production gates stay binding.

## Repeatable comparison and tool prerequisite

The checked-in `tests/test_gotrue_source.py` runs the selected publisher builders and
compares their environment and argv to both the public authority and Python profile.
It pins selected-input.json separately, verifies source manifests/helpers (including
container-lifecycle.ts), checks the selected Node binary SHA256 and delegates full
payload fingerprinting to the existing toolchain owner. It neither qualifies runtime
nor treats a historical tool receipt as current-source preparation.

From a fresh checkout on the supported Linux x86_64 GNU host, choose a fresh UUID:

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id <fresh-UUID>
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id <fresh-UUID>
KDG_PROFILE_TOOLCHAIN_RUN_ID=<fresh-UUID> PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_gotrue_source
```

Preparation/qualification use the existing target, artifact pins and delivery tooling;
see DEVELOPMENT.md for host/port requirements and incomplete-run preservation. This
test makes no network or Docker call and never installs tools itself. An existing
retained owner artifact may also be selected explicitly: only the known Node bytes
and unchanged receipt/payload identity support the pure comparison. Source-bound
runtime prerequisites still need a fresh run. Without the explicit variable unittest
reports a skip; that skip is not conformance evidence. CI must set it for this check.

The independently executed builder gets **manually supplied Linux context** for
extraHosts and the three lifecycle labels. The comparison verifies the pinned
container-lifecycle.ts bytes, but does not execute its Effect lifecycle or independently
resolve those context values. The API envelope remains covered by the independent
Python oracle; it is not a captured native Docker API exchange.

## Recovering the selected input derivation

Every publisher unit/schema source is retrievable using its immutable `url` in
sources.json. Retrieve the bytes, verify `sha256`, and preserve them outside this
source directory (the runtime uses only the checked-in fixed input/output). For
example, this read-only retrieval writes only new files under a chosen empty folder:

```python
from pathlib import Path
import hashlib, json, urllib.request
manifest = json.loads(Path('platform/deployment/fixtures/supabase-gotrue-source/sources.json').read_text())
destination = Path('/tmp/gotrue-derivation-source')
destination.mkdir(mode=0o700)  # choose a fresh destination; never overwrite evidence
for name, item in manifest.items():
    if 'role' not in item:
        continue
    raw = urllib.request.urlopen(item['url'], timeout=30).read()
    assert hashlib.sha256(raw).hexdigest() == item['sha256']
    with (destination / name).open('xb') as stream:
        stream.write(raw)
```

Start with the verbatim `baseEnvInput` constant in gotrue.service.unit.test.ts. Retain
its email/SMS/MFA/rateLimit/web3/oauthServer/hooks/providers/security/default scalar
values, except the explicit overrides below. The auth index/email/SMS/MFA/rate-limit/
session/web3 schema sources in the manifest provide the corresponding default context;
they are provenance, not a claim that the full config parser was executed.

| Selected fields | Authority |
| --- | --- |
| dbHost, dbPassword, kongContainerName | Public fixture project naming and literal postgres; no observed runtime values |
| apiUrl | Approved target origins[1] |
| authExternalUrl, siteUrl, additionalRedirectUrls | Existing dev.configuration auth external_url/site_url/additional_redirect_urls |
| enableSignup, enableAnonymousSignIns, enableRefreshTokenRotation, enableManualLinking | Existing dev.configuration corresponding auth enable_* fields |
| email.enable_signup | Explicit false for this no-signup profile |
| jwtSecret | Existing public synthetic create-profile JWT_SECRET |
| All remaining input fields | Exact publisher unit baseEnvInput constant |

selected-input.json SHA256 is
`0192b3c338ca65aaec3de13770583338855d2199c02be8b1eb4fd88e7eafea4c`.
Passing that complete fixed input to buildGotrueEnv produces public-environment.json;
the checked-in conformance test proves that comparison without fetching anything.

## Upstream notice

Snapshots are attributed to Supabase, Inc. and contributors at the pinned commit.
`apps/cli/package.json` declares MIT. The pinned repository has no root LICENSE;
LICENSE here retains the verbatim MIT notice from `apps/cli-go/LICENSE`, identical
to `packages/config/LICENSE` (SHA256
`81f7d60afa4316010b1c0df8eb8f0c80b27586a86b72f1bde85e129bfd10d52a`).
Original notice URL:
https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli-go/LICENSE
