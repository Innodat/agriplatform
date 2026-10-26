"""Closed audit adapter acceptance with repository doubles, never native authority proof."""
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import FrozenInstanceError
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
import closed_corpus_audit as auditor
from corpus_source import BOOK_METADATA
from corpus_publication import CommandReceipt, PublicationError
from test_corpus_publication_input import command, encode, source_bytes

ACTOR = '22222222-2222-4222-8222-222222222222'
REVISION = '33333333-3333-4333-8333-333333333333'


class Rows:
    def __init__(self, rows): self.rows = rows
    def fetchone(self): return self.rows[0] if self.rows else None
    def fetchall(self): return deepcopy(self.rows)


class NamedCursor:
    def __init__(self, db, name):
        self.db, self.name, self.offset = db, name, 0
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def execute(self, query, params):
        assert self.db.in_snapshot
        self.db.events.append(('scan', self.name))
    def fetchmany(self, count):
        rows = self.db.tables[self.name.removeprefix('audit_')]
        chunk = rows[self.offset:self.offset + count]
        self.offset += len(chunk)
        return deepcopy(chunk)


class Connection:
    def __init__(self, body):
        self.events, self.in_snapshot, self.row_factory = [], False, object()
        self.fail_exit, self.fail_scan = False, False
        self.visible = True
        payload = body['payload']
        self.observation = dict(enforcement=True, source_id='tanakh',
                                attempt_id=payload['expected_attempt_id'], generation=payload['expected_generation'],
                                input_sha256=payload['input']['source_sha256'], epoch_state='closed', attempt_state='closed',
                                **{k: payload['input'][k] for k in ('catalogue_version','versification_id','tokenization_version')},
                                executor_actor_id=ACTOR, principal_enabled=True, authority_enabled=True)
        self.tables = dict(book=deepcopy(BOOK_METADATA), chapter=[], verse=[], word=[])
        for n, book in enumerate(BOOK_METADATA, 1):
            self.tables['chapter'].append(dict(id=n, book_id=book['id'], chapter_num=1))
            self.tables['verse'].append(dict(id=n, chapter_id=n, book_id=book['id'], chapter_num=1, verse_num=1))
            self.tables['word'].append(dict(id=n, verse_id=n, position=1, surface_he='שָׁ/אָב'))

    @contextmanager
    def transaction(self):
        assert not self.in_snapshot
        self.in_snapshot = True
        self.events.append(('begin',))
        try:
            yield
            if self.fail_exit: raise RuntimeError('private-exit-marker')
        except Exception:
            self.events.append(('rollback',))
            raise
        else:
            self.events.append(('exit',))
        finally:
            self.in_snapshot = False

    def execute(self, query, params=None):
        assert self.in_snapshot
        assert 'FOR UPDATE' not in query and 'FOR SHARE' not in query
        self.events.append(('sql', query))
        if 'corpus_fence_control' in query:
            return Rows([] if self.observation is None else [deepcopy(self.observation)])
        if 'row_security_active' in query:
            return Rows([dict(name=table, base_table=True, visible=self.visible)
                         for table in ('book','chapter','verse','word')])
        return Rows([])

    def cursor(self, *, name):
        if self.fail_scan: raise RuntimeError('private-scan-marker')
        return NamedCursor(self, name)


def setup(monkeypatch):
    body = command('seal')
    connection = Connection(body)
    receipt = CommandReceipt(1, body['operation_id'], 'corpus.seal', 'tanakh', ACTOR,
                             body['payload']['expected_attempt_id'], body['payload']['expected_generation'], 'closed')
    # Type guard is separately tested; doubles model execution order, not native login permissions.
    monkeypatch.setattr(auditor, '_idle', lambda db: connection.events.append(('idle',)))
    def lookup(db, raw):
        assert not db.in_snapshot
        assert raw == encode(body)
        db.events.append(('lookup',))
        return receipt
    monkeypatch.setattr(auditor, 'lookup_outcome', lookup)
    return body, connection


def run(body, connection):
    return auditor.audit_closed_attempt(connection, encode(body), source_bytes(), source_revision=REVISION)


def test_complete_closed_audit_uses_one_snapshot_and_returns_unpublished_immutable_candidate(monkeypatch):
    body, db = setup(monkeypatch)
    factory, original = db.row_factory, deepcopy(db.tables)
    result = run(body, db)
    assert result.publication is False and len(result.verses) == 39
    assert result.attempt_id == body['payload']['expected_attempt_id']
    assert result.generation == int(body['payload']['expected_generation'])
    assert result.source_revision == REVISION and result.executor_actor_id == ACTOR
    assert result.verses[0].observed_word_ids == ('1',)
    assert db.events[0:3] == [('idle',), ('lookup',), ('begin',)]
    assert db.events[-1] == ('exit',)
    assert [e[1] for e in db.events if e[0]=='scan'] == ['audit_book','audit_chapter','audit_verse','audit_word']
    assert any('REPEATABLE READ READ ONLY' in e[1] for e in db.events if e[0]=='sql')
    assert db.row_factory is factory and db.tables == original and not db.in_snapshot
    with pytest.raises(FrozenInstanceError): result.source_revision = ACTOR


@pytest.mark.parametrize('field,value', [('attempt_id', REVISION), ('generation','1'), ('source_id','other'),
                                        ('input_sha256','0'*64), ('epoch_state','updating'), ('attempt_state','retired'),
                                        ('catalogue_version','other'), ('versification_id','other'),
                                        ('tokenization_version','other'), ('executor_actor_id',REVISION)])
def test_changed_closed_identity_never_scans_or_returns_candidate(monkeypatch, field, value):
    body, db = setup(monkeypatch)
    db.observation[field] = value
    factory = db.row_factory
    with pytest.raises(auditor.ClosedAuditError, match='closed_corpus_audit.conflict'):
        run(body, db)
    assert not any(e[0]=='scan' for e in db.events)
    assert ('rollback',) in db.events and db.row_factory is factory


@pytest.mark.parametrize('field,code', [('enforcement','unavailable'), ('principal_enabled','access_denied'),
                                      ('authority_enabled','access_denied')])
def test_disabled_gate_or_authority_denies_before_full_scan(monkeypatch, field, code):
    body, db = setup(monkeypatch)
    db.observation[field] = False
    with pytest.raises(auditor.ClosedAuditError, match='closed_corpus_audit.'+code): run(body, db)
    assert not any(e[0]=='scan' for e in db.events)


@pytest.mark.parametrize('change', ['missing_gate','hidden','missing_word','changed_surface','duplicate_id','scan_failure','exit_failure'])
def test_missing_inconsistent_or_failed_snapshot_returns_no_proof(monkeypatch, change):
    body, db = setup(monkeypatch)
    if change == 'missing_gate': db.observation = None
    elif change == 'hidden': db.visible = False
    elif change == 'missing_word': db.tables['word'].pop()
    elif change == 'changed_surface': db.tables['word'][0]['surface_he'] = 'אחר'
    elif change == 'duplicate_id': db.tables['word'][1]['id'] = 1
    elif change == 'scan_failure': db.fail_scan = True
    else: db.fail_exit = True
    factory = db.row_factory
    expected = 'corpus_mismatch' if change in ('missing_word','changed_surface','duplicate_id') else 'unavailable'
    with pytest.raises(auditor.ClosedAuditError) as failure: run(body, db)
    assert failure.value.code == 'closed_corpus_audit.' + expected
    assert 'private-' not in str(failure.value)
    assert failure.value.__context__ is None
    assert db.row_factory is factory and not db.in_snapshot


def test_regenerated_ids_preserve_exact_full_verse_digest(monkeypatch):
    body, db = setup(monkeypatch)
    first = run(body, db)
    for row in db.tables['word']: row['id'] += 1000
    second = run(body, db)
    assert second.verses[0].verse_token_digest == first.verses[0].verse_token_digest
    assert second.verses[0].observed_word_ids == ('1001',)


@pytest.mark.parametrize('change', ['begin','bad_revision','bad_source','missing_receipt','denied_lookup'])
def test_invalid_input_or_unreconciled_seal_does_not_open_snapshot(monkeypatch, change):
    body, db = setup(monkeypatch)
    raw, source, revision = encode(body), source_bytes(), REVISION
    if change == 'begin': raw = encode(command('begin'))
    elif change == 'bad_revision': revision = 'invalid'
    elif change == 'bad_source': source += b' '
    elif change == 'missing_receipt': monkeypatch.setattr(auditor, 'lookup_outcome', lambda *args: None)
    else:
        def denied(*args): raise PublicationError('access_denied')
        monkeypatch.setattr(auditor, 'lookup_outcome', denied)
    with pytest.raises(auditor.ClosedAuditError):
        auditor.audit_closed_attempt(db, raw, source, source_revision=revision)
    assert ('begin',) not in db.events


def test_nonconnection_is_rejected_without_sql():
    with pytest.raises(auditor.ClosedAuditError):
        auditor.audit_closed_attempt(object(), encode(command('seal')), source_bytes(), source_revision=REVISION)


@pytest.mark.parametrize('phase', ['preflight','scan','assembly'])
def test_total_deadline_cannot_return_late_candidate(monkeypatch, phase):
    body, db = setup(monkeypatch)
    clock = [0.0]
    monkeypatch.setattr(auditor.time, 'monotonic', lambda: clock[0])
    name = {'preflight':'build_source_candidate', 'scan':'_compare', 'assembly':'build_manifest_candidate'}[phase]
    original = getattr(auditor, name)
    def delayed(*args, **kwargs):
        result = original(*args, **kwargs)
        clock[0] = auditor.WORKFLOW_SECONDS + 1
        return result
    monkeypatch.setattr(auditor, name, delayed)
    factory = db.row_factory
    with pytest.raises(auditor.ClosedAuditError, match='closed_corpus_audit.deadline_exceeded'):
        run(body, db)
    assert db.row_factory is factory and not db.in_snapshot
    if phase == 'preflight': assert ('lookup',) not in db.events
    elif phase == 'scan': assert ('rollback',) in db.events
    else: assert ('exit',) in db.events


def test_read_grant_failure_is_safe_and_restores_caller(monkeypatch):
    body, db = setup(monkeypatch)
    original, factory = db.execute, db.row_factory
    class Denied(RuntimeError):
        sqlstate = '42501'
    def denied(query, params=None):
        if 'corpus_fence_control' in query: raise Denied('private-credentials-marker')
        return original(query, params)
    db.execute = denied
    with pytest.raises(auditor.ClosedAuditError, match='closed_corpus_audit.access_denied') as failure:
        run(body, db)
    assert failure.value.__context__ is None
    assert db.row_factory is factory and ('rollback',) in db.events


@pytest.mark.parametrize('caller_factory', ['dict','custom'])
def test_actual_controller_lookup_normalizes_and_restores_caller_factory(monkeypatch, caller_factory):
    from dataclasses import asdict
    from psycopg.rows import dict_row, tuple_row
    import corpus_publication as controller
    body, db = setup(monkeypatch)
    factory = dict_row if caller_factory == 'dict' else object()
    db.row_factory = factory
    receipt = CommandReceipt(1, body['operation_id'], 'corpus.seal', 'tanakh', ACTOR,
                             body['payload']['expected_attempt_id'], body['payload']['expected_generation'], 'closed')
    monkeypatch.setattr(controller, '_idle', lambda connection: None)
    monkeypatch.setattr(auditor, 'lookup_outcome', controller.lookup_outcome)
    original = db.execute
    def execute(query, params=None):
        if 'lookup_corpus_command_outcome' in query:
            payload = asdict(receipt)
            return Rows([(payload,)] if db.row_factory is tuple_row else [{'result':payload}])
        return original(query, params)
    db.execute = execute
    result = run(body, db)
    assert len(result.verses) == 39 and db.row_factory is factory


def test_late_receipt_reconciliation_does_not_open_audit_snapshot(monkeypatch):
    body, db = setup(monkeypatch)
    clock = [0.0]
    monkeypatch.setattr(auditor.time, 'monotonic', lambda: clock[0])
    original, factory = auditor.lookup_outcome, db.row_factory
    def delayed(*args):
        receipt = original(*args)
        clock[0] = auditor.WORKFLOW_SECONDS + 1
        return receipt
    monkeypatch.setattr(auditor, 'lookup_outcome', delayed)
    with pytest.raises(auditor.ClosedAuditError, match='closed_corpus_audit.deadline_exceeded'):
        run(body, db)
    assert ('lookup',) in db.events and ('begin',) not in db.events
    assert db.row_factory is factory


def test_lookup_failure_restores_factory_before_raising(monkeypatch):
    from psycopg.rows import tuple_row
    body, db = setup(monkeypatch)
    factory = db.row_factory
    def denied(connection, raw):
        assert connection.row_factory is tuple_row
        raise PublicationError('access_denied')
    monkeypatch.setattr(auditor, 'lookup_outcome', denied)
    with pytest.raises(auditor.ClosedAuditError, match='closed_corpus_audit.access_denied'):
        run(body, db)
    assert db.row_factory is factory and ('begin',) not in db.events
