"""Leave-only retained identity/member compatibility proof; root prepares all fixtures.

No infrastructure/Auth/bootstrap/reference changes. Business transitions use protected
commands; the sole owner mutation disables/restores one explicitly named authority.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
import os
from pathlib import Path
import stat
import sys
from uuid import UUID,uuid4
from sqlalchemy import text
from sqlalchemy.engine import make_url

sys.path.insert(0,str(Path(__file__).resolve().parent))
from qualify_person_links import Qualification,Journal,safe_diagnostic,APPROVED_RUN,APPROVED_PORT
from identity_native_guard import DATABASE_PREFIX


def uuid(value):
    if type(value) is not str or not UUID(value).int or str(UUID(value))!=value:raise ValueError('transition_fixture_uuid_invalid')
    return value


def decimal(value):
    if type(value) is not str or not value.isascii() or not value.isdecimal() or value.startswith('0') or len(value)>19 or int(value)>9223372036854775807:
        raise ValueError('transition_fixture_revision_invalid')
    return value


def load_fixture(path,run_id,port):
    if run_id!=APPROVED_RUN or type(port) is not int or port!=APPROVED_PORT:raise ValueError('transition_target_not_approved')
    path=Path(path).absolute()
    if path.is_symlink() or path.parent.is_symlink():raise ValueError('transition_fixture_invalid')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        info=os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode)!=0o600 or info.st_uid!=os.getuid() or info.st_size>65536:raise ValueError('transition_fixture_invalid')
        with os.fdopen(os.dup(fd),'rb') as stream:value=json.load(stream)
    finally:os.close(fd)
    required={'run_id','port','database','owner_url','operator_url','runtime_url','legacy_probe_url','org_ids','retained_accounts','replacement','receipt_authority_id'}
    if type(value) is not dict or set(value)!=required or value['run_id']!=run_id or value['port']!=port:raise ValueError('transition_fixture_invalid')
    if type(value['database']) is not str or not value['database'].startswith(DATABASE_PREFIX):raise ValueError('transition_fixture_database_invalid')
    for key,login in [('owner_url','identity_migrator'),('operator_url','identity_operator'),('runtime_url','access_runtime'),('legacy_probe_url','identity_legacy_probe_runtime')]:
        parsed=make_url(value[key])
        if (parsed.drivername,parsed.username,parsed.host,parsed.port,parsed.database,bool(parsed.query))!=('postgresql',login,'127.0.0.1',port,value['database'],False):raise ValueError('transition_fixture_target_invalid')
    if type(value['org_ids']) is not list or len(value['org_ids'])!=2 or len(set(map(uuid,value['org_ids'])))!=2:raise ValueError('transition_fixture_org_invalid')
    accounts=value['retained_accounts']
    if type(accounts) is not list or len(accounts)!=3:raise ValueError('transition_fixture_cohort_invalid')
    for account in accounts:
        if type(account) is not dict or set(account)!={'account_id','actor_id','person_id','membership_id'}:raise ValueError('transition_fixture_cohort_invalid')
        for name in ('account_id','actor_id','person_id'):uuid(account[name])
        decimal(account['membership_id'])
        if account['actor_id']!=account['account_id']:raise ValueError('transition_legacy_actor_not_preserved')
    if any(len({a[key] for a in accounts})!=3 for key in ('account_id','person_id','membership_id')):raise ValueError('transition_fixture_cohort_invalid')
    replacement=value['replacement']
    if type(replacement) is not dict or set(replacement)!={'account_id','actor_id','person_id'}:raise ValueError('transition_fixture_cohort_invalid')
    for item in replacement.values():uuid(item)
    if replacement['person_id']!=accounts[2]['person_id'] or replacement['account_id'] in {a['account_id'] for a in accounts} or replacement['actor_id'] in {a['actor_id'] for a in accounts}:raise ValueError('transition_replacement_binding_invalid')
    uuid(value['receipt_authority_id'])
    return value


class Transition(Qualification):
    def invoke(self,value,lookup=False,key='operator_url'):
        if value['command'] in ('person.create','account.link_person'):
            return super().invoke(value,lookup,key)
        reference=dict(stage='outcome' if lookup else 'execute',command=value['command'],operation_id=value['operation_id'],
            target=dict(org_id=value['scope']['org_id'],account_id=value['payload']['account_id']),credential_kind=key)
        self.record(status='attempting',**reference);db=self.engine(key)
        try:
            with db.connect() as connection:
                login=make_url(self.fixture[key]).username
                assert tuple(connection.execute(text('SELECT session_user,current_user')).one())==(login,login)
                connection.rollback()
                receipt=(__import__('identity_operator').outcome(connection,value['operation_id'],command=value['command'],
                    org_id=value['scope']['org_id'],account_id=value['payload']['account_id']) if lookup else
                    __import__('identity_operator').execute(connection,json.dumps(value,separators=(',',':')).encode()))
                self.record(status='committed' if receipt is not None else 'unresolved',**reference)
                return receipt
        except Exception as error:
            self.record(status='failed',diagnostic=safe_diagnostic(error),**reference);raise
        finally:db.dispose()
    def membership(self,command,account,org,**payload):
        return dict(schema_version=1,operation_id=str(uuid4()),command=command,scope=dict(kind='organization',org_id=org),
            payload=dict(account_id=account,**payload),reason_code='synthetic_fixture',evidence_ref='synthetic:identity-transition')
    def legacy(self,account,org,member):
        db=self.engine('legacy_probe_url')
        try:
            with db.begin() as connection:
                connection.execute(text('SET LOCAL ROLE authenticated'))
                claims=dict(sub=account,role='authenticated',org_id=org,member_id=member)
                connection.execute(text("SELECT set_config('request.jwt.claims',:claims,true)"),dict(claims=json.dumps(claims)))
                return [row[0] for row in connection.execute(text('SELECT role FROM public.get_user_roles()')).all()]
        finally:db.dispose()
    def hook(self,account,org):
        db=self.engine('legacy_probe_url')
        try:
            with db.begin() as connection:
                connection.execute(text('SET LOCAL ROLE supabase_auth_admin'))
                event=dict(user_id=account,user_metadata=dict(current_org_id=org),claims=dict(sub=account,role='authenticated'))
                return connection.execute(text('SELECT identity.custom_access_token_hook(CAST(:event AS jsonb))'),dict(event=json.dumps(event))).scalar_one()['claims']
        finally:db.dispose()
    def validate_probe(self):
        rows=self.sql("SELECT r.rolsuper,r.rolinherit,r.rolcreaterole,r.rolcreatedb,r.rolcanlogin,r.rolreplication,r.rolbypassrls FROM pg_roles r WHERE r.rolname='identity_legacy_probe_runtime'",key='legacy_probe_url')
        assert [tuple(row) for row in rows]==[(False,False,False,False,True,False,False)]
        rows=self.sql("SELECT pg_get_userbyid(roleid),admin_option,to_jsonb(m)->>'inherit_option',to_jsonb(m)->>'set_option' FROM pg_auth_members m WHERE member=(SELECT oid FROM pg_roles WHERE rolname='identity_legacy_probe_runtime') ORDER BY 1",key='legacy_probe_url')
        assert [tuple(row) for row in rows]==[('authenticated',False,'false','true'),('supabase_auth_admin',False,'false','true')]
    def revoke_receipt(self,link):
        authority=self.fixture['receipt_authority_id'];account=link['payload']['account_id']
        rows=self.sql("SELECT database_login::text,command,scope_kind,org_id,target_account_id::text,enabled FROM identity.operator_authorities WHERE id=CAST(:id AS uuid)",dict(id=authority))
        assert [tuple(row) for row in rows]==[('identity_operator','account.link_person','platform',None,account,True)]
        self.record(stage='authority-revoke',status='attempting',authority_id=authority,operation_id=link['operation_id'])
        try:
            self.sql('UPDATE identity.operator_authorities SET enabled=false WHERE id=CAST(:id AS uuid)',dict(id=authority))
            before=self.state()
            self.denied(link,code='access_denied')
            self.denied(link,lookup=True,code='access_denied')
            assert self.state()==before
            self.record(stage='authority-revoke',status='denial-confirmed',authority_id=authority)
        finally:
            self.sql('UPDATE identity.operator_authorities SET enabled=true WHERE id=CAST(:id AS uuid)',dict(id=authority))
            self.record(stage='authority-restore',status='restored',authority_id=authority)
        assert self.invoke(link,lookup=True).result.target.account_id==account
    def run(self):
        self.validate_probe();accounts=self.fixture['retained_accounts'];org,other=self.fixture['org_ids']
        ids=[a['account_id'] for a in accounts]+[self.fixture['replacement']['account_id']]
        actors=self.sql('SELECT id::text,kind,actor_key,created_by::text,created_at FROM identity.actor WHERE id=ANY(CAST(:ids AS uuid[])) ORDER BY id',dict(ids=[a['actor_id'] for a in accounts]+[self.fixture['replacement']['actor_id']]))
        roles=self.sql('SELECT r.id,r.member_id,r.role::text,r.deleted_at FROM identity.member_role r WHERE r.member_id=ANY(CAST(:ids AS bigint[])) ORDER BY r.id',dict(ids=[a['membership_id'] for a in accounts]))
        assert len(actors)==4 and len(roles)>=3
        links=[]
        for account in accounts:
            person=self.value(account['person_id']);first=self.invoke(person);assert first.result.disposition=='created'
            assert self.invoke(person,lookup=True)==first and self.invoke(person)==first
            link=self.value(account['person_id'],{k:account[k] for k in ('account_id','actor_id')})
            first=self.invoke(link);assert first.result.disposition=='created';assert self.invoke(link,lookup=True)==first
            links.append(link)
        replacement=self.fixture['replacement'];link=self.value(replacement['person_id'],{k:replacement[k] for k in ('account_id','actor_id')})
        assert self.invoke(link).result.target.actor_id==replacement['actor_id']
        from qualify_person_links import assert_projection
        for account in accounts+[replacement]:
            assert_projection(self.projection(account['account_id']),account['account_id'],account['actor_id'],account['person_id'],1)
        self.checks.append('three-independent-retained-people-and-explicit-replacement-link-distinct-actors')
        for account in accounts:
            aid,mid=account['account_id'],account['membership_id']
            original=self.sql('SELECT id,user_id::text,org_id::text,created_at,created_actor_id::text,revision FROM identity.org_member WHERE id=CAST(:id AS bigint)',dict(id=mid))[0]
            assert original[1:3]==(aid,org) and original[5]==1
            expected_roles=[row[0] for row in self.sql('SELECT role::text FROM identity.member_role WHERE member_id=CAST(:id AS bigint) AND deleted_at IS NULL',dict(id=mid))]
            assert expected_roles and sorted(self.legacy(aid,org,mid))==sorted(expected_roles)
            assert self.legacy(replacement['account_id'],org,mid)==[]
            retirement=self.membership('membership.retire',aid,org,membership_id=mid,expected_revision='1')
            retired=self.invoke(retirement);assert self.invoke(retirement,lookup=True)==retired
            assert self.legacy(aid,org,mid)==[]
            claims=self.hook(aid,org);assert claims['member_id'] is None and claims['user_roles']==[] and org not in claims['org_ids']
            rejoin=self.membership('membership.join',aid,org,expected_previous_membership_id=mid)
            joined=self.invoke(rejoin);new=joined.result.target.membership_id
            assert new!=mid and self.invoke(rejoin,lookup=True)==joined
            stale=deepcopy(rejoin);stale['operation_id']=str(uuid4());self.denied(stale,code='operation_conflict')
            changed=deepcopy(rejoin);changed['payload']['expected_previous_membership_id']=None;self.denied(changed,code='operation_conflict')
            retire_new=self.membership('membership.retire',aid,org,membership_id=new,expected_revision='1');self.invoke(retire_new)
            later=self.membership('membership.join',aid,org,expected_previous_membership_id=new);latest=self.invoke(later)
            assert self.invoke(rejoin)==joined and self.invoke(retirement)==retired
            active=self.sql('SELECT id::text FROM identity.org_member WHERE user_id=CAST(:account AS uuid) AND org_id=CAST(:org AS uuid) AND deleted_at IS NULL',dict(account=aid,org=org))
            assert active==[(latest.result.target.membership_id,)]
            assert self.legacy(aid,org,mid)==[] and self.legacy(aid,org,latest.result.target.membership_id)==[]
            claims=self.hook(aid,org);assert str(claims['member_id'])==latest.result.target.membership_id and claims['user_roles']==[]
            retained=self.sql('SELECT id,user_id::text,org_id::text,created_at,created_actor_id::text,revision FROM identity.org_member WHERE id=CAST(:id AS bigint)',dict(id=mid))[0]
            assert retained[:5]==original[:5] and retained[5]==2
        self.checks.append('retire-rejoin-retained-history-old-role-hook-denial-and-delayed-command-replay')
        race=self.membership('membership.join',accounts[0]['account_id'],other,expected_previous_membership_id=None)
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda _:self.invoke(race),range(2)))
        assert results[0]==results[1]
        rows=self.sql("SELECT o.id::text,o.command_type,o.operation_id::text,o.result,e.event_id::text,e.outcome_id::text,e.target,e.event_type FROM identity.operation_outcome o LEFT JOIN identity.business_event e ON e.outcome_id=o.id WHERE o.operation_id=CAST(:operation AS uuid) AND o.command_type='membership.join'",dict(operation=race['operation_id']))
        assert len(rows)==1
        oid,command,operation,result,event,event_outcome,target,event_type=rows[0]
        from dataclasses import asdict
        expected=asdict(results[0].result);expected.pop('command')
        assert command=='membership.join' and operation==race['operation_id'] and result==expected and event==results[0].result.event_id and event_outcome==oid and target==expected['target'] and event_type=='identity.membership_joined'
        assert self.sql('SELECT count(*) FROM identity.org_member WHERE org_id=CAST(:org AS uuid) AND user_id=CAST(:account AS uuid) AND deleted_at IS NULL',dict(org=other,account=accounts[0]['account_id']))==[(1,)]
        self.checks.append('concurrent-second-organization-join-one-active-membership')
        self.revoke_receipt(links[0]);self.checks.append('current-authority-revoke-outcome-denial-and-explicit-restoration')
        assert actors==self.sql('SELECT id::text,kind,actor_key,created_by::text,created_at FROM identity.actor WHERE id=ANY(CAST(:ids AS uuid[])) ORDER BY id',dict(ids=[a['actor_id'] for a in accounts]+[replacement['actor_id']]))
        assert roles==self.sql('SELECT r.id,r.member_id,r.role::text,r.deleted_at FROM identity.member_role r WHERE r.member_id=ANY(CAST(:ids AS bigint[])) ORDER BY r.id',dict(ids=[a['membership_id'] for a in accounts]))
        assert self.sql('SELECT count(*) FROM identity.users WHERE id=ANY(CAST(:ids AS uuid[]))',dict(ids=ids))==[(4,)]
        assert self.sql('SELECT count(*) FROM identity.member_role WHERE member_id IN (SELECT id FROM identity.org_member WHERE user_id=CAST(:account AS uuid))',dict(account=replacement['account_id']))==[(0,)]
        self.checks.append('retained-account-actor-role-and-profile-identifiers-preserved-no-replacement-access-inheritance')
        return dict(status='passed',run_id=APPROVED_RUN,database=self.fixture['database'],checks=self.checks,
            activation_gate='Access permission consumers and later People/Leave integration remain unqualified and gated',
            limits=['Root separately proves pre-adoption bootstrap and release failure/retry; provider deletion is not performed or inferred.',
                    'No Access/PtS grant effectiveness or production qualification is inferred.'])


def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('--fixture',required=True);parser.add_argument('--run-id',required=True)
    parser.add_argument('--port',required=True,type=int);parser.add_argument('--output',required=True);args=parser.parse_args(argv)
    journal=None
    try:
        if not __debug__:raise ValueError('transition_optimized_python_prohibited')
        fixture=load_fixture(args.fixture,args.run_id,args.port);output=Path(args.output)
        if output.exists():raise ValueError('transition_output_exists')
        journal=Journal(str(output)+'.attempts.jsonl');result=Transition(fixture,journal).run()
        fd=os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'w') as stream:json.dump(result,stream,sort_keys=True,indent=2);stream.write('\n')
    except Exception as error:
        diagnostic=safe_diagnostic(error)
        if journal is not None:journal(dict(stage='transition',status='failed',diagnostic=diagnostic))
        print(json.dumps(dict(status='failed',code='identity_transition_requires_reconciliation',diagnostic=diagnostic)));return 2
    finally:
        if journal is not None:journal.close()
    print(json.dumps(dict(status='passed',checks=len(result['checks']))));return 0

if __name__=='__main__':raise SystemExit(main())
