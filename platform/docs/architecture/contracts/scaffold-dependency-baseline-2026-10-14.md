# Exact direct dependency baseline — 2026-10-14

Newest stable releases selected at planning time. This is a metadata-backed selection,
not a lockfile, clean-install or runtime compatibility result. Do not use floating
`latest` in delivery manifests. Refresh deliberately when implementation starts and
record any changed pin with affected acceptance evidence. Existing PtS/Scribeswell
manifests and locks are not edited by this planning baseline.

Sources: npm registry package latest tags and PyPI release metadata read directly
2026-10-14; all 35 initial queries and required peer/native-wheel supplements succeeded. Runtime releases independently checked against
[Node downloads](https://nodejs.org/en/download) and
[Python downloads](https://www.python.org/downloads/).

| Runtime/tool | Exact selected version | Qualification |
| --- | --- | --- |
| Node.js | 26.11.1 | Newest stable Current release; not labelled LTS |
| Python | 3.15.0 | Newest stable release; ordinary GIL-enabled CPython |

## Direct package pins

| Ecosystem | Package | Exact version | Primary source |
| --- | --- | --- | --- |
| npm | typescript | 7.0.2 | [metadata](https://registry.npmjs.org/typescript) |
| npm | react | 19.3.0 | [metadata](https://registry.npmjs.org/react) |
| npm | react-dom | 19.3.0 | [metadata](https://registry.npmjs.org/react-dom) |
| npm | vite | 8.3.4 | [metadata](https://registry.npmjs.org/vite) |
| npm | @vitejs/plugin-react | 6.1.2 | [metadata](https://registry.npmjs.org/@vitejs%2fplugin-react) |
| npm | @types/react | 19.3.0 | [metadata](https://registry.npmjs.org/@types%2freact) |
| npm | @types/react-dom | 19.3.0 | [metadata](https://registry.npmjs.org/@types%2freact-dom) |
| npm | @types/node | 26.6.5 | [metadata](https://registry.npmjs.org/@types%2fnode) |
| npm | @playwright/test | 1.64.0 | [metadata](https://registry.npmjs.org/@playwright%2ftest) |
| npm | @supabase/supabase-js | 2.117.3 | [metadata](https://registry.npmjs.org/@supabase%2fsupabase-js) |
| npm | tailwindcss | 4.3.3 | [metadata](https://registry.npmjs.org/tailwindcss) |
| npm | @tailwindcss/vite | 4.3.3 | [metadata](https://registry.npmjs.org/@tailwindcss%2fvite) |
| npm | lucide-react | 1.57.0 | [metadata](https://registry.npmjs.org/lucide-react) |
| npm | zod | 4.6.7 | [metadata](https://registry.npmjs.org/zod) |
| npm | react-router-dom | 7.18.4 | [metadata](https://registry.npmjs.org/react-router-dom) |
| npm | supabase | 2.120.0 | [metadata](https://registry.npmjs.org/supabase) |
| npm | tsx | 4.23.15 | [metadata](https://registry.npmjs.org/tsx) |
| npm | npm | 12.2.0 | [metadata](https://registry.npmjs.org/npm) |
| npm | shadcn | 4.21.4 | [metadata](https://registry.npmjs.org/shadcn) |
| npm | vitest | 5.0.4 | [metadata](https://registry.npmjs.org/vitest) |
| npm | @testing-library/react | 16.3.3 | [metadata](https://registry.npmjs.org/@testing-library%2freact) |
| npm | @testing-library/dom | 10.4.2 | [metadata](https://registry.npmjs.org/@testing-library%2fdom/latest) |
| npm | @testing-library/user-event | 14.6.8 | [metadata](https://registry.npmjs.org/@testing-library%2fuser-event) |
| npm | jsdom | 30.1.2 | [metadata](https://registry.npmjs.org/jsdom) |
| Python | fastapi | 0.143.0 | [metadata](https://pypi.org/pypi/fastapi/json) |
| Python | uvicorn | 0.54.0 | [metadata](https://pypi.org/pypi/uvicorn/json) |
| Python | pydantic | 2.14.1 | [metadata](https://pypi.org/pypi/pydantic/json) |
| Python | pydantic-settings | 2.15.0 | [metadata](https://pypi.org/pypi/pydantic-settings/json) |
| Python | SQLAlchemy | 2.1.4 | [metadata](https://pypi.org/pypi/SQLAlchemy/json) |
| Python | psycopg | 3.3.6 | [metadata](https://pypi.org/pypi/psycopg/json) |
| Python | alembic | 1.20.0 | [metadata](https://pypi.org/pypi/alembic/json) |
| Python | httpx | 0.28.1 | [metadata](https://pypi.org/pypi/httpx/json) |
| Python | pytest | 9.1.1 | [metadata](https://pypi.org/pypi/pytest/json) |
| Python | rfc8785 | 0.1.4 | [metadata](https://pypi.org/pypi/rfc8785/json) |
| Python | uv | 0.13.1 | [metadata](https://pypi.org/pypi/uv/json) |
| Python | PyJWT | 2.15.1 | [metadata](https://pypi.org/pypi/PyJWT/json) |

Dependency selection is scoped: shadcn is a build-time source tool, Supabase CLI/npm/
tsx/uv are development/build tools, pytest and browser/component tools are dev-only.
KDG and affected Access declare their own required Python subset; no app requirements
file becomes service authority. Boto3/Content/People/worker packages are absent for KDG.

TypeScript 7.0.2 supplies `tsc`; Microsoft documents that 7.0 has no legacy compiler API.
Choose CLI-driven type checks and client generation. If a selected lint/codegen tool
actually requires that API, pin Microsoft’s `@typescript/typescript6` compatibility
package under the documented alias arrangement in that tool’s owner and prove it;
do not change KDG’s `tsc` to 5.9/6 silently. No compatibility package is added speculatively.
[Microsoft TS7 announcement](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/).

Static fit: Vite8.3.4 pairs with plugin-react6.1.2; React/DOM/types19.3.0 pair; Tailwind/
Vite plugin4.3.3 supports Vite8; Vitest5.0.4 supports Vite8; Node26.11.1 satisfies the
declared Node engines including npm12.2.0/jsdom30.1.2. These claims use publisher
metadata; installation/build/actual-device behavior still needs delivery acceptance.

Only required peers are selected. No React Compiler/Babel/canvas/coverage extension is
enabled implicitly. Testing Library DOM10.4.2 satisfies required peers; plugin-react6.1.2 declares its
OXC/Babel/React Compiler peers optional, so they are omitted. Binary Python dependencies must
supply supported CPython3.15 target wheels or an explicitly verified source-build plan;
requires-python alone is not proof that a native extension runs.

Full transitive resolution/hashes, OS/architecture and image digests are release-build
evidence. Owner locks/root workspace lock capture the resolution during authorized
Build; no hand-written substitute lock or unverifiable image digest is introduced.

Native metadata supplement: Pydantic core2.50.1 and Psycopg binary3.3.6 publish ordinary
CPython3.15 manylinux wheels for x86_64 and aarch64. Psycopg aarch64 requires glibc2.27+
(x86_64 wheel glibc2.17+); selected container base must satisfy this. Wheel availability
is verified metadata, not execution. No free-threaded Python or custom source-build path
is selected. Choose exact supported Linux/container identity and lock wheel hashes in ENV
delivery before runtime activation.
