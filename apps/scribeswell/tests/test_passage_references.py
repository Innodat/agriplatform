"""Pinned catalogue/parser acceptance. No SQL or imported-text availability claims."""
import copy
import json
import subprocess
import sys
from pathlib import Path
import pytest
from apps.scribeswell.backend import passage_references as refs

@pytest.mark.parametrize(('text','book','target'), [
 ('Psalm110:1','Ps',{'kind':'verse_range','start':{'chapter':110,'verse':1},'end':{'chapter':110,'verse':1}}),
 ('Ps 110:1–3','Ps',{'kind':'verse_range','start':{'chapter':110,'verse':1},'end':{'chapter':110,'verse':3}}),
 ('תהילים קי:1','Ps',{'kind':'verse_range','start':{'chapter':110,'verse':1},'end':{'chapter':110,'verse':1}}),
 ('Genesis1:31–2:3','Gen',{'kind':'verse_range','start':{'chapter':1,'verse':31},'end':{'chapter':2,'verse':3}}),
 ('Matthew26:63–64','Matt',{'kind':'verse_range','start':{'chapter':26,'verse':63},'end':{'chapter':26,'verse':64}}),
 ('בראשית ט״ו','Gen',{'kind':'chapter','chapter':15}),
 ('1 Samuel 2','1Sam',{'kind':'chapter','chapter':2}),
])
def test_reference_identity(text,book,target):
 result=refs.parse_reference(text)
 assert result['book_id']==book and result['target']==target
 assert refs.validate_reference(result)==result

@pytest.mark.parametrize('text',['Genesis 1.1','Ps 11.0:1','Ps2:10–13','Gen 0','Gen 1:0','Gen 1:3–1','Genesis 51','Matt 26:76','Gen 1:31–','G 1','Gen יה','Gen יו','Gen אא','Gen 1:1–Exod 1:1','Gen 1:2–1:1'])
def test_invalid_never_guesses(text):
 with pytest.raises(refs.ReferenceError):refs.parse_reference(text)

@pytest.mark.parametrize('change',[
 {'catalogue_version':'0'*64},{'versification_id':'crosswire-kjv-3765'}, {'owner':'forged'},
 {'target':{'kind':'chapter','chapter':True}}, {'target':{'kind':'chapter','chapter':'1'}},
 {'target':{'kind':'chapter','chapter':1,'verse':1}},
])
def test_strict_source_and_shape(change):
 value=refs.parse_reference('Gen 1');value.update(change)
 with pytest.raises(refs.ReferenceError):refs.validate_reference(value)

def test_inventory_pinning_and_browser_parity():
 app=Path(__file__).resolve().parents[1]
 result=subprocess.run([sys.executable,str(app/'tools/py/build_reference_catalogue.py'),'--check'],capture_output=True)
 assert result.returncode==0,result.stderr.decode()
 inventory=json.loads((app/'data/reference-catalogue/catalogue.json').read_text())
 assert len(inventory['books'])==66
 assert inventory==json.loads((app/'web/src/generated/reference-catalogue.json').read_text())
 assert refs.BOOKS['Matt']['text_support']=='reference_only'
 assert refs.BOOKS['Ps']['chapter_verse_counts'][1]==12

def test_collection_wire_is_closed_and_independent():
 from apps.scribeswell.backend.personal_notes_contract import parse_command, ContractInputError, PassageList
 op='11111111-1111-4111-8111-111111111111'
 ref=refs.parse_reference('Gen 1')
 payload={'operation_id':op,'expected_revision':'1','items':[{'id':op,'reference':ref}]}
 parsed=parse_command('study.passages.replace',json.dumps(payload).encode())
 assert parsed.items[0].reference.model_dump(mode='json')==ref
 for mutate in [lambda p:p['items'].append(p['items'][0]),lambda p:p.update(actor=op),lambda p:p['items'][0]['reference'].update(catalogue_version='f'*64)]:
  changed=copy.deepcopy(payload);mutate(changed)
  with pytest.raises(ContractInputError):parse_command('study.passages.replace',json.dumps(changed).encode())
 assert PassageList.model_validate_json(json.dumps({'study_id':op,'revision':'1','items':[]})).revision=='1'

@pytest.mark.parametrize('text',['Ps. 110:1','Psalm קי:1','Psalm קטו:1','Psalm קטז:1','Ps 119:קטו–קטז'])
def test_declared_book_punctuation_and_canonical_hundreds(text):
 assert refs.parse_reference(text)['book_id']=='Ps'

@pytest.mark.parametrize('text',['Genesis 1.1','Ps 11.0:1','Genesis 1:1.0','Genesis 1:1-1.2'])
def test_numeric_punctuation_never_changes_meaning(text):
 with pytest.raises(refs.ReferenceError):refs.parse_reference(text)

def test_ambiguous_alias_is_typed_and_offers_choices(monkeypatch):
 monkeypatch.setitem(refs.ALIASES,'shared',{'Gen','Exod'})
 with pytest.raises(refs.ReferenceError) as caught:refs.parse_reference('shared1')
 assert caught.value.code=='reference_ambiguous' and set(caught.value.choices)=={'Gen','Exod'}

def test_two_hundred_distinct_valid_ranges_fit_collection_specific_bounded_command():
 from apps.scribeswell.backend.personal_notes_contract import parse_command,ContractInputError
 from uuid import uuid4
 items=[{'id':str(uuid4()),'reference':refs.parse_reference(f'Gen 1:1–{chapter}:{verse}')} for chapter in range(2,20) for verse in range(1,min(19,refs.BOOKS['Gen']['chapter_verse_counts'][chapter-1])+1)][:200]
 payload={'operation_id':str(uuid4()),'expected_revision':'1','items':items}
 raw=json.dumps(payload).encode()
 assert len(raw)>65536
 assert len(parse_command('study.passages.replace',raw).items)==200
 with pytest.raises(ContractInputError):parse_command('study.passages.replace',raw+b' '*131072)

@pytest.mark.parametrize('rebind',['same_id_new_reference','same_reference_new_id'])
def test_storage_refuses_retained_identity_rebinding_before_any_write(rebind):
 """Actual replacement-method control flow only; cursor double is not SQL proof."""
 import asyncio
 sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
 from personal_notes_storage import PersonalNotesStorage
 from personal_notes_contract import parse_command
 from personal_notes_access import NotesError
 first='11111111-1111-4111-8111-111111111111';second='22222222-2222-4222-8222-222222222222'
 reference=refs.parse_reference('Gen1');current={'study_id':first,'revision':'2','items':[{'id':first,'reference':reference}]}
 class Storage(PersonalNotesStorage):
  async def _passages(self,*args):return current,[]
 class Cursor:
  def __init__(self):self.writes=[]
  async def execute(self,*args):self.writes.append(args)
 candidate={'id':first if rebind=='same_id_new_reference' else second,'reference':refs.parse_reference('Ps110') if rebind=='same_id_new_reference' else reference}
 payload=parse_command('study.passages.replace',json.dumps({'operation_id':second,'expected_revision':'2','items':[candidate]}).encode())
 cursor=Cursor()
 with pytest.raises(NotesError,match='scribeswell_personal_notes_input_invalid'):
  asyncio.run(Storage('postgresql://unused')._replace_passages(cursor,first,first,first,payload))
 assert cursor.writes==[]

@pytest.mark.parametrize('text',['Gen . 1','Gen 1׃1','Gen 1׀1','Genesis 1:1׃2','Ps 11.0:1','Gen 1.1'])
def test_review_numeric_punctuation_is_not_pointing(text):
 with pytest.raises(refs.ReferenceError):refs.parse_reference(text)

@pytest.mark.parametrize('text',['I. Samuel 2','II. Samuel 2','Ps. 110:1'])
def test_review_book_only_punctuation(text):
 assert refs.parse_reference(text)['target']
