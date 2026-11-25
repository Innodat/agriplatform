"""Restricted Leave configuration commands. Login mapping supplies durable executor."""
import json,re
from datetime import date,datetime,timezone
from typing import Annotated,Literal
from pydantic import Field,TypeAdapter,field_validator,model_validator
from contracts import Closed,identifier,json_object
from draft_choices import MODES,configuration_name
class OperationError(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)
class Scope(Closed):
    kind:Literal['organization']
    org_id:Annotated[str,Field(strict=True)]
    @field_validator('org_id')
    @classmethod
    def id(cls,value):return identifier(value)
class CreatePayload(Closed):
    type_id:Annotated[str,Field(strict=True)]
    version_id:Annotated[str,Field(strict=True)]
    code:Annotated[str,Field(strict=True)]
    name:Annotated[str,Field(strict=True)]
    permitted_modes:list[Literal['full_days','half_day','hours']]=Field(min_length=1,max_length=3)
    effective_from:Annotated[str,Field(strict=True)]
    effective_to:Annotated[str,Field(strict=True)]|None
    expected_absent:Literal[True]
    @field_validator('type_id','version_id')
    @classmethod
    def ids(cls,value):return identifier(value)
    @field_validator('code')
    @classmethod
    def code_value(cls,value):
        value=value.strip().lower()
        if not re.fullmatch(r'[a-z][a-z0-9_]{0,63}',value):raise ValueError('code')
        return value
    @field_validator('name')
    @classmethod
    def name_value(cls,value):return configuration_name(value)
    @field_validator('permitted_modes')
    @classmethod
    def modes(cls,value):
        if len(set(value))!=len(value):raise ValueError('modes')
        return [mode for mode in MODES if mode in value]
    @field_validator('effective_from','effective_to')
    @classmethod
    def dates(cls,value):
        if value is not None and (not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}',value) or date.fromisoformat(value).isoformat()!=value):raise ValueError('date')
        return value
    @model_validator(mode='after')
    def order(self):
        if self.effective_to is not None and self.effective_to<self.effective_from:raise ValueError('date')
        return self
class ArchivePayload(Closed):
    type_id:Annotated[str,Field(strict=True)]
    expected_revision:Annotated[str,Field(strict=True,pattern=r'^[1-9][0-9]{0,18}$')]
    @field_validator('type_id')
    @classmethod
    def id(cls,value):return identifier(value)
    @field_validator('expected_revision')
    @classmethod
    def revision(cls,value):
        if int(value)>9223372036854775807:raise ValueError('revision')
        return value
class Envelope(Closed):
    schema_version:Literal[1]
    operation_id:Annotated[str,Field(strict=True)]
    scope:Scope
    reason_code:Literal['initial_setup','synthetic_fixture','identity_adoption','access_change','setup_correction']
    evidence_ref:Annotated[str,Field(strict=True,pattern=r'^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}$')]|None=None
    @field_validator('operation_id')
    @classmethod
    def id(cls,value):return identifier(value)
    @field_validator('evidence_ref')
    @classmethod
    def evidence(cls,value):
        if value is not None and '://' in value:raise ValueError('evidence')
        return value
class CreateCommand(Envelope):
    command:Literal['leave_type.create']
    payload:CreatePayload
class ArchiveCommand(Envelope):
    command:Literal['leave_type.archive']
    payload:ArchivePayload
Command=Annotated[CreateCommand|ArchiveCommand,Field(discriminator='command')]
def parse_command(raw):
    try:
        if type(raw) is not bytes or len(raw)>65536:raise ValueError()
        value=json_object(raw)
        if type(value.get('schema_version')) is not int:raise ValueError()
        if value.get('command')=='leave_type.create' and type(value.get('payload',{}).get('expected_absent')) is not bool:raise ValueError()
        # JSON strings must be Unicode scalars even in optional reference fields.
        raw.decode('utf-8').encode('utf-8')
        command=TypeAdapter(Command).validate_python(value)
        canonical_command(command) # verifies decoded escape strings as well
        return command
    except Exception:raise OperationError('command_invalid') from None
def canonical_command(command):
    # This closed schema has ASCII property names, only integer 1, booleans/null,
    # strings and arrays. stdlib JSON's Unicode scalar encoding is exact RFC8785
    # for that subset; no float/general-purpose JCS implementation is introduced.
    return json.dumps(command.model_dump(mode='json',exclude_none=False),ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
def mapped(error):
    state=getattr(error,'sqlstate',None)
    return OperationError({'42501':'access_denied','P0002':'operation_conflict','P0003':'operation_payload_mismatch','23505':'operation_conflict','23503':'operation_conflict','23514':'command_invalid','22023':'command_invalid','22007':'command_invalid','22008':'command_invalid','22P02':'command_invalid','22003':'command_invalid','55P03':'operation_busy','57014':'operation_busy'}.get(state,'operation_unavailable'))
def receipt(value,command,operation,org,type_id):
    try:
        if type(value) is not dict or set(value)!={'operation_id','status','result','command_version','result_version','committed_at'} or value['operation_id']!=operation or value['status']!='committed' or type(value['command_version']) is not int or value['command_version']!=1 or type(value['result_version']) is not int or value['result_version']!=1:raise ValueError()
        result=value['result'];target=result['target']
        if set(result)!={'command','target','disposition','revision','event_id'} or result['command']!=command or result['disposition']!=('created' if command=='leave_type.create' else 'changed') or type(result['revision']) is not str or not re.fullmatch(r'[1-9][0-9]{0,18}',result['revision']) or int(result['revision'])>9223372036854775807:raise ValueError()
        identifier(result['event_id'])
        if set(target)!=({'org_id','type_id','version_id'} if command=='leave_type.create' else {'org_id','type_id'}) or target['org_id']!=org or target['type_id']!=type_id:raise ValueError()
        for item in target.values():identifier(item)
        stamp=datetime.fromisoformat(value['committed_at'])
        if stamp.tzinfo is None or stamp.utcoffset()!=timezone.utc.utcoffset(stamp):raise ValueError()
        return value
    except Exception:raise OperationError('operation_verification_unavailable') from None
async def execute(connection,raw):
    command=parse_command(raw);canonical=canonical_command(command)
    from psycopg.pq import TransactionStatus
    if connection.info.transaction_status!=TransactionStatus.IDLE:raise OperationError('connection_busy')
    try:
        async with connection.transaction():
            await connection.execute("SELECT set_config('transaction_timeout','2000',true),set_config('statement_timeout','2000',true),set_config('lock_timeout','1000',true),set_config('TimeZone','UTC',true)")
            cursor=await connection.execute('SELECT leave.execute_command(%s::jsonb,%s)',(canonical.decode('utf-8'),canonical))
            result=receipt((await cursor.fetchone())[0],command.command,command.operation_id,command.scope.org_id,command.payload.type_id)
            if command.command=='leave_type.create' and result['result']['target']['version_id']!=command.payload.version_id:raise OperationError('operation_verification_unavailable')
        return result
    except OperationError:raise
    except Exception as error:raise mapped(error) from None
async def outcome(connection,command,operation,org,type_id):
    try:
        if command not in ('leave_type.create','leave_type.archive'):raise ValueError()
        operation=identifier(operation);org=identifier(org);type_id=identifier(type_id)
    except Exception:raise OperationError('command_invalid') from None
    try:
        async with connection.transaction():
            await connection.execute("SELECT set_config('transaction_timeout','2000',true),set_config('statement_timeout','2000',true),set_config('lock_timeout','1000',true),set_config('TimeZone','UTC',true)")
            cursor=await connection.execute('SELECT leave.command_outcome(%s,%s,%s,%s)',(command,org,type_id,operation));value=(await cursor.fetchone())[0]
            if value=={'operation_id':operation,'status':'unresolved'}:return value
            return receipt(value,command,operation,org,type_id)
    except OperationError:raise
    except Exception as error:raise mapped(error) from None
