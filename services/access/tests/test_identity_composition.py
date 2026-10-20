from pathlib import Path
import sys
import pytest
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from tools.py import run_compose_supabase as compose

def test_explicit_identity_handover_keeps_other_owners_and_legacy_default():
    modules = [compose.Module('platform',ROOT/'platform')]
    legacy = compose.collect_migrations(modules)
    owned = compose.select_identity_authority(legacy,'owned')
    assert len(legacy)-len(owned)==6
    assert any('content_system' in m.file_name for m in owned)
    assert compose.select_identity_authority(legacy,'legacy')==legacy

def test_owned_no_clean_rejects_duplicate_authority(tmp_path):
    old=tmp_path/'20250815110000_platform_create_identity_schema.sql'
    old.write_text('historical')
    with pytest.raises(SystemExit,match='duplicate Identity'):
        compose.validate_identity_output('owned', True, tmp_path)
    assert old.read_text()=='historical'


def test_owned_main_without_migrations_refuses_retained_legacy_outputs(tmp_path,monkeypatch):
    import argparse
    output=tmp_path/'migrations'
    output.mkdir()
    old=output/next(iter(compose.IDENTITY_SOURCE_NAMES))
    old.write_text('preserved historical SQL')
    monkeypatch.setattr(compose,'ROOT_SUPABASE_DIR',tmp_path)
    monkeypatch.setattr(compose,'REPO_ROOT',tmp_path)
    monkeypatch.setattr(compose,'OUTPUT_MIGRATIONS_DIR',output)
    monkeypatch.setattr(compose,'parse_args',lambda:argparse.Namespace(
        check_only=False,dry_run=False,no_migrations=True,no_seeds=True,no_functions=True,
        identity_authority='owned',no_clean=False,no_platform=True,apps=[],include_db_packs=False,
        seed_mode='flat',allow_empty=True,no_manifest=False))
    written=[]
    monkeypatch.setattr(compose,'write_manifest',lambda *args:written.append(True))
    with pytest.raises(SystemExit,match='duplicate Identity'):
        compose.main()
    assert not written
    assert old.read_text()=='preserved historical SQL'
