"""PREPARED ONLY. No native collection or execution in this delivery.

Reuses the owning disposable publication fixture; existing fixture qualification
and explicit SCRIBESWELL_PUBLICATION_NATIVE=1 remain mandatory. Never KDG ports.
"""
import json
import os
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit,unquote,quote
from uuid import uuid4
import pytest
import psycopg
from alembic.config import Config
from alembic import command
from test_corpus_publish_native import native_database,closed,publication_source,operator,publish_closed_attempt,APP,CUSTODY
from test_owned_migrations import migration_url
from test_corpus_publication_input import encode
from database import Database
from services import bible_service


@pytest.fixture(autouse=True)
def compatible_publication_labels(monkeypatch):
 import test_corpus_publish_native as publication_fixture
 from passage_references import CATALOGUE_VERSION
 original=publication_fixture.body
 def compatible(*args,**kwargs):
  result=original(*args,**kwargs)
  if 'input' in result.get('payload',{}):result['payload']['input'].update(catalogue_version=CATALOGUE_VERSION,versification_id='oshb-hebrew-json-c2d8e9e5')
  return result
 monkeypatch.setattr(publication_fixture,'body',compatible)


def reader_upgrade(url,monkeypatch):
 monkeypatch.setenv('SCRIBESWELL_MIGRATION_DATABASE_URL',migration_url(url));config=Config(str(APP/'alembic.ini'))
 config.attributes.update(scribeswell_validation_profile='reader-evidence-v1',scribeswell_prepared_actor=CUSTODY)
 command.upgrade(config,'head');return config

def runtime_url(url):
 parsed=urlsplit(url);return urlunsplit(parsed._replace(netloc='scribeswell_runtime:'+quote(unquote(parsed.password or ''),safe='')+'@'+parsed.hostname+':'+str(parsed.port)))

def test_native_snapshot_publication_actual_words_and_private_metadata_denials(closed,publication_source,monkeypatch):
 admin,url,seal,_=closed
 assert urlsplit(url).port not in (55481,55482)
 with operator(url) as db:publish_closed_attempt(db,encode(seal),publication_source,operation_id=str(uuid4()))
 reader_upgrade(url,monkeypatch);reader_upgrade(url,monkeypatch)
 db=Database(runtime_url(url),'scribeswell_runtime');db.open()
 try:
  monkeypatch.setattr(bible_service,'get_database',lambda:db)
  verses=bible_service.get_verses('Gen',1).model_dump(mode='json')['data']
  assert all(v['anchor_evidence']['status']=='ready' for v in verses)
  with psycopg.connect(runtime_url(url)) as runtime:
   for table in ('corpus_manifest_header','corpus_manifest_verse','corpus_current_publication','current_corpus_publication','alembic_version'):
    assert not runtime.execute("SELECT has_table_privilege(current_user,%s,'SELECT')",('scribeswell.'+table,)).fetchone()[0]
   assert runtime.execute("SELECT has_function_privilege(current_user,'scribeswell.reader_verse_evidence(text,integer,integer)','EXECUTE')").fetchone()[0]
 finally:db.close()


def test_native_missing_optional_routine_keeps_public_text_and_savepoint_usable(native_database,monkeypatch):
 # Historical0003 fixture has no reader evidence routine; do not upgrade it here.
 admin,url=native_database
 db=Database(runtime_url(url),'scribeswell_runtime');db.open()
 try:
  with db.reader_snapshot():
   assert db.reader_publication('Gen',1,1) is None
   assert isinstance(db.read('book'),list)
 finally:db.close()


def test_native_reader_repeatable_snapshot_excludes_concurrent_word_change(closed,publication_source,monkeypatch):
 admin,url,seal,_=closed
 with operator(url) as connection:publish_closed_attempt(connection,encode(seal),publication_source,operation_id=str(uuid4()))
 reader_upgrade(url,monkeypatch)
 db=Database(runtime_url(url),'scribeswell_runtime');db.open()
 try:
  with db.reader_snapshot():
   before=db.read('word',filters={'verse_id':1},order=('position',))
   # Fixture owner may disable the dormant-enforcement guard only in a separately
   # controlled integration scenario; concurrent recovery alone retires proof.
   admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=false')
   admin.execute("UPDATE scribeswell.word SET surface_he='שונה' WHERE verse_id=1")
   assert db.reader_publication('Gen',1,1) is not None
   assert db.read('word',filters={'verse_id':1},order=('position',))==before
  with db.reader_snapshot():
   assert db.reader_publication('Gen',1,1) is None
   assert db.read('word',filters={'verse_id':1},order=('position',))!=before
 finally:db.close()

def test_native_reader_forward_failure_rolls_back_routine_grant_and_ledger_then_retries(native_database,monkeypatch):
 import tempfile,shutil
 from test_corpus_publish_native import upgrade
 admin,url=native_database;upgrade(url,monkeypatch)
 monkeypatch.setenv('SCRIBESWELL_MIGRATION_DATABASE_URL',migration_url(url))
 with tempfile.TemporaryDirectory(prefix='scribeswell-reader-failed-ddl-') as directory:
  history=Path(directory)/'history';shutil.copytree(APP/'migrations',history)
  migration=history/'versions/0005_reader_evidence.py'
  migration.write_text(migration.read_text().replace('def upgrade():op.execute(DDL)',"def upgrade():\n op.execute(DDL)\n raise RuntimeError('synthetic failure after reader DDL')"))
  config=Config(str(APP/'alembic.ini'));config.set_main_option('script_location',str(history));config.attributes['scribeswell_validation_profile']='reader-evidence-v1'
  with pytest.raises(Exception):command.upgrade(config,'head')
 assert admin.execute('SELECT version_num FROM scribeswell.alembic_version').fetchone()==('scribeswell_0004',)
 assert admin.execute("SELECT to_regprocedure('scribeswell.reader_verse_evidence(text,integer,integer)')").fetchone()==(None,)
 config=Config(str(APP/'alembic.ini'));config.attributes['scribeswell_validation_profile']='reader-evidence-v1';command.upgrade(config,'head');command.upgrade(config,'head')
 assert admin.execute('SELECT version_num FROM scribeswell.alembic_version').fetchone()==('scribeswell_0005',)
 for role in ('anon','authenticated','service_role','scribeswell_import'):
  assert not admin.execute("SELECT has_function_privilege(%s,'scribeswell.reader_verse_evidence(text,integer,integer)','EXECUTE')",(role,)).fetchone()[0]
