import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime,timezone,timedelta
import httpx
from jose import jwt
import pytest

PATH=Path(__file__).resolve().parents[3]/'platform/builder-cli/templates/backend/auth/jwt_optional.py'
@pytest.fixture
def verifier(monkeypatch):
 monkeypatch.setitem(sys.modules,'config',SimpleNamespace(settings=SimpleNamespace(supabase_jwt_secret='local-test-secret',supabase_url='http://127.0.0.1:54321',supabase_anon_key='test-public-key')))
 monkeypatch.setenv('SUPABASE_URL','http://127.0.0.1:54321')
 monkeypatch.setenv('SUPABASE_ANON_KEY','test-public-key')
 spec=importlib.util.spec_from_file_location('directory_verifier',PATH);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def asymmetric_token(algorithm="ES256"):
 from cryptography.hazmat.primitives.asymmetric import ec
 from cryptography.hazmat.primitives import serialization
 from cryptography.hazmat.primitives.asymmetric import rsa
 key_object=ec.generate_private_key(ec.SECP256R1()) if algorithm=='ES256' else rsa.generate_private_key(public_exponent=65537,key_size=2048)
 key=key_object.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
 return jwt.encode({'sub':'reader','org_id':'organization','exp':datetime.now(timezone.utc)+timedelta(minutes=5)},key,algorithm=algorithm)

@pytest.mark.parametrize("algorithm",["ES256","RS256"])
def test_current_supabase_session(verifier,monkeypatch,algorithm):
 token=asymmetric_token(algorithm);calls=[]
 def get(url,**kw):
  calls.append((url,kw));return httpx.Response(200,json={'id':'reader'},request=httpx.Request('GET',url))
 monkeypatch.setattr(httpx,'get',get)
 assert verifier._decode_token(token)['org_id']=='organization'
 assert calls[0][0]=='http://127.0.0.1:54321/auth/v1/user'
 assert calls[0][1]['headers']['Authorization']=='Bearer '+token
 assert calls[0][1]['timeout']<=5

@pytest.mark.parametrize('status,body',[(401,{}),(403,{}),(500,{}),(200,{'id':'other'})])
def test_rejected_verification(verifier,monkeypatch,status,body):
 monkeypatch.setattr(httpx,'get',lambda url,**kw:httpx.Response(status,json=body,request=httpx.Request('GET',url)))
 assert verifier._decode_token(asymmetric_token()) is None

def test_unavailable_auth(verifier,monkeypatch):
 def fail(*a,**kw):raise httpx.ConnectError('unavailable')
 monkeypatch.setattr(httpx,'get',fail);assert verifier._decode_token(asymmetric_token()) is None

def test_legacy_and_malformed(verifier):
 token=jwt.encode({'sub':'legacy','exp':datetime.now(timezone.utc)+timedelta(minutes=1)},'local-test-secret',algorithm='HS256')
 assert verifier._decode_token(token)['sub']=='legacy'
 assert verifier._decode_token('malformed') is None
 expired=jwt.encode({'sub':'legacy','exp':0},'local-test-secret',algorithm='HS256');assert verifier._decode_token(expired) is None

def test_vendored_copy_matches_template():
 assert PATH.read_bytes()==(PATH.parents[5]/'services/app-directory/auth/jwt_optional.py').read_bytes()

def test_file_based_configuration(monkeypatch,tmp_path):
 for name in ['SUPABASE_URL','SUPABASE_ANON_KEY']:monkeypatch.delenv(name,raising=False)
 env=tmp_path/'.env.local';env.write_text('SUPABASE_URL=http://127.0.0.1:54321\nSUPABASE_ANON_KEY=local-public\n')
 config_path=PATH.parents[5]/'services/app-directory/config.py'
 spec=importlib.util.spec_from_file_location('directory_file_config',config_path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 settings=module.Settings(_env_file=env)
 assert settings.supabase_url=='http://127.0.0.1:54321'
 assert settings.supabase_anon_key=='local-public'

def test_directory_endpoint_resolves_current_session(verifier,monkeypatch):
 from fastapi import FastAPI
 from fastapi.testclient import TestClient
 from types import ModuleType
 directory=PATH.parents[5]/'services/app-directory'
 monkeypatch.syspath_prepend(str(directory))
 monkeypatch.setitem(sys.modules,'auth.jwt_optional',verifier)
 # Use the real catalogue/config and router; only the external Auth response is simulated.
 spec=importlib.util.spec_from_file_location('config',directory/'config.py');config=importlib.util.module_from_spec(spec);spec.loader.exec_module(config)
 monkeypatch.setitem(sys.modules,'config',config)
 from routers.apps import router
 def get(url,**kw):return httpx.Response(200,json={'id':'reader'},request=httpx.Request('GET',url))
 monkeypatch.setattr(httpx,'get',get)
 app=FastAPI();app.include_router(router,prefix='/api')
 with TestClient(app) as client:
  response=client.get('/api/me/apps',headers={'Authorization':'Bearer '+asymmetric_token()})
  assert response.status_code==200
  assert response.json()['context']['org_id']=='organization'
  assert any(entry['id']=='pts' for entry in response.json()['apps'])
  rejected=client.get('/api/me/apps',headers={'Authorization':'Bearer malformed'})
  assert rejected.json()['apps']==[]
