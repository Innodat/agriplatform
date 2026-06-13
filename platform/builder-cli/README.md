# platform/builder-cli

**Status:** Placeholder — Phase 3

CLI tool for scaffolding features and enforcing platform patterns.

## Purpose
- Automate boilerplate: one command creates router + service + page + hook
- Enforce consistency: validate-patterns fails CI if patterns are violated
- Reduce AI reliance: generated artifacts carry the structural knowledge

## Planned commands
```bash
create-feature <name>     # scaffold full feature (UI + API + types)
generate-models [table]   # regenerate Zod + Pydantic from Supabase
validate-patterns         # lint: check generated files, prompt sizes, naming
```

## Planned structure
```
platform/builder-cli/
  src/
    commands/
      create-feature.ts
      generate-models.ts
      validate-patterns.ts
    templates/           ← Handlebars/EJS templates for scaffolding
    lib/
      supabase-introspect.ts
      codegen.ts
  bin/
    platform-cli.ts
  package.json
```

## Phase
Built in **Phase 3** after FastAPI + codegen (Phases 1–2) are stable.
