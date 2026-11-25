"""Leave D1: atomic explicit start, compact outcomes and authorized current reads."""
import asyncio,time,re
from datetime import datetime,timezone
from typing import Annotated,Literal
from uuid import UUID,uuid4
from contextlib import asynccontextmanager
import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from pydantic import model_validator, Field,field_validator,ValidationError
from pydantic_core import PydanticCustomError
from contracts import Closed,identifier
from draft_context import Ready,Setup,Editable,ReadOnly,Notice
from access_client import Failure
from runtime_database import validated_url
from command_fingerprint import create_plain_fingerprint

MAX=9223372036854775807
class DraftFailure(Failure):
    def __init__(self,status,error_id,details=None):super().__init__(status,error_id);self.details=details or {}
def counter(value,positive=False):
    if type(value) is not str or re.fullmatch(r'0|[1-9][0-9]{0,18}',value) is None or int(value)>MAX or positive and value=='0':raise ValueError('counter')
    return value
def v4(value):
    value=identifier(value)
    if UUID(value).version!=4:raise ValueError('uuid4')
    return value
class Start(Closed):
    operation_id:str
    expected_scope_generation:str
    @field_validator('operation_id')
    @classmethod
    def operation(cls,value):return v4(value)
    @field_validator('expected_scope_generation')
    @classmethod
    def generation(cls,value):return counter(value)
class Summary(Closed):
    draft_id:str
    revision:str
    @field_validator('draft_id')
    @classmethod
    def id(cls,v):return v4(v)
    @field_validator('revision')
    @classmethod
    def rev(cls,v):return counter(v,True)
class DraftReady(Ready):
    scope_generation:str
    active_draft:Summary|None
    @field_validator('scope_generation')
    @classmethod
    def generation(cls,v):return counter(v)
ExtendedContext=Annotated[DraftReady|Setup,Field(discriminator='status')]
class StartResult(Summary):
    command:Literal['start']
    scope_generation:str
    disposition:Literal['created','resumed']
    @field_validator('scope_generation')
    @classmethod
    def generation(cls,v):return counter(v)
class SaveResult(Summary):
    command:Literal['save']
    scope_generation:str
    disposition:Literal['saved']
    @field_validator('scope_generation')
    @classmethod
    def generation(cls,v):return counter(v)
class DiscardResult(Summary):
    command:Literal['discard']
    scope_generation:str
    disposition:Literal['discarded']
    @field_validator('scope_generation')
    @classmethod
    def generation(cls,v):return counter(v)
CommandResult=Annotated[StartResult|SaveResult|DiscardResult,Field(discriminator='command')]
class Committed(Closed):
    operation_id:str
    status:Literal['committed']
    result:CommandResult
    @field_validator('operation_id')
    @classmethod
    def operation(cls,v):return v4(v)
class DraftUnresolved(Closed):
    operation_id:str
    status:Literal['unresolved']
    @field_validator('operation_id')
    @classmethod
    def operation(cls,v):return v4(v)
Outcome=Annotated[Committed|DraftUnresolved,Field(discriminator='status')]
class StartCommitted(Committed):result:StartResult
class SaveCommitted(Committed):result:SaveResult
class DiscardCommitted(Committed):result:DiscardResult
StartOutcome=Annotated[StartCommitted|DraftUnresolved,Field(discriminator='status')]
SaveOutcome=Annotated[SaveCommitted|DraftUnresolved,Field(discriminator='status')]
DiscardOutcome=Annotated[DiscardCommitted|DraftUnresolved,Field(discriminator='status')]
class DateEntry(Closed):
    text:Annotated[str,Field(strict=True,max_length=64)]
    format:Literal['dmy_numeric_v1']
    @field_validator('text')
    @classmethod
    def scalar(cls,v):
        if '\0' in v or any(0xd800<=ord(c)<=0xdfff for c in v):raise PydanticCustomError('unsafe_text','Unsafe text')
        return v
class DurationEntry(DateEntry):
    text:Annotated[str,Field(strict=True,max_length=32)]
    format:Literal['decimal_hours_dot_v1']
class FullDays(Closed):start:DateEntry;end:DateEntry
class HalfDay(Closed):date:DateEntry
class Hours(HalfDay):duration:DurationEntry
class Input(Closed):
    input_version:Literal[1]
    leave_type_id:str|None
    duration_mode:Literal['full_days','half_day','hours']|None
    full_days:FullDays
    half_day:HalfDay
    hours:Hours
    note:Annotated[str,Field(strict=True,max_length=4000)]
    @field_validator('input_version',mode='before')
    @classmethod
    def version(cls,v):
        if type(v) is not int or v!=1:raise ValueError('version')
        return v
    @field_validator('leave_type_id')
    @classmethod
    def type_id(cls,v):return identifier(v) if v is not None else v
    @field_validator('note')
    @classmethod
    def scalar(cls,v):return DateEntry.scalar(v)
class RevisionCommand(Closed):
    operation_id:str
    expected_revision:str
    @field_validator('operation_id')
    @classmethod
    def operation(cls,v):return v4(v)
    @field_validator('expected_revision')
    @classmethod
    def rev(cls,v):return counter(v,True)
class Discard(RevisionCommand):pass
class Save(RevisionCommand):
    input:Input
class Active(Summary):
    org_id:str
    state:Literal['active']
    input:Input
    editability:Annotated[Editable|ReadOnly,Field(discriminator='status')]
    setup_notices:list[Notice]
    updated_at:str
class Discarded(Summary):
    org_id:str
    state:Literal['discarded']
    discarded_at:str
DraftRead=Annotated[Active|Discarded,Field(discriminator='state')]
def empty_input():
    date=lambda:dict(text='',format='dmy_numeric_v1')
    return dict(input_version=1,leave_type_id=None,duration_mode=None,full_days=dict(start=date(),end=date()),half_day=dict(date=date()),hours=dict(date=date(),duration=dict(text='',format='decimal_hours_dot_v1')),note='')
def command_fingerprint(org,actor,employment,operation,generation):
    return create_plain_fingerprint(dict(purpose='leave.draft.command',fingerprint_version=1,command_version=1,org_id=org,actor_id=actor,employment_id=employment,operation_id=operation,command='start',draft_id=None,expected_revision=None,expected_scope_generation=generation,input=None))
def revision_fingerprint(org,actor,employment,draft,command,kind,input_value):
    return create_plain_fingerprint(dict(purpose='leave.draft.command',fingerprint_version=1,command_version=1,org_id=org,actor_id=actor,employment_id=employment,operation_id=command.operation_id,command=kind,draft_id=draft,expected_revision=command.expected_revision,expected_scope_generation=None,input=input_value))
def save_fingerprint(org,actor,employment,draft,command):
    return revision_fingerprint(org,actor,employment,draft,command,'save',command.input.model_dump())
def discard_fingerprint(org,actor,employment,draft,command):
    return revision_fingerprint(org,actor,employment,draft,command,'discard',None)
def require_ready(prepared):
    public=prepared.public
    if not isinstance(public,Ready):raise DraftFailure(409,'leave.setup_required',{'reason':public.reason})
    return public

def evidence(prepared):
    d=prepared.authority.manage_decision or prepared.authority.decision;o=prepared.observation
    base={k:o[k] for k in ('org_id','person_id','employment_id','revision','observed_at')}
    base.update(kind='discovery' if o['status']=='found' else 'effective',decision_id=d.decision_id,checked_at=d.checked_at,membership_id=d.membership_id,account_id=d.account_id)
    if base['kind']=='discovery':base['has_periods']=o['has_periods']
    else:base.update(as_of_date=o['as_of_date'],employment_state=o['employment_state'],period=o['period'],timezone=prepared.timezone.evidence)
    return base

class DraftRepository:
    def __init__(self,url):self.url=validated_url(url).set(drivername='postgresql').render_as_string(hide_password=False)
    def __repr__(self):return '<LeaveDraftRepository private>'
    @asynccontextmanager
    async def connection(self,prepared,budget,write=False,*,local=None,snapshot=False):
        public=require_ready(prepared);d=prepared.authority.decision;conn=None;expiry=None
        try:
            budget.remaining()
            if prepared.observed_at is None or not budget.started_at<=prepared.observed_at<=time.monotonic():raise DraftFailure(503,'dependency_unavailable')
            conn=await psycopg.AsyncConnection.connect(self.url,connect_timeout=max(1,min(3,int(budget.remaining()))),row_factory=dict_row)
            # The two-second local deadline includes COMMIT; a separate absolute
            # transport cutoff handles cancellation and uncertain commit completion.
            deadline=min(budget.deadline,time.monotonic()+2)
            if local is not None:local['deadline']=deadline
            expiry=asyncio.get_running_loop().call_at(deadline,conn.pgconn.finish)
            async with asyncio.timeout_at(deadline):
                async with conn.transaction():
                    # Source guards need a fresh statement snapshot after taking
                    # their coordination lock, regardless of the database default.
                    await conn.execute('SET TRANSACTION ISOLATION LEVEL '+('REPEATABLE READ' if snapshot else 'READ COMMITTED'))
                    if not write:await conn.execute('SET TRANSACTION READ ONLY')
                    await conn.execute("SELECT set_config('transaction_timeout',%s,true),set_config('statement_timeout',%s,true),set_config('lock_timeout',%s,true),set_config('app.org_id',%s,true),set_config('app.actor_id',%s,true),set_config('app.account_id',%s,true),set_config('app.employment_id',%s,true),set_config('app.mode',%s,true)",(str(budget.milliseconds(2)),str(budget.milliseconds(2)),str(budget.milliseconds(1)),public.org_id,d.actor_id,d.account_id,public.employment_id,'own_write' if write else 'own_read'))
                    yield conn
                budget.remaining()
        except Failure:raise
        except asyncio.CancelledError:raise
        except Exception:raise DraftFailure(503,'outcome_unresolved' if write else 'operation_verification_unavailable') from None
        finally:
            if expiry:expiry.cancel()
            if conn is not None:
                conn.pgconn.finish()
                try:
                    async with asyncio.timeout(.1):await conn.close()
                except BaseException:pass
    async def snapshot(self,prepared,budget):
        p=require_ready(prepared)
        async with self.connection(prepared,budget) as c:
            row=await (await c.execute('''SELECT s.generation,d.id,d.revision FROM (SELECT %s::uuid org_id,%s::uuid employment_id) x LEFT JOIN leave.draft_scope s USING(org_id,employment_id) LEFT JOIN leave.draft d ON d.org_id=x.org_id AND d.employment_id=x.employment_id AND d.state='active' ''',(p.org_id,p.employment_id))).fetchone()
            return dict(scope_generation=str(row['generation'] or 0),active_draft=dict(draft_id=str(row['id']),revision=str(row['revision'])) if row['id'] else None)
    async def read(self,prepared,budget,draft):
        p=require_ready(prepared)
        async with self.connection(prepared,budget) as c:
            row=await (await c.execute('SELECT id,revision,state,input,updated_at,discarded_at FROM leave.draft WHERE org_id=%s AND employment_id=%s AND id=%s',(p.org_id,p.employment_id,draft))).fetchone()
            if not row:raise DraftFailure(404,'resource_not_found')
            result=dict(org_id=p.org_id,draft_id=str(row['id']),revision=str(row['revision']),state=row['state'])
            if row['state']=='active':return Active(**result,input=row['input'],editability=p.editability,setup_notices=p.setup_notices,updated_at=row['updated_at'].astimezone(timezone.utc).isoformat())
            return Discarded(**result,discarded_at=row['discarded_at'].astimezone(timezone.utc).isoformat())
    async def editor(self,prepared,budget,draft):
        """One local snapshot for the requested row and visible background summary."""
        p=require_ready(prepared)
        async with self.connection(prepared,budget,snapshot=True) as c:
            row=await (await c.execute('SELECT id,revision,state,input,updated_at,discarded_at FROM leave.draft WHERE org_id=%s AND employment_id=%s AND id=%s',(p.org_id,p.employment_id,draft))).fetchone()
            if not row:raise DraftFailure(404,'resource_not_found')
            scope=await (await c.execute('''SELECT s.generation,d.id,d.revision FROM (SELECT %s::uuid org_id,%s::uuid employment_id) x LEFT JOIN leave.draft_scope s USING(org_id,employment_id) LEFT JOIN leave.draft d ON d.org_id=x.org_id AND d.employment_id=x.employment_id AND d.state='active' ''',(p.org_id,p.employment_id))).fetchone()
            summary=dict(scope_generation=str(scope['generation'] or 0),active_draft=dict(draft_id=str(scope['id']),revision=str(scope['revision'])) if scope['id'] else None)
            common=dict(org_id=p.org_id,draft_id=str(row['id']),revision=str(row['revision']),state=row['state'])
            value=Active(**common,input=row['input'],editability=p.editability,setup_notices=p.setup_notices,updated_at=row['updated_at'].astimezone(timezone.utc).isoformat()) if row['state']=='active' else Discarded(**common,discarded_at=row['discarded_at'].astimezone(timezone.utc).isoformat())
            return value,summary
    async def receipt(self,c,prepared,operation):
        p=require_ready(prepared);d=prepared.authority.decision
        row=await (await c.execute('SELECT * FROM leave.operation_receipt WHERE org_id=%s AND actor_id=%s AND operation_id=%s',(p.org_id,d.actor_id,operation))).fetchone()
        if row and str(row['employment_id'])!=p.employment_id:raise DraftFailure(409,'operation_mismatch')
        return row
    def outcome(self,row,operation):
        if row['command_version']!=1 or row['fingerprint_algorithm']!='sha256-jcs-v1' or row['fingerprint_version']!=1:raise DraftFailure(503,'operation_verification_unavailable')
        return Committed(operation_id=operation,status='committed',result=row['result'])
    async def lookup(self,prepared,budget,operation):
        async with self.connection(prepared,budget) as c:
            row=await self.receipt(c,prepared,operation)
            return self.outcome(row,operation) if row else DraftUnresolved(operation_id=operation,status='unresolved')
    async def start(self,prepared,budget,command,configuration,clock):
        p=require_ready(prepared);d=prepared.authority.decision;operation=command.operation_id
        fingerprint=command_fingerprint(p.org_id,d.actor_id,p.employment_id,operation,command.expected_scope_generation)
        local={};window=None
        async with self.connection(prepared,budget,True,local=local) as c:
            # First insertion contends on the unique scope key, then every writer
            # follows scope -> receipt -> draft. No HTTP occurs in this scope.
            await c.execute('INSERT INTO leave.draft_scope(org_id,employment_id,generation) VALUES(%s,%s,0) ON CONFLICT DO NOTHING',(p.org_id,p.employment_id))
            scope=await (await c.execute('SELECT generation FROM leave.draft_scope WHERE org_id=%s AND employment_id=%s FOR UPDATE',(p.org_id,p.employment_id))).fetchone()
            await c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",('leave.draft.operation.'+p.org_id+'.'+d.actor_id+'.'+operation,))
            row=await self.receipt(c,prepared,operation)
            if row:
                if row['command']!='start' or bytes(row['fingerprint'])!=fingerprint:raise DraftFailure(409,'operation_mismatch')
                result=self.outcome(row,operation)
            else:
                if p.editability.status!='editable':
                    reason=p.editability.reason
                    if reason=='permission_missing':raise DraftFailure(403,'access_denied')
                    if reason=='employment_periods_missing':raise DraftFailure(409,'leave.setup_required',{'reason':reason})
                    raise DraftFailure(403,'leave.draft_read_only',{'reason':reason})
                if str(scope['generation'])!=command.expected_scope_generation:raise DraftFailure(409,'leave.draft_start_outdated',{'current_scope_generation':str(scope['generation'])})
                if prepared.observation['status']=='effective':
                    if configuration is None:raise DraftFailure(503,'dependency_unavailable')
                    window=await configuration.guard(c,prepared,budget,clock,local['deadline'])
                draft=await (await c.execute("SELECT id,revision FROM leave.draft WHERE org_id=%s AND employment_id=%s AND state='active' FOR UPDATE",(p.org_id,p.employment_id))).fetchone()
                disposition='resumed'
                if not draft:
                    disposition='created'
                    draft=await (await c.execute("INSERT INTO leave.draft(id,org_id,employment_id,state,revision,input) VALUES(%s,%s,%s,'active',1,%s) RETURNING id,revision",(str(uuid4()),p.org_id,p.employment_id,Jsonb(empty_input())))).fetchone()
                result=Committed(operation_id=operation,status='committed',result=StartResult(command='start',draft_id=str(draft['id']),revision=str(draft['revision']),scope_generation=str(scope['generation']),disposition=disposition))
                await c.execute('''INSERT INTO leave.operation_receipt(org_id,actor_id,operation_id,employment_id,draft_id,command,command_version,fingerprint_algorithm,fingerprint_version,fingerprint,committed_revision,result,observation) VALUES(%s,%s,%s,%s,%s,'start',1,'sha256-jcs-v1',1,%s,%s,%s,%s)''',(p.org_id,d.actor_id,operation,p.employment_id,str(draft['id']),fingerprint,draft['revision'],Jsonb(result.result.model_dump()),Jsonb(evidence(prepared))))
                # Refresh once more after draft/receipt waits. The full remaining
                # transaction, including COMMIT, must fit before the same boundary.
                if window is not None:window.check(clock,local['deadline'])
        return result

    async def save(self,prepared,budget,draft,command,configuration,clock):
        return await self._revise(prepared,budget,draft,command,configuration,clock,'save')

    async def discard(self,prepared,budget,draft,command,configuration,clock):
        return await self._revise(prepared,budget,draft,command,configuration,clock,'discard')

    async def _revise(self,prepared,budget,draft,command,configuration,clock,kind):
        p=require_ready(prepared);d=prepared.authority.decision;operation=command.operation_id
        input_value=command.input.model_dump() if kind=='save' else None
        fingerprint=revision_fingerprint(p.org_id,d.actor_id,p.employment_id,draft,command,kind,input_value)
        local={};window=None
        async with self.connection(prepared,budget,True,local=local) as c:
            scope=await (await c.execute('SELECT generation FROM leave.draft_scope WHERE org_id=%s AND employment_id=%s FOR UPDATE',(p.org_id,p.employment_id))).fetchone()
            if not scope:raise DraftFailure(404,'resource_not_found')
            await c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",('leave.draft.operation.'+p.org_id+'.'+d.actor_id+'.'+operation,))
            row=await self.receipt(c,prepared,operation)
            if row:
                if row['command']!=kind or bytes(row['fingerprint'])!=fingerprint:raise DraftFailure(409,'operation_mismatch')
                result=self.outcome(row,operation)
            else:
                target=await (await c.execute('SELECT id,revision,state FROM leave.draft WHERE org_id=%s AND employment_id=%s AND id=%s FOR UPDATE',(p.org_id,p.employment_id,draft))).fetchone()
                if not target:raise DraftFailure(404,'resource_not_found')
                if kind=='save' and target['state']=='discarded':raise DraftFailure(409,'leave.draft_discarded',{'draft_id':draft})
                if p.editability.status!='editable':
                    reason=p.editability.reason
                    if reason=='permission_missing':raise DraftFailure(403,'access_denied')
                    if reason=='employment_periods_missing':raise DraftFailure(409,'leave.setup_required',{'reason':reason})
                    raise DraftFailure(403,'leave.draft_read_only',{'reason':reason})
                if target['state']=='discarded':raise DraftFailure(409,'leave.draft_discarded',{'draft_id':draft})
                if str(target['revision'])!=command.expected_revision:raise DraftFailure(409,'leave.draft_revision_conflict',{'current_revision':str(target['revision'])})
                if prepared.observation['status']=='effective':
                    if configuration is None:raise DraftFailure(503,'dependency_unavailable')
                    window=await configuration.guard(c,prepared,budget,clock,local['deadline'])
                if kind=='discard':
                    changed=await (await c.execute("UPDATE leave.draft SET input=NULL,state='discarded',revision=revision+1 WHERE org_id=%s AND employment_id=%s AND id=%s RETURNING revision",(p.org_id,p.employment_id,draft))).fetchone()
                    advanced=await (await c.execute('UPDATE leave.draft_scope SET generation=generation+1 WHERE org_id=%s AND employment_id=%s RETURNING generation',(p.org_id,p.employment_id))).fetchone()
                    details=DiscardResult(command='discard',draft_id=draft,revision=str(changed['revision']),scope_generation=str(advanced['generation']),disposition='discarded')
                else:
                    changed=await (await c.execute('UPDATE leave.draft SET input=%s,revision=revision+1 WHERE org_id=%s AND employment_id=%s AND id=%s RETURNING revision',(Jsonb(input_value),p.org_id,p.employment_id,draft))).fetchone()
                    details=SaveResult(command='save',draft_id=draft,revision=str(changed['revision']),scope_generation=str(scope['generation']),disposition='saved')
                result=Committed(operation_id=operation,status='committed',result=details)
                await c.execute("""INSERT INTO leave.operation_receipt(org_id,actor_id,operation_id,employment_id,draft_id,command,command_version,fingerprint_algorithm,fingerprint_version,fingerprint,committed_revision,result,observation) VALUES(%s,%s,%s,%s,%s,%s,1,'sha256-jcs-v1',1,%s,%s,%s,%s)""",(p.org_id,d.actor_id,operation,p.employment_id,draft,kind,fingerprint,changed['revision'],Jsonb(details.model_dump()),Jsonb(evidence(prepared))))
                if window is not None:window.check(clock,local['deadline'])
        return result

class GenerationDetails(Closed):
    current_scope_generation:str
class RevisionDetails(Closed):
    current_revision:str
    @field_validator('current_revision')
    @classmethod
    def revision(cls,v):return counter(v,True)
class TargetDetails(Closed):
    draft_id:str
    @field_validator('draft_id')
    @classmethod
    def target(cls,v):return v4(v)
class ReasonDetails(Closed):
    reason:Literal['employment_ended','employment_missing','employment_periods_missing','identity_person_link_required','identity_actor_setup_required']
class SizeDetails(Closed):max_bytes:Literal[32768]
FieldPath=Literal['$','operation_id','expected_revision','expected_scope_generation','input','input.input_version','input.leave_type_id','input.duration_mode','input.note','input.full_days','input.half_day','input.hours','input.full_days.start','input.full_days.start.text','input.full_days.start.format','input.full_days.end','input.full_days.end.text','input.full_days.end.format','input.half_day.date','input.half_day.date.text','input.half_day.date.format','input.hours.date','input.hours.date.text','input.hours.date.format','input.hours.duration','input.hours.duration.text','input.hours.duration.format']
FieldRule=Literal['required','unknown_field','invalid_type','invalid_value','too_long','unsafe_text','invalid_json']
class FieldIssue(Closed):
    path:FieldPath
    rule:FieldRule
class FieldDetails(Closed):
    fields:Annotated[list[FieldIssue],Field(min_length=1,max_length=64)]
class EmptyDetails(Closed):pass

def validation_details(error):
    # Only declared paths and stable rules leave this boundary. Unknown keys may
    # themselves contain sensitive input; report their nearest declared container.
    from typing import get_args
    declared=set(get_args(FieldPath));issues=[]
    for item in error.errors(include_url=False,include_context=False,include_input=False):
        parts=[str(v) for v in item['loc']];path='.'.join(parts)
        while path not in declared and parts:parts.pop();path='.'.join(parts)
        path=path if path in declared else '$';kind=item['type']
        rule={'missing':'required','extra_forbidden':'unknown_field','string_too_long':'too_long','unsafe_text':'unsafe_text','string_type':'invalid_type','model_type':'invalid_type','dict_type':'invalid_type'}.get(kind,'invalid_value')
        issue={'path':path,'rule':rule}
        if issue not in issues:issues.append(issue)
        if len(issues)==64:break
    return {'fields':issues}

class DraftErrorEnvelope(Closed):
    error_id:str
    error:str
    details:GenerationDetails|RevisionDetails|TargetDetails|ReasonDetails|SizeDetails|FieldDetails|EmptyDetails

# The opening contract composes owner queries without changing prior read shapes.
from draft_choices import Choices
class EditorActive(Closed):
    context:DraftReady
    draft:Active
    choices:Choices
    @model_validator(mode='after')
    def bindings(self):
        c,d=self.context,self.draft
        if c.org_id!=d.org_id or c.active_draft is None or c.active_draft.draft_id!=d.draft_id or c.active_draft.revision!=d.revision or c.editability!=d.editability or c.setup_notices!=d.setup_notices:raise ValueError('editor_binding')
        selected=self.choices.selected;target=d.input.leave_type_id
        if target is None:
            if selected.status!='not_requested':raise ValueError('selected_binding')
        elif selected.status=='not_requested' or selected.status=='available' and selected.choice.type_id!=target:raise ValueError('selected_binding')
        if selected.status=='obsolete' and any(choice.type_id==target for choice in self.choices.choices):raise ValueError('selected_binding')
        if selected.status=='available':
            for choice in self.choices.choices:
                if choice.type_id==target and choice!=selected.choice:raise ValueError('selected_binding')
        return self
class EditorClosed(Closed):
    context:DraftReady
    draft:Discarded
    @model_validator(mode='after')
    def bindings(self):
        if self.context.org_id!=self.draft.org_id or self.context.active_draft is not None and self.context.active_draft.draft_id==self.draft.draft_id:raise ValueError('editor_binding')
        return self
EditorRead=EditorActive|EditorClosed
