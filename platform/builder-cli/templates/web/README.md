# Web App Scaffold Template

Stampable Vite + React + TypeScript + Tailwind + ShadCN-ready web app template.

## Placeholders

| Placeholder | Example |
|-------------|---------|
| `{{APP_NAME}}` | `system-engineering` |
| `{{APP_DISPLAY_NAME}}` | `System Engineering` |
| `{{DEV_PORT}}` | `5175` |
| `{{BACKEND_PORT}}` | `8002` |

## Usage

```bash
# From repo root — copy and replace placeholders
cp -r platform/builder-cli/templates/web apps/<app-name>/web
cd apps/<app-name>/web
# Replace all {{PLACEHOLDER}} tokens
# npm install
# npm run dev
```

## What's included

```
src/
├── vite-env.d.ts           # Vite env types
├── main.tsx                # Entry point
├── App.tsx                 # Router setup
├── index.css               # Tailwind base
├── lib/
│   ├── supabase.ts         # Supabase Auth client
│   └── app-directory.ts    # App Directory service client
├── context/
│   └── AuthContext.tsx     # Auth state provider
├── hooks/
│   └── useMyApps.ts        # Fetches apps from app-directory
├── components/
│   └── layout/
│       ├── AppShell.tsx    # Topbar + main layout
│       ├── Topbar.tsx      # Brand + AppLauncher + auth
│       └── AppLauncher.tsx # Burger menu (vendored from platform/ui-business)
└── schemas/                # App-specific Zod schemas go here
```

## Notes

- `AppLauncher.tsx` is vendored from `platform/ui-business` — per silo rules, no runtime import from `platform/*`.
- `@platform/app-directory-client` is resolved via tsconfig paths + vite alias (no npm install needed in monorepo).
- `tsconfig.json` in this directory excludes all files from type-checking (template files are not compiled in-place).
