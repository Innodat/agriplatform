# Edge-case review findings received from user

Received 2026-10-21. External independent review of the standalone edge handoff.
Raw findings below are not yet triaged. Await verification-gap review before
assigning verdicts or changing implementation under BMAD Build step04.

```text
[
{
"location": "services/access/tests/qualify_membership_actor_attribution.py:299",
"trigger_condition": "An unexpected database exception escapes qualification, including actor-fixture uniqueness or constraint failures.",
"guard_snippet": "try: main()\nexcept Exception as error: print('qualification_failed:'+type(error).name,file=sys.stderr); raise SystemExit(1) from None",
"potential_consequence": "Uncaught tracebacks expose SQL and PostgreSQL diagnostic values despite hide_parameters=True."
},
{
"location": "services/access/tests/qualify_membership_actor_attribution.py:278-281",
"trigger_condition": "Another transaction holds a conflicting lock on identity.alembic_version during unknown-history qualification.",
"guard_snippet": "c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))",
"potential_consequence": "The qualification hangs indefinitely with default timeouts, preventing completion and rollback."
}
]
```
