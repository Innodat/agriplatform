"""Atomic selection insert/original receipt; no network work inside the write transaction."""
import asyncio
from uuid import uuid4
import psycopg
from psycopg.rows import dict_row
from runtime_database import validated_url
from async_transaction_context import transaction,execute
from contracts import Receipt,SelectionResult
from transaction_context import WriteError

class Repository:
    def __init__(self,url):
        parsed=validated_url(url)
        self.url=parsed.set(drivername='postgresql').render_as_string(hide_password=False)
    def __repr__(self):return '<LeaveRepository private>'
    async def run(self,kind,context,budget,operation):
        conn=None;expiry=None
        try:
            async with asyncio.timeout_at(budget.deadline):
                conn=await psycopg.AsyncConnection.connect(self.url,connect_timeout=max(1,min(3,int(budget.remaining()))),row_factory=dict_row)
                expiry=asyncio.get_running_loop().call_at(budget.deadline,conn.pgconn.finish)
                result=None
                # Unique insertion waits for the competing transaction; a separate
                # READ COMMITTED query then sees its original committed event.
                async with transaction(conn,budget,context.local):
                    parameters={'org':context.local.org_id,'account':context.local.account_id,'actor':context.local.actor_id,'operation':operation}
                    if kind=='select':
                        await execute(conn,budget,'''INSERT INTO leave.organization_selection(event_id,org_id,account_id,actor_id,membership_id,operation_id,decision_id,checked_at)
                            VALUES(%(event)s,%(org)s,%(account)s,%(actor)s,%(membership)s,%(operation)s,%(decision)s,%(checked)s)
                            ON CONFLICT(org_id,actor_id,operation_id) DO NOTHING''',parameters|{'event':str(uuid4()),'membership':int(context.decision.membership_id),'decision':context.decision.decision_id,'checked':context.decision.checked_at})
                    cursor=await execute(conn,budget,'''SELECT event_id,org_id,account_id,actor_id,operation_id FROM leave.organization_selection
                        WHERE org_id=%(org)s AND account_id=%(account)s AND actor_id=%(actor)s AND operation_id=%(operation)s''',parameters)
                    row=await cursor.fetchone()
                    if row is not None:
                        if tuple(str(row[k]) for k in ('org_id','account_id','actor_id','operation_id'))!=(context.local.org_id,context.local.account_id,context.local.actor_id,operation):raise WriteError('operation_verification_unavailable')
                        result=Receipt(operation_id=operation,result=SelectionResult(org_id=context.local.org_id,event_id=str(row['event_id']))).model_dump()
                    if kind=='select' and result is None:raise WriteError('outcome_unresolved')
                return result
        except asyncio.CancelledError:raise
        except Exception:raise WriteError('outcome_unresolved' if kind=='select' else 'operation_verification_unavailable') from None
        finally:
            if expiry is not None:expiry.cancel()
            if conn is not None:
                conn.pgconn.finish()
                try:
                    async with asyncio.timeout(.1):await conn.close()
                except BaseException:pass
