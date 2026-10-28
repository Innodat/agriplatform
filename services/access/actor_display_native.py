"""Private, unpooled Psycopg dependency for the isolated actor-display candidate.

The caller supplies the original absolute monotonic deadline. No environment,
global connection, pool, retry, account join, mapping mutation or label cache exists.
"""
import asyncio
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from dataclasses import dataclass
import logging
import os
import time
from uuid import UUID

from psycopg import AsyncConnection
from psycopg.conninfo import conninfo_to_dict
from actor_display_contract import MAX_ACTORS, ResolvedActorDisplay


class NativeReadFailure(RuntimeError):
    def __init__(self):
        super().__init__('identity_actor_display_read_failed')


class NativeConfigurationFailure(RuntimeError):
    def __init__(self):
        super().__init__('identity_actor_display_configuration_invalid')


_PRIVATE_DRIVER_OPERATION=ContextVar('actor_display_private_driver_operation',default=False)


class _PrivateDriverDiagnostics(logging.Filter):
    def filter(self,record):
        return not _PRIVATE_DRIVER_OPERATION.get()


# Installed Psycopg emits connect/resolution/cancel diagnostics on this logger.
# A task-local filter removes this operation's raw records before any handler;
# it leaves unrelated concurrent tasks and the logger's level/handlers unchanged.
logging.getLogger('psycopg').addFilter(_PrivateDriverDiagnostics())


def _reject_ambient_routes():
    if any(os.environ.get(name) for name in ('PGHOSTADDR','PGSERVICE','PGSERVICEFILE')):
        raise NativeConfigurationFailure()


class PrivateConnection:
    """Explicit server-held conninfo; never infer configuration from the process."""
    __slots__=('_conninfo',)

    def __init__(self, conninfo: str):
        _reject_ambient_routes()
        try:
            parameters=conninfo_to_dict(conninfo)
            if (any(not parameters.get(name) or not parameters[name].strip()
                    for name in ('host','port','dbname','user','password'))
                or parameters['user']!='identity_actor_display_runtime'
                or not parameters['port'].isascii() or not parameters['port'].isdigit()
                or not 1<=int(parameters['port'])<=65535
                or ',' in parameters['host']
                or parameters['dbname'].startswith(('postgresql://','postgres://'))
                or '=' in parameters['dbname']
                or any(name in parameters for name in ('service','servicefile'))):
                raise ValueError()
        except Exception:
            raise NativeConfigurationFailure() from None
        self._conninfo=conninfo

    def __repr__(self):
        return '<ActorDisplayConnection private>'

    async def __call__(self):
        _reject_ambient_routes()
        token=_PRIVATE_DRIVER_OPERATION.set(True)
        try:
            return await AsyncConnection.connect(self._conninfo, autocommit=True,
                                                 prepare_threshold=None)
        finally:
            _PRIVATE_DRIVER_OPERATION.reset(token)


@dataclass(frozen=True, repr=False)
class _Outcome:
    rows: object=None
    failed: bool=False


class NativeActorDisplayReader:
    """Own acquisition and every query until the dedicated connection is closed.

    Injected acquisition must return a fresh unpooled Psycopg AsyncConnection and
    cooperate with cancellation, as PrivateConnection does. On interruption finish
    the libpq transport before cancelling the operation: Psycopg's normal query
    cancellation otherwise starts independent five-second cancel/drain budgets and
    can log raw cancellation diagnostics. Closing this read-only transport rolls
    back on the server and releases its locks; it cannot publish a late result.
    """
    __slots__=('_acquire',)

    def __init__(self, acquire: Callable[[], Awaitable[AsyncConnection]]):
        self._acquire=acquire

    def __repr__(self):
        return '<NativeActorDisplayReader private>'

    async def __call__(self, selected: tuple[UUID, ...], deadline: float):
        if (type(selected) is not tuple or not 1<=len(selected)<=MAX_ACTORS
            or any(not isinstance(value,UUID) or not value.int for value in selected)
            or len(set(selected))!=len(selected) or time.monotonic()>=deadline):
            raise NativeReadFailure()
        connection=None
        cleanup_failed=False

        def finish():
            nonlocal cleanup_failed
            if connection is not None:
                # PGconn.finish is local, synchronous and idempotent. There is no
                # pool return or network rollback wait outside the original timer.
                try:
                    connection.pgconn.finish()
                except Exception:
                    cleanup_failed=True

        async def operation():
            nonlocal connection
            token=_PRIVATE_DRIVER_OPERATION.set(True)
            try:
                connection=await self._acquire()
                if not isinstance(connection,AsyncConnection) or getattr(connection,'_pool',None) is not None:
                    raise NativeReadFailure()
                await connection.execute('BEGIN READ ONLY')
                remaining=int((deadline-time.monotonic()-.02)*1000)
                if remaining<1:
                    raise NativeReadFailure()
                await connection.execute("SELECT set_config('statement_timeout',%s,true),set_config('lock_timeout',%s,true)",
                                         (str(remaining)+'ms',str(remaining)+'ms'))
                cursor=await connection.execute('SELECT actor_id,display_name FROM identity.actor_displays(%s::uuid[])',
                                                (list(selected),))
                rows=await cursor.fetchmany(MAX_ACTORS+1)
                if len(rows)>len(selected):
                    raise NativeReadFailure()
                result=[];seen=set()
                for row in rows:
                    if type(row) is not tuple or len(row)!=2 or not isinstance(row[0],UUID) or row[0] not in selected or row[0] in seen:
                        raise NativeReadFailure()
                    ResolvedActorDisplay(actor_id=str(row[0]),status='resolved',display_name=row[1])
                    seen.add(row[0]);result.append({'actor_id':row[0],'display_name':row[1]})
                await connection.execute('ROLLBACK')
                if time.monotonic()>=deadline:
                    raise NativeReadFailure()
                return _Outcome(rows=result)
            except Exception:
                # A shielded task must never finish with private driver diagnostics
                # as its exception (Python3.15 may log these on cancellation).
                return _Outcome(failed=True)
            finally:
                try:
                    finish()
                finally:
                    _PRIVATE_DRIVER_OPERATION.reset(token)

        task=asyncio.create_task(operation())
        try:
            async with asyncio.timeout_at(deadline-.01):
                outcome=await asyncio.shield(task)
        except BaseException:
            finish()
            task.cancel()
            while not task.done():
                try:
                    await asyncio.shield(task)
                except asyncio.CancelledError:
                    # Retain ownership across repeated caller cancellations.
                    finish();task.cancel()
            if not task.cancelled():
                task.result()
            raise
        if outcome.failed or cleanup_failed:
            raise NativeReadFailure()
        return outcome.rows
