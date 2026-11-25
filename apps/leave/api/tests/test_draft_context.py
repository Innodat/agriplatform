"""E1-CONTEXT AC01–05: preparation observations confer no draft write authority."""
import asyncio,sys
from pathlib import Path
import json
from uuid import uuid4
from datetime import datetime,timedelta,timezone
import httpx,pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from main import create_app
from access_client import AccessClient,Failure
from transaction_context import Budget

ORG,PERSON,EMPLOYEE,ACCOUNT,ACTOR=[str(uuid4()) for _ in range(5)]
NOW=datetime(2026,11,7,23,30,tzinfo=timezone.utc)
class Access:
    def __init__(self):self.calls=[];self.manage=True;self.error=None
    async def own(self,authorization,org,budget):
        self.calls.append(org)
        if self.error:raise Failure(*self.error)
        from access_client import OwnDecision,OwnContext
        d=OwnDecision(account_id=ACCOUNT,actor_id=ACTOR,person_id=PERSON,permission='leave.request.own.read',authorization_scope={'kind':'organization','org_id':org},resource_scope={'kind':'own','person_id':PERSON},membership_id='19',decision_id=str(uuid4()),checked_at=NOW.isoformat())
        return OwnContext(d,self.manage)
class People:
    def __init__(self):self.calls=[];self.has_periods=True;self.state='current';self.missing=False;self.error=None
    async def read(self,authorization,org,person,budget,employment=None,as_of=None):
        self.calls.append(as_of)
        if self.error:raise Failure(*self.error)
        base=dict(org_id=org,person_id=person,observed_at=NOW.isoformat())
        if self.missing:return dict(status='not_found',**base)
        base.update(employment_id=EMPLOYEE,revision='2')
        if as_of is None:return dict(status='found',has_periods=self.has_periods,**base)
        return dict(status='effective',as_of_date=as_of,employment_state=self.state,period=None if self.state=='setup_required' else dict(period_id=str(uuid4()),start_date='2026-01-01' if self.state!='future' else '2028-01-01',end_date='2026-01-02' if self.state=='ended' else None),**base)
class Config:
    def __init__(self):self.calls=[];self.zone='Africa/Johannesburg';self.notice=None
    async def timezone(self,context,employment,budget,now):
        self.calls.append((context,employment,now))
        from work_timezone import TimezoneObservation
        return TimezoneObservation(self.zone,self.notice,{})
def request(access=None,people=None,config=None):
    async def run():
        app=create_app(repository=object(),access=access or Access(),environment={},people=people or People(),configuration=config or Config(),clock=lambda:NOW)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://leave') as client:return await client.get(f'/v1/organizations/{ORG}/me/draft-context',headers={'Authorization':'Bearer synthetic'})
    return asyncio.run(run())

@pytest.mark.parametrize('state,expected',[('current',{'status':'editable'}),('future',{'status':'editable'}),('ended',{'status':'read_only','reason':'employment_ended'})])
def test_context_current_future_ended_and_server_business_date(state,expected):
    people=People();people.state=state;r=request(people=people)
    assert r.status_code==200 and r.json()==dict(status='ready',org_id=ORG,employment_id=EMPLOYEE,editability=expected,setup_notices=[])
    assert people.calls==[None,'2026-11-08']
    assert r.headers['cache-control']=='private, no-store'
    assert 'active_draft' not in r.json() and 'scope_generation' not in r.json()

@pytest.mark.parametrize('notice',['work_timezone_missing','work_timezone_invalid'])
def test_undated_setup_is_nonblocking_and_never_implies_ended(notice):
    config=Config();config.zone=None;config.notice=notice;people=People();people.state='ended';r=request(people=people,config=config)
    assert r.status_code==200 and r.json()['editability']=={'status':'editable'}
    assert r.json()['setup_notices']==[{'code':notice}] and people.calls==[None]

def test_permission_restriction_precedes_config_and_period_reasons():
    access=Access();access.manage=False;people=People();people.has_periods=False;config=Config();r=request(access,people,config)
    assert r.json()['editability']=={'status':'read_only','reason':'permission_missing'} and not config.calls and people.calls==[None]

def test_no_periods_remains_readable_and_no_employment_is_distinct():
    people=People();people.has_periods=False;config=Config();r=request(people=people,config=config)
    assert r.json()['editability']=={'status':'read_only','reason':'employment_periods_missing'} and not config.calls
    people.missing=True;r=request(people=people)
    assert r.json()==dict(status='setup_required',org_id=ORG,reason='employment_missing')

@pytest.mark.parametrize('name,reason',[('identity.person_link_required','identity_person_link_required'),('identity.actor_setup_required','identity_actor_setup_required')])
def test_identity_setup_discloses_no_employment_or_configuration(name,reason):
    access=Access();access.error=(409,name);people=People();config=Config();r=request(access,people,config)
    assert r.json()==dict(status='setup_required',org_id=ORG,reason=reason) and not people.calls and not config.calls

@pytest.mark.parametrize('status,name',[(403,'access_denied'),(503,'authorization_unavailable')])
def test_read_denial_and_outage_are_errors_without_scope_disclosure(status,name):
    access=Access();access.error=(status,name);people=People();config=Config();r=request(access,people,config)
    assert r.status_code==status and r.json()['error_id']==name and not people.calls and not config.calls

def test_people_outage_never_becomes_missing_setup():
    people=People();people.error=(503,'dependency_unavailable');r=request(people=people)
    assert r.status_code==503 and r.json()['error_id']=='dependency_unavailable'

@pytest.mark.parametrize('field',['org_id','person_id','employment_id','as_of_date','period','revision','extra','status','has_periods'])
def test_people_adapter_rejects_wrong_identity_date_shape_and_state(field):
    from people_client import PeopleClient
    from transaction_context import Budget
    async def execute():
        p=People();value=await p.read('x',ORG,PERSON,None,EMPLOYEE,'2026-11-08')
        if field in ('org_id','person_id','employment_id'):value[field]=str(uuid4())
        elif field=='as_of_date':value[field]='2026-11-07'
        elif field=='period':value['period']['start_date']='2028-01-01'
        elif field=='revision':value[field]='9223372036854775808'
        elif field=='status':value[field]='found'
        else:value[field]=True
        client=PeopleClient('http://localhost:8192','k'*40,transport=httpx.MockTransport(lambda r:httpx.Response(200,json=value)))
        with pytest.raises(Failure) as error:await client.read('Bearer x',ORG,PERSON,Budget(),EMPLOYEE,'2026-11-08')
        assert error.value.error_id=='dependency_unavailable'
    asyncio.run(execute())

@pytest.mark.parametrize('content',[b'{"status":"found","status":"not_found"}',b'[]',b'x'*65537,b'{"status":NaN}'])
def test_people_adapter_rejects_duplicate_malformed_and_oversized_content(content):
    from people_client import PeopleClient
    from transaction_context import Budget
    async def execute():
        client=PeopleClient('http://localhost:8192','k'*40,transport=httpx.MockTransport(lambda r:httpx.Response(200,content=content)))
        with pytest.raises(Failure):await client.read('Bearer x',ORG,PERSON,Budget())
    asyncio.run(execute())

def test_total_context_deadline_cancels_dependency_without_partial_success(monkeypatch):
    from transaction_context import Budget
    import main
    class ShortBudget(Budget):
        def __init__(self):super().__init__();self.deadline=self.started_at+.03
    class SlowPeople(People):
        async def read(self,*args):await asyncio.sleep(1)
    monkeypatch.setattr(main,'Budget',ShortBudget)
    r=request(people=SlowPeople());assert r.status_code==503 and r.json()['error_id']=='dependency_unavailable'

def chain():
    profile=str(uuid4());return dict(settings=dict(org_id=ORG,default_profile_id=profile,revision=1),assignment=None,profile=dict(org_id=ORG,id=profile,archived_at=None),version=dict(org_id=ORG,profile_id=profile,effective_from='2026-01-01T00:00:00+00:00',effective_until=None,work_timezone='Africa/Johannesburg'))
def test_timezone_explicit_default_override_and_retained_utc_boundaries():
    from work_timezone import resolve
    row=chain();assert resolve(row,ORG,EMPLOYEE,NOW).zone=='Africa/Johannesburg'
    explicit=str(uuid4());row['assignment']=dict(org_id=ORG,employment_id=EMPLOYEE,profile_id=explicit,timezone_override='Pacific/Honolulu',effective_from='2026-01-01T00:00:00Z',effective_until=None)
    row['profile']['id']=explicit;row['version']['profile_id']=explicit
    assert resolve(row,ORG,EMPLOYEE,NOW).zone=='Pacific/Honolulu'
    row['assignment']['timezone_override']='broken/no-such-zone';assert resolve(row,ORG,EMPLOYEE,NOW).notice=='work_timezone_invalid'
    row['assignment']['timezone_override']=None;row['version']['effective_until']=NOW.isoformat();assert resolve(row,ORG,EMPLOYEE,NOW).notice=='work_timezone_invalid'

@pytest.mark.parametrize('broken',['cross_org','archived','missing_explicit','invalid_override','missing_default','missing_version'])
def test_broken_configuration_never_silently_falls_back(broken):
    from work_timezone import resolve
    row=chain()
    if broken=='cross_org':row['profile']['org_id']=str(uuid4())
    elif broken=='archived':row['profile']['archived_at']=NOW.isoformat()
    elif broken=='missing_explicit':row['assignment']=dict(org_id=ORG,employment_id=EMPLOYEE,profile_id=str(uuid4()),timezone_override=None)
    elif broken=='invalid_override':row['assignment']=dict(org_id=ORG,employment_id=EMPLOYEE,profile_id=None,timezone_override='broken/no-such-zone',effective_from='2026-01-01T00:00:00Z',effective_until=None)
    elif broken=='missing_default':row['settings']['default_profile_id']=None
    else:row['version']=None
    assert resolve(row,ORG,EMPLOYEE,NOW).notice==('work_timezone_missing' if broken in ('missing_default','missing_version') else 'work_timezone_invalid')

@pytest.mark.parametrize('zone',['localtime','posixrules'])
def test_host_timezone_files_are_not_named_work_timezones(zone):
    from work_timezone import resolve
    row=chain();row['version']['work_timezone']=zone
    assert resolve(row,ORG,EMPLOYEE,NOW).notice=='work_timezone_invalid'

def test_context_openapi_requires_every_variant_discriminator():
    schemas=create_app(environment={}).openapi()['components']['schemas']
    for name in ('Ready','Setup','Editable','ReadOnly'):
        assert 'status' in schemas[name].get('required',[]),name


SESSION = '/v2/identity/current-session'
COMBINED = '/v2/organizations/leave-own-context'
SINGLE = '/v2/check'


class AccessWire:
    def __init__(self, manage=True, status=200, error_id=None, alter=None):
        self.manage = manage
        self.status = status
        self.error_id = error_id
        self.alter = alter
        self.calls = []
        self.client = AccessClient('http://localhost:8191', 's'*40, 'c'*40, 'p'*40,
                                   transport=httpx.MockTransport(self.handle))

    async def handle(self, message):
        path = message.url.path
        self.calls.append(path)
        assert message.method == 'POST' and message.headers['Authorization'] == 'Bearer synthetic'
        if path == SESSION:
            assert message.headers['X-Service-Key'] == 'c'*40
            expiry = datetime.now(timezone.utc)+timedelta(hours=1)
            return httpx.Response(200, json={'account_id': ACCOUNT, 'session_id': str(uuid4()),
                'credential_expires_at': expiry.isoformat(), 'observed_at': NOW.isoformat()})
        assert message.headers['X-Service-Key'] == 's'*40
        read = (await Access().own('x', ORG, None)).decision.model_dump()
        if path == SINGLE:
            assert json.loads(message.content) == {'permission': 'leave.request.own.read',
                                                  'authorization_scope': {'kind': 'organization', 'org_id': ORG}}
            return httpx.Response(200, json=read)
        assert path == COMBINED and json.loads(message.content) == {'org_id': ORG}
        if self.status != 200:
            return httpx.Response(self.status, json={'error_id': self.error_id, 'error': 'safe', 'details': {}})
        manage = {**read, 'permission': 'leave.request.own.manage', 'decision_id': str(uuid4())}
        value = {'read': read, 'manage': manage if self.manage else None}
        if self.alter:
            self.alter(value)
        return httpx.Response(200, json=value)


@pytest.mark.parametrize('manage', [True, False])
def test_preparation_uses_session_then_one_combined_decision_before_people(manage):
    wire = AccessWire(manage)

    class OrderedPeople(People):
        async def read(self, *args):
            assert wire.calls == [SESSION, COMBINED]
            return await super().read(*args)

    people, config = OrderedPeople(), Config()
    response = request(wire.client, people, config)
    assert response.status_code == 200
    assert wire.calls == [SESSION, COMBINED]
    assert response.json()['editability'] == ({'status': 'editable'} if manage else
                                              {'status': 'read_only', 'reason': 'permission_missing'})
    assert people.calls == ([None, '2026-11-08'] if manage else [None])
    assert bool(config.calls) == manage


@pytest.mark.parametrize('status,owner_error,leave_status,leave_error', [
    (403, 'access_denied', 403, 'access_denied'),
    (503, 'authorization_unavailable', 503, 'authorization_unavailable'),
    (403, 'service_access_denied', 503, 'dependency_unavailable'),
])
def test_combined_failure_stops_before_people_and_protected_data(status, owner_error, leave_status, leave_error):
    wire, people, config = AccessWire(status=status, error_id=owner_error), People(), Config()
    response = request(wire.client, people, config)
    assert (response.status_code, response.json()['error_id']) == (leave_status, leave_error)
    assert wire.calls == [SESSION, COMBINED]
    assert not people.calls and not config.calls and 'employment_id' not in response.text


@pytest.mark.parametrize('which,field,value', [
    ('read', 'account_id', str(uuid4())),
    ('read', 'permission', 'leave.request.own.manage'),
    ('manage', 'account_id', str(uuid4())),
    ('manage', 'actor_id', str(uuid4())),
    ('manage', 'person_id', str(uuid4())),
    ('manage', 'membership_id', '20'),
    ('manage', 'authorization_scope', {'kind': 'organization', 'org_id': str(uuid4())}),
    ('manage', 'resource_scope', {'kind': 'own', 'person_id': str(uuid4())}),
    ('manage', 'permission', 'leave.request.own.read'),
])
def test_wrong_nested_binding_never_reaches_people(which, field, value):
    wire = AccessWire(alter=lambda body: body[which].update({field: value}))
    people, config = People(), Config()
    response = request(wire.client, people, config)
    assert (response.status_code, response.json()['error_id']) == (503, 'authorization_unavailable')
    assert wire.calls == [SESSION, COMBINED] and not people.calls and not config.calls


@pytest.mark.parametrize('alter', [
    lambda body: body.pop('manage'),
    lambda body: body.update(read=None),
    lambda body: body.update(manage={}),
    lambda body: body.update(extra=True),
])
def test_combined_requires_closed_shape_and_explicit_nullable_manage(alter):
    wire, people = AccessWire(alter=alter), People()
    response = request(wire.client, people)
    assert (response.status_code, response.json()['error_id']) == (503, 'authorization_unavailable')
    assert wire.calls == [SESSION, COMBINED] and not people.calls


def test_choices_read_path_still_uses_current_session_and_single_read():
    wire = AccessWire()
    context = asyncio.run(wire.client.own_read('Bearer synthetic', ORG, Budget()))
    assert context.decision.permission == 'leave.request.own.read' and context.manage_decision is None
    assert wire.calls == [SESSION, SINGLE]

requires_composed_opening = pytest.mark.skipif(
    '/v1/organizations/{org_id}/drafts/{draft_id}/editor' not in create_app(environment={}).openapi()['paths'],
    reason='Composed editor opening is an optional scaffold profile',
)

@requires_composed_opening
@pytest.mark.parametrize('status,error_id,manage', [
    (200, None, False), (403, 'access_denied', False), (503, 'authorization_unavailable', False),
])
def test_editor_open_uses_combined_authority_before_protected_reads(status, error_id, manage):
    from test_editor_opening import Store, Choices, request as open_request
    wire = AccessWire(manage, status, error_id)
    store, people, choices = Store(), People(), Choices()
    response = open_request(store=store, choices=choices, access=wire.client, people=people)
    assert response.status_code == status and wire.calls == [SESSION, COMBINED]
    if status == 200:
        assert response.json()['draft']['editability'] == {'status': 'read_only', 'reason': 'permission_missing'}
        assert people.calls == [None] and len(store.calls) == len(choices.calls) == 1
    else:
        assert response.json()['error_id'] == error_id
        assert not store.calls and not people.calls and not choices.calls


OTHER_PERSON = str(uuid4())


@requires_composed_opening
@pytest.mark.parametrize('manage,alter', [
    (False, lambda body: body['read'].update(account_id=str(uuid4()))),
    (False, lambda body: body['read'].update(authorization_scope={
        'kind': 'organization', 'org_id': str(uuid4()),
    })),
    (True, lambda body: body['manage'].update(
        person_id=OTHER_PERSON, resource_scope={'kind': 'own', 'person_id': OTHER_PERSON},
    )),
    (True, lambda body: body['manage'].update(decision_id=body['read']['decision_id'])),
    (False, lambda body: body['read'].update(checked_at='2026-11-07\x0023:30:00Z')),
    (True, lambda body: body['manage'].update(checked_at='2026-11-07 23:30:00Z')),
], ids=['read-only-account', 'read-only-organization', 'different-people',
        'duplicate-decision-id', 'read-timestamp', 'manage-timestamp'])
def test_editor_open_rejects_malformed_or_mismatched_combined_authority(manage, alter):
    from test_editor_opening import Store, Choices, request as open_request
    wire = AccessWire(manage, alter=alter)
    store, people, choices = Store(), People(), Choices()
    response = open_request(store=store, choices=choices, access=wire.client, people=people)
    assert response.status_code == 503
    assert response.json()['error_id'] == 'authorization_unavailable'
    assert wire.calls == [SESSION, COMBINED]
    assert not store.calls and not people.calls and not choices.calls


@requires_composed_opening
def test_save_and_reopen_prepare_current_authority_and_read_committed_input():
    from drafts import SaveCommitted, SaveResult, empty_input, evidence
    from test_editor_opening import Store, Choices, DRAFT, TYPE
    wire_decisions = []
    wire = AccessWire(alter=wire_decisions.append)
    decisions = []
    save_evidence = []

    class SavedStore(Store):
        async def save(self, prepared, budget, draft, command, configuration, clock):
            decisions.append(prepared.authority.manage_decision)
            save_evidence.append(evidence(prepared))
            self.saved = command.input
            return SaveCommitted(operation_id=command.operation_id, status='committed',
                result=SaveResult(command='save', draft_id=draft, revision='8', scope_generation='3', disposition='saved'))

        async def editor(self, prepared, budget, draft):
            decisions.append(prepared.authority.decision)
            result, summary = await super().editor(prepared, budget, draft)
            result = result.model_copy(update={'input': self.saved, 'revision': '8'})
            return result, {**summary, 'active_draft': {'draft_id': draft, 'revision': '8'}}

    async def run():
        store = SavedStore()
        app = create_app(repository=object(), access=wire.client, environment={}, people=People(),
            configuration=Config(), clock=lambda:NOW, drafts=store, choices=Choices())
        root = f'/v1/organizations/{ORG}/drafts/{DRAFT}'
        content = {**empty_input(), 'leave_type_id': TYPE, 'note': 'exact saved input'}
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://leave',
                                     headers={'Authorization': 'Bearer synthetic'}) as client:
            saved = await client.put(root+'/input', json={'input': content, 'operation_id': str(uuid4()), 'expected_revision': '7'})
            assert saved.status_code == 200 and saved.json()['result']['revision'] == '8'
            wire.manage = False
            opened = await client.get(root+'/editor')
            assert opened.status_code == 200
            assert opened.json()['draft']['input'] == content
            assert opened.json()['draft']['editability'] == {'status': 'read_only', 'reason': 'permission_missing'}

    asyncio.run(run())
    assert wire.calls == [SESSION, COMBINED, SESSION, COMBINED]
    assert [decision.permission for decision in decisions] == ['leave.request.own.manage', 'leave.request.own.read']
    assert save_evidence[0]['decision_id'] == wire_decisions[0]['manage']['decision_id']
    assert save_evidence[0]['decision_id'] != wire_decisions[0]['read']['decision_id']


def test_save_restarted_preparation_rechecks_session_and_combined_before_store():
    from drafts import DraftFailure
    from test_draft_input import request as save_request
    wire = AccessWire()

    class RetryStore:
        def __init__(self):
            self.calls = 0

        async def save(self, *args):
            self.calls += 1
            wire.status, wire.error_id = 403, 'access_denied'
            raise DraftFailure(409, 'leave.draft_preparation_changed')

    store = RetryStore()
    response = save_request(store=store, access=wire.client)
    assert (response.status_code, response.json()['error_id']) == (403, 'access_denied')
    assert wire.calls == [SESSION, COMBINED, SESSION, COMBINED]
    assert store.calls == 1
