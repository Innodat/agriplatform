"""Synthetic-only ID-A qualification. Credentials are private fixture input, never argv.

Run with IDENTITY_QUALIFICATION_DIR pointing at the fresh native-wrapper proof directory.
The root qualification owner provisions scratch DBs first; this creates no Docker resources.
Reference recording is an explicit developer fixture operation from known source executions.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import re
from urllib.parse import urlunsplit, quote
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
OWNER = ROOT / 'services/access/identity-migrations'
sys.path.insert(0, str(OWNER))
import identity_baseline as baseline
from sqlalchemy import create_engine, text


def sha(data):
    return hashlib.sha256(data).hexdigest()


def validate_fixture_urls(private, run, target):
    prefix = 'ida_' + run['run_id'].replace('-', '')[:12] + '_' + run.get('database_namespace', '')
    cases = set(private['databases'])
    for group, user in [('databases','postgres'),('owner_urls','identity_migrator'),('runtime_urls','access_runtime')]:
        assert set(private[group]) == cases
        for case,url in private[group].items():
            parsed = urlsplit(url)
            assert parsed.scheme == 'postgresql'
            assert parsed.hostname in ('127.0.0.1','localhost')
            assert parsed.port == target['ports']['database']
            assert parsed.username == user
            assert parsed.path == ('/postgres' if case=='native' else '/'+prefix+case)
            assert not parsed.query and not parsed.fragment
    assert private['admin_url'] == private['databases']['native']
    api = urlsplit(private['api_url'])
    assert api.scheme == 'http' and api.hostname in ('127.0.0.1','localhost')
    assert api.port == target['ports']['supabase_api']
    assert api.path in ('','/') and not api.query and not api.fragment
    assert api.username is None and api.password is None


def fixture():
    proof = Path(os.environ['IDENTITY_QUALIFICATION_DIR']).resolve()
    assert proof.is_relative_to(ROOT / 'platform/deployment/.local/identity-baseline')
    run = json.loads((proof / 'run.json').read_text())
    assert run['status'] == 'started'
    sys.path.insert(0, str(ROOT / 'platform/deployment'))
    import dev, native_cli
    raw = dev.read(Path(run['target']))
    target = dev.decode(raw)
    native_cli.check_run(ROOT / 'platform/deployment/.local/kdg' / run['run_id'], target, raw, run['run_id'])
    private = json.loads((proof / 'credentials.json').read_text())
    validate_fixture_urls(private, run, target)
    return proof, private


def engine(url):
    return create_engine(url.replace('postgresql://', 'postgresql+psycopg://', 1), hide_parameters=True,
                         connect_args={'connect_timeout': 5})


# Direct entries only: effective privilege checks would include inherited vendor
# administrator authority and cannot tell which exact temporary grants to undo.
FIXTURE_REFERENCE_ACLS_SQL = """
SELECT 'schema', n.nspacl::text, EXISTS (
    SELECT 1 FROM aclexplode(n.nspacl) a
    WHERE a.grantor=(SELECT oid FROM pg_roles WHERE rolname='identity_migrator')
      AND a.grantee=(SELECT oid FROM pg_roles WHERE rolname='postgres')
      AND a.privilege_type='USAGE')
FROM pg_namespace n WHERE n.nspname='identity'
UNION ALL
SELECT c.relname, att.attacl::text, EXISTS (
    SELECT 1 FROM aclexplode(att.attacl) a
    WHERE a.grantor=(SELECT oid FROM pg_roles WHERE rolname='identity_migrator')
      AND a.grantee=(SELECT oid FROM pg_roles WHERE rolname='postgres')
      AND a.privilege_type='REFERENCES')
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
JOIN pg_attribute att ON att.attrelid=c.oid
WHERE n.nspname='identity' AND c.relname IN ('users','org') AND att.attname='id'
ORDER BY 1
"""


class Qualification:
    def __init__(self, proof, private):
        self.proof, self.private = proof, private
        self.records = json.loads((proof / 'identity-qualification.json').read_text())['steps'] if (proof / 'identity-qualification.json').exists() else []

    def persist(self):
        (self.proof / 'identity-qualification.json').write_text(json.dumps({'steps': self.records}, indent=2) + '\n')

    def command(self, label, case, mode='clean', expected=None, action=('upgrade', 'head')):
        env = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C.UTF-8',
               'IDENTITY_MIGRATION_DATABASE_URL': self.private['owner_urls'][case].replace('postgresql://', 'postgresql+psycopg://', 1),
               'IDENTITY_MIGRATION_MODE': mode}
        cmd = [sys.executable, '-I', '-B', '-m', 'alembic', '-c', str(ROOT / 'services/access/identity-alembic.ini'), *action]
        started = time.monotonic()
        result = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=90)
        log = result.stdout + result.stderr
        original_label = label
        attempt = 1
        while (self.proof / (label + '.log')).exists():
            attempt += 1
            label = original_label + '-attempt-' + str(attempt)
        path = self.proof / (label + '.log')
        path.write_text(log)
        path.chmod(0o600)
        row = {'label': label, 'case': case, 'mode': mode, 'command': cmd,
               'exit_code': result.returncode, 'elapsed_seconds': round(time.monotonic() - started, 3),
               'log_sha256': sha(log.encode()), 'credentials': 'private fixture owner_urls only'}
        self.records.append(row)
        self.persist()
        assert (result.returncode != 0 and expected in log) if expected else result.returncode == 0, label
        if expected:
            row['expected_failure'] = expected
            self.persist()
        print(label, 'PASS', flush=True)

    def snapshot(self, case):
        db = engine(self.private['owner_urls'][case])
        try:
            with db.connect() as connection:
                return baseline.catalog_snapshot(connection)
        finally:
            db.dispose()

    def legacy(self, case):
        db = engine(self.private['owner_urls'][case])
        try:
            with db.begin() as connection:
                assert connection.execute(text('SELECT session_user,current_user')).one() == ('identity_migrator', 'identity_migrator')
                assert connection.execute(text("SELECT to_regclass('identity.users')")).scalar_one() is None
                for source in baseline.source_sql()[:-1]:
                    connection.exec_driver_sql(source)
        finally:
            db.dispose()
        self.records.append({'label': 'legacy-source-' + case, 'source_pins': json.loads((OWNER / 'source-pins.json').read_text()), 'status': 'passed'})
        self.persist()

    def record_reference(self):
        assert not (OWNER / 'reference.json').exists(), 'reference_already_exists'
        # Independently execute the pinned sources and fixed integration in a
        # rollback-only transaction. Migration execution itself never bypasses its
        # trusted postcondition merely to bootstrap this developer fixture.
        revision_spec = importlib.util.spec_from_file_location('identity_source_fixture', OWNER/'versions/0001_baseline.py')
        revision = importlib.util.module_from_spec(revision_spec)
        revision_spec.loader.exec_module(revision)
        db = engine(self.private['owner_urls']['clean'])
        try:
            with db.connect() as connection:
                transaction = connection.begin()
                try:
                    assert connection.execute(text("SELECT to_regclass('identity.users')")).scalar_one() is None
                    for source in baseline.source_sql():
                        connection.exec_driver_sql(source)
                    connection.exec_driver_sql(revision.LEGACY_INTEGRATION_SQL)
                    owned_reference = baseline.catalog_fingerprints(baseline.catalog_snapshot(connection))
                finally:
                    transaction.rollback()
        finally:
            db.dispose()
        self.legacy('legacy')
        reference = {'_generated': 'GENERATED by tests/qualify_identity_baseline.py --record-reference; change owning fixture/code, never hand-edit',
                     'source_pins': json.loads((OWNER / 'source-pins.json').read_text()),
                     'legacy': baseline.catalog_fingerprints(self.snapshot('legacy')), 'owned': owned_reference}
        content = (json.dumps(reference, sort_keys=True, indent=2) + '\n').encode()
        module = OWNER / 'identity_baseline.py'
        source = module.read_text()
        assert 'REFERENCE_SHA256 = None' in source, 'reference_pin_already_present'
        temporary = OWNER / '.reference-recording'
        with temporary.open('xb') as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        temporary.replace(OWNER / 'reference.json')
        assert sha((OWNER / 'reference.json').read_bytes()) == sha(content)
        module.write_text(source.replace('REFERENCE_SHA256 = None', 'REFERENCE_SHA256 = ' + repr(sha(content))))
        self.records.append({'label': 'trusted-reference', 'sha256': sha(content), 'known_source_cases': ['clean', 'legacy']})
        self.persist()
        print('trusted-reference PASS', sha(content), flush=True)
        self.command('clean-first', 'clean')


    def record_actor_reference(self):
        """Independent rollback-only known-source fixture, never target approval."""
        destination = OWNER / 'actor-reference.json'
        assert not destination.exists(), 'actor_reference_already_exists'
        module = OWNER / 'identity_baseline.py'
        module_source = module.read_text()
        assert 'ACTOR_REFERENCE_SHA256 = None' in module_source, 'actor_reference_pin_already_present'
        def load_revision(name, filename):
            spec = importlib.util.spec_from_file_location(name, OWNER/'versions'/filename)
            revision = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(revision)
            return revision
        original = load_revision('identity_original_fixture', '0001_baseline.py')
        actor = load_revision('identity_actor_fixture', '0002_actor_registry.py')
        db = engine(self.private['owner_urls']['actor_reference'])
        try:
            with db.connect() as connection:
                transaction = connection.begin()
                try:
                    assert baseline.preflight(connection, 'clean') == 'clean'
                    for source in baseline.source_sql():
                        connection.exec_driver_sql(source)
                    connection.exec_driver_sql(original.LEGACY_INTEGRATION_SQL)
                    # Characterize the old reference before adding new structures.
                    baseline.verify_catalog(connection, 'owned')
                    connection.execute(text(actor.ACTOR_SCHEMA_SQL))
                    fingerprint = baseline.catalog_fingerprints(baseline.catalog_snapshot(connection))
                finally:
                    transaction.rollback()
            with db.connect() as connection:
                assert baseline.preflight(connection, 'clean') == 'clean'
        finally:
            db.dispose()
        reference = {
            '_generated': 'GENERATED by tests/qualify_identity_baseline.py --record-actor-reference; change owning fixture/code, never hand-edit',
            'source_pins': json.loads((OWNER/'source-pins.json').read_text()),
            'migration_sha256': sha((OWNER/'versions/0002_actor_registry.py').read_bytes()),
            'actor': fingerprint,
        }
        content = (json.dumps(reference, sort_keys=True, indent=2) + '\n').encode()
        temporary = OWNER / '.actor-reference-recording'
        created_temporary = False
        try:
            with temporary.open('xb') as output:
                created_temporary = True
                output.write(content)
                output.flush()
                os.fsync(output.fileno())
            # Hard-link publication is atomic and exclusive: never replace a fixture.
            os.link(temporary, destination)
        finally:
            if created_temporary:
                temporary.unlink(missing_ok=True)
        assert module.read_text() == module_source, 'reference_module_changed_during_recording'
        module.write_text(module_source.replace('ACTOR_REFERENCE_SHA256 = None',
                                              'ACTOR_REFERENCE_SHA256 = ' + repr(sha(content))))
        self.records.append({'label': 'trusted-actor-reference', 'sha256': sha(content),
                             'migration_sha256': reference['migration_sha256'],
                             'known_source_case': 'actor_reference', 'rolled_back': True})
        self.persist()
        print('trusted-actor-reference PASS', sha(content), flush=True)

    def record_projection_reference(self):
        """Known-source rollback-only fixture for the first restricted reader."""
        destination=OWNER/'projection-reference.json'
        assert not destination.exists(), 'projection_reference_already_exists'
        module=OWNER/'identity_baseline.py'
        captured = {module: module.read_bytes(), OWNER/'source-pins.json': (OWNER/'source-pins.json').read_bytes()}
        assert b'PROJECTION_REFERENCE_SHA256 = None' in captured[module]
        revisions=[]
        for name in ['0001_baseline.py','0002_actor_registry.py','0003_current_account_actor.py']:
            path = OWNER/'versions'/name
            captured[path] = path.read_bytes()
            # Execute the exact captured source that the fixture digest binds.
            spec=importlib.util.spec_from_file_location('projection_source_'+name[:4],path)
            revision=importlib.util.module_from_spec(spec)
            exec(compile(captured[path], str(path), 'exec'), revision.__dict__)
            revisions.append(revision)
        db=engine(self.private['owner_urls']['projection_reference'])
        try:
            with db.connect() as connection:
                transaction=connection.begin()
                try:
                    assert baseline.preflight(connection,'clean')=='clean'
                    baseline.verify_projection_role(connection,staged=True)
                    for source in baseline.source_sql():connection.exec_driver_sql(source)
                    connection.exec_driver_sql(revisions[0].LEGACY_INTEGRATION_SQL)
                    connection.execute(text(revisions[1].ACTOR_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'actor')
                    connection.execute(text(revisions[2].PROJECTION_SCHEMA_SQL))
                    baseline.verify_projection_role(connection)
                    fingerprints=baseline.projection_catalog_fingerprints(baseline.projection_catalog_snapshot(connection))
                finally:
                    transaction.rollback()
            with db.connect() as connection:
                assert baseline.preflight(connection,'clean')=='clean'
                baseline.verify_projection_role(connection,staged=True)
        finally:db.dispose()
        reference={'_generated':'GENERATED by tests/qualify_identity_baseline.py --record-projection-reference; change owning fixture/code, never hand-edit',
                   'source_pins':json.loads(captured[OWNER/'source-pins.json']),
                   'migration_sha256':sha(captured[OWNER/'versions/0003_current_account_actor.py']),
                   'projection':fingerprints}
        content=(json.dumps(reference,sort_keys=True,indent=2)+'\n').encode()
        temporary=OWNER/'.projection-reference-recording';created=False
        try:
            with temporary.open('xb') as output:
                created=True;output.write(content);output.flush();os.fsync(output.fileno())
            assert all(path.read_bytes() == data for path,data in captured.items()), 'projection_reference_source_changed'
            os.link(temporary,destination)
        finally:
            if created:temporary.unlink(missing_ok=True)
        self.records.append({'label':'trusted-projection-reference','status':'passed','sha256':sha(content),'migration_sha256':reference['migration_sha256'],'known_source_case':'projection_reference','rolled_back':True,'helper_sha256':sha(captured[module]),'source_sha256':{str(path.relative_to(OWNER)):sha(data) for path,data in captured.items()},'pin_update_required':True})
        self.persist();print('trusted-projection-reference PASS',sha(content),flush=True)

    def record_organization_reference(self):
        """Known-source rollback-only fixture for the selected organization reader."""
        destination=OWNER/'organization-reference.json'
        assert not destination.exists(), 'organization_reference_already_exists'
        module=OWNER/'identity_baseline.py'
        captured = {module: module.read_bytes(), OWNER/'source-pins.json': (OWNER/'source-pins.json').read_bytes()}
        assert b'ORGANIZATION_REFERENCE_SHA256 = None' in captured[module]
        for name in ['reference.json','actor-reference.json','projection-reference.json']:
            path=OWNER/name; captured[path]=path.read_bytes()
        baseline.trusted_projection_reference()
        revisions=[]
        for name in ['0001_baseline.py','0002_actor_registry.py','0003_current_account_actor.py','0004_current_account_organization.py']:
            path = OWNER/'versions'/name
            captured[path] = path.read_bytes()
            # Execute the exact captured source that the fixture digest binds.
            spec=importlib.util.spec_from_file_location('projection_source_'+name[:4],path)
            revision=importlib.util.module_from_spec(spec)
            exec(compile(captured[path], str(path), 'exec'), revision.__dict__)
            revisions.append(revision)
        db=engine(self.private['owner_urls']['organization_reference'])
        try:
            with db.connect() as connection:
                transaction=connection.begin()
                try:
                    assert baseline.preflight(connection,'clean')=='clean'
                    baseline.verify_projection_role(connection,staged=True)
                    for source in baseline.source_sql():connection.exec_driver_sql(source)
                    connection.exec_driver_sql(revisions[0].LEGACY_INTEGRATION_SQL)
                    connection.execute(text(revisions[1].ACTOR_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'actor')
                    connection.execute(text(revisions[2].PROJECTION_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'projection')
                    connection.execute(text(revisions[3].ORGANIZATION_SCHEMA_SQL))
                    baseline.verify_projection_role(connection)
                    fingerprints=baseline.projection_catalog_fingerprints(baseline.projection_catalog_snapshot(connection))
                finally:
                    transaction.rollback()
            with db.connect() as connection:
                assert baseline.preflight(connection,'clean')=='clean'
                baseline.verify_projection_role(connection,staged=True)
        finally:db.dispose()
        reference={'_generated':'GENERATED by tests/qualify_identity_baseline.py --record-organization-reference; change owning fixture/code, never hand-edit',
                   'source_pins':json.loads(captured[OWNER/'source-pins.json']),
                   'migration_sha256':sha(captured[OWNER/'versions/0004_current_account_organization.py']),
                   'organization':fingerprints}
        content=(json.dumps(reference,sort_keys=True,indent=2)+'\n').encode()
        temporary=OWNER/'.organization-reference-recording';created=False
        try:
            with temporary.open('xb') as output:
                created=True;output.write(content);output.flush();os.fsync(output.fileno())
            assert all(path.read_bytes() == data for path,data in captured.items()), 'organization_reference_source_changed'
            os.link(temporary,destination)
        finally:
            if created:temporary.unlink(missing_ok=True)
        self.records.append({'label':'trusted-organization-reference','status':'passed','sha256':sha(content),'migration_sha256':reference['migration_sha256'],'known_source_case':'organization_reference','rolled_back':True,'helper_sha256':sha(captured[module]),'source_sha256':{str(path.relative_to(OWNER)):sha(data) for path,data in captured.items()},'pin_update_required':True})
        self.persist();print('trusted-organization-reference PASS',sha(content),flush=True)

    def record_authority_reference(self):
        """Known-source rollback-only fixture for the selected organization reader."""
        destination=OWNER/'authority-reference.json'
        assert not destination.exists(), 'authority_reference_already_exists'
        module=OWNER/'identity_baseline.py'
        captured = {module: module.read_bytes(), OWNER/'source-pins.json': (OWNER/'source-pins.json').read_bytes()}
        assert (Path(baseline.__file__).resolve()==module.resolve()
                and sha(captured[module])==baseline.IMPORTED_SOURCE_SHA256), 'authority_reference_stale_imported_helper'
        assert b'AUTHORITY_REFERENCE_SHA256 = None' in captured[module]
        for name in ['reference.json','actor-reference.json','projection-reference.json','organization-reference.json']:
            path=OWNER/name; captured[path]=path.read_bytes()
        baseline.trusted_organization_reference()
        revisions=[]
        for name in ['0001_baseline.py','0002_actor_registry.py','0003_current_account_actor.py','0004_current_account_organization.py','0005_operator_authority.py']:
            path = OWNER/'versions'/name
            captured[path] = path.read_bytes()
            # Execute the exact captured source that the fixture digest binds.
            spec=importlib.util.spec_from_file_location('projection_source_'+name[:4],path)
            revision=importlib.util.module_from_spec(spec)
            exec(compile(captured[path], str(path), 'exec'), revision.__dict__)
            revisions.append(revision)
        db=engine(self.private['owner_urls']['authority_reference'])
        try:
            with db.connect() as connection:
                transaction=connection.begin()
                try:
                    assert baseline.preflight(connection,'clean')=='clean'
                    baseline.verify_projection_role(connection,staged=True)
                    baseline.verify_authority_roles(connection,staged=True)
                    for source in baseline.source_sql():connection.exec_driver_sql(source)
                    connection.exec_driver_sql(revisions[0].LEGACY_INTEGRATION_SQL)
                    connection.execute(text(revisions[1].ACTOR_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'actor')
                    connection.execute(text(revisions[2].PROJECTION_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'projection')
                    connection.execute(text(revisions[3].ORGANIZATION_SCHEMA_SQL))
                    baseline.verify_projection_role(connection)
                    baseline.verify_catalog(connection,'organization')
                    connection.execute(text(revisions[4].AUTHORITY_SCHEMA_SQL))
                    baseline.verify_authority_roles(connection)
                    fingerprints=baseline.catalog_fingerprints(baseline.authority_catalog_snapshot(connection))
                finally:
                    transaction.rollback()
            with db.connect() as connection:
                assert baseline.preflight(connection,'clean')=='clean'
                baseline.verify_projection_role(connection,staged=True)
        finally:db.dispose()
        reference={'_generated':'GENERATED by tests/qualify_identity_baseline.py --record-authority-reference; change owning fixture/code, never hand-edit',
                   'source_pins':json.loads(captured[OWNER/'source-pins.json']),
                   'migration_sha256':sha(captured[OWNER/'versions/0005_operator_authority.py']),
                   'authority':fingerprints}
        content=(json.dumps(reference,sort_keys=True,indent=2)+'\n').encode()
        temporary=OWNER/'.authority-reference-recording';created=False
        try:
            descriptor=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(descriptor,'wb') as output:
                created=True;output.write(content);output.flush();os.fsync(output.fileno())
            assert all(path.read_bytes() == data for path,data in captured.items()), 'authority_reference_source_changed'
            os.link(temporary,destination)
        finally:
            if created:temporary.unlink(missing_ok=True)
        self.records.append({'label':'trusted-authority-reference','status':'passed','sha256':sha(content),'migration_sha256':reference['migration_sha256'],'known_source_case':'authority_reference','rolled_back':True,'helper_sha256':sha(captured[module]),'source_sha256':{str(path.relative_to(OWNER)):sha(data) for path,data in captured.items()},'pin_update_required':True})
        self.persist();print('trusted-authority-reference PASS',sha(content),flush=True)

    def record_command_reference(self):
        """Known-source rollback-only fixture for the selected organization reader."""
        destination=OWNER/'command-reference.json'
        assert not destination.exists(), 'command_reference_already_exists'
        module=OWNER/'identity_baseline.py'
        captured = {module: module.read_bytes(), OWNER/'source-pins.json': (OWNER/'source-pins.json').read_bytes()}
        assert (Path(baseline.__file__).resolve()==module.resolve()
                and sha(captured[module])==baseline.IMPORTED_SOURCE_SHA256), 'command_reference_stale_imported_helper'
        assert b'COMMAND_REFERENCE_SHA256 = None' in captured[module]
        for name in ['reference.json','actor-reference.json','projection-reference.json','organization-reference.json','authority-reference.json']:
            path=OWNER/name; captured[path]=path.read_bytes()
        baseline.trusted_authority_reference()
        revisions=[]
        for name in ['0001_baseline.py','0002_actor_registry.py','0003_current_account_actor.py','0004_current_account_organization.py','0005_operator_authority.py','0006_actor_command.py']:
            path = OWNER/'versions'/name
            captured[path] = path.read_bytes()
            # Execute the exact captured source that the fixture digest binds.
            spec=importlib.util.spec_from_file_location('projection_source_'+name[:4],path)
            revision=importlib.util.module_from_spec(spec)
            exec(compile(captured[path], str(path), 'exec'), revision.__dict__)
            revisions.append(revision)
        db=engine(self.private['owner_urls']['command_reference'])
        try:
            with db.connect() as connection:
                transaction=connection.begin()
                try:
                    assert baseline.preflight(connection,'clean')=='clean'
                    baseline.verify_projection_role(connection,staged=True)
                    baseline.verify_authority_roles(connection,staged=True)
                    baseline.verify_command_role(connection,staged=True)
                    for source in baseline.source_sql():connection.exec_driver_sql(source)
                    connection.exec_driver_sql(revisions[0].LEGACY_INTEGRATION_SQL)
                    connection.execute(text(revisions[1].ACTOR_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'actor')
                    connection.execute(text(revisions[2].PROJECTION_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'projection')
                    connection.execute(text(revisions[3].ORGANIZATION_SCHEMA_SQL))
                    baseline.verify_projection_role(connection)
                    baseline.verify_catalog(connection,'organization')
                    connection.execute(text(revisions[4].AUTHORITY_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'authority')
                    connection.exec_driver_sql(revisions[5].COMMAND_SCHEMA_SQL, execution_options={'no_parameters': True})
                    baseline.verify_command_role(connection)
                    fingerprints=baseline.catalog_fingerprints(baseline.command_catalog_snapshot(connection))
                finally:
                    transaction.rollback()
            with db.connect() as connection:
                assert baseline.preflight(connection,'clean')=='clean'
                baseline.verify_projection_role(connection,staged=True)
        finally:db.dispose()
        reference={'_generated':'GENERATED by tests/qualify_identity_baseline.py --record-command-reference; change owning fixture/code, never hand-edit',
                   'source_pins':json.loads(captured[OWNER/'source-pins.json']),
                   'migration_sha256':sha(captured[OWNER/'versions/0006_actor_command.py']),
                   'command':fingerprints}
        content=(json.dumps(reference,sort_keys=True,indent=2)+'\n').encode()
        temporary=OWNER/'.command-reference-recording';created=False
        try:
            descriptor=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(descriptor,'wb') as output:
                created=True;output.write(content);output.flush();os.fsync(output.fileno())
            assert all(path.read_bytes() == data for path,data in captured.items()), 'command_reference_source_changed'
            os.link(temporary,destination)
        finally:
            if created:temporary.unlink(missing_ok=True)
        self.records.append({'label':'trusted-command-reference','status':'passed','sha256':sha(content),'migration_sha256':reference['migration_sha256'],'known_source_case':'command_reference','rolled_back':True,'helper_sha256':sha(captured[module]),'source_sha256':{str(path.relative_to(OWNER)):sha(data) for path,data in captured.items()},'pin_update_required':True})
        self.persist();print('trusted-command-reference PASS',sha(content),flush=True)

    def record_target_reference(self):
        """Known-source rollback-only fixture for the selected organization reader."""
        if not __debug__:
            raise RuntimeError('target_reference_optimized_python_prohibited')
        destination=OWNER/'target-reference.json'
        assert not destination.exists(), 'target_reference_already_exists'
        module=OWNER/'identity_baseline.py'
        captured = {module: module.read_bytes(), OWNER/'source-pins.json': (OWNER/'source-pins.json').read_bytes()}
        assert (Path(baseline.__file__).resolve()==module.resolve()
                and sha(captured[module])==baseline.IMPORTED_SOURCE_SHA256), 'target_reference_stale_imported_helper'
        assert b'TARGET_REFERENCE_SHA256 = None' in captured[module]
        for name in ['reference.json','actor-reference.json','projection-reference.json','organization-reference.json','authority-reference.json','command-reference.json']:
            path=OWNER/name; captured[path]=path.read_bytes()
        baseline.trusted_command_reference()
        revisions=[]
        for name in ['0001_baseline.py','0002_actor_registry.py','0003_current_account_actor.py','0004_current_account_organization.py','0005_operator_authority.py','0006_actor_command.py','0007_organization_targets.py']:
            path = OWNER/'versions'/name
            captured[path] = path.read_bytes()
            # Execute the exact captured source that the fixture digest binds.
            spec=importlib.util.spec_from_file_location('projection_source_'+name[:4],path)
            revision=importlib.util.module_from_spec(spec)
            exec(compile(captured[path], str(path), 'exec'), revision.__dict__)
            revisions.append(revision)
        db=engine(self.private['owner_urls']['target_reference'])
        try:
            with db.connect() as connection:
                transaction=connection.begin()
                try:
                    assert baseline.preflight(connection,'clean')=='clean'
                    baseline.verify_projection_role(connection,staged=True)
                    baseline.verify_authority_roles(connection,staged=True)
                    baseline.verify_command_role(connection,staged=True)
                    baseline.verify_target_roles(connection,staged=True)
                    for source in baseline.source_sql():connection.exec_driver_sql(source)
                    connection.exec_driver_sql(revisions[0].LEGACY_INTEGRATION_SQL)
                    connection.execute(text(revisions[1].ACTOR_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'actor')
                    connection.execute(text(revisions[2].PROJECTION_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'projection')
                    connection.execute(text(revisions[3].ORGANIZATION_SCHEMA_SQL))
                    baseline.verify_projection_role(connection)
                    baseline.verify_catalog(connection,'organization')
                    connection.execute(text(revisions[4].AUTHORITY_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'authority')
                    connection.exec_driver_sql(revisions[5].COMMAND_SCHEMA_SQL, execution_options={'no_parameters': True})
                    baseline.verify_command_role(connection)
                    baseline.verify_catalog(connection,'command')
                    connection.exec_driver_sql(revisions[6].TARGET_SCHEMA_SQL, execution_options={'no_parameters': True})
                    baseline.verify_target_roles(connection)
                    fingerprints=baseline.catalog_fingerprints(baseline.target_catalog_snapshot(connection))
                finally:
                    transaction.rollback()
            with db.connect() as connection:
                assert baseline.preflight(connection,'clean')=='clean'
                baseline.verify_projection_role(connection,staged=True)
                baseline.verify_authority_roles(connection,staged=True)
                baseline.verify_command_role(connection,staged=True)
                baseline.verify_target_roles(connection,staged=True)
        finally:db.dispose()
        reference={'_generated':'GENERATED by tests/qualify_identity_baseline.py --record-target-reference; change owning fixture/code, never hand-edit',
                   'source_pins':json.loads(captured[OWNER/'source-pins.json']),
                   'migration_sha256':sha(captured[OWNER/'versions/0007_organization_targets.py']),
                   'target':fingerprints}
        content=(json.dumps(reference,sort_keys=True,indent=2)+'\n').encode()
        temporary=OWNER/'.target-reference-recording';created=False
        try:
            descriptor=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(descriptor,'wb') as output:
                created=True;output.write(content);output.flush();os.fsync(output.fileno())
            assert all(path.read_bytes() == data for path,data in captured.items()), 'target_reference_source_changed'
            os.link(temporary,destination)
        finally:
            if created:temporary.unlink(missing_ok=True)
        self.records.append({'label':'trusted-target-reference','status':'passed','sha256':sha(content),'migration_sha256':reference['migration_sha256'],'known_source_case':'target_reference','rolled_back':True,'helper_sha256':sha(captured[module]),'source_sha256':{str(path.relative_to(OWNER)):sha(data) for path,data in captured.items()},'pin_update_required':True})
        self.persist();print('trusted-target-reference PASS',sha(content),flush=True)

    def record_profile_reference(self):
        """Known-source rollback-only fixture for protected profile column privileges."""
        if not __debug__:
            raise RuntimeError('profile_reference_optimized_python_prohibited')
        destination=OWNER/'profile-reference.json'
        assert not destination.exists(), 'profile_reference_already_exists'
        module=OWNER/'identity_baseline.py'
        captured = {module: module.read_bytes(), OWNER/'source-pins.json': (OWNER/'source-pins.json').read_bytes()}
        assert (Path(baseline.__file__).resolve()==module.resolve()
                and sha(captured[module])==baseline.IMPORTED_SOURCE_SHA256), 'profile_reference_stale_imported_helper'
        assert b'PROFILE_REFERENCE_SHA256 = None' in captured[module]
        for name in ['reference.json','actor-reference.json','projection-reference.json','organization-reference.json','authority-reference.json','command-reference.json','target-reference.json']:
            path=OWNER/name; captured[path]=path.read_bytes()
        baseline.trusted_target_reference()
        revisions=[]
        for name in ['0001_baseline.py','0002_actor_registry.py','0003_current_account_actor.py','0004_current_account_organization.py','0005_operator_authority.py','0006_actor_command.py','0007_organization_targets.py','0008_profile_fields.py']:
            path = OWNER/'versions'/name
            captured[path] = path.read_bytes()
            # Execute the exact captured source that the fixture digest binds.
            spec=importlib.util.spec_from_file_location('projection_source_'+name[:4],path)
            revision=importlib.util.module_from_spec(spec)
            exec(compile(captured[path], str(path), 'exec'), revision.__dict__)
            revisions.append(revision)
        db=engine(self.private['owner_urls']['profile_reference'])
        try:
            with db.connect() as connection:
                transaction=connection.begin()
                try:
                    assert baseline.preflight(connection,'clean')=='clean'
                    baseline.verify_projection_role(connection,staged=True)
                    baseline.verify_authority_roles(connection,staged=True)
                    baseline.verify_command_role(connection,staged=True)
                    baseline.verify_target_roles(connection,staged=True)
                    for source in baseline.source_sql():connection.exec_driver_sql(source)
                    connection.exec_driver_sql(revisions[0].LEGACY_INTEGRATION_SQL)
                    connection.execute(text(revisions[1].ACTOR_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'actor')
                    connection.execute(text(revisions[2].PROJECTION_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'projection')
                    connection.execute(text(revisions[3].ORGANIZATION_SCHEMA_SQL))
                    baseline.verify_projection_role(connection)
                    baseline.verify_catalog(connection,'organization')
                    connection.execute(text(revisions[4].AUTHORITY_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'authority')
                    connection.exec_driver_sql(revisions[5].COMMAND_SCHEMA_SQL, execution_options={'no_parameters': True})
                    baseline.verify_command_role(connection)
                    baseline.verify_catalog(connection,'command')
                    connection.exec_driver_sql(revisions[6].TARGET_SCHEMA_SQL, execution_options={'no_parameters': True})
                    baseline.verify_target_roles(connection)
                    baseline.verify_catalog(connection,'target')
                    connection.exec_driver_sql(revisions[7].PROFILE_FIELDS_SQL, execution_options={'no_parameters': True})
                    baseline.verify_profile_privileges(connection)
                    fingerprints=baseline.catalog_fingerprints(baseline.target_catalog_snapshot(connection))
                finally:
                    transaction.rollback()
            with db.connect() as connection:
                assert baseline.preflight(connection,'clean')=='clean'
                baseline.verify_projection_role(connection,staged=True)
                baseline.verify_authority_roles(connection,staged=True)
                baseline.verify_command_role(connection,staged=True)
                baseline.verify_target_roles(connection,staged=True)
        finally:db.dispose()
        reference={'_generated':'GENERATED by tests/qualify_identity_baseline.py --record-profile-reference; change owning fixture/code, never hand-edit',
                   'source_pins':json.loads(captured[OWNER/'source-pins.json']),
                   'migration_sha256':sha(captured[OWNER/'versions/0008_profile_fields.py']),
                   'profile':fingerprints}
        content=(json.dumps(reference,sort_keys=True,indent=2)+'\n').encode()
        temporary=OWNER/'.profile-reference-recording';created=False
        try:
            descriptor=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(descriptor,'wb') as output:
                created=True;output.write(content);output.flush();os.fsync(output.fileno())
            assert all(path.read_bytes() == data for path,data in captured.items()), 'profile_reference_source_changed'
            os.link(temporary,destination)
        finally:
            if created:temporary.unlink(missing_ok=True)
        self.records.append({'label':'trusted-profile-reference','status':'passed','sha256':sha(content),'migration_sha256':reference['migration_sha256'],'known_source_case':'profile_reference','rolled_back':True,'helper_sha256':sha(captured[module]),'source_sha256':{str(path.relative_to(OWNER)):sha(data) for path,data in captured.items()},'pin_update_required':True})
        self.persist();print('trusted-profile-reference PASS',sha(content),flush=True)

    def record_legacy_roles_reference(self):
        """Known-source rollback-only fixture for the exact legacy role identity binding."""
        if not __debug__:
            raise RuntimeError('legacy_roles_reference_optimized_python_prohibited')
        destination=OWNER/'legacy-role-reference.json'
        assert not destination.exists(), 'legacy_roles_reference_already_exists'
        module=OWNER/'identity_baseline.py'
        captured = {module: module.read_bytes(), OWNER/'source-pins.json': (OWNER/'source-pins.json').read_bytes()}
        assert (Path(baseline.__file__).resolve()==module.resolve()
                and sha(captured[module])==baseline.IMPORTED_SOURCE_SHA256), 'legacy_roles_reference_stale_imported_helper'
        assert b'LEGACY_ROLES_REFERENCE_SHA256 = None' in captured[module]
        for name in ['reference.json','actor-reference.json','projection-reference.json','organization-reference.json','authority-reference.json','command-reference.json','target-reference.json','profile-reference.json']:
            path=OWNER/name; captured[path]=path.read_bytes()
        baseline.trusted_profile_reference()
        revisions=[]
        for name in ['0001_baseline.py','0002_actor_registry.py','0003_current_account_actor.py','0004_current_account_organization.py','0005_operator_authority.py','0006_actor_command.py','0007_organization_targets.py','0008_profile_fields.py','0009_legacy_roles.py']:
            path = OWNER/'versions'/name
            captured[path] = path.read_bytes()
            # Execute the exact captured source that the fixture digest binds.
            spec=importlib.util.spec_from_file_location('projection_source_'+name[:4],path)
            revision=importlib.util.module_from_spec(spec)
            exec(compile(captured[path], str(path), 'exec'), revision.__dict__)
            revisions.append(revision)
        db=engine(self.private['owner_urls']['legacy_roles_reference'])
        try:
            with db.connect() as connection:
                transaction=connection.begin()
                try:
                    connection.execute(text("SET LOCAL statement_timeout='60s'; SET LOCAL lock_timeout='5s'"))
                    assert baseline.preflight(connection,'clean')=='clean'
                    baseline.verify_projection_role(connection,staged=True)
                    baseline.verify_authority_roles(connection,staged=True)
                    baseline.verify_command_role(connection,staged=True)
                    baseline.verify_target_roles(connection,staged=True)
                    for source in baseline.source_sql():connection.exec_driver_sql(source)
                    connection.exec_driver_sql(revisions[0].LEGACY_INTEGRATION_SQL)
                    connection.execute(text(revisions[1].ACTOR_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'actor')
                    connection.execute(text(revisions[2].PROJECTION_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'projection')
                    connection.execute(text(revisions[3].ORGANIZATION_SCHEMA_SQL))
                    baseline.verify_projection_role(connection)
                    baseline.verify_catalog(connection,'organization')
                    connection.execute(text(revisions[4].AUTHORITY_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'authority')
                    connection.exec_driver_sql(revisions[5].COMMAND_SCHEMA_SQL, execution_options={'no_parameters': True})
                    baseline.verify_command_role(connection)
                    baseline.verify_catalog(connection,'command')
                    connection.exec_driver_sql(revisions[6].TARGET_SCHEMA_SQL, execution_options={'no_parameters': True})
                    baseline.verify_target_roles(connection)
                    baseline.verify_catalog(connection,'target')
                    connection.exec_driver_sql(revisions[7].PROFILE_FIELDS_SQL, execution_options={'no_parameters': True})
                    baseline.verify_profile_privileges(connection)
                    baseline.verify_catalog(connection,'profile')
                    connection.exec_driver_sql(revisions[8].LEGACY_ROLES_SQL, execution_options={'no_parameters': True})
                    fingerprints=baseline.catalog_fingerprints(baseline.target_catalog_snapshot(connection))
                finally:
                    transaction.rollback()
            with db.connect() as connection:
                connection.execute(text("SET LOCAL statement_timeout='60s'; SET LOCAL lock_timeout='5s'"))
                assert baseline.preflight(connection,'clean')=='clean'
                baseline.verify_projection_role(connection,staged=True)
                baseline.verify_authority_roles(connection,staged=True)
                baseline.verify_command_role(connection,staged=True)
                baseline.verify_target_roles(connection,staged=True)
        finally:db.dispose()
        reference={'_generated':'GENERATED by tests/qualify_identity_baseline.py --record-legacy-role-reference; change owning fixture/code, never hand-edit',
                   'source_pins':json.loads(captured[OWNER/'source-pins.json']),
                   'migration_sha256':sha(captured[OWNER/'versions/0009_legacy_roles.py']),
                   'legacy_roles':fingerprints}
        content=(json.dumps(reference,sort_keys=True,indent=2)+'\n').encode()
        temporary=OWNER/'.legacy-role-reference-recording';created=False
        try:
            descriptor=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(descriptor,'wb') as output:
                created=True;output.write(content);output.flush();os.fsync(output.fileno())
            assert all(path.read_bytes() == data for path,data in captured.items()), 'legacy_roles_reference_source_changed'
            os.link(temporary,destination)
        finally:
            if created:temporary.unlink(missing_ok=True)
        self.records.append({'label':'trusted-legacy-role-reference','status':'passed','sha256':sha(content),'migration_sha256':reference['migration_sha256'],'known_source_case':'legacy_roles_reference','rolled_back':True,'helper_sha256':sha(captured[module]),'source_sha256':{str(path.relative_to(OWNER)):sha(data) for path,data in captured.items()},'pin_update_required':True})
        self.persist();print('trusted-legacy-role-reference PASS',sha(content),flush=True)

    def record_token_hook_reference(self):
        """Known-source rollback-only fixture for the exact legacy role identity binding."""
        if not __debug__:
            raise RuntimeError('token_hook_reference_optimized_python_prohibited')
        destination=OWNER/'token-hook-reference.json'
        assert not destination.exists(), 'token_hook_reference_already_exists'
        module=OWNER/'identity_baseline.py'
        captured = {module: module.read_bytes(), OWNER/'source-pins.json': (OWNER/'source-pins.json').read_bytes()}
        assert (Path(baseline.__file__).resolve()==module.resolve()
                and sha(captured[module])==baseline.IMPORTED_SOURCE_SHA256), 'token_hook_reference_stale_imported_helper'
        assert b'TOKEN_HOOK_REFERENCE_SHA256 = None' in captured[module]
        for name in ['reference.json','actor-reference.json','projection-reference.json','organization-reference.json','authority-reference.json','command-reference.json','target-reference.json','profile-reference.json','legacy-role-reference.json']:
            path=OWNER/name; captured[path]=path.read_bytes()
        baseline.trusted_legacy_roles_reference()
        revisions=[]
        for name in ['0001_baseline.py','0002_actor_registry.py','0003_current_account_actor.py','0004_current_account_organization.py','0005_operator_authority.py','0006_actor_command.py','0007_organization_targets.py','0008_profile_fields.py','0009_legacy_roles.py','0010_token_hook.py']:
            path = OWNER/'versions'/name
            captured[path] = path.read_bytes()
            # Execute the exact captured source that the fixture digest binds.
            spec=importlib.util.spec_from_file_location('projection_source_'+name[:4],path)
            revision=importlib.util.module_from_spec(spec)
            exec(compile(captured[path], str(path), 'exec'), revision.__dict__)
            revisions.append(revision)
        db=engine(self.private['owner_urls']['token_hook_reference'])
        try:
            with db.connect() as connection:
                transaction=connection.begin()
                try:
                    connection.execute(text("SET LOCAL statement_timeout='60s'; SET LOCAL lock_timeout='5s'"))
                    assert baseline.preflight(connection,'clean')=='clean'
                    baseline.verify_projection_role(connection,staged=True)
                    baseline.verify_authority_roles(connection,staged=True)
                    baseline.verify_command_role(connection,staged=True)
                    baseline.verify_target_roles(connection,staged=True)
                    for source in baseline.source_sql():connection.exec_driver_sql(source)
                    connection.exec_driver_sql(revisions[0].LEGACY_INTEGRATION_SQL)
                    connection.execute(text(revisions[1].ACTOR_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'actor')
                    connection.execute(text(revisions[2].PROJECTION_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'projection')
                    connection.execute(text(revisions[3].ORGANIZATION_SCHEMA_SQL))
                    baseline.verify_projection_role(connection)
                    baseline.verify_catalog(connection,'organization')
                    connection.execute(text(revisions[4].AUTHORITY_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'authority')
                    connection.exec_driver_sql(revisions[5].COMMAND_SCHEMA_SQL, execution_options={'no_parameters': True})
                    baseline.verify_command_role(connection)
                    baseline.verify_catalog(connection,'command')
                    connection.exec_driver_sql(revisions[6].TARGET_SCHEMA_SQL, execution_options={'no_parameters': True})
                    baseline.verify_target_roles(connection)
                    baseline.verify_catalog(connection,'target')
                    connection.exec_driver_sql(revisions[7].PROFILE_FIELDS_SQL, execution_options={'no_parameters': True})
                    baseline.verify_profile_privileges(connection)
                    baseline.verify_catalog(connection,'profile')
                    connection.exec_driver_sql(revisions[8].LEGACY_ROLES_SQL, execution_options={'no_parameters': True})
                    baseline.verify_catalog(connection,'legacy_roles')
                    connection.exec_driver_sql(revisions[9].TOKEN_HOOK_SQL, execution_options={'no_parameters': True})
                    fingerprints=baseline.catalog_fingerprints(baseline.target_catalog_snapshot(connection))
                finally:
                    transaction.rollback()
            with db.connect() as connection:
                connection.execute(text("SET LOCAL statement_timeout='60s'; SET LOCAL lock_timeout='5s'"))
                assert baseline.preflight(connection,'clean')=='clean'
                baseline.verify_projection_role(connection,staged=True)
                baseline.verify_authority_roles(connection,staged=True)
                baseline.verify_command_role(connection,staged=True)
                baseline.verify_target_roles(connection,staged=True)
        finally:db.dispose()
        reference={'_generated':'GENERATED by tests/qualify_identity_baseline.py --record-token-hook-reference; change owning fixture/code, never hand-edit',
                   'source_pins':json.loads(captured[OWNER/'source-pins.json']),
                   'migration_sha256':sha(captured[OWNER/'versions/0010_token_hook.py']),
                   'token_hook':fingerprints}
        content=(json.dumps(reference,sort_keys=True,indent=2)+'\n').encode()
        temporary=OWNER/'.token-hook-reference-recording';created=False
        try:
            descriptor=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(descriptor,'wb') as output:
                created=True;output.write(content);output.flush();os.fsync(output.fileno())
            assert all(path.read_bytes() == data for path,data in captured.items()), 'token_hook_reference_source_changed'
            os.link(temporary,destination)
        finally:
            if created:temporary.unlink(missing_ok=True)
        self.records.append({'label':'trusted-token-hook-reference','status':'passed','sha256':sha(content),'migration_sha256':reference['migration_sha256'],'known_source_case':'token_hook_reference','rolled_back':True,'helper_sha256':sha(captured[module]),'source_sha256':{str(path.relative_to(OWNER)):sha(data) for path,data in captured.items()},'pin_update_required':True})
        self.persist();print('trusted-token-hook-reference PASS',sha(content),flush=True)

    def record_membership_binding_reference(self):
        """Known-source rollback-only fixture for the exact legacy role identity binding."""
        if not __debug__:
            raise RuntimeError('membership_binding_reference_optimized_python_prohibited')
        destination=OWNER/'membership-binding-reference.json'
        assert not destination.exists(), 'membership_binding_reference_already_exists'
        module=OWNER/'identity_baseline.py'
        captured = {module: module.read_bytes(), OWNER/'source-pins.json': (OWNER/'source-pins.json').read_bytes()}
        assert (Path(baseline.__file__).resolve()==module.resolve()
                and sha(captured[module])==baseline.IMPORTED_SOURCE_SHA256), 'membership_binding_reference_stale_imported_helper'
        assert b'MEMBERSHIP_BINDING_REFERENCE_SHA256 = None' in captured[module]
        for name in ['reference.json','actor-reference.json','projection-reference.json','organization-reference.json','authority-reference.json','command-reference.json','target-reference.json','profile-reference.json','legacy-role-reference.json','token-hook-reference.json']:
            path=OWNER/name; captured[path]=path.read_bytes()
        baseline.trusted_token_hook_reference()
        revisions=[]
        for name in ['0001_baseline.py','0002_actor_registry.py','0003_current_account_actor.py','0004_current_account_organization.py','0005_operator_authority.py','0006_actor_command.py','0007_organization_targets.py','0008_profile_fields.py','0009_legacy_roles.py','0010_token_hook.py','0011_membership_binding.py']:
            path = OWNER/'versions'/name
            captured[path] = path.read_bytes()
            # Execute the exact captured source that the fixture digest binds.
            spec=importlib.util.spec_from_file_location('projection_source_'+name[:4],path)
            revision=importlib.util.module_from_spec(spec)
            exec(compile(captured[path], str(path), 'exec'), revision.__dict__)
            revisions.append(revision)
        db=engine(self.private['owner_urls']['membership_binding_reference'])
        try:
            with db.connect() as connection:
                transaction=connection.begin()
                try:
                    connection.execute(text("SET LOCAL statement_timeout='60s'; SET LOCAL lock_timeout='5s'"))
                    assert baseline.preflight(connection,'clean')=='clean'
                    baseline.verify_projection_role(connection,staged=True)
                    baseline.verify_authority_roles(connection,staged=True)
                    baseline.verify_command_role(connection,staged=True)
                    baseline.verify_target_roles(connection,staged=True)
                    for source in baseline.source_sql():connection.exec_driver_sql(source)
                    connection.exec_driver_sql(revisions[0].LEGACY_INTEGRATION_SQL)
                    baseline.verify_catalog(connection,'owned')
                    connection.execute(text(revisions[1].ACTOR_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'actor')
                    connection.execute(text(revisions[2].PROJECTION_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'projection')
                    connection.execute(text(revisions[3].ORGANIZATION_SCHEMA_SQL))
                    baseline.verify_projection_role(connection)
                    baseline.verify_catalog(connection,'organization')
                    connection.execute(text(revisions[4].AUTHORITY_SCHEMA_SQL))
                    baseline.verify_catalog(connection,'authority')
                    connection.exec_driver_sql(revisions[5].COMMAND_SCHEMA_SQL, execution_options={'no_parameters': True})
                    baseline.verify_command_role(connection)
                    baseline.verify_catalog(connection,'command')
                    connection.exec_driver_sql(revisions[6].TARGET_SCHEMA_SQL, execution_options={'no_parameters': True})
                    baseline.verify_target_roles(connection)
                    baseline.verify_catalog(connection,'target')
                    connection.exec_driver_sql(revisions[7].PROFILE_FIELDS_SQL, execution_options={'no_parameters': True})
                    baseline.verify_profile_privileges(connection)
                    baseline.verify_catalog(connection,'profile')
                    connection.exec_driver_sql(revisions[8].LEGACY_ROLES_SQL, execution_options={'no_parameters': True})
                    baseline.verify_catalog(connection,'legacy_roles')
                    connection.exec_driver_sql(revisions[9].TOKEN_HOOK_SQL, execution_options={'no_parameters': True})
                    baseline.verify_catalog(connection,'token_hook')
                    connection.exec_driver_sql(revisions[10].MEMBERSHIP_BINDING_SQL, execution_options={'no_parameters': True})
                    fingerprints=baseline.catalog_fingerprints(baseline.target_catalog_snapshot(connection))
                finally:
                    transaction.rollback()
            with db.connect() as connection:
                connection.execute(text("SET LOCAL statement_timeout='60s'; SET LOCAL lock_timeout='5s'"))
                assert baseline.preflight(connection,'clean')=='clean'
                baseline.verify_projection_role(connection,staged=True)
                baseline.verify_authority_roles(connection,staged=True)
                baseline.verify_command_role(connection,staged=True)
                baseline.verify_target_roles(connection,staged=True)
        finally:db.dispose()
        reference={'_generated':'GENERATED by tests/qualify_identity_baseline.py --record-membership-binding-reference; change owning fixture/code, never hand-edit',
                   'source_pins':json.loads(captured[OWNER/'source-pins.json']),
                   'migration_sha256':sha(captured[OWNER/'versions/0011_membership_binding.py']),
                   'membership_binding':fingerprints}
        content=(json.dumps(reference,sort_keys=True,indent=2)+'\n').encode()
        temporary=OWNER/'.membership-binding-reference-recording';created=False
        try:
            descriptor=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(descriptor,'wb') as output:
                created=True;output.write(content);output.flush();os.fsync(output.fileno())
            assert all(path.read_bytes() == data for path,data in captured.items()), 'membership_binding_reference_source_changed'
            os.link(temporary,destination)
        finally:
            if created:temporary.unlink(missing_ok=True)
        self.records.append({'label':'trusted-membership-binding-reference','status':'passed','sha256':sha(content),'migration_sha256':reference['migration_sha256'],'known_source_case':'membership_binding_reference','rolled_back':True,'helper_sha256':sha(captured[module]),'source_sha256':{str(path.relative_to(OWNER)):sha(data) for path,data in captured.items()},'pin_update_required':True})
        self.persist();print('trusted-membership-binding-reference PASS',sha(content),flush=True)

    def sql(self, case, statement, values=None, role='owner_urls'):
        db = engine(self.private[role][case])
        try:
            with db.begin() as connection:
                result = connection.execute(text(statement), values or {})
                return result.fetchall() if result.returns_rows else []
        finally:
            db.dispose()

    def data_state(self, case, membership_without_revision=False):
        # New owner-only tables must remain unreadable to legacy integration roles.
        db = engine(self.private['owner_urls'][case])
        try:
            with db.connect() as connection:
                tables = list(connection.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='identity' AND table_type='BASE TABLE' AND table_name<>'alembic_version' ORDER BY table_name")).scalars())
                values = {}
                for table in tables:
                    # Names are catalog-selected owner tables, quoted as identifiers.
                    name = connection.dialect.identifier_preparer.quote(table)
                    projection="to_jsonb(t)-'revision'" if membership_without_revision and table=='org_member' else 'to_jsonb(t)'
                    rows = connection.exec_driver_sql('SELECT '+projection+' FROM identity.' + name + ' t').scalars().all()
                    values[table] = sha(json.dumps(sorted(rows, key=lambda row: json.dumps(row,sort_keys=True,default=str)),sort_keys=True,default=str).encode())
                for name in ['identity.alembic_version','supabase_migrations.schema_migrations']:
                    exists = connection.execute(text('SELECT to_regclass(:name)'), {'name':name}).scalar_one()
                    rows = connection.exec_driver_sql('SELECT to_jsonb(t) FROM ' + name + ' t').scalars().all() if exists else None
                    values[name] = sha(json.dumps(sorted(rows,key=lambda row:json.dumps(row,sort_keys=True)) if rows is not None else None,sort_keys=True).encode())
                return values
        finally:
            db.dispose()

    def original_ledger(self, case):
        self.sql(case, 'CREATE SCHEMA supabase_migrations; CREATE TABLE supabase_migrations.schema_migrations(version text PRIMARY KEY,name text NOT NULL)',role='databases')
        for name in baseline.SOURCE_NAMES:
            self.sql(case,'INSERT INTO supabase_migrations.schema_migrations VALUES (:version,:name)', {'version':name[:14],'name':name[15:-4]},role='databases')
        self.sql(case,'GRANT USAGE ON SCHEMA supabase_migrations TO identity_migrator; GRANT SELECT ON supabase_migrations.schema_migrations TO identity_migrator',role='databases')

    def row_fixtures(self, case):
        ids = [str(uuid.uuid4()) for _ in range(4)]
        for user in ids[:2]:
            self.sql(case,'INSERT INTO auth.users(id,email) VALUES (:id,:email)', {'id':user,'email':'synthetic-'+user+'@example.invalid'},role='databases')
        for index,organization in enumerate(ids[2:]):
            self.sql(case,"INSERT INTO identity.org(id,name,slug) VALUES (:id,'Synthetic organization',:slug)", {'id':organization,'slug':'synthetic-'+organization})
            self.sql(case,'INSERT INTO identity.org_member(org_id,user_id) VALUES (:org,:account)', {'org':organization,'account':ids[index]})
        # Temporarily supply creation-only FK authority, then restore exact legacy ACLs.
        # Existing FK constraints survive REVOKE, representing preexisting consumers.
        original_acls=self.sql(case,FIXTURE_REFERENCE_ACLS_SQL)
        assert {row[0] for row in original_acls}=={'schema','users','org'}
        self.sql(case,'GRANT USAGE ON SCHEMA identity TO postgres; GRANT REFERENCES (id) ON identity.users,identity.org TO postgres')
        try:
            for schema in ['finance','cs']:
                self.sql(case,'CREATE SCHEMA '+schema+'; CREATE TABLE '+schema+'.identity_reference(actor_id uuid REFERENCES identity.users(id),org_id uuid REFERENCES identity.org(id))',role='databases')
                self.sql(case,'INSERT INTO '+schema+'.identity_reference VALUES (:actor,:org)', {'actor':ids[0],'org':ids[2]},role='databases')
        finally:
            for name,acl,had_direct_grant in original_acls:
                if not had_direct_grant:
                    statement=('REVOKE USAGE ON SCHEMA identity FROM postgres' if name=='schema'
                               else 'REVOKE REFERENCES (id) ON identity.'+name+' FROM postgres')
                    self.sql(case,statement)
            assert self.sql(case,FIXTURE_REFERENCE_ACLS_SQL)==original_acls, 'fixture_reference_acls_changed'

        return ids

    def external_state(self, case):
        rows = self.sql(case,"SELECT n.nspname,c.relname,k.conname,pg_get_constraintdef(k.oid) FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('finance','cs') ORDER BY 1,2,3",role='databases')
        state = {'constraints': [list(row) for row in rows]}
        for schema in ['finance','cs']:
            state[schema] = [list(row) for row in self.sql(case,'SELECT actor_id::text,org_id::text FROM '+schema+'.identity_reference ORDER BY 1,2',role='databases')]
        return sha(json.dumps(state,sort_keys=True).encode())

    def runtime(self, case, ids):
        db = engine(self.private['runtime_urls'][case])
        try:
            with db.begin() as connection:
                assert connection.execute(text('SELECT session_user,current_user')).one() == ('access_runtime','access_runtime')
                connection.execute(text("SELECT set_config('app.org_id',:org,true),set_config('app.actor_id',:actor,true)"), {'org':ids[2],'actor':ids[0]})
                assert connection.execute(text('SELECT id::text FROM identity.org')).scalars().all() == [ids[2]]
                assert connection.execute(text('SELECT user_id::text FROM identity.org_member')).scalars().all() == [ids[0]]
                for statement in ['SELECT * FROM identity.users','UPDATE identity.org SET deleted_at=now()','UPDATE identity.users SET is_platform_admin=true']:
                    savepoint = connection.begin_nested()
                    try:
                        connection.execute(text(statement))
                    except Exception as error:
                        assert getattr(getattr(error,'orig',error),'sqlstate',None) == '42501'
                    else:
                        raise AssertionError('runtime_privileged_operation_allowed')
                    finally:
                        savepoint.rollback()
            with db.begin() as connection:
                assert connection.execute(text('SELECT id FROM identity.org')).all() == []
                assert connection.execute(text('SELECT user_id FROM identity.org_member')).all() == []
        finally:
            db.dispose()
        self.records.append({'label':'restricted-runtime-and-connection-reuse','status':'passed'})
        self.persist()

    def auth(self):
        self.command('native-clean','native')
        account_email = 'synthetic-' + str(uuid.uuid4()) + '@example.invalid'
        password = 'Synthetic-' + str(uuid.uuid4()) + '!'
        private_account = self.proof / ('synthetic-auth-' + str(uuid.uuid4()) + '.json')
        with private_account.open('x') as account_file:
            private_account.chmod(0o600)
            json.dump({'email':account_email,'password':password},account_file)
        def request(path,body=None,admin=False,token=None):
            key = self.private['service_role_key'] if admin else self.private['anon_key']
            headers = {'apikey':key,'authorization':'Bearer '+(token or key),'content-type':'application/json'}
            data = json.dumps(body).encode() if body is not None else None
            try:
                with urlopen(Request(self.private['api_url']+'/auth/v1/'+path,data=data,headers=headers),timeout=15) as response:
                    assert response.status in (200,201)
                    result = json.load(response)
                    self.records.append({'label':'auth-http','path':path.split('?')[0],'http_status':response.status})
                    self.persist()
                    return result
            except HTTPError as error:
                body = error.read(4096)
                try: payload = json.loads(body)
                except Exception: payload = {}
                codes = {name:value for name,value in payload.items() if name in ('error_code','code','error') and isinstance(value,(str,int)) and re.fullmatch(r'[a-zA-Z0-9_]+',str(value))}
                self.records.append({'label':'auth-http','path':path.split('?')[0],'http_status':error.code,'safe_codes':codes})
                self.persist()
                raise
        created = request('admin/users',{'email':account_email,'password':password,'email_confirm':True},admin=True)
        account = created['id']
        assert self.sql('native','SELECT id::text FROM identity.users WHERE id=:id',{'id':account}) == [(account,)]
        # ID-A proves owner hook/profile integration. Password/provider sign-in is
        # a separate Auth consumer gate; this fixture disables the email provider.
        # Vendor-local Auth role uses the explicitly selected local DB password.
        parsed = urlsplit(self.private['admin_url'])
        auth_url = urlunsplit(parsed._replace(netloc='supabase_auth_admin:'+quote(parsed.password or '',safe='')+'@'+parsed.hostname+':'+str(parsed.port)))
        db = engine(auth_url)
        try:
            with db.begin() as connection:
                assert connection.execute(text('SELECT session_user,current_user')).one() == ('supabase_auth_admin','supabase_auth_admin')
                event = {'user_id':account,'claims':{}}
                result = connection.execute(text('SELECT identity.custom_access_token_hook(CAST(:event AS jsonb))'),{'event':json.dumps(event)}).scalar_one()
                assert result['claims']['user_roles'] == []
                assert result['claims']['member_id'] is None
        finally:
            db.dispose()
        # Characterize the retained PUBLIC helper without inventing Auth INSERT rights.
        assert self.sql('native',"SELECT has_function_privilege('anon','identity.create_user(text)','EXECUTE')") == [(True,)]
        db = engine(self.private['owner_urls']['native'])
        try:
            with db.connect() as connection:
                transaction = connection.begin()
                try:
                    connection.execute(text("SELECT identity.create_user('unused-synthetic@example.invalid')"))
                except Exception as error:
                    assert getattr(getattr(error,'orig',error),'sqlstate',None) == '42501'
                else:
                    raise AssertionError('legacy_helper_gained_auth_insert')
                finally:
                    transaction.rollback()
        finally:
            db.dispose()
        self.command('native-repeat','native')
        self.records.append({'label':'native-auth-api-profile-and-hook','status':'passed','hook_role':'supabase_auth_admin','hook_configuration':'invoked directly, not enabled in vendor JWT pipeline','profile_account_only':True,'password_signin_qualified':False,'legacy_helper_auth_insert_denied':True})
        self.persist()

    def review_regressions(self):
        """Focused review cases on separately prepared synthetic databases only."""
        def empty_state(case):
            return self.sql(case,"SELECT c.relname,c.relkind FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='identity' ORDER BY 1"), self.sql(case,"SELECT n.nspname,p.proname,pg_get_functiondef(p.oid) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='identity' OR (n.nspname='public' AND p.proname='get_user_roles') ORDER BY 1,2"), self.sql(case,"SELECT tgname,pg_get_triggerdef(oid) FROM pg_trigger WHERE tgrelid='auth.users'::regclass AND NOT tgisinternal ORDER BY 1"), self.data_state(case)
        # Bare upgrade base must not poison an otherwise eligible empty target.
        before = empty_state('upgrade_base')
        self.command('empty-upgrade-base-refuse','upgrade_base',expected='identity_unknown_history',action=('upgrade','base'))
        assert empty_state('upgrade_base') == before
        # Force failure after source one has written tables/types/seeds, when the
        # second source installs its external Auth trigger. No test-only migration switch.
        self.sql('rollback','REVOKE TRIGGER ON auth.users FROM identity_migrator',role='databases')
        before = empty_state('rollback')
        self.command('mid-source-failure-rollback','rollback',expected='identity_migration_failed_requires_reconciliation')
        assert empty_state('rollback') == before
        self.sql('rollback','GRANT TRIGGER ON auth.users TO identity_migrator',role='databases')
        self.command('rollback-reconciled-clean','rollback')
        # A real elevated runtime profile is rejected by transactional postflight.
        parsed = urlsplit(self.private['admin_url'])
        admin_url = urlunsplit(parsed._replace(netloc='supabase_admin:'+quote(parsed.password or '',safe='')+'@'+parsed.hostname+':'+str(parsed.port)))
        admin = engine(admin_url)
        before = empty_state('upgrade_base')
        try:
            with admin.begin() as connection:
                connection.exec_driver_sql('ALTER ROLE access_runtime BYPASSRLS')
            self.command('elevated-runtime-clean-refuse','upgrade_base',expected='identity_catalog_mismatch:roles')
            assert empty_state('upgrade_base') == before
        finally:
            with admin.begin() as connection:
                connection.exec_driver_sql('ALTER ROLE access_runtime NOBYPASSRLS')
            admin.dispose()
        self.command('restricted-runtime-clean','upgrade_base')
        # Column privileges on the private history cannot escape table REVOKE.
        self.sql('upgrade_base','GRANT UPDATE(version_num) ON identity.alembic_version TO authenticated')
        before = self.data_state('upgrade_base')
        self.command('ledger-column-grant-refuse','upgrade_base',expected='identity_unknown_history')
        assert self.data_state('upgrade_base') == before
        self.sql('upgrade_base','REVOKE UPDATE(version_num) ON identity.alembic_version FROM authenticated')
        self.command('ledger-column-reconciled','upgrade_base')
        # Original Supabase history has independent refusal cases, including retries.
        self.legacy('legacy_history')
        self.original_ledger('legacy_history')
        self.review_history_regressions()
        self.review_composition()
        self.review_populated_auth()

    def review_history_regressions(self):
        version,name = baseline.SOURCE_NAMES[0][:14],baseline.SOURCE_NAMES[0][15:-4]
        changes = [('partial', 'DELETE FROM supabase_migrations.schema_migrations WHERE version=:version'),
                   ('misnamed', "UPDATE supabase_migrations.schema_migrations SET name='platform_identity_wrong' WHERE version=:version"),
                   ('unknown', "INSERT INTO supabase_migrations.schema_migrations VALUES ('20990101000000','platform_identity_unknown')")]
        for label,statement in changes:
            self.sql('legacy_history',statement,{'version':version},role='databases')
            catalog,data = self.snapshot('legacy_history'),self.data_state('legacy_history')
            self.command('legacy-'+label+'-refuse','legacy_history',mode='adopt',expected='identity_unknown_legacy_history')
            assert self.snapshot('legacy_history') == catalog and self.data_state('legacy_history') == data
            self.sql('legacy_history',"DELETE FROM supabase_migrations.schema_migrations WHERE version IN (:version,'20990101000000')",{'version':version},role='databases')
            self.sql('legacy_history',"INSERT INTO supabase_migrations.schema_migrations VALUES (:version,:name)",{'version':version,'name':name},role='databases')
        self.command('legacy-ledger-reconciled','legacy_history',mode='adopt')
        self.sql('legacy_history',changes[-1][1],role='databases')
        before = self.data_state('legacy_history')
        self.command('owned-unknown-legacy-refuse','legacy_history',expected='identity_unknown_legacy_history')
        assert self.data_state('legacy_history') == before
        self.original_ledger('clean_history')
        before = self.data_state('clean_history')
        self.command('clean-conflicting-original-ledger','clean_history',expected='identity_conflicting_legacy_history')
        assert self.data_state('clean_history') == before
        assert not self.sql('clean_history', "SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='identity'")
    def review_composition(self):
        # Execute actual retained composition sources and both seeds as their caller.
        self.command('composition-identity-first','composition')
        # Minimal external Storage contract fixture; vendor Storage runtime is not
        # under test here. Native Auth integration is proved separately.
        self.sql('composition','CREATE SCHEMA storage; CREATE TABLE storage.buckets(id text PRIMARY KEY,name text,public boolean,file_size_limit bigint,allowed_mime_types text[])',role='databases')
        sys.path.insert(0,str(ROOT))
        from tools.py import run_compose_supabase as compose
        modules=[compose.Module('platform',ROOT/'platform'),compose.Module('expense',ROOT/'apps/expense'),compose.Module('scribeswell',ROOT/'apps/scribeswell')]
        migrations=compose.select_identity_authority(compose.collect_migrations(modules),'owned')
        for migration in migrations:
            self.sql('composition',migration.source_path.read_text(),role='databases')
            self.records.append({'label':'composed-source','file':migration.repo_relative_source,'status':'passed'})
            self.persist()
        for seed in [ROOT/'platform/supabase/seeds/001_identity.sql',ROOT/'apps/expense/supabase/seeds/010_finance.sql']:
            self.sql('composition',seed.read_text(),role='databases')
        assert self.sql('composition',"SELECT count(*) FROM identity.org WHERE slug='kok-home'") == [(1,)]
        self.command('composition-seeded-repeat','composition')
        # All source sequences are PostgreSQL identity sequences: ordinary OWNED BY
        # cannot detach them (the review's suggested sequence mutation is forbidden).
        db = engine(self.private['owner_urls']['composition'])
        try:
            with db.connect() as connection:
                transaction=connection.begin()
                try:
                    connection.exec_driver_sql('ALTER SEQUENCE identity.org_member_id_seq OWNED BY NONE')
                except Exception as error:
                    assert getattr(getattr(error,'orig',error),'sqlstate',None) == '0A000'
                else:
                    raise AssertionError('identity_sequence_dependency_detached')
                finally:
                    transaction.rollback()
        finally:
            db.dispose()
        self.records.append({'label':'review-history-rollback-role-composition-regressions','status':'passed','composed_migrations':len(migrations),'retained_seeds':2})
        self.persist()

    def review_populated_auth(self):
        self.command('populated-auth-clean','populated_auth')
        case='populated_auth'
        account,active_org,inactive_org=[str(uuid.uuid4()) for _ in range(3)]
        self.sql(case,'INSERT INTO auth.users(id,email) VALUES (:id,:email)',{'id':account,'email':'synthetic-'+account+'@example.invalid'},role='databases')
        for organization in [active_org,inactive_org]:
            self.sql(case,"INSERT INTO identity.org(id,name,slug) VALUES (:id,'Synthetic hook organization',:slug)",{'id':organization,'slug':'hook-'+organization})
        active_member=self.sql(case,'INSERT INTO identity.org_member(org_id,user_id,is_owner) VALUES (:org,:account,true) RETURNING id',{'org':active_org,'account':account})[0][0]
        self.sql(case,'INSERT INTO identity.org_member(org_id,user_id,deleted_at) VALUES (:org,:account,now())',{'org':inactive_org,'account':account})
        active_role=self.sql(case,"INSERT INTO identity.member_role(member_id,role) VALUES (:member,'employee') RETURNING id",{'member':active_member})[0][0]
        self.sql(case,"INSERT INTO identity.member_role(member_id,role,deleted_at) VALUES (:member,'admin',now())",{'member':active_member})
        parsed=urlsplit(self.private['databases'][case])
        auth_url=urlunsplit(parsed._replace(netloc='supabase_auth_admin:'+quote(parsed.password or '',safe='')+'@'+parsed.hostname+':'+str(parsed.port)))
        db=engine(auth_url)
        try:
            with db.connect() as connection:
                assert connection.execute(text('SELECT session_user,current_user')).one()==('supabase_auth_admin','supabase_auth_admin')
                result=connection.execute(text('SELECT identity.custom_access_token_hook(CAST(:event AS jsonb))'),{'event':json.dumps({'user_id':account,'claims':{}})}).scalar_one()['claims']
                assert result['org_id']==active_org and result['org_slug']=='hook-'+active_org
                assert result['member_id']==active_member and result['is_org_owner'] is True
                assert result['user_roles']==['employee'] and result['role_ids']==[active_role]
                assert result['org_ids']==[active_org]
        finally:
            db.dispose()
        self.command('populated-auth-repeat','populated_auth')
        self.records.append({'label':'populated-auth-active-and-deleted-member-role-claims','status':'passed','actual_login':'supabase_auth_admin','synthetic_scratch_accounts_only':True})
        self.persist()

    def verify(self, native_auth=True):
        self.command('clean-repeat','clean')
        ids = self.row_fixtures('legacy')
        self.original_ledger('legacy')
        # Fixture preparation restores the exact trusted legacy catalog.
        baseline.compare_catalog(baseline.catalog_fingerprints(self.snapshot('legacy')),baseline.trusted_reference('legacy'))
        before = self.data_state('legacy')
        external = self.external_state('legacy')
        self.command('legacy-adopt','legacy',mode='adopt')
        after = self.data_state('legacy')
        assert all(after[key] == value for key,value in before.items() if key!='identity.alembic_version')
        assert self.external_state('legacy') == external
        state = self.data_state('legacy')
        self.command('legacy-repeat','legacy',mode='adopt')
        assert self.data_state('legacy') == state
        assert baseline.catalog_fingerprints(self.snapshot('legacy')) == baseline.trusted_actor_reference()
        self.runtime('legacy',ids)
        # New foreign-key consumers also work through the post-adoption narrow grant.
        self.sql('legacy','CREATE TABLE finance.new_reference(actor_id uuid REFERENCES identity.users(id),org_id uuid REFERENCES identity.org(id))',role='databases')
        for case in ['mismatch_acl','mismatch_trigger','mismatch_owner','mismatch_default','mismatch_history','mismatch_columns']:
            if case=='mismatch_owner':
                name = urlsplit(self.private['databases'][case]).path[1:]
                self.sql(case,'GRANT CREATE ON DATABASE '+name+' TO identity_migrator',role='databases')
                self.sql(case,'ALTER SCHEMA identity RENAME TO identity_empty_retained')
                self.sql(case,'CREATE SCHEMA identity; GRANT USAGE,CREATE ON SCHEMA identity TO identity_migrator WITH GRANT OPTION; REVOKE CREATE ON DATABASE '+name+' FROM identity_migrator',role='databases')
            self.legacy(case)
            change = {'mismatch_acl':'GRANT SELECT ON identity.org TO anon',
                      'mismatch_trigger':'ALTER TABLE identity.users DISABLE TRIGGER audit_identity_users',
                      'mismatch_owner':None,
                      'mismatch_default':'ALTER DEFAULT PRIVILEGES IN SCHEMA identity GRANT SELECT ON TABLES TO anon',
                      'mismatch_history':"CREATE TABLE identity.alembic_version(version_num varchar(32) NOT NULL PRIMARY KEY); REVOKE ALL ON identity.alembic_version FROM PUBLIC,anon,authenticated,service_role,supabase_auth_admin,access_runtime; INSERT INTO identity.alembic_version VALUES ('identity_unknown')",
                      'mismatch_columns':'ALTER TABLE identity.users ADD COLUMN unexpected_fixture integer'}[case]
            if change:self.sql(case,change)
            before_catalog = self.snapshot(case)
            before_data = self.data_state(case)
            self.command(case+'-refuse',case,mode='adopt',expected='identity_unknown_history' if case=='mismatch_history' else 'identity_catalog_mismatch')
            assert self.snapshot(case) == before_catalog
            assert self.data_state(case) == before_data
        before = self.data_state('legacy')
        self.command('bare-stamp-refuse','legacy',expected='identity_use_verified_upgrade_route',action=('stamp','head'))
        self.command('downgrade-refuse','legacy',expected='identity_use_verified_upgrade_route',action=('downgrade','base'))
        assert self.data_state('legacy') == before
        if native_auth:
            self.auth()
        self.records.append({'label':'all-matrix-scenarios' if native_auth else 'database-matrix-scenarios','native_auth_included':native_auth,'status':'passed','business_rows_and_original_history_preserved':True,'external_fk_values_and_definitions_preserved':True})
        self.persist()

def main():
    if sys.argv[1:] == ['--record-membership-binding-reference'] and not __debug__:
        raise RuntimeError('membership_binding_reference_optimized_python_prohibited')
    if sys.argv[1:] == ['--record-token-hook-reference'] and not __debug__:
        raise RuntimeError('token_hook_reference_optimized_python_prohibited')
    if sys.argv[1:] == ['--record-legacy-role-reference'] and not __debug__:
        raise RuntimeError('legacy_roles_reference_optimized_python_prohibited')
    if sys.argv[1:] == ['--record-profile-reference'] and not __debug__:
        raise RuntimeError('profile_reference_optimized_python_prohibited')
    if sys.argv[1:] == ['--record-target-reference'] and not __debug__:
        raise RuntimeError('target_reference_optimized_python_prohibited')
    proof, private = fixture()
    q = Qualification(proof, private)
    if sys.argv[1:] == ['--record-membership-binding-reference']:
        q.record_membership_binding_reference()
        return
    if sys.argv[1:] == ['--record-token-hook-reference']:
        q.record_token_hook_reference()
        return
    if sys.argv[1:] == ['--record-legacy-role-reference']:
        q.record_legacy_roles_reference()
        return
    if sys.argv[1:] == ['--record-profile-reference']:
        q.record_profile_reference()
        return
    if sys.argv[1:] == ['--record-target-reference']:
        q.record_target_reference()
        return
    if sys.argv[1:] == ['--record-command-reference']:
        q.record_command_reference()
        return
    if sys.argv[1:] == ['--record-authority-reference']:
        q.record_authority_reference()
    elif sys.argv[1:] == ['--record-organization-reference']:
        q.record_organization_reference()
    elif sys.argv[1:] == ['--record-projection-reference']:
        q.record_projection_reference()
    elif sys.argv[1:] == ['--record-actor-reference']:
        q.record_actor_reference()
    elif sys.argv[1:] == ['--record-reference']:
        q.record_reference()
    elif sys.argv[1:] == ['--verify']:
        q.verify()
    elif sys.argv[1:] == ['--review-regressions']:
        q.review_regressions()
    else:
        raise AssertionError('qualification_arguments_invalid')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('identity_qualification_failed:' + type(error).__name__, file=sys.stderr)
        raise SystemExit(1) from None
