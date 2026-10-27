"""Own-account language HTTP contract; PostgreSQL effects are qualified separately."""
import sys
from pathlib import Path
from uuid import UUID
from contextlib import asynccontextmanager
import pytest
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from main import create_app

ACCOUNT=UUID('11111111-1111-4111-8111-111111111111')
HEADERS={'Authorization':'Bearer synthetic','X-Service-Key':'synthetic-preferences-key'}
BODY={'operation_id':'22222222-2222-4222-8222-222222222222','expected_revision':'0','preferred_locale':'pt'}

class Rows:
    def __init__(self,row):self.row=row
    def mappings(self):return self
    def one_or_none(self):return self.row

class Database:
    def __init__(self,row=None,fail_commit=False):
        self.row=row or {'preferred_locale':'pt','revision':1};self.calls=[];self.fail_commit=fail_commit;self.committed=False
    @asynccontextmanager
    async def begin(self,deadline):
        yield self
        if self.fail_commit:raise OSError('synthetic-sensitive-commit-details')
        self.committed=True
    async def execute(self,statement,parameters=None):
        self.calls.append((str(statement),parameters))
        return Rows(self.row)

def client(monkeypatch,db=None,account=ACCOUNT):
    monkeypatch.setenv('IDENTITY_PREFERENCES_SERVICE_KEY',HEADERS['X-Service-Key'])
    return TestClient(create_app(db=object(),authenticate=lambda token:account,preferences_db=db))

def test_read_is_bound_to_verified_account_and_private(monkeypatch):
    db=Database();c=client(monkeypatch,db);r=c.get('/v2/me/preferences/language',headers=HEADERS)
    assert r.status_code==200 and r.json()=={'preferred_locale':'pt','revision':'1'}
    assert r.headers['cache-control']=='private, no-store'
    assert any(params and params.get('account')==str(ACCOUNT) for _,params in db.calls)
    assert db.committed

def test_write_accepts_desired_portuguese_without_org_or_person(monkeypatch):
    db=Database();r=client(monkeypatch,db).put('/v2/me/preferences/language',headers=HEADERS,json=BODY)
    assert r.status_code==200 and r.json()['preferred_locale']=='pt'
    assert any('set_account_language' in sql for sql,_ in db.calls)
    assert db.committed

@pytest.mark.parametrize('patch',[{'account_id':str(ACCOUNT)},{'org_id':str(ACCOUNT)},{'preferred_locale':'pt-BR'},{'preferred_locale':'PT'},{'expected_revision':0},{'expected_revision':'01'},{'expected_revision':'9223372036854775808'},{'operation_id':'00000000-0000-0000-0000-000000000000'}])
def test_closed_write_contract_rejects_overrides_and_invalid_values(monkeypatch,patch):
    db=Database();r=client(monkeypatch,db).put('/v2/me/preferences/language',headers=HEADERS,json={**BODY,**patch})
    assert r.status_code==422 and r.json()=={'detail':{'code':'identity.preference_invalid'}}
    assert not db.calls

def test_commit_failure_never_acknowledges_or_reports_absence(monkeypatch):
    r=client(monkeypatch,Database(fail_commit=True)).put('/v2/me/preferences/language',headers=HEADERS,json=BODY)
    assert r.status_code==503 and r.json()=={'detail':{'code':'identity.preference_unavailable'}}
    assert 'sensitive' not in r.text

def test_missing_database_is_unavailable(monkeypatch):
    r=client(monkeypatch).get('/v2/me/preferences/language',headers=HEADERS)
    assert r.status_code==503 and 'preferred_locale' not in r.json()

@pytest.mark.parametrize('headers',[{}, {'Authorization':'Bearer synthetic'},{**HEADERS,'X-Service-Key':'wrong'}])
def test_service_and_user_context_are_required(monkeypatch,headers):
    db=Database();r=client(monkeypatch,db).get('/v2/me/preferences/language',headers=headers)
    assert r.status_code in (401,403) and not db.calls

def test_duplicate_and_oversize_payloads_fail_safely(monkeypatch):
    db=Database();c=client(monkeypatch,db)
    for body in ('{"preferred_locale":"en","preferred_locale":"pt"}', 'x'*2049):
        r=c.put('/v2/me/preferences/language',headers=HEADERS,content=body)
        assert r.status_code==422 and 'x'*20 not in r.text
    assert not db.calls

def test_malformed_database_result_is_unavailable(monkeypatch):
    r=client(monkeypatch,Database({'preferred_locale':'secret-value','revision':1})).get('/v2/me/preferences/language',headers=HEADERS)
    assert r.status_code==503 and 'secret-value' not in r.text

def test_openapi_requires_both_credentials_and_declares_wire_types(monkeypatch):
    schema=client(monkeypatch).get('/openapi.json').json()
    for method in ('get','put'):
        operation=schema['paths']['/v2/me/preferences/language'][method]
        assert operation['security']==[{'IdentityPreferenceBearer':[],'IdentityPreferenceServiceKey':[]}]
        assert operation['responses']['200']['content']['application/json']['schema']['$ref'].endswith('/LanguagePreference')
    body=schema['paths']['/v2/me/preferences/language']['put']['requestBody']['content']['application/json']['schema']
    assert body['additionalProperties'] is False and body['properties']['preferred_locale']['enum']==['en','pt']


def test_openapi_declares_stable_preference_error_contract(monkeypatch):
    schema=client(monkeypatch).get('/openapi.json').json()
    codes={'authentication_required','access_denied','identity.actor_setup_required',
        'identity.preference_revision_conflict','identity.preference_operation_conflict',
        'identity.preference_invalid','identity.preference_unavailable'}
    details=schema['components']['schemas']['PreferenceErrorDetails']
    assert set(details['properties']['code']['enum'])==codes
    for method in ('get','put'):
        for status in ('401','403','409','422','503'):
            ref=schema['paths']['/v2/me/preferences/language'][method]['responses'][status]['content']['application/json']['schema']['$ref']
            assert ref.endswith('/PreferenceErrorResponse')

@pytest.mark.parametrize('state,status,code',[
    ('IP001',409,'identity.preference_revision_conflict'),
    ('IP002',409,'identity.preference_operation_conflict'),
    ('IP003',409,'identity.actor_setup_required'),
    ('IP004',422,'identity.preference_invalid'),
    ('42501',403,'access_denied'),
    ('08006',503,'identity.preference_unavailable')])
def test_database_failures_use_typed_safe_error_codes(monkeypatch,state,status,code):
    from sqlalchemy.exc import DBAPIError
    class DriverError(Exception):sqlstate=state
    class Failed(Database):
        async def execute(self,*args,**kwargs):raise DBAPIError('PRIVATE SQL',{'private':'value'},DriverError('PRIVATE DATABASE CONTENT'))
    r=client(monkeypatch,Failed()).put('/v2/me/preferences/language',headers=HEADERS,json=BODY)
    assert r.status_code==status and r.json()=={'detail':{'code':code}}
    assert 'PRIVATE' not in r.text
