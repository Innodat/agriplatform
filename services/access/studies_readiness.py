"""Read-only owner release preparation for opt-in Studies; never provisioning."""
import json
import re
from hashlib import sha256
from pathlib import Path
from uuid import UUID

HERE=Path(__file__).resolve().parent
IDENTITY_HEAD='identity_0026'
ACCESS_HEAD='access_0019'
ARTIFACT_VERSION=2
RUNTIME_SOURCES=('main.py','organization_check.py','studies_access.py','studies_identity.py','studies_contract.py','studies_readiness.py','identity_preferences.py','caller_policy.py','capability_contract.py','capability_check.py','identity_context.py','discovery.py','discovery_contract.py','discovery_query.py')
DATABASE_ROLES={'STUDIES_ACCESS_DATABASE_URL':'access_studies_runtime',
 'STUDIES_IDENTITY_DATABASE_URL':'identity_studies_reader_runtime',
 'STUDIES_IDENTITY_SETUP_DATABASE_URL':'identity_studies_setup_runtime'}

def runtime_hashes():return {name:sha256((HERE/name).read_bytes()).hexdigest() for name in RUNTIME_SOURCES}

def source_hashes():
    ACCESS=HERE;ROOT=HERE.parent.parent
    paths=[ACCESS/name for name in (*RUNTIME_SOURCES,'main.py','organization_check.py','studies_contract.py','studies_identity.py','studies_access.py','studies_readiness.py','export_openapi.py','openapi.json','STUDIES-ENROLLMENT.md')]
    paths += [ACCESS/name for name in ('identity-migrations/versions/0021_studies_account_setup.py','identity-migrations/identity_baseline.py','identity-migrations/identity_studies_catalog.py','identity-migrations/studies_migration_support.py','identity-migrations/studies-setup-reference.json','migrations/versions/0016_studies_account_enrollment.py','migrations/access_baseline.py','migrations/access_studies_catalog.py','migrations/studies_migration_support.py','deployment/manifest.json','tools/prepare_studies_runtime_roles.sql','tools/prepare_studies_auth_evidence.sql')]
    paths += [ACCESS/'tests/qualify_studies_enrollment.py',ACCESS/'tests/test_studies_access.py',ACCESS/'tests/test_studies_identity.py',ACCESS/'tests/studies_types.test.ts',ACCESS/'tests/inspect_studies_enrollment.py',ROOT/'platform/deployment/release.py',ROOT/'platform/deployment/host-release.py',ROOT/'platform/deployment/tests/test_release.py',ROOT/'platform/deployment/tests/test_host.py',ACCESS/'tests/test_studies_readiness.py',ROOT/'platform/docs/architecture/contracts/scribeswell-study-enrollment.md',ROOT/'apps/scribeswell/docs/PERSONAL_NOTES_V1.md']
    # Current owner verification transitively relies on the complete immutable
    # migration/catalogue/reference chain, including the Identity source pins.
    for directory in ('identity-migrations','migrations'):
        paths += [path for path in (ACCESS/directory).rglob('*') if path.is_file() and path.suffix in ('.py','.json','.ini')]
    paths += [ROOT/name for name in json.loads((ACCESS/'identity-migrations/source-pins.json').read_bytes())]
    paths += [ACCESS/'identity-alembic.ini',ACCESS/'alembic.ini',ACCESS/'tests/qualify_studies_current.py',ROOT/'apps/scribeswell/tests/studies_owner_fixture.py',ROOT/'platform/deployment/environments/scribeswell-local.json']
    # The current native helper delegates fixture setup and verification to
    # these sources; retain them as executed qualification inputs as well.
    paths += list((ROOT/'platform/deployment').glob('*.py'))
    paths += [ROOT/'platform/deployment/registry.json']
    for directory in ('studies-migrations','tools/sql','supabase/migrations'):
        paths += [path for path in (ROOT/'apps/scribeswell'/directory).rglob('*') if path.is_file() and path.suffix in ('.py','.sql','.json')]
    paths += list((ROOT/'platform/deployment/schema').glob('*.json'))
    paths += list((ACCESS/'tools').glob('*.sql'))
    paths += [path for path in (ACCESS/'contracts/generated').rglob('*') if path.is_file()]
    return {str(path.relative_to(ROOT)):sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}


def closed_json(raw):
    def pairs(items):
        value={}
        for key,item in items:
            if key in value:raise ValueError('duplicate_json_key')
            value[key]=item
        return value
    return json.loads(raw,object_pairs_hook=pairs)


def validate_sources(recorded):
    root=HERE.parent.parent
    if not isinstance(recorded,dict) or not recorded:raise ValueError('studies_qualification_missing_or_stale')
    for relative,digest in recorded.items():
        if not isinstance(relative,str):raise ValueError('studies_qualification_missing_or_stale')
        path=Path(relative)
        if path.is_absolute() or '..' in path.parts or path.as_posix()!=relative or not (root/path).resolve().is_relative_to(root.resolve()):
            raise ValueError('studies_qualification_missing_or_stale')
        if not isinstance(digest,str) or not re.fullmatch('[a-f0-9]{64}',digest) or sha256((root/path).read_bytes()).hexdigest()!=digest:
            raise ValueError('studies_qualification_missing_or_stale')
    if recorded!=source_hashes():raise ValueError('studies_qualification_missing_or_stale')

STAGE_FIELDS={
 'current-first-use-race.json':('first_use_absent_actor_and_grant','one_initial_grant_event_and_actor_event','canonical_check','zero_memberships'),
 'boundaries.json':('partial_actor_without_grant','collision_unverified_deleted_refused','fresh_context','lost_response_retry','revoked_replay_denied','one_initial_grant_event'),
 'current-denials.json':('banned_missing_deleted_system_keyed_refused','disabled_check_new_enrollment_replay_denied','availability_restored_by_protected_command','same_operation_retry_after_fresh_evidence','uncommitted_outcome_and_grant_absent'),
 'confirmed-http-denials.json':('live_provider_still_verified','local_current_auth_denial_precedes_retained_grant'),
 'current-cli-proof.json':('failure_ledgers_preserved','source_populated_upgrade'),
 'current-clean-upgrade-proof.json':('empty_owner_histories','no_account_or_grant_seeds'),
 'provider-proof.json':('native_identity_hook','isolated_profile_hook','zero_memberships'),
 'lock-eligibility.json':('account_and_actor_locks_observed','ban_delete_unverify_refused','no_actor_or_receipt_written','replay_denied')}

def validate_stage_proofs(proofs,sources):
    if set(proofs)!=set(STAGE_FIELDS):raise ValueError('studies_qualification_cases_missing')
    for name,fields in STAGE_FIELDS.items():
        value=proofs[name]
        if value.get('executed_sources')!=sources or any(value.get(field) is not True for field in fields):
            raise ValueError('studies_qualification_cases_missing_or_stale')
    if proofs['current-first-use-race.json'].get('initial_statuses')!=[200]*4:raise ValueError('studies_qualification_cases_missing')
    for name,field in [('boundaries.json','actual_sql_timeout_seconds'),('current-denials.json','write_lock_timeout_seconds')]:
        value=proofs[name].get(field)
        if type(value) not in (int,float) or not 0<value<1:raise ValueError('studies_qualification_cases_missing')
    denials=proofs['boundaries.json'].get('restricted_role_denials',[])
    expected=sorted((role,action) for role in DATABASE_ROLES.values() for action in ('SELECT','SELECT','SELECT','SET','SET'))
    if sorted(tuple(row) for row in denials)!=expected:raise ValueError('studies_qualification_cases_missing')
    results=proofs['confirmed-http-denials.json'].get('results',[])
    if sorted((row.get('status'),row.get('error_id'),row.get('path')) for row in results)!=sorted((403,error,path) for error in ('identity.verification_required','access_denied') for path in ('/v2/check','/v2/enrollments/scribeswell-studies')):raise ValueError('studies_qualification_cases_missing')
    cli=proofs['current-cli-proof.json']
    expected=[('cli-access-before-identity',1),('cli-identity-failure',1),('cli-identity-upgrade',0),('cli-identity-repeat',0),('cli-access-failure',1),('cli-access-upgrade',0),('cli-access-repeat',0)]
    if cli.get('activation_executed') is not False or [(row.get('stage'),row.get('exit_code')) for row in cli.get('results',[])]!=expected:raise ValueError('studies_qualification_cases_missing')
    if [(row.get('owner'),row.get('exit_code')) for row in proofs['current-clean-upgrade-proof.json'].get('ordered_owner_results',[])]!=[('identity',0),('access',0)]:raise ValueError('studies_qualification_cases_missing')
    return {name:True for name in ('first_use_race','actor_only_recovery','adopted_collision_current_denial','native_deadline','lost_response_revoked_replay','restricted_roles','clean_upgrade','populated_upgrade_failure_repeat','provider_profile_hook','current_auth_after_lock')}

def validate_qualification(record,directory):
    if record.get('schema_version')!=ARTIFACT_VERSION or type(record.get('schema_version')) is not int or record.get('identity_revision')!=IDENTITY_HEAD or record.get('access_revision')!=ACCESS_HEAD:raise ValueError('studies_qualification_missing_or_stale')
    validate_sources(record.get('sources'))
    if record.get('runtime_sources')!=runtime_hashes():raise ValueError('studies_qualification_missing_or_stale')
    if set(record.get('proof_sha256',{}))!=set(STAGE_FIELDS):raise ValueError('studies_qualification_cases_missing')
    proofs={}
    for name,digest in record['proof_sha256'].items():
        raw=(directory/name).read_bytes()
        if sha256(raw).hexdigest()!=digest:raise ValueError('studies_qualification_proof_changed')
        proofs[name]=json.loads(raw)
    if record.get('cases')!=validate_stage_proofs(proofs,record['sources']):raise ValueError('studies_qualification_cases_missing')

def validate_artifact(raw):
    try:
        value=closed_json(raw)
        expected={'schema_version','release_id','identity_revision','access_revision','service_actor_id',
            'runtime_sources','qualification_sha256','profile_hook_qualified','live_provider_qualified'}
        if set(value)!=expected or value['schema_version']!=ARTIFACT_VERSION or type(value['schema_version']) is not int:raise ValueError('schema')
        if value['identity_revision']!=IDENTITY_HEAD or value['access_revision']!=ACCESS_HEAD:raise ValueError('head')
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}',value['release_id']):raise ValueError('release')
        actor=UUID(value['service_actor_id'])
        if not actor.int or str(actor)!=value['service_actor_id']:raise ValueError('executor')
        if value['runtime_sources']!=runtime_hashes():raise ValueError('source')
        if not re.fullmatch('[a-f0-9]{64}',value['qualification_sha256']):raise ValueError('qualification')
        if value['profile_hook_qualified'] is not True or value['live_provider_qualified'] is not True:raise ValueError('proof')
        return value
    except (ValueError,TypeError,KeyError,AttributeError,OSError):raise ValueError('studies_readiness_missing_or_stale') from None

def prepare(identity_url,access_url,qualification_path,release_id):
    from sqlalchemy import create_engine,text
    from sqlalchemy.engine import make_url
    qualification=json.loads(Path(qualification_path).read_bytes())
    validate_qualification(qualification,Path(qualification_path).parent)
    observed={}
    for owner,url in [('identity',identity_url),('access',access_url)]:
        parsed=make_url(url)
        if parsed.username!=owner+'_migrator':raise ValueError('studies_preparation_owner_required')
        db=create_engine(parsed,pool_pre_ping=True,hide_parameters=True,connect_args={'connect_timeout':2})
        try:
            with db.connect() as c:
                c.exec_driver_sql('SET TRANSACTION READ ONLY')
                c.exec_driver_sql("SET LOCAL statement_timeout='2s';SET LOCAL lock_timeout='1s'")
                revision=c.exec_driver_sql('SELECT version_num FROM '+owner+'.alembic_version').scalar_one()
                if revision!=(IDENTITY_HEAD if owner=='identity' else ACCESS_HEAD):raise ValueError('studies_owner_upgrade_required')
                # Existing owner baselines verify actual routines, RLS, ACLs and
                # immutable source history; the ledger alone is insufficient.
                import sys
                directory=HERE/('identity-migrations' if owner=='identity' else 'migrations')
                previous=list(sys.path)
                try:
                    sys.path.insert(0,str(directory))
                    if owner=='identity':
                        from identity_baseline import verify_owned_postcondition
                        verify_owned_postcondition(c,require_head=True)
                    else:
                        from access_baseline import verify_postcondition
                        verify_postcondition(c)
                finally:sys.path[:]=previous
                if owner=='identity':
                    row=c.exec_driver_sql("SELECT p.executor_actor_id FROM identity.studies_runtime_principal p JOIN identity.actor a ON a.id=p.executor_actor_id WHERE p.database_login='identity_studies_setup_runtime' AND p.enabled AND a.kind='service' AND a.actor_key IS NOT NULL").one_or_none()
                    hook=c.exec_driver_sql("SELECT EXISTS(SELECT 1 FROM pg_trigger t JOIN pg_proc p ON p.oid=t.tgfoid JOIN pg_namespace n ON n.oid=p.pronamespace WHERE t.tgrelid='auth.users'::regclass AND t.tgname='on_auth_user_created' AND t.tgenabled='O' AND n.nspname='identity' AND p.proname='handle_new_user')").scalar_one()
                    if not hook:raise ValueError('studies_profile_hook_required')
                else:
                    row=c.exec_driver_sql("SELECT executor_actor_id FROM access.studies_runtime_principal WHERE database_login='access_studies_runtime' AND enabled").one_or_none()
                    registered=c.exec_driver_sql("SELECT EXISTS(SELECT 1 FROM access.applications a JOIN access.permissions p ON p.app_id=a.app_id WHERE a.app_id='scribeswell' AND a.enabled AND p.permission='scribeswell.studies.use' AND p.scope_kind='account')").scalar_one()
                    if not registered:raise ValueError('studies_registration_required')
                if row is None:raise ValueError('studies_runtime_principal_required')
                observed[owner]=str(row[0])
                for role in (('identity_studies_reader_runtime','identity_studies_setup_runtime') if owner=='identity' else ('access_studies_runtime',)):
                    safe=c.execute(text("SELECT rolcanlogin AND NOT (rolsuper OR rolinherit OR rolcreaterole OR rolcreatedb OR rolreplication OR rolbypassrls) AND NOT EXISTS(SELECT 1 FROM pg_auth_members m WHERE m.member=r.oid OR m.roleid=r.oid) FROM pg_roles r WHERE rolname=:role"),{'role':role}).scalar_one()
                    if not safe:raise ValueError('studies_runtime_role_unsafe')
                    raw=c.execute(text("SELECT EXISTS(SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('identity','access') AND c.relkind IN ('r','p') AND (has_table_privilege(:role,c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') OR has_any_column_privilege(:role,c.oid,'SELECT,INSERT,UPDATE,REFERENCES')))"),{'role':role}).scalar_one()
                    if raw:raise ValueError('studies_runtime_raw_privileges_unsafe')
        finally:db.dispose()
    if observed['identity']!=observed['access']:raise ValueError('studies_executor_preparation_mismatch')
    artifact={'schema_version':ARTIFACT_VERSION,'release_id':release_id,'identity_revision':IDENTITY_HEAD,'access_revision':ACCESS_HEAD,
        'service_actor_id':observed['identity'],'runtime_sources':runtime_hashes(),
        'qualification_sha256':sha256(Path(qualification_path).read_bytes()).hexdigest(),
        'profile_hook_qualified':True,'live_provider_qualified':True}
    validate_artifact(json.dumps(artifact))
    return artifact

if __name__=='__main__':
    import argparse,os
    parser=argparse.ArgumentParser();parser.add_argument('--qualification',required=True,type=Path)
    parser.add_argument('--release-id',required=True);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    try:
        artifact=prepare(os.environ['IDENTITY_MIGRATION_DATABASE_URL'],os.environ['ACCESS_MIGRATION_DATABASE_URL'],args.qualification,args.release_id)
        fd=os.open(args.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as output:json.dump(artifact,output,sort_keys=True);output.write('\n')
        print('studies_readiness_prepared')
    except Exception:
        print('studies_readiness_unavailable',file=__import__('sys').stderr)
        raise SystemExit(1) from None
