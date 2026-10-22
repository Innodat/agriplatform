"""Transaction-bound fencing, activated only with synthetic fixture authority."""
import os
import sys
from pathlib import Path
import pytest
APP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(APP/'migrations'))
from generate_reference import prepared_fixture
from test_owned_migrations import invoke

@pytest.fixture(scope='module')
def fence_database():
    if not os.environ.get('SCRIBESWELL_TEST_DATABASE_URL'):
        pytest.skip('Set SCRIBESWELL_TEST_DATABASE_URL to a disposable local cluster')
    with prepared_fixture() as (admin,url):
        result=invoke(url)
        assert result.returncode==0,result.stderr
        yield admin,url

def test_dormant_control_and_empty_private_structures(fence_database):
    admin,_=fence_database
    assert admin.execute('SELECT singleton,enforcement FROM scribeswell.corpus_fence_control').fetchall()==[(True,False)]
    for table in ('corpus_epoch','corpus_write_binding'):
        assert admin.execute('SELECT count(*) FROM scribeswell.'+table).fetchone()==(0,)

import psycopg
from contextlib import contextmanager, suppress
from concurrent.futures import ThreadPoolExecutor
from test_postgres_acceptance import role_url
TABLES=('book','chapter','verse','word','morpheme')
ATTEMPT='11111111-1111-4111-8111-111111111111'
ACTOR='22222222-2222-4222-8222-222222222222'
DIGEST='a'*64
BIND='SELECT scribeswell.bind_corpus_write(%s,%s,%s,%s)'
TUPLE=('fixture-source',1,ATTEMPT,DIGEST)

@pytest.fixture
def enabled(fence_database):
    admin,url=fence_database
    admin.execute("INSERT INTO scribeswell.corpus_epoch(singleton,source_id,generation,attempt_id,input_sha256,state,created_by_actor_id,updated_by_actor_id) VALUES(true,%s,%s,%s,%s,'updating',%s,%s)",TUPLE+(ACTOR,ACTOR))
    admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=true')
    admin.execute('GRANT EXECUTE ON FUNCTION scribeswell.bind_corpus_write(text,bigint,uuid,text) TO scribeswell_import')
    try:
        yield admin,url
    finally:
        admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=false')
        admin.execute('DELETE FROM scribeswell.corpus_epoch')
        admin.execute('REVOKE EXECUTE ON FUNCTION scribeswell.bind_corpus_write(text,bigint,uuid,text) FROM scribeswell_import')
        for table in TABLES:
            admin.execute('REVOKE DELETE,TRUNCATE ON scribeswell.'+table+' FROM scribeswell_import')
        assert admin.execute('SELECT count(*) FROM scribeswell.corpus_write_binding').fetchone()==(0,)

def importer(url):
    return bounded_connection(url,'scribeswell_import')

def bounded_connection(url,role):
    return psycopg.connect(role_url(url,role),autocommit=True,connect_timeout=5,
        options='-c statement_timeout=6000 -c lock_timeout=5000 -c idle_in_transaction_session_timeout=10000')

@contextmanager
def background(connection,operation):
    pool=ThreadPoolExecutor(max_workers=1)
    future=pool.submit(operation)
    try:
        yield future
    finally:
        if not future.done():
            connection.cancel()
        with suppress(Exception):
            future.result(timeout=7)
        pool.shutdown(wait=False,cancel_futures=True)

def denied(connection,query,params=None):
    with pytest.raises(psycopg.errors.InsufficientPrivilege,match='scribeswell_corpus_write_denied'):
        connection.execute(query,params)

@pytest.mark.parametrize('table',TABLES)
@pytest.mark.parametrize('operation',('insert','update','delete','truncate'))
def test_every_statement_operation_requires_binding(enabled,table,operation):
    admin,url=enabled
    # Extra fixture-only DML grants reach the guard while shipped grants stay narrow.
    admin.execute('GRANT DELETE,TRUNCATE ON '+','.join('scribeswell.'+t for t in TABLES)+' TO scribeswell_import')
    statement={
        'insert':f'INSERT INTO scribeswell.{table} SELECT * FROM scribeswell.{table} WHERE false',
        'update':f'UPDATE scribeswell.{table} SET id=id WHERE false',
        'delete':f'DELETE FROM scribeswell.{table} WHERE false',
        'truncate':f'TRUNCATE scribeswell.{table} CASCADE',
    }[operation]
    with importer(url) as connection:
        denied(connection,statement)
        with connection.transaction():
            connection.execute(BIND,TUPLE)
            connection.execute(statement)
            assert admin.execute('SELECT count(*) FROM scribeswell.corpus_write_binding').fetchone()==(0,)
            # Rollback protects fixture corpus and proves transient binding rollback.
            connection.execute('ROLLBACK')

@pytest.mark.parametrize('value',[
    ('wrong-source',1,ATTEMPT,DIGEST),
    ('fixture-source',2,ATTEMPT,DIGEST),
    ('fixture-source',1,'33333333-3333-4333-8333-333333333333',DIGEST),
    ('fixture-source',1,ATTEMPT,'b'*64),
    (None,1,ATTEMPT,DIGEST),
])
def test_exact_approved_tuple_required(enabled,value):
    _,url=enabled
    with importer(url) as connection:
        denied(connection,BIND,value)
        denied(connection,'UPDATE scribeswell.book SET id=id WHERE false')

@pytest.mark.parametrize('state',('closed','advanced','missing'))
def test_closed_stale_missing_epoch_denied(enabled,state):
    admin,url=enabled
    if state=='closed':admin.execute("UPDATE scribeswell.corpus_epoch SET state='closed'")
    if state=='advanced':admin.execute('UPDATE scribeswell.corpus_epoch SET generation=2')
    if state=='missing':admin.execute('DELETE FROM scribeswell.corpus_epoch')
    with importer(url) as connection:
        denied(connection,BIND,TUPLE)
        denied(connection,'UPDATE scribeswell.book SET id=id WHERE false')

@pytest.mark.parametrize('finish',('commit','rollback','early_constraints'))
def test_binding_dies_at_transaction_boundary_and_pool_reuse(enabled,finish):
    admin,url=enabled
    with importer(url) as connection:
        connection.execute('BEGIN')
        connection.execute(BIND,TUPLE)
        assert connection.execute('SELECT pg_current_xact_id()::text').fetchone()[0]
        connection.execute('UPDATE scribeswell.book SET id=id WHERE false')
        if finish=='early_constraints':
            connection.execute('SET CONSTRAINTS ALL IMMEDIATE')
            denied(connection,'UPDATE scribeswell.book SET id=id WHERE false')
            connection.execute('ROLLBACK')
        else:
            connection.execute(finish)
        assert admin.execute('SELECT count(*) FROM scribeswell.corpus_write_binding').fetchone()==(0,)
        denied(connection,'UPDATE scribeswell.book SET id=id WHERE false')
        with connection.transaction():
            connection.execute(BIND,TUPLE)
            connection.execute('UPDATE scribeswell.book SET id=id WHERE false')
        assert admin.execute('SELECT count(*) FROM scribeswell.corpus_write_binding').fetchone()==(0,)


def test_guc_copy_and_other_backend_have_no_authority(enabled):
    _,url=enabled
    with importer(url) as original, importer(url) as copied:
        with original.transaction():
            original.execute(BIND,TUPLE)
            copied.execute("SELECT set_config('scribeswell.source_id',%s,false),set_config('scribeswell.generation','1',false),set_config('scribeswell.attempt_id',%s,false),set_config('scribeswell.input_sha256',%s,false)",(TUPLE[0],ATTEMPT,DIGEST))
            denied(copied,'UPDATE scribeswell.book SET id=id WHERE false')
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                copied.execute('INSERT INTO scribeswell.corpus_write_binding SELECT * FROM scribeswell.corpus_write_binding')


def test_copy_and_upsert_share_fence(enabled):
    admin,url=enabled
    with importer(url) as connection:
        def copy():
            with connection.cursor().copy('COPY scribeswell.book FROM STDIN') as stream:
                stream.write_row((1,'Gen','Genesis','א','old','torah',1))
        # Shipped RLS rejects COPY before trigger execution. Temporarily remove
        # only that earlier fixture barrier to qualify the underlying fence too.
        with pytest.raises(psycopg.errors.FeatureNotSupported,match='row-level security'):copy()
        admin.execute('ALTER TABLE scribeswell.book DISABLE ROW LEVEL SECURITY')
        try:
            with pytest.raises(psycopg.errors.InsufficientPrivilege,match='scribeswell_corpus_write_denied'):copy()
            statement="INSERT INTO scribeswell.book VALUES(1,'Gen','Genesis','א','old','torah',1) ON CONFLICT(id) DO UPDATE SET name_en=excluded.name_en"
            denied(connection,statement)
            with connection.transaction():
                connection.execute(BIND,TUPLE)
                copy()
                connection.execute(statement)
                connection.execute('ROLLBACK')
        finally:admin.execute('ALTER TABLE scribeswell.book ENABLE ROW LEVEL SECURITY')

@pytest.mark.parametrize('role',('anon','authenticated','service_role','scribeswell_runtime','scribeswell_import'))
def test_shipped_private_access_denied(fence_database,role):
    admin,url=fence_database
    with admin.transaction():
        admin.execute('SET LOCAL ROLE '+role)
        for table in ('corpus_fence_control','corpus_epoch','corpus_write_binding'):
            for action in ('SELECT','INSERT','UPDATE','DELETE','TRUNCATE','TRIGGER'):
                assert not admin.execute('SELECT has_table_privilege(current_user,%s,%s)',('scribeswell.'+table,action)).fetchone()[0]
        for routine in ('bind_corpus_write(text,bigint,uuid,text)','guard_corpus_write()','cleanup_corpus_write_binding()'):
            assert not admin.execute('SELECT has_function_privilege(current_user,%s,\'EXECUTE\')',('scribeswell.'+routine,)).fetchone()[0]
    if role in ('scribeswell_runtime','scribeswell_import'):
        with psycopg.connect(role_url(url,role),autocommit=True) as connection:
            for statement in ('SET ROLE scribeswell_migrator','ALTER TABLE scribeswell.book DISABLE TRIGGER corpus_write_fence',"SET session_replication_role='replica'",'SELECT * FROM scribeswell.corpus_write_binding',BIND.replace('%s',"NULL")):
                with pytest.raises(psycopg.errors.InsufficientPrivilege):connection.execute(statement)


def test_actual_login_required_even_with_execute(enabled):
    _,url=enabled
    with bounded_connection(url,'scribeswell_migrator') as owner:
        denied(owner,BIND,TUPLE)


def test_missing_control_fails_closed_even_dormant(fence_database):
    admin,url=fence_database
    admin.execute('DELETE FROM scribeswell.corpus_fence_control')
    try:
        with importer(url) as connection:
            denied(connection,'UPDATE scribeswell.book SET id=id WHERE false')
    finally:admin.execute('INSERT INTO scribeswell.corpus_fence_control VALUES(true,false)')


def wait_blocked(admin,pid,blocker):
    import time
    deadline=time.monotonic()+2
    while time.monotonic()<deadline:
        if blocker in admin.execute('SELECT pg_blocking_pids(%s)',(pid,)).fetchone()[0]:return
        time.sleep(.01)
    pytest.fail('transition must be observed blocked by the active write transaction')

@pytest.mark.parametrize('change',('generation=generation+1',"state='closed'"))
def test_epoch_transition_waits_for_bound_write(enabled,change):
    admin,url=enabled
    with importer(url) as connection, bounded_connection(url,'scribeswell_migrator') as owner:
        connection.execute('BEGIN')
        connection.execute(BIND,TUPLE)
        connection.execute('UPDATE scribeswell.book SET id=id WHERE false')
        def change_epoch():
            # Future owner commands follow the same control-before-epoch order.
            with owner.transaction():
                owner.execute('SELECT enforcement FROM scribeswell.corpus_fence_control WHERE singleton FOR SHARE')
                owner.execute('UPDATE scribeswell.corpus_epoch SET '+change)
        with background(owner,change_epoch) as transition:
            try:
                wait_blocked(admin,owner.info.backend_pid,connection.info.backend_pid)
                assert not transition.done()
            finally:connection.execute('COMMIT')
            transition.result(timeout=5)
        denied(connection,'UPDATE scribeswell.book SET id=id WHERE false')


def test_dormant_writer_holds_control_until_commit(fence_database):
    admin,url=fence_database
    with importer(url) as connection, bounded_connection(url,'scribeswell_migrator') as owner:
        connection.execute('BEGIN')
        connection.execute('UPDATE scribeswell.book SET id=id WHERE false')
        try:
            with background(owner,lambda:owner.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=true')) as transition:
                try:
                    wait_blocked(admin,owner.info.backend_pid,connection.info.backend_pid)
                    assert not transition.done()
                finally:connection.execute('COMMIT')
                transition.result(timeout=5)
            denied(connection,'UPDATE scribeswell.book SET id=id WHERE false')
        finally:admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=false')

@pytest.mark.parametrize('source',('', 'a'*65, ' space', 'α', 'a/b', 'a\n'))
def test_epoch_source_label_matches_evidence_namespace(fence_database,source):
    admin,_=fence_database
    with pytest.raises(psycopg.errors.CheckViolation):
        admin.execute("INSERT INTO scribeswell.corpus_epoch(singleton,source_id,generation,attempt_id,input_sha256,state,created_by_actor_id,updated_by_actor_id) VALUES(true,%s,1,%s,%s,'updating',%s,%s)",(source,ATTEMPT,DIGEST,ACTOR,ACTOR))


def test_committed_bound_business_writes_survive_binding_cleanup(enabled):
    admin,url=enabled
    try:
        with importer(url) as connection:
            with connection.transaction():
                connection.execute(BIND,TUPLE)
                connection.execute(BIND,TUPLE)  # ON CONFLICT retains this transaction's authority.
                connection.execute("INSERT INTO scribeswell.book VALUES (1,'Gen','Genesis','א','old','torah',1)")
                connection.execute('INSERT INTO scribeswell.chapter VALUES (101,1,1)')
                connection.execute('INSERT INTO scribeswell.verse VALUES (201,101,1,1,1)')
                connection.execute("INSERT INTO scribeswell.word VALUES (301,201,1,'אָב','אָב','1','HNcmsa')")
                connection.execute("INSERT INTO scribeswell.morpheme(id,word_id,segment_index,language,part_of_speech,pos_code) VALUES (401,301,0,'hebrew','noun','Ncmsa')")
                connection.execute("UPDATE scribeswell.book SET name_en='Genesis committed' WHERE id=1")
            # Separate admin connection observes committed corpus but no context.
            assert admin.execute('SELECT count(*) FROM scribeswell.corpus_write_binding').fetchone()==(0,)
            for table in TABLES:
                assert admin.execute('SELECT count(*) FROM scribeswell.'+table).fetchone()==(1,)
            assert admin.execute('SELECT name_en FROM scribeswell.book WHERE id=1').fetchone()==('Genesis committed',)
            denied(connection,"UPDATE scribeswell.book SET name_en='unbound' WHERE id=1")
            assert admin.execute('SELECT name_en FROM scribeswell.book WHERE id=1').fetchone()==('Genesis committed',)
    finally:
        admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=false')
        admin.execute('TRUNCATE scribeswell.book CASCADE')


@pytest.mark.parametrize('change',('generation=2',"state='closed'"))
def test_transition_first_waiting_binder_rechecks_committed_epoch(enabled,change):
    admin,url=enabled
    with importer(url) as connection, bounded_connection(url,'scribeswell_migrator') as owner:
        owner.execute('BEGIN')
        owner.execute('SELECT enforcement FROM scribeswell.corpus_fence_control WHERE singleton FOR SHARE')
        owner.execute('UPDATE scribeswell.corpus_epoch SET '+change)
        try:
            with background(connection,lambda:connection.execute(BIND,TUPLE)) as binding:
                try:
                    wait_blocked(admin,connection.info.backend_pid,owner.info.backend_pid)
                    assert not binding.done()
                finally:owner.execute('COMMIT')
                with pytest.raises(psycopg.errors.InsufficientPrivilege,match='scribeswell_corpus_write_denied'):
                    binding.result(timeout=7)
            denied(connection,'UPDATE scribeswell.book SET id=id WHERE false')
            # A subsequent owner recovery creates a fresh updating generation.
            with owner.transaction():
                owner.execute('SELECT enforcement FROM scribeswell.corpus_fence_control WHERE singleton FOR SHARE')
                owner.execute("UPDATE scribeswell.corpus_epoch SET generation=2,state='updating'")
            with connection.transaction():
                connection.execute(BIND,(TUPLE[0],2,ATTEMPT,DIGEST))
                connection.execute('UPDATE scribeswell.book SET id=id WHERE false')
        finally:owner.execute('ROLLBACK')


def test_savepoint_rollback_removes_new_binding(enabled):
    admin,url=enabled
    with importer(url) as connection:
        connection.execute('BEGIN')
        connection.execute('SAVEPOINT before_binding')
        connection.execute(BIND,TUPLE)
        connection.execute('UPDATE scribeswell.book SET id=id WHERE false')
        connection.execute('ROLLBACK TO SAVEPOINT before_binding')
        denied(connection,'UPDATE scribeswell.book SET id=id WHERE false')
        connection.execute('ROLLBACK')
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_write_binding').fetchone()==(0,)


def test_savepoint_rollback_preserves_earlier_binding(enabled):
    admin,url=enabled
    with importer(url) as connection:
        with connection.transaction():
            connection.execute(BIND,TUPLE)
            connection.execute('SAVEPOINT after_binding')
            connection.execute(BIND,TUPLE)
            connection.execute("INSERT INTO scribeswell.book VALUES (1,'Gen','Genesis','א','old','torah',1)")
            connection.execute('ROLLBACK TO SAVEPOINT after_binding')
            connection.execute('UPDATE scribeswell.book SET id=id WHERE false')
        assert admin.execute('SELECT count(*) FROM scribeswell.book').fetchone()==(0,)
        assert admin.execute('SELECT count(*) FROM scribeswell.corpus_write_binding').fetchone()==(0,)
        denied(connection,'UPDATE scribeswell.book SET id=id WHERE false')


def test_disconnect_rolls_back_bound_write_and_releases_waiting_owner(enabled):
    admin,url=enabled
    connection=importer(url)
    try:
        with bounded_connection(url,'scribeswell_migrator') as owner:
            connection.execute('BEGIN')
            connection.execute(BIND,TUPLE)
            connection.execute("INSERT INTO scribeswell.book VALUES (1,'Gen','Genesis','א','old','torah',1)")
            def advance():
                with owner.transaction():
                    owner.execute('SELECT enforcement FROM scribeswell.corpus_fence_control WHERE singleton FOR SHARE')
                    owner.execute('UPDATE scribeswell.corpus_epoch SET generation=2')
            with background(owner,advance) as transition:
                try:
                    wait_blocked(admin,owner.info.backend_pid,connection.info.backend_pid)
                    assert not transition.done()
                finally:connection.close()
                transition.result(timeout=7)
            assert admin.execute('SELECT generation FROM scribeswell.corpus_epoch').fetchone()==(2,)
            assert admin.execute('SELECT count(*) FROM scribeswell.book').fetchone()==(0,)
            assert admin.execute('SELECT count(*) FROM scribeswell.corpus_write_binding').fetchone()==(0,)
    finally:connection.close()


@pytest.mark.parametrize('table',TABLES)
def test_owner_direct_corpus_dml_has_no_import_login_authority(enabled,table):
    admin,url=enabled
    before=admin.execute('SELECT * FROM scribeswell.'+table).fetchall()
    with bounded_connection(url,'scribeswell_migrator') as owner:
        denied(owner,f'INSERT INTO scribeswell.{table} SELECT * FROM scribeswell.{table} WHERE false')
        denied(owner,f'UPDATE scribeswell.{table} SET id=id WHERE false')
        denied(owner,f'DELETE FROM scribeswell.{table} WHERE false')
        denied(owner,f'TRUNCATE scribeswell.{table} CASCADE')
    assert admin.execute('SELECT * FROM scribeswell.'+table).fetchall()==before


@pytest.mark.parametrize('field,value',[
    ('generation',0),('generation',-1),
    ('attempt_id','00000000-0000-0000-0000-000000000000'),
    ('created_by_actor_id','00000000-0000-0000-0000-000000000000'),
    ('updated_by_actor_id','00000000-0000-0000-0000-000000000000'),
    ('input_sha256','a'*63),('input_sha256','a'*65),
    ('input_sha256','A'*64),('input_sha256','g'*64),
    ('state','ready'),('state',''),('singleton',False),
])
def test_epoch_structural_constraints_reject_invalid_rows(fence_database,field,value):
    from psycopg import sql
    admin,_=fence_database
    values=dict(singleton=True,source_id=TUPLE[0],generation=1,attempt_id=ATTEMPT,
        input_sha256=DIGEST,state='updating',created_by_actor_id=ACTOR,updated_by_actor_id=ACTOR)
    values[field]=value
    statement=sql.SQL('INSERT INTO scribeswell.corpus_epoch ({}) VALUES ({})').format(
        sql.SQL(',').join(map(sql.Identifier,values)),sql.SQL(',').join(sql.Placeholder() for _ in values))
    with pytest.raises(psycopg.errors.CheckViolation):admin.execute(statement,list(values.values()))
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_epoch').fetchone()==(0,)


def test_control_and_epoch_singletons_reject_second_rows(enabled):
    admin,_=enabled
    for table in ('corpus_fence_control','corpus_epoch'):
        before=admin.execute('SELECT * FROM scribeswell.'+table).fetchall()
        with pytest.raises(psycopg.errors.UniqueViolation):
            admin.execute(f'INSERT INTO scribeswell.{table} SELECT * FROM scribeswell.{table}')
        assert admin.execute('SELECT * FROM scribeswell.'+table).fetchall()==before
