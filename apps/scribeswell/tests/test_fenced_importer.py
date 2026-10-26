"""Application-side fence binding; doubles do not qualify database enforcement."""
from contextlib import contextmanager
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/py'))
from import_bible import BibleImporter, ImportBinding, ImportBindingError
from corpus_source import BOOK_METADATA
from test_import_bible import Database


ATTEMPT = '10000000-0000-4000-8000-000000000001'


def source_file(tmp_path):
    data = {b['name_en']: [[[['אָב', '1', 'HNcmsa']]]] for b in BOOK_METADATA}
    data['Genesis'].append([[['בֵּן', '1', 'HNcmsa']]])
    path = tmp_path / 'source.json'
    path.write_text(json.dumps(data, ensure_ascii=False))
    return path


def binding(path, **changes):
    return ImportBinding(**dict(source_id='fixture', attempt_id=ATTEMPT, generation='7',
                                input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), **changes))


class FencedDatabase(Database):
    def __init__(self, reject_bind=None):
        super().__init__()
        self.events, self.active, self.bound, self.serial = [], False, False, 0
        self.reject_bind = reject_bind

    @contextmanager
    def transaction(self):
        assert not self.active
        self.active, self.bound = True, False
        self.serial += 1
        before = deepcopy(self.rows)
        self.events.append(('begin', self.serial))
        try:
            yield
        except Exception:
            self.rows = before
            self.events.append(('rollback', self.serial))
            raise
        else:
            self.events.append(('commit', self.serial))
        finally:
            self.active, self.bound = False, False

    @contextmanager
    def connection(self):
        assert self.active
        yield self

    def execute(self, query, values):
        assert self.active
        assert query == 'SELECT scribeswell.bind_corpus_write(%s,%s,%s,%s)'
        self.events.append(('bind', self.serial, values))
        if self.serial == self.reject_bind:
            raise RuntimeError('fixture rejected stale attempt')
        self.bound = True

    def upsert(self, *args):
        assert self.active and self.bound, 'write preceded transaction binding'
        self.events.append(('write', self.serial, args[0]))
        return super().upsert(*args)


def importer(path, db):
    obj = BibleImporter('', dry_run=True, binding=binding(path))
    obj.dry_run, obj.db = False, db
    return obj


def test_seed_and_every_chapter_bind_same_transaction_before_writes(tmp_path):
    path, db = source_file(tmp_path), FencedDatabase()
    obj = importer(path, db)
    obj.run(path, only_book='Gen')
    binds = [e for e in db.events if e[0] == 'bind']
    assert [e[1] for e in binds] == [1, 2, 3]
    assert all(e[2] == ('fixture', 7, ATTEMPT, obj.binding.input_sha256) for e in binds)
    assert len(db.rows['chapter']) == 2
    assert all(db.events.index(('begin', n)) < db.events.index(next(e for e in binds if e[1] == n))
               for n in (1, 2, 3))


@pytest.mark.parametrize('reject', [1, 2, 3])
def test_rejected_binding_aborts_without_unbound_continuation(tmp_path, reject):
    path, db = source_file(tmp_path), FencedDatabase(reject_bind=reject)
    with pytest.raises(RuntimeError, match='stale attempt'):
        importer(path, db).run(path, only_book='Gen')
    assert ('rollback', reject) in db.events
    assert not any(e[0] == 'write' and e[1] == reject for e in db.events)
    assert not any(e[1] > reject for e in db.events)
    assert len(db.rows['chapter']) == max(0, reject - 2)


@pytest.mark.parametrize('change', ['checksum', 'partial', 'invalid_other_book'])
def test_fenced_partial_repair_qualifies_complete_exact_artifact_before_writes(tmp_path, change):
    path, db = source_file(tmp_path), FencedDatabase()
    obj = importer(path, db)
    data = json.loads(path.read_bytes())
    if change == 'checksum': path.write_bytes(path.read_bytes() + b' ')
    elif change == 'partial':
        data.pop('Exodus')
        path.write_text(json.dumps(data))
        obj.binding = binding(path)
    else:
        data['Exodus'] = [[[['', '1', 'HNcmsa']]]]
        path.write_text(json.dumps(data))
        obj.binding = binding(path)
    with pytest.raises((ImportBindingError, ValueError)):
        obj.run(path, only_book='Gen')
    assert db.events == [] and not any(db.rows.values())


def test_direct_write_entry_points_cannot_skip_source_qualification(tmp_path):
    path, db = source_file(tmp_path), FencedDatabase()
    obj = importer(path, db)
    for action in (obj.seed_books, lambda: obj.import_book('Genesis', [[[['אָב', '1', 'HNcmsa']]]])):
        with pytest.raises(ImportBindingError):
            action()
    assert db.events == []


def test_dry_run_never_binds(tmp_path):
    path = source_file(tmp_path)
    obj = BibleImporter('', dry_run=True, binding=binding(path))
    obj.run(path, only_book='Gen')
    assert obj.db is None and obj.stats['words'] == 2


@pytest.mark.parametrize('field,value', [('source_id', ''), ('attempt_id', 'bad'),
                                       ('generation', True), ('generation', '01'),
                                       ('generation', str(2 ** 63)), ('input_sha256', 'BAD')])
def test_binding_rejects_malformed_identity(tmp_path, field, value):
    path = source_file(tmp_path)
    values = dict(source_id='fixture', attempt_id=ATTEMPT, generation='7',
                  input_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    values[field] = value
    with pytest.raises(ImportBindingError):
        ImportBinding(**values)


def test_verification_does_not_bind_or_write(tmp_path):
    path, db = source_file(tmp_path), FencedDatabase()
    obj = importer(path, db)
    obj.run(path, only_book='Gen')
    before = deepcopy(db.rows)
    db.events.clear()
    obj.run(path, only_book='Gen', verify_only=True)
    assert db.rows == before
    assert not any(e[0] in ('bind', 'write') for e in db.events)


def test_import_and_report_use_one_approved_source_read(tmp_path, capsys):
    path, db = source_file(tmp_path), FencedDatabase()
    obj = importer(path, db)
    approved = path.read_bytes()
    original_seed = obj.seed_books
    def seed_then_change_source():
        original_seed()
        path.write_text('{}')
    obj.seed_books = seed_then_change_source
    obj.run(path, only_book='Gen')
    report = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert report['source_sha256'] == hashlib.sha256(approved).hexdigest()
    assert len(db.rows['chapter']) == 2 and len(db.rows['word']) == 2
    assert not obj._run_active
    with pytest.raises(ImportBindingError):
        obj.import_book('Genesis', [[[['אָב', '1', 'HNcmsa']]]])


def test_failed_run_clears_qualification(tmp_path):
    path, db = source_file(tmp_path), FencedDatabase(reject_bind=2)
    obj = importer(path, db)
    with pytest.raises(RuntimeError):
        obj.run(path, only_book='Gen')
    assert not obj._run_active
    with pytest.raises(ImportBindingError):
        obj.seed_books()


@pytest.mark.parametrize('case', ['duplicate_key', 'oversize'])
def test_bad_artifact_is_rejected_before_transaction(tmp_path, monkeypatch, case):
    path, db = source_file(tmp_path), FencedDatabase()
    if case == 'duplicate_key':
        raw = path.read_bytes()
        path.write_bytes(raw[:-1] + b',"Genesis":[]}')
    else:
        import import_bible
        monkeypatch.setattr(import_bible, 'MAX_SOURCE_BYTES', 8)
    with pytest.raises(ImportBindingError):
        importer(path, db).run(path, only_book='Gen')
    assert not db.events


def test_cli_accepts_complete_binding_and_refuses_partial_options(tmp_path):
    import subprocess
    path = source_file(tmp_path)
    cli = Path(__file__).resolve().parents[1] / 'tools/py/import_bible.py'
    base = [sys.executable, str(cli), '--source', str(path), '--dry-run', '--book', 'Gen']
    options = ['--source-id', 'fixture', '--attempt-id', ATTEMPT,
               '--generation', '7', '--expected-source-sha256', binding(path).input_sha256]
    complete = subprocess.run(base + options, capture_output=True, text=True)
    assert complete.returncode == 0, complete.stderr
    assert json.loads(complete.stdout.splitlines()[-1])['counts']['words'] == 2
    for omit in range(4):
        partial = subprocess.run(base + options[:omit*2] + options[omit*2+2:], capture_output=True, text=True)
        assert partial.returncode == 2
        assert 'required together' in partial.stderr
        assert partial.stdout == ''


@pytest.mark.parametrize('change', ['chapters', 'verses', 'tokens', 'surface', 'strong'])
def test_fenced_preflight_uses_full_source_qualification_bounds(tmp_path, change):
    path = source_file(tmp_path)
    data = json.loads(path.read_bytes())
    word = ['אָב', '1', 'HNcmsa']
    if change == 'chapters': data['Exodus'] = [[[word]]] * 151
    elif change == 'verses': data['Exodus'] = [[[word]] * 177]
    elif change == 'tokens': data['Exodus'] = [[ [word] * 513 ]]
    elif change == 'surface': data['Exodus'] = [[[['א' * 1025, '1', 'HNcmsa']]]]
    else: data['Exodus'] = [[[['אָב', '1' * 2049, 'HNcmsa']]]]
    path.write_text(json.dumps(data, ensure_ascii=False))
    obj = BibleImporter('', dry_run=True, binding=binding(path))
    with pytest.raises(ImportBindingError):
        obj.run(path, only_book='Gen')


def test_fenced_cli_invalid_source_never_exposes_morphology(tmp_path):
    import subprocess
    path = source_file(tmp_path)
    data = json.loads(path.read_bytes())
    data['Exodus'][0][0][0][2] = 'HZPRIVATE_MARKER'
    path.write_text(json.dumps(data))
    cli = Path(__file__).resolve().parents[1] / 'tools/py/import_bible.py'
    result = subprocess.run([sys.executable, str(cli), '--source', str(path), '--dry-run',
                             '--book', 'Gen', '--source-id', 'fixture', '--attempt-id', ATTEMPT,
                             '--generation', '7', '--expected-source-sha256', binding(path).input_sha256],
                            capture_output=True, text=True)
    assert result.returncode == 1
    assert 'PRIVATE_MARKER' not in result.stderr + result.stdout
    assert result.stderr.strip() == 'Import failed: approved source or attempt binding is invalid'


def test_late_chapter_write_failure_rolls_back_only_that_chapter(tmp_path):
    path, db = source_file(tmp_path), FencedDatabase()
    obj = importer(path, db)
    original = db.upsert
    def fail_after_upsert(table, rows, conflict):
        original(table, rows, conflict)
        if db.serial == 3 and table == 'morpheme':
            raise RuntimeError('fixture late write failure')
    db.upsert = fail_after_upsert
    with pytest.raises(RuntimeError, match='late write failure'):
        obj.run(path, only_book='Gen')
    assert ('commit', 2) in db.events and ('rollback', 3) in db.events
    assert any(e == ('write', 3, 'morpheme') for e in db.events)
    assert len(db.rows['book']) == 39
    assert [c['chapter_num'] for c in db.rows['chapter']] == [1]
    assert len(db.rows['verse']) == len(db.rows['word']) == len(db.rows['morpheme']) == 1
    assert not obj._run_active


def test_actual_repository_wrapper_reuses_bound_transaction_connection(tmp_path):
    from contextvars import ContextVar
    from database import Database as Repository
    from contextlib import nullcontext
    events, leases = [], []
    class Connection:
        def transaction(self): return nullcontext()
        def execute(self, query, params):
            assert query == 'SELECT scribeswell.bind_corpus_write(%s,%s,%s,%s)'
            events.append(('bind', self))
        def cursor(self): return nullcontext(self)
        def executemany(self, query, params):
            assert query.as_string().startswith('INSERT INTO scribeswell."book"')
            assert len(params) == 39
            events.append(('write', self))
    class Pool:
        @contextmanager
        def connection(self):
            connection = Connection()
            leases.append(connection)
            yield connection
    db = Repository.__new__(Repository)
    db.pool, db._connection = Pool(), ContextVar('fenced-importer-test-connection', default=None)
    obj = importer(source_file(tmp_path), db)
    obj._run_active = True
    obj.seed_books()
    assert len(leases) == 1
    assert events == [('bind', leases[0]), ('write', leases[0])]
    assert db._connection.get() is None
