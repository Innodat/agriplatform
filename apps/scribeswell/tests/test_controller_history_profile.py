"""Native controller-history qualification on an exclusively owned disposable PG17."""
import pytest
from test_corpus_publication import controller_database, enabled, body, operator, execute
from test_prepared_controller_profile import staged, CUSTODY, engine_for, native
from test_owned_migrations import invoke
import baseline

PROFILE = 'controller-history-v1'


def state(admin, url):
    from catalogue import snapshot
    from test_owned_migrations import business_state
    engine = engine_for(url)
    try:
        with engine.begin() as connection:
            catalogue = snapshot(connection, head=True)
    finally:
        engine.dispose()
    # JSON text preserves even PostgreSQL infinity values without the driver's
    # finite Python datetime conversion; all rows and fields remain compared.
    records = {table: admin.execute('SELECT row_to_json(t)::text FROM scribeswell.' + table + ' t ORDER BY 1').fetchall()
               for table in ('alembic_version', 'corpus_operator_principal', 'corpus_operator_authority',
                             'corpus_fence_control', 'corpus_epoch', 'corpus_attempt',
                             'corpus_command_outcome', 'corpus_write_binding')}
    return catalogue, business_state(admin), records


def direct(url, expected=CUSTODY):
    engine = engine_for(url)
    try:
        with engine.begin() as connection:
            return baseline.preflight_controller_history(connection, expected)
    finally:
        engine.dispose()


def chain(staged):
    admin, url = staged
    admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=true')
    with operator(url) as connection:
        first = body(); began = execute(connection, first)
        seal = body('seal', began); closed = execute(connection, seal)
        recovery = body('recover', closed); current = execute(connection, recovery)
    return [(first, began), (seal, closed), (recovery, current)]


def test_existing_profiles_reject_history_without_mutation(staged, monkeypatch):
    admin, url = staged
    chain(staged)
    before = state(admin, url)
    assert invoke(url).returncode != 0
    with pytest.raises(baseline.BaselineError, match='dormant_state_required'):
        native(url, monkeypatch, dict(scribeswell_validation_profile='prepared-controller-v1', scribeswell_prepared_actor=CUSTODY))
    assert state(admin, url) == before


def test_history_replay_preserves_actual_chain(staged, monkeypatch):
    admin, url = staged
    chain(staged)
    before = state(admin, url)
    assert direct(url) == baseline.REVISION
    config = native(url, monkeypatch, dict(scribeswell_validation_profile=PROFILE, scribeswell_prepared_actor=CUSTODY))
    assert config.attributes['scribeswell_validated_profile'] == PROFILE
    assert config.attributes['scribeswell_before'] == config.attributes['scribeswell_after'] == baseline.REVISION
    assert state(admin, url) == before


@pytest.mark.parametrize('mode', ['empty', 'armed', 'updating', 'closed', 'recover_updating', 'recover_closed'])
def test_supported_lifecycle_states(staged, monkeypatch, mode):
    admin, url = staged
    if mode != 'empty':
        admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=true')
    if mode not in ('empty', 'armed'):
        with operator(url) as connection:
            receipt = execute(connection, body())
            if mode in ('closed', 'recover_closed'):
                receipt = execute(connection, body('seal', receipt))
            if mode.startswith('recover'):
                receipt = execute(connection, body('recover', receipt))
    before = state(admin, url)
    assert direct(url) == baseline.REVISION
    config = native(url, monkeypatch, dict(scribeswell_validation_profile=PROFILE, scribeswell_prepared_actor=CUSTODY))
    assert config.attributes['scribeswell_validated_profile'] == PROFILE
    assert state(admin, url) == before


def test_suspension_and_original_lookup_preserved(staged):
    from corpus_publication import lookup_outcome, PublicationError
    from test_corpus_publication_input import encode
    admin, url = staged
    commands = chain(staged)
    admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=false')
    # Old receipt lookup is available with current authority even while paused.
    with operator(url) as connection:
        for request, receipt in commands:
            assert lookup_outcome(connection, encode(request)) == receipt
    admin.execute('UPDATE scribeswell.corpus_operator_principal SET enabled=false,revision=revision+1')
    admin.execute('UPDATE scribeswell.corpus_operator_authority SET enabled=false,revision=revision+1')
    before = state(admin, url)
    assert direct(url) == baseline.REVISION
    with operator(url) as connection:
        with pytest.raises(PublicationError, match='access_denied'):
            lookup_outcome(connection, encode(commands[0][0]))
    assert state(admin, url) == before


def test_historical_executor_rotation_is_not_rebound_authority(staged):
    from corpus_publication import lookup_outcome, PublicationError
    from test_corpus_publication_input import encode
    admin, url = staged
    commands = chain(staged)
    replacement = '33333333-3333-4333-8333-333333333333'
    admin.execute('UPDATE scribeswell.corpus_operator_principal SET executor_actor_id=%s,revision=revision+1,updated_by_actor_id=%s', (replacement, replacement))
    expected = dict(CUSTODY, executor_actor_id=replacement)
    with operator(url) as connection:
        current = execute(connection, body('recover', commands[-1][1]))
        assert current.executor_actor_id == replacement
        with pytest.raises(PublicationError, match='conflict'):
            lookup_outcome(connection, encode(commands[0][0]))
    before = state(admin, url)
    assert direct(url, expected) == baseline.REVISION
    with pytest.raises(baseline.BaselineError, match='custody_mismatch'):
        direct(url)
    assert state(admin, url) == before


def tamper(admin, query):
    # Simulate owner-corrupted data, with the exact original trigger catalogue
    # restored before validation; no structural drift hides the data predicate.
    tables = ('corpus_attempt', 'corpus_command_outcome')
    for table in tables:
        admin.execute('ALTER TABLE scribeswell.' + table + ' DISABLE TRIGGER corpus_record_protection')
    try:
        admin.execute(query)
    finally:
        for table in tables:
            admin.execute('ALTER TABLE scribeswell.' + table + ' ENABLE ALWAYS TRIGGER corpus_record_protection')


@pytest.mark.parametrize('query', [
    'DELETE FROM scribeswell.corpus_command_outcome WHERE generation=1 AND semantic_command->>\'command\'=\'corpus.begin\'',
    'DELETE FROM scribeswell.corpus_epoch',
    'UPDATE scribeswell.corpus_epoch SET generation=3',
    "UPDATE scribeswell.corpus_epoch SET source_id='other'",
    "UPDATE scribeswell.corpus_epoch SET attempt_id='44444444-4444-4444-8444-444444444444'",
    "UPDATE scribeswell.corpus_epoch SET input_sha256=repeat('b',64)",
    "UPDATE scribeswell.corpus_epoch SET state='closed'",
    "UPDATE scribeswell.corpus_epoch SET created_at='infinity'",
    "UPDATE scribeswell.corpus_epoch SET updated_at='-infinity'",
    "UPDATE scribeswell.corpus_epoch SET created_by_actor_id='44444444-4444-4444-8444-444444444444'",
    "UPDATE scribeswell.corpus_epoch SET updated_by_actor_id='44444444-4444-4444-8444-444444444444'",
    "UPDATE scribeswell.corpus_epoch SET updated_at=updated_at+interval '1 second'",
    "UPDATE scribeswell.corpus_attempt SET state='closed' WHERE generation=1",
    "UPDATE scribeswell.corpus_attempt SET state='retired' WHERE generation=2",
    "UPDATE scribeswell.corpus_attempt SET catalogue_version='other' WHERE generation=1",
    "UPDATE scribeswell.corpus_attempt SET created_by_actor_id='44444444-4444-4444-8444-444444444444' WHERE generation=1",
    "UPDATE scribeswell.corpus_attempt SET updated_by_actor_id='44444444-4444-4444-8444-444444444444' WHERE generation=1",
    "UPDATE scribeswell.corpus_attempt SET created_at=created_at+interval '1 second' WHERE generation=1",
    "UPDATE scribeswell.corpus_command_outcome SET semantic_command='{}'::jsonb WHERE generation=1",
    "UPDATE scribeswell.corpus_command_outcome SET semantic_command=jsonb_set(semantic_command,'{operation_id}','\"44444444-4444-4444-8444-444444444444\"') WHERE generation=1",
    "UPDATE scribeswell.corpus_command_outcome SET semantic_command=jsonb_set(semantic_command,'{scope,source_id}','\"other\"') WHERE generation=1",
    "UPDATE scribeswell.corpus_command_outcome SET semantic_command=jsonb_set(semantic_command,'{payload,input,source_sha256}',to_jsonb(repeat('b',64))) WHERE generation=1",
    "UPDATE scribeswell.corpus_command_outcome SET semantic_command=jsonb_set(semantic_command,'{payload,expected_generation}','\"7\"') WHERE generation=2",
    "UPDATE scribeswell.corpus_command_outcome SET semantic_command=jsonb_set(semantic_command,'{payload,expected_attempt_id}','\"44444444-4444-4444-8444-444444444444\"') WHERE generation=2",
    "UPDATE scribeswell.corpus_command_outcome SET result=result||'{\"extra\":true}'::jsonb WHERE generation=1",
    "UPDATE scribeswell.corpus_command_outcome SET result=jsonb_set(result,'{generation}','2') WHERE generation=1",
    'UPDATE scribeswell.corpus_command_outcome SET principal_revision=99 WHERE generation=1',
    'UPDATE scribeswell.corpus_command_outcome SET authority_revision=99 WHERE generation=1',
    "UPDATE scribeswell.corpus_command_outcome SET created_at=created_at+interval '1 second' WHERE generation=2",
])
def test_corrupt_history_rejected_without_mutation(staged, query):
    admin, url = staged
    chain(staged)
    tamper(admin, query)
    before = state(admin, url)
    with pytest.raises(baseline.BaselineError, match='^scribeswell_history_') as failure:
        direct(url)
    assert failure.value.__cause__ is None
    assert state(admin, url) == before


def test_closed_current_requires_seal(staged):
    admin, url = staged
    commands = chain(staged)
    with operator(url) as connection:
        execute(connection, body('seal', commands[-1][1]))
    tamper(admin, "DELETE FROM scribeswell.corpus_command_outcome WHERE generation=2 AND semantic_command->>'command'='corpus.seal'")
    before = state(admin, url)
    with pytest.raises(baseline.BaselineError, match='scribeswell_history_invalid'):
        direct(url)
    assert state(admin, url) == before


@pytest.mark.parametrize('table,limit', [('corpus_attempt', 2), ('corpus_command_outcome', 3)])
def test_count_caps_exact_boundary_and_one_over(staged, monkeypatch, table, limit):
    import controller_history
    admin, url = staged
    chain(staged)
    constant = 'MAX_ATTEMPTS' if table == 'corpus_attempt' else 'MAX_OUTCOMES'
    assert controller_history.MAX_ATTEMPTS == 10000 and controller_history.MAX_OUTCOMES == 20000
    monkeypatch.setattr(controller_history, constant, limit)
    before = state(admin, url)
    assert direct(url) == baseline.REVISION
    monkeypatch.setattr(controller_history, constant, limit - 1)
    with pytest.raises(baseline.BaselineError, match='^scribeswell_history_limit_exceeded$'):
        direct(url)
    assert state(admin, url) == before


@pytest.mark.parametrize('table', ['corpus_attempt', 'corpus_command_outcome'])
def test_real_cardinality_one_over_fixed_caps(staged, table):
    admin, url = staged
    chain(staged)
    if table == 'corpus_attempt':
        admin.execute("""INSERT INTO scribeswell.corpus_attempt(attempt_id,source_id,generation,input_sha256,catalogue_version,versification_id,tokenization_version,state,created_by_actor_id,updated_by_actor_id)
            SELECT gen_random_uuid(),'tanakh',g,repeat('a',64),'fixture','fixture','fixture','retired',%s,%s
            FROM generate_series(3,10001) g""", (CUSTODY['executor_actor_id'], CUSTODY['executor_actor_id']))
        assert admin.execute('SELECT count(*) FROM scribeswell.corpus_attempt').fetchone() == (10001,)
    else:
        admin.execute("""INSERT INTO scribeswell.corpus_command_outcome(database_login,operation_id,semantic_command,executor_actor_id,principal_revision,authority_revision,result,attempt_id,source_id,generation,created_by_actor_id)
            SELECT 'scribeswell_corpus_operator',gen_random_uuid(),'{}'::jsonb,%s,1,1,'{}'::jsonb,a.attempt_id,a.source_id,a.generation,%s
            FROM scribeswell.corpus_attempt a CROSS JOIN generate_series(1,19998) WHERE a.generation=1""", (CUSTODY['executor_actor_id'], CUSTODY['executor_actor_id']))
        assert admin.execute('SELECT count(*) FROM scribeswell.corpus_command_outcome').fetchone() == (20001,)
    before = state(admin, url)
    with pytest.raises(baseline.BaselineError, match='^scribeswell_history_limit_exceeded$'):
        direct(url)
    assert state(admin, url) == before


@pytest.mark.parametrize('attrs', [
    {'scribeswell_validation_profile': PROFILE},
    {'scribeswell_validation_profile': PROFILE, 'scribeswell_prepared_actor': None},
    {'scribeswell_validation_profile': PROFILE, 'scribeswell_prepared_actor': dict(CUSTODY, extra=True)},
])
def test_closed_history_selection(staged, monkeypatch, attrs):
    admin, url = staged
    before = state(admin, url)
    with pytest.raises(baseline.BaselineError):
        native(url, monkeypatch, attrs)
    assert state(admin, url) == before


@pytest.mark.parametrize('isolation', ['fresh', 'AUTOCOMMIT', 'REPEATABLE READ', 'SERIALIZABLE', 'read_only'])
def test_history_requires_caller_writable_read_committed(staged, isolation):
    _, url = staged
    engine = engine_for(url)
    try:
        with engine.connect() as connection:
            if isolation in ('AUTOCOMMIT', 'REPEATABLE READ', 'SERIALIZABLE'):
                connection = connection.execution_options(isolation_level=isolation)
            if isolation != 'fresh':
                connection.begin()
            if isolation == 'read_only':
                connection.exec_driver_sql('SET TRANSACTION READ ONLY')
            with pytest.raises(baseline.BaselineError, match='transaction_required'):
                baseline.preflight_controller_history(connection, CUSTODY)
            if isolation == 'fresh':
                assert not connection.in_transaction()
    finally:
        engine.dispose()


@pytest.mark.parametrize('change,restore', [
    ('ALTER ROLE scribeswell_corpus_operator CREATEDB', 'ALTER ROLE scribeswell_corpus_operator NOCREATEDB'),
    ('GRANT SELECT ON scribeswell.book TO scribeswell_corpus_operator', 'REVOKE SELECT ON scribeswell.book FROM scribeswell_corpus_operator'),
    ('CREATE TABLE scribeswell.unexpected(id int)', 'DROP TABLE scribeswell.unexpected'),
])
def test_history_retains_strict_target_checks(staged, change, restore):
    admin, url = staged
    chain(staged)
    admin.execute(change)
    try:
        before = state(admin, url)
        with pytest.raises(baseline.BaselineError):
            direct(url)
        assert state(admin, url) == before
    finally:
        admin.execute(restore)


@pytest.mark.parametrize('revision', [None, 'scribeswell_0001', 'scribeswell_0002'])
def test_history_cannot_adopt_or_upgrade_earlier_ledger(staged, revision):
    admin, url = staged
    if revision is None:
        admin.execute('TRUNCATE scribeswell.alembic_version')
    else:
        admin.execute('UPDATE scribeswell.alembic_version SET version_num=%s', (revision,))
    try:
        before = state(admin, url)
        with pytest.raises(baseline.BaselineError, match='ledger_invalid' if revision is None else 'revision_required'):
            direct(url)
        assert state(admin, url) == before
    finally:
        admin.execute('TRUNCATE scribeswell.alembic_version')
        admin.execute('INSERT INTO scribeswell.alembic_version VALUES (%s)', (baseline.REVISION,))


@pytest.mark.parametrize('fault', ['postcheck', 'commit'])
def test_native_fault_rolls_back_real_pending_row_and_clears_evidence(staged, monkeypatch, fault):
    import sqlalchemy
    from sqlalchemy import event
    from alembic import command
    from alembic.config import Config
    from test_owned_migrations import APP, migration_url
    admin, url = staged
    chain(staged)
    admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=false')
    before = state(admin, url)
    engine = engine_for(url)
    config = Config(str(APP / 'alembic.ini'))
    config.attributes.update(scribeswell_validation_profile=PROFILE, scribeswell_prepared_actor=CUSTODY, scribeswell_validated_profile='stale')
    original = baseline.preflight_controller_history
    calls = []
    def mutate_and_fail(connection):
        connection.exec_driver_sql("UPDATE scribeswell.book SET name_en='pending history fault' WHERE id=1")
        raise RuntimeError('private injected fault')
    def checked(connection, actor):
        result = original(connection, actor)
        calls.append(1)
        assert 'scribeswell_validated_profile' not in config.attributes
        if len(calls) == 2 and fault == 'postcheck':
            mutate_and_fail(connection)
        return result
    if fault == 'commit':
        event.listen(engine, 'commit', mutate_and_fail)
    monkeypatch.setattr(baseline, 'preflight_controller_history', checked)
    monkeypatch.setattr(sqlalchemy, 'create_engine', lambda *args, **kwargs: engine)
    monkeypatch.setenv('SCRIBESWELL_MIGRATION_DATABASE_URL', migration_url(url))
    with pytest.raises(baseline.BaselineError, match='^scribeswell_migration_failed_requires_reconciliation$') as failure:
        command.upgrade(config, 'head')
    assert calls == [1, 1]
    assert 'scribeswell_validated_profile' not in config.attributes
    assert failure.value.__cause__ is None and failure.value.__suppress_context__
    assert state(admin, url) == before


def test_transition_first_validation_waits_before_table_locks(staged):
    from psycopg.types.json import Jsonb
    from test_corpus_publication import EXECUTE
    from test_corpus_writer_fence import background, wait_blocked
    admin, url = staged
    admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=true')
    engine = engine_for(url)
    try:
        with operator(url) as caller, engine.begin() as checker:
            caller.execute('BEGIN')
            receipt = caller.execute(EXECUTE, (Jsonb(body()),)).fetchone()[0]
            pid = checker.exec_driver_sql('SELECT pg_backend_pid()').scalar()
            with background(checker.connection.dbapi_connection, lambda: baseline.preflight_controller_history(checker, CUSTODY)) as future:
                try:
                    wait_blocked(admin, pid, caller.info.backend_pid)
                    # Before transition completion the checker owns no table SHARE
                    # lock; it cannot invert epoch/attempt write acquisition.
                    assert admin.execute("SELECT count(*) FROM pg_locks WHERE pid=%s AND mode='ShareLock' AND relation IS NOT NULL", (pid,)).fetchone() == (0,)
                finally:
                    caller.execute('COMMIT')
                assert future.result(timeout=5) == baseline.REVISION
            assert checker.exec_driver_sql('SELECT attempt_id::text FROM scribeswell.corpus_epoch').scalar() == receipt['attempt_id']
    finally:
        engine.dispose()
    assert direct(url) == baseline.REVISION


def test_validation_first_new_transition_waits_for_advisory_release(staged):
    from psycopg.types.json import Jsonb
    from test_corpus_publication import EXECUTE
    from test_corpus_writer_fence import background, wait_blocked
    admin, url = staged
    admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=true')
    engine = engine_for(url)
    try:
        with engine.begin() as checker, operator(url) as caller:
            assert baseline.preflight_controller_history(checker, CUSTODY) == baseline.REVISION
            pid = checker.exec_driver_sql('SELECT pg_backend_pid()').scalar()
            before = state(admin, url)
            with background(caller, lambda: caller.execute(EXECUTE, (Jsonb(body()),)).fetchone()[0]) as transition:
                try:
                    wait_blocked(admin, caller.info.backend_pid, pid)
                    assert state(admin, url) == before
                finally:
                    checker.commit()
                receipt = transition.result(timeout=5)
                assert receipt['generation'] == '1'
    finally:
        engine.dispose()
    assert direct(url) == baseline.REVISION


def test_bound_writer_finishes_and_cleanup_precedes_history_check(staged):
    from test_corpus_writer_fence import importer, BIND, background, wait_blocked
    admin, url = staged
    receipt = chain(staged)[-1][1]
    engine = engine_for(url)
    admin.execute('GRANT EXECUTE ON FUNCTION scribeswell.bind_corpus_write(text,bigint,uuid,text) TO scribeswell_import')
    try:
        with importer(url) as writer, engine.begin() as checker:
            writer.execute('BEGIN')
            digest = admin.execute('SELECT input_sha256 FROM scribeswell.corpus_epoch').fetchone()[0]
            writer.execute(BIND, ('tanakh', int(receipt.generation), receipt.attempt_id, digest))
            writer.execute("UPDATE scribeswell.book SET name_en='bound history writer' WHERE id=1")
            # Restore exact supported ACL before inspecting it. The already
            # executing writer retains its transaction-bound authority until commit.
            admin.execute('REVOKE EXECUTE ON FUNCTION scribeswell.bind_corpus_write(text,bigint,uuid,text) FROM scribeswell_import')
            pid = checker.exec_driver_sql('SELECT pg_backend_pid()').scalar()
            with background(checker.connection.dbapi_connection, lambda: baseline.preflight_controller_history(checker, CUSTODY)) as future:
                try:
                    wait_blocked(admin, pid, writer.info.backend_pid)
                finally:
                    writer.execute('COMMIT')
                assert future.result(timeout=5) == baseline.REVISION
    finally:
        admin.execute('REVOKE EXECUTE ON FUNCTION scribeswell.bind_corpus_write(text,bigint,uuid,text) FROM scribeswell_import')
        engine.dispose()
    assert admin.execute('SELECT name_en FROM scribeswell.book WHERE id=1').fetchone() == ('bound history writer',)
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_write_binding').fetchone() == (0,)
    assert direct(url) == baseline.REVISION


def test_committed_binding_debris_fails_after_catalogue_restored(staged):
    admin, url = staged
    receipt = chain(staged)[-1][1]
    admin.execute('ALTER TABLE scribeswell.corpus_write_binding DISABLE TRIGGER corpus_binding_cleanup')
    try:
        admin.execute("INSERT INTO scribeswell.corpus_write_binding VALUES ('scribeswell_import',pg_backend_pid(),pg_current_xact_id(),'tanakh',%s,%s,repeat('a',64))", (int(receipt.generation), receipt.attempt_id))
    finally:
        admin.execute('ALTER TABLE scribeswell.corpus_write_binding ENABLE ALWAYS TRIGGER corpus_binding_cleanup')
    before = state(admin, url)
    with pytest.raises(baseline.BaselineError, match='^scribeswell_history_invalid$'):
        direct(url)
    assert state(admin, url) == before


def test_configuration_writer_first_fails_with_safe_bounded_wait(staged):
    import time
    admin, url = staged
    chain(staged)
    before = state(admin, url)
    with admin.transaction():
        admin.execute('UPDATE scribeswell.corpus_operator_authority SET enabled=false,revision=revision+1')
        started = time.monotonic()
        with pytest.raises(baseline.BaselineError, match='^scribeswell_history_validation_failed$') as failure:
            direct(url)
        assert time.monotonic() - started < 4
        assert failure.value.__cause__ is None and failure.value.__suppress_context__
        admin.execute('ROLLBACK')
    assert state(admin, url) == before


@pytest.mark.parametrize('kind', ['duplicate_origin', 'duplicate_seal', 'orphan_attempt', 'gapped_history'])
def test_history_cardinality_and_missing_generation(staged, kind):
    admin, url = staged
    chain(staged)
    if kind.startswith('duplicate'):
        command_name = 'corpus.begin' if kind == 'duplicate_origin' else 'corpus.seal'
        # All envelope/receipt fields remain self-consistent. Only cardinality
        # differs, so the test cannot pass through an unrelated JSON mismatch.
        admin.execute('ALTER TABLE scribeswell.corpus_command_outcome DISABLE TRIGGER corpus_record_protection')
        try:
            admin.execute("""INSERT INTO scribeswell.corpus_command_outcome
                SELECT o.database_login,n.id,jsonb_set(o.semantic_command,'{operation_id}',to_jsonb(n.id::text)),
                    o.executor_actor_id,o.principal_revision,o.authority_revision,
                    jsonb_set(o.result,'{operation_id}',to_jsonb(n.id::text)),o.attempt_id,o.source_id,o.generation,
                    o.created_by_actor_id,o.created_at
                FROM scribeswell.corpus_command_outcome o CROSS JOIN LATERAL (SELECT gen_random_uuid() AS id) n
                WHERE o.semantic_command->>'command'=%s""", (command_name,))
        finally:
            admin.execute('ALTER TABLE scribeswell.corpus_command_outcome ENABLE ALWAYS TRIGGER corpus_record_protection')
        assert admin.execute("SELECT count(*) FROM scribeswell.corpus_command_outcome WHERE semantic_command->>'command'=%s", (command_name,)).fetchone() == (2,)
    elif kind == 'orphan_attempt':
        admin.execute("""INSERT INTO scribeswell.corpus_attempt(attempt_id,source_id,generation,input_sha256,catalogue_version,versification_id,tokenization_version,state,created_by_actor_id,updated_by_actor_id)
            SELECT gen_random_uuid(),source_id,3,input_sha256,catalogue_version,versification_id,tokenization_version,'retired',created_by_actor_id,updated_by_actor_id
            FROM scribeswell.corpus_attempt WHERE generation=2""")
    else:
        tamper(admin, 'DELETE FROM scribeswell.corpus_command_outcome WHERE generation=1;DELETE FROM scribeswell.corpus_attempt WHERE generation=1')
        assert admin.execute('SELECT generation FROM scribeswell.corpus_attempt').fetchall() == [(2,)]
    before = state(admin, url)
    with pytest.raises(baseline.BaselineError, match='^scribeswell_history_invalid$'):
        direct(url)
    assert state(admin, url) == before


@pytest.mark.parametrize('field,value', [
    ('version', '"1"'), ('operation_id', '"44444444-4444-4444-8444-444444444444"'),
    ('command', '"corpus.seal"'), ('source_id', '"other"'),
    ('executor_actor_id', '"44444444-4444-4444-8444-444444444444"'),
    ('attempt_id', '"44444444-4444-4444-8444-444444444444"'),
    ('generation', '1'), ('state', '"closed"'),
])
def test_each_result_field_uses_original_typed_receipt(staged, field, value):
    from psycopg.types.json import Jsonb
    import json
    admin, url = staged
    chain(staged)
    admin.execute('ALTER TABLE scribeswell.corpus_command_outcome DISABLE TRIGGER corpus_record_protection')
    try:
        admin.execute("UPDATE scribeswell.corpus_command_outcome SET result=jsonb_set(result,%s,%s) WHERE semantic_command->>'command'='corpus.begin'", ([field], Jsonb(json.loads(value))))
    finally:
        admin.execute('ALTER TABLE scribeswell.corpus_command_outcome ENABLE ALWAYS TRIGGER corpus_record_protection')
    before = state(admin, url)
    with pytest.raises(baseline.BaselineError, match='^scribeswell_history_invalid$'):
        direct(url)
    assert state(admin, url) == before


@pytest.mark.parametrize('field', ['catalogue_version', 'versification_id', 'tokenization_version'])
def test_all_input_identity_fields_match_attempt(staged, field):
    admin, url = staged
    chain(staged)
    admin.execute('ALTER TABLE scribeswell.corpus_command_outcome DISABLE TRIGGER corpus_record_protection')
    try:
        admin.execute("UPDATE scribeswell.corpus_command_outcome SET semantic_command=jsonb_set(semantic_command,%s,'\"other\"'::jsonb) WHERE generation=2", (['payload', 'input', field],))
    finally:
        admin.execute('ALTER TABLE scribeswell.corpus_command_outcome ENABLE ALWAYS TRIGGER corpus_record_protection')
    before = state(admin, url)
    with pytest.raises(baseline.BaselineError, match='^scribeswell_history_invalid$'):
        direct(url)
    assert state(admin, url) == before


def test_timeout_ceilings_and_catalogue_path_reused_in_history(staged):
    _, url = staged
    chain(staged)
    engine = engine_for(url)
    try:
        with engine.begin() as connection:
            connection.exec_driver_sql("SET LOCAL statement_timeout='1200ms'")
            connection.exec_driver_sql("SET LOCAL lock_timeout='150ms'")
            connection.exec_driver_sql('CREATE TEMP TABLE pg_roles AS SELECT * FROM pg_catalog.pg_roles')
            connection.exec_driver_sql('SET LOCAL search_path=public,pg_catalog')
            assert baseline.preflight_controller_history(connection, CUSTODY) == baseline.REVISION
            assert connection.exec_driver_sql('SHOW search_path').scalar() == 'pg_catalog, pg_temp'
            assert connection.exec_driver_sql('SHOW statement_timeout').scalar() == '1200ms'
            assert connection.exec_driver_sql('SHOW lock_timeout').scalar() == '150ms'
    finally:
        engine.dispose()


def test_fixed_full_history_limit_accepts_complete_coherent_state(staged, monkeypatch):
    admin, url = staged
    # Large synthetic history qualifies the actual numeric capacity independently
    # of small real-command fixtures. Equal event timestamps are legal when native
    # commands share a transaction. Keep all structural/attribution triggers active.
    with admin.transaction():
        admin.execute("""INSERT INTO scribeswell.corpus_attempt(attempt_id,source_id,generation,input_sha256,catalogue_version,versification_id,tokenization_version,state,created_by_actor_id,updated_by_actor_id)
            SELECT gen_random_uuid(),'tanakh',g,repeat('a',64),'fixture','fixture','fixture',
                CASE WHEN g=10000 THEN 'closed' ELSE 'retired' END,%s,%s
            FROM generate_series(1,10000) g""", (CUSTODY['executor_actor_id'], CUSTODY['executor_actor_id']))
        admin.execute("""WITH events AS (
            SELECT a.*,p.attempt_id AS previous_attempt,gen_random_uuid() AS operation,
                CASE WHEN a.generation=1 THEN 'corpus.begin' ELSE 'corpus.recover' END AS command,
                jsonb_build_object('source_sha256',a.input_sha256,'catalogue_version',a.catalogue_version,
                    'versification_id',a.versification_id,'tokenization_version',a.tokenization_version) AS identity
            FROM scribeswell.corpus_attempt a LEFT JOIN scribeswell.corpus_attempt p ON p.generation=a.generation-1)
            INSERT INTO scribeswell.corpus_command_outcome(database_login,operation_id,semantic_command,executor_actor_id,principal_revision,authority_revision,result,attempt_id,source_id,generation,created_by_actor_id)
            SELECT 'scribeswell_corpus_operator',operation,
                jsonb_build_object('schema_version',1,'operation_id',operation::text,'command',command,
                    'scope',jsonb_build_object('kind','source','source_id',source_id),
                    'payload',CASE WHEN generation=1 THEN jsonb_build_object('expected_absent',true,'input',identity)
                        ELSE jsonb_build_object('expected_generation',(generation-1)::text,'expected_attempt_id',previous_attempt::text,'input',identity) END,
                    'reason_code','synthetic_fixture','evidence_ref','fixture:capacity'),
                created_by_actor_id,1,1,
                jsonb_build_object('version',1,'operation_id',operation::text,'command',command,'source_id',source_id,
                    'executor_actor_id',created_by_actor_id::text,'attempt_id',attempt_id::text,'generation',generation::text,'state','updating'),
                attempt_id,source_id,generation,created_by_actor_id FROM events""")
        admin.execute("""WITH events AS (SELECT a.*,gen_random_uuid() AS operation,
            jsonb_build_object('source_sha256',input_sha256,'catalogue_version',catalogue_version,
                'versification_id',versification_id,'tokenization_version',tokenization_version) AS identity
            FROM scribeswell.corpus_attempt a)
            INSERT INTO scribeswell.corpus_command_outcome(database_login,operation_id,semantic_command,executor_actor_id,principal_revision,authority_revision,result,attempt_id,source_id,generation,created_by_actor_id)
            SELECT 'scribeswell_corpus_operator',operation,
                jsonb_build_object('schema_version',1,'operation_id',operation::text,'command','corpus.seal',
                    'scope',jsonb_build_object('kind','source','source_id',source_id),
                    'payload',jsonb_build_object('expected_generation',generation::text,'expected_attempt_id',attempt_id::text,'input',identity),
                    'reason_code','synthetic_fixture','evidence_ref','fixture:capacity'),
                created_by_actor_id,1,1,
                jsonb_build_object('version',1,'operation_id',operation::text,'command','corpus.seal','source_id',source_id,
                    'executor_actor_id',created_by_actor_id::text,'attempt_id',attempt_id::text,'generation',generation::text,'state','closed'),
                attempt_id,source_id,generation,created_by_actor_id FROM events""")
        admin.execute("""INSERT INTO scribeswell.corpus_epoch(source_id,generation,attempt_id,input_sha256,state,created_by_actor_id,updated_by_actor_id)
            SELECT source_id,generation,attempt_id,input_sha256,state,created_by_actor_id,updated_by_actor_id
            FROM scribeswell.corpus_attempt WHERE generation=10000""")
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_attempt').fetchone() == (10000,)
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_command_outcome').fetchone() == (20000,)
    before = state(admin, url)
    assert direct(url) == baseline.REVISION
    config = native(url, monkeypatch, dict(scribeswell_validation_profile=PROFILE, scribeswell_prepared_actor=CUSTODY))
    assert config.attributes['scribeswell_validated_profile'] == PROFILE
    assert state(admin, url) == before


@pytest.mark.parametrize('path', [['schema_version'], ['reason_code'], ['evidence_ref'], ['payload', 'expected_absent']])
def test_json_nulls_rejected_by_existing_native_grammar(staged, path):
    from psycopg.types.json import Jsonb
    import psycopg
    admin, url = staged
    request = body()
    target = request
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = None
    with pytest.raises(psycopg.errors.InvalidParameterValue):
        admin.execute('SELECT scribeswell.validate_corpus_command(%s)', (Jsonb(request),))
    chain(staged)
    admin.execute('ALTER TABLE scribeswell.corpus_command_outcome DISABLE TRIGGER corpus_record_protection')
    try:
        admin.execute("UPDATE scribeswell.corpus_command_outcome SET semantic_command=jsonb_set(semantic_command,%s,'null'::jsonb) WHERE semantic_command->>'command'='corpus.begin'", (path,))
    finally:
        admin.execute('ALTER TABLE scribeswell.corpus_command_outcome ENABLE ALWAYS TRIGGER corpus_record_protection')
    before = state(admin, url)
    with pytest.raises(baseline.BaselineError, match='^scribeswell_history_validation_failed$'):
        direct(url)
    assert state(admin, url) == before


@pytest.mark.parametrize('policy', ['principal', 'authority'])
def test_outcome_cannot_claim_current_disabled_revision(staged, policy):
    admin, url = staged
    chain(staged)
    admin.execute('UPDATE scribeswell.corpus_operator_' + policy + ' SET enabled=false,revision=revision+1')
    field = 'principal_revision' if policy == 'principal' else 'authority_revision'
    tamper(admin, 'UPDATE scribeswell.corpus_command_outcome SET ' + field + '=2')
    before = state(admin, url)
    with pytest.raises(baseline.BaselineError, match='^scribeswell_history_invalid$'):
        direct(url)
    assert state(admin, url) == before


@pytest.mark.parametrize('kind', ['principal_decrease', 'same_revision_actor', 'authority_decrease'])
def test_in_bound_historical_ordering_rejects_inconsistent_evidence(staged, kind):
    admin, url = staged
    commands = chain(staged)
    if kind == 'authority_decrease':
        with operator(url) as connection:
            execute(connection, body('recover', commands[-1][1]))
        admin.execute('UPDATE scribeswell.corpus_operator_authority SET revision=3')
        tamper(admin, "UPDATE scribeswell.corpus_command_outcome SET authority_revision=2 WHERE generation=2")
    else:
        admin.execute('UPDATE scribeswell.corpus_operator_principal SET revision=3')
        if kind == 'principal_decrease':
            tamper(admin, "UPDATE scribeswell.corpus_command_outcome SET principal_revision=2 WHERE semantic_command->>'command'='corpus.begin'")
        else:
            tamper(admin, """UPDATE scribeswell.corpus_command_outcome SET principal_revision=2;
                UPDATE scribeswell.corpus_command_outcome SET
                    executor_actor_id='33333333-3333-4333-8333-333333333333',
                    created_by_actor_id='33333333-3333-4333-8333-333333333333',
                    result=jsonb_set(result,'{executor_actor_id}','"33333333-3333-4333-8333-333333333333"'::jsonb)
                WHERE semantic_command->>'command'='corpus.seal'""")
    # Every revision stays positive and within current bounds; receipt semantics,
    # topology, input and final attribution still match, isolating window ordering.
    assert admin.execute('SELECT max(principal_revision),max(authority_revision) FROM scribeswell.corpus_command_outcome').fetchone()[0] <= 3
    before = state(admin, url)
    with pytest.raises(baseline.BaselineError, match='^scribeswell_history_invalid$'):
        direct(url)
    assert state(admin, url) == before


def test_recovery_adopts_new_source_identity_and_preserves_original_outcomes(staged, monkeypatch):
    import hashlib
    from corpus_publication import execute_command, lookup_outcome
    from test_corpus_publication_input import source_bytes, encode
    admin, url = staged
    admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=true')
    old_source = source_bytes()
    new_source = old_source.replace('אָב'.encode(), 'אֵם'.encode())
    assert new_source != old_source
    new_input = dict(source_sha256=hashlib.sha256(new_source).hexdigest(), catalogue_version='catalogue-v2',
                     versification_id='versification-v2', tokenization_version='tokens-v2')
    with operator(url) as connection:
        initial = body(); began = execute(connection, initial)
        recovery = body('recover', began); recovery['payload']['input'] = new_input
        recovered = execute_command(connection, encode(recovery), new_source)
        seal = body('seal', recovered); seal['payload']['input'] = new_input
        closed = execute_command(connection, encode(seal), new_source)
    assert recovered.attempt_id != began.attempt_id and closed.attempt_id == recovered.attempt_id
    identities = admin.execute('SELECT generation,input_sha256,catalogue_version,versification_id,tokenization_version FROM scribeswell.corpus_attempt ORDER BY generation').fetchall()
    assert identities == [(1, hashlib.sha256(old_source).hexdigest(), 'catalogue-v1', 'versification-v1', 'tokens-v1'),
                          (2, new_input['source_sha256'], 'catalogue-v2', 'versification-v2', 'tokens-v2')]
    before = state(admin, url)
    config = native(url, monkeypatch, dict(scribeswell_validation_profile=PROFILE, scribeswell_prepared_actor=CUSTODY))
    assert config.attributes['scribeswell_validated_profile'] == PROFILE
    with operator(url) as connection:
        for request, receipt, source in ((initial, began, old_source), (recovery, recovered, new_source), (seal, closed, new_source)):
            assert lookup_outcome(connection, encode(request)) == receipt
            assert execute_command(connection, encode(request), source) == receipt
    assert state(admin, url) == before


def test_rotation_between_origin_and_seal_preserves_distinct_attribution(staged, monkeypatch):
    from corpus_publication import lookup_outcome, PublicationError
    from test_corpus_publication_input import encode
    admin, url = staged
    admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=true')
    initial = body()
    with operator(url) as connection:
        began = execute(connection, initial)
    replacement = '33333333-3333-4333-8333-333333333333'
    admin.execute('UPDATE scribeswell.corpus_operator_principal SET executor_actor_id=%s,revision=revision+1,updated_by_actor_id=%s', (replacement, replacement))
    expected = dict(CUSTODY, executor_actor_id=replacement)
    seal = body('seal', began)
    with operator(url) as connection:
        closed = execute(connection, seal)
    assert closed.executor_actor_id == replacement
    for table in ('corpus_attempt', 'corpus_epoch'):
        assert admin.execute('SELECT created_by_actor_id::text,updated_by_actor_id::text FROM scribeswell.' + table).fetchall() == [(CUSTODY['executor_actor_id'], replacement)]
    assert admin.execute("SELECT executor_actor_id::text,principal_revision FROM scribeswell.corpus_command_outcome ORDER BY result->>'state' DESC").fetchall() == [(CUSTODY['executor_actor_id'], 1), (replacement, 2)]
    before = state(admin, url)
    config = native(url, monkeypatch, dict(scribeswell_validation_profile=PROFILE, scribeswell_prepared_actor=expected))
    assert config.attributes['scribeswell_validated_profile'] == PROFILE
    with operator(url) as connection:
        assert lookup_outcome(connection, encode(seal)) == execute(connection, seal) == closed
        with pytest.raises(PublicationError, match='conflict'):
            lookup_outcome(connection, encode(initial))
        with pytest.raises(PublicationError, match='conflict'):
            execute(connection, initial)
    assert state(admin, url) == before


def test_lost_commit_acknowledgement_leaves_durable_effect_and_requires_reconciliation(staged, monkeypatch):
    import sqlalchemy
    from alembic import command
    from alembic.config import Config
    from test_owned_migrations import APP, migration_url
    admin, url = staged
    chain(staged)
    admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=false')
    before = state(admin, url)
    engine = engine_for(url)
    config = Config(str(APP / 'alembic.ini'))
    config.attributes.update(scribeswell_validation_profile=PROFILE, scribeswell_prepared_actor=CUSTODY)
    original = baseline.preflight_controller_history
    original_commit = engine.dialect.do_commit
    checked_calls = []
    committed = []
    def checked(connection, actor):
        result = original(connection, actor)
        checked_calls.append(1)
        if len(checked_calls) == 2:
            connection.exec_driver_sql("UPDATE scribeswell.book SET name_en='durable before ack loss' WHERE id=1")
        return result
    def lost_ack(connection):
        assert checked_calls == [1, 1]
        assert 'scribeswell_validated_profile' not in config.attributes
        original_commit(connection)  # Real DBAPI commit succeeds first.
        committed.append(1)
        raise RuntimeError('private lost commit acknowledgement')
    monkeypatch.setattr(baseline, 'preflight_controller_history', checked)
    monkeypatch.setattr(engine.dialect, 'do_commit', lost_ack)
    monkeypatch.setattr(sqlalchemy, 'create_engine', lambda *args, **kwargs: engine)
    monkeypatch.setenv('SCRIBESWELL_MIGRATION_DATABASE_URL', migration_url(url))
    with pytest.raises(baseline.BaselineError, match='^scribeswell_migration_failed_requires_reconciliation$') as failure:
        command.upgrade(config, 'head')
    assert committed == [1]
    assert 'scribeswell_validated_profile' not in config.attributes
    assert failure.value.__cause__ is None and failure.value.__suppress_context__
    assert admin.execute('SELECT name_en FROM scribeswell.book WHERE id=1').fetchone() == ('durable before ack loss',)
    after = state(admin, url)
    assert before[0] == after[0] and before[2] == after[2]  # No controller/ledger change.
    # A new owner-native rehearsal inspects actual committed state; it cannot
    # assume rollback from the lost acknowledgement or undo the durable marker.
    monkeypatch.setattr(baseline, 'preflight_controller_history', original)
    monkeypatch.setattr(engine.dialect, 'do_commit', original_commit)
    command.upgrade(config, 'head')
    assert config.attributes['scribeswell_validated_profile'] == PROFILE
    assert state(admin, url) == after
