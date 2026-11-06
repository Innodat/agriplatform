"""Separate private history; controlled upgrade only, no API/startup migration."""
import os
from pathlib import Path
import sys
from alembic import context
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine,pool,text
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studies-database-tools'))
from owned_migration import MigrationPolicy,MigrationError,migration_transaction
from sqlalchemy.engine import make_url
config=context.config
POLICY=MigrationPolicy('scribeswell_studies','scribeswell_studies_migrator','scribeswell_studies_runtime','scribeswell_studies_operator')
engine=None
# A reused Config must never retain a previous committed observation after failure.
for name in ('scribeswell_studies_before','scribeswell_studies_after'):
    config.attributes.pop(name,None)
try:
    if context.is_offline_mode():raise ValueError
    url=make_url(os.environ['SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL'])
    if url.drivername not in ('postgresql','postgresql+psycopg') or url.username!=POLICY.migrator or not url.password or url.query.get('options'):raise ValueError
    url=url.set(drivername='postgresql+psycopg')
    engine=create_engine(url,poolclass=pool.NullPool,hide_parameters=True,connect_args={'connect_timeout':5,'passfile':'/dev/null'})
    with migration_transaction(engine,POLICY) as connection:
        context.configure(connection=connection,version_table_schema=POLICY.schema,transactional_ddl=True)
        options=context.get_context().opts
        if getattr(options.get('fn'),'__name__',None)!='upgrade' or options.get('destination_rev')!='head':raise ValueError
        history=ScriptDirectory.from_config(config)
        heads=history.get_heads()
        expected=config.attributes.get('scribeswell_studies_expected_head')
        if len(heads)!=1 or (expected is not None and heads!=[expected]):raise ValueError
        revisions={revision.revision for revision in history.walk_revisions()}
        current=context.get_context().get_current_heads()
        if len(current)>1 or (current and current[0] not in revisions):raise ValueError
        before=current[0] if current else None
        with context.begin_transaction():context.run_migrations()
        after=context.get_context().get_current_heads()
        if after!=tuple(heads):raise ValueError
        connection.execute(text('REVOKE ALL ON scribeswell_studies.alembic_version FROM PUBLIC,scribeswell_studies_runtime,scribeswell_studies_operator'))
    # migration_transaction exits only after the transaction commit succeeds.
    config.attributes['scribeswell_studies_before']=before
    config.attributes['scribeswell_studies_after']=after[0]
except Exception:
    raise MigrationError('scribeswell_studies_migration_failed_requires_reconciliation') from None
finally:
    if engine is not None:engine.dispose()
