# Proven owner boundary examples

PtS verifies the `transaction_context.py` pattern with actual non-owner PostgreSQL
roles, pool reuse, rollback and concurrent organizations. Copy the helper into the
owning application during future scaffold work; platform build-time examples are
not shared backend runtime implementations.

See `apps/pts/alembic.ini`, its `migrations/env.py`, restricted role bootstrap,
`services/access` current authorization HTTP contract, and `tools/py/deploy_pts.py`
for the independently owned-history pattern. Each owner keeps its own versions and
schema, requires explicit migration configuration, and never migrates on startup.
The builder CLI remains a placeholder; these examples do not claim generation tests
or a working generator. Existing legacy SQL composition remains supported.
