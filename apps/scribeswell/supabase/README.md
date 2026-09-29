# Scribeswell schema history

`migrations/20260614000000_scribeswell_create_schema.sql` owns the `scribeswell`
book/chapter/verse/word/morpheme tables, legacy read views, RLS and existing grants
in the shared Supabase project. Applied migration SQL is immutable.

Restricted direct PostgreSQL roles are a separately reviewed operator bootstrap at
`../deployment/bootstrap/001_direct_database_roles.sql`. They are not applied at API
startup. Runtime reads use base tables under RLS; legacy views remain compatible.
See [the explicit transition and recovery procedure](../deployment/README.md).
Do not push the root composed schema or run remote migrations as a setup shortcut.
