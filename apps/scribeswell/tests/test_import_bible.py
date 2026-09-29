import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools' / 'py'))
from import_bible import BibleImporter


class Database:
    """In-memory owner repository; transport behavior is exercised against PostgreSQL."""
    def __init__(self, cap=1000):
        self.rows = {t: [] for t in ('book', 'chapter', 'verse', 'word', 'morpheme')}

    def read(self, table, *, columns='*', filters=None, in_filters=None, order=('id',)):
        rows = [r.copy() for r in self.rows[table] if all(r[k] == v for k, v in (filters or {}).items()) and all(r[k] in v for k, v in (in_filters or {}).items())]
        for key in reversed(order):
            rows.sort(key=lambda r: r[key])
        return rows

    def one(self, table, **kwargs):
        rows = self.read(table, **kwargs)
        return rows[0] if rows else None

    def upsert(self, table, pending, conflict):
        rows = self.rows[table]
        keys = conflict.split(',')
        for row in pending:
            old = next((r for r in rows if all(r[k] == row[k] for k in keys)), None)
            if old is None:
                rows.append({'id': len(rows) + 1, **row})
            else:
                old.update(row)

    def transaction(self):
        from contextlib import nullcontext
        return nullcontext()


def importer(db):
    obj = BibleImporter('', dry_run=True)
    obj.dry_run, obj.db = False, db
    return obj


def test_import_preserves_words_and_morphemes_past_server_row_limit():
    db = Database()
    source = [[[['אָב', '1', 'HNcmsa']] for _ in range(600)] for _ in range(2)]
    importer(db).import_book('Genesis', source)
    assert len(db.rows['word']) == 1200
    assert len(db.rows['morpheme']) == 1200


def test_invalid_word_fails_before_writes():
    db = Database()
    with pytest.raises(ValueError, match='Genesis 1:1'):
        importer(db).import_book('Genesis', [[[['', '1', 'HNcmsa']]]])
    assert not db.rows['chapter']


def test_dry_run_accepts_actual_list_format():
    obj = BibleImporter('', dry_run=True)
    obj.import_book('Genesis', [[[['אָב', '1', 'HNcmsa']]]])
    assert obj.stats['words'] == 1
    assert obj.stats['morphemes'] == 1


def test_repair_is_idempotent_and_audit_detects_lost_word():
    db = Database(cap=2)
    obj = importer(db)
    source = [[[['אָב', '1', 'HNcmsa'], ['אָב', '1', 'HNcmsa']]]]
    obj.import_book('Genesis', source)
    before = {t: [r.copy() for r in rows] for t, rows in db.rows.items()}
    obj.import_book('Genesis', source)
    assert db.rows == before
    obj.import_book('Genesis', source, verify_only=True)
    assert db.rows == before
    db.rows['word'].pop()
    with pytest.raises(RuntimeError, match='Genesis 1 words: missing 1'):
        obj.import_book('Genesis', source, verify_only=True)


def test_unknown_book_filter_fails_before_seed(tmp_path):
    import json
    source = tmp_path / 'source.json'
    source.write_text(json.dumps({'Genesis': [[[['אָב', '1', 'HNcmsa']]]]}))
    db = Database()
    with pytest.raises(ValueError, match='unavailable'):
        importer(db).run(source, only_book='typo')
    assert not any(db.rows.values())


def test_pagination_fails_on_incomplete_response():
    from pagination import fetch_all

    class Truncated:
        def range(self, start, end):
            return self

        def execute(self):
            return SimpleNamespace(data=[], count=4)

    with pytest.raises(RuntimeError, match='Incomplete query'):
        fetch_all(Truncated())
