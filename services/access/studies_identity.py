"""Live primary-account evidence and current Identity profile, never JWT claims."""
import asyncio
import time
from datetime import datetime,timezone
from uuid import UUID
import httpx
import psycopg
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

class StudiesFailure(Exception):
    def __init__(self,status,error_id):self.status=status;self.error_id=error_id

def remaining(deadline):
    value=deadline-time.monotonic()
    if value<=0:raise StudiesFailure(503,'authorization_unavailable')
    return value

def account_uuid(value):
    if not isinstance(value,(str,UUID)):raise ValueError('account')
    account=UUID(str(value))
    if not account.int:raise ValueError('account')
    return account

async def live_account(authorization,deadline,environment):
    if not authorization.startswith('Bearer ') or not authorization[7:].strip():
        raise StudiesFailure(401,'authentication_required')
    try:
        budget=min(2.0,remaining(deadline))
        async with asyncio.timeout(budget):
            async with httpx.AsyncClient(timeout=budget,follow_redirects=False) as client:
                response=await client.get(environment['SUPABASE_URL'].rstrip('/')+'/auth/v1/user',
                    headers={'Authorization':authorization,'apikey':environment['SUPABASE_ANON_KEY']})
                if response.status_code in (401,403):raise StudiesFailure(401,'authentication_required')
                response.raise_for_status()
                value=response.json()
                account=account_uuid(value['id'])
                if value.get('deleted_at') is not None or value.get('is_anonymous') is True:
                    raise StudiesFailure(403,'access_denied')
                banned=value.get('banned_until')
                if banned and datetime.fromisoformat(banned.replace('Z','+00:00'))>datetime.now(timezone.utc):
                    raise StudiesFailure(403,'access_denied')
                verified=value.get('email_confirmed_at')
                if not verified or not isinstance(value.get('email'),str) or not value['email'].strip():
                    raise StudiesFailure(403,'identity.verification_required')
                timestamp=datetime.fromisoformat(verified.replace('Z','+00:00'))
                if timestamp.tzinfo is None or timestamp>datetime.now(timezone.utc):raise ValueError('verification')
                remaining(deadline)
                return account
    except StudiesFailure:raise
    except (httpx.HTTPError,TimeoutError,ValueError,TypeError,KeyError,AttributeError):
        raise StudiesFailure(503,'authorization_unavailable') from None

async def transaction(db,account,deadline,sql,parameters=None,readonly=False,error_id='authorization_unavailable'):
    if db is None:raise StudiesFailure(503,error_id)
    try:
        async with asyncio.timeout(remaining(deadline)):
            async with (db.begin(deadline) if isinstance(db,AsyncDatabase) else db.begin()) as conn:
                if readonly:await conn.execute(text('SET TRANSACTION READ ONLY'))
                # All values are positive; zero would silently disable PostgreSQL bounds.
                milliseconds=max(1,int(remaining(deadline)*1000))
                await conn.execute(text("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',:account,true),set_config('app.actor_id','',true),set_config('app.org_id','',true),set_config('statement_timeout',:statement,true),set_config('lock_timeout',:lock,true),set_config('idle_in_transaction_session_timeout',:idle,true)"),
                    {'account':str(account),'statement':str(min(2000,milliseconds)),
                     'lock':str(min(1000,milliseconds)),'idle':str(milliseconds)})
                remaining(deadline)
                row=(await conn.execute(text(sql),parameters or {})).mappings().one_or_none()
                remaining(deadline)
            remaining(deadline)
            return row
    except StudiesFailure:raise
    except (SQLAlchemyError,psycopg.Error,TimeoutError,OSError) as error:
        state=getattr(getattr(error,'orig',error),'sqlstate',None)
        if state=='IS003':raise StudiesFailure(403,'access_denied') from None
        if state=='IS006':raise StudiesFailure(403,'identity.verification_required') from None
        raise StudiesFailure(503,error_id) from None

def bound_actor(row,account,allow_absent=False):
    try:
        if row is None or account_uuid(row['account_id'])!=account:raise ValueError('binding')
        if row['actor_id'] is None and allow_absent:return None
        return account_uuid(row['actor_id'])
    except (ValueError,KeyError,TypeError):raise StudiesFailure(503,'identity.setup_unavailable') from None

async def evidence(db,account,deadline):
    row=await transaction(db,account,deadline,'SELECT account_id,actor_id FROM identity.studies_account_evidence()',readonly=True,error_id='identity.setup_unavailable')
    return bound_actor(row,account,True)

async def prepare(db,account,operation,deadline):
    row=await transaction(db,account,deadline,'SELECT account_id,actor_id FROM identity.prepare_studies_account(:operation)',{'operation':operation},error_id='identity.setup_unavailable')
    return bound_actor(row,account)

class AsyncDatabase:
    """Dedicated async psycopg connections; no blocking adapter or write thread.

    Connections close after each transaction so verified context never crosses requests.
    No new pool dependency is required by this first consumer.
    """
    def __init__(self,url):self.url=url.replace('postgresql+psycopg://','postgresql://',1)
    def begin(self,deadline):
        from contextlib import asynccontextmanager
        import psycopg
        from psycopg.rows import dict_row
        @asynccontextmanager
        async def begin():
            connection=await psycopg.AsyncConnection.connect(self.url,connect_timeout=1,row_factory=dict_row)
            # libpq's public finish closes the dedicated socket synchronously.
            # This runs before cancellation cleanup can wait for psycopg's two
            # five-second cancel phases. Closing never proves server rollback.
            timer=asyncio.get_running_loop().call_at(deadline,connection.pgconn.finish)
            try:
                async with connection.transaction():
                    yield AsyncConnection(connection)
            finally:
                timer.cancel()
                await connection.close()
        return begin()

class AsyncConnection:
    def __init__(self,connection):self.connection=connection
    async def execute(self,statement,parameters=None):
        # Every statement is owner-authored. psycopg binds parameters itself.
        import re
        sql=re.sub(r'(?<!:):([a-z_]+)',r'%(\1)s',str(statement))
        cursor=await self.connection.execute(sql,parameters)
        rows=await cursor.fetchall() if cursor.description else []
        return AsyncRows(rows)
class AsyncRows:
    def __init__(self,rows):self.rows=rows
    def mappings(self):return self
    def one_or_none(self):
        if len(self.rows)>1:raise ValueError('owner_row_count')
        return self.rows[0] if self.rows else None
