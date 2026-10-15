# ENV frontend dependency qualification

This private workspace is an isolated synthetic consumer of the [approved exact
baseline](../docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md).
No runtime owner imports it. It qualifies package compatibility, including an explicit
synthetic Chromium smoke when requested, not an application, generator, shadcn source
generation, device readiness or real Auth service.
The canonical lock is the repository root `package-lock.json`; never add a fixture lock.

Use the [disposable proof runbook](../deployment/qualification/web/README.md).
Never install or invoke these commands using the checkout's existing node_modules.
Inside a proof root installed by that runner, selected npm executes these scripts:

- `type-check`: actual native TypeScript 7 validates source/tests/config and rejects a
  deliberate string-to-number assignment with TS2322 in an independent temp directory.
  `strict` remains enabled. Third-party declaration checking has the precise limitation
  below; it is never presented as fully coherent TypeScript7 upstream declarations.
- `test`: Vitest/jsdom with actual React DOM and user events tests interaction, router
  rendering, typed Zod rejection and Supabase Auth-client construction/session access
  with a fetch function that throws on every request. No external Auth is contacted.
- `build`: native Vite/React/Tailwind compilation and a compiled CSS utility assertion.
- `tools`: every direct installed version is checked against its exact manifest pin;
  compiler/Vite/Vitest/tsx/npm/shadcn/Playwright CLIs execute their version commands.
  Supabase's exact npm package is verified, with the matching previously qualified
  publisher binary selected by `ENV_SUPABASE_BINARY`; its download-on-postinstall npm
  wrapper is deliberately disabled. This does not prove shadcn generation or Playwright
  browser installation. No optional React Compiler or compatibility compiler is selected.

Five impacts: scaffold gains compatibility evidence only; shared UI is unchanged;
existing root agent instructions remain sufficient; documentation gains this runbook and
ENV evidence; accepted ADRs remain unchanged. Runtime, generator/owner foundations,
Docker, provider/device and release gates remain separate.

The exact installed `@supabase/auth-js2.117.3` has an upstream WebAuthn declaration
conflict with TypeScript7's native DOM library: `webauthn.dom.d.ts:501` declares
`PublicKeyCredentialFuture<T> extends PublicKeyCredential`, but its `toJSON(): T`
uses `AuthenticationExtensionsLargeBlobOutputs.blob: ArrayBuffer` while native
`AuthenticationExtensionsLargeBlobOutputsJSON.blob` is a JSON `string`. The compiler
reports TS2430. No runtime source or dependency pin is patched or downgraded.

The normal fixture check uses `skipLibCheck: true`, which skips checking declaration
files, including dependency `.d.ts` files; it continues strict checking of fixture
TypeScript/TSX source and its use of imported types. `check-declarations.mjs` reruns
with `skipLibCheck: false` and requires exactly the recorded upstream TS2430, including
the WebAuthn/ArrayBuffer/string details, retaining raw diagnostics in the disposable
fixture’s `declaration-diagnostics.log`, so new unexplained declaration failures are
not silently accepted. The independent negative compiler test still rejects an actual
invalid assignment with TS2322 (native compiler exit1). WebAuthn/passkey behavior and
full upstream declaration coherence remain unqualified.

Build and test configurations are separate. `vite.config.ts` imports the fixture's
Vite8.3.4 identity and checks its React/Tailwind plugins without casts. Vitest5.0.4 in
the retained root graph resolves its own compatible Vite7.3.6 peer; `vitest.config.ts`
uses that identity with automatic JSX transformation and no Vite8 build plugins.
A CSS-only ambient module avoids importing competing Vite client global types. The
native production build, rather than the jsdom runner, supplies Vite8/plugin proof.

With the proof runner's existing explicit browser path, `scripts/browser-smoke.mjs`
internally serves the built production assets through Vite8's public `preview()` on
loopback port0 and uses installed pinned Playwright Chromium. It verifies the rendered
heading, increment, details navigation/reload and computed Tailwind padding16px; it
bounds browser and preview teardown. The runner invokes it after build without adding
a public npm script or downloading a browser. This proof stays distinct from jsdom and
owner browser regression checks and never exercises real Auth or device/runtime gates.
