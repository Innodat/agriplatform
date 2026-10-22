"""Controlled native replay qualification; production custody is external."""
from pathlib import Path
import pytest
from sqlalchemy import create_engine, pool
from alembic import command
from alembic.config import Config
from test_owned_migrations import business_state, invoke, migration_url
from test_corpus_publication import controller_database, enabled, ACTOR
import baseline
from catalogue import snapshot

APP = Path(__file__).resolve().parents[1]
CUSTODY = dict(schema_version=1, source_id='tanakh', executor_actor_id=ACTOR,
               actor_kind='service', actor_key='fixture.controller', preparation_evidence_ref='fixture:identity')

@pytest.fixture
def staged(enabled):
    admin, url = enabled
    admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=false')
    if not admin.execute('SELECT 1 FROM scribeswell.book').fetchone():
        admin.execute("""INSERT INTO scribeswell.book VALUES (1,'Gen','Genesis','א','old','torah',1);
            INSERT INTO scribeswell.chapter VALUES (101,1,1);
            INSERT INTO scribeswell.verse VALUES (201,101,1,1,1);
            INSERT INTO scribeswell.word VALUES (301,201,1,'אָב','אָב','1','HNcmsa');
            INSERT INTO scribeswell.morpheme(id,word_id,segment_index,language,part_of_speech,pos_code)
            VALUES (401,301,0,'hebrew','noun','Ncmsa')""")
        for offset,table in enumerate(('chapter','verse','word','morpheme')):
            admin.execute("SELECT setval(%s::regclass,%s,true)",('scribeswell.'+table+'_id_seq',901+offset))
    yield admin, url


def engine_for(url):
    return create_engine(migration_url(url).replace('postgresql://', 'postgresql+psycopg://'), poolclass=pool.NullPool)


def direct(url, custody=CUSTODY):
    engine = engine_for(url)
    try:
        with engine.begin() as connection:
            return baseline.preflight_prepared(connection, custody)
    finally:
        engine.dispose()


def native(url, monkeypatch, attrs):
    monkeypatch.setenv('SCRIBESWELL_MIGRATION_DATABASE_URL', migration_url(url))
    config = Config(str(APP / 'alembic.ini'))
    config.attributes.update(attrs)
    command.upgrade(config, 'head')
    return config


def state(admin, url):
    engine = engine_for(url)
    try:
        with engine.begin() as connection:
            catalogue = snapshot(connection, head=True)
    finally:
        engine.dispose()
    return catalogue, business_state(admin), {t: admin.execute('SELECT * FROM scribeswell.'+t+' ORDER BY 1').fetchall()
        for t in ('alembic_version','corpus_operator_principal','corpus_operator_authority','corpus_fence_control','corpus_epoch','corpus_attempt','corpus_command_outcome','corpus_write_binding')}


def test_dormant_characterization(staged):
    admin, url = staged
    before = state(admin,url)
    result = invoke(url)
    assert result.returncode != 0 and 'scribeswell_catalogue_mismatch' in result.stderr
    assert invoke(url,extra_env={'SCRIBESWELL_VALIDATION_PROFILE':'prepared-controller-v1'}).returncode != 0
    assert state(admin,url) == before


def test_prepared_replay_preserves_everything(staged, monkeypatch):
    admin, url = staged
    before = state(admin,url)
    assert direct(url) == baseline.REVISION
    config = native(url,monkeypatch,dict(scribeswell_validation_profile='prepared-controller-v1',scribeswell_prepared_actor=CUSTODY))
    assert config.attributes['scribeswell_validated_profile'] == 'prepared-controller-v1'
    assert config.attributes['scribeswell_before'] == config.attributes['scribeswell_after'] == baseline.REVISION
    assert state(admin,url) == before

@pytest.mark.parametrize('change',[
    {'schema_version':True}, {'schema_version':1.0}, {'schema_version':2}, {'source_id':'bad/source'},
    {'actor_kind':'person'}, {'actor_key':'Bad'}, {'preparation_evidence_ref':'bad secret'},
    {'executor_actor_id':'00000000-0000-0000-0000-000000000000'},
    {'executor_actor_id':'22222222222242228222222222222222'}, {'extra':'override'},
    {'executor_actor_id':None}, {'source_id':[]},
])
def test_closed_custody_denied_without_changes(staged,change):
    admin,url=staged
    before=state(admin,url)
    with pytest.raises(baseline.BaselineError,match='scribeswell_prepared_custody_invalid'):
        direct(url,CUSTODY|change)
    assert state(admin,url)==before

@pytest.mark.parametrize('value',[None,{},[],{k:v for k,v in CUSTODY.items() if k!='actor_key'}])
def test_missing_custody_denied(staged,value):
    _,url=staged
    with pytest.raises(baseline.BaselineError,match='custody_invalid'):direct(url,value)

@pytest.mark.parametrize('change',[
    {'source_id':'other'}, {'executor_actor_id':'33333333-3333-4333-8333-333333333333'},
    {'actor_key':'other'}, {'preparation_evidence_ref':'other'},
])
def test_custody_mismatch(staged,change):
    admin,url=staged;before=state(admin,url)
    with pytest.raises(baseline.BaselineError,match='custody_mismatch'):direct(url,CUSTODY|change)
    assert state(admin,url)==before

@pytest.mark.parametrize('attrs',[
    {'scribeswell_validation_profile':None}, {'scribeswell_validation_profile':'other'},
    {'scribeswell_prepared_actor':CUSTODY}, {'scribeswell_validation_profile':'dormant','scribeswell_prepared_actor':CUSTODY},
    {'scribeswell_validation_profile':'prepared-controller-v1'},
    {'scribeswell_validation_profile':'prepared-controller-v1','scribeswell_prepared_actor':None},
])
def test_invalid_native_selection(staged,monkeypatch,attrs):
    admin,url=staged;before=state(admin,url)
    with pytest.raises(baseline.BaselineError):native(url,monkeypatch,attrs)
    assert state(admin,url)==before

@pytest.mark.parametrize('change,restore',[
    ('ALTER ROLE scribeswell_corpus_operator SUPERUSER','ALTER ROLE scribeswell_corpus_operator NOSUPERUSER'),
    ('ALTER ROLE scribeswell_corpus_operator BYPASSRLS','ALTER ROLE scribeswell_corpus_operator NOBYPASSRLS'),
    ('ALTER ROLE scribeswell_corpus_operator CREATEDB','ALTER ROLE scribeswell_corpus_operator NOCREATEDB'),
    ('ALTER ROLE scribeswell_corpus_operator CREATEROLE','ALTER ROLE scribeswell_corpus_operator NOCREATEROLE'),
    ('ALTER ROLE scribeswell_corpus_operator REPLICATION','ALTER ROLE scribeswell_corpus_operator NOREPLICATION'),
    ('ALTER ROLE scribeswell_corpus_operator INHERIT','ALTER ROLE scribeswell_corpus_operator NOINHERIT'),
    ('ALTER ROLE scribeswell_corpus_operator NOLOGIN','ALTER ROLE scribeswell_corpus_operator LOGIN'),
    ('GRANT scribeswell_import TO scribeswell_corpus_operator','REVOKE scribeswell_import FROM scribeswell_corpus_operator'),
    ('GRANT scribeswell_corpus_operator TO scribeswell_runtime','REVOKE scribeswell_corpus_operator FROM scribeswell_runtime'),
    ("ALTER ROLE scribeswell_corpus_operator SET search_path=public",'ALTER ROLE scribeswell_corpus_operator RESET ALL'),
    ('GRANT CREATE ON SCHEMA public TO scribeswell_corpus_operator','REVOKE CREATE ON SCHEMA public FROM scribeswell_corpus_operator'),
    ('GRANT SELECT ON scribeswell.book TO scribeswell_corpus_operator','REVOKE SELECT ON scribeswell.book FROM scribeswell_corpus_operator'),
    ('GRANT UPDATE(name_en) ON scribeswell.book TO scribeswell_corpus_operator','REVOKE UPDATE(name_en) ON scribeswell.book FROM scribeswell_corpus_operator'),
    ('GRANT USAGE ON SEQUENCE scribeswell.word_id_seq TO scribeswell_corpus_operator','REVOKE USAGE ON SEQUENCE scribeswell.word_id_seq FROM scribeswell_corpus_operator'),
    ('GRANT EXECUTE ON FUNCTION scribeswell.bind_corpus_write(text,bigint,uuid,text) TO scribeswell_corpus_operator','REVOKE EXECUTE ON FUNCTION scribeswell.bind_corpus_write(text,bigint,uuid,text) FROM scribeswell_corpus_operator'),
    ('GRANT EXECUTE ON FUNCTION scribeswell.execute_corpus_command(jsonb) TO scribeswell_corpus_operator WITH GRANT OPTION','REVOKE GRANT OPTION FOR EXECUTE ON FUNCTION scribeswell.execute_corpus_command(jsonb) FROM scribeswell_corpus_operator'),
    ('GRANT USAGE ON SCHEMA scribeswell TO scribeswell_corpus_operator WITH GRANT OPTION','REVOKE GRANT OPTION FOR USAGE ON SCHEMA scribeswell FROM scribeswell_corpus_operator'),
    ('REVOKE EXECUTE ON FUNCTION scribeswell.execute_corpus_command(jsonb) FROM scribeswell_corpus_operator','GRANT EXECUTE ON FUNCTION scribeswell.execute_corpus_command(jsonb) TO scribeswell_corpus_operator'),
    ('CREATE SCHEMA unrelated AUTHORIZATION scribeswell_corpus_operator','DROP SCHEMA unrelated'),
    ('CREATE SCHEMA unrelated;CREATE TABLE unrelated.secret(id int);GRANT SELECT ON unrelated.secret TO scribeswell_corpus_operator','DROP SCHEMA unrelated CASCADE'),
    ('CREATE SCHEMA unrelated;CREATE TABLE unrelated.secret(id int);GRANT SELECT(id) ON unrelated.secret TO scribeswell_corpus_operator','DROP SCHEMA unrelated CASCADE'),
    ('CREATE SCHEMA unrelated;CREATE SEQUENCE unrelated.secret;GRANT USAGE ON unrelated.secret TO scribeswell_corpus_operator','DROP SCHEMA unrelated CASCADE'),
    ('CREATE SCHEMA unrelated;CREATE FUNCTION unrelated.secret() RETURNS int LANGUAGE sql AS $$SELECT 1$$;GRANT EXECUTE ON FUNCTION unrelated.secret() TO scribeswell_corpus_operator','DROP SCHEMA unrelated CASCADE'),
    ('CREATE SCHEMA unrelated;GRANT USAGE ON SCHEMA unrelated TO PUBLIC;CREATE FUNCTION unrelated.secret() RETURNS int LANGUAGE sql SECURITY DEFINER AS $$SELECT 1$$','DROP SCHEMA unrelated CASCADE'),
    ('CREATE SCHEMA unrelated;ALTER DEFAULT PRIVILEGES IN SCHEMA unrelated GRANT SELECT ON TABLES TO scribeswell_corpus_operator','ALTER DEFAULT PRIVILEGES IN SCHEMA unrelated REVOKE SELECT ON TABLES FROM scribeswell_corpus_operator;DROP SCHEMA unrelated'),
    ('CREATE SCHEMA unrelated;CREATE TABLE unrelated.secret(id int);GRANT USAGE ON SCHEMA unrelated TO PUBLIC;GRANT SELECT ON unrelated.secret TO PUBLIC','DROP SCHEMA unrelated CASCADE'),
    ('CREATE TABLE scribeswell.extra(id int)','DROP TABLE scribeswell.extra'),
])
def test_authority_and_catalogue_denials_preserve_target(staged,change,restore):
    admin,url=staged
    admin.execute(change)
    try:
        before=state(admin,url)
        with pytest.raises(baseline.BaselineError):direct(url)
        assert state(admin,url)==before
    finally:admin.execute(restore)


def test_disabled_mappings_preserved(staged,monkeypatch):
    admin,url=staged
    admin.execute('UPDATE scribeswell.corpus_operator_principal SET enabled=false,revision=revision+1')
    admin.execute('UPDATE scribeswell.corpus_operator_authority SET enabled=false,revision=revision+1')
    before=state(admin,url)
    assert direct(url)==baseline.REVISION
    native(url,monkeypatch,dict(scribeswell_validation_profile='prepared-controller-v1',scribeswell_prepared_actor=CUSTODY))
    assert state(admin,url)==before

@pytest.mark.parametrize('change',[
    'DELETE FROM scribeswell.corpus_operator_authority',
    "DELETE FROM scribeswell.corpus_operator_authority WHERE command='corpus.seal'",
    "INSERT INTO scribeswell.corpus_operator_authority SELECT database_login,'other',command,enabled,revision,created_by_actor_id,updated_by_actor_id,created_at,updated_at FROM scribeswell.corpus_operator_authority",
    'UPDATE scribeswell.corpus_fence_control SET enforcement=true',
])
def test_configuration_denials(staged,change):
    admin,url=staged
    if change.startswith('DELETE'):
        retained=admin.execute("SELECT * FROM scribeswell.corpus_operator_authority WHERE command<>'corpus.seal'").fetchall() if 'WHERE' in change else []
        admin.execute('TRUNCATE scribeswell.corpus_operator_authority')
        for row in retained:admin.execute('INSERT INTO scribeswell.corpus_operator_authority VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',row)
    else:admin.execute(change)
    before=state(admin,url)
    with pytest.raises(baseline.BaselineError):direct(url)
    assert state(admin,url)==before

@pytest.mark.parametrize('revision',['scribeswell_0001','scribeswell_0002',None])
def test_requires_exact_existing_0003(staged,revision):
    admin,url=staged
    if revision is None:admin.execute('DROP TABLE scribeswell.alembic_version')
    else:admin.execute('UPDATE scribeswell.alembic_version SET version_num=%s',(revision,))
    try:
        with pytest.raises(baseline.BaselineError,match='revision_required'):direct(url)
    finally:
        if revision is None:
            admin.execute('CREATE TABLE scribeswell.alembic_version(version_num varchar(32), CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))')
            admin.execute('ALTER TABLE scribeswell.alembic_version OWNER TO scribeswell_migrator')
            admin.execute('REVOKE ALL ON scribeswell.alembic_version FROM PUBLIC,anon,authenticated,service_role,scribeswell_runtime,scribeswell_import')
            admin.execute('INSERT INTO scribeswell.alembic_version VALUES (%s)',(baseline.REVISION,))
        else:admin.execute('UPDATE scribeswell.alembic_version SET version_num=%s',(baseline.REVISION,))


def test_injected_postcheck_rolls_back_and_clears_profile(staged,monkeypatch):
    admin,url=staged;before=state(admin,url);original=baseline.preflight_prepared;calls=[]
    def injected(connection,expected):
        result=original(connection,expected);calls.append(1)
        if len(calls)==2:
            connection.exec_driver_sql("UPDATE scribeswell.book SET name_en='temporary' WHERE id=1")
            raise baseline.BaselineError('injected_postcheck')
        return result
    monkeypatch.setattr(baseline,'preflight_prepared',injected)
    monkeypatch.setenv('SCRIBESWELL_MIGRATION_DATABASE_URL',migration_url(url))
    config=Config(str(APP/'alembic.ini'))
    config.attributes.update(scribeswell_validation_profile='prepared-controller-v1',scribeswell_prepared_actor=CUSTODY,scribeswell_validated_profile='stale')
    with pytest.raises(baseline.BaselineError,match='injected_postcheck'):command.upgrade(config,'head')
    assert 'scribeswell_validated_profile' not in config.attributes
    assert state(admin,url)==before

@pytest.mark.parametrize('isolation',['REPEATABLE READ','SERIALIZABLE','AUTOCOMMIT'])
def test_requires_caller_owned_read_committed(staged,isolation):
    _,url=staged;engine=engine_for(url)
    try:
        with engine.connect().execution_options(isolation_level=isolation) as connection:
            if isolation!='AUTOCOMMIT':connection.begin()
            with pytest.raises(baseline.BaselineError,match='transaction_required'):
                baseline.preflight_prepared(connection,CUSTODY)
    finally:engine.dispose()


def test_read_only_denied(staged):
    _,url=staged;engine=engine_for(url)
    try:
        with engine.begin() as connection:
            connection.exec_driver_sql('SET TRANSACTION READ ONLY')
            with pytest.raises(baseline.BaselineError,match='transaction_required'):baseline.preflight_prepared(connection,CUSTODY)
    finally:engine.dispose()

@pytest.mark.parametrize('table',['epoch','history','binding'])
def test_any_history_rejected(staged,table):
    from test_corpus_publication import operator, execute, body
    admin,url=staged
    admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=true')
    with operator(url) as connection:
        receipt=execute(connection,body())
    admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=false')
    if table=='epoch':
        admin.execute('TRUNCATE scribeswell.corpus_attempt,scribeswell.corpus_command_outcome')
    elif table=='history':
        admin.execute('TRUNCATE scribeswell.corpus_epoch')
    else:
        admin.execute('TRUNCATE scribeswell.corpus_epoch,scribeswell.corpus_attempt,scribeswell.corpus_command_outcome')
        # Synthesize stale debris without retaining catalogue drift. Ordinary
        # commits clean this table through the deferred ALWAYS trigger.
        admin.execute('ALTER TABLE scribeswell.corpus_write_binding DISABLE TRIGGER corpus_binding_cleanup')
        try:
            admin.execute("INSERT INTO scribeswell.corpus_write_binding VALUES ('scribeswell_import',pg_backend_pid(),pg_current_xact_id(),'tanakh',1,%s,repeat('a',64))",(receipt.attempt_id,))
        finally:
            admin.execute('ALTER TABLE scribeswell.corpus_write_binding ENABLE ALWAYS TRIGGER corpus_binding_cleanup')
    actual=tuple(admin.execute('SELECT count(*) FROM scribeswell.'+name).fetchone()[0]
                 for name in ('corpus_epoch','corpus_attempt','corpus_command_outcome','corpus_write_binding'))
    assert actual=={'epoch':(1,0,0,0),'history':(0,1,1,0),'binding':(0,0,0,1)}[table]
    before=state(admin,url)
    with pytest.raises(baseline.BaselineError,match='dormant_state_required'):direct(url)
    assert state(admin,url)==before

@pytest.mark.parametrize('sql',[
    'UPDATE scribeswell.corpus_operator_principal SET enabled=false,revision=revision+1',
    'UPDATE scribeswell.corpus_operator_authority SET enabled=false,revision=revision+1',
    "INSERT INTO scribeswell.corpus_operator_authority SELECT database_login,'other',command,enabled,revision,created_by_actor_id,updated_by_actor_id,created_at,updated_at FROM scribeswell.corpus_operator_authority",
    'UPDATE scribeswell.corpus_fence_control SET enforcement=true',
])
def test_locks_block_configuration_writes(staged,sql):
    import psycopg
    from test_postgres_acceptance import role_url
    admin,url=staged;engine=engine_for(url)
    try:
        with engine.begin() as connection:
            baseline.preflight_prepared(connection,CUSTODY)
            assert connection.exec_driver_sql('SHOW statement_timeout').scalar()=='5s'
            assert connection.exec_driver_sql('SHOW lock_timeout').scalar()=='2s'
            locks=connection.exec_driver_sql("SELECT relname FROM pg_locks JOIN pg_class ON oid=relation WHERE pid=pg_backend_pid() AND mode='ShareLock' ORDER BY relname").scalars().all()
            assert locks==sorted(('corpus_operator_principal','corpus_operator_authority','corpus_fence_control','corpus_epoch','corpus_attempt','corpus_command_outcome','corpus_write_binding'))
            with psycopg.connect(role_url(url,'scribeswell_migrator'),autocommit=True) as writer:
                writer.execute("SET lock_timeout='150ms'")
                with pytest.raises(psycopg.errors.LockNotAvailable):writer.execute(sql)
            # Current reader and importer locks remain compatible.
            for role,table in [('scribeswell_runtime','book_read'),('scribeswell_import','book')]:
                with psycopg.connect(role_url(url,role),autocommit=True) as reader:
                    reader.execute("SET lock_timeout='150ms'")
                    reader.execute('SELECT * FROM scribeswell.'+table+' LIMIT 1')
                    if role=='scribeswell_import':
                        # The statement fence takes control FOR SHARE even with
                        # no matching rows, proving RowShareLock compatibility.
                        reader.execute('UPDATE scribeswell.book SET id=id WHERE false')
    finally:engine.dispose()

@pytest.mark.parametrize('failure',['selection','postcheck','offline','unsupported'])
def test_reused_success_config_cannot_retain_profile(staged,monkeypatch,failure):
    admin,url=staged
    config=native(url,monkeypatch,dict(scribeswell_validation_profile='prepared-controller-v1',scribeswell_prepared_actor=CUSTODY))
    assert config.attributes['scribeswell_validated_profile']=='prepared-controller-v1'
    before=state(admin,url)
    if failure=='selection':config.attributes['scribeswell_validation_profile']=None
    elif failure=='postcheck':
        original=baseline.preflight_prepared;calls=[]
        def fail(connection,actor):
            result=original(connection,actor);calls.append(1)
            if len(calls)==2:raise baseline.BaselineError('injected_postcheck')
            return result
        monkeypatch.setattr(baseline,'preflight_prepared',fail)
    with pytest.raises(baseline.BaselineError):
        if failure=='unsupported':command.stamp(config,'head')
        else:command.upgrade(config,'head',sql=failure=='offline')
    assert 'scribeswell_validated_profile' not in config.attributes
    assert state(admin,url)==before


def test_configuration_writer_first_fails_bounded_and_safe(staged):
    import time
    admin,url=staged
    before=state(admin,url)
    with admin.transaction():
        admin.execute('UPDATE scribeswell.corpus_operator_authority SET enabled=false,revision=revision+1')
        start=time.monotonic()
        with pytest.raises(baseline.BaselineError,match='^scribeswell_prepared_validation_failed$') as failure:
            direct(url)
        assert time.monotonic()-start<4
        assert failure.value.__cause__ is None and failure.value.__suppress_context__
        admin.execute('ROLLBACK')
    assert state(admin,url)==before


def test_autocommit_with_prior_query_still_denied(staged):
    _,url=staged;engine=engine_for(url)
    try:
        with engine.connect().execution_options(isolation_level='AUTOCOMMIT') as connection:
            connection.exec_driver_sql('SELECT 1')
            with pytest.raises(baseline.BaselineError,match='transaction_required'):
                baseline.preflight_prepared(connection,CUSTODY)
    finally:engine.dispose()


def test_orphan_preparation_bundle_denied(staged):
    admin,url=staged
    admin.execute('TRUNCATE scribeswell.corpus_operator_principal,scribeswell.corpus_operator_authority,scribeswell.corpus_command_outcome')
    before=state(admin,url)
    with pytest.raises(baseline.BaselineError,match='custody_mismatch'):direct(url)
    assert state(admin,url)==before


def test_other_object_class_authority_denied(staged):
    admin,url=staged
    admin.execute("CREATE SCHEMA unrelated;CREATE TYPE unrelated.secret AS ENUM ('one');GRANT USAGE ON TYPE unrelated.secret TO scribeswell_corpus_operator")
    try:
        before=state(admin,url)
        with pytest.raises(baseline.BaselineError,match='operator_authority'):direct(url)
        assert state(admin,url)==before
    finally:admin.execute('DROP SCHEMA unrelated CASCADE')

@pytest.mark.parametrize('change,restore,effective',[
    ('CREATE FOREIGN DATA WRAPPER profile_wrapper;GRANT USAGE ON FOREIGN DATA WRAPPER profile_wrapper TO PUBLIC',
     'DROP FOREIGN DATA WRAPPER profile_wrapper',
     "SELECT has_foreign_data_wrapper_privilege('scribeswell_corpus_operator','profile_wrapper','USAGE')"),
    ('CREATE FOREIGN DATA WRAPPER profile_wrapper;CREATE SERVER profile_server FOREIGN DATA WRAPPER profile_wrapper;GRANT USAGE ON FOREIGN SERVER profile_server TO PUBLIC',
     'DROP SERVER profile_server;DROP FOREIGN DATA WRAPPER profile_wrapper',
     "SELECT has_server_privilege('scribeswell_corpus_operator','profile_server','USAGE')"),
    ('GRANT CREATE ON TABLESPACE pg_default TO PUBLIC','REVOKE CREATE ON TABLESPACE pg_default FROM PUBLIC',
     "SELECT has_tablespace_privilege('scribeswell_corpus_operator','pg_default','CREATE')"),
    ('GRANT ALTER SYSTEM ON PARAMETER work_mem TO PUBLIC','REVOKE ALTER SYSTEM ON PARAMETER work_mem FROM PUBLIC',
     "SELECT has_parameter_privilege('scribeswell_corpus_operator','work_mem','ALTER SYSTEM')"),
    ('GRANT SET ON PARAMETER log_statement TO PUBLIC','REVOKE SET ON PARAMETER log_statement FROM PUBLIC',
     "SELECT has_parameter_privilege('scribeswell_corpus_operator','log_statement','SET')"),
])
def test_public_nonordinary_authority_denied(staged,change,restore,effective):
    admin,url=staged
    admin.execute(change)
    try:
        assert admin.execute(effective).fetchone()==(True,)
        before=state(admin,url)
        # These checks inspect grants only: never invoke foreign access, create
        # tablespaces or execute ALTER SYSTEM / privileged settings.
        with pytest.raises(baseline.BaselineError,match='operator_authority'):direct(url)
        assert state(admin,url)==before
        assert admin.execute(effective).fetchone()==(True,)
    finally:admin.execute(restore)


def test_ordinary_public_session_privileges_stay_compatible(staged):
    admin,url=staged
    admin.execute('GRANT SET ON PARAMETER work_mem TO PUBLIC')
    try:
        assert admin.execute("SELECT context FROM pg_settings WHERE name='work_mem'").fetchone()==('user',)
        assert admin.execute("SELECT has_database_privilege('scribeswell_corpus_operator',current_database(),'TEMP')").fetchone()==(True,)
        before=state(admin,url)
        assert direct(url)==baseline.REVISION
        assert state(admin,url)==before
    finally:admin.execute('REVOKE SET ON PARAMETER work_mem FROM PUBLIC')

@pytest.mark.parametrize('routine',['pg_read_file(text)','pg_ls_dir(text)'])
def test_public_protected_core_execute_denied(staged,routine):
    admin,url=staged
    initial=admin.execute("SELECT initprivs::text FROM pg_catalog.pg_init_privs WHERE classoid='pg_catalog.pg_proc'::regclass AND objoid=%s::regprocedure AND objsubid=0 AND privtype='i'",(routine,)).fetchone()
    assert initial is not None
    admin.execute('GRANT EXECUTE ON FUNCTION pg_catalog.'+routine+' TO PUBLIC')
    try:
        before=state(admin,url)
        with pytest.raises(baseline.BaselineError,match='operator_authority'):direct(url)
        assert state(admin,url)==before
        # Never invoke the protected routine; inspect grants only.
        assert admin.execute("SELECT has_function_privilege('scribeswell_corpus_operator',%s,'EXECUTE')",(routine,)).fetchone()==(True,)
    finally:admin.execute('REVOKE EXECUTE ON FUNCTION pg_catalog.'+routine+' FROM PUBLIC')


def test_ordinary_core_builtins_preserved(staged):
    admin,url=staged
    assert admin.execute("SELECT has_function_privilege('scribeswell_corpus_operator','pg_catalog.length(text)','EXECUTE')").fetchone()==(True,)
    assert direct(url)==baseline.REVISION

@pytest.mark.parametrize('scope,kind,privilege',[
    ('IN SCHEMA profile_defaults','TABLES','SELECT'),
    ('IN SCHEMA profile_defaults','TABLES','INSERT'),
    ('IN SCHEMA profile_defaults','SEQUENCES','USAGE'),
    ('','TABLES','SELECT'),('','SEQUENCES','SELECT'),
])
def test_public_consequential_defaults_denied(staged,scope,kind,privilege):
    admin,url=staged
    admin.execute('CREATE SCHEMA profile_defaults;GRANT USAGE ON SCHEMA profile_defaults TO PUBLIC')
    admin.execute(f'ALTER DEFAULT PRIVILEGES {scope} GRANT {privilege} ON {kind} TO PUBLIC')
    try:
        before=state(admin,url)
        with pytest.raises(baseline.BaselineError,match='operator_authority'):direct(url)
        assert state(admin,url)==before
    finally:
        admin.execute(f'ALTER DEFAULT PRIVILEGES {scope} REVOKE {privilege} ON {kind} FROM PUBLIC')
        admin.execute('DROP SCHEMA profile_defaults')

@pytest.mark.parametrize('kind,privilege',[('FUNCTIONS','EXECUTE'),('TYPES','USAGE')])
def test_ordinary_public_defaults_preserved(staged,kind,privilege):
    admin,url=staged
    admin.execute('CREATE SCHEMA profile_defaults;GRANT USAGE ON SCHEMA profile_defaults TO PUBLIC')
    admin.execute(f'ALTER DEFAULT PRIVILEGES IN SCHEMA profile_defaults GRANT {privilege} ON {kind} TO PUBLIC')
    try:
        before=state(admin,url)
        assert direct(url)==baseline.REVISION
        assert state(admin,url)==before
    finally:
        admin.execute(f'ALTER DEFAULT PRIVILEGES IN SCHEMA profile_defaults REVOKE {privilege} ON {kind} FROM PUBLIC')
        admin.execute('DROP SCHEMA profile_defaults')


def test_stricter_caller_timeouts_preserved(staged):
    _,url=staged;engine=engine_for(url)
    try:
        with engine.begin() as connection:
            connection.exec_driver_sql("SET LOCAL statement_timeout='1200ms'")
            connection.exec_driver_sql("SET LOCAL lock_timeout='150ms'")
            assert baseline.preflight_prepared(connection,CUSTODY)==baseline.REVISION
            assert connection.exec_driver_sql('SHOW statement_timeout').scalar()=='1200ms'
            assert connection.exec_driver_sql('SHOW lock_timeout').scalar()=='150ms'
    finally:engine.dispose()


def test_temporary_role_shadow_cannot_hide_unsafe_operator(staged):
    admin,url=staged;engine=engine_for(url)
    admin.execute('ALTER ROLE scribeswell_corpus_operator CREATEDB')
    try:
        with engine.begin() as connection:
            connection.exec_driver_sql('CREATE TEMP TABLE pg_roles AS SELECT * FROM pg_catalog.pg_roles')
            connection.exec_driver_sql("UPDATE pg_temp.pg_roles SET rolcreatedb=false WHERE rolname='scribeswell_corpus_operator'")
            connection.exec_driver_sql('SET LOCAL search_path=public,pg_catalog')
            with pytest.raises(baseline.BaselineError,match='operator_authority'):
                baseline.preflight_prepared(connection,CUSTODY)
            assert connection.exec_driver_sql('SHOW search_path').scalar()=='pg_catalog, pg_temp'
    finally:
        engine.dispose()
        admin.execute('ALTER ROLE scribeswell_corpus_operator NOCREATEDB')


def test_reordered_public_path_is_made_safe(staged):
    _,url=staged;engine=engine_for(url)
    try:
        with engine.begin() as connection:
            connection.exec_driver_sql('SET LOCAL search_path=public,pg_catalog')
            assert baseline.preflight_prepared(connection,CUSTODY)==baseline.REVISION
            assert connection.exec_driver_sql('SHOW search_path').scalar()=='pg_catalog, pg_temp'
    finally:engine.dispose()


def test_fresh_default_connection_requires_explicit_transaction(staged):
    admin,url=staged;engine=engine_for(url)
    before=state(admin,url)
    try:
        with engine.connect() as connection:
            assert not connection.in_transaction()
            with pytest.raises(baseline.BaselineError,match='^scribeswell_prepared_transaction_required$'):
                baseline.preflight_prepared(connection,CUSTODY)
            assert not connection.in_transaction()
    finally:engine.dispose()
    assert state(admin,url)==before


def test_reordered_equivalent_three_acl_cells_preserved(staged,monkeypatch):
    from psycopg import sql
    admin,url=staged
    objects=[('SCHEMA','scribeswell',"SELECT nspacl::text FROM pg_namespace WHERE nspname='scribeswell'"),
             ('FUNCTION','scribeswell.execute_corpus_command(jsonb)',"SELECT proacl::text FROM pg_proc WHERE oid='scribeswell.execute_corpus_command(jsonb)'::regprocedure"),
             ('FUNCTION','scribeswell.lookup_corpus_command_outcome(jsonb)',"SELECT proacl::text FROM pg_proc WHERE oid='scribeswell.lookup_corpus_command_outcome(jsonb)'::regprocedure")]
    for kind,identity,query in objects:
        original=admin.execute(query).fetchone()[0]
        rows=admin.execute("SELECT pg_get_userbyid(grantee),privilege_type FROM aclexplode(%s::aclitem[])",(original,)).fetchall()
        # Supported cells have only owner-granted nongrantable named-role rights.
        for role in dict.fromkeys(row[0] for row in rows):
            admin.execute(sql.SQL('REVOKE ALL ON '+kind+' '+identity+' FROM {}').format(sql.Identifier(role)))
        for role,privilege in reversed(rows):
            admin.execute(sql.SQL('GRANT '+privilege+' ON '+kind+' '+identity+' TO {}').format(sql.Identifier(role)))
        assert admin.execute(query).fetchone()[0]!=original
    before=state(admin,url)
    assert direct(url)==baseline.REVISION
    config=native(url,monkeypatch,dict(scribeswell_validation_profile='prepared-controller-v1',scribeswell_prepared_actor=CUSTODY))
    assert config.attributes['scribeswell_validated_profile']=='prepared-controller-v1'
    assert state(admin,url)==before


def test_native_commit_boundary_failure_has_no_profile_evidence(staged,monkeypatch):
    import sqlalchemy
    from sqlalchemy import event
    admin,url=staged;before=state(admin,url);engine=engine_for(url)
    config=Config(str(APP/'alembic.ini'))
    config.attributes.update(scribeswell_validation_profile='prepared-controller-v1',scribeswell_prepared_actor=CUSTODY)
    original=baseline.preflight_prepared;validations=[];commits=[]
    def checked(connection,actor):
        result=original(connection,actor);validations.append(1);return result
    def commit_failure(connection):
        assert len(validations)==2
        assert 'scribeswell_validated_profile' not in config.attributes
        connection.exec_driver_sql("UPDATE scribeswell.book SET name_en='commit-boundary temporary' WHERE id=1")
        commits.append(1)
        raise RuntimeError('private injected driver failure')
    event.listen(engine,'commit',commit_failure)
    monkeypatch.setattr(baseline,'preflight_prepared',checked)
    monkeypatch.setattr(sqlalchemy,'create_engine',lambda *args,**kwargs:engine)
    monkeypatch.setenv('SCRIBESWELL_MIGRATION_DATABASE_URL',migration_url(url))
    with pytest.raises(baseline.BaselineError,match='^scribeswell_migration_failed_requires_reconciliation$') as failure:
        command.upgrade(config,'head')
    assert commits==[1] and len(validations)==2
    assert failure.value.__cause__ is None and failure.value.__suppress_context__
    assert 'scribeswell_validated_profile' not in config.attributes
    assert state(admin,url)==before
