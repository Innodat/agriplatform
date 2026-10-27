"""Focused host oracles; these doubles do not establish actual mail/Auth proof."""
import copy
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlencode
from uuid import uuid4
import pytest

sys.path.insert(0,str(Path(__file__).parent))
import studies_signup_fixture as signup
import studies_owner_fixture as owner

EMAIL='signup-'+'a'*32+'@example.invalid'
LINK='http://localhost:55491/auth/v1/verify?'+urlencode({'token':'synthetic-private-token','type':'signup','redirect_to':'http://localhost:5192/'})

def message(link=LINK,email=EMAIL):
    return {'ID':'synthetic-id','To':[{'Address':email}],'HTML':'<a href="'+link.replace('&','&amp;')+'">Confirm</a>','Text':''}

def listing(*messages):return {'total':len(messages),'messages':list(messages)}

class Response:
    def __init__(self,value,status=200,chunks=None):self.value=value;self.status_code=status;self.chunks=chunks
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def iter_bytes(self):return iter(self.chunks if self.chunks is not None else [json.dumps(self.value).encode()])

class Client:
    def __init__(self,*responses):self.responses=iter(responses);self.calls=[]
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def stream(self,method,url,**kwargs):self.calls.append((method,url,kwargs));return next(self.responses)

def test_exact_local_mail_returns_only_validated_confirmation_link():
    item=message();client=Client(Response(listing(item)),Response(item))
    assert signup.Mailbox(client).poll(EMAIL)==LINK
    assert [call[:2] for call in client.calls]==[
        ('GET','http://127.0.0.1:15494/api/v1/messages?start=0&limit=100'),
        ('GET','http://127.0.0.1:15494/api/v1/message/synthetic-id')]
    assert all(call[2]['follow_redirects'] is False and 0<call[2]['timeout']<=2 for call in client.calls)

@pytest.mark.parametrize('link',[
    LINK.replace('localhost:55491','localhost:55481'),LINK.replace('localhost:55491','evil.invalid'),
    LINK.replace('http:','https:'),LINK.replace('localhost:55491','127.0.0.1:55491'),
    LINK.replace('/auth/v1/verify','/auth/v1/callback'),LINK+'&type=signup',LINK+'&extra=x',LINK+'#token=x',
    LINK.replace('http%3A%2F%2Flocalhost%3A5192%2F','http%3A%2F%2Fevil.invalid%2F'),
    LINK.replace('http%3A%2F%2Flocalhost%3A5192%2F','http%3A%2F%2Flocalhost%3A5192%2F%3Fprivate%3Dx'),
    LINK.replace('type=signup','type=magiclink'),LINK.replace('localhost:55491','user:pass@localhost:55491'),
    LINK.replace('synthetic-private-token',''),LINK+'&redirect_to=http%3A%2F%2Flocalhost%3A5192%2F',
    LINK+'\n', 'http://[broken/auth/v1/verify?token=private',
])
def test_confirmation_url_rejects_foreign_ambiguous_or_unsafe_inputs(link):
    with pytest.raises(RuntimeError,match='^qualification_signup_invalid_link$') as failure:signup.validate_link(link)
    assert 'private-token' not in str(failure.value)

def test_html_and_text_repetition_of_same_link_is_unambiguous():
    item=message();item['Text']='Confirm: '+LINK
    assert signup.message_link(item,EMAIL)==LINK

@pytest.mark.parametrize('change,code',[
    ('wrong-recipient','wrong_recipient'),('multiple-recipients','wrong_recipient'),('cc-recipient','wrong_recipient'),
    ('missing-link','missing_link'),('ambiguous-link','ambiguous_link'),('wrong-link','invalid_link'),('bad-html','mail_shape'),
])
def test_mailbody_rejects_wrong_missing_or_ambiguous_evidence(change,code):
    item=message()
    if change=='wrong-recipient':item['To'][0]['Address']='other@example.invalid'
    elif change=='multiple-recipients':item['To'].append({'Address':'other@example.invalid'})
    elif change=='cc-recipient':item['Cc']=[{'Address':'other@example.invalid'}]
    elif change=='missing-link':item['HTML']='No confirmation here'
    elif change=='ambiguous-link':item['Text']=LINK.replace('synthetic-private-token','second-private-token')
    elif change=='wrong-link':item['HTML']=item['HTML'].replace('localhost:55491','evil.invalid')
    else:item['HTML']={}
    with pytest.raises(RuntimeError,match='^qualification_signup_'+code+'$'):signup.message_link(item,EMAIL)

def test_mail_poll_missing_recipient_has_total_bound():
    now=[0]
    client=Client(*(Response(listing(message(email='other@example.invalid'))) for _ in range(10)))
    def sleep(seconds):now[0]+=seconds
    with pytest.raises(RuntimeError,match='^qualification_signup_mail_timeout$'):
        signup.Mailbox(client,clock=lambda:now[0],sleep=sleep).poll(EMAIL,seconds=.5)
    assert now[0]==.5 and len(client.calls)==3

@pytest.mark.parametrize('change,code',[
    ('duplicate','ambiguous_mail'),('wrong-detail-recipient','wrong_recipient'),('wrong-detail-id','mail_shape'),
    ('unsafe-id','mail_shape'),('overflow','mail_shape'),('malformed','mail_shape'),
])
def test_mailbox_cannot_select_arbitrary_message_or_hide_ambiguity(change,code):
    item=message();detail=message();summary=listing(item)
    if change=='duplicate':summary=listing(item,item)
    elif change=='wrong-detail-recipient':detail['To'][0]['Address']='other@example.invalid'
    elif change=='wrong-detail-id':detail['ID']='another-id'
    elif change=='unsafe-id':item['ID']='../release'
    elif change=='overflow':summary['total']=101
    else:summary={'messages':'private body','total':0}
    with pytest.raises(RuntimeError,match='^qualification_signup_'+code+'$'):
        signup.Mailbox(Client(Response(summary),Response(detail))).poll(EMAIL)

@pytest.mark.parametrize('response,code',[
    (Response({},status=302),'mail_response'),(Response({},status=500),'mail_response'),
    (Response(None,chunks=[b'x'*(signup.MAX_MAIL_BYTES+1)]),'mail_size'),
    (Response(None,chunks=[b'private token is not json']),'mail_shape'),
])
def test_mail_response_errors_have_fixed_private_diagnostics(response,code):
    with pytest.raises(RuntimeError,match='^qualification_signup_'+code+'$') as failure:
        signup.Mailbox(Client(response)).poll(EMAIL)
    assert 'private token' not in str(failure.value)

def test_mail_stream_deadline_is_checked_between_chunks():
    ticks=iter((0,1,4));mail=signup.Mailbox(clock=lambda:next(ticks))
    with pytest.raises(RuntimeError,match='^qualification_signup_mail_timeout$'):
        mail.read(Client(Response(None,chunks=[b'{}',b'{}'])),'/api/v1/messages',3)

@pytest.mark.parametrize('seconds',[0,-1,21])
def test_mail_poll_cannot_extend_the_declared_deadline(seconds):
    client=Client()
    with pytest.raises(RuntimeError,match='mail_timeout'):signup.Mailbox(client).poll(EMAIL,seconds=seconds)
    assert not client.calls

def test_mail_poll_retries_network_failure_until_bounded_deadline():
    import httpx
    now=[0]
    class Unavailable(Client):
        def stream(self,*args,**kwargs):raise httpx.ReadTimeout('private synthetic URL and body')
    with pytest.raises(RuntimeError,match='^qualification_signup_mail_timeout$'):
        signup.Mailbox(Unavailable(),clock=lambda:now[0],sleep=lambda seconds:now.__setitem__(0,now[0]+seconds)).poll(EMAIL,seconds=.5)
    assert now[0]==.5

@pytest.mark.parametrize('recipient',['real@example.com','signup-short@example.invalid','signup-'+'a'*32+'@example.com'])
def test_non_synthetic_recipients_are_refused_before_mail_io(recipient):
    client=Client()
    with pytest.raises(RuntimeError,match='recipient_invalid'):signup.Mailbox(client).poll(recipient)
    assert client.calls==[]

def enrollment_states():
    before={name:[] for name in owner.PROTECTED_TABLES};before['identity.org']=[{'id':'unchanged-org'}]
    before['identity.person']=[{'id':'unchanged-person'}];before['identity.employment']=[{'id':'unchanged-employment'}]
    before['identity.users']=[{'id':'new-account'}]
    after=copy.deepcopy(before);expected={'account':'new-account','actor':'durable-actor','enrollment':'explicit-operation'}
    after['identity.actor']=[{'id':'durable-actor','kind':'account','actor_key':None,'created_by':'executor','updated_by':'executor','created_at':1,'updated_at':1}]
    after['identity.account_actor']=[{'account_id':'new-account','actor_id':'durable-actor','actor_kind':'account','created_by':'executor','created_at':1}]
    row={'account_id':'new-account','actor_id':'durable-actor','executor_actor_id':'executor','initiator_actor_id':'durable-actor','operation_id':'explicit-operation'}
    for table in ('identity.studies_setup_event','identity.studies_setup_outcome','access.studies_account_grant','access.studies_assignment_event','access.studies_enrollment_outcome'):after[table]=[dict(row)]
    after['access.studies_account_grant'][0].update(permission='scribeswell.studies.use',authorization_scope='account',revoked_at=None,created_at=1)
    return before,after,expected

@pytest.mark.parametrize('change',[None,'wrong-actor','wrong-executor','wrong-initiator','wrong-operation','org-membership','new-person','new-employment','baseline-change','premature-study','wrong-scope','revoked-grant'])
def test_enrollment_oracle_checks_current_permission_durable_attribution_and_no_prerequisites(change):
    before,after,expected=enrollment_states()
    if change=='wrong-actor':after['identity.account_actor'][0]['actor_id']='other'
    elif change=='wrong-executor':after['identity.studies_setup_outcome'][0]['executor_actor_id']='other'
    elif change=='wrong-initiator':after['access.studies_assignment_event'][0]['initiator_actor_id']='other'
    elif change=='wrong-operation':after['identity.studies_setup_event'][0]['operation_id']='implicit'
    elif change=='org-membership':after['identity.org_member']=[{'id':'new'}]
    elif change=='new-person':after['identity.person'].append({'id':'new'})
    elif change=='new-employment':after['identity.employment'].append({'id':'new'})
    elif change=='baseline-change':after['identity.org'][0]['id']='changed'
    elif change=='premature-study':after['scribeswell_studies.studies']=[{'id':'new'}]
    elif change=='wrong-scope':after['access.studies_account_grant'][0]['authorization_scope']='organization'
    elif change=='revoked-grant':after['access.studies_account_grant'][0]['revoked_at']='now'
    if change:
        with pytest.raises(AssertionError):signup.assert_enrollment(before,after,expected,'executor')
    else:signup.assert_enrollment(before,after,expected,'executor')

def signup_profile_states():
    # Characterize identity.log_audit's users INSERT shape from the pinned
    # 20250815160000_platform_create_audit_log_tbl.sql owner migration.
    account='11111111-1111-4111-8111-111111111111'
    before={name:[] for name in owner.PROTECTED_TABLES}
    before['identity.users']=[{'id':'old'}]
    before['identity.audit_log']=[]
    after=copy.deepcopy(before)
    profile={'id':account,'username':EMAIL,'actor_key':None,'deleted_at':None,'is_system':False,
        'created_by':None,'created_at':'2026-10-27T12:00:00+00:00','updated_by':None,'updated_at':'2026-10-27T12:00:00+00:00'}
    after['identity.users'].append(profile)
    after['identity.audit_log'].append({'id':'22222222-2222-4222-8222-222222222222','table_name':'users',
        'record_id':account,'operation':'INSERT','actor_id':None,'timestamp':'2026-10-27T12:00:00+00:00',
        'diff':copy.deepcopy(profile),'column_changes':None})
    return before,after,account

def test_legitimate_owner_profile_insert_audit_is_characterized():
    before,after,account=signup_profile_states()
    signup.assert_profile_only(before,after,account)

@pytest.mark.parametrize('change',[None,'implicit-binding','implicit-study','baseline-mutation','wrong-account'])
def test_signup_profile_only_oracle_rejects_implicit_effects(change):
    before,after,account=signup_profile_states()
    if change=='implicit-binding':after['identity.account_actor'].append({'id':'implicit'})
    elif change=='implicit-study':after['scribeswell_studies.studies'].append({'id':'implicit'})
    elif change=='baseline-mutation':after['identity.users'][0]['id']='changed'
    elif change=='wrong-account':after['identity.users'][1]['id']='other'
    if change:
        with pytest.raises(AssertionError):signup.assert_profile_only(before,after,account)
    else:signup.assert_profile_only(before,after,account)

@pytest.mark.parametrize('change',['foreign-record','wrong-operation','mismatched-diff','wrong-table','authenticated-actor',
    'column-changes','missing-audit','extra-audit','invalid-id','nil-id','invalid-time','unqualified-time','unrelated-change','old-audit-change'])
def test_profile_audit_oracle_rejects_every_unrelated_or_invalid_change(change):
    before,after,account=signup_profile_states();audit=after['identity.audit_log'][0]
    if change=='foreign-record':audit['record_id']='33333333-3333-4333-8333-333333333333'
    elif change=='wrong-operation':audit['operation']='UPDATE'
    elif change=='mismatched-diff':audit['diff']['username']='other@example.invalid'
    elif change=='wrong-table':audit['table_name']='actor'
    elif change=='authenticated-actor':audit['actor_id']=account
    elif change=='column-changes':audit['column_changes']={}
    elif change=='missing-audit':after['identity.audit_log'].clear()
    elif change=='extra-audit':after['identity.audit_log'].append(dict(audit,id='33333333-3333-4333-8333-333333333333'))
    elif change=='invalid-id':audit['id']='not-a-uuid'
    elif change=='nil-id':audit['id']='00000000-0000-0000-0000-000000000000'
    elif change=='invalid-time':audit['timestamp']='not-a-timestamp'
    elif change=='unqualified-time':audit['timestamp']='2026-10-27T12:00:00'
    elif change=='unrelated-change':after['identity.org_member'].append({'id':'unexpected'})
    else:
        before['identity.audit_log'].append({'id':'retained-audit','operation':'INSERT'})
        after['identity.audit_log'].append({'id':'retained-audit','operation':'DELETE'})
    with pytest.raises(AssertionError):signup.assert_profile_only(before,after,account)

def test_signup_hook_runs_only_after_original_owner_observations(tmp_path,monkeypatch):
    events=[]
    monkeypatch.setattr(owner,'RESERVATIONS',tmp_path/'reservations');monkeypatch.setattr(owner,'check_ports',lambda:None)
    class Run(owner.Qualification):
        def wrapper(self,action):events.append(action)
        def capture_status(self):pass
        def prepare_owners(self):pass
        def start_apps(self):pass
        def browser(self):events.append('original-browser')
        def observe(self,label):events.append(label)
        def snapshot(self,*args,**kwargs):pass
        def operator(self,*args):events.append('original-disable')
        def command(self,*args,**kwargs):events.append('original-denial-browser')
        def extra_qualification(self):events.append('signup-hook')
        def verify_sources(self):events.append('sources')
    Run(str(uuid4()),Path('/explicit/supabase'),tmp_path/'proof').execute()
    assert events.index('signup-hook')>events.index('after-denial')>events.index('original-denial-browser')>events.index('after-browser')
    assert events[-3:]==['signup-hook','sources','stop']

def test_expiry_checkpoint_waits_for_actual_provider_sent_time_without_auth_writes(tmp_path,monkeypatch):
    from datetime import datetime,timezone,timedelta
    sent=datetime(2026,10,27,tzinfo=timezone.utc);times=iter((sent+timedelta(seconds=121),sent+timedelta(seconds=122)))
    class Clock:
        @staticmethod
        def now(zone):assert zone==timezone.utc;return next(times)
    monkeypatch.setattr(signup,'datetime',Clock);sleeps=[];monkeypatch.setattr(signup.time,'sleep',sleeps.append)
    run=object.__new__(signup.SignupQualification);run.proof=tmp_path
    run.signup_inputs={'expired':{'email':EMAIL}};calls=[]
    run.auth_account=lambda email,confirmed:calls.append((email,confirmed)) or {'sent_at':sent}
    run.snapshot=lambda name,previous:calls.append((name,previous))
    run.record_auth=lambda name:calls.append(('auth-observation',name))
    run.signup_observe('expiry-ready')
    observation=json.loads((tmp_path/'expiry-observation.json').read_text())
    assert sleeps==[.2] and observation=={'otp_expiry_seconds':120,'elapsed_seconds':122,'fixture_did_not_write_auth':True}
    assert calls==[(EMAIL,False),('signup-before-expiry-link','signup-expired-created'),('auth-observation','expiry-ready')]
    assert (tmp_path/'expiry-observation.json').stat().st_mode&0o777==0o600

def test_source_inventory_freezes_all_signup_execution_inputs():
    paths=owner.source_inventory()
    for name in ('tests/studies_signup_fixture.py','tools/py/qualify_studies_signup.py','web/playwright.signup.config.cjs','web/tests/studies-signup.integration.cjs'):
        assert owner.APP/name in paths

def test_signup_diagnostics_allow_only_safe_source_locations():
    result=subprocess.run(['node',str(owner.APP/'web/tests/studies-signup-reporter.oracle.cjs')],capture_output=True,text=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='signup-safe-source-oracle-passed'
    assert 'private-synthetic' not in result.stdout+result.stderr
