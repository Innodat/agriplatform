"""Synthetic handoff; actual PostgreSQL sessions and mapping transaction effects."""
from urllib.parse import unquote, urlsplit

import pytest
from psycopg import sql
from sqlalchemy import create_engine, pool

from test_corpus_publication import controller_database, OPERATOR
from test_owned_migrations import migration_url, business_state
from test_prepared_controller_profile import CUSTODY, native
from caller_preparation_rehearsal import stage_initial

from concurrent.futures import ThreadPoolExecutor
import time
import psycopg
from sqlalchemy import event
from sqlalchemy.exc import DBAPIError
from caller_preparation_rehearsal import locked_state, reconcile
from test_corpus_publication import operator, body, execute
from corpus_publication import lookup_outcome
from test_corpus_publication_input import encode
from corpus_publication import PublicationError


# Fixture-owned assertion only. No Identity registration/verification is performed.
PREPARER = '44444444-4444-4444-8444-444444444444'


@pytest.fixture
def rehearsal(controller_database):
    admin, url = controller_database
    admin.execute('CREATE ROLE scribeswell_corpus_operator LOGIN NOINHERIT NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE NOREPLICATION')
    try:
        admin.execute(sql.SQL('ALTER ROLE scribeswell_corpus_operator PASSWORD {}').format(sql.Literal(unquote(urlsplit(url).password))))
        # Owner grants are separate from the four-row mapping transaction.
        with admin.transaction():
            admin.execute('SET LOCAL ROLE scribeswell_migrator')
            admin.execute('GRANT USAGE ON SCHEMA scribeswell TO scribeswell_corpus_operator')
            admin.execute('GRANT EXECUTE ON FUNCTION scribeswell.execute_corpus_command(jsonb),scribeswell.lookup_corpus_command_outcome(jsonb) TO scribeswell_corpus_operator')
        engine = create_engine(migration_url(url).replace('postgresql://', 'postgresql+psycopg://'), poolclass=pool.NullPool, connect_args={'connect_timeout': 3})
        try:
            yield admin, url, engine
        finally:
            engine.dispose()
    finally:
        admin.execute('TRUNCATE scribeswell.corpus_command_outcome,scribeswell.corpus_operator_authority,scribeswell.corpus_operator_principal')
        admin.execute('REVOKE EXECUTE ON FUNCTION scribeswell.execute_corpus_command(jsonb),scribeswell.lookup_corpus_command_outcome(jsonb) FROM scribeswell_corpus_operator')
        admin.execute('REVOKE USAGE ON SCHEMA scribeswell FROM scribeswell_corpus_operator')
        admin.execute('DROP ROLE scribeswell_corpus_operator')


def test_initial_mapping_commits_disabled_and_native_replay_preserves(rehearsal, monkeypatch):
    admin, url, engine = rehearsal
    admin.execute("INSERT INTO scribeswell.book VALUES (1,'Gen','Genesis','א','old','torah',1)")
    before = business_state(admin)
    with engine.begin() as connection:
        assert stage_initial(connection, CUSTODY, PREPARER) == 'created'
    principal = admin.execute('SELECT enabled,revision,executor_actor_id::text,created_by_actor_id::text,updated_by_actor_id::text,created_at=updated_at FROM scribeswell.corpus_operator_principal').fetchall()
    assert principal == [(False, 1, CUSTODY['executor_actor_id'], PREPARER, PREPARER, True)]
    assert admin.execute('SELECT command,enabled,revision,created_by_actor_id::text,updated_by_actor_id::text FROM scribeswell.corpus_operator_authority ORDER BY command').fetchall() == [
        ('corpus.'+variant, False, 1, PREPARER, PREPARER) for variant in ('begin', 'recover', 'seal')]
    mappings_before_replay = snapshot(engine)
    config = native(url, monkeypatch, {'scribeswell_validation_profile': 'prepared-controller-v1', 'scribeswell_prepared_actor': CUSTODY})
    assert config.attributes['scribeswell_validated_profile'] == 'prepared-controller-v1'
    assert business_state(admin) == before
    assert snapshot(engine) == mappings_before_replay
    assert admin.execute('SELECT enforcement FROM scribeswell.corpus_fence_control').fetchone() == (False,)
    for table in ('corpus_epoch','corpus_attempt','corpus_command_outcome','corpus_write_binding'):
        assert admin.execute('SELECT count(*) FROM scribeswell.'+table).fetchone() == (0,)



def snapshot(engine):
    with engine.begin() as connection:
        return locked_state(connection)


def test_exact_reuse_is_noop_and_records_actual_synthetic_session(rehearsal):
    admin, url, engine = rehearsal
    with engine.begin() as connection:
        observed = connection.exec_driver_sql('SELECT session_user,current_user,current_database(),pg_backend_pid()').one()
        run_record = {'actor': PREPARER, 'run': 'fixture:caller-rehearsal', 'observed': tuple(observed)}
        assert stage_initial(connection, CUSTODY, PREPARER) == 'created'
    assert run_record['observed'][:3] == ('scribeswell_migrator','scribeswell_migrator',urlsplit(url).path[1:])
    assert run_record['actor'] != CUSTODY['executor_actor_id']
    before = snapshot(engine)
    with engine.begin() as connection:
        assert stage_initial(connection, CUSTODY, PREPARER) == 'unchanged'
    assert snapshot(engine) == before  # includes every timestamp/attribution/revision
    with operator(url) as connection:
        for query in ('SELECT * FROM scribeswell.corpus_operator_principal',
                      'SELECT * FROM scribeswell.corpus_operator_authority',
                      'SET ROLE scribeswell_migrator',
                      "UPDATE scribeswell.book SET name_en='forbidden' WHERE false"):
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                connection.execute(query)
        for variant in ('begin', 'recover', 'seal'):
            request = body(variant)
            for action in (lambda: execute(connection, request),
                           lambda: lookup_outcome(connection, encode(request))):
                with pytest.raises(PublicationError, match='access_denied'):
                    action()


@pytest.mark.parametrize('insertion', [1, 2, 3, 4])
def test_failed_insert_rolls_back_whole_bundle(rehearsal, insertion):
    admin, _, engine = rehearsal
    before = snapshot(engine)
    writes = []
    def fail(connection, cursor, statement, parameters, context, executemany):
        if statement.startswith('INSERT INTO scribeswell.corpus_operator_'):
            writes.append(statement)
            if len(writes) == insertion:
                # Fail in PostgreSQL after the preceding inserts have run.
                cursor.execute('SELECT 1/0')
    event.listen(engine, 'before_cursor_execute', fail)
    try:
        # Direct callback cursor execution bypasses SQLAlchemy's DBAPI wrapper.
        with pytest.raises(psycopg.errors.DivisionByZero) as failure:
            with engine.begin() as connection:
                stage_initial(connection, CUSTODY, PREPARER)
        assert failure.value.sqlstate == '22012'
    finally:
        event.remove(engine, 'before_cursor_execute', fail)
    assert len(writes) == insertion
    assert snapshot(engine) == before
    assert admin.execute('SELECT rolcanlogin FROM pg_roles WHERE rolname=%s', (OPERATOR,)).fetchone() == (True,)
    assert admin.execute("SELECT has_schema_privilege(%s,'scribeswell','USAGE')", (OPERATOR,)).fetchone() == (True,)


def test_failed_postcheck_rolls_back(rehearsal, monkeypatch):
    _, _, engine = rehearsal
    import caller_preparation_rehearsal as protocol
    original = protocol.matches_initial
    with monkeypatch.context() as patch:
        patch.setattr(protocol, 'matches_initial', lambda *args: False)
        with pytest.raises(ValueError, match='postcheck_failed'):
            with engine.begin() as connection:
                protocol.stage_initial(connection, CUSTODY, PREPARER)
    assert snapshot(engine) == ((), ())
    assert protocol.matches_initial is original


@pytest.mark.parametrize('change', ['partial', 'extra', 'wrong_actor', 'enabled', 'revision'])
def test_unexpected_before_state_refused_without_repair(rehearsal, change):
    admin, _, engine = rehearsal
    with engine.begin() as connection:
        stage_initial(connection, CUSTODY, PREPARER)
    # Owner-only fixture corruption, not production recovery instructions.
    if change == 'partial':
        admin.execute('TRUNCATE scribeswell.corpus_operator_authority')
    elif change == 'extra':
        admin.execute("INSERT INTO scribeswell.corpus_operator_authority(database_login,source_id,command,enabled,revision,created_by_actor_id,updated_by_actor_id) VALUES(%s,'other','corpus.begin',false,1,%s,%s)", (OPERATOR,PREPARER,PREPARER))
    elif change == 'wrong_actor':
        admin.execute('UPDATE scribeswell.corpus_operator_principal SET executor_actor_id=%s,revision=revision+1', (PREPARER,))
    elif change == 'enabled':
        admin.execute('UPDATE scribeswell.corpus_operator_authority SET enabled=true,revision=revision+1')
    else:
        admin.execute('UPDATE scribeswell.corpus_operator_authority SET revision=revision+1')
    before = snapshot(engine)
    with pytest.raises(ValueError, match='preparation_conflict'):
        with engine.begin() as connection:
            stage_initial(connection, CUSTODY, PREPARER)
    assert snapshot(engine) == before


def wait_for_block(admin, pid):
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        row = admin.execute('SELECT pg_blocking_pids(%s)', (pid,)).fetchone()
        if row[0]:
            return row[0]
        time.sleep(.005)
    pytest.fail('second actual backend never observed blocked')


@pytest.mark.parametrize('conflicting', [False, True])
def test_concurrent_preparers_serialize_before_observation(rehearsal, conflicting):
    admin, _, engine = rehearsal
    from threading import Event
    ready = Event()
    pids = []
    def second():
        with engine.begin() as connection:
            pids.append(connection.exec_driver_sql('SELECT pg_backend_pid()').scalar())
            ready.set()
            return stage_initial(connection, CUSTODY | ({'actor_key':'fixture.other'} if conflicting else {}), PREPARER)
    with ThreadPoolExecutor(max_workers=1) as workers:
        with engine.begin() as first:
            first_pid = first.exec_driver_sql('SELECT pg_backend_pid()').scalar()
            assert stage_initial(first, CUSTODY, PREPARER) == 'created'
            future = workers.submit(second)
            assert ready.wait(2)
            assert wait_for_block(admin, pids[0]) == [first_pid]
            assert not future.done()
        if conflicting:
            with pytest.raises(ValueError, match='preparation_conflict'):
                future.result(timeout=3)
        else:
            assert future.result(timeout=3) == 'unchanged'
    state = snapshot(engine)
    assert len(state[0]) == 1 and len(state[1]) == 3
    assert all(row[4] == 1 for row in state[1])


@pytest.mark.parametrize('lock', ['advisory', 'principal', 'authority'])
def test_mapping_lock_timeout_is_bounded_and_no_writes(rehearsal, lock):
    admin, _, engine = rehearsal
    before = snapshot(engine)
    with admin.transaction():
        if lock == 'advisory':
            admin.execute("SELECT pg_advisory_xact_lock(hashtext('scribeswell-owned-migrations'))")
        else:
            admin.execute('LOCK TABLE scribeswell.corpus_operator_'+lock+' IN SHARE ROW EXCLUSIVE MODE')
        start = time.monotonic()
        with pytest.raises(DBAPIError) as failure:
            with engine.begin() as connection:
                stage_initial(connection, CUSTODY, PREPARER)
        assert failure.value.orig.sqlstate == '55P03'
        assert time.monotonic() - start < 3
    assert snapshot(engine) == before


@pytest.mark.parametrize('outcome', ['commit', 'rollback', 'active', 'conflict', 'partial', 'extra'])
def test_lost_acknowledgement_requires_ended_session_and_exact_observation(rehearsal, outcome):
    admin, _, engine = rehearsal
    before = snapshot(engine)
    original = engine.connect()
    transaction = original.begin()
    try:
        observation = tuple(original.exec_driver_sql('SELECT pg_backend_pid(),session_user,current_user,current_database()').one())
        pid = observation[0]
        attempt_record = {'run': 'fixture:lost-ack-'+outcome, 'actor': PREPARER,
                          'session': observation, 'preparation_ref': CUSTODY['preparation_evidence_ref'],
                          'before': before}
        assert observation[1:] == ('scribeswell_migrator', 'scribeswell_migrator', urlsplit(engine.url.render_as_string()).path[1:])
        stage_initial(original, CUSTODY, PREPARER)
        intended = locked_state(original)
        attempt_record['intended'] = intended
        if outcome == 'active':
            with engine.begin() as observer:
                assert reconcile(observer, before, intended, original_pid=pid) == 'unknown'
            assert admin.execute('SELECT count(*) FROM scribeswell.corpus_operator_principal').fetchone() == (0,)
            return
        if outcome == 'rollback':
            transaction.rollback()
        else:
            # Real driver COMMIT succeeds; deliberately lose only its acknowledgement.
            with pytest.raises(ConnectionError, match='injected_lost_ack'):
                transaction.commit()
                raise ConnectionError('injected_lost_ack')
        original.close()  # NullPool: backend must end before reconciliation.
        # Client close is asynchronous; require observed server termination.
        deadline = time.monotonic()+2
        while admin.execute('SELECT 1 FROM pg_stat_activity WHERE pid=%s', (pid,)).fetchone() is not None:
            if time.monotonic() >= deadline:
                with engine.begin() as observer:
                    assert reconcile(observer, before, intended, original_pid=pid) == 'unknown'
                pytest.fail('original backend termination unverified; no reconciliation writes permitted')
            time.sleep(.005)
        if outcome == 'conflict':
            admin.execute('UPDATE scribeswell.corpus_operator_authority SET revision=revision+1')
        elif outcome == 'partial':
            # Build partial owner state only inside the disposable fixture.
            admin.execute('TRUNCATE scribeswell.corpus_operator_authority')
        elif outcome == 'extra':
            admin.execute("INSERT INTO scribeswell.corpus_operator_authority(database_login,source_id,command,enabled,revision,created_by_actor_id,updated_by_actor_id) VALUES(%s,'other','corpus.begin',false,1,%s,%s)", (OPERATOR,PREPARER,PREPARER))
        actual_before_reconciliation = snapshot(engine)
        with engine.begin() as observer:
            result = reconcile(observer, attempt_record['before'], attempt_record['intended'], original_pid=attempt_record['session'][0])
        assert result == {'commit':'committed','rollback':'unchanged-before','conflict':'conflict','partial':'conflict','extra':'conflict'}[outcome]
        assert snapshot(engine) == actual_before_reconciliation  # never retry/repair
    finally:
        if transaction.is_active:
            transaction.rollback()
        original.close()


@pytest.mark.parametrize('setting', ['isolation', 'readonly', 'autocommit'])
def test_unsupported_transaction_shape_refused(rehearsal, setting):
    _, _, engine = rehearsal
    with engine.connect() as connection:
        if setting == 'isolation':
            connection = connection.execution_options(isolation_level='SERIALIZABLE')
        elif setting == 'autocommit':
            with pytest.raises(ValueError, match='transaction_required'):
                stage_initial(connection, CUSTODY, PREPARER)
            return
        with connection.begin():
            if setting == 'readonly':
                connection.exec_driver_sql('SET TRANSACTION READ ONLY')
            with pytest.raises(ValueError, match='read_committed_required|writable_required'):
                stage_initial(connection, CUSTODY, PREPARER)
    assert snapshot(engine) == ((), ())


def test_dbapi_autocommit_with_logical_transaction_is_refused(rehearsal):
    _, _, engine = rehearsal
    with engine.connect().execution_options(isolation_level='AUTOCOMMIT') as connection:
        with connection.begin():
            assert connection.in_transaction() and connection.connection.dbapi_connection.autocommit
            with pytest.raises(ValueError, match='transaction_required'):
                stage_initial(connection, CUSTODY, PREPARER)
    assert snapshot(engine) == ((), ())


def test_actual_owner_session_required_not_set_role_impersonation(rehearsal):
    admin, url, engine = rehearsal
    owner = create_engine(url.replace('postgresql://','postgresql+psycopg://'), poolclass=pool.NullPool)
    try:
        with owner.begin() as connection:
            connection.exec_driver_sql('SET LOCAL ROLE scribeswell_migrator')
            from baseline import BaselineError
            with pytest.raises(BaselineError, match='unsafe_authority'):
                stage_initial(connection, CUSTODY, PREPARER)
    finally:
        owner.dispose()
    assert snapshot(engine) == ((), ())


def test_mapping_transaction_holds_expected_locks_and_server_timestamps(rehearsal):
    _, _, engine = rehearsal
    with engine.begin() as connection:
        stage_initial(connection, CUSTODY, PREPARER)
        modes = connection.exec_driver_sql("SELECT relname,mode FROM pg_locks JOIN pg_class ON oid=relation WHERE pid=pg_backend_pid() AND relname IN ('corpus_operator_principal','corpus_operator_authority') AND mode='ShareRowExclusiveLock' ORDER BY relname").all()
        assert modes == [('corpus_operator_authority','ShareRowExclusiveLock'),('corpus_operator_principal','ShareRowExclusiveLock')]
        assert connection.exec_driver_sql("SELECT count(*) FROM pg_locks WHERE pid=pg_backend_pid() AND locktype='advisory' AND granted").scalar() == 1
        assert connection.exec_driver_sql('SELECT created_at=transaction_timestamp() AND updated_at=transaction_timestamp() FROM scribeswell.corpus_operator_principal').scalar() is True
        assert connection.exec_driver_sql('SELECT bool_and(created_at=transaction_timestamp() AND updated_at=transaction_timestamp()) FROM scribeswell.corpus_operator_authority').scalar() is True
