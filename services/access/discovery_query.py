"""Fixed multirow owner calls within one short verified-account read transaction."""
import asyncio
import time
import psycopg
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from studies_identity import AsyncDatabase,StudiesFailure,remaining

SQL_SECONDS=2.0

async def read(db,account,deadline,app=None,after=None,page_size=None):
    if db is None:raise StudiesFailure(503,'authorization_unavailable')
    budget=min(SQL_SECONDS,remaining(deadline))
    try:
        async with asyncio.timeout(budget):
            async with (db.begin(min(deadline,time.monotonic()+budget)) if isinstance(db,AsyncDatabase) else db.begin()) as conn:
                await conn.execute(text('SET TRANSACTION READ ONLY'))
                milliseconds=max(1,int(remaining(deadline)*1000))
                await conn.execute(text("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',:account,true),set_config('app.actor_id','',true),set_config('app.org_id','',true),set_config('app.discovery_transaction',pg_current_xact_id()::text,true),set_config('statement_timeout',:statement,true),set_config('lock_timeout',:lock,true),set_config('idle_in_transaction_session_timeout',:idle,true)"),{'account':str(account),'statement':str(min(2000,milliseconds)),'lock':str(min(1000,milliseconds)),'idle':str(milliseconds)})
                if app is None:
                    result=await conn.execute(text('SELECT * FROM access.discover_applications()'))
                else:
                    result=await conn.execute(text('SELECT * FROM access.discover_organizations(:application,:after,:page_size)'),{'application':app,'after':after,'page_size':page_size})
                rows=result.mappings().all()
                remaining(deadline)
            remaining(deadline)
            return rows
    except StudiesFailure:raise
    except (SQLAlchemyError,psycopg.Error,TimeoutError,OSError,ValueError,TypeError,KeyError) as error:
        if getattr(getattr(error,'orig',error),'sqlstate',None)=='ID003':raise StudiesFailure(403,'access_denied') from None
        raise StudiesFailure(503,'authorization_unavailable') from None
