import copy
import pytest
from apps.pts.backend.collection import select

def library(licence, **changes):
    right={'id':'R','licence':licence, **changes}
    poem={'id':'P','work_id':'P','title':'Poem','text':'Swahili verse','source_id':'S','creator':{'name':'Author'},'geography':{},'classification':{'genre':'poem'},'quality':{'text_status':'checked_transcription','complete_in_witness':True}}
    return {'schema_version':'1.2','poems':[poem],'sources':[{'id':'S','title':'Primary poems','rights_id':'R'}],'rights':[right],'witnesses':[],'source_documents':[]}

@pytest.mark.parametrize('licence',['CC BY 4.0','CC BY-NC 4.0','CC BY-SA 4.0','CC BY-NC-SA 4.0','CC BY-ND 4.0','CC BY-NC-ND 4.0'])
def test_direct_cc4_poems_are_eligible_for_private_noncommercial_training(licence):
    result=select(library(licence),availability='research')
    assert len(result['poems'])==1
    usage=result['research_usage']['P']
    assert usage['eligible_for_private_training'] is True
    assert usage['scope']=='private_noncommercial_psalm_ai_training'
    assert usage['status'] in ['allowed','conditional']
    assert usage['public_release_assessed'] is False

def test_container_licence_does_not_clear_independent_quoted_poems():
    result=select(library('Article-level CC BY 4.0',assessment='Independent poem rights unresolved',review_status='Conservative rights hold'),availability='research')
    assert result['poems']==[]
    full=select(library('Article-level CC BY 4.0',assessment='Independent poem rights unresolved',review_status='Conservative rights hold'))
    assert full['research_usage']['P']['status']=='review'

def test_nd3_and_unknown_licences_are_not_silently_approved():
    for licence in ['CC BY-NC-ND 3.0','No licence established','unknown']:
        assert select(library(licence),availability='research')['poems']==[]

def test_ready_filter_requires_checked_complete_text_without_rewriting_original():
    value=library('CC BY-NC-ND 4.0');original=copy.deepcopy(value)
    assert select(value,availability='research')['poems']
    assert value==original
    value['poems'][0]['quality']['text_status']='ocr_draft'
    assert select(value,availability='research')['poems']==[]
    assert select(value)['research_usage']['P']['eligible_for_private_training'] is True
    value['poems'][0]['text']=None
    assert select(value,availability='research')['poems']==[]

def test_explicit_hold_overrides_generic_cc4_label():
    assert select(library('CC BY 4.0',ai_use={'private_model_training':False}),availability='research')['poems']==[]

def test_wastara_pdf_working_terms_support_only_the_private_project():
    value=library('Conflicting CC BY 4.0 metadata / CC BY-NC-SA 4.0 PDF',ai_use={'rights_tier':'licence_clarification_needed'})
    result=select(value,availability='research')
    assert result['research_usage']['P']['status']=='conditional'
    assert 'PDF' in result['research_usage']['P']['summary']
    assert result['research_usage']['P']['public_release_assessed'] is False

def test_ready_training_export_does_not_append_unchecked_witness_text():
    value=library('CC BY 4.0')
    value['witnesses']=[{'id':'W','poem_id':'P','source_id':'S','text':'Unchecked OCR witness','status':'ocr_draft'}]
    assert select(value,availability='research')['witnesses']==[]
    assert select(value)['witnesses']==value['witnesses']

@pytest.mark.parametrize('licence',['CC0 1.0','https://creativecommons.org/publicdomain/zero/1.0/','CC BY 3.0','https://creativecommons.org/licenses/by-nc/3.0/'])
def test_direct_reusable_terms_are_not_unnecessarily_held(licence):
    assert select(library(licence),availability='research')['poems']

def test_unresolved_conflicting_terms_need_review_unless_the_pdf_working_terms_are_known():
    assert select(library('Conflicting CC BY 4.0 / all rights reserved'),availability='research')['poems']==[]
