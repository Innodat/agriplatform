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
const { apps, context } = await appDirectoryClient.getMyApps();
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
