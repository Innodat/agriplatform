# ENV/scaffold newest-stable technology review

2026-10-14. Required architecture technology gate, following the owner's explicit
newest-stable preference. This supersedes using PtS lock resolutions as a ceiling
for KDG selection. Existing application locks remain evidence about those applications.
No packages installed, lockfiles generated or application code implemented.

**Verdict: selected direct-version baseline is supported by primary registry
metadata; installation and runtime stability remain delivery acceptance.** Newest
stable means ordinary releases, excluding beta/rc/canary/nightly; Node Current is
distinguished from LTS. This report does not assert reproducible resolution or
native-wheel/container availability merely from a release number.

## Exact release snapshot

Primary npm/PyPI metadata was fetched successfully in this session and inspected
from /tmp/kdg-latest-metadata.json (35 successful responses, with source URLs,
engines/peers or Python requirements, and artifact integrity). Links below identify
the registry authority. These are verified newest stable direct versions at the
session snapshot, rather than older source ranges or third-party recommendations.
Supplemental metadata in /tmp/kdg-extra-metadata.json verifies required Testing
Library DOM, plugin optional peers and CPython 3.15 native wheel availability.

| npm package | Stable version | Primary source |
| --- | --- | --- |
| react | 19.3.0 | [registry](https://registry.npmjs.org/react) |
| react-dom | 19.3.0 | [registry](https://registry.npmjs.org/react-dom) |
| vite | 8.3.4 | [registry](https://registry.npmjs.org/vite) |
| @vitejs/plugin-react | 6.1.2 | [registry](https://registry.npmjs.org/@vitejs%2fplugin-react) |
| typescript | 7.0.2 | [registry](https://registry.npmjs.org/typescript) |
| @types/react | 19.3.0 | [registry](https://registry.npmjs.org/@types%2freact) |
| @types/react-dom | 19.3.0 | [registry](https://registry.npmjs.org/@types%2freact-dom) |
| @types/node | 26.6.5 | [registry](https://registry.npmjs.org/@types%2fnode) |
| @playwright/test | 1.64.0 | [registry](https://registry.npmjs.org/@playwright%2ftest) |
| @supabase/supabase-js | 2.117.3 | [registry](https://registry.npmjs.org/@supabase%2fsupabase-js) |
| supabase CLI | 2.120.0 | [registry](https://registry.npmjs.org/supabase) |
| tailwindcss | 4.3.3 | [registry](https://registry.npmjs.org/tailwindcss) |
| @tailwindcss/vite | 4.3.3 | [registry](https://registry.npmjs.org/@tailwindcss%2fvite) |
| lucide-react | 1.57.0 | [registry](https://registry.npmjs.org/lucide-react) |
| zod | 4.6.7 | [registry](https://registry.npmjs.org/zod) |
| react-router-dom | 7.18.4 | [registry](https://registry.npmjs.org/react-router-dom) |
| tsx | 4.23.15 | [registry](https://registry.npmjs.org/tsx) |
| npm | 12.2.0 | [registry](https://registry.npmjs.org/npm) |
| shadcn CLI | 4.21.4 | [registry](https://registry.npmjs.org/shadcn) |
| vitest | 5.0.4 | [registry](https://registry.npmjs.org/vitest) |
| @testing-library/react | 16.3.3 | [registry](https://registry.npmjs.org/@testing-library%2freact) |
| @testing-library/dom | 10.4.2 | [registry](https://registry.npmjs.org/@testing-library%2fdom) |
| @testing-library/user-event | 14.6.8 | [registry](https://registry.npmjs.org/@testing-library%2fuser-event) |
| jsdom | 30.1.2 | [registry](https://registry.npmjs.org/jsdom) |

| Python package/tool | Stable version | Primary source |
| --- | --- | --- |
| fastapi | 0.143.0 | [PyPI](https://pypi.org/project/fastapi/) |
| uvicorn | 0.54.0 | [PyPI](https://pypi.org/project/uvicorn/) |
| pydantic | 2.14.1 | [PyPI](https://pypi.org/project/pydantic/) |
| pydantic-settings | 2.15.0 | [PyPI](https://pypi.org/project/pydantic-settings/) |
| SQLAlchemy | 2.1.4 | [PyPI](https://pypi.org/project/SQLAlchemy/) |
| psycopg | 3.3.6 | [PyPI](https://pypi.org/project/psycopg/) |
| alembic | 1.20.0 | [PyPI](https://pypi.org/project/alembic/) |
| httpx | 0.28.1 | [PyPI](https://pypi.org/project/httpx/) |
| pytest | 9.1.1 | [PyPI](https://pypi.org/project/pytest/) |
| rfc8785 | 0.1.4 | [PyPI](https://pypi.org/project/rfc8785/) |
| uv | 0.13.1 | [PyPI](https://pypi.org/project/uv/) |
| PyJWT | 2.15.1 | [PyPI](https://pypi.org/project/PyJWT/) |

Latest stable runtime choices are **Node 26.11.1 Current** (latest LTS is
24.21.0) and **Python 3.15.0**, stable since 2026-10-09. Thus Python 3.14 is
not newest stable. These selections implement the owner's preference; they do not
claim LTS status for Node 26 today. [Node downloads](https://nodejs.org/en/download),
[Python 3.15.0 release](https://www.python.org/downloads/release/python-3150/).

## Fit and remaining evidence

- Node 26.11.1 satisfies npm 12.2.0/jsdom 30.1.2 engines
  (^22.22.2 || ^24.15.0 || >=26), Vite/plugin-react engines, Vitest 5 engines and
  the recorded Supabase/Playwright/shadcn floors. React DOM and React typings
  bind the matching 19.3 family. @vitejs/plugin-react 6.1.2 requires Vite ^8;
  @tailwindcss/vite 4.3.3 and Vitest 5.0.4 both explicitly admit Vite 8. The
  recorded router, Lucide and Testing Library React peers admit React 19.
- Python 3.15.0 clears recorded Requires-Python floors (the highest direct floor
  is SQLAlchemy >=3.11). FastAPI's Pydantic >=2.9, settings' Pydantic >=2.7,
  Alembic's SQLAlchemy >=2.0 and HTTPX bounds admit these selections. Lower-bound
  metadata alone does not prove Python 3.15 runtime compatibility. Supplemental
  PyPI metadata confirms ordinary cp315 wheels for pydantic-core 2.50.1 and
  psycopg-binary 3.3.6 on manylinux x86_64 and aarch64. The aarch64 Psycopg wheel
  needs glibc >=2.27, whereas its x86_64 wheel supports >=2.17. ENV must prove the
  selected container/host meets its wheel tags and run the actual suites.
  [Pydantic core](https://pypi.org/pypi/pydantic-core/json),
  [Psycopg binary](https://pypi.org/pypi/psycopg-binary/json).
- Do not copy PtS-era Vite/plugin, TS5, Zod3 or React18 template assumptions into
  this baseline. Generate disposable output, lock the complete resolution and
  prove type-check/build/unit/browser/auth/contract suites. Exact selected pins
  prevent future latest drift; revalidation is explicit if selection changes.
- Testing Library DOM 10.4.2 satisfies React's ^10.0.0 and user-event's >=7.21.4
  requirements. Plugin-react 6.1.2 peerDependenciesMeta explicitly marks
  oxc-transform-react, @rolldown/plugin-babel and babel-plugin-react-compiler
  optional; omit these features from the minimum baseline. jest-dom is not
  selected. [Plugin metadata](https://registry.npmjs.org/@vitejs%2fplugin-react/6.1.2).
- shadcn is a source-generation CLI, not a complete runtime component inventory.
  Pin its invocation and chosen generated components/dependencies during scaffold
  delivery. No component suite compatibility is inferred solely from the CLI pin.
- The API can select bare FastAPI plus explicit Uvicorn/settings dependencies;
  do not add standard/all extras, cloud deployment or observability services from
  documentation examples without a concrete consuming need. PyJWT crypto extras,
  Psycopg binary/pool choice and optional frontend peers remain explicit choices
  with locked dependencies when consumed.

No installation/runtime suite was run. Remaining stability evidence belongs to
ENV/P1/SERVICE/WRITE delivery and first consumers, under the existing planning
contracts; it does not reopen KDG product discovery or authorize implementation.

## Shared baseline reconciliation

Reviewed platform/docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md.
Its 35 direct versions, runtime choices and static-fit claims agree with registry
evidence. Its TS7 compiler-API distinction correctly prevents an old codegen tool
from silently downgrading the app compiler; actual selected generation tools must
prove CLI compatibility. Close its temporary required-DOM/optional-peer paragraph
using the supplemental evidence above and add DOM 10.4.2 to the exact pin table.
This is a small documentation reconciliation, not a technology blocker or demand
to install packages during planning.

## Environment/generation contract technology gate

Reviewed platform/docs/architecture/contracts/scaffold-environment-and-generation.md.
**PASS for planning selection; no additional technology blocker found.** The document
distinguishes selected runtimes from unpulled image identities and planned commands
from installed tools. platform/deployment/dev.py is absent as stated; existing
platform/deployment/release.py and host-release.py provide coordinator reuse evidence,
while their Identity/Access/KDG target adapters still need delivery proof. No planned
command was represented as a passing execution.

The Supabase CLI-owned image set/qualified PostgreSQL major is the right boundary:
newest library preference cannot safely select a replacement database container or
upgrade a live project. Exact image availability/digests, OS/glibc/native wheel fit
and release-target compatibility remain explicit ENV acceptance, not invented pins.

LAN-only .test HTTPS is a feasible selected execution assumption. RFC 6761 reserves
.test for private networks and requires explicit DNS configuration; default resolution
can return negative answers. The contract already requires local routing and trusted
test certificates and claims no public registration/hosting.
[RFC 6761 section 6.2](https://www.rfc-editor.org/rfc/rfc6761#section-6.2).

Entra's documented URI restrictions admit HTTPS callbacks and localhost HTTP during
development; non-localhost ports match exactly. A browser follows the redirect to
the LAN hostname, so no public callback hosting requirement follows from these rules.
This is a feasibility inference, not verified provider registration or device login.
The separate Supabase provider callback and app return are correct; Supabase documents
localhost plus API external_url for local Azure development. ENV must configure the
matching external Auth origin in each disposable desktop/device target and qualify
the actual flow. The contract's deferred DNS/CA/registration and replacement-target
qualification already cover this evidence without provisioning anything now.
[Entra redirect restrictions](https://learn.microsoft.com/en-us/entra/identity-platform/reply-url),
[Supabase Azure local development](https://supabase.com/docs/guides/auth/social-login/auth-azure).

No certificate, DNS, Entra registration, hosted target, container or repository
configuration was changed by this review.
