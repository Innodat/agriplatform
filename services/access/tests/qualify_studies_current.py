"""Single-use current-owner qualification; never touches retained KDG/Leave fixtures.

Runs two new isolated native clusters sequentially: clean and populated upgrade.
All mutations are confined to their canonical run UUIDs; preparation is read-only.
"""
from __future__ import annotations
if not __debug__:raise RuntimeError('qualification_optimized_python_prohibited')
import argparse,asyncio,json,os,secrets,signal,subprocess,sys,time
from pathlib import Path
from uuid import UUID,uuid4
from hashlib import sha256
import psycopg
from psycopg import sql
from sqlalchemy import create_engine,text
from sqlalchemy.engine import make_url
ROOT=Path(__file__).resolve().parents[3]
ACCESS=ROOT/'services/access'
sys.path[:0]=[str(ACCESS),str(ROOT/'apps/scribeswell/tests')]
from studies_owner_fixture import Qualification,private,check_ports
import studies_readiness as readiness
PROOF=None
FIXTURE=None
EXECUTED_SOURCES=None

def source_hashes():return readiness.source_hashes()
def write_private(path,value):
    if path.name in readiness.STAGE_FIELDS:
        if EXECUTED_SOURCES!=source_hashes():raise RuntimeError('qualification_sources_changed')
        value={**value,'executed_sources':EXECUTED_SOURCES}
    private(path,value)
def inputs():return FIXTURE.admin
def connect(url,autocommit=False):
    return psycopg.connect(url.render_as_string(hide_password=False),autocommit=autocommit,connect_timeout=3)
def engine(url):return create_engine(url.set(drivername='postgresql+psycopg'),hide_parameters=True,connect_args={'connect_timeout':3})
def owner_url(case,owner):
    if case!='upgrade':raise ValueError('unexpected_case')
    return FIXTURE.urls[owner+'_migrator']
def runtime_urls():return {role:FIXTURE.urls[role].render_as_string(hide_password=False) for role in readiness.DATABASE_ROLES.values()}
def runtime_app():
    from unittest.mock import patch
    from main import create_app
    from studies_identity import AsyncDatabase
    env=runtime_environment()
    with patch.dict(os.environ,env,clear=True):
        return create_app(object(),studies_db=AsyncDatabase(env['STUDIES_ACCESS_DATABASE_URL']),studies_identity_db=AsyncDatabase(env['STUDIES_IDENTITY_DATABASE_URL']),studies_setup_db=AsyncDatabase(env['STUDIES_IDENTITY_SETUP_DATABASE_URL']))
def runtime_environment():
    return {**FIXTURE.environment,'SCRIBESWELL_SERVICE_KEY':FIXTURE.service_key,'SUPABASE_URL':FIXTURE.status['api_url'],'SUPABASE_ANON_KEY':FIXTURE.status['anon_key'],**{key:FIXTURE.urls[role].render_as_string(hide_password=False) for key,role in readiness.DATABASE_ROLES.items()}}

async def require_studies_failure(call,expected,label):
    from studies_identity import StudiesFailure
    try:await call()
    except StudiesFailure as failure:
        assert (failure.status,failure.error_id)==expected,'unexpected_studies_refusal:'+label
        return {'case':label,'status':failure.status,'error_id':failure.error_id}
    else:raise AssertionError('studies_refusal_missing:'+label)


async def boundaries():
    import time,httpx
    sys.path.insert(0,str(ACCESS))
    from studies_identity import AsyncDatabase,evidence,prepare,transaction,StudiesFailure
    provider=json.loads((PROOF/'provider.json').read_text());runtime=json.loads((PROOF/'runtime.json').read_text());urls=runtime_urls()
    subjects={name:str(uuid4()) for name in ('partial','adopted','collision','unverified','deleted')}
    write_private(PROOF/'boundary-subjects.json',subjects)
    source=inputs();private=json.loads((PROOF/'private.json').read_text());admin=source.set(username='supabase_admin',database=private['databases']['upgrade'])
    with connect(admin) as c:
        for name,account in subjects.items():
            verified=None if name=='unverified' else '2026-01-01T00:00:00Z'
            c.execute('INSERT INTO auth.users(id,email,deleted_at,email_confirmed_at,banned_until,is_anonymous) VALUES(%s,%s,NULL,%s,NULL,false)',(account,'studies-'+name+'-'+uuid4().hex+'@example.invalid',verified))
        c.execute('UPDATE auth.users SET deleted_at=statement_timestamp() WHERE id=%s',(subjects['deleted'],))
    db=engine(owner_url('upgrade','identity'));adopted=str(uuid4())
    with db.begin() as c:
        for actor,kind,key in ((adopted,'account',None),(subjects['collision'],'system','studies.collision.'+uuid4().hex)):
            c.execute(text('INSERT INTO identity.actor(id,kind,display_name,actor_key,created_by,updated_by) VALUES(CAST(:actor AS uuid),:kind,:display,:key,CAST(:executor AS uuid),CAST(:executor AS uuid))'),{'actor':actor,'kind':kind,'display':'Synthetic boundary actor','key':key,'executor':runtime['service_actor']})
        c.execute(text("INSERT INTO identity.account_actor(account_id,actor_id,actor_kind,created_by) VALUES(CAST(:account AS uuid),CAST(:actor AS uuid),'account',CAST(:executor AS uuid))"),{'account':subjects['adopted'],'actor':adopted,'executor':runtime['service_actor']})
    db.dispose()
    reader=AsyncDatabase(urls['identity_studies_reader_runtime']);setup=AsyncDatabase(urls['identity_studies_setup_runtime']);access=AsyncDatabase(urls['access_studies_runtime'])
    assert await evidence(reader,__import__('uuid').UUID(subjects['partial']),time.monotonic()+3) is None
    operation=uuid4();actor=await prepare(setup,__import__('uuid').UUID(subjects['partial']),operation,time.monotonic()+3)
    assert str(actor)==subjects['partial']
    absent=await transaction(access,actor,time.monotonic()+3,'SELECT account_id,actor_id FROM access.check_studies_permission(:actor)',{'actor':actor},readonly=True)
    assert absent is None,'actor_setup_granted_permission'
    assert await prepare(setup,actor,operation,time.monotonic()+3)==actor,'partial_actor_not_reused'
    account=__import__('uuid').UUID(subjects['adopted'])
    assert str(await evidence(reader,account,time.monotonic()+3))==adopted
    assert str(await prepare(setup,account,uuid4(),time.monotonic()+3))==adopted,'adopted_actor_replaced'
    refusal_results=[]
    for name,expected in (('collision',(503,'identity.setup_unavailable')),
            ('unverified',(403,'identity.verification_required')),('deleted',(403,'access_denied'))):
        refusal_results.append(await require_studies_failure(
            lambda: evidence(reader,__import__('uuid').UUID(subjects[name]),time.monotonic()+3),expected,'evidence:'+name))
        refusal_results.append(await require_studies_failure(
            lambda: prepare(setup,__import__('uuid').UUID(subjects[name]),uuid4(),time.monotonic()+3),expected,'setup:'+name))
    # Actual cancellation must close dedicated socket inside the total deadline.
    started=time.monotonic()
    try:await transaction(access,actor,started+.1,'SELECT pg_sleep(10)',readonly=True)
    except StudiesFailure:pass
    else:raise AssertionError('native_timeout_acknowledged')
    elapsed=time.monotonic()-started
    assert elapsed<1,'native_deadline_cleanup_overrun'
    # Fresh connections cannot retain another account or organization context.
    fresh=await transaction(access,actor,time.monotonic()+3,"SELECT current_setting('app.account_id') AS account,current_setting('app.org_id') AS org,current_setting('statement_timeout') AS statement",readonly=True)
    assert fresh['account']==str(actor) and fresh['org']=='' and fresh['statement']!='0'
    denials=[]
    for role in ('identity_studies_reader_runtime','identity_studies_setup_runtime','access_studies_runtime'):
        for statement in ('SELECT * FROM identity.users','SELECT * FROM identity.account_actor','SELECT * FROM access.studies_account_grant','SET ROLE identity_studies_owner','SET ROLE access_studies_owner'):
            try:
                with connect(make_url(urls[role])) as c:c.execute(statement)
            except psycopg.Error as error:
                assert error.sqlstate=='42501';denials.append((role,statement.split()[0]))
            else:raise AssertionError('runtime_raw_authority_bypass')
    # Drop an actual committed transport response; retry original operation only.
    app=runtime_app();headers={'Authorization':'Bearer '+provider['token'],'X-Service-Key':runtime['service_key']};lost=str(uuid4())
    class LostResponse(httpx.ASGITransport):
        async def handle_async_request(self,request):
            await super().handle_async_request(request)
            raise httpx.ReadError('synthetic_lost_response')
    async with httpx.AsyncClient(transport=LostResponse(app=app),base_url='http://synthetic') as client:
        try:await client.post('/v2/enrollments/scribeswell-studies',headers=headers,json={'operation_id':lost})
        except httpx.ReadError:pass
        else:raise AssertionError('lost_response_not_exercised')
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic') as client:
        retry=await client.post('/v2/enrollments/scribeswell-studies',headers=headers,json={'operation_id':lost})
        assert retry.status_code==200 and retry.json()['result']['disposition']=='unchanged'
        # Controlled revocation records actor and operation; no regrant API exists.
        db=engine(owner_url('upgrade','access'))
        with db.begin() as c:
            c.execute(text("UPDATE access.studies_account_grant SET revoked_at=statement_timestamp(),revoked_by=CAST(:actor AS uuid),revocation_operation_id=CAST(:operation AS uuid) WHERE account_id=CAST(:account AS uuid) AND revoked_at IS NULL"),{'actor':runtime['service_actor'],'operation':str(uuid4()),'account':provider['account']})
        db.dispose()
        replay=await client.post('/v2/enrollments/scribeswell-studies',headers=headers,json={'operation_id':lost})
        check=await client.post('/v2/check',headers=headers,json={'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}})
        assert replay.status_code==check.status_code==403,'revoked_grant_resurrected'
    with connect(admin) as c:
        assert c.execute('SELECT count(*) FROM access.studies_account_grant WHERE account_id=%s',(provider['account'],)).fetchone()[0]==1
        assert c.execute('SELECT count(*) FROM access.studies_assignment_event WHERE account_id=%s',(provider['account'],)).fetchone()[0]==1
        assert c.execute('SELECT count(*) FROM identity.studies_setup_event WHERE account_id=%s',(provider['account'],)).fetchone()[0]==1
    write_private(PROOF/'boundaries.json',{'subjects':subjects,'refusal_results':refusal_results,'adopted_actor':adopted,'partial_actor_without_grant':True,'collision_unverified_deleted_refused':True,'actual_sql_timeout_seconds':elapsed,'fresh_context':True,'restricted_role_denials':denials,'lost_response_retry':True,'revoked_replay_denied':True,'one_initial_grant_event':True})

async def first_use_race(prefix='race'):
    import httpx,time
    provider=json.loads((PROOF/'provider.json').read_text());runtime=json.loads((PROOF/'runtime.json').read_text())
    api=provider['api'];email='studies-race-'+uuid4().hex+'@example.invalid'
    async with httpx.AsyncClient(timeout=3) as client:
        headers={'apikey':provider['service_key'],'Authorization':'Bearer '+provider['service_key']}
        response=await client.post(api+'/auth/v1/admin/users',headers=headers,json={'email':email,'email_confirm':True})
        assert response.status_code==200;account=response.json()['id']
        write_private(PROOF/(prefix+'-provider-created.json'),{'account':account,'email':email})
        response=await client.post(api+'/auth/v1/admin/generate_link',headers=headers,json={'type':'magiclink','email':email})
        assert response.status_code==200;value=response.json();hashed=value.get('hashed_token') or value['properties']['hashed_token']
        response=await client.post(api+'/auth/v1/verify',headers={'apikey':provider['anon_key']},json={'type':'magiclink','token_hash':hashed})
        assert response.status_code==200;token=response.json()['access_token']
        response=await client.get(api+'/auth/v1/user',headers={'apikey':provider['anon_key'],'Authorization':'Bearer '+token})
        assert response.status_code==200 and response.json()['id']==account;verified=response.json()['email_confirmed_at']
    write_private(PROOF/(prefix+'-provider-private.json'),{'account':account,'email':email,'token':token})
    source=inputs();private=json.loads((PROOF/'private.json').read_text());admin=source.set(username='supabase_admin',database=private['databases']['upgrade'])
    with connect(admin) as c:
        c.execute('INSERT INTO auth.users(id,email,deleted_at,email_confirmed_at,banned_until,is_anonymous) VALUES(%s,%s,NULL,%s,NULL,false) ON CONFLICT(id) DO NOTHING',(account,email,verified))
        assert c.execute('SELECT count(*) FROM identity.account_actor WHERE account_id=%s',(account,)).fetchone()[0]==0
        assert c.execute('SELECT count(*) FROM access.studies_account_grant WHERE account_id=%s',(account,)).fetchone()[0]==0
    shared=str(uuid4());operations=[shared,shared,str(uuid4()),str(uuid4())]
    write_private(PROOF/(prefix+'-operation-inputs.json'),{'account':account,'operations':operations})
    app=runtime_app();headers={'Authorization':'Bearer '+token,'X-Service-Key':runtime['service_key']}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic') as client:
        started=time.monotonic()
        initial=await asyncio.gather(*(client.post('/v2/enrollments/scribeswell-studies',headers=headers,json={'operation_id':operation}) for operation in operations))
        write_private(PROOF/(prefix+'-initial-responses.json'),{'elapsed':time.monotonic()-started,'responses':[{'status':r.status_code,'body':r.json()} for r in initial]})
        assert all(response.status_code==200 for response in initial),'first_race_unavailable_requires_diagnosis'
        acknowledged=[]
        for operation in operations:
            response=await client.post('/v2/enrollments/scribeswell-studies',headers=headers,json={'operation_id':operation})
            assert response.status_code==200,'first_race_original_retry_failed'
            acknowledged.append(response.json())
        assert acknowledged[0]==acknowledged[1],'same_operation_race_different_result'
        assert len({value['operation_id'] for value in acknowledged if value['result']['disposition']=='created'})==1
        for first,ack in zip(initial,acknowledged):
            if first.status_code==200:assert first.json()==ack,'original_success_disposition_changed'
        decision=await client.post('/v2/check',headers=headers,json={'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}})
        assert decision.status_code==200 and decision.json()['actor_id']==account
    with connect(admin) as c:
        for table,column in (('access.studies_account_grant','account_id'),('access.studies_assignment_event','account_id'),('identity.studies_setup_event','account_id')):
            assert c.execute(sql.SQL('SELECT count(*) FROM {} WHERE {}=%s').format(sql.SQL(table),sql.Identifier(column)),(account,)).fetchone()[0]==1
        assert c.execute('SELECT count(*) FROM identity.org_member WHERE user_id=%s',(account,)).fetchone()[0]==0
    write_private(PROOF/('first-use-race.json' if prefix=='race' else 'current-first-use-race.json'),{'account':account,'initial_statuses':[response.status_code for response in initial],'original_acknowledgements':acknowledged,'first_use_absent_actor_and_grant':True,'one_initial_grant_event_and_actor_event':True,'zero_memberships':True,'canonical_check':True})

async def current_denials():
    import time,httpx
    sys.path.insert(0,str(ACCESS))
    from studies_identity import AsyncDatabase,evidence,prepare,transaction,StudiesFailure
    from access_operator import execute
    names=('banned','missing_profile','deleted_profile','system_profile','keyed_profile')
    subjects={name:str(uuid4()) for name in names};write_private(PROOF/'current-denial-subjects.json',subjects)
    source=inputs();private=json.loads((PROOF/'private.json').read_text());admin=source.set(username='supabase_admin',database=private['databases']['upgrade'])
    with connect(admin) as c:
        for name,account in subjects.items():
            c.execute('INSERT INTO auth.users(id,email,deleted_at,email_confirmed_at,banned_until,is_anonymous) VALUES(%s,%s,NULL,%s,NULL,false)',(account,'studies-current-'+uuid4().hex+'@example.invalid','2026-01-01T00:00:00Z'))
        c.execute("UPDATE auth.users SET banned_until='9999-01-01T00:00:00Z' WHERE id=%s",(subjects['banned'],))
    owner=engine(owner_url('upgrade','identity'))
    with owner.begin() as c:
        c.execute(text('DELETE FROM identity.users WHERE id=CAST(:account AS uuid)'),{'account':subjects['missing_profile']})
        c.execute(text('UPDATE identity.users SET deleted_at=statement_timestamp() WHERE id=CAST(:account AS uuid)'),{'account':subjects['deleted_profile']})
        c.execute(text('UPDATE identity.users SET is_system=true WHERE id=CAST(:account AS uuid)'),{'account':subjects['system_profile']})
        c.execute(text('UPDATE identity.users SET actor_key=:key WHERE id=CAST(:account AS uuid)'),{'account':subjects['keyed_profile'],'key':'studies.synthetic.'+uuid4().hex})
    owner.dispose();urls=runtime_urls();reader=AsyncDatabase(urls['identity_studies_reader_runtime']);setup=AsyncDatabase(urls['identity_studies_setup_runtime'])
    refusal_results=[]
    for name,account in subjects.items():
        expected=(403,'access_denied') if name=='banned' else (503,'identity.setup_unavailable')
        for operation,call in (('evidence',lambda: evidence(reader,__import__('uuid').UUID(account),time.monotonic()+3)),('setup',lambda:prepare(setup,__import__('uuid').UUID(account),uuid4(),time.monotonic()+3))):
            refusal_results.append(await require_studies_failure(call,expected,operation+':'+name))
    # Supported protected availability commands retain registry audit/outcomes.
    operator=engine(FIXTURE.urls['access_operator'])
    def enabled(value,revision):
        envelope={'schema_version':1,'operation_id':str(uuid4()),'command':'application.set_enabled','scope':{'kind':'platform'},'payload':{'app_id':'scribeswell','enabled':value,'expected_revision':revision},'reason_code':'synthetic_fixture','evidence_ref':'synthetic:studies-availability'}
        with operator.connect() as c:receipt=execute(c,json.dumps(envelope).encode())
        write_private(PROOF/('availability-'+uuid4().hex+'.json'),{'command':envelope,'receipt':receipt})
    provider=json.loads((PROOF/'provider.json').read_text());race=json.loads((PROOF/'race-provider-private.json').read_text());runtime=json.loads((PROOF/'runtime.json').read_text())
    app=runtime_app();headers={'Authorization':'Bearer '+race['token'],'X-Service-Key':runtime['service_key']}
    operation=json.loads((PROOF/'race-operation-inputs.json').read_text())['operations'][0]
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic') as client:
        baseline=await client.post('/v2/check',headers=headers,json={'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}})
        assert baseline.status_code==200,'availability_positive_precondition_failed'
        enabled(False,'2')
        try:
            for body in ({'operation_id':operation},{'operation_id':str(uuid4())}):
                response=await client.post('/v2/enrollments/scribeswell-studies',headers=headers,json=body)
                assert response.status_code==403 and response.json()['error_id']=='access_denied'
            response=await client.post('/v2/check',headers=headers,json={'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}})
            assert response.status_code==403
        finally:enabled(True,'3')
    operator.dispose()
    # A timeout while blocked at the SQL command boundary cannot create a receipt.
    partial=json.loads((PROOF/'boundary-subjects.json').read_text())['partial'];actor=__import__('uuid').UUID(partial);operation=uuid4();access=AsyncDatabase(urls['access_studies_runtime'])
    with connect(make_url(owner_url('upgrade','access'))) as blocker:
        blocker.execute("SELECT pg_advisory_xact_lock(hashtextextended('access:studies-account:v1:'||%s,0))",(partial,))
        started=time.monotonic()
        try:await transaction(access,actor,started+.2,'SELECT disposition,account_id,actor_id FROM access.enroll_studies_account(:operation,:actor)',{'operation':operation,'actor':actor})
        except StudiesFailure:pass
        else:raise AssertionError('blocked_command_acknowledged')
        elapsed=time.monotonic()-started;assert elapsed<1
    with connect(admin) as c:
        assert c.execute('SELECT count(*) FROM access.studies_enrollment_outcome WHERE account_id=%s AND operation_id=%s',(partial,operation)).fetchone()[0]==0
        assert c.execute('SELECT count(*) FROM access.studies_account_grant WHERE account_id=%s',(partial,)).fetchone()[0]==0
    assert await evidence(reader,actor,time.monotonic()+3)==actor
    retry=await transaction(access,actor,time.monotonic()+3,'SELECT disposition,account_id,actor_id FROM access.enroll_studies_account(:operation,:actor)',{'operation':operation,'actor':actor})
    assert retry['disposition']=='created'
    write_private(PROOF/'current-denials.json',{'subjects':subjects,'refusal_results':refusal_results,'banned_missing_deleted_system_keyed_refused':True,'disabled_check_new_enrollment_replay_denied':True,'availability_restored_by_protected_command':True,'write_lock_timeout_seconds':elapsed,'uncommitted_outcome_and_grant_absent':True,'same_operation_retry_after_fresh_evidence':True})

async def lock_eligibility():
    """Committed Auth changes during either existing advisory wait must deny."""
    import time
    from uuid import UUID
    sys.path.insert(0,str(ACCESS))
    from studies_identity import AsyncDatabase,prepare,StudiesFailure
    source=inputs();private=json.loads((PROOF/'private.json').read_text())
    admin=source.set(username='supabase_admin',database=private['databases']['upgrade'])
    setup=AsyncDatabase(runtime_urls()['identity_studies_setup_runtime'])
    results=[]
    for replay in (False,True):
        for namespace in ('account-actor','actor-id'):
            if replay and namespace=='actor-id':continue # adopted mapping takes only account lock
            for change in ('banned_until','deleted_at','email_confirmed_at'):
                account=uuid4();operation=uuid4()
                with connect(admin) as c:
                    c.execute('INSERT INTO auth.users(id,email,email_confirmed_at,is_anonymous) VALUES(%s,%s,statement_timestamp(),false)',(account,'studies-lock-'+uuid4().hex+'@example.invalid'))
                if replay:assert await prepare(setup,account,operation,time.monotonic()+3)==account
                with connect(admin) as holder:
                    holder.execute("SELECT pg_advisory_xact_lock(identity.command_lock(%s))",('identity:'+namespace+':v1:'+str(account),))
                    task=asyncio.create_task(prepare(setup,account,operation,time.monotonic()+3))
                    blocked=False
                    for _ in range(100):
                        await asyncio.sleep(.005)
                        with connect(admin,True) as observer:
                            blocked=observer.execute("SELECT EXISTS(SELECT 1 FROM pg_stat_activity WHERE usename='identity_studies_setup_runtime' AND wait_event='advisory' AND datname=current_database())").fetchone()[0]
                        if blocked:break
                    assert blocked,'setup_did_not_wait_on_expected_lock'
                    value=None if change=='email_confirmed_at' else ('2100-01-01T00:00:00Z' if change=='banned_until' else '2026-01-01T00:00:00Z')
                    holder.execute(sql.SQL('UPDATE auth.users SET {}=%s WHERE id=%s').format(sql.Identifier(change)),(value,account))
                    holder.commit()
                try:
                    await task
                    outcome='accepted'
                except StudiesFailure as error:outcome=error.error_id
                with connect(admin) as c:
                    counts=c.execute('SELECT (SELECT count(*) FROM identity.account_actor WHERE account_id=%s),(SELECT count(*) FROM identity.studies_setup_outcome WHERE account_id=%s)',(account,account)).fetchone()
                results.append({'lock':namespace,'change':change,'replay':replay,'wait_observed':blocked,'outcome':outcome,'counts':list(counts)})
    refused=all(row['outcome']==('identity.verification_required' if row['change']=='email_confirmed_at' else 'access_denied') for row in results)
    absent=all(row['counts']==([1,1] if row['replay'] else [0,0]) for row in results)
    write_private(PROOF/'lock-eligibility.json',{'results':results,'account_and_actor_locks_observed':all(row['wait_observed'] for row in results),'ban_delete_unverify_refused':refused,'no_actor_or_receipt_written':absent,'replay_denied':all(row['outcome']!='accepted' for row in results if row['replay'])})
    assert refused and absent,'auth_change_during_lock_wait_was_missed'


async def provider_subject():
    import httpx
    api=FIXTURE.status['api_url'];service=FIXTURE.status['service_role_key'];anon=FIXTURE.status['anon_key']
    email='studies-current-'+uuid4().hex+'@example.invalid'
    async with httpx.AsyncClient(timeout=3) as client:
        headers={'apikey':service,'Authorization':'Bearer '+service}
        response=await client.post(api+'/auth/v1/admin/users',headers=headers,json={'email':email,'email_confirm':True})
        assert response.status_code==200;account=response.json()['id']
        response=await client.post(api+'/auth/v1/admin/generate_link',headers=headers,json={'type':'magiclink','email':email})
        assert response.status_code==200;value=response.json();hashed=value.get('hashed_token') or value['properties']['hashed_token']
        response=await client.post(api+'/auth/v1/verify',headers={'apikey':anon},json={'type':'magiclink','token_hash':hashed})
        assert response.status_code==200;token=response.json()['access_token']
        response=await client.get(api+'/auth/v1/user',headers={'apikey':anon,'Authorization':'Bearer '+token})
        assert response.status_code==200 and response.json()['id']==account and response.json()['email_confirmed_at']
    with FIXTURE.connect() as c:
        hook=c.execute("SELECT EXISTS(SELECT 1 FROM pg_trigger t JOIN pg_proc p ON p.oid=t.tgfoid JOIN pg_namespace n ON n.oid=p.pronamespace WHERE t.tgrelid='auth.users'::regclass AND t.tgname='on_auth_user_created' AND t.tgenabled='O' AND n.nspname='identity' AND p.proname='handle_new_user')").fetchone()[0]
        profile=c.execute('SELECT id FROM identity.users WHERE id=%s',(account,)).fetchone()
        memberships=c.execute('SELECT count(*) FROM identity.org_member WHERE user_id=%s',(account,)).fetchone()[0]
    assert hook and profile and str(profile[0])==account and memberships==0
    write_private(PROOF/'provider.json',{'api':api,'anon_key':anon,'service_key':service,'account':account,'email':email,'token':token})
    write_private(PROOF/'provider-proof.json',{'native_identity_hook':hook,'isolated_profile_hook':bool(profile),'zero_memberships':memberships==0})

async def confirmed_http_denials():
    """Observe a real verified provider result, then change current Auth before SQL.

    Same provider database as Identity, so stale positive evidence is deliberately
    bounded to one request. No provider response or proof field is fabricated.
    """
    import httpx
    from unittest.mock import patch
    from studies_identity import live_account,AsyncDatabase
    from main import create_app
    provider=json.loads((PROOF/'provider.json').read_text());env=runtime_environment();results=[]
    for assignment,error in (("email_confirmed_at=NULL",'identity.verification_required'),("banned_until='9999-01-01T00:00:00Z'",'access_denied')):
        for path in ('/v2/check','/v2/enrollments/scribeswell-studies'):
            with FIXTURE.connect() as c:c.execute("UPDATE auth.users SET email_confirmed_at='2026-01-01T00:00:00Z',banned_until=NULL WHERE id=%s",(provider['account'],))
            observed=[]
            async def after_live(authorization,deadline):
                account=await live_account(authorization,deadline,env)
                observed.append(str(account))
                with FIXTURE.connect() as c:c.execute(sql.SQL('UPDATE auth.users SET '+assignment+' WHERE id=%s'),(provider['account'],))
                return account
            with patch.dict(os.environ,env,clear=True):
                app=create_app(object(),studies_provider=after_live,studies_db=AsyncDatabase(env['STUDIES_ACCESS_DATABASE_URL']),studies_identity_db=AsyncDatabase(env['STUDIES_IDENTITY_DATABASE_URL']),studies_setup_db=AsyncDatabase(env['STUDIES_IDENTITY_SETUP_DATABASE_URL']))
            body={'operation_id':str(uuid4())} if path.endswith('scribeswell-studies') else {'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}}
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic') as client:
                response=await client.post(path,headers={'Authorization':'Bearer '+provider['token'],'X-Service-Key':FIXTURE.service_key},json=body)
            assert observed==[provider['account']] and response.status_code==403 and response.json()['error_id']==error
            results.append({'path':path,'status':response.status_code,'error_id':response.json()['error_id']})
    with FIXTURE.connect() as c:c.execute("UPDATE auth.users SET email_confirmed_at='2026-01-01T00:00:00Z',banned_until=NULL WHERE id=%s",(provider['account'],))
    write_private(PROOF/'confirmed-http-denials.json',{'results':results,'live_provider_still_verified':True,'local_current_auth_denial_precedes_retained_grant':True,'evidence_order':'live-provider, committed-current-Auth-change, Identity-SQL'})

class CurrentQualification(Qualification):
    def __init__(self,*args,populated=False,**kwargs):
        super().__init__(*args,**kwargs);self.populated=populated;self.cli_results=[];self.principals_done=False

    def migration_case(self,owner,label,*,target='head',fail=False,partial=False,expected=0):
        directory=ACCESS/('identity-migrations' if owner=='identity' else 'migrations')
        module='identity_baseline' if owner=='identity' else 'access_baseline'
        function='verify_owned_postcondition' if owner=='identity' else 'verify_postcondition'
        marker=self.proof/(label+'-postcondition.json')
        marker_content='{"postcondition_verified":true}\n'
        code=f'import sys;sys.path.insert(0,{str(directory)!r});from alembic.config import Config;from alembic import command;'
        if partial or fail:
            code+=f'import {module} as baseline;original=baseline.{function};'
            body='def replacement(c,*args,**kwargs):\n original(c,require_head=False)\n' if partial else (
                'def replacement(c,*args,**kwargs):\n original(c,*args,**kwargs)\n import os\n'
                +f' fd=os.open({str(marker)!r},os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)\n'
                +f' with os.fdopen(fd,"w") as out:out.write({marker_content!r})\n'
                +' raise RuntimeError("synthetic_postcondition_failure")\n')
            code+=f'exec({body!r});baseline.{function}=replacement;'
        ini=ACCESS/('identity-alembic.ini' if owner=='identity' else 'alembic.ini')
        code+=f'command.upgrade(Config({str(ini)!r}),{target!r})'
        env={**self.environment,owner.upper()+'_MIGRATION_DATABASE_URL':self.urls[owner+'_migrator'].set(drivername='postgresql+psycopg').render_as_string(hide_password=False)}
        path=self.proof/(label+'.log');fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'wb') as output:
            process=subprocess.Popen([sys.executable,'-I','-B','-c',code],env=env,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
            try:result=process.wait(timeout=90)
            finally:self.stop_process(process)
        self.events.append({'stage':label,'exit_code':result})
        assert (result==0)==(expected==0),'migration_case_failed:'+label
        observation={'stage':label,'exit_code':result,'log_sha256':sha256(path.read_bytes()).hexdigest()}
        if fail:
            assert marker.is_file() and not marker.is_symlink() and marker.stat().st_mode&0o777==0o600,'injected_postcondition_not_observed:'+label
            assert marker.read_bytes()==b'{"postcondition_verified":true}\n','injected_postcondition_marker_invalid:'+label
            observation['postcondition_marker_sha256']=sha256(marker.read_bytes()).hexdigest()
        self.cli_results.append(observation)

    def before_owner_migrations(self):
        if not self.populated:return
        self.migration_case('access','cli-access-before-identity',expected=1)
        # Ordinary supported previous revision, using its own verified catalogue.
        # Only the fixture suppresses the env's final-head requirement for this
        # explicitly selected prior revision. No source/catalogue is rewritten.

    def migrate(self,owner,config):
        if not self.populated or owner=='scribeswell_studies':return super().migrate(owner,config)
        if owner=='identity':
            self.migration_case('identity','identity-prior',target='identity_0025',partial=True)
            import httpx
            service=self.status['service_role_key']
            response=httpx.post(self.status['api_url']+'/auth/v1/admin/users',headers={'apikey':service,'Authorization':'Bearer '+service},json={'email':'prior-'+uuid4().hex+'@example.invalid','email_confirm':True},timeout=3)
            assert response.status_code==200;self.prior_account=response.json()['id']
        else:
            self.migration_case('access','access-prior',target='access_0018')
            self.prepare_principals()
        before=self.ledger(owner)
        before_label='before-'+owner+'-failed-migration'
        self.snapshot(before_label)
        self.migration_case(owner,'cli-'+owner+'-failure',fail=True,expected=1)
        self.snapshot('after-'+owner+'-failed-migration',previous=before_label)
        assert self.ledger(owner)==before
        self.migration_case(owner,'cli-'+owner+'-upgrade')
        self.migration_case(owner,'cli-'+owner+'-repeat')
        with self.connect() as c:assert c.execute('SELECT id FROM identity.users WHERE id=%s',(self.prior_account,)).fetchone()

    def observe(self,label,initial=False):
        if not (initial and self.populated):return super().observe(label,initial=initial)
        from studies_owner_fixture import empty_protected_state
        state=self.snapshot(label)
        assert {row['id'] for row in state['identity.users']}=={self.prior_account,*[account['account_id'] for account in self.accounts]}
        assert {row['id'] for row in state['identity.actor']}=={self.actor}
        empty_protected_state(state)

    def ledger(self,owner):
        with self.connect() as c:return c.execute('SELECT version_num FROM '+owner+'.alembic_version').fetchone()[0]

    def prepare_principals(self):
        if self.principals_done:return
        if not self.populated:
            with self.connect() as c:
                assert c.execute('SELECT count(*) FROM identity.actor').fetchone()[0]==0
                assert c.execute('SELECT count(*) FROM identity.users').fetchone()[0]==0
                assert c.execute('SELECT count(*) FROM access.studies_account_grant').fetchone()[0]==0
            self.clean_no_seeds=True
        super().prepare_principals();self.principals_done=True

    def execute_current(self,callback):
        try:
            check_ports();self.wrapper('prepare');self.owned=True
            self.wrapper('up');self.wrapper('verify');self.capture_status()
            self.prepare_owners();callback(self);self.verify_sources();self.events.append({'stage':'passed'})
        except BaseException as error:
            import traceback
            private(self.proof/'failure.json',{'type':type(error).__name__,'sqlstate':getattr(error,'sqlstate',None),'frames':[{'file':f.filename,'line':f.lineno,'function':f.name} for f in traceback.extract_tb(error.__traceback__)]})
            self.events.append({'stage':'failed'});raise
        finally:
            for process in reversed(self.processes):self.stop_process(process)
            if self.owned:self.wrapper('stop')
            private(self.proof/'result.json',{'run_id':self.run_id,'events':self.events,'scope':'isolated current-owner readiness; no production activation'})

def retain_qualification():
    proofs={name:json.loads((PROOF/name).read_bytes()) for name in readiness.STAGE_FIELDS}
    sources=readiness.source_hashes()
    record={'schema_version':readiness.ARTIFACT_VERSION,'identity_revision':readiness.IDENTITY_HEAD,'access_revision':readiness.ACCESS_HEAD,'runtime_sources':readiness.runtime_hashes(),'sources':sources,
        'cases':readiness.validate_stage_proofs(proofs,sources),
        'proof_sha256':{name:sha256((PROOF/name).read_bytes()).hexdigest() for name in proofs}}
    write_private(PROOF/'qualification.json',record)
    readiness.validate_qualification(record,PROOF)

def prepared():
    return readiness.prepare(FIXTURE.urls['identity_migrator'].set(drivername='postgresql+psycopg').render_as_string(hide_password=False),FIXTURE.urls['access_migrator'].set(drivername='postgresql+psycopg').render_as_string(hide_password=False),PROOF/'qualification.json','synthetic-current-'+FIXTURE.run_id)

def preparation_refusals():
    """Commit isolated faults, observe refusal, explicitly restore; never repair in prepare."""
    from studies_owner_fixture import protected_state
    results=[]
    def attempt(label):
        with FIXTURE.connect() as c:c.execute('BEGIN READ ONLY');before=protected_state(c);c.execute('ROLLBACK')
        try:prepared()
        except Exception as error:code=type(error).__name__
        else:raise AssertionError('unsafe_preparation_accepted:'+label)
        with FIXTURE.connect() as c:c.execute('BEGIN READ ONLY');after=protected_state(c);c.execute('ROLLBACK')
        assert before==after,'preparation_changed_business_state'
        results.append({'case':label,'refused':True,'exception_type':code,'protected_state_unchanged':True})
    cases=[
        ('old-identity',"UPDATE identity.alembic_version SET version_num='identity_0021'","UPDATE identity.alembic_version SET version_num='identity_0026'"),
        ('unknown-access',"UPDATE access.alembic_version SET version_num='access_0020'","UPDATE access.alembic_version SET version_num='access_0019'"),
        ('partial-access','DELETE FROM access.alembic_version',"INSERT INTO access.alembic_version VALUES('access_0019')"),
        ('disabled-identity',"UPDATE identity.studies_runtime_principal SET enabled=false,revision=revision+1,operation_id=gen_random_uuid()","UPDATE identity.studies_runtime_principal SET enabled=true,revision=revision+1,operation_id=gen_random_uuid()"),
        ('disabled-access',"UPDATE access.studies_runtime_principal SET enabled=false,revision=revision+1,operation_id=gen_random_uuid()","UPDATE access.studies_runtime_principal SET enabled=true,revision=revision+1,operation_id=gen_random_uuid()"),
        ('missing-hook','ALTER TABLE auth.users DISABLE TRIGGER on_auth_user_created','ALTER TABLE auth.users ENABLE TRIGGER on_auth_user_created'),
        ('unsafe-role','ALTER ROLE access_studies_runtime CREATEDB','ALTER ROLE access_studies_runtime NOCREATEDB'),
        ('raw-privileges','GRANT SELECT ON access.studies_account_grant TO access_studies_runtime','REVOKE SELECT ON access.studies_account_grant FROM access_studies_runtime'),
    ]
    for label,fault,restore in cases:
        owner='identity_migrator' if label=='disabled-identity' else 'access_migrator' if label=='disabled-access' else None
        with FIXTURE.connect(owner) as c:c.execute(fault)
        try:attempt(label)
        finally:
            with FIXTURE.connect(owner) as c:c.execute(restore)
    # Binding faults require bypassing the immutable guard only in this synthetic
    # database. Restore the guard before preparation so catalogue checks stay real.
    alternate=str(uuid4())
    with FIXTURE.connect('identity_migrator') as c:
        c.execute("INSERT INTO identity.actor(id,kind,display_name,actor_key,created_by,updated_by) VALUES(%s,'service','Synthetic mismatch',%s,%s,%s)",(alternate,'mismatch.'+FIXTURE.run_id,FIXTURE.actor,FIXTURE.actor))
    for label,owner,table in (('missing-principal','identity','identity.studies_runtime_principal'),('mismatched-principal','access','access.studies_runtime_principal')):
        with FIXTURE.connect() as c:
            c.execute('ALTER TABLE '+table+' DISABLE TRIGGER studies_principal_guard')
            original=c.execute('SELECT to_jsonb(t) FROM '+table+' t').fetchone()[0]
            if label=='missing-principal':c.execute('DELETE FROM '+table)
            else:c.execute('UPDATE '+table+' SET executor_actor_id=%s',(alternate,))
            c.execute('ALTER TABLE '+table+' ENABLE TRIGGER studies_principal_guard')
        try:attempt(label)
        finally:
            with FIXTURE.connect() as c:
                c.execute('ALTER TABLE '+table+' DISABLE TRIGGER studies_principal_guard')
                if label=='missing-principal':
                    c.execute('INSERT INTO '+table+' SELECT * FROM jsonb_populate_record(NULL::'+table+',%s::jsonb)',(json.dumps(original),))
                else:c.execute('UPDATE '+table+' SET executor_actor_id=%s',(FIXTURE.actor,))
                c.execute('ALTER TABLE '+table+' ENABLE TRIGGER studies_principal_guard')
    for label,assignment,restore in (('non-service-actor',"kind='system'","kind='service'"),('unkeyed-service',"actor_key=NULL",'actor_key=%s')):
        with FIXTURE.connect() as c:
            key=c.execute('SELECT actor_key FROM identity.actor WHERE id=%s',(FIXTURE.actor,)).fetchone()[0]
            c.execute('ALTER TABLE identity.actor DISABLE TRIGGER actor_guard')
            c.execute('UPDATE identity.actor SET '+assignment+' WHERE id=%s',(FIXTURE.actor,))
            c.execute('ALTER TABLE identity.actor ENABLE TRIGGER actor_guard')
        try:attempt(label)
        finally:
            with FIXTURE.connect() as c:
                c.execute('ALTER TABLE identity.actor DISABLE TRIGGER actor_guard')
                c.execute('UPDATE identity.actor SET '+restore+' WHERE id=%s',((key,FIXTURE.actor) if '%s' in restore else (FIXTURE.actor,)))
                c.execute('ALTER TABLE identity.actor ENABLE TRIGGER actor_guard')
    # Registration uses its existing protected command rather than table bypass.
    FIXTURE.operator('application.set_enabled',{'app_id':'scribeswell','enabled':False,'expected_revision':'4'})
    try:attempt('missing-enabled-registration')
    finally:FIXTURE.operator('application.set_enabled',{'app_id':'scribeswell','enabled':True,'expected_revision':'5'})
    artifact=prepared()
    write_private(PROOF/'preparation-refusals.json',{'results':results,'restored_preparation_succeeded':True})
    return artifact

async def default_startup(artifact):
    import httpx
    from unittest.mock import patch
    from main import create_app
    env=runtime_environment();refused=[]
    variants=[('missing-artifact',{}),('malformed-artifact',{'STUDIES_READINESS_JSON':'{}'})]
    for name in readiness.DATABASE_ROLES:
        variants.append(('missing-'+name,{'STUDIES_READINESS_JSON':json.dumps(artifact),name:None}))
    for label,altered in variants:
        values=env|altered;values={k:v for k,v in values.items() if v is not None}
        with patch.dict(os.environ,values,clear=True):
            try:create_app()
            except RuntimeError:refused.append(label)
            else:raise AssertionError('partial_default_startup_accepted:'+label)
    for label,change in [('old-version',{'schema_version':1}),('old-pair',{'identity_revision':'identity_0021','access_revision':'access_0016'}),('future-head',{'access_revision':'access_0020'}),('stale-runtime',{'runtime_sources':{}})]:
        with patch.dict(os.environ,env|{'STUDIES_READINESS_JSON':json.dumps(artifact|change)},clear=True):
            try:create_app()
            except RuntimeError:refused.append(label)
            else:raise AssertionError('stale_default_startup_accepted:'+label)
    values=env|{'STUDIES_READINESS_JSON':json.dumps(artifact)}
    with patch.dict(os.environ,values,clear=True):app=create_app()
    race=json.loads((PROOF/'race-provider-private.json').read_text());provider=json.loads((PROOF/'provider.json').read_text())
    headers={'X-Service-Key':FIXTURE.service_key,'Authorization':'Bearer '+race['token']}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic') as client:
        response=await client.post('/v2/check',headers=headers,json={'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}})
        assert response.status_code==200 and len(response.json())==6
        headers['Authorization']='Bearer '+provider['token']
        revoked=await client.post('/v2/check',headers=headers,json={'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}})
        assert revoked.status_code==403
        headers['Authorization']='Bearer '+race['token']
        with FIXTURE.connect() as c:c.execute("UPDATE auth.users SET email_confirmed_at=NULL WHERE id=%s",(race['account'],))
        denied=await client.post('/v2/check',headers=headers,json={'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}})
        assert denied.status_code==403 and denied.json()['error_id']=='identity.verification_required'
    # Separate OS process imports the unmodified default module under the same env.
    with FIXTURE.connect() as c:c.execute("UPDATE auth.users SET email_confirmed_at='2026-01-01T00:00:00Z' WHERE id=%s",(race['account'],))
    owner=FIXTURE.spawn('default-access-http',[sys.executable,'-m','uvicorn','main:app','--host','127.0.0.1','--port','8193','--no-access-log','--log-level','error'],values,ACCESS)
    from studies_owner_fixture import wait_http
    wait_http('http://127.0.0.1:8193/health',owner)
    with httpx.Client(timeout=3) as client:
        positive=client.post('http://127.0.0.1:8193/v2/check',headers=headers,json={'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}})
        assert positive.status_code==200 and len(positive.json())==6
        with FIXTURE.connect() as c:c.execute('UPDATE auth.users SET email_confirmed_at=NULL WHERE id=%s',(race['account'],))
        response=client.post('http://127.0.0.1:8193/v2/check',headers=headers,json={'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}})
        assert response.status_code==403 and response.json()['error_id']=='identity.verification_required'
    FIXTURE.stop_process(owner);FIXTURE.processes.remove(owner)
    write_private(PROOF/'default-startup.json',{'no_database_or_provider_injection':True,'default_module_process_started':True,'default_process_positive_then_current_denial':True,'restricted_six_field_check':True,'revoked_grant_denied':True,'current_account_denied':True,'startup_refusals':refused,'artifact_sha256':sha256((PROOF/'readiness.json').read_bytes()).hexdigest()})


def inspect_read_only():
    from studies_owner_fixture import protected_state
    with FIXTURE.connect() as c:
        c.execute('BEGIN READ ONLY')
        assert c.execute('SELECT version_num FROM identity.alembic_version').fetchone()[0]==readiness.IDENTITY_HEAD
        assert c.execute('SELECT version_num FROM access.alembic_version').fetchone()[0]==readiness.ACCESS_HEAD
        assert c.execute("SELECT count(*) FROM access.studies_account_grant g JOIN access.studies_assignment_event e USING(account_id) WHERE g.actor_id<>e.actor_id OR g.executor_actor_id<>e.executor_actor_id OR g.initiator_actor_id<>e.initiator_actor_id").fetchone()[0]==0
        assert c.execute("SELECT count(*) FROM access.studies_account_grant g WHERE NOT EXISTS(SELECT 1 FROM access.studies_assignment_event e WHERE e.account_id=g.account_id)").fetchone()[0]==0
        assert c.execute("SELECT count(*) FROM identity.studies_setup_event e JOIN identity.account_actor a USING(account_id) WHERE e.actor_id<>a.actor_id OR e.initiator_actor_id<>a.actor_id").fetchone()[0]==0
        identity=c.execute('SELECT executor_actor_id FROM identity.studies_runtime_principal WHERE enabled').fetchone()[0]
        access=c.execute('SELECT executor_actor_id FROM access.studies_runtime_principal WHERE enabled').fetchone()[0]
        assert identity==access==UUID(FIXTURE.actor)
        state=protected_state(c);c.execute('ROLLBACK')
    readiness.validate_qualification(json.loads((PROOF/'qualification.json').read_bytes()),PROOF)
    write_private(PROOF/'independent-inspection.json',{'read_only':True,'exact_current_heads':True,'matching_service_executor':True,'grant_event_actor_attribution_consistent':True,'qualification_sources_and_proofs_validated':True,'protected_counts':{name:len(rows) for name,rows in state.items()},'protected_sha256':sha256(json.dumps(state,sort_keys=True,default=str).encode()).hexdigest()})


def qualify():
    global PROOF,FIXTURE,EXECUTED_SOURCES
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id',required=True);parser.add_argument('--clean-run-id',required=True)
    parser.add_argument('--supabase',required=True,type=Path);parser.add_argument('--proof',required=True,type=Path)
    args=parser.parse_args()
    if args.run_id==args.clean_run_id:raise ValueError('distinct_new_runs_required')
    EXECUTED_SOURCES=source_hashes()
    clean=CurrentQualification(args.clean_run_id,args.supabase,args.proof/'clean')
    clean.execute_current(lambda fixture:None)
    FIXTURE=CurrentQualification(args.run_id,args.supabase,args.proof/'current',populated=True);PROOF=FIXTURE.proof
    def native(fixture):
        import platform,importlib.metadata
        write_private(PROOF/'interpreter.json',{'executable':sys.executable,'python_version':platform.python_version(),'dependencies':{name:importlib.metadata.version(name) for name in ('fastapi','uvicorn','pydantic','SQLAlchemy','psycopg','alembic','rfc8785','httpx')}})
        write_private(PROOF/'private.json',{'databases':{'upgrade':fixture.admin.database}})
        write_private(PROOF/'runtime.json',{'service_actor':fixture.actor,'service_key':fixture.service_key})
        write_private(PROOF/'current-clean-upgrade-proof.json',{'empty_owner_histories':True,'no_account_or_grant_seeds':clean.clean_no_seeds,'ordered_owner_results':[{'owner':owner,'exit_code':0} for owner in ('identity','access')],'clean_run_id':clean.run_id,'clean_result_sha256':sha256((clean.proof/'result.json').read_bytes()).hexdigest()})
        observed={row['stage']:row for row in fixture.cli_results}
        ordered=[observed[label] for label in ('cli-access-before-identity','cli-identity-failure','cli-identity-upgrade','cli-identity-repeat','cli-access-failure','cli-access-upgrade','cli-access-repeat')]
        write_private(PROOF/'current-cli-proof.json',{'failure_ledgers_preserved':True,'source_populated_upgrade':True,'activation_executed':False,'results':ordered})
        asyncio.run(provider_subject())
        # Establish the primary subject's acknowledged initial grant before
        # exercising a later distinct operation whose HTTP response is lost.
        async def initial_enrollment():
            import httpx
            provider=json.loads((PROOF/'provider.json').read_bytes())
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=runtime_app()),base_url='http://synthetic') as client:
                response=await client.post('/v2/enrollments/scribeswell-studies',headers={'Authorization':'Bearer '+provider['token'],'X-Service-Key':fixture.service_key},json={'operation_id':str(uuid4())})
            assert response.status_code==200 and response.json()['result']['disposition']=='created'
        asyncio.run(initial_enrollment())
        asyncio.run(first_use_race())
        write_private(PROOF/'current-first-use-race.json',json.loads((PROOF/'first-use-race.json').read_bytes()))
        asyncio.run(boundaries());asyncio.run(current_denials());asyncio.run(confirmed_http_denials());asyncio.run(lock_eligibility())
        retain_qualification()
        artifact=preparation_refusals();write_private(PROOF/'readiness.json',artifact)
        asyncio.run(default_startup(artifact));inspect_read_only()
    FIXTURE.execute_current(native)
    print('studies_current_owner_qualification_passed')

if __name__=='__main__':
    def interrupted(signum,frame):raise KeyboardInterrupt()
    signal.signal(signal.SIGTERM,interrupted)
    try:qualify()
    except KeyboardInterrupt:raise SystemExit(130) from None
    except Exception as error:
        print('studies_current_owner_qualification_failed:'+type(error).__name__,file=sys.stderr)
        raise SystemExit(1) from None
