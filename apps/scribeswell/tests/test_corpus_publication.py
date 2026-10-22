"""Dormant transactional controller acceptance on disposable PostgreSQL 17."""
import os
import sys
from pathlib import Path
import pytest
APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP / 'backend'))
sys.path.insert(0, str(APP / 'migrations'))
from generate_reference import prepared_fixture
from test_owned_migrations import invoke

@pytest.fixture(scope='module')
def controller_database():
    if not os.environ.get('SCRIBESWELL_TEST_DATABASE_URL'):
        pytest.skip('Set SCRIBESWELL_TEST_DATABASE_URL to a disposable local cluster')
    with prepared_fixture() as (admin, url):
        result = invoke(url)
        assert result.returncode == 0, result.stderr
        yield admin, url

def test_controller_ships_empty_and_dormant(controller_database):
    admin, _ = controller_database
    for table in ('corpus_operator_principal', 'corpus_operator_authority', 'corpus_attempt', 'corpus_command_outcome'):
        assert admin.execute('SELECT count(*) FROM scribeswell.' + table).fetchone() == (0,)
    assert admin.execute('SELECT enforcement FROM scribeswell.corpus_fence_control').fetchone() == (False,)

import copy
import hashlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
import json
import time
import uuid
from urllib.parse import unquote, urlsplit
import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb
from corpus_publication import execute_command, lookup_outcome, PublicationError
from test_corpus_publication_input import command, source_bytes, encode
from test_postgres_acceptance import role_url
from test_corpus_writer_fence import BIND, background, importer, wait_blocked, bounded_connection

OPERATOR = 'scribeswell_corpus_operator'
ACTOR = '22222222-2222-4222-8222-222222222222'
TABLES = ('corpus_command_outcome','corpus_attempt','corpus_operator_authority','corpus_operator_principal')
EXECUTE = 'SELECT scribeswell.execute_corpus_command(%s)'
LOOKUP = 'SELECT scribeswell.lookup_corpus_command_outcome(%s)'

@pytest.fixture
def enabled(controller_database):
    admin, url = controller_database
    assert not admin.execute('SELECT FROM pg_roles WHERE rolname=%s', (OPERATOR,)).fetchall(), 'fixture operator must be absent'
    admin.execute('CREATE ROLE scribeswell_corpus_operator LOGIN NOINHERIT NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE NOREPLICATION')
    try:
        admin.execute(sql.SQL('ALTER ROLE scribeswell_corpus_operator PASSWORD {}').format(sql.Literal(unquote(urlsplit(url).password))))
        admin.execute('GRANT USAGE ON SCHEMA scribeswell TO scribeswell_corpus_operator')
        admin.execute('GRANT EXECUTE ON FUNCTION scribeswell.execute_corpus_command(jsonb),scribeswell.lookup_corpus_command_outcome(jsonb) TO scribeswell_corpus_operator')
        admin.execute("""INSERT INTO scribeswell.corpus_operator_principal(database_login,enabled,revision,executor_actor_id,actor_kind,actor_key,preparation_evidence_ref,created_by_actor_id,updated_by_actor_id)
        VALUES(%s,true,1,%s,'service','fixture.controller','fixture:identity',%s,%s)""", (OPERATOR, ACTOR, ACTOR, ACTOR))
        for variant in ('begin','recover','seal'):
            admin.execute("""INSERT INTO scribeswell.corpus_operator_authority(database_login,source_id,command,enabled,revision,created_by_actor_id,updated_by_actor_id)
            VALUES(%s,'tanakh',%s,true,1,%s,%s)""", (OPERATOR,'corpus.'+variant,ACTOR,ACTOR))
        admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=true')
        yield admin, url
    finally:
        admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=false')
        admin.execute('TRUNCATE scribeswell.corpus_epoch,scribeswell.corpus_write_binding,' + ','.join('scribeswell.'+table for table in TABLES))
        admin.execute('REVOKE EXECUTE ON FUNCTION scribeswell.bind_corpus_write(text,bigint,uuid,text) FROM scribeswell_import')
        admin.execute('REVOKE EXECUTE ON FUNCTION scribeswell.execute_corpus_command(jsonb),scribeswell.lookup_corpus_command_outcome(jsonb) FROM scribeswell_corpus_operator')
        admin.execute('REVOKE USAGE ON SCHEMA scribeswell FROM scribeswell_corpus_operator')
        admin.execute('DROP ROLE scribeswell_corpus_operator')


def operator(url):
    return psycopg.connect(role_url(url, OPERATOR), autocommit=True, connect_timeout=5)


def body(variant='begin', previous=None):
    value = command(variant)
    value['operation_id'] = str(uuid.uuid4())
    if previous is not None:
        value['payload']['expected_generation'] = previous.generation
        value['payload']['expected_attempt_id'] = previous.attempt_id
    return value


def execute(connection, value):
    return execute_command(connection, encode(value), source_bytes())


def counts(admin):
    return tuple(admin.execute('SELECT count(*) FROM scribeswell.'+table).fetchone()[0]
                 for table in ('corpus_epoch','corpus_attempt','corpus_command_outcome','corpus_write_binding'))


def test_committed_history_replay_and_attribution(enabled):
    admin, url = enabled
    with operator(url) as connection:
        first = body(); started = execute(connection, first)
        sealed_body = body('seal', started); sealed = execute(connection, sealed_body)
        recovery_body = body('recover', sealed); recovered = execute(connection, recovery_body)
        assert started.generation == '1' and recovered.generation == '2'
        assert recovered.attempt_id != started.attempt_id
        assert sealed.state == 'closed' and recovered.state == 'updating'
        for value, receipt in ((first, started),(sealed_body,sealed),(recovery_body,recovered)):
            assert execute(connection, value) == lookup_outcome(connection, encode(value)) == receipt
        assert counts(admin) == (1,2,3,0)
        assert admin.execute('SELECT generation,state FROM scribeswell.corpus_epoch').fetchone() == (2,'updating')
        assert admin.execute('SELECT state FROM scribeswell.corpus_attempt ORDER BY generation').fetchall() == [('retired',),('updating',)]
        assert admin.execute('SELECT DISTINCT executor_actor_id::text,principal_revision,authority_revision,created_by_actor_id::text,isfinite(created_at) FROM scribeswell.corpus_command_outcome').fetchall() == [(ACTOR,1,1,ACTOR,True)]
        with pytest.raises(FrozenInstanceError):
            started.state = 'closed'
        changed = copy.deepcopy(first); changed['evidence_ref'] = 'changed'
        before=controller_state(admin)
        with pytest.raises(PublicationError, match='corpus_publication.conflict'):
            execute(connection, changed)
        assert controller_state(admin)==before
        assert lookup_outcome(connection, encode(body())) is None


@pytest.mark.parametrize('mutation', ['principal_disabled','authority_disabled','rebound','wrong_source','wrong_command'])
def test_current_authority_gates_historical_receipts(enabled, mutation):
    admin, url = enabled
    with operator(url) as connection:
        value = body(); execute(connection, value)
        expected = 'access_denied'
        if mutation == 'principal_disabled':
            admin.execute('UPDATE scribeswell.corpus_operator_principal SET enabled=false,revision=revision+1')
        elif mutation == 'authority_disabled':
            admin.execute('UPDATE scribeswell.corpus_operator_authority SET enabled=false,revision=revision+1')
        elif mutation == 'rebound':
            admin.execute("UPDATE scribeswell.corpus_operator_principal SET executor_actor_id='33333333-3333-4333-8333-333333333333',revision=revision+1")
            expected = 'conflict'
        elif mutation == 'wrong_source': value['scope']['source_id'] = 'other'
        else:
            value = body('seal'); admin.execute("UPDATE scribeswell.corpus_operator_authority SET enabled=false,revision=revision+1 WHERE command='corpus.seal'")
        before=controller_state(admin)
        with pytest.raises(PublicationError, match='corpus_publication.'+expected):
            lookup_outcome(connection, encode(value))
        assert controller_state(admin)==before
        assert counts(admin) == (1,1,1,0)


@pytest.mark.parametrize('change', ['SUPERUSER','BYPASSRLS','CREATEDB','CREATEROLE','REPLICATION','INHERIT','membership','member_of_operator'])
def test_unsafe_actual_role_denied(enabled, change):
    admin, url = enabled
    if change == 'membership': admin.execute('GRANT scribeswell_import TO scribeswell_corpus_operator')
    elif change == 'member_of_operator': admin.execute('GRANT scribeswell_corpus_operator TO anon')
    else: admin.execute('ALTER ROLE scribeswell_corpus_operator '+change)
    try:
        with operator(url) as connection:
            with pytest.raises(PublicationError, match='access_denied'):
                execute(connection, body())
        assert counts(admin) == (0,0,0,0)
    finally:
        if change == 'membership': admin.execute('REVOKE scribeswell_import FROM scribeswell_corpus_operator')
        elif change == 'member_of_operator': admin.execute('REVOKE scribeswell_corpus_operator FROM anon')
        else: admin.execute('ALTER ROLE scribeswell_corpus_operator NO'+change)


@pytest.mark.parametrize('role', ('anon','authenticated','service_role','scribeswell_runtime','scribeswell_import'))
def test_shipped_roles_have_no_controller_privileges(controller_database, role):
    admin, _ = controller_database
    for table in TABLES:
        assert admin.execute('SELECT has_table_privilege(%s,%s,\'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER\')', (role,'scribeswell.'+table)).fetchone() == (False,)
    for signature in ('execute_corpus_command(jsonb)','lookup_corpus_command_outcome(jsonb)',
                      'validate_corpus_command(jsonb)','corpus_command_internal(jsonb,boolean)',
                      'protect_corpus_controller_record()'):
        assert admin.execute("SELECT has_function_privilege(%s,%s,'EXECUTE')",
                             (role,'scribeswell.'+signature)).fetchone() == (False,)


@pytest.mark.parametrize('mutator', [
    lambda v: {},
    lambda v: dict(v, schema_version=1.0),
    lambda v: dict(v, scope={}),
    lambda v: dict(v, payload={}),
    lambda v: dict(v, payload={'expected_absent':True,'input':{}}),
    lambda v: dict(v, payload={'expected_absent':1,'input':v['payload']['input']}),
    lambda v: dict(v, operation_id='00000000-0000-0000-0000-000000000000'),
    lambda v: dict(v, evidence_ref='unsafe whitespace'),
    lambda v: dict(v, reason_code='source_seal'),
    lambda v: dict(v, actor_id=ACTOR),
    lambda v: dict(v, scope={'kind':'source','source_id':None}),
    lambda v: dict(v, payload={'expected_absent':True,'input':dict(v['payload']['input'],catalogue_version=True)}),
])
def test_native_validation_independent_of_byte_parser(enabled, mutator):
    admin, url = enabled
    before=controller_state(admin)
    with operator(url) as connection:
        with pytest.raises(psycopg.errors.InvalidParameterValue, match='corpus_publication.input_invalid'):
            connection.execute(EXECUTE, (Jsonb(mutator(body())),))
        assert controller_state(admin)==before


@pytest.mark.parametrize('mutation', ['stale','cross_source','seal_identity','existing_begin','sealed_seal'])
def test_conflicts_are_atomic(enabled, mutation):
    admin, url = enabled
    with operator(url) as connection:
        initial = execute(connection, body())
        value = body('seal', initial)
        if mutation == 'stale': value['payload']['expected_generation']='2'
        elif mutation == 'cross_source':
            value['scope']['source_id']='other'
            admin.execute("INSERT INTO scribeswell.corpus_operator_authority SELECT database_login,'other',command,enabled,revision,created_by_actor_id,updated_by_actor_id,created_at,updated_at FROM scribeswell.corpus_operator_authority WHERE command='corpus.seal'")
        elif mutation == 'seal_identity': value['payload']['input']['tokenization_version']='different'
        elif mutation == 'existing_begin': value = body()
        else: execute(connection, value); value = body('seal',initial)
        before = controller_state(admin)
        with pytest.raises(PublicationError, match='conflict'):
            execute(connection, value)
        assert controller_state(admin) == before


@pytest.mark.parametrize('variant', ['begin','recover','seal'])
def test_injected_outcome_fault_rolls_back_all_transitions(enabled, variant):
    admin, url = enabled
    with operator(url) as connection:
        previous=execute(connection,body()) if variant!='begin' else None
    before=controller_state(admin)
    admin.execute("CREATE FUNCTION scribeswell.fixture_fail() RETURNS trigger LANGUAGE plpgsql AS $$BEGIN RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='fixture_fault'; END$$")
    admin.execute('CREATE TRIGGER fixture_fault BEFORE INSERT ON scribeswell.corpus_command_outcome FOR EACH ROW EXECUTE FUNCTION scribeswell.fixture_fail()')
    try:
        with operator(url) as connection:
            value=body(variant,previous)
            with pytest.raises(PublicationError, match='conflict') as caught:
                execute(connection,value)
            assert caught.value.__context__ is None
            assert controller_state(admin) == before
            assert lookup_outcome(connection,encode(value)) is None
    finally:
        admin.execute('DROP TRIGGER fixture_fault ON scribeswell.corpus_command_outcome')
        admin.execute('DROP FUNCTION scribeswell.fixture_fail()')


def test_concurrent_same_operation_and_distinct_begins(enabled):
    admin,url=enabled
    value=body()
    def run(value):
        with operator(url) as connection: return execute(connection,value)
    with ThreadPoolExecutor(max_workers=2) as pool:
        receipts=list(pool.map(run,[value,value]))
    assert receipts[0]==receipts[1] and counts(admin)==(1,1,1,0)
    before=controller_state(admin)
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes=list(pool.map(lambda _: _conflict(run,body()),range(2)))
    assert controller_state(admin)==before
    assert outcomes==['corpus_publication.conflict']*2 and counts(admin)==(1,1,1,0)


def _conflict(fn, value):
    try: return fn(value)
    except PublicationError as error: return error.code


@pytest.mark.parametrize('variant', ['recover','seal'])
@pytest.mark.parametrize('first', ['writer','transition'])
def test_writer_transition_ordering_and_stale_exclusion(enabled, variant, first):
    admin,url=enabled
    admin.execute('GRANT EXECUTE ON FUNCTION scribeswell.bind_corpus_write(text,bigint,uuid,text) TO scribeswell_import')
    with operator(url) as connection, importer(url) as writer:
        old=execute(connection,body()); value=body(variant,old)
        old_tuple=('tanakh',int(old.generation),old.attempt_id,value['payload']['input']['source_sha256'])
        if first=='writer':
            with writer.transaction():
                writer.execute(BIND,old_tuple)
                writer.execute('UPDATE scribeswell.book SET id=id WHERE false')
                with background(connection,lambda:execute(connection,value)) as future:
                    wait_blocked(admin,connection.info.backend_pid,writer.info.backend_pid)
                    assert not future.done()
                    writer.execute('COMMIT')
                    new=future.result(timeout=3)
        else:
            with connection.transaction():
                connection.execute(EXECUTE,(Jsonb(value),))
                with background(writer,lambda:writer.execute(BIND,old_tuple)) as future:
                    wait_blocked(admin,writer.info.backend_pid,connection.info.backend_pid)
                    assert not future.done()
                    connection.execute('COMMIT')
                    with pytest.raises(psycopg.errors.InsufficientPrivilege): future.result(timeout=3)
            new=lookup_outcome(connection,encode(value))
        with pytest.raises(psycopg.errors.InsufficientPrivilege): writer.execute(BIND,old_tuple)
        if variant=='recover':
            with writer.transaction():
                writer.execute(BIND,('tanakh',int(new.generation),new.attempt_id,old_tuple[3]))
                writer.execute('UPDATE scribeswell.book SET id=id WHERE false')
        assert counts(admin)==(1,2 if variant=='recover' else 1,2,0)


def test_authority_revocation_waits_for_current_operation(enabled):
    admin,url=enabled
    with operator(url) as connection, bounded_connection(url,'scribeswell_migrator') as owner:
        value=body()
        with connection.transaction():
            connection.execute(EXECUTE,(Jsonb(value),))
            with background(owner,lambda:owner.execute("UPDATE scribeswell.corpus_operator_authority SET enabled=false,revision=revision+1 WHERE command='corpus.begin'")) as future:
                wait_blocked(admin,owner.info.backend_pid,connection.info.backend_pid)
                assert not future.done()
                connection.execute('COMMIT'); future.result(timeout=3)
        with pytest.raises(PublicationError,match='access_denied'): lookup_outcome(connection,encode(value))


def test_nonidle_and_isolation_rejected_before_source_work(enabled):
    _,url=enabled
    with operator(url) as connection:
        with connection.transaction():
            with pytest.raises(PublicationError,match='unavailable'): execute_command(connection,b'invalid',b'invalid')
        connection.isolation_level=psycopg.IsolationLevel.SERIALIZABLE
        with pytest.raises(PublicationError,match='unavailable'): execute_command(connection,b'invalid',b'invalid')
        connection.isolation_level=None
        with pytest.raises(ValueError,match='input_invalid'): execute_command(connection,b'invalid',b'invalid')
        value=body()
        with pytest.raises(ValueError,match='source_evidence'): execute_command(connection,encode(value),b'invalid')
        with connection.transaction():
            connection.execute('SET TRANSACTION ISOLATION LEVEL SERIALIZABLE')
            with pytest.raises(psycopg.errors.ObjectNotInPrerequisiteState,match='unavailable'):
                connection.execute(EXECUTE,(Jsonb(value),))


def test_missing_mapping_disabled_fence_and_forged_session(enabled):
    admin,url=enabled
    value=body()
    # SET ROLE and a copied GUC cannot forge the original authenticated session.
    with admin.transaction():
        admin.execute('SET LOCAL ROLE scribeswell_corpus_operator')
        admin.execute("SELECT set_config('scribeswell.executor_actor_id',%s,true)",(ACTOR,))
        with pytest.raises(psycopg.errors.InsufficientPrivilege,match='access_denied'):
            admin.execute(EXECUTE,(Jsonb(value),))
    with operator(url) as connection:
        admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=false')
        with pytest.raises(PublicationError,match='unavailable'): execute(connection,value)
        admin.execute('TRUNCATE scribeswell.corpus_operator_authority,scribeswell.corpus_operator_principal CASCADE')
        with pytest.raises(PublicationError,match='access_denied'): execute(connection,value)
    assert counts(admin)==(0,0,0,0)


def test_live_login_revocation_and_direct_authority_lock_deadline(enabled):
    admin,url=enabled
    with operator(url) as connection:
        admin.execute('ALTER ROLE scribeswell_corpus_operator NOLOGIN')
        with pytest.raises(PublicationError,match='access_denied'): execute(connection,body())
        admin.execute('ALTER ROLE scribeswell_corpus_operator LOGIN')
        with admin.transaction():
            admin.execute('UPDATE scribeswell.corpus_operator_principal SET revision=revision+1')
            started=time.monotonic()
            with pytest.raises(psycopg.errors.LockNotAvailable):
                connection.execute(EXECUTE,(Jsonb(body()),))
            assert 1.5 <= time.monotonic()-started < 4
    assert counts(admin)==(0,0,0,0)


@pytest.mark.parametrize('variant', ['begin','recover','seal'])
def test_transaction_rollback_keeps_previous_state(enabled, variant):
    admin,url=enabled
    with operator(url) as connection:
        old=execute(connection,body()) if variant!='begin' else None
        value=body(variant,old)
        before=controller_state(admin)
        with connection.transaction():
            connection.execute(EXECUTE,(Jsonb(value),))
            connection.execute('ROLLBACK')
        assert controller_state(admin)==before
        assert lookup_outcome(connection,encode(value)) is None
        if old:
            assert admin.execute('SELECT generation,attempt_id::text,state FROM scribeswell.corpus_epoch').fetchone()==(1,old.attempt_id,'updating')


def test_overflow_rejects_without_partial_mutation(enabled):
    admin,url=enabled
    # A fixture-only seeded historical high generation reaches the native overflow guard.
    high=9223372036854775807; attempt=str(uuid.uuid4()); value=body('recover')
    identity=value['payload']['input']
    admin.execute("INSERT INTO scribeswell.corpus_attempt(attempt_id,source_id,generation,input_sha256,catalogue_version,versification_id,tokenization_version,state,created_by_actor_id,updated_by_actor_id) VALUES(%s,'tanakh',%s,%s,%s,%s,%s,'updating',%s,%s)",
                  (attempt,high,identity['source_sha256'],identity['catalogue_version'],identity['versification_id'],identity['tokenization_version'],ACTOR,ACTOR))
    admin.execute("INSERT INTO scribeswell.corpus_epoch(source_id,generation,attempt_id,input_sha256,state,created_by_actor_id,updated_by_actor_id) VALUES('tanakh',%s,%s,%s,'updating',%s,%s)",(high,attempt,identity['source_sha256'],ACTOR,ACTOR))
    value['payload'].update(expected_generation=str(high),expected_attempt_id=attempt)
    before=controller_state(admin)
    with operator(url) as connection:
        with pytest.raises(PublicationError,match='conflict'): execute(connection,value)
    assert controller_state(admin)==before
    assert counts(admin)==(1,1,0,0)
    assert admin.execute('SELECT state FROM scribeswell.corpus_attempt').fetchone()==('updating',)


def test_commit_response_loss_reconciles_actual_durable_outcome(enabled,monkeypatch):
    from psycopg.transaction import Transaction
    admin,url=enabled
    original=Transaction.__exit__
    with operator(url) as connection:
        value=body()
        def lost(self,*args):
            original(self,*args)
            raise psycopg.OperationalError('simulated sensitive transport details')
        with monkeypatch.context() as scoped:
            scoped.setattr(Transaction,'__exit__',lost)
            with pytest.raises(PublicationError,match='unknown_outcome') as caught:
                execute(connection,value)
        assert caught.value.__context__ is None
        assert counts(admin)==(1,1,1,0)
        receipt=lookup_outcome(connection,encode(value))
        assert receipt==execute(connection,value)
        assert counts(admin)==(1,1,1,0)


@pytest.mark.parametrize('variant', ['begin','recover','seal'])
@pytest.mark.parametrize('field,replacement', [
    ('operation_id','33333333-3333-4333-8333-333333333333'), ('source_id','other'),
    ('executor_actor_id','invalid'), ('executor_actor_id','00000000-0000-0000-0000-000000000000'),
    ('attempt_id','invalid'), ('attempt_id','00000000-0000-0000-0000-000000000000'),
    ('generation','0'), ('generation','9223372036854775808'), ('generation','7'),
    ('state','retired'), ('version',True),
])
def test_invalid_response_rolls_back_without_receipt(enabled,monkeypatch,variant,field,replacement):
    import corpus_publication
    admin,url=enabled
    original=corpus_publication._receipt
    def invalid(value,parsed):
        changed=dict(value); changed[field]=replacement
        return original(changed,parsed)
    with operator(url) as connection:
        previous=execute(connection,body()) if variant!='begin' else None
        value=body(variant,previous); before=controller_state(admin)
        with monkeypatch.context() as scoped:
            scoped.setattr(corpus_publication,'_receipt',invalid)
            with pytest.raises(PublicationError,match='unknown_outcome'): execute(connection,value)
        assert controller_state(admin)==before
        assert lookup_outcome(connection,encode(value)) is None


@pytest.mark.parametrize('table', TABLES)
def test_operator_direct_table_access_denied(enabled,table):
    _,url=enabled
    with operator(url) as connection:
        for statement in ('SELECT * FROM ', 'DELETE FROM ', 'TRUNCATE '):
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                connection.execute(statement+'scribeswell.'+table)
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            connection.execute('SET ROLE scribeswell_migrator')


def test_outcome_and_approved_input_are_immutable(enabled):
    admin,url=enabled
    with operator(url) as connection: execute(connection,body())
    for statement in ("UPDATE scribeswell.corpus_command_outcome SET result='{}'",'DELETE FROM scribeswell.corpus_command_outcome',
                      "UPDATE scribeswell.corpus_attempt SET input_sha256='"+'b'*64+"'",
                      "UPDATE scribeswell.corpus_operator_principal SET actor_key='different',revision=revision+1"):
        before=controller_state(admin)
        with pytest.raises(psycopg.errors.RaiseException,match='conflict'): admin.execute(statement)
        assert controller_state(admin)==before
    assert counts(admin)==(1,1,1,0)


def test_distinct_initial_begins_serialize_absent_epoch(enabled):
    admin,url=enabled
    with operator(url) as first, operator(url) as second:
        one,two=body(),body()
        with first.transaction():
            first.execute(EXECUTE,(Jsonb(one),))
            with background(second,lambda:execute(second,two)) as future:
                wait_blocked(admin,second.info.backend_pid,first.info.backend_pid)
                assert counts(admin)==(0,0,0,0)
                first.execute('COMMIT')
                with pytest.raises(PublicationError,match='conflict'): future.result(timeout=3)
        assert lookup_outcome(first,encode(one)) is not None
        assert lookup_outcome(second,encode(two)) is None
    assert counts(admin)==(1,1,1,0)


def test_lookup_waits_for_inflight_command_and_revocation(enabled):
    admin,url=enabled
    with operator(url) as first, operator(url) as second, bounded_connection(url,'scribeswell_migrator') as owner:
        value=body()
        with first.transaction():
            returned=first.execute(EXECUTE,(Jsonb(value),)).fetchone()[0]
            with background(second,lambda:lookup_outcome(second,encode(value))) as future:
                wait_blocked(admin,second.info.backend_pid,first.info.backend_pid)
                first.execute('COMMIT')
                assert future.result(timeout=3).attempt_id==returned['attempt_id']
        # A direct lookup keeps current-authority shares to its commit boundary.
        with first.transaction():
            first.execute(LOOKUP,(Jsonb(value),))
            with background(owner,lambda:owner.execute('UPDATE scribeswell.corpus_operator_principal SET enabled=false,revision=revision+1')) as future:
                wait_blocked(admin,owner.info.backend_pid,first.info.backend_pid)
                first.execute('COMMIT'); future.result(timeout=3)
        with pytest.raises(PublicationError,match='access_denied'): lookup_outcome(second,encode(value))


def controller_state(admin):
    """Complete protected state, including immutable attribution and stored receipts."""
    return {table:admin.execute('SELECT to_jsonb(t) FROM scribeswell.'+table+
                               ' t ORDER BY to_jsonb(t)::text').fetchall()
            for table in TABLES+('corpus_epoch','corpus_write_binding','corpus_fence_control')}


@pytest.mark.parametrize('variant', ['recover','seal'])
@pytest.mark.parametrize('field,value', [
    ('expected_attempt_id','INVALID'), ('expected_attempt_id','00000000-0000-0000-0000-000000000000'),
    ('expected_generation','0'), ('expected_generation','01'), ('expected_generation',1),
    ('expected_generation','9223372036854775808'), ('expected_generation','9'*40),
    ('extra','unexpected'), ('input',{}),
    ('input',dict(command()['payload']['input'],source_sha256='INVALID')),
    ('input',dict(command()['payload']['input'],catalogue_version=False)),
    ('input',dict(command()['payload']['input'],extra='unexpected')),
])
def test_native_recover_seal_validation_preserves_full_state(enabled,variant,field,value):
    admin,url=enabled
    with operator(url) as connection:
        previous=execute(connection,body()); request=body(variant,previous)
        request['payload'][field]=value; before=controller_state(admin)
        with pytest.raises(psycopg.errors.InvalidParameterValue,match='input_invalid'):
            connection.execute(EXECUTE,(Jsonb(request),))
        assert controller_state(admin)==before


def test_native_size_limit_preserves_full_state(enabled):
    admin,url=enabled
    request=body(); request['evidence_ref']='x'*65537
    before=controller_state(admin)
    with operator(url) as connection:
        with pytest.raises(psycopg.errors.InvalidParameterValue,match='input_invalid'):
            connection.execute(EXECUTE,(Jsonb(request),))
    assert controller_state(admin)==before


def alternate_source():
    return source_bytes().replace('שָׁ/אָב'.encode(), 'שָׁ/בֵּן'.encode())


@pytest.mark.parametrize('field',['source_sha256','catalogue_version','versification_id','tokenization_version'])
def test_each_seal_input_mismatch_reaches_sql_and_preserves_state(enabled,field):
    admin,url=enabled
    with operator(url) as connection:
        previous=execute(connection,body()); request=body('seal',previous)
        raw=source_bytes()
        if field=='source_sha256':
            raw=alternate_source()
            request['payload']['input'][field]=hashlib.sha256(raw).hexdigest()
        else: request['payload']['input'][field]='different-v2'
        before=controller_state(admin)
        with pytest.raises(PublicationError,match='conflict'):
            execute_command(connection,encode(request),raw)
        assert controller_state(admin)==before


@pytest.mark.parametrize('first_variant,second_variant',[
    ('recover','recover'), ('recover','seal'), ('seal','recover'),
])
def test_competing_transitions_serialize_current_tuple(enabled,first_variant,second_variant):
    admin,url=enabled
    with operator(url) as first, operator(url) as second:
        previous=execute(first,body())
        one,two=body(first_variant,previous),body(second_variant,previous)
        with first.transaction():
            first.execute(EXECUTE,(Jsonb(one),))
            with background(second,lambda:execute(second,two)) as future:
                wait_blocked(admin,second.info.backend_pid,first.info.backend_pid)
                first.execute('COMMIT')
                committed=controller_state(admin)
                if first_variant=='seal':
                    result=future.result(timeout=3)
                    assert result.generation=='2' and result.state=='updating'
                else:
                    with pytest.raises(PublicationError,match='conflict'): future.result(timeout=3)
                    assert controller_state(admin)==committed
        assert lookup_outcome(first,encode(one)) is not None
        assert (lookup_outcome(second,encode(two)) is not None)==(first_variant=='seal')
        assert counts(admin)==(1,2,3 if first_variant=='seal' else 2,0)


@pytest.mark.parametrize('table',['corpus_operator_principal','corpus_operator_authority'])
@pytest.mark.parametrize('action',['execute','lookup'])
def test_revocation_first_waits_then_denies_without_receipt(enabled,table,action):
    admin,url=enabled
    with operator(url) as connection, bounded_connection(url,'scribeswell_migrator') as owner:
        historical=body(); execute(connection,historical)
        request=historical if action=='lookup' else body('recover',lookup_outcome(connection,encode(historical)))
        before=controller_state(admin)
        def run():
            return lookup_outcome(connection,encode(request)) if action=='lookup' else execute(connection,request)
        with owner.transaction():
            owner.execute('UPDATE scribeswell.'+table+' SET enabled=false,revision=revision+1')
            with background(connection,run) as future:
                wait_blocked(admin,connection.info.backend_pid,owner.info.backend_pid)
                owner.execute('COMMIT')
                after_revocation=controller_state(admin)
                with pytest.raises(PublicationError,match='access_denied'): future.result(timeout=3)
        assert controller_state(admin)==after_revocation
        for record in ('corpus_epoch','corpus_attempt','corpus_command_outcome','corpus_write_binding'):
            assert after_revocation[record]==before[record]


def test_record_protection_preserves_creation_revision_keys_and_terminal_history(enabled):
    admin,url=enabled
    with operator(url) as connection:
        previous=execute(connection,body())
        execute(connection,body('seal',previous))
        closed_attempt=previous.attempt_id
        execute(connection,body('recover',previous))
    statements=[
        "UPDATE scribeswell.corpus_operator_principal SET created_by_actor_id='33333333-3333-4333-8333-333333333333',revision=revision+1",
        "UPDATE scribeswell.corpus_operator_principal SET created_at=created_at-interval '1 second',revision=revision+1",
        'UPDATE scribeswell.corpus_operator_principal SET revision=revision-1',
        'UPDATE scribeswell.corpus_operator_authority SET revision=revision-1',
        "UPDATE scribeswell.corpus_operator_authority SET source_id='changed',revision=revision+1",
        "UPDATE scribeswell.corpus_operator_authority SET database_login='different',revision=revision+1",
        "UPDATE scribeswell.corpus_operator_authority SET created_by_actor_id='33333333-3333-4333-8333-333333333333',revision=revision+1",
        "UPDATE scribeswell.corpus_operator_authority SET command='corpus.seal',revision=revision+1 WHERE command='corpus.begin'",
        "UPDATE scribeswell.corpus_operator_authority SET created_at=created_at-interval '1 second',revision=revision+1",
        "UPDATE scribeswell.corpus_attempt SET created_by_actor_id='33333333-3333-4333-8333-333333333333'",
        "UPDATE scribeswell.corpus_attempt SET created_at=created_at-interval '1 second'",
        "UPDATE scribeswell.corpus_attempt SET state='updating' WHERE attempt_id='"+closed_attempt+"'",
        "UPDATE scribeswell.corpus_attempt SET state='closed' WHERE attempt_id='"+closed_attempt+"'",
        'DELETE FROM scribeswell.corpus_attempt',
    ]
    for statement in statements:
        before=controller_state(admin)
        with pytest.raises(psycopg.errors.RaiseException,match='conflict'): admin.execute(statement)
        assert controller_state(admin)==before
    # Independently prove a closed predecessor cannot be reopened by direct update.
    with operator(url) as connection:
        epoch=admin.execute('SELECT attempt_id::text,generation::text FROM scribeswell.corpus_epoch').fetchone()
        request=body('seal'); request['payload'].update(expected_attempt_id=epoch[0],expected_generation=epoch[1])
        execute(connection,request)
    before=controller_state(admin)
    with pytest.raises(psycopg.errors.RaiseException,match='conflict'):
        admin.execute("UPDATE scribeswell.corpus_attempt SET state='updating' WHERE state='closed'")
    assert controller_state(admin)==before


def test_recovery_replaces_approved_identity_and_only_new_checksum_binds(enabled):
    admin,url=enabled
    admin.execute('GRANT EXECUTE ON FUNCTION scribeswell.bind_corpus_write(text,bigint,uuid,text) TO scribeswell_import')
    with operator(url) as connection, importer(url) as writer:
        initial_request=body(); initial=execute(connection,initial_request)
        request=body('recover',initial); raw=alternate_source()
        identity=dict(source_sha256=hashlib.sha256(raw).hexdigest(),catalogue_version='catalogue-v2',
                      versification_id='versification-v2',tokenization_version='tokens-v2')
        request['payload']['input']=identity
        recovered=execute_command(connection,encode(request),raw)
        rows=admin.execute('SELECT input_sha256,catalogue_version,versification_id,tokenization_version,state FROM scribeswell.corpus_attempt ORDER BY generation').fetchall()
        old=initial_request['payload']['input']
        assert rows==[(old['source_sha256'],old['catalogue_version'],old['versification_id'],old['tokenization_version'],'retired'),
                      (identity['source_sha256'],'catalogue-v2','versification-v2','tokens-v2','updating')]
        assert admin.execute('SELECT input_sha256,attempt_id::text,generation FROM scribeswell.corpus_epoch').fetchone()==(identity['source_sha256'],recovered.attempt_id,2)
        for checksum in (old['source_sha256'],identity['source_sha256']):
            with writer.transaction():
                if checksum==old['source_sha256']:
                    with pytest.raises(psycopg.errors.InsufficientPrivilege):
                        writer.execute(BIND,('tanakh',2,recovered.attempt_id,checksum))
                else:
                    writer.execute(BIND,('tanakh',2,recovered.attempt_id,checksum))
                    writer.execute('UPDATE scribeswell.book SET id=id WHERE false')
        assert admin.execute('SELECT count(*) FROM scribeswell.corpus_write_binding').fetchone()==(0,)


@pytest.mark.parametrize('response', [None, {}, {'version': True}, {'generation': '0'}])
def test_incomplete_response_rolls_back_without_receipt(enabled, monkeypatch, response):
    import corpus_publication
    admin, url = enabled
    original = corpus_publication._receipt

    def invalid(value, parsed):
        return original(response, parsed)

    with operator(url) as connection:
        request = body()
        before = controller_state(admin)
        with monkeypatch.context() as scoped:
            scoped.setattr(corpus_publication, '_receipt', invalid)
            with pytest.raises(PublicationError, match='unknown_outcome'):
                execute(connection, request)
        assert controller_state(admin) == before
        assert lookup_outcome(connection, encode(request)) is None
