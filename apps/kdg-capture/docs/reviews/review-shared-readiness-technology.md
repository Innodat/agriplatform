# Shared readiness technology and repository reality review

2026-10-14. Technology/reality lens for the architecture reviewer gate. Scope:
ARCHITECTURE-SPINE.md, the shared KDG readiness addendum, shared-prerequisites.md,
KDG command validation and the KDG initial fingerprint disposition. Read-only
inspection and primary-source verification; no install, implementation or live writes.
The user's acknowledgement covers all owners; this review does not reopen ownership.

**Verdict: PASS for the selected planning baseline, with the recorded pre-Build
inputs still open.** No technology contradiction requires changing the selected
JCS/HMAC/operator/scaffold design. This is neither executable readiness PASS nor
evidence that shared capabilities already exist.

## Verified claims

- JCS is RFC 8785, with UTF-8 output, recursive UTF-16 code-unit key ordering,
  preserved Unicode and array ordering. Duplicate keys, lone surrogates and
  non-finite numbers must fail. KDG contracts explicitly reject these inputs;
  decimal-string revisions avoid JavaScript integer loss and initial ratings are
  bounded integers. The non-BMP conformance fixture is necessary: Python's ordinary
  key sorting is insufficient. The selected baseline correctly requires library
  conformance rather than asserting an installed implementation. [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785).
- HMAC-SHA-256 with a random 32-byte key and full digest fits the selected
  database-only candidate-guessing threat boundary. The contract states the key,
  runtime and oracle limitations, independent backup/restore, overlap/rollback and
  missing-key refusal. No home-grown primitive is needed; Python exposes HMAC and
  constant-time digest comparison. These sources verify the construction, not a
  chosen Python/library version. [RFC 2104](https://www.rfc-editor.org/rfc/rfc2104),
  [Python hmac documentation](https://docs.python.org/3/library/hmac.html).
- PostgreSQL session_user normally identifies the initiating login; SET ROLE and
  SECURITY DEFINER change current_user instead. Superusers can change session
  authorization, so the claimed binding depends on the documented restricted
  operator role, not merely reading the field. The selected protected per-owner
  login mapping fits that model. No PostgreSQL 18 pin is selected by consulting
  current documentation. [PostgreSQL identity functions](https://www.postgresql.org/docs/current/functions-info.html).
- The proposed npm workspace invocation is valid once its package and script
  exist; missing scripts must fail rather than use --if-present. uv owner projects
  support adjacent pyproject.toml/uv.lock and reproducible exact resolutions. This
  supports the dependency ownership direction, not proof that the owner manifests
  or locked verification commands currently exist. [npm workspaces](https://docs.npmjs.com/cli/v11/using-npm/workspaces/),
  [uv project structure](https://docs.astral.sh/uv/concepts/projects/layout/).

## Repository evidence and remaining gates

1. **Existing pins remain reuse evidence.** Reading apps/pts/web/package-lock.json
   confirms React 19.3.0, Vite 7.3.6, TypeScript 5.9.3, Supabase JS 2.117.1 and
   Playwright 1.63.0. Their recorded Node engines intersect at >=22.12.0; the spine
   accurately labels these as existing PtS resolutions, not KDG selected pins or
   an installed compatibility proof. ENV still needs an exact selected package,
   Node/npm/Python/uv/container matrix with unchanged-lock installation evidence.
2. **Generator commands are future targets.** Root package.json declares platform/*
   workspaces, but platform/builder-cli has no package.json; its README calls it a
   placeholder. The addendum correctly marks schema/recipe paths and generate /
   test:generation commands as planned. No generator command was executed against
   this absent package. P1/SERVICE must deliver and verify those targets, generated
   output installation roots, regeneration safeguards and required suites.
3. **Independent Python ownership is not implemented.** services/access and apps/pts
   currently lack pyproject.toml/uv.lock. Access's Dockerfile installs
   apps/pts/requirements.txt, exactly the coupling the prerequisite packet assigns
   to its affected owner item. Exact owner-specific locked commands/dev groups,
   package roots and image input changes remain delivery inputs.
4. **Operator and key safety need real-role evidence.** ID-B must prove dedicated
   non-superuser login authentication, denied session-authorization impersonation,
   role/mapping changes and cross-owner access, including actual connection/pool
   configuration. WRITE/ENV must supply concrete secret paths/principals, JCS
   library pin/vectors, key isolation and coordinated data/key restore proof.
   These named gates are already present; documentation cannot establish them.

No finding calls for KDG requirements gathering, implementation now, changing Leave
fingerprinting, installing a new cryptography service or revising accepted ADRs.
