# platform/ui-business

**Status:** Shared launcher implemented; other patterns remain planned

The native file client is now consumed by PtS after its first real same-site TLS,
provider, native PDF and browser Download proof. `createNativeFileClient` supplies
only credentialed file-session/context transport and strict owner-origin/context
validation. Applications retain auth refresh/logout, current action authority and
localized feedback; native viewers/downloads remain browser-owned. Its focused
tests are `tests/native-files.test.mjs`. PtS's fresh isolated frozen-image proof
also covers genuine-provider renewal, logout/switch/delayed-cookie/expiry and the
native resource matrix; final delivery audit/reviews remain with PtS. This
promotion does not claim hosted readiness.

Reusable domain-level components shared across apps. Built on `platform/ui-core`.

## Purpose
- Provide high-level patterns: `CrudPage`, `ReaderLayout`, `StatsGrid`, `FilterBar`
- Encode the implicit UI DSL as explicit, composable components
- Reduce per-app custom layout code

## Planned contents
```
src/
  components/
    crud-page.tsx         ← generic admin/CRUD page shell
    reader-layout.tsx     ← book/chapter/verse reader shell
    stats-grid.tsx        ← summary card grid
    filter-bar.tsx        ← search + filter row
    app-shell.tsx         ← Topbar + Sidebar layout
  index.ts
```

## Phase
Will be seeded in **Phase 3** by extracting patterns from:
- `apps/receipts-web` → CrudPage, StatsGrid, FilterBar
- `apps/bible-web` → ReaderLayout

## App launcher

`AppLauncher` is implemented as a build-time React component, shared by PtS and
Scribeswell. Import it from `@platform/ui-business`; its namespaced CSS is bundled
with the component and does not require Tailwind. Supply directory-provided `apps`
and optional `currentAppId`, `isLoading`, and `label`. Links open a new tab.

The menu supports Enter/Space, Arrow Up/Down, Home/End, Escape, Tab and outside
pointer dismissal. `AppLauncherItem` is a menuitem link and uses the catalogue's
`book-open`/`library` icon or a generic grid fallback. Consumer apps must not override
its internal layout with broad menu/link selectors. Browser acceptance coverage
lives in the PtS launcher suite and Scribeswell reader suite.

Set `iconOnly` to render only the grid icon in the trigger (Scribeswell). The
default is `false`, retaining the Apps text and chevron (PtS). The accessible
label, hover title, keyboard interaction and touch target are preserved.

## Current session binding

Use `useCurrentApps(client, session, loading)` with a host-owned
`{accountId,accessToken,generation?}` or null session. Keep the client stable. Pass its
`apps`/`status` to `AppLauncher`, and `refresh` as both `onRetry` and `onRefresh`.
An optional `onSignIn` invokes the existing host sign-in surface; omit it if unavailable.
States distinguish checking, anonymous, expired authentication, current account denial,
empty success and unavailable discovery. No old-session links survive a render after
account/token/generation changes; aborted/superseded observations cannot reappear.
Reopening and focus/visibility return recheck current discovery without polling.
Without a host sign-in callback, anonymous/expired status itself receives keyboard focus;
no inactive sign-in button is emitted.

The menu retains44px controls, labelled/icon-only triggers, new-tab destination URLs,
roving focus, Escape, Tab and outside dismissal; empty/loading status remains reachable.
Run `npm test --workspace @platform/ui-business` for real loopback Chromium fixtures and
`npm run type-check --workspace @platform/ui-business`. Client tests and both consumers'
launcher suites provide additional deadline, host session and public-reader coverage.
