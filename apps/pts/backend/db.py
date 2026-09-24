from contextlib import contextmanager
from sqlalchemy import create_engine, text


def engine(url):
    return create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=5,
                         connect_args={'connect_timeout': 5}, hide_parameters=True)


@contextmanager
def scoped(db, org_id, actor_id, consistent=False):
    with db.begin() as conn:
        if consistent:
            conn.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY"))
        conn.execute(text("SELECT set_config('app.org_id', :org, true), set_config('app.actor_id', :actor, true), set_config('statement_timeout', '10000', true)"),
                     {'org': str(org_id), 'actor': str(actor_id)})
        yield conn


def load(conn):
    library = {}
    for row in conn.execute(text('SELECT id, payload FROM pts.metadata ORDER BY ordinal, id')).mappings():
        library[row['id']] = row['payload']
    for kind in ('rights', 'sources', 'poems', 'witnesses', 'source_documents'):
        library[kind] = list(conn.execute(text(f'SELECT payload FROM pts.{kind} ORDER BY ordinal, id')).scalars())
    if not library.get('schema_version'):
        library['schema_version'] = '1.2'
    return library
