"""Closed internal Studies enrollment wire; no target-account input."""
import json
from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, field_validator

PERMISSION='scribeswell.studies.use'
class Closed(BaseModel):
    model_config=ConfigDict(extra='forbid',json_schema_serialization_defaults_required=True)
class Operation(Closed):
    operation_id: UUID
    @field_validator('operation_id',mode='before')
    @classmethod
    def operation_uuid(cls,value):
        if not isinstance(value,str) or not UUID(value).int or str(UUID(value))!=value:raise ValueError('operation')
        return value
class AccountScope(Closed):
    kind: Literal['account']
class AccountCheck(Closed):
    permission: Literal['scribeswell.studies.use']
    authorization_scope: AccountScope
class EnrollmentResult(Closed):
    disposition: Literal['created','unchanged']
    account_id: UUID
    actor_id: UUID
    permission: Literal['scribeswell.studies.use']=PERMISSION
class EnrollmentAck(Closed):
    operation_id: UUID
    status: Literal['committed']='committed'
    result: EnrollmentResult
class AccountDecision(Closed):
    account_id: UUID
    actor_id: UUID
    permission: Literal['scribeswell.studies.use']=PERMISSION
    authorization_scope: AccountScope
    decision_id: UUID
    checked_at: datetime
class StudiesError(Closed):
    error_id: Literal['authentication_required','service_access_denied','access_denied',
        'identity.verification_required','validation_failed','authorization_unavailable',
        'identity.setup_unavailable','dependency_unavailable']
    error: Literal['Request could not be completed']='Request could not be completed'
    details: None=None

def object_pairs(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('duplicate')
        result[key]=value
    return result

def decode(raw,model):
    if len(raw)>4096 or raw.startswith(b'\xef\xbb\xbf'):raise ValueError('body')
    value=json.loads(raw.decode('utf-8'),object_pairs_hook=object_pairs,
        parse_constant=lambda _:(_ for _ in ()).throw(ValueError('constant')))
    return model.model_validate(value)

def inline_schema(model):
    schema=model.model_json_schema();definitions=schema.pop('$defs',{})
    def inline(value):
        if isinstance(value,dict):
            if '$ref' in value:return inline(definitions[value['$ref'].rsplit('/',1)[1]])
            return {key:inline(item) for key,item in value.items()}
        if isinstance(value,list):return [inline(item) for item in value]
        return value
    return inline(schema)
