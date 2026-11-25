"""D2-A acceptance: strict complete input and compact save/recovery contracts."""
import asyncio,copy,sys
from pathlib import Path
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import httpx,pytest
from drafts import Input,empty_input
from main import create_app
from test_draft_context import Access,People,Config,ORG,NOW

DRAFT=str(uuid4());OPERATION=str(uuid4())
def body():return dict(operation_id=OPERATION,expected_revision='1',input=empty_input())
class Store:
    def __init__(self):self.calls=[]
    async def save(self,prepared,budget,draft,command,configuration,clock):
        from drafts import Committed,SaveResult
        self.calls.append(command.model_dump())
        return Committed(operation_id=command.operation_id,status='committed',result=SaveResult(command='save',draft_id=draft,revision='2',scope_generation='0',disposition='saved'))
def request(payload=None,*,raw=None,store=None,config=None,access=None):
    async def run():
        app=create_app(repository=object(),access=access or Access(),environment={},people=People(),configuration=config or Config(),clock=lambda:NOW,drafts=store or Store())
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://leave') as client:
            return await client.put(f'/v1/organizations/{ORG}/drafts/{DRAFT}/input',headers={'Authorization':'Bearer synthetic'},**({'content':raw} if raw is not None else {'json':payload or body()}))
    return asyncio.run(run())
@pytest.mark.parametrize('version',[True,False,1.0,'1',None,2])
def test_input_version_is_exact_integer_one(version):
    value=empty_input();value['input_version']=version
    with pytest.raises(ValueError):Input.model_validate(value)

def test_save_complete_input_without_normalization_or_domain_validation():
    value=body();value['input']['note']=' e\u0301 😀\n <script> '
    value['input']['full_days']['start']['text']=' 31/02/2026 '
    value['input']['full_days']['end']['text']='24/09/'
    value['input']['hours']['duration']['text']='1,5'
    store=Store();r=request(value,store=store)
    assert r.status_code==200 and r.json()['result']['command']=='save'
    assert store.calls==[value] and r.headers['cache-control']=='private, no-store'
    assert 'input' not in r.json()['result'] and 'note' not in r.text

@pytest.mark.parametrize('mutate,path,rule',[
    (lambda v:v['input'].pop('hours'),'input.hours','required'),
    (lambda v:v['input'].update(secret_medical_note='private'),'input','unknown_field'),
    (lambda v:v['input'].update(note='😀'*4001),'input.note','too_long'),
    (lambda v:v['input'].update(note='secret\0text'),'input.note','unsafe_text'),
    (lambda v:v['input'].update(input_version=True),'input.input_version','invalid_value'),
    (lambda v:v.update(expected_revision='01'),'expected_revision','invalid_value'),
    (lambda v:v['input']['hours']['duration'].update(text=1),'input.hours.duration.text','invalid_type'),
])
def test_safe_declared_validation_details(mutate,path,rule):
    value=body();mutate(value);store=Store();r=request(value,store=store)
    assert r.status_code==422 and r.json()=={'error_id':'validation_failed','error':'Request could not be completed','details':{'fields':[{'path':path,'rule':rule}]}}
    assert not store.calls and 'secret' not in r.text and 'private' not in r.text

@pytest.mark.parametrize('raw',[b'{"operation_id":"x","operation_id":"y"}',b'{',b'[]',b'{"input":NaN}',b'\xff'])
def test_malformed_body_has_safe_root_rule(raw):
    r=request(raw=raw);assert r.status_code==422
    assert r.json()['details']=={'fields':[{'path':'$','rule':'invalid_json'}]}

def test_body_byte_limit_is_32768_utf8_bytes_without_echo():
    r=request(raw=b' '*32769);assert r.status_code==413
    assert r.json()['details']=={'max_bytes':32768}

def test_save_fingerprint_binds_complete_input_target_guard_without_observations():
    from drafts import save_fingerprint,Save
    value=body();command=Save.model_validate(value);args=(ORG,ORG,ORG,DRAFT,command)
    first=save_fingerprint(*args)
    assert len(first)==32 and first==save_fingerprint(*args)
    reordered={k:value[k] for k in reversed(value)}
    assert first==save_fingerprint(ORG,ORG,ORG,DRAFT,Save.model_validate(reordered))
    for mutate in (lambda v:v['input'].update(note=' '),lambda v:v['input']['hours']['duration'].update(text='1.'),lambda v:v.update(expected_revision='2')):
        changed=copy.deepcopy(value);mutate(changed)
        assert first!=save_fingerprint(ORG,ORG,ORG,DRAFT,Save.model_validate(changed))
    assert first!=save_fingerprint(ORG,ORG,ORG,str(uuid4()),command)

@pytest.mark.parametrize('group,field,limit',[('full_days','start',64),('full_days','end',64),('half_day','date',64),('hours','date',64),('hours','duration',32)])
def test_each_text_boundary_counts_codepoints_without_truncation(group,field,limit):
    value=body();value['input'][group][field]['text']='😀'*limit
    store=Store();assert request(value,store=store).status_code==200
    assert store.calls[0]['input'][group][field]['text']=='😀'*limit
    value['input'][group][field]['text']+='😀';r=request(value)
    assert r.status_code==422 and r.json()['details']=={'fields':[{'path':'input.'+group+'.'+field+'.text','rule':'too_long'}]}
