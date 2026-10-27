"""Read-only current authority transactions; live provider runs before opening them."""
import asyncio
import psycopg
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from studies_identity import AsyncDatabase,StudiesFailure,account_uuid,remaining

SQL_SECONDS=2.0

async def current(db,account,org,deadline,function,permission=None):
    if db is None:raise StudiesFailure(503,'authorization_unavailable')
    try:
        budget=min(SQL_SECONDS,remaining(deadline))
        async with asyncio.timeout(budget):
            async with (db.begin(min(deadline,__import__('time').monotonic()+budget)) if isinstance(db,AsyncDatabase) else db.begin()) as conn:
                await conn.execute(text('SET TRANSACTION READ ONLY'))
                await conn.execute(text("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',:account,true),set_config('app.actor_id','',true),set_config('app.org_id',:org,true),set_config('statement_timeout','2000',true),set_config('lock_timeout','1000',true),set_config('idle_in_transaction_session_timeout','2000',true)"),{'account':str(account),'org':str(org) if org else ''})
                # function comes solely from the three fixed owner-authored call sites.
                row=(await conn.execute(text('SELECT * FROM '+function+('(:permission)' if permission is not None else '()')),{'permission':permission} if permission is not None else {})).mappings().one_or_none()
            remaining(deadline)
            return row
    except StudiesFailure:raise
    except (SQLAlchemyError,psycopg.Error,TimeoutError,OSError,ValueError):
        raise StudiesFailure(503,'authorization_unavailable') from None

def bind(row,account,org=None):
    if row is None:raise StudiesFailure(403,'access_denied')
    try:
        if account_uuid(row['account_id'])!=account:raise ValueError('account')
        actor=None if row['actor_id'] is None else account_uuid(row['actor_id'])
        if org:
            if account_uuid(row['org_id'])!=org:raise ValueError('organization')
            member=row['membership_id']
            if type(member) is not int or not 0<member<=9223372036854775807:raise ValueError('membership')
            person=None if row['person_id'] is None else account_uuid(row['person_id'])
            return actor,str(member),person
        return actor,None,None
    except (ValueError,KeyError,TypeError):raise StudiesFailure(503,'authorization_unavailable') from None
