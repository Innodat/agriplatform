"""D4 guarded discard and compact outcome acceptance."""
import asyncio
from uuid import uuid4

import httpx
import pytest

from test_draft_context import ACCOUNT, ACTOR, EMPLOYEE, NOW, ORG, Access, Config, People

from main import create_app

DRAFT = str(uuid4())
OPERATION = str(uuid4())
PATH = f'/v1/organizations/{ORG}/drafts/{DRAFT}/discard'


class GuardedConfig(Config):
    async def guard(self, connection, prepared, budget, clock, deadline):
        from types import SimpleNamespace

        assert prepared.observation['status'] == 'effective'
        def check(checked_clock, checked_deadline):
            assert checked_clock() == clock() and checked_deadline == deadline

        return SimpleNamespace(check=check)


class Store:
    def __init__(self):
        self.calls = []

    async def discard(self, prepared, budget, draft, command, configuration, clock):
        from drafts import DiscardCommitted, DiscardResult

        self.calls.append((draft, command.model_dump()))
        return DiscardCommitted(
            operation_id=command.operation_id,
            status='committed',
            result=DiscardResult(command='discard', draft_id=draft, revision='2',
                                 scope_generation='1', disposition='discarded'),
        )


def request(store, payload):
    async def run():
        app = create_app(repository=object(), access=Access(), environment={}, people=People(),
                         configuration=Config(), clock=lambda: NOW, drafts=store)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://leave') as client:
            return await client.post(PATH, headers={'Authorization': 'Bearer synthetic'}, json=payload)

    return asyncio.run(run())


def test_discard_accepts_only_guard_and_operation_and_acknowledges_committed_outcome():
    store = Store()
    payload = {'operation_id': OPERATION, 'expected_revision': '1'}
    response = request(store, payload)
    assert response.status_code == 200
    assert response.headers['cache-control'] == 'private, no-store'
    assert response.json() == {
        'operation_id': OPERATION,
        'status': 'committed',
        'result': {'command': 'discard', 'draft_id': DRAFT, 'revision': '2',
                   'scope_generation': '1', 'disposition': 'discarded'},
    }
    assert store.calls == [(DRAFT, payload)]
    response = request(store, {**payload, 'input': {'note': 'must never be accepted'}})
    assert response.status_code == 422
    assert 'must never be accepted' not in response.text
    assert store.calls == [(DRAFT, payload)]


def discard_command(operation=OPERATION, revision='1'):
    return {'operation_id': operation, 'expected_revision': revision}


class Database:
    """Observe the real repository transaction with in-memory commit and fault injection."""

    def __init__(self):
        from drafts import empty_input

        self.rows = {DRAFT: {'id': DRAFT, 'revision': 1, 'state': 'active', 'input': empty_input()}}
        self.row['input']['note'] = 'Private unfinished input'
        self.generation = 0
        self.receipts = {}
        self.steps = []
        self.fail_at = None

    @property
    def row(self):
        return self.rows[DRAFT]

    async def connect(self, *args, **kwargs):
        from contextlib import asynccontextmanager
        from copy import deepcopy
        from types import SimpleNamespace

        db = self

        class Connection:
            pgconn = SimpleNamespace(finish=lambda: None)

            async def close(self):
                pass

            @asynccontextmanager
            async def transaction(self):
                self.writing = True
                self.rows = deepcopy(db.rows)
                self.generation = db.generation
                self.receipts = deepcopy(db.receipts)
                try:
                    yield
                    if self.writing and db.fail_at == 'before_commit':
                        raise RuntimeError('Private synthetic database error')
                    db.rows, db.generation, db.receipts = self.rows, self.generation, self.receipts
                    db.steps.append('commit')
                    if self.writing and db.fail_at == 'after_commit':
                        raise RuntimeError('Private synthetic lost commit response')
                except BaseException:
                    db.steps.append('error')
                    raise

            async def execute(self, sql, params=()):
                async def fetchone():
                    return value

                if sql == 'SET TRANSACTION READ ONLY':
                    self.writing = False
                if sql.startswith('SET TRANSACTION') or sql.startswith('SELECT set_config'):
                    return
                if sql.startswith('INSERT INTO leave.draft_scope'):
                    assert params == (ORG, EMPLOYEE)
                    return
                if sql.startswith('SELECT generation'):
                    db.steps.append('scope')
                    assert params == (ORG, EMPLOYEE)
                    value = {'generation': self.generation}
                elif sql.startswith('SELECT pg_advisory_xact_lock'):
                    db.steps.append('operation-lock')
                    assert params[0].startswith('leave.draft.operation.' + ORG + '.' + ACTOR + '.')
                    return
                elif sql.startswith('SELECT * FROM leave.operation_receipt'):
                    db.steps.append('receipt-read')
                    assert params[:2] == (ORG, ACTOR)
                    value = self.receipts.get(params[2])
                elif sql.startswith('SELECT id,revision,state'):
                    db.steps.append('target')
                    assert params[:2] == (ORG, EMPLOYEE)
                    value = self.rows.get(params[2])
                elif sql.startswith('SELECT id,revision FROM leave.draft'):
                    assert params == (ORG, EMPLOYEE)
                    value = next((row for row in self.rows.values() if row['state'] == 'active'), None)
                elif sql.startswith('INSERT INTO leave.draft('):
                    draft, org, employment, input_value = params
                    assert (org, employment) == (ORG, EMPLOYEE)
                    value = {'id': draft, 'state': 'active', 'revision': 1, 'input': input_value.obj}
                    self.rows[draft] = value
                elif sql.startswith("UPDATE leave.draft SET input=NULL,state='discarded',revision=revision+1"):
                    db.steps.append('discard')
                    assert params == (ORG, EMPLOYEE, DRAFT)
                    row = self.rows[params[2]]
                    row.update(input=None, state='discarded', revision=row['revision'] + 1)
                    value = {'revision': row['revision']}
                elif sql.startswith('UPDATE leave.draft SET input=%s,revision=revision+1'):
                    input_value, org, employment, draft = params
                    assert (org, employment) == (ORG, EMPLOYEE)
                    row = self.rows[draft]
                    row.update(input=input_value.obj, revision=row['revision'] + 1)
                    value = {'revision': row['revision']}
                elif sql.startswith('UPDATE leave.draft_scope SET generation=generation+1'):
                    db.steps.append('advance')
                    assert params == (ORG, EMPLOYEE)
                    self.generation += 1
                    value = {'generation': self.generation}
                elif sql.startswith('INSERT INTO leave.operation_receipt'):
                    db.steps.append('receipt-write')
                    if db.fail_at == 'receipt':
                        raise RuntimeError('Private synthetic evidence failure')
                    org, actor, operation, employment, draft = params[:5]
                    if ",'start',1," in sql:
                        kind = 'start'
                        fingerprint, revision, result, observation = params[5:]
                    else:
                        kind, fingerprint, revision, result, observation = params[5:]
                    assert (org, actor, employment) == (ORG, ACTOR, EMPLOYEE)
                    assert draft == result.obj['draft_id'] and kind == result.obj['command']
                    assert len(fingerprint) == 32
                    assert observation.obj['account_id'] == ACCOUNT
                    self.receipts[operation] = dict(command=kind, employment_id=employment, fingerprint=fingerprint,
                                                    command_version=1, fingerprint_algorithm='sha256-jcs-v1',
                                                    fingerprint_version=1, committed_revision=revision, result=result.obj)
                    return
                else:
                    raise AssertionError('unexpected command in discard transaction')
                return SimpleNamespace(fetchone=fetchone)

        return Connection()


@pytest.fixture
def database(monkeypatch):
    from drafts import DraftRepository

    db = Database()
    monkeypatch.setattr('drafts.psycopg.AsyncConnection.connect', db.connect)
    repository = DraftRepository('postgresql+psycopg://leave_runtime:synthetic@localhost/synthetic')
    return db, repository


def exercise(repository, actions, *, access=None, people=None):
    async def run():
        app = create_app(repository=object(), access=access or Access(), environment={}, people=people or People(),
                         configuration=GuardedConfig(), clock=lambda: NOW, drafts=repository)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://leave',
                                     headers={'Authorization': 'Bearer synthetic'}) as client:
            return [await action(client) for action in actions]

    return asyncio.run(run())


def post(command=None, path=PATH):
    return lambda client: client.post(path, json=command or discard_command())


def outcome(operation=OPERATION):
    return lambda client: client.get(f'/v1/organizations/{ORG}/operations/{operation}')


@pytest.mark.parametrize('failure', ['receipt', 'before_commit'])
def test_evidence_or_commit_failure_never_leaves_partial_discard(database, failure):
    db, repository = database
    db.fail_at = failure
    failed, missing = exercise(repository, [post(), outcome()])
    assert failed.status_code == 503 and failed.json()['error_id'] == 'outcome_unresolved'
    assert 'Private' not in failed.text
    assert missing.json() == {'operation_id': OPERATION, 'status': 'unresolved'}
    assert db.steps[:8] == ['scope', 'operation-lock', 'receipt-read', 'target',
                            'discard', 'advance', 'receipt-write', 'error']
    assert db.row['state'] == 'active' and db.row['input']['note'] == 'Private unfinished input'
    assert db.generation == 0 and db.row['revision'] == 1 and db.receipts == {}
    db.fail_at = None
    assert exercise(repository, [post()])[0].status_code == 200
    assert db.row['input'] is None and db.row['revision'] == 2 and db.generation == 1


def test_committed_lost_response_recovers_original_outcome_without_mutating_again(database):
    db, repository = database
    access = Access()
    db.fail_at = 'after_commit'
    failed = exercise(repository, [post()], access=access)[0]
    assert failed.status_code == 503 and failed.json()['error_id'] == 'outcome_unresolved'
    db.fail_at = None
    # Read authority is still required. Losing manage blocks a new discard, while an
    # already committed outcome remains visible to its currently authorized owner.
    access.manage = False
    recovered, replay = exercise(repository, [outcome(), post()], access=access)
    assert recovered.status_code == replay.status_code == 200
    assert replay.json() == recovered.json() == {
        'operation_id': OPERATION, 'status': 'committed',
        'result': {'command': 'discard', 'disposition': 'discarded', 'draft_id': DRAFT,
                   'revision': '2', 'scope_generation': '1'},
    }
    assert db.row == {'id': DRAFT, 'revision': 2, 'state': 'discarded', 'input': None}
    assert db.generation == 1 and list(db.receipts) == [OPERATION]
    assert db.steps.count('target') == db.steps.count('receipt-write') == 1
    access.error = (403, 'access_denied')
    for response in exercise(repository, [outcome(), post()], access=access):
        assert response.status_code == 403 and response.json()['details'] == {}


def test_fresh_conflict_terminal_and_mismatch_have_safe_scoped_details(database):
    db, repository = database
    stale, invisible, committed, mismatch, terminal = exercise(repository, [
        post(discard_command(revision='2')),
        post(path=f'/v1/organizations/{ORG}/drafts/{uuid4()}/discard'),
        post(),
        post(discard_command(revision='2')),
        post(discard_command(str(uuid4()), '2')),
    ])
    assert (stale.status_code, stale.json()['error_id'], stale.json()['details']) == (
        409, 'leave.draft_revision_conflict', {'current_revision': '1'},
    )
    assert (invisible.status_code, invisible.json()['error_id'], invisible.json()['details']) == (
        404, 'resource_not_found', {},
    )
    assert committed.status_code == 200
    assert (mismatch.status_code, mismatch.json()['error_id'], mismatch.json()['details']) == (
        409, 'operation_mismatch', {},
    )
    assert (terminal.status_code, terminal.json()['error_id'], terminal.json()['details']) == (
        409, 'leave.draft_discarded', {'draft_id': DRAFT},
    )
    assert db.steps.count('receipt-write') == 1


@pytest.mark.parametrize('case,status,identifier', [
    ('read_only', 403, 'access_denied'),
    ('missing_employment', 409, 'leave.setup_required'),
    ('authorization_revoked', 403, 'access_denied'),
])
def test_fresh_discard_requires_current_employee_preparation_and_manage(database, case, status, identifier):
    db, repository = database
    access, people = Access(), People()
    if case == 'read_only':
        access.manage = False
    elif case == 'missing_employment':
        people.missing = True
    else:
        access.error = (403, 'access_denied')
    response = exercise(repository, [post()], access=access, people=people)[0]
    assert response.status_code == status and response.json()['error_id'] == identifier
    assert db.row['state'] == 'active' and db.generation == 0 and db.receipts == {}
    assert 'discard' not in db.steps


def test_discard_fingerprint_binds_command_target_and_guard():
    from drafts import Discard, Save, discard_fingerprint, empty_input, save_fingerprint

    command = Discard.model_validate(discard_command())
    first = discard_fingerprint(ORG, ACTOR, EMPLOYEE, DRAFT, command)
    assert len(first) == 32 and first == discard_fingerprint(ORG, ACTOR, EMPLOYEE, DRAFT, command)
    assert first != discard_fingerprint(ORG, ACTOR, EMPLOYEE, str(uuid4()), command)
    newer = Discard.model_validate(discard_command(revision='2'))
    assert first != discard_fingerprint(ORG, ACTOR, EMPLOYEE, DRAFT, newer)
    save = Save.model_validate({**discard_command(), 'input': empty_input()})
    assert first != save_fingerprint(ORG, ACTOR, EMPLOYEE, DRAFT, save)



def test_old_operations_keep_their_original_outcome_after_a_fresh_empty_start(database):
    from drafts import empty_input

    db, repository = database
    starts = f'/v1/organizations/{ORG}/me/draft/start'
    saves = f'/v1/organizations/{ORG}/drafts/{DRAFT}/input'
    first_start = {'operation_id': str(uuid4()), 'expected_scope_generation': '0'}
    first_input = {**empty_input(), 'note': 'Saved once on the closed draft'}
    first_save = {**discard_command(str(uuid4())), 'input': first_input}
    first_discard = discard_command(revision='2')

    start = lambda value: lambda client: client.post(starts, json=value)
    save = lambda value: lambda client: client.put(saves, json=value)
    initial, saved, closed, late_save, outdated_start, replacement, resumed, *replayed = exercise(repository, [
        start(first_start), save(first_save), post(first_discard),
        save({**discard_command(str(uuid4()), '3'), 'input': first_input}),
        start({'operation_id': str(uuid4()), 'expected_scope_generation': '0'}),
        start({'operation_id': str(uuid4()), 'expected_scope_generation': '1'}),
        start({'operation_id': str(uuid4()), 'expected_scope_generation': '1'}),
        start(first_start), save(first_save), post(first_discard),
    ])

    assert initial.status_code == saved.status_code == closed.status_code == 200
    assert saved.json()['result']['revision'] == '2'
    assert closed.json()['result']['revision'] == '3'
    assert late_save.status_code == 409 and late_save.json()['error_id'] == 'leave.draft_discarded'
    assert outdated_start.status_code == 409 and outdated_start.json()['error_id'] == 'leave.draft_start_outdated'
    assert outdated_start.json()['details'] == {'current_scope_generation': '1'}
    assert replacement.status_code == resumed.status_code == 200
    next_draft = replacement.json()['result']['draft_id']
    assert next_draft != DRAFT
    assert replacement.json()['result']['disposition'] == 'created'
    assert resumed.json()['result'] == {**replacement.json()['result'], 'disposition': 'resumed'}
    assert [response.json() for response in replayed] == [response.json() for response in (initial, saved, closed)]
    assert db.row['input'] is None and db.row['revision'] == 3 and db.generation == 1
    assert db.rows[next_draft]['input'] == empty_input() and db.rows[next_draft]['revision'] == 1
    assert len(db.receipts) == 5
