"""Format transition acceptance; method doubles do not establish SQL permissions."""
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

import pytest
from apps.scribeswell.backend import personal_notes_contract as contract
from apps.scribeswell.backend.passage_references import parse_reference

OP='11111111-1111-4111-8111-111111111111'
STUDY='22222222-2222-4222-8222-222222222222'
NOTE='33333333-3333-4333-8333-333333333333'

def value(version=2, text='Genesis 1:31–2:3'):
 return {'document':{'version':version,'blocks':[{'type':'paragraph','direction':'rtl','content':[{'type':'text','text':'שלום ','marks':['bold']},{'type':'passage_link','reference':parse_reference('Gen 1:31–2:3'),'label':text}]}]},'connections':[],'highlights':[]}

def payload(v=None, revision='2'):
 return {'operation_id':OP,'expected_revision':revision,'value':v or value()}

def test_format2_exact_roundtrip_and_empty_format2_retained():
 command=contract.parse_command('note.replace',json.dumps(payload()).encode())
 assert command.model_dump(mode='json')==payload()
 empty=value();empty['document']['blocks']=[]
 assert contract.parse_command('note.replace',json.dumps(payload(empty)).encode()).value.document.version==2

@pytest.mark.parametrize('mutation',[
 lambda v:v['document'].update(version=1),lambda v:v['document'].update(version=True),
 lambda v:v['document']['blocks'][0]['content'][1].update(label=''),
 lambda v:v['document']['blocks'][0]['content'][1].update(label='x'*201),
 lambda v:v['document']['blocks'][0]['content'][1].update(label='\ud800'),
 lambda v:v['document']['blocks'][0]['content'][1].update(url='https://example.org'),
 lambda v:v['document']['blocks'][0]['content'][1].update(marks=[]),
 lambda v:v['document']['blocks'][0]['content'][1]['reference'].update(catalogue_version='0'*64),
 lambda v:v['document']['blocks'][0]['content'][1]['reference']['target']['end'].update(verse=99),
 lambda v:v['document']['blocks'][0]['content'][1].update(type='unknown'),
])
def test_closed_link_rejection_is_safe(mutation):
 v=value();mutation(v)
 with pytest.raises(contract.ContractInputError) as caught:contract.parse_command('note.replace',json.dumps(payload(v)).encode())
 assert str(caught.value)=='scribeswell_personal_notes_input_invalid' and caught.value.__context__ is None

def test_link_labels_count_toward_document_text_budget():
 v=value();v['document']['blocks']=[{'type':'paragraph','direction':'auto','content':[{'type':'passage_link','reference':parse_reference('Gen 1'),'label':'x'*200} for _ in range(251)]}]
 from pydantic import ValidationError
 with pytest.raises(ValidationError,match='document budget exceeded'):contract.DocumentV2.model_validate_json(json.dumps(v['document']))

def test_locked_downgrade_fence_and_committed_v1_replay():
 sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
 from personal_notes_storage import PersonalNotesStorage
 from personal_notes_contract import parse_command
 from personal_notes_access import NotesError
 ordinary={'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]}
 submitted=parse_command('note.replace',json.dumps(payload(ordinary)).encode())
 now=datetime.now(timezone.utc)
 row={'id':NOTE,'study_id':STUDY,'account_id':OP,'revision':2,'visibility':'study','value':value(),'created_at':now,'updated_at':now,'created_by':OP,'updated_by':OP}
 class Cursor:
  def __init__(self):self.calls=[];self.receipt=None
  async def execute(self,sql,args=()):self.calls.append((sql,args))
  async def fetchone(self):return self.receipt
 cursor=Cursor();live_checks=[]
 class Storage(PersonalNotesStorage):
  @asynccontextmanager
  async def transaction(self,*args,**kwargs):yield cursor
  async def _parent(self,*args,**kwargs):assert kwargs.get('lock',False);return {}
  async def _note(self,*args,**kwargs):assert kwargs.get('lock',False);return row
  async def _live_outcome(self,cursor,account,outcome):live_checks.append(dict(outcome))
 storage=Storage('unused')
 async def run():
  with pytest.raises(NotesError) as caught:await storage.execute({'account_id':OP,'actor_id':OP},'note.replace',submitted,STUDY,NOTE,time.monotonic()+5)
  assert caught.value.code=='note_format_unsupported'
  assert not any(sql.startswith(('UPDATE','INSERT')) for sql,_ in cursor.calls)
  # Coherent distinct history: v1 no-op replacement at1 acknowledged1;
  # a later rich replacement advanced the same note to current revision2.
  earlier=payload(ordinary,revision='1');earlier['operation_id']=NOTE
  committed=parse_command('note.replace',json.dumps(earlier).encode())
  ack={'operation_id':NOTE,'command':'note.replace','study_id':STUDY,'note_id':NOTE,'revision':'1'}
  fingerprint=hashlib.sha256(json.dumps({'command':'note.replace','version':1,'study_id':STUDY,'note_id':NOTE,'payload':committed.model_dump(mode='json')},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
  cursor.receipt={'fingerprint':fingerprint,'outcome':ack};cursor.calls=[]
  assert await storage.execute({'account_id':OP,'actor_id':OP},'note.replace',committed,STUDY,NOTE,time.monotonic()+5)==ack
  assert live_checks==[ack] and row['revision']==2 and row['value']==value()
  assert not any(sql.startswith(('UPDATE','INSERT')) for sql,_ in cursor.calls)
 asyncio.run(run())

def test_actual_baseline_contract_refuses_v2_and_keeps_ordinary_serialization():
 sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
 sys.path.insert(0,str(Path(__file__).with_name('fixtures')))
 from note_links_baseline_loader import load
 baseline,storage=load()
 ordinary={'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]}
 raw=json.dumps(payload(ordinary)).encode()
 assert baseline.parse_command('note.replace',raw).model_dump_json()==contract.parse_command('note.replace',raw).model_dump_json()
 with pytest.raises(baseline.ContractInputError):baseline.parse_command('note.replace',json.dumps(payload()).encode())
 assert storage.NoteView is not contract.NoteView

def test_reference_models_count_toward_document_node_budget():
 from pydantic import ValidationError
 link={'type':'passage_link','reference':parse_reference('Gen 1'),'label':'x'}
 v=value();v['document']['blocks']=[{'type':'paragraph','direction':'auto','content':[link]*128} for _ in range(8)]
 with pytest.raises(ValidationError,match='document budget exceeded'):contract.DocumentV2.model_validate_json(json.dumps(v['document']))

@pytest.mark.parametrize('label',['Plain stored label שלום 😀','<b>plain characters</b>'])
def test_stored_label_is_preserved_as_scalar_plain_text(label):
 v=value(text=label)
 assert contract.parse_command('note.replace',json.dumps(payload(v)).encode()).value.document.blocks[0].content[1].label==label
