# @platform/app-directory-client

Typed fetch+Zod client for the `services/app-directory` service.

This is the **one sanctioned shared frontend package** — it is a service client with a clear API contract, not shared runtime logic. Apps call the service over HTTP; this package just provides typed wrappers and Zod validation.

## Usage

```ts
import { createAppDirectoryClient } from "@platform/app-directory-client";
import { supabase } from "@/lib/supabase";

const appDirectoryClient = createAppDirectoryClient({
  baseUrl: import.meta.env.VITE_APP_DIRECTORY_URL,
  getToken: async () => {
    const { data } = await supabase.auth.getSession();
    return data.session?.access_token;
  },
});

// In a React hook:
const { apps, protected_access_status } = await appDirectoryClient.getCurrentApps({signal});
```

## Exports

| Export | Description |
|--------|-------------|
| `createAppDirectoryClient(options)` | Factory — returns a typed client instance |
| `AppEntrySchema` | Zod schema for a single app |
| `MeContextSchema` | Zod schema for identity context |
| `MeAppsResponseSchema` | Zod schema for /me/apps response |
| `AppEntry`, `MeContext`, `MeAppsResponse` | Inferred TypeScript types |

## Contract alignment

Zod schemas here mirror the Pydantic schemas in `services/app-directory/schemas/app_schemas.py`. Keep them in sync.

## Current observations

`getCurrentApps({token,signal})` calls v2 with an explicitly captured host-session token,
no-store and no redirects. A total8s deadline includes token acquisition, transport and
body handling; caller cancellation also rejects transports ignoring abort.
`AppDirectoryError.errorId` is `authentication_required`, `access_denied`,
`discovery_unavailable` or `request_cancelled`. Error text/details from the server are
never copied into client exceptions. Anonymous/unavailable observations cannot carry
links; duplicate/unpublished or unsafe-URL entries are invalid.

Existing DTOs, `getMyApps`, `getMyContext` and exports remain supported. `getAllApps`
remains a source-compatible method but its public HTTP endpoint has been removed; do
not use it as anonymous fallback. React hosts use `useCurrentApps` from ui-business.
Run `npm test --workspace @platform/app-directory-client` and its `type-check` script
with selected Node26.11.1. Named-case detail can be obtained by directly running
`node --import tsx platform/app-directory-client/tests/current-apps.test.ts`.
