import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
os.environ.setdefault('SUPABASE_URL', 'http://localhost:54321')
os.environ.setdefault('SUPABASE_SECRET_KEY', 'test-key')
from main import app
from test_import_bible import Database

from services import bible_service


def database(words):
    db = Database(cap=3)
    db.rows['book_read'] = [{'id': 27, 'osis_id': 'Ps'}]
    db.rows['verse_read'] = [{'id': 1, 'verse_num': 1, 'book_id': 27, 'chapter_num': 23}]
    db.rows['word_read'] = words
    return db


def test_empty_stored_verse_is_visible_http_failure(monkeypatch):
    monkeypatch.setattr(bible_service, 'get_database', lambda: database([]))
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get('/api/bible/books/Ps/chapters/23/verses')
    assert response.status_code == 503
    assert 'Ps 23:1' in response.json()['error']


def test_reader_fetches_all_word_pages(monkeypatch):
    words = [{'id': i, 'verse_id': 1, 'position': i, 'surface_he': 'אָב', 'display_he': 'אָב',
              'lemma_strong': '1', 'morph_code': 'HNcmsa'} for i in range(1, 8)]
    monkeypatch.setattr(bible_service, 'get_database', lambda: database(words))
    assert len(bible_service.get_verses('Ps', 23).data[0].words) == 7
