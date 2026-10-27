"""Local-only real signup qualification layered on the original owner lifecycle.

Mail bodies/credentials/confirmation URLs never enter diagnostics. Only the two
GET Mailpit read endpoints are used; nothing sends/releases/relays mail here.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import secrets
import sys
import time
from urllib.parse import parse_qs, urlsplit
from uuid import UUID, uuid4

from studies_owner_fixture import APP, ROOT, TARGET_CONFIG, WEB_URL, Qualification, private

OTP_SECONDS=120
MAIL_SECONDS=20
MAX_MAIL_BYTES=512*1024

def fail(code):
    raise RuntimeError('qualification_signup_'+code) from None

def validate_link(value):
    try:
        if not isinstance(value,str) or len(value)>4096 or any(ord(c)<33 for c in value):fail('invalid_link')
        url=urlsplit(value)
        expected=urlsplit(TARGET_CONFIG['origins'][1])
        if (url.scheme!='http' or url.netloc!=expected.netloc or url.path!='/auth/v1/verify'
                or url.fragment or url.username is not None or url.password is not None):fail('invalid_link')
        query=parse_qs(url.query,keep_blank_values=True,strict_parsing=True,max_num_fields=4)
        if set(query)!={'token','type','redirect_to'} or any(len(v)!=1 for v in query.values()):fail('invalid_link')
        if (query['type']!=['signup'] or query['redirect_to']!=[WEB_URL+'/']
                or not re.fullmatch(r'[A-Za-z0-9_-]{10,512}',query['token'][0])):fail('invalid_link')
    except (ValueError,TypeError):fail('invalid_link')
    return value

class Links(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.values=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()=='a':self.values.extend(value for name,value in attrs if name.lower()=='href' and value)

def exact_recipient(message,email):
    recipients=message.get('To')
    return (isinstance(recipients,list) and len(recipients)==1
        and isinstance(recipients[0],dict) and recipients[0].get('Address')==email
        and not message.get('Cc') and not message.get('Bcc'))

def message_link(message,email):
    if not isinstance(message,dict) or not exact_recipient(message,email):fail('wrong_recipient')
    html=message.get('HTML','');text=message.get('Text','')
    if not isinstance(html,str) or not isinstance(text,str):fail('mail_shape')
    parser=Links();parser.feed(html)
    values=parser.values+re.findall(r'https?://[^\s<>"\']+',text)
    # Template prose may link to the app. Select confirmation-shaped links,
    # then validate every candidate, including wrong origins and redirects.
    candidates=set()
    for value in values:
        try:
            url=urlsplit(value)
            if '/auth/v1/verify' in url.path or 'token=' in url.query:candidates.add(value)
        except ValueError:fail('invalid_link')
    if len(candidates)!=1:fail('ambiguous_link' if candidates else 'missing_link')
    return validate_link(candidates.pop())

class Mailbox:
    def __init__(self,client=None,clock=time.monotonic,sleep=time.sleep):
        self.client=client;self.clock=clock;self.sleep=sleep
        self.origin='http://127.0.0.1:'+str(TARGET_CONFIG['ports']['mail'])

    def read(self,client,path,deadline):
        remaining=deadline-self.clock()
        if remaining<=0:fail('mail_timeout')
        # httpx never follows redirects or environment proxies. Bound streamed
        # bytes and each read as well as the overall polling deadline.
        try:
            with client.stream('GET',self.origin+path,timeout=min(2,remaining),follow_redirects=False) as response:
                if response.status_code!=200:fail('mail_response')
                raw=bytearray()
                for chunk in response.iter_bytes():
                    raw.extend(chunk)
                    if len(raw)>MAX_MAIL_BYTES:fail('mail_size')
                    if self.clock()>=deadline:fail('mail_timeout')
                return json.loads(raw)
        except (ValueError,TypeError):fail('mail_shape')

    def poll(self,email,seconds=MAIL_SECONDS):
        import httpx
        if not re.fullmatch(r'signup-[a-f0-9]{32}@example\.invalid',email):fail('recipient_invalid')
        if not 0<seconds<=MAIL_SECONDS:fail('mail_timeout')
        deadline=self.clock()+seconds
        with httpx.Client(trust_env=False) if self.client is None else self.client as client:
            while self.clock()<deadline:
                try:
                    listing=self.read(client,'/api/v1/messages?start=0&limit=100',deadline)
                    if not isinstance(listing,dict):fail('mail_shape')
                    messages=listing.get('messages');total=listing.get('total')
                    if (not isinstance(messages,list) or type(total) is not int or total!=len(messages)
                            or len(messages)>100 or any(not isinstance(m,dict) or not isinstance(m.get('To'),list) for m in messages)):fail('mail_shape')
                    selected=[m for m in messages if any(isinstance(r,dict) and r.get('Address')==email for r in (m.get('To') or []))]
                    if len(selected)>1:fail('ambiguous_mail')
                    if selected:
                        item=selected[0]
                        if not exact_recipient(item,email):fail('wrong_recipient')
                        identifier=item.get('ID')
                        if not isinstance(identifier,str) or not re.fullmatch(r'[A-Za-z0-9-]{1,128}',identifier):fail('mail_shape')
                        detail=self.read(client,'/api/v1/message/'+identifier,deadline)
                        if not isinstance(detail,dict) or detail.get('ID')!=identifier:fail('mail_shape')
                        return message_link(detail,email)
                except httpx.HTTPError:
                    # Fixed timeout/refusal diagnostics, never vendor exception
                    # strings which can contain request values or response data.
                    pass
                self.sleep(min(.2,max(0,deadline-self.clock())))
        fail('mail_timeout')

def added_rows(before,after,allowed):
    """Every old row is immutable; permit only exact per-table additions."""
    assert before.keys()==after.keys()
    additions={}
    for table,old in before.items():
        new=after[table]
        assert all(row in new for row in old),'Signup changed baseline business row'
        extra=[row for row in new if row not in old]
        assert len(new)==len(old)+allowed.get(table,0) and len(extra)==allowed.get(table,0),'Unexpected signup business effects'
        additions[table]=extra
    return additions

def assert_profile_only(before,after,account):
    # The existing owner trigger audits every profile INSERT. Permit that exact
    # companion row, while retaining complete baseline/no-authority comparisons.
    assert 'identity.audit_log' in before
    additions=added_rows(before,after,{'identity.users':1,'identity.audit_log':1})
    profile=additions['identity.users'][0];audit=additions['identity.audit_log'][0]
    assert profile['id']==account
    assert set(audit)=={'id','table_name','record_id','operation','actor_id','timestamp','diff','column_changes'}
    assert audit['table_name']=='users' and audit['record_id']==account and audit['operation']=='INSERT'
    assert audit['diff']==profile and audit['column_changes'] is None and audit['actor_id'] is None
    try:
        identifier=UUID(audit['id']);timestamp=datetime.fromisoformat(audit['timestamp'])
    except (ValueError,TypeError,AttributeError):raise AssertionError('Invalid profile audit identity or timestamp') from None
    assert identifier.int and str(identifier)==audit['id']
    assert timestamp.utcoffset() is not None and timestamp.utcoffset().total_seconds()==0
    return additions

def assert_enrollment(before,after,expected,executor):
    tables=('identity.actor','identity.account_actor','identity.studies_setup_event','identity.studies_setup_outcome',
        'access.studies_account_grant','access.studies_assignment_event','access.studies_enrollment_outcome')
    additions=added_rows(before,after,dict.fromkeys(tables,1))
    account=expected['account'];actor=expected['actor'];operation=expected['enrollment']
    binding=additions['identity.account_actor'][0]
    assert binding['account_id']==account and binding['actor_id']==actor and binding['actor_kind']=='account'
    assert binding['created_by']==executor and binding['created_at']
    row=additions['identity.actor'][0]
    assert row['id']==actor and row['kind']=='account' and row['actor_key'] is None
    assert row['created_by']==row['updated_by']==executor and row['created_at'] and row['updated_at']>=row['created_at']
    for table in tables[2:]:
        row=additions[table][0]
        assert row['account_id']==account and row['actor_id']==actor
        assert row['executor_actor_id']==executor and row['initiator_actor_id']==actor
        if table!='access.studies_account_grant':assert row['operation_id']==operation
    grant=additions['access.studies_account_grant'][0]
    assert grant['permission']=='scribeswell.studies.use' and grant['authorization_scope']=='account' and grant['revoked_at'] is None and grant['created_at']
    assert not after['identity.org_member']

class SignupQualification(Qualification):
    qualification_scope='Local signup/confirmation and owner HTTP/domain integration only; no production mail, default readiness, release or device claim'

    def auth_account(self,email,confirmed):
        with self.connect() as connection:
            rows=connection.execute('SELECT id,email_confirmed_at,confirmation_sent_at,created_at FROM auth.users WHERE email=%s',(email,)).fetchall()
        assert len(rows)==1 and bool(rows[0][1])==confirmed
        account,confirmation,sent,created=rows[0]
        assert sent is not None
        return {'id':str(account),'confirmed':bool(confirmation),'sent_at':sent,'created_at':created}

    def record_auth(self,name):
        with self.connect() as connection:
            rows=connection.execute('SELECT id,email_confirmed_at IS NOT NULL,confirmation_sent_at,created_at FROM auth.users WHERE email=ANY(%s) ORDER BY id',([value['email'] for value in self.signup_inputs.values()],)).fetchall()
        private(self.proof/('signup-'+name+'-auth.json'),{'independent_sql':True,'accounts':[
            {'account_id':str(account),'confirmed':confirmed,'confirmation_sent_at':sent,'created_at':created}
            for account,confirmed,sent,created in rows]})

    def signup_observe(self,name):
        inputs=self.signup_inputs
        if name=='valid-created':
            auth=self.auth_account(inputs['valid']['email'],False);self.signup_account=auth['id']
            assert_profile_only(self.signup_baseline,self.snapshot('signup-created'),auth['id'])
            link=Mailbox().poll(inputs['valid']['email'])
            private(self.proof/'valid-confirmation-private.json',{'link':link})
        elif name=='valid-unconfirmed':
            self.auth_account(inputs['valid']['email'],False)
            self.snapshot('signup-unconfirmed',previous='signup-created')
        elif name=='valid-confirmed':
            self.auth_account(inputs['valid']['email'],True)
            self.snapshot('signup-confirmed',previous='signup-created')
        elif name=='valid-enrolled':
            expected=json.loads((self.proof/'signup-enrollment-private.json').read_text())
            assert expected['account']==self.signup_account
            state=self.snapshot('signup-enrolled')
            assert_enrollment(self.protected_snapshots['signup-confirmed'],state,expected,self.actor)
        elif name=='valid-study-created':
            before=self.protected_snapshots['signup-enrolled'];after=self.snapshot('signup-study-created')
            additions=added_rows(before,after,{'scribeswell_studies.studies':1,'scribeswell_studies.receipts':1})
            expected=json.loads((self.proof/'signup-study-private.json').read_text())
            actor=json.loads((self.proof/'signup-enrollment-private.json').read_text())['actor']
            row=additions['scribeswell_studies.studies'][0]
            assert row['id']==expected['study'] and row['account_id']==self.signup_account and row['active']
            assert row['created_by']==row['updated_by']==actor and row['created_at'] and row['updated_at']>=row['created_at']
            row=additions['scribeswell_studies.receipts'][0]
            assert row['command']=='study.create' and row['operation_id']==expected['operation'] and row['created_by']==actor and row['account_id']==self.signup_account
            assert row['created_at'] and row['outcome']['study_id']==expected['study']
        elif name=='reused-rejected':self.snapshot('signup-reused',previous='signup-study-created')
        elif name=='expired-created':
            auth=self.auth_account(inputs['expired']['email'],False);self.expired_account=auth['id']
            assert_profile_only(self.protected_snapshots['signup-reused'],self.snapshot('signup-expired-created'),auth['id'])
            private(self.proof/'expired-confirmation-private.json',{'link':Mailbox().poll(inputs['expired']['email'])})
        elif name=='expiry-ready':
            # Real elapsed provider OTP expiry: do not update Auth/token tables,
            # change system clocks, forge timestamps or substitute an invalid link.
            auth=self.auth_account(inputs['expired']['email'],False)
            limit=time.monotonic()+OTP_SECONDS+5
            while True:
                elapsed=(datetime.now(timezone.utc)-auth['sent_at']).total_seconds()
                if elapsed>=OTP_SECONDS+2:break
                if time.monotonic()>=limit:fail('expiry_wait_timeout')
                time.sleep(min(.2,OTP_SECONDS+2-elapsed))
            private(self.proof/'expiry-observation.json',{'otp_expiry_seconds':OTP_SECONDS,'elapsed_seconds':elapsed,'fixture_did_not_write_auth':True})
            self.snapshot('signup-before-expiry-link',previous='signup-expired-created')
        elif name=='expired-rejected':
            self.auth_account(inputs['expired']['email'],False)
            self.snapshot('signup-expired-rejected',previous='signup-expired-created')
        else:fail('checkpoint_invalid')
        self.record_auth(name)

    def extra_qualification(self):
        self.operator('application.set_enabled',{'app_id':'scribeswell','enabled':True,'expected_revision':'3'})
        self.signup_baseline=self.snapshot('signup-baseline')
        self.signup_inputs={name:{'email':'signup-'+uuid4().hex+'@example.invalid','password':secrets.token_urlsafe(32)} for name in ('valid','expired')}
        private(self.proof/'signup-browser-private.json',{**self.signup_inputs,
            'service_key_sentinel':self.service_key,'provider_service_sentinel':self.status['service_role_key']})
        names=('valid-created','valid-unconfirmed','valid-confirmed','valid-enrolled','valid-study-created',
            'reused-rejected','expired-created','expiry-ready','expired-rejected')
        def checkpoints(process):
            for name in names:
                limit=time.monotonic()+45
                while not (self.proof/('signup-'+name+'-check.json')).exists():
                    if process.poll() is not None or time.monotonic()>=limit:fail('checkpoint_missing')
                    time.sleep(.05)
                self.signup_observe(name)
                private(self.proof/('signup-'+name+'-observed.json'),{'independent_sql':True})
        self.command('browser-signup',['node',ROOT/'node_modules/@playwright/test/cli.js','test','--config',APP/'web/playwright.signup.config.cjs'],
            env={**self.environment,'SCRIBESWELL_SIGNUP_FIXTURE':str(self.proof/'signup-browser-private.json')},cwd=APP/'web',timeout=240,on_started=checkpoints)

def qualify():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id',required=True);parser.add_argument('--supabase',required=True,type=Path);parser.add_argument('--proof',required=True,type=Path)
    args=parser.parse_args()
    SignupQualification(args.run_id,args.supabase,args.proof).execute()
