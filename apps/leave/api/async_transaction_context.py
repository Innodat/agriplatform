# GENERATED neutral owner-copy template; update builder source and regenerate consumers.
"""Psycopg async adapter for canonical bounded context and exact operation locking.

Budget, verified shape and lock serialization remain in transaction_context. Owner
closes the dedicated transport at cancellation/deadline, including commit cleanup.
"""
from contextlib import asynccontextmanager
from psycopg import Error,OperationalError,InterfaceError
from psycopg.errors import LockNotAvailable
from psycopg.pq import TransactionStatus
from transaction_context import VerifiedContext,OutcomeKey,WriteError,outcome_lock_key

async def _limits(conn,budget):
    await conn.execute("SELECT set_config('statement_timeout',%s,true),set_config('lock_timeout',%s,true)",(str(budget.milliseconds(5)),str(budget.milliseconds(2))))

async def execute(conn,budget,statement,parameters=None):
    try:
        await _limits(conn,budget)
        result=await conn.execute(statement,parameters or {})
        budget.remaining()
        return result
    except (OperationalError,InterfaceError):raise WriteError('outcome_unresolved') from None
    except Error:raise WriteError('internal_error') from None

@asynccontextmanager
async def transaction(conn,budget,context):
    if type(context) is not VerifiedContext or conn.autocommit or conn.info.transaction_status!=TransactionStatus.IDLE:raise WriteError('invalid_write_context')
    budget.local_start(context)
    committing=False
    try:
        async with conn.transaction():
            await conn.execute('SET TRANSACTION ISOLATION LEVEL READ COMMITTED')
            await _limits(conn,budget)
            await conn.execute("SELECT set_config('transaction_timeout',%s,true),set_config('app.org_id',%s,true),set_config('app.account_id',%s,true),set_config('app.actor_id',%s,true),set_config('app.mode',%s,true)",(str(budget.milliseconds(10)),context.org_id,context.account_id,context.actor_id,context.mode))
            yield conn
            await _limits(conn,budget)
            budget.remaining()
            committing=True
        # Commit may be durable with a late acknowledgement. Never infer rollback.
        budget.remaining()
    except (OperationalError,InterfaceError):raise WriteError('outcome_unresolved') from None
    except Error:raise WriteError('outcome_unresolved' if committing else 'internal_error') from None

async def outcome_lock(conn,budget,key,context):
    if (type(key) is not OutcomeKey or type(context) is not VerifiedContext or (key.org_id,key.account_id)!=(context.org_id,context.account_id) or conn.autocommit or conn.info.transaction_status!=TransactionStatus.INTRANS):raise WriteError('invalid_write_context')
    try:
        await _limits(conn,budget)
        await conn.execute('SELECT pg_advisory_xact_lock(%s)',(outcome_lock_key(key),))
        budget.remaining()
    except LockNotAvailable:raise WriteError('operation_busy') from None
    except (OperationalError,InterfaceError):raise WriteError('outcome_unresolved') from None
    except Error as error:raise WriteError('operation_busy' if error.sqlstate=='55P03' else 'internal_error') from None
