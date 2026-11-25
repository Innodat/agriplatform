"""Leave entry-only closed wire contracts. No employment, drafts or universal active scope."""
import json,re
from typing import Annotated,Literal
from uuid import UUID
from pydantic import BaseModel,ConfigDict,Field,field_validator

class Closed(BaseModel):model_config=ConfigDict(extra='forbid')
Identifier=Annotated[str,Field(strict=True)]
def identifier(value):
    if type(value) is not str or not UUID(value).int or str(UUID(value))!=value:raise ValueError('identifier')
    return value

def json_object(raw):
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise ValueError('duplicate')
            result[key]=value
        return result
    value=json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError()))
    if type(value) is not dict:raise ValueError('object')
    return value

class Selection(Closed):
    operation_id:Identifier
    @field_validator('operation_id')
    @classmethod
    def id(cls,value):return identifier(value)
class SelectionResult(Closed):
    command:Literal['select_organization']='select_organization'
    org_id:Identifier
    event_id:Identifier
    @field_validator('org_id','event_id')
    @classmethod
    def ids(cls,value):return identifier(value)
class Receipt(Selection):
    status:Literal['committed']='committed'
    result:SelectionResult
class Unresolved(Selection):status:Literal['unresolved']='unresolved'
class Language(Closed):
    preferred_locale:Literal['en','pt']
    revision:Annotated[str,Field(pattern=r'^(0|[1-9][0-9]{0,18})$')]
    @field_validator('revision')
    @classmethod
    def revision_range(cls,value):
        if int(value)>9223372036854775807:raise ValueError('revision')
        return value
class SetLanguage(Selection):
    expected_revision:Annotated[str,Field(pattern=r'^(0|[1-9][0-9]{0,18})$')]
    preferred_locale:Literal['en','pt']
    @field_validator('expected_revision')
    @classmethod
    def revision_range(cls,value):return Language.revision_range(value)
