"""Fresh genuine-provider/native cleanup proofs; never a retained fixture target."""
import base64
import json
import secrets
import time
from uuid import uuid4

import httpx
import psycopg
from sqlalchemy.engine import make_url

from apps.pts.tests.integration_fixture import private, raw, mint


def recovery_session(configuration,output):
    """Restricted fresh-fixture operator: genuine provider recovery verification.

    This does not supply a browser auth client or refresh owner. Its only output
    is a private standard provider Session for the existing SDK callback path.
    """
    from pathlib import Path
    selected=json.loads(Path(configuration).read_text())
    with httpx.Client(timeout=5,trust_env=False) as client:
        generated=client.post(selected['origin']+'/admin/generate_link',headers={'Authorization':'Bearer '+selected['admin']},
            json={'type':'recovery','email':selected['email']})
        assert generated.status_code==200,'provider_recovery_link_failed'
        token=generated.json()['hashed_token']
        verified=client.post(selected['origin']+'/verify',json={'type':'recovery','token_hash':token})
        assert verified.status_code==200,'provider_recovery_verification_failed'
        session=verified.json();assert session['user']['id']==selected['account'] and session['access_token'] and session['refresh_token']
        private(Path(output),session)


def unmapped_account(f):
    admin=mint(f.frame['secret'],f.frame['issuer'],aud='authenticated',role='service_role')
    email='pts-unmapped-'+f.nonce+'@example.invalid';password=secrets.token_urlsafe(32)
    with httpx.Client(timeout=5,trust_env=False) as client:
        result=client.post(f.frame['origin']+'/admin/users',headers={'Authorization':'Bearer '+admin},json={'email':email,'password':password,'email_confirm':True})
        assert result.status_code==200
        signed=client.post(f.frame['origin']+'/token?grant_type=password',json={'email':email,'password':password})
        assert signed.status_code==200
    subject={'account':signed.json()['user']['id'],'email':email,'password':password,'absent_grants':True,'unmapped':True,**signed.json()}
    with psycopg.connect(raw(f.frame['urls']['admin'])) as connection:
        assert connection.execute('SELECT count(*) FROM identity.account_actor WHERE account_id=%s',(subject['account'],)).fetchone()==(0,)
        assert connection.execute('SELECT count(*) FROM access.account_grants WHERE account_id=%s',(subject['account'],)).fetchone()==(0,)
    f.subjects.append(subject);private(f.out/'cleanup-unmapped-subject-private.json',subject)


def qualify(f):
    f.guard();origin=f.services['access']['origin'];pts=f.services['pts']['origin'];key=f.pts_environment['PTS_CURRENT_SESSION_SERVICE_KEY']
    observations=[]
    unmapped=next((value for value in f.subjects if value.get('unmapped')),None)
    if unmapped:
        with psycopg.connect(raw(f.frame['urls']['admin'])) as connection:
            counts={
                'account_actors':connection.execute('SELECT count(*) FROM identity.account_actor WHERE account_id=%s',(unmapped['account'],)).fetchone()[0],
                'account_grants':connection.execute('SELECT count(*) FROM access.account_grants WHERE account_id=%s',(unmapped['account'],)).fetchone()[0],
                'cleanup_receipts':connection.execute('SELECT count(*) FROM identity.file_cleanup_receipts WHERE account_id=%s',(unmapped['account'],)).fetchone()[0],
            }
        assert counts=={'account_actors':0,'account_grants':0,'cleanup_receipts':0},'unmapped_logout_created_owner_state'
        observations.append({'case':'post-browser-unmapped-logout-created-no-owner-state','counts':counts})
    # A genuine ordinary login has no cleanup receipt under these browser faults.
    # Only this NEW fixture's native owner can establish its exact provider absence;
    # SDK-null and generic401 are deliberately insufficient oracles.
    oracle_path=f.out/'private-fault-session-oracles-private.json'
    if oracle_path.exists():
        pairs=json.loads(oracle_path.read_text());assert len(pairs)==3,'private_fault_oracles_incomplete'
        with psycopg.connect(raw(f.frame['urls']['admin'])) as connection:
            for pair in pairs:
                assert pair['account_id']==f.subjects[0]['account']
                assert connection.execute('SELECT count(*) FROM auth.sessions WHERE user_id=%s AND id=%s',(pair['account_id'],pair['session_id'])).fetchone()==(0,),'private_fault_original_provider_session_still_present'
        observations.append({'case':'ordinary-private-fault-exact-original-provider-absence','faults':[pair['case'] for pair in pairs],'exact_absent_pairs':len(pairs),'oracle':'actual fresh native Auth pair, not SDK-null/401'})
    with httpx.Client(timeout=5,trust_env=False) as client:
        def owner(path,token,expected=200,**kwargs):
            started=time.monotonic()
            response=client.post(origin+'/v2/identity/'+path,headers={'Authorization':'Bearer '+token,'X-Service-Key':key},**kwargs)
            assert response.status_code==expected,'cleanup_owner_status_'+str(response.status_code)
            assert response.headers['cache-control']=='private, no-store'
            assert time.monotonic()-started<2.4
            return response.json()
        def signin(index):
            result=client.post(f.frame['origin']+'/token?grant_type=password',json={'email':f.subjects[index]['email'],'password':f.subjects[index]['password']})
            assert result.status_code==200;return result.json()
        sessions=[signin(0),signin(1)]
        originals=[value['access_token'] for value in sessions]
        evidence=[owner('file-cleanup/prepare',token) for token in originals]
        assert evidence[0]['session_id']!=evidence[1]['session_id']
        owner('file-cleanup/prepare',originals[0])
        with psycopg.connect(raw(f.frame['urls']['admin'])) as connection:
            rows=connection.execute('SELECT account_id,session_id,created_by,executor_role FROM identity.file_cleanup_receipts WHERE session_id=ANY(%s::uuid[])',([value['session_id'] for value in evidence],)).fetchall()
            assert len(rows)==2
            for account,session,actor,executor in rows:
                expected=next(value for value in f.subjects if value['account']==str(account))
                assert str(actor)==expected['actor_id'] and str(actor)!=str(account) and executor=='identity_current_session_runtime'
        observations.append({'case':'exact-original-receipts-repeat-and-distinct-verified-actor','receipt_count':2})
        owner('file-cleanup/check','arbitrary',401)
        owner('file-cleanup/check',originals[0],422,json={'account_id':f.subjects[1]['account']})
        owner('file-cleanup/check?session_id='+evidence[1]['session_id'],originals[0],422)
        # Current eligibility is intentionally not provider-session absence.
        with psycopg.connect(raw(f.frame['urls']['identity'])) as connection:
            connection.execute('UPDATE identity.users SET deleted_at=now() WHERE id=%s',(f.subjects[0]['account'],))
        try:
            owner('current-session',originals[0],401)
            assert owner('file-cleanup/check',originals[0])['provider_session']=='present'
        finally:
            with psycopg.connect(raw(f.frame['urls']['identity'])) as connection:
                connection.execute('UPDATE identity.users SET deleted_at=NULL WHERE id=%s',(f.subjects[0]['account'],))
        observations.append({'case':'ineligible-account-is-not-revoked-session','cleanup_provider_session':'present','current_status':401})
        with psycopg.connect(raw(f.frame['urls']['admin'])) as blocker:
            blocker.execute('LOCK TABLE identity.file_cleanup_receipts IN ACCESS EXCLUSIVE MODE')
            owner('file-cleanup/check',originals[0],503)
        assert owner('file-cleanup/check',originals[0])['provider_session']=='present'
        f.docker('pause',f.frame['container'])
        try:
            owner('current-session',originals[0],503)
            assert owner('file-cleanup/check',originals[0])['provider_session']=='present'
        finally:f.docker('unpause',f.frame['container'])
        f.wait(f.frame['origin'])
        observations.append({'case':'native-owner-outage-and-genuine-provider-outage-recovery','cleanup-never-reported-absence':True})
        # Native runtime has only the three constrained routines; no raw receipt,
        # mapping, Auth table, DDL or receipt mutation authority.
        runtime=make_url(f.frame['urls']['admin']).set(username=f.session_owner.RUNTIME,password=f.session_roles[f.session_owner.RUNTIME]).render_as_string(hide_password=False)
        denied=[]
        for statement in ('SELECT credential_sha256 FROM identity.file_cleanup_receipts','SELECT actor_id FROM identity.account_actor','SELECT id FROM auth.sessions','SELECT id FROM auth.users','UPDATE identity.file_cleanup_receipts SET created_at=now()','DELETE FROM identity.file_cleanup_receipts','CREATE TABLE identity.cleanup_forbidden(id int)'):
            try:
                with psycopg.connect(raw(runtime)) as connection:connection.execute(statement)
            except psycopg.errors.InsufficientPrivilege as failure:denied.append(failure.sqlstate)
            else:raise AssertionError('cleanup_native_forbidden_operation_succeeded')
        assert denied==['42501']*7
        observations.append({'case':'actual-restricted-cleanup-role-denials','sqlstates':denied})
        # An externally revoked, still-unexpired original remains cleanup-only.
        result=client.post(f.frame['origin']+'/logout?scope=local',headers={'Authorization':'Bearer '+originals[0]})
        assert result.status_code in (200,204)
        owner('current-session',originals[0],401);owner('file-cleanup/prepare',originals[0],401)
        assert owner('file-cleanup/check',originals[0])['provider_session']=='absent'
        observations.append({'case':'externally-revoked-original-cleanup-only','current_and_prepare':401,'provider_session':'absent'})
        # Test-only expiry observation derives from the genuine provider's response;
        # runtime authority continues through the unchanged owner verification.
        expiry=json.loads(base64.urlsafe_b64decode(originals[1].split('.')[1]+'=='))['exp']
        assert expiry-time.time()<65
        while time.time()<=expiry+1:time.sleep(min(1,expiry+1-time.time()+.01))
        owner('current-session',originals[1],401);owner('file-cleanup/prepare',originals[1],401)
        assert owner('file-cleanup/check',originals[1])['provider_session']=='present'
        refreshed=client.post(f.frame['origin']+'/token?grant_type=refresh_token',json={'refresh_token':sessions[1]['refresh_token']})
        assert refreshed.status_code==200
        live=owner('current-session',refreshed.json()['access_token'])
        assert live['account_id']==evidence[1]['account_id'] and live['session_id']==evidence[1]['session_id']
        result=client.post(f.frame['origin']+'/logout?scope=local',headers={'Authorization':'Bearer '+refreshed.json()['access_token']})
        assert result.status_code in (200,204)
        for _ in range(2):
            assert owner('file-cleanup/check',originals[1])['provider_session']=='absent'
            clear=client.post(pts+'/api/file-session/clear',headers={'Authorization':'Bearer '+originals[1],'Origin':f.frontend_origin,'Host':httpx.URL(f.file_origin).netloc.decode()})
            assert clear.status_code==200 and clear.json()['provider_session']=='absent'
        observations.append({'case':'genuine-expired-live-original-refresh-and-repeat-cleanup-after-revocation','current_and_prepare':401,'existing-provider-refresh':200,'exact-session-preserved':True,'expired-original-final-proof':'absent'})
    private(f.out/'cleanup-owner-native-proof.json',{'observations':observations,'packaged_access':bool(getattr(f,'access_image',None)),'raw_credentials_or_digests_exported':False})
    f.checks.append('actual-cleanup-receipts-expiry-revocation-permissions-owner-provider-outage-and-recovery')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--recovery-input',required=True);parser.add_argument('--recovery-output',required=True);args=parser.parse_args()
    try:recovery_session(args.recovery_input,args.recovery_output)
    except Exception:raise SystemExit('provider_recovery_fixture_failed') from None
