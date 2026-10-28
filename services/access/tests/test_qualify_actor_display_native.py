"""Focused source/ledger safeguards; native authority behavior stays in qualifier."""
from contextlib import contextmanager
import importlib.util
import json
from pathlib import Path

import pytest

SPEC=importlib.util.spec_from_file_location('actor_native_qualifier',Path(__file__).with_name('qualify_actor_display_native.py'))
qualifier=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(qualifier)


def source(root,head):
    access=root/'services/access'
    versions=access/'identity-migrations/versions';versions.mkdir(parents=True)
    (versions/'0027.py').write_text("revision='identity_0027'\ndown_revision=None\n")
    if head==28:
        (versions/'0028.py').write_text("revision='identity_0028'\ndown_revision='identity_0027'\n")
    (access/'identity-alembic.ini').write_text('[alembic]\n')
    (access/'tools').mkdir();(access/'tools/identity_bridge.sql').write_text('')
    return root


def test_prepare27_refuses_current28_sources_before_any_resource_start(tmp_path,monkeypatch):
    root=source(tmp_path/'root',28);proof=tmp_path/'proof';calls=[]
    monkeypatch.setattr(qualifier,'ROOT',root)
    monkeypatch.setattr(qualifier,'PREDECESSOR_FRAME',None)
    monkeypatch.setattr(qualifier,'command',lambda *args,**kwargs:calls.append(args))
    with pytest.raises(AssertionError,match='captured_predecessor_head_must_be27'):
        qualifier.prepare27(proof)
    assert calls==[] and not (proof/'private.json').exists()
    assert not (proof/'predecessor27.json').exists()
    assert (proof/'captured27-sources.json').is_file()


def test_qualified27_source_head_is_accepted(tmp_path):
    qualifier.require_source27(source(tmp_path,27))


@pytest.mark.parametrize('rows',[[],[('identity_0028',)],[('identity_0027',),('identity_0028',)]])
def test_actual_ledger_must_be_exactly27_before_recording_qualification(tmp_path,monkeypatch,rows):
    class Connection:
        def execute(self,statement):
            assert statement=='SELECT version_num FROM identity.alembic_version'
            return self
        def fetchall(self):return rows
    @contextmanager
    def connect(proof):yield Connection()
    monkeypatch.setattr(qualifier,'connect',connect)
    with pytest.raises(AssertionError,match='qualified_predecessor_ledger_must_be27'):
        qualifier.record_predecessor27(tmp_path)
    assert not (tmp_path/'predecessor27.json').exists()


def test_only_actual27_ledger_is_recorded(tmp_path,monkeypatch):
    class Connection:
        def execute(self,statement):return self
        def fetchall(self):return [('identity_0027',)]
    @contextmanager
    def connect(proof):yield Connection()
    monkeypatch.setattr(qualifier,'connect',connect)
    qualifier.record_predecessor27(tmp_path)
    assert json.loads((tmp_path/'predecessor27.json').read_text())['qualified_head']=='identity_0027'
