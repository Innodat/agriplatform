"""Proven transaction-local context example. Copy into an owner; no runtime cross-owner import."""
from contextlib import contextmanager
from sqlalchemy import create_engine, text


def engine(url):
    return create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=5,
                         connect_args={'connect_timeout': 5}, hide_parameters=True)


@contextmanager
def scoped(db, org_id, actor_id):
    with db.begin() as conn:
        conn.execute(text("SELECT set_config('app.org_id', :org, true), set_config('app.actor_id', :actor, true), set_config('statement_timeout', '10000', true)"),
                     {'org': str(org_id), 'actor': str(actor_id)})
        yield conn

