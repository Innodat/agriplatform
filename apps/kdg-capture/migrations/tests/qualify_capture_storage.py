"""Explicit rollback-only PostgreSQL qualification on the one retained KDG fixture.

No preparation, migration promotion, commit, reset or cleanup. Administrative role
switching/seeding belongs only to this fixture; it is not runtime authorization.
"""
from datetime import date
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import re
import sys
import time
from uuid import uuid4
from unittest.mock import patch

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, pool, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import native_fixture as fixture
sys.path.insert(0, str(ROOT / 'apps/kdg-capture/api'))
from capture_commands import parse_create, parse_edit, validate_answers
from questionnaire import initial_definition, parse_definition

FIXTURE = fixture.BASE / 'fixture-cff53592f5ca43a1a0cc65398957140f/fixture.json'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sys.path.insert(0, str(ROOT / 'apps/kdg-capture/write-candidate'))
import capture_create as create
outcomes = create.outcomes
candidate = load('kdg_native_storage_candidate', ROOT / 'apps/kdg-capture/migrations/candidates/0002_capture_storage.py')
write = outcomes.write

ORG, ACCOUNT, ACTOR, OTHER_ACCOUNT, OTHER_ACTOR, QUESTIONNAIRE, VERSION, CHILD = [
    f'{number:08x}-aaaa-4aaa-8aaa-{number:012x}' for number in range(1, 9)
]
QUESTION_IDS = [f'{number:08x}-aaaa-4aaa-8aaa-{number:012x}' for number in range(9, 13)]


class RollbackQualification(Exception):
    """Private sentinel: passing cases must still rollback every object and row."""


def sqlstate(error):
    seen = set()
    while error is not None and id(error) not in seen:
        seen.add(id(error))
        value = getattr(getattr(error, 'orig', error), 'sqlstate', None)
        if isinstance(value, str) and re.fullmatch('[0-9A-Z]{5}', value):
            return value
        error = error.__context__
    return None


def inspect_current(value, admin):
    """Narrow fixture identity/state checks plus current before/after metadata digest.

    Historical global digest is reported separately; it is not overwritten or assumed
    to describe later local work. No data/role/schema changes happen here.
    """
    for kind, role in zip(('migrator', 'runtime', 'operator'), fixture.ROLES):
        with fixture.connect(make_url(value['urls'][kind]), readonly=True) as connection:
            assert connection.execute('SHOW transaction_read_only').fetchone() == ('on',)
            assert connection.execute('SELECT current_user,session_user').fetchone() == (role, role)
            assert connection.execute("SELECT pg_has_role(current_user,'supabase_admin','MEMBER')").fetchone() == (False,)
            if kind != 'migrator':
                assert connection.execute("SELECT pg_has_role(current_user,'kdg_capture_migrator','MEMBER')").fetchone() == (False,)
                assert connection.execute("SELECT has_schema_privilege(current_user,'kdg_capture','CREATE')").fetchone() == (False,)
                assert connection.execute("SELECT has_table_privilege(current_user,'kdg_capture.alembic_version','SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')").fetchone() == (False,)
    with fixture.connect(admin.set(database=value['database']), readonly=True) as connection:
        assert connection.execute('SELECT version_num FROM kdg_capture.alembic_version').fetchall() == [('0001_kdg_foundation',)]
        assert connection.execute("SELECT tablename FROM pg_tables WHERE schemaname='kdg_capture' ORDER BY tablename").fetchall() == [('alembic_version',)]
        assert connection.execute('SELECT value FROM fixture_foreign.sentinel').fetchall() == [(1,)]
        roles = connection.execute('SELECT rolname,rolsuper,rolcreaterole,rolcreatedb,rolbypassrls,rolreplication FROM pg_roles WHERE rolname=ANY(%s) ORDER BY rolname', (list(fixture.ROLES),)).fetchall()
        assert roles == [(role, False, False, False, False, False) for role in sorted(fixture.ROLES)]
    return fixture.retained_cluster_state(admin, value['database'])


def set_context(connection, account=ACCOUNT, actor=ACTOR, mode='own_write', org=ORG):
    connection.execute(text("SELECT set_config('app.org_id',:org,true), set_config('app.account_id',:account,true), "
                            "set_config('app.actor_id',:actor,true), set_config('app.mode',:mode,true)"),
                       dict(org=org, account=account, actor=actor, mode=mode))


def seed(connection):
    """Fixture administrator only: no Identity/Auth/access records or app grants."""
    definition = initial_definition(QUESTION_IDS)
    raw = json.dumps(definition.model_dump())
    connection.execute(text('INSERT INTO kdg_capture.questionnaire(id,org_id,created_by) VALUES(:id,:org,:actor)'),
                       dict(id=QUESTIONNAIRE, org=ORG, actor=ACTOR))
    connection.execute(text('INSERT INTO kdg_capture.questionnaire_version(id,org_id,questionnaire_id,display_version,definition,definition_hash,published_by) '
                            'VALUES(:id,:org,:questionnaire,1,CAST(:definition AS jsonb),:hash,:actor)'),
                       dict(id=VERSION, org=ORG, questionnaire=QUESTIONNAIRE, definition=raw,
                            hash=sha256(raw.encode()).hexdigest(), actor=ACTOR))
    newer_definition = initial_definition([f'{n:08x}-aaaa-4aaa-8aaa-{n:012x}' for n in range(13,17)])
    newer_raw = json.dumps(newer_definition.model_dump())
    connection.execute(text('INSERT INTO kdg_capture.questionnaire_version(id,org_id,questionnaire_id,display_version,definition,definition_hash,published_by) '
                            'VALUES(:id,:org,:questionnaire,2,CAST(:definition AS jsonb),:hash,:actor)'),
                       dict(id=str(uuid4()),org=ORG,questionnaire=QUESTIONNAIRE,definition=newer_raw,
                            hash=sha256(newer_raw.encode()).hexdigest(),actor=ACTOR))
    connection.execute(text("INSERT INTO kdg_capture.child(id,org_id,display_name,active,revision,created_by,updated_by) VALUES(:id,:org,'Synthetic child',true,1,:actor,:actor)"),
                       dict(id=CHILD, org=ORG, actor=ACTOR))
    connection.execute(text('INSERT INTO kdg_capture.child_assignment(id,org_id,child_id,account_id,membership_id,active,revision,created_by,updated_by) '
                            'VALUES(:id,:org,:child,:account,1,true,1,:actor,:actor)'),
                       dict(id=str(uuid4()), org=ORG, child=CHILD, account=OTHER_ACCOUNT, actor=ACTOR))
    for account in (ACCOUNT, OTHER_ACCOUNT):
        connection.execute(text("INSERT INTO kdg_capture.child_eligibility(org_id,ref,account_id,membership_id,child_id,child_revision,observed_active,create_permission,issued_by) "
                                "VALUES(:org,:ref,:account,1,:child,1,true,'kdg_capture.capture.create.all',:actor)"),
                           dict(org=ORG, ref=account, account=account, child=CHILD, actor=ACTOR))


CAPTURE_INSERT = '''INSERT INTO kdg_capture.capture
(id,org_id,child_id,questionnaire_id,questionnaire_version_id,owner_account_id,owner_actor_id,
child_eligibility_ref,creator_membership_id,observation_date,answers,captured_at,revision,created_by,updated_by)
VALUES(:capture,:org,:child,:questionnaire,:version,:account,:actor,:ref,1,:date,CAST(:answers AS jsonb),:device,1,:actor,:actor)'''
HISTORY_INSERT = '''INSERT INTO kdg_capture.capture_revision
(org_id,capture_id,revision,owner_account_id,owner_actor_id,child_id,questionnaire_id,questionnaire_version_id,
observation_date,answers,captured_at,executor_account_id,executor_actor_id,initiator_actor_id,outcome_id,command_type,operation_id)
SELECT c.org_id,c.id,c.revision,c.owner_account_id,c.owner_actor_id,c.child_id,c.questionnaire_id,c.questionnaire_version_id,
c.observation_date,c.answers,c.captured_at,:account,:actor,:initiator,:outcome,:command,:operation
FROM kdg_capture.capture c WHERE c.org_id=:org AND c.id=:capture'''


def append_receipt(connection, budget, context, capture, revision='1', command='capture.create', *, operation=None):
    operation, internal = operation or str(uuid4()), str(uuid4())
    key = write.OutcomeKey('kdg_capture', context.org_id, context.account_id, command, operation)
    write.outcome_lock(connection, budget, key, context)
    assert outcomes.lookup_private(connection, budget, key, context) is None
    receipt = dict(operation_id=operation, command_type=command, command_version=1,
                   status='committed', result=dict(capture_id=capture, revision=revision))
    outcomes.append(connection, budget, key, context, outcome_id=internal, receipt=receipt)
    return dict(org=context.org_id, account=context.account_id, actor=context.actor_id,
                initiator=context.actor_id, capture=capture, outcome=internal,
                command=command, operation=operation), key, receipt


def create_capture(connection, budget, context):
    capture = str(uuid4())
    answers = {QUESTION_IDS[0]: {'value': 1}, **{key: {'value': False} for key in QUESTION_IDS[1:]}}
    command = parse_create(json.dumps(dict(operation_id=str(uuid4()), command_version=1,
        capture_id=capture, child_id=CHILD, questionnaire_version_id=VERSION,
        observation_date='2026-10-24', answers=answers, captured_at='2026-10-24T10:11:12.123456789Z',
        child_eligibility_ref=context.account_id)))
    receipt = create.create_in_transaction(connection, budget, context, command,
        membership_id='1', permission=create.ALL).model_dump()
    key = write.OutcomeKey('kdg_capture', context.org_id, context.account_id,
                           'capture.create', command.operation_id)
    found = outcomes.lookup_private(connection, budget, key, context)
    assert found is not None
    parameters = dict(capture=capture, org=ORG, child=CHILD, questionnaire=QUESTIONNAIRE, version=VERSION,
                      account=context.account_id, actor=context.actor_id, ref=context.account_id,
                      date=date(2026,10,24), answers=json.dumps(answers), device=command.captured_at)
    evidence = dict(org=ORG, account=context.account_id, actor=context.actor_id,
                    initiator=context.actor_id, capture=capture, outcome=found.id,
                    command='capture.create', operation=command.operation_id)
    stored = connection.execute(text('SELECT observation_date,answers,captured_at,owner_account_id::text,owner_actor_id::text,created_by::text,updated_by::text,revision '
                                     'FROM kdg_capture.capture WHERE id=:id'), dict(id=capture)).one()
    assert tuple(stored) == (date.fromisoformat(command.observation_date), answers, command.captured_at,
                             context.account_id, context.actor_id, context.actor_id, context.actor_id, 1)
    assert connection.execute(text('SELECT questionnaire_version_id::text FROM kdg_capture.capture WHERE id=:id'),
                              dict(id=capture)).scalar_one() == VERSION
    assert connection.execute(text('SELECT count(*) FROM kdg_capture.questionnaire_version')).scalar_one() == 2
    history = connection.execute(text('SELECT observation_date,answers,captured_at,operation_id::text,outcome_id::text,executor_account_id::text,executor_actor_id::text,initiator_actor_id::text '
                                      'FROM kdg_capture.capture_revision WHERE capture_id=:id'), dict(id=capture)).one()
    assert tuple(history) == (date.fromisoformat(command.observation_date), answers, command.captured_at,
                              command.operation_id, evidence['outcome'], context.account_id, context.actor_id, context.actor_id)
    connection.execute(text('SET CONSTRAINTS ALL IMMEDIATE'))
    connection.execute(text('SET CONSTRAINTS ALL DEFERRED'))
    assert outcomes.lookup_private(connection, budget, key, context).receipt().model_dump() == receipt
    return parameters, evidence


def qualify_create_rules(connection, budget, context, passed):
    """Exercise the actual body, with each synthetic variation rolled back."""
    answers = {QUESTION_IDS[0]: {'value': 1}, **{key: {'value': False} for key in QUESTION_IDS[1:]}}
    def command(**changes):
        values = dict(operation_id=str(uuid4()), command_version=1, capture_id=str(uuid4()),
            child_id=CHILD, questionnaire_version_id=VERSION, observation_date='2026-10-24',
            captured_at='2026-10-24T10:11:12Z', child_eligibility_ref=context.account_id, answers=answers)
        values.update(changes)
        return parse_create(json.dumps(values))
    def counts():
        return tuple(connection.execute(text('SELECT count(*) FROM kdg_capture.' + table)).scalar_one()
                     for table in ('capture', 'operation_outcome', 'capture_revision'))
    baseline = counts()
    for name, expected, changes, member, permission, mutation in (
        ('create_rejects_missing_assignment', 'assignment_unavailable', {}, '1', create.ASSIGNED, None),
        ('create_rejects_old_membership_eligibility', 'child_eligibility_unavailable', {}, '2', create.ALL, None),
        ('create_rejects_foreign_eligibility', 'child_eligibility_unavailable', {'child_eligibility_ref': OTHER_ACCOUNT}, '1', create.ALL, None),
        ('create_rejects_missing_original_version', 'questionnaire_version_unavailable', {'questionnaire_version_id': str(uuid4())}, '1', create.ALL, None),
        ('create_rejects_invalid_original_answers', 'validation_failed', {'answers': {}}, '1', create.ALL, None),
        ('prior_active_child_create_after_inactivity', None, {}, '1', create.ALL,
         'UPDATE kdg_capture.child SET active=false,revision=2'),
        ('current_assignment_create', None, {}, '1', create.ASSIGNED,
         "UPDATE kdg_capture.child_assignment SET account_id='" + ACCOUNT + "'"),
        ('create_rejects_inactive_assignment', 'assignment_unavailable', {}, '1', create.ASSIGNED,
         "UPDATE kdg_capture.child_assignment SET account_id='" + ACCOUNT + "',active=false"),
        ('create_rejects_old_membership_assignment', 'assignment_unavailable', {}, '1', create.ASSIGNED,
         "UPDATE kdg_capture.child_assignment SET account_id='" + ACCOUNT + "',membership_id=2"),
    ):
        with connection.begin_nested() as case:
            if mutation:
                # Test-only alternate writer; model owner cooperation before mutation.
                create.child_lock(connection, budget, context, CHILD)
                connection.execute(text('SET LOCAL ROLE supabase_admin'))
                connection.execute(text(mutation))
                connection.execute(text('SET LOCAL ROLE kdg_capture_runtime'))
            try:
                create.create_in_transaction(connection, budget, context, command(**changes),
                    membership_id=member, permission=permission)
            except write.WriteError as error:
                assert expected is not None and str(error) == expected, 'unexpected_create_refusal'
                assert counts() == baseline, 'failed_create_left_writes'
            else:
                assert expected is None, 'expected_create_refusal_missing'
                connection.execute(text('SET CONSTRAINTS ALL IMMEDIATE'))
                assert counts() == tuple(value + 1 for value in baseline), 'create_linkage_missing'
            case.rollback()
        assert counts() == baseline
        passed(name)


    # A valid assigned observation remains historical evidence when CURRENT all
    # authority no longer needs that now-inactive assignment.
    with connection.begin_nested() as case:
        create.child_lock(connection,budget,context,CHILD)
        connection.execute(text('SET LOCAL ROLE supabase_admin'))
        connection.execute(text('UPDATE kdg_capture.child_assignment SET account_id=:account,active=false'),dict(account=ACCOUNT))
        connection.execute(text("INSERT INTO kdg_capture.child_eligibility(org_id,ref,account_id,membership_id,child_id,child_revision,observed_active,create_permission,assignment_id,assignment_revision,issued_by) "
            "SELECT org_id,'historical-assigned',account_id,membership_id,child_id,1,true,:permission,id,revision,:actor FROM kdg_capture.child_assignment"),
            dict(permission=create.ASSIGNED,actor=ACTOR))
        connection.execute(text('SET LOCAL ROLE kdg_capture_runtime'))
        create.create_in_transaction(connection,budget,context,command(child_eligibility_ref='historical-assigned'),membership_id='1',permission=create.ALL)
        connection.execute(text('SET CONSTRAINTS ALL IMMEDIATE'))
        assert counts() == tuple(value + 1 for value in baseline)
        case.rollback()
    assert counts() == baseline
    passed('historical_assigned_current_all_without_active_assignment')

    with connection.begin_nested() as case:
        second_child = str(uuid4())
        connection.execute(text('SET LOCAL ROLE supabase_admin'))
        connection.execute(text("INSERT INTO kdg_capture.child(id,org_id,display_name,active,revision,created_by,updated_by) VALUES(:id,:org,'Other synthetic child',true,1,:actor,:actor)"),
            dict(id=second_child,org=ORG,actor=ACTOR))
        connection.execute(text("INSERT INTO kdg_capture.child_eligibility(org_id,ref,account_id,membership_id,child_id,child_revision,observed_active,create_permission,issued_by) "
            "VALUES(:org,'other-child-ref',:account,1,:child,1,true,:permission,:actor)"),
            dict(org=ORG,account=ACCOUNT,child=second_child,permission=create.ALL,actor=ACTOR))
        connection.execute(text('SET LOCAL ROLE kdg_capture_runtime'))
        try:
            create.create_in_transaction(connection,budget,context,command(child_eligibility_ref='other-child-ref'),membership_id='1',permission=create.ALL)
        except write.WriteError as error:
            assert str(error) == 'child_eligibility_unavailable'
        else:
            raise AssertionError('wrong_child_eligibility_accepted')
        assert counts() == baseline
        case.rollback()
    passed('same_account_current_member_wrong_child_reference_refused')

    # Inject an actual native history-constraint failure AFTER capture+outcome SQL.
    bad_history = create.HISTORY_INSERT.replace(
        "CAST(:actor AS uuid),\nCAST(:outcome AS uuid)", "NULL,\nCAST(:outcome AS uuid)")
    assert bad_history != create.HISTORY_INSERT
    reached_history = []
    execute = write.execute
    def observe_history(conn, original_budget, statement, parameters=None):
        if statement == bad_history:
            assert counts() == (baseline[0]+1,baseline[1]+1,baseline[2]), 'required_pre_failure_inserts_missing'
            reached_history.append(True)
        return execute(conn,original_budget,statement,parameters)
    with patch.object(create,'HISTORY_INSERT',bad_history), patch.object(write,'execute',observe_history):
        state = expect_error(connection,
            lambda: create.create_in_transaction(connection,budget,context,command(),membership_id='1',permission=create.ALL),
            ('23514',),immediate=True)
    assert reached_history == [True], 'native_history_failure_not_executed'
    assert counts() == baseline, 'post_insert_failure_not_rolled_back'
    passed('native_history_failure_rolls_back_capture_and_outcome',state)


def expect_error(connection, action, expected, *, immediate=False):
    """Each negative case must fail with its expected SQLSTATE, then fully rollback."""
    with connection.begin_nested() as savepoint:
        action_completed = False
        try:
            action()
            action_completed = True
            connection.execute(text('SET CONSTRAINTS ALL IMMEDIATE'))
        except (SQLAlchemyError, write.WriteError) as error:
            code = sqlstate(error)
            savepoint.rollback()
            assert code in expected, f'unexpected_sqlstate:{code}'
            assert not (immediate and action_completed), 'expected_immediate_refusal_missing'
            return code
        savepoint.rollback()
        raise AssertionError('expected_database_refusal_missing')


def qualify():
    if not __debug__:
        raise RuntimeError('optimized_python_prohibited')
    import inspect_native
    value, original = fixture.load(FIXTURE)
    admin = fixture.administrator()
    before = inspect_current(value, admin)
    try:
        inspect_native.inspect(FIXTURE)
        historical_inspector = True
    except AssertionError:
        historical_inspector = False
    engine = create_engine(admin.set(database=value['database'], drivername='postgresql+psycopg'),
        poolclass=pool.NullPool, hide_parameters=True,
        connect_args=dict(connect_timeout=5, hostaddr='127.0.0.1', sslmode='disable',
                          gssencmode='disable', passfile='/dev/null'))
    cases = []
    def passed(name, state=None):
        cases.append(dict(case=name, sqlstate=state))
    body_error = None
    try:
        with engine.connect() as connection:
            budget = write.Budget()
            context = write.VerifiedContext(ORG, ACCOUNT, ACTOR, 'own_write', time.monotonic())
            try:
                with write.transaction(connection, budget, context):
                    connection.execute(text('SET LOCAL ROLE kdg_capture_migrator'))
                    with Operations.context(MigrationContext.configure(connection)):
                        candidate.upgrade()
                    passed('actual_candidate_ddl')
                    connection.execute(text('SET LOCAL ROLE supabase_admin'))
                    seed(connection)
                    connection.execute(text('SET LOCAL ROLE kdg_capture_runtime'))
                    identity = connection.execute(text('SELECT current_user,session_user')).one()
                    assert tuple(identity) == ('kdg_capture_runtime','supabase_admin')
                    passed('runtime_current_role_admin_session_explicit')
                    limits = connection.execute(text("SELECT EXTRACT(EPOCH FROM current_setting('statement_timeout')::interval), "
                        "EXTRACT(EPOCH FROM current_setting('lock_timeout')::interval), "
                        "EXTRACT(EPOCH FROM current_setting('transaction_timeout')::interval)")).one()
                    assert all(0 < observed <= cap for observed, cap in zip(limits, (5, 2, 10)))
                    passed('bounded_database_limits_installed')
                    # A second EXISTING restricted connection holds only a synthetic
                    # advisory key, no candidate table visibility or persistent write.
                    contested_child = str(uuid4())
                    with fixture.connect(make_url(value['urls']['runtime'])) as holder:
                        holder.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",
                            ('kdg_capture:child:v1:' + ORG + ':' + contested_child,))
                        state = expect_error(connection,
                            lambda: create.child_lock(connection, budget, context, contested_child),
                            ('55P03',), immediate=True)
                        holder.rollback()
                    passed('child_coordination_lock_wait_bounded_two_connections', state)
                    # Same restricted holder rolled back: acquisition must now succeed.
                    create.child_lock(connection,budget,context,contested_child)
                    passed('child_coordination_lock_released_after_holder_rollback')
                    qualify_create_rules(connection, budget, context, passed)
                    own, own_evidence = create_capture(connection, budget, context)
                    passed('capture_outcome_history_and_original_receipt')
                    passed('older_published_definition_persisted_despite_newer_version')
                    original_command = parse_create(json.dumps(dict(operation_id=own_evidence['operation'],
                        command_version=1,capture_id=str(uuid4()),child_id=str(uuid4()),questionnaire_version_id=str(uuid4()),
                        observation_date='2026-10-24',answers={},captured_at='2026-10-24T00:00:00Z',child_eligibility_ref='missing')))
                    try:
                        create.create_in_transaction(connection,budget,context,original_command,membership_id='1',permission=create.ALL)
                    except write.WriteError as error:
                        assert str(error) == 'operation_verification_unavailable'
                    else:
                        raise AssertionError('fresh_path_disclosed_or_overwrote_existing_outcome')
                    passed('existing_outcome_stops_before_incoming_semantics')
                    noop, _, _ = append_receipt(connection, budget, context, own['capture'], command='capture.edit')
                    connection.execute(text('SET CONSTRAINTS ALL IMMEDIATE'))
                    connection.execute(text('SET CONSTRAINTS ALL DEFERRED'))
                    assert connection.execute(text('SELECT count(*) FROM kdg_capture.capture_revision')).scalar_one() == 1
                    passed('noop_receipt_without_fake_history')
                    with connection.begin_nested() as edit_case:
                        changed_answers = json.loads(own['answers'])
                        changed_answers[QUESTION_IDS[0]] = {'value':5}
                        edit = parse_edit(json.dumps(dict(operation_id=str(uuid4()),command_version=1,
                            expected_revision='1',observation_date='2026-10-23',answers=changed_answers)))
                        definition = connection.execute(text('SELECT definition FROM kdg_capture.questionnaire_version WHERE id=:id'),dict(id=VERSION)).scalar_one()
                        validate_answers(edit,parse_definition(json.dumps(definition)))
                        changed = connection.execute(text('UPDATE kdg_capture.capture SET observation_date=:date,answers=CAST(:answers AS jsonb),revision=2 '
                                                          'WHERE id=:id AND revision=CAST(:expected AS bigint)'),
                            dict(id=own['capture'],expected=edit.expected_revision,date=date.fromisoformat(edit.observation_date),answers=json.dumps(changed_answers)))
                        assert changed.rowcount == 1
                        edited, edit_key, edit_receipt = append_receipt(connection,budget,context,own['capture'],'2','capture.edit',operation=edit.operation_id)
                        assert connection.execute(text(HISTORY_INSERT),edited).rowcount == 1
                        connection.execute(text('SET CONSTRAINTS ALL IMMEDIATE'))
                        record = connection.execute(text('SELECT revision,observation_date,answers,captured_at FROM kdg_capture.capture WHERE id=:id'),dict(id=own['capture'])).one()
                        assert tuple(record) == (2,date.fromisoformat(edit.observation_date),changed_answers,own['device'])
                        saved_history = connection.execute(text('SELECT observation_date,answers,operation_id::text,executor_actor_id::text FROM kdg_capture.capture_revision WHERE capture_id=:id AND revision=2'),dict(id=own['capture'])).one()
                        assert tuple(saved_history) == (date.fromisoformat(edit.observation_date),changed_answers,edit.operation_id,ACTOR)
                        assert outcomes.lookup_private(connection,budget,edit_key,context).receipt().model_dump() == edit_receipt
                        edit_case.rollback()
                    passed('valid_changed_edit_and_original_receipt')
                    def reject(name, action, expected=('23514',), *, immediate=False):
                        passed(name, expect_error(connection, action, expected, immediate=immediate))
                    reject('runtime_cannot_change_owner', lambda: connection.execute(text('UPDATE kdg_capture.capture SET owner_account_id=:other WHERE id=:capture'),dict(other=OTHER_ACCOUNT,capture=own['capture'])), ('42501',))
                    reject('runtime_cannot_mutate_outcome', lambda: connection.execute(text('UPDATE kdg_capture.operation_outcome SET result=result')), ('42501',))
                    reject('runtime_cannot_ddl', lambda: connection.execute(text('CREATE TABLE kdg_capture.forbidden(value int)')), ('42501',))
                    reject('invalid_device_hour', lambda: connection.execute(text(CAPTURE_INSERT), {**own,'capture':str(uuid4()),'device':'2026-10-24T24:00:00Z'}), immediate=True)
                    reject('capture_without_history', lambda: connection.execute(text(CAPTURE_INSERT), {**own,'capture':str(uuid4())}), ('23503','23514'))
                    reject('same_org_foreign_child', lambda: connection.execute(text(CAPTURE_INSERT), {**own,'capture':str(uuid4()),'child':str(uuid4())}), ('23503',))
                    reject('unknown_reported_revision', lambda: append_receipt(connection,budget,context,own['capture'],'999','capture.edit'), ('23503',))
                    set_context(connection, OTHER_ACCOUNT, OTHER_ACTOR)
                    other_context = write.VerifiedContext(ORG,OTHER_ACCOUNT,OTHER_ACTOR,'own_write',time.monotonic())
                    other, _ = create_capture(connection,budget,other_context)
                    set_context(connection)
                    assert connection.execute(text('SELECT count(*) FROM kdg_capture.capture')).scalar_one() == 1
                    assert connection.execute(text('SELECT count(*) FROM kdg_capture.capture_revision')).scalar_one() == 1
                    assert connection.execute(text('SELECT count(*) FROM kdg_capture.child_eligibility')).scalar_one() == 1
                    assert connection.execute(text('SELECT count(*) FROM kdg_capture.child_assignment')).scalar_one() == 0
                    passed('own_scope_hides_other_capture_history_eligibility_assignment')
                    reject('own_outcome_cannot_target_other_owner', lambda: append_receipt(connection,budget,context,other['capture'],command='capture.edit'), ('42501',))
                    set_context(connection,mode='all_read')
                    assert connection.execute(text('SELECT count(*) FROM kdg_capture.capture')).scalar_one() == 2
                    assert connection.execute(text('SELECT count(*) FROM kdg_capture.operation_outcome')).scalar_one() == 2
                    assert connection.execute(text('SELECT count(*) FROM kdg_capture.capture_revision')).scalar_one() == 2
                    assert connection.execute(text('SELECT count(*) FROM kdg_capture.child_eligibility')).scalar_one() == 1
                    assert connection.execute(text('SELECT count(*) FROM kdg_capture.child_assignment')).scalar_one() == 1
                    passed('all_read_keeps_outcomes_and_eligibility_caller_scoped')
                    reject('read_mode_cannot_insert', lambda: connection.execute(text(CAPTURE_INSERT),{**own,'capture':str(uuid4())}), ('42501',))
                    set_context(connection,mode='own_write',org=str(uuid4()))
                    assert connection.execute(text('SELECT count(*) FROM kdg_capture.capture')).scalar_one() == 0
                    for table in ('capture_revision','operation_outcome','child_eligibility','child_assignment','questionnaire','questionnaire_version','child'):
                        assert connection.execute(text(f'SELECT count(*) FROM kdg_capture.{table}')).scalar_one() == 0
                    passed('foreign_org_all_domain_tables_empty')
                    set_context(connection,mode='')
                    assert connection.execute(text('SELECT count(*) FROM kdg_capture.capture')).scalar_one() == 0
                    for table in ('capture_revision','operation_outcome','child_eligibility','child_assignment','questionnaire','questionnaire_version','child'):
                        assert connection.execute(text(f'SELECT count(*) FROM kdg_capture.{table}')).scalar_one() == 0
                    passed('missing_mode_all_domain_tables_empty')
                    set_context(connection)
                    connection.execute(text('SET LOCAL ROLE supabase_admin'))
                    reject('immutable_capture_guard_for_alternate_writer', lambda: connection.execute(text('UPDATE kdg_capture.capture SET owner_account_id=:other WHERE id=:capture'),dict(other=OTHER_ACCOUNT,capture=own['capture'])))
                    reject('immutable_history_for_alternate_writer', lambda: connection.execute(text('UPDATE kdg_capture.capture_revision SET answers=answers')))
                    reject('unicode_blank_child_name', lambda: connection.execute(text("INSERT INTO kdg_capture.child(id,org_id,display_name,active,revision,created_by,updated_by) VALUES(:id,:org,:name,true,1,:actor,:actor)"),dict(id=str(uuid4()),org=ORG,name='\t\u3000',actor=ACTOR)))
                    connection.execute(text('SET LOCAL ROLE kdg_capture_runtime'))
                    def bad_initiator():
                        connection.execute(text("UPDATE kdg_capture.capture SET observation_date=DATE '2026-10-23',revision=2 WHERE id=:id"),dict(id=own['capture']))
                        evidence,_,_=append_receipt(connection,budget,context,own['capture'],'2','capture.edit')
                        connection.execute(text(HISTORY_INSERT),{**evidence,'initiator':None})
                    reject('history_outcome_initiator_disagreement',bad_initiator, immediate=True)
                    def fabricated_history():
                        evidence,_,_=append_receipt(connection,budget,context,own['capture'],'2','capture.edit')
                        statement=HISTORY_INSERT.replace('c.org_id,c.id,c.revision,','c.org_id,c.id,2,')
                        connection.execute(text(statement),evidence)
                    reject('history_without_real_capture_transition',fabricated_history, immediate=True)
                    passed('forced_deferred_checks_executed')
                    raise RollbackQualification()
            except RollbackQualification:
                passed('outer_transaction_rolled_back')
    except Exception as error:
        body_error = error
    finally:
        try:
            engine.dispose()
        except Exception as error:
            if body_error is None:
                body_error = error
    after = None
    inspection_error = None
    try:
        after = inspect_current(value, admin)
    except Exception as error:
        inspection_error = error
    restored = inspection_error is None and before == after
    if body_error is not None:
        body_error.rollback_verified = restored
        raise body_error from None
    if inspection_error is not None:
        raise inspection_error from None
    try:
        inspect_native.inspect(FIXTURE)
        historical_after = True
    except AssertionError:
        historical_after = False
    assert restored, 'current_metadata_changed'
    passed('ledger_only_and_current_metadata_restored')
    return dict(qualified=True, rollback_only=True, cases=cases,
        historical_inspector_before_passed=historical_inspector,
        historical_inspector_after_passed=historical_after,
        historical_global_hash_matches=before == original['before'], current_metadata_sha256=before,
        role_identity={'current_user':'kdg_capture_runtime','session_user':'supabase_admin'},
        head='0001_kdg_foundation', durable_commit=False, concurrent_visibility=False,
        source_hashes={str(path.relative_to(ROOT)):sha256(path.read_bytes()).hexdigest() for path in (
            Path(__file__), Path(candidate.__file__), Path(outcomes.__file__), Path(write.__file__),
            Path(create.__file__),
            Path(fixture.__file__), Path(inspect_native.__file__),
            ROOT/'apps/kdg-capture/api/capture_commands.py', ROOT/'apps/kdg-capture/api/questionnaire.py',
            ROOT/'apps/kdg-capture/api/context.py')})


def main(argv=None):
    try:
        if (sys.argv[1:] if argv is None else argv) != ['--run']:
            raise ValueError('explicit_action_required')
        result = qualify()
        destination = FIXTURE.parent / ('capture-storage-' + uuid4().hex + '.json')
        fixture.write_private(destination, result)
        print(json.dumps(dict(qualified=True, rollback_only=True, cases=len(result['cases']), report=str(destination))))
        return 0
    except Exception as error:
        print(json.dumps(dict(qualified=False, error='kdg_native_storage_failed', sqlstate=sqlstate(error),
                              rollback_verified=getattr(error,'rollback_verified',False))), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
