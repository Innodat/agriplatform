"""Reader ownership and deadline failures complement actual PostgreSQL qualification."""
import asyncio
import logging
from pathlib import Path
import sys
import time
from types import SimpleNamespace
from uuid import UUID

import pytest
from psycopg import AsyncConnection
from psycopg.conninfo import make_conninfo

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from actor_display_native import NativeActorDisplayReader,NativeReadFailure,PrivateConnection,NativeConfigurationFailure

ACTOR=UUID(int=1001)
PRIVATE='synthetic-private-diagnostic-name-and-credential'
EXPLICIT=dict(host='127.0.0.1',port='6543',dbname='actor_native_synthetic',
              user='identity_actor_display_runtime',password=PRIVATE)


@pytest.fixture(autouse=True)
def no_ambient_selector_routes(monkeypatch):
    for name in ('PGHOSTADDR','PGSERVICE','PGSERVICEFILE'):
        monkeypatch.delenv(name,raising=False)


class Connection(AsyncConnection):
    def __init__(self,rows=None,*,blocked=False,rollback_failure=False,finish_failure=False):
        self.calls=[];self.finished=False;self.started=asyncio.Event()
        self.rows=rows if rows is not None else [(ACTOR,'Retained')]
        self.blocked=blocked;self.rollback_failure=rollback_failure;self.finish_failure=finish_failure
        self.pgconn=SimpleNamespace(finish=self.finish,status=1)
        self._pool=None

    def finish(self):
        self.finished=True
        if self.finish_failure:raise RuntimeError(PRIVATE)

    async def execute(self,query,params=None):
        self.calls.append((query,params))
        if query.startswith('SELECT actor_id'):
            self.started.set()
            if self.blocked:
                try:await asyncio.sleep(20)
                except asyncio.CancelledError:
                    assert self.finished,'transport must close before cancelling driver wait'
                    await asyncio.sleep(.01)
                    raise
        if query=='ROLLBACK' and self.rollback_failure:raise RuntimeError(PRIVATE)
        return self

    async def fetchmany(self,bound):
        return self.rows[:bound]


def run(coroutine):
    return asyncio.run(coroutine)


def test_missing_differs_from_failed_read_and_every_connection_closes():
    async def scenario():
        empty=Connection([])
        async def acquire():return empty
        assert await NativeActorDisplayReader(acquire)((ACTOR,),time.monotonic()+1)==[]
        assert empty.finished
        broken=Connection(rollback_failure=True)
        async def broken_acquire():return broken
        with pytest.raises(NativeReadFailure,match='identity_actor_display_read_failed') as error:
            await NativeActorDisplayReader(broken_acquire)((ACTOR,),time.monotonic()+1)
        assert broken.finished and PRIVATE not in str(error.value)
    run(scenario())


def test_bound_uuid_array_read_only_original_remaining_budget():
    async def scenario():
        connection=Connection()
        async def acquire():
            await asyncio.sleep(.03)
            return connection
        deadline=time.monotonic()+.2
        assert await NativeActorDisplayReader(acquire)((ACTOR,),deadline)==[{'actor_id':ACTOR,'display_name':'Retained'}]
        assert connection.calls[0]==('BEGIN READ ONLY',None)
        assert connection.calls[2][1]==([ACTOR],)
        budget=int(connection.calls[1][1][0][:-2])
        assert 1<=budget<170 and connection.finished
    run(scenario())


@pytest.mark.parametrize('rows',[
    [(UUID(int=9000),'Foreign')],[(ACTOR,'One'),(ACTOR,'Two')],
    [(ACTOR,'')],[(ACTOR,'private\nname')],[(str(ACTOR),'Wrong type')],
    [(ACTOR,'a'*257)],[(ACTOR,'Name','extra')],
])
def test_invalid_projection_fails_batch_and_closes(rows):
    async def scenario():
        connection=Connection(rows)
        async def acquire():return connection
        with pytest.raises(NativeReadFailure):
            await NativeActorDisplayReader(acquire)((ACTOR,),time.monotonic()+1)
        assert connection.finished
    run(scenario())


def test_acquisition_consumes_original_deadline_and_is_joined():
    async def scenario():
        ended=[]
        async def acquire():
            try:await asyncio.sleep(20)
            finally:ended.append(True)
        started=time.monotonic()
        with pytest.raises(TimeoutError):
            await NativeActorDisplayReader(acquire)((ACTOR,),started+.06)
        assert ended==[True] and time.monotonic()-started<.3
    run(scenario())


def test_repeated_cancellation_closes_transport_and_owns_unwind(caplog):
    async def scenario():
        connection=Connection(blocked=True)
        async def acquire():return connection
        task=asyncio.create_task(NativeActorDisplayReader(acquire)((ACTOR,),time.monotonic()+1))
        await connection.started.wait()
        task.cancel();await asyncio.sleep(0);task.cancel();await asyncio.sleep(0);task.cancel()
        with pytest.raises(asyncio.CancelledError):await task
        assert connection.finished
        assert not [t for t in asyncio.all_tasks() if t is not asyncio.current_task() and not t.done()]
    with caplog.at_level(logging.DEBUG):run(scenario())
    assert PRIVATE not in caplog.text


def test_cleanup_exception_is_private_failure_not_success_or_task_exception(caplog):
    async def scenario():
        connection=Connection(finish_failure=True)
        async def acquire():return connection
        with pytest.raises(NativeReadFailure) as error:
            await NativeActorDisplayReader(acquire)((ACTOR,),time.monotonic()+1)
        assert PRIVATE not in str(error.value)
        assert not [t for t in asyncio.all_tasks() if t is not asyncio.current_task() and not t.done()]
    with caplog.at_level(logging.DEBUG):run(scenario())
    assert PRIVATE not in caplog.text


def test_deadline_cannot_publish_late_rows():
    async def scenario():
        connection=Connection(blocked=True)
        async def acquire():return connection
        with pytest.raises(TimeoutError):
            await NativeActorDisplayReader(acquire)((ACTOR,),time.monotonic()+.06)
        assert connection.finished
    run(scenario())


@pytest.mark.parametrize('selected',[(),(UUID(int=0),),(ACTOR,ACTOR),('not-uuid',),tuple(UUID(int=i+1) for i in range(204))])
def test_invalid_selection_never_acquires(selected):
    async def acquire():raise AssertionError('must not acquire')
    with pytest.raises(NativeReadFailure):run(NativeActorDisplayReader(acquire)(selected,time.monotonic()+1))


def test_connection_and_reader_representations_are_private():
    connection=PrivateConnection(make_conninfo(**EXPLICIT))
    assert PRIVATE not in repr(connection)
    assert PRIVATE not in repr(NativeActorDisplayReader(connection))


def test_actual_psycopg_connect_logging_is_private_without_silencing_other_tasks(monkeypatch,caplog):
    import psycopg.connection_async as driver
    from psycopg import OperationalError
    async def scenario():
        entered=asyncio.Event();resume=asyncio.Event();waits=[]
        async def failed_wait(*args,**kwargs):
            waits.append(True);entered.set();await resume.wait()
            raise OperationalError(PRIVATE)
        monkeypatch.setattr(driver.waiting,'wait_conn_async',failed_wait)
        reader=NativeActorDisplayReader(PrivateConnection(make_conninfo(**EXPLICIT)))
        task=asyncio.create_task(reader((ACTOR,),time.monotonic()+1))
        await entered.wait()
        logging.getLogger('psycopg').debug('unrelated concurrent diagnostic')
        resume.set()
        with pytest.raises(NativeReadFailure):await task
        logging.getLogger('psycopg').debug('unrelated diagnostic after operation')
        assert waits==[True]
    with caplog.at_level(logging.DEBUG,logger='psycopg'):run(scenario())
    assert PRIVATE not in caplog.text
    assert 'connection attempt:' not in caplog.text and 'connection failed:' not in caplog.text
    assert 'unrelated concurrent diagnostic' in caplog.text
    assert 'unrelated diagnostic after operation' in caplog.text


@pytest.mark.parametrize('missing',list(EXPLICIT))
def test_incomplete_conninfo_cannot_inherit_ambient_target_or_login(monkeypatch,missing):
    monkeypatch.setenv('PGHOST','ambient.invalid');monkeypatch.setenv('PGUSER','postgres')
    monkeypatch.setenv('PGPORT','5432');monkeypatch.setenv('PGDATABASE','ambient')
    monkeypatch.setenv('PGPASSWORD','ambient-secret')
    parameters={name:value for name,value in EXPLICIT.items() if name!=missing}
    with pytest.raises(NativeConfigurationFailure,match='^identity_actor_display_configuration_invalid$'):
        PrivateConnection(make_conninfo(**parameters))


@pytest.mark.parametrize('parameters',[
    {**EXPLICIT,'user':'postgres'},{**EXPLICIT,'password':''},
    {**EXPLICIT,'host':''},{**EXPLICIT,'port':'0'},
    {**EXPLICIT,'service':'ambient'},{**EXPLICIT,'dbname':'postgresql://ambient/other'},
])
def test_invalid_explicit_connection_configuration_fails_safely(parameters):
    with pytest.raises(NativeConfigurationFailure) as error:PrivateConnection(make_conninfo(**parameters))
    assert PRIVATE not in str(error.value)


@pytest.mark.parametrize('selector',['PGHOSTADDR','PGSERVICE','PGSERVICEFILE'])
def test_ambient_alternate_routes_are_refused_at_construction_and_acquisition(monkeypatch,selector):
    connection=PrivateConnection(make_conninfo(**EXPLICIT))
    monkeypatch.setenv(selector,'synthetic-ambient-route')
    with pytest.raises(NativeConfigurationFailure):PrivateConnection(make_conninfo(**EXPLICIT))
    with pytest.raises(NativeConfigurationFailure):run(connection())


def test_complete_explicit_synthetic_configuration_ignores_ordinary_ambient_defaults(monkeypatch):
    monkeypatch.setenv('PGHOST','ambient.invalid');monkeypatch.setenv('PGUSER','postgres')
    observed=[]
    async def connect(conninfo,**kwargs):
        from psycopg.conninfo import conninfo_to_dict
        observed.append(conninfo_to_dict(conninfo));return 'synthetic connection'
    monkeypatch.setattr(AsyncConnection,'connect',connect)
    assert run(PrivateConnection(make_conninfo(**EXPLICIT))())=='synthetic connection'
    assert observed==[EXPLICIT]
