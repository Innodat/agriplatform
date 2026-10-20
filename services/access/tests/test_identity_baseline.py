"""ID-A acceptance guards; actual PostgreSQL scenarios are owner-qualified separately."""
import importlib.util
from pathlib import Path
import sys
import pytest
OWNER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(OWNER / 'identity-migrations'))

def test_sources_are_pinned_and_outer_transactions_removed():
    from identity_baseline import source_sql, SOURCES
    assert len(SOURCES) == 7
    sql = source_sql()
    assert len(sql) == 7
    assert 'CREATE SCHEMA IF NOT EXISTS identity;' not in sql[0]
    assert 'create type identity.app_permission' in sql[0]
    assert 'create table identity.users' in sql[0]
    assert not sql[-2].strip().lower().startswith('begin;')
    assert not sql[-2].strip().lower().endswith('commit;')

def test_unknown_catalog_refuses_without_target_approval():
    from identity_baseline import compare_catalog, BaselineError
    with pytest.raises(BaselineError, match='catalog_mismatch'):
        compare_catalog({'columns': ['unknown']}, {'columns': ['trusted']})

def test_downgrade_is_prohibited():
    spec = importlib.util.spec_from_file_location('identity_revision', OWNER/'identity-migrations/versions/0001_baseline.py')
    revision = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(revision)
    with pytest.raises(RuntimeError, match='Destructive'):
        revision.downgrade()

def test_reference_has_no_caller_control():
    from identity_baseline import trusted_reference, BaselineError
    try:
        reference = trusted_reference('legacy')
    except BaselineError as exc:
        assert str(exc) == 'identity_reference_unavailable'
    else:
        assert reference['relations']


def test_modified_historical_source_is_refused_before_any_database_work(tmp_path,monkeypatch):
    import identity_baseline as baseline
    path=tmp_path/baseline.SOURCES[0]
    path.parent.mkdir(parents=True)
    path.write_text('CREATE TABLE identity.surprise(id int)')
    monkeypatch.setattr(baseline,'ROOT',tmp_path)
    with pytest.raises(baseline.BaselineError,match='identity_source_pin_mismatch'):
        baseline.source_sql()


def test_reference_digest_mismatch_refuses_target_selected_catalog(tmp_path,monkeypatch):
    import identity_baseline as baseline
    (tmp_path/'reference.json').write_text('{"legacy":{"relations":["target-approved"]}}')
    monkeypatch.setattr(baseline,'HERE',tmp_path)
    monkeypatch.setattr(baseline,'REFERENCE_SHA256','0'*64)
    with pytest.raises(baseline.BaselineError,match='identity_reference_unavailable'):
        baseline.trusted_reference('legacy')


def test_catalog_fingerprints_are_deterministic_and_sensitive_to_each_category():
    from identity_baseline import catalog_fingerprints
    catalog = {'columns': [['id', 'uuid']], 'functions': [['hook', 'body']]}
    original = catalog_fingerprints(catalog)
    assert catalog_fingerprints(dict(reversed(list(catalog.items())))) == original
    changed = catalog_fingerprints({'columns': [['id', 'text']], 'functions': [['hook', 'body']]})
    assert changed['columns'] != original['columns']
    assert changed['functions'] == original['functions']
    assert original['columns']['rows'] == 1
    assert len(original['columns']['sha256']) == 64


def test_owned_integration_preserves_legacy_references_and_scoped_synthetic_seed_dml(monkeypatch):
    spec = importlib.util.spec_from_file_location('identity_integration', OWNER/'identity-migrations/versions/0001_baseline.py')
    revision = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(revision)
    statements=[]
    class Connection:
        def exec_driver_sql(self,sql):
            statements.append(sql)
    class Context:
        class config:
            attributes={'identity_state':'adopt'}
    class Operations:
        def get_bind(self):
            return Connection()
    monkeypatch.setattr(revision,'context',Context())
    monkeypatch.setattr(revision,'op',Operations())
    revision.upgrade()
    grants='\n'.join(statements[1:])
    assert 'GRANT USAGE ON SCHEMA identity TO postgres;' in grants
    assert 'GRANT REFERENCES (id) ON identity.users, identity.org TO postgres;' in grants
    assert 'GRANT SELECT (id) ON identity.users TO postgres;' in grants
    assert 'GRANT INSERT (name, slug, created_by, updated_by) ON identity.org TO postgres;' in grants
    assert 'GRANT INSERT (member_id, role, created_by, updated_by) ON identity.member_role TO postgres;' in grants
    assert 'GRANT UPDATE (actor_key, is_system, username, is_platform_admin, updated_at)' in grants
    assert grants == revision.LEGACY_INTEGRATION_SQL
    assert not any(privilege in grants for privilege in ('DELETE','ALL','auth.users'))


def test_qualification_rejects_foreign_owner_runtime_and_auth_urls_before_network():
    import importlib.util
    script = OWNER / 'tests/qualify_identity_baseline.py'
    spec = importlib.util.spec_from_file_location('identity_qualification', script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    run = {'run_id':'99b7231c-0a5b-4bdb-98e8-3329564c526a'}
    target = {'ports':{'database':55482,'supabase_api':55481}}
    fixture = {'admin_url':'postgresql://postgres:synthetic@127.0.0.1:55482/postgres',
               'api_url':'http://127.0.0.1:55481',
               'databases':{'native':'postgresql://postgres:synthetic@127.0.0.1:55482/postgres'},
               'owner_urls':{'native':'postgresql://identity_migrator:synthetic@127.0.0.1:55482/postgres'},
               'runtime_urls':{'native':'postgresql://access_runtime:synthetic@127.0.0.1:55482/postgres'}}
    import copy
    module.validate_fixture_urls(fixture,run,target)
    for field in ['databases','owner_urls','runtime_urls']:
        invalid = copy.deepcopy(fixture)
        invalid[field]['native'] = invalid[field]['native'].replace('127.0.0.1','foreign.invalid')
        with pytest.raises(AssertionError):module.validate_fixture_urls(invalid,run,target)
    for field,value in [('api_url','https://foreign.invalid'),('admin_url','postgresql://postgres:synthetic@foreign.invalid/postgres')]:
        invalid = copy.deepcopy(fixture);invalid[field] = value
        with pytest.raises(AssertionError):module.validate_fixture_urls(invalid,run,target)


def test_private_ledger_rejects_column_grants():
    from identity_baseline import verify_owned_history, BaselineError
    class Result:
        def __init__(self,value):self.value=value
        def scalar_one(self):return self.value
        def all(self):return self.value
        def scalars(self):return self.value
    class Connection:
        def execute(self,sql):
            query=str(sql)
            if 'SELECT version_num' in query:return Result(['identity_0001'])
            if 'information_schema.columns' in query:return Result([('version_num','character varying',32,'NO',None)])
            if 'SELECT pg_get_userbyid' in query:return Result('identity_migrator')
            if 'pg_attribute' in query:return Result(1)
            if 'pg_constraint' in query:return Result([('p','PRIMARY KEY (version_num)')])
            return Result(0)
    with pytest.raises(BaselineError,match='identity_unknown_history'):
        verify_owned_history(Connection())


def test_owned_postcondition_rechecks_head_legacy_history_and_catalog(monkeypatch):
    import identity_baseline as baseline
    checked=[]
    monkeypatch.setattr(baseline,'verify_owned_history',lambda connection:checked.append('head') or 'identity_0001')
    monkeypatch.setattr(baseline,'verify_legacy_history',lambda connection:checked.append('legacy'))
    monkeypatch.setattr(baseline,'verify_catalog',lambda connection,kind:checked.append(kind))
    baseline.verify_owned_postcondition(object())
    assert checked==['head','legacy','owned']


@pytest.mark.parametrize('revisions',[[],['unknown'],['identity_0001','unknown'],['identity_0002','identity_0001']])
def test_private_ledger_requires_exact_known_head(revisions):
    from identity_baseline import verify_owned_history, BaselineError
    class Result:
        def scalars(self):return revisions
    class Connection:
        def execute(self,sql):return Result()
    with pytest.raises(BaselineError,match='identity_unknown_history'):
        verify_owned_history(Connection())


def test_migration_postcondition_failure_rolls_back_after_ledger_cleanup(monkeypatch):
    import runpy
    import sqlalchemy
    import identity_baseline as baseline
    from alembic import context
    events=[]
    class Transaction:
        def __enter__(self):return self
        def __exit__(self,kind,value,tb):events.append('rollback' if kind else 'commit')
        def exec_driver_sql(self,sql):
            if 'REVOKE ALL ON identity.alembic_version' in sql:events.append('cleanup')
    class Engine:
        def begin(self):return Transaction()
        def dispose(self):pass
    class Config:
        cmd_opts=None
        attributes={}
    def upgrade():pass
    class MigrationContext:
        opts={'fn':upgrade}
    monkeypatch.setenv('IDENTITY_MIGRATION_DATABASE_URL','synthetic-prepared-url')
    monkeypatch.setattr(sqlalchemy,'create_engine',lambda *args,**kwargs:Engine())
    monkeypatch.setattr(context,'config',Config(),raising=False)
    monkeypatch.setattr(context,'is_offline_mode',lambda:False)
    monkeypatch.setattr(context,'configure',lambda **kwargs:None)
    monkeypatch.setattr(context,'get_context',lambda:MigrationContext())
    monkeypatch.setattr(context,'run_migrations',lambda:events.append('migrated'))
    monkeypatch.setattr(baseline,'preflight',lambda *args:'clean')
    def reject(connection, require_head=False):
        assert require_head
        events.append('postcondition')
        raise baseline.BaselineError('identity_catalog_mismatch:roles')
    monkeypatch.setattr(baseline,'verify_owned_postcondition',reject)
    with pytest.raises(baseline.BaselineError,match='identity_catalog_mismatch'):
        runpy.run_path(str(OWNER/'identity-migrations/env.py'))
    assert events==['migrated','cleanup','postcondition','rollback']


def test_actor_revision_is_additive_and_destructive_recovery_is_prohibited():
    path = OWNER/'identity-migrations/versions/0002_actor_registry.py'
    assert path.exists(), 'additive actor foundation is missing'
    spec = importlib.util.spec_from_file_location('identity_actor_revision', path)
    revision = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(revision)
    assert revision.revision == 'identity_0002'
    assert revision.down_revision == 'identity_0001'
    assert revision.ACTOR_SCHEMA_SQL
    with pytest.raises(RuntimeError, match='Destructive'):
        revision.downgrade()


def test_actor_reference_is_separate_and_fails_closed(tmp_path, monkeypatch):
    import identity_baseline as baseline
    assert baseline.ACTOR_REVISION == 'identity_0002'
    monkeypatch.setattr(baseline, 'HERE', tmp_path)
    monkeypatch.setattr(baseline, 'ACTOR_REFERENCE_SHA256', None)
    with pytest.raises(baseline.BaselineError, match='identity_reference_unavailable'):
        baseline.trusted_actor_reference()


def test_owned_catalog_selection_follows_exact_revision(monkeypatch):
    import identity_baseline as baseline
    checked = []
    monkeypatch.setattr(baseline, 'verify_owned_history', lambda connection: 'identity_0002')
    monkeypatch.setattr(baseline, 'verify_legacy_history', lambda connection: checked.append('legacy'))
    monkeypatch.setattr(baseline, 'verify_catalog', lambda connection, kind: checked.append(kind))
    baseline.verify_owned_postcondition(object())
    assert checked == ['legacy', 'actor']


def test_final_postcondition_rejects_previous_head(monkeypatch):
    import identity_baseline as baseline
    monkeypatch.setattr(baseline, 'verify_owned_history', lambda connection: 'identity_0001')
    with pytest.raises(baseline.BaselineError, match='identity_unknown_history'):
        baseline.verify_owned_postcondition(object(), require_head=True)


@pytest.mark.parametrize('revision', ['identity_0001', 'identity_0002'])
def test_private_ledger_accepts_only_known_structurally_private_revisions(revision):
    from identity_baseline import verify_owned_history
    class Result:
        def __init__(self, value): self.value = value
        def scalar_one(self): return self.value
        def all(self): return self.value
        def scalars(self): return self.value
    class Connection:
        def execute(self, sql):
            query = str(sql)
            if 'SELECT version_num' in query: return Result([revision])
            if 'information_schema.columns' in query:
                return Result([('version_num', 'character varying', 32, 'NO', None)])
            if 'SELECT pg_get_userbyid' in query: return Result('identity_migrator')
            if 'pg_constraint' in query: return Result([('p', 'PRIMARY KEY (version_num)')])
            return Result(0)
    assert verify_owned_history(Connection()) == revision


@pytest.mark.parametrize('corruption', ['digest', 'sources', 'migration', None])
def test_actor_reference_checks_fixed_digest_sources_and_ddl(tmp_path, monkeypatch, corruption):
    import hashlib
    import json
    import identity_baseline as baseline
    (tmp_path/'versions').mkdir()
    ddl = b'explicit synthetic fixture DDL'
    (tmp_path/'versions/0002_actor_registry.py').write_bytes(ddl)
    (tmp_path/'source-pins.json').write_text('{"original": "pin"}')
    reference = {'source_pins': {'original': 'pin'}, 'migration_sha256': hashlib.sha256(ddl).hexdigest(),
                 'actor': {'columns': {'sha256': 'fixed', 'rows': 1}}}
    if corruption == 'sources': reference['source_pins'] = {'unexpected': 'source'}
    if corruption == 'migration': reference['migration_sha256'] = '0'*64
    content = json.dumps(reference).encode()
    (tmp_path/'actor-reference.json').write_bytes(content)
    monkeypatch.setattr(baseline, 'HERE', tmp_path)
    monkeypatch.setattr(baseline, 'ACTOR_REFERENCE_SHA256',
                        '0'*64 if corruption == 'digest' else hashlib.sha256(content).hexdigest())
    if corruption:
        with pytest.raises(baseline.BaselineError, match='identity_reference_unavailable'):
            baseline.trusted_actor_reference()
    else:
        assert baseline.trusted_actor_reference() == reference['actor']


def test_actor_ddl_uses_compiled_sql_for_literal_postgres_format_tokens(monkeypatch):
    from sqlalchemy import text
    from sqlalchemy.dialects.postgresql.psycopg import PGDialect_psycopg
    spec = importlib.util.spec_from_file_location('identity_actor_compiled', OWNER/'identity-migrations/versions/0002_actor_registry.py')
    revision = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(revision)
    statements = []
    class Connection:
        def execute(self, statement): statements.append(statement)
    monkeypatch.setattr(revision.op, 'get_bind', lambda: Connection())
    revision.upgrade()
    assert len(statements) == 1
    compiled = statements[0].compile(dialect=PGDialect_psycopg())
    assert not compiled.params
    assert '%%I' in str(compiled) and '%%s' in str(compiled)
    assert str(statements[0]) == str(text(revision.ACTOR_SCHEMA_SQL))


def test_actor_reference_recorder_preserves_foreign_temporary_file(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location('identity_reference_recording', OWNER/'tests/qualify_identity_baseline.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    (tmp_path/'versions').mkdir()
    (tmp_path/'versions/0001_baseline.py').write_text('LEGACY_INTEGRATION_SQL = ""\n')
    (tmp_path/'versions/0002_actor_registry.py').write_text('ACTOR_SCHEMA_SQL = ""\n')
    (tmp_path/'identity_baseline.py').write_text('ACTOR_REFERENCE_SHA256 = None\n')
    (tmp_path/'source-pins.json').write_text('{}')
    temporary = tmp_path/'.actor-reference-recording'
    temporary.write_bytes(b'foreign invocation evidence')
    class Transaction:
        def rollback(self): pass
    class Connection:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def begin(self): return Transaction()
        def exec_driver_sql(self, *args): pass
        def execute(self, *args): pass
    class Engine:
        def connect(self): return Connection()
        def dispose(self): pass
    monkeypatch.setattr(module, 'OWNER', tmp_path)
    monkeypatch.setattr(module, 'engine', lambda url: Engine())
    monkeypatch.setattr(module.baseline, 'preflight', lambda *args: 'clean')
    monkeypatch.setattr(module.baseline, 'source_sql', lambda: [])
    monkeypatch.setattr(module.baseline, 'verify_catalog', lambda *args: None)
    monkeypatch.setattr(module.baseline, 'catalog_snapshot', lambda *args: {})
    runner = module.Qualification(tmp_path, {'owner_urls': {'actor_reference': 'synthetic'}})
    with pytest.raises(FileExistsError):
        runner.record_actor_reference()
    assert temporary.read_bytes() == b'foreign invocation evidence'
    assert not (tmp_path/'actor-reference.json').exists()
    assert (tmp_path/'identity_baseline.py').read_text() == 'ACTOR_REFERENCE_SHA256 = None\n'
