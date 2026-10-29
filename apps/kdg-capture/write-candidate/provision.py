"""Unmounted protected setup producer. Opaque committed references confer no rights."""
import asyncio
from datetime import datetime, timedelta, timezone
import json
import re
import secrets
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field
from sqlalchemy.exc import SQLAlchemyError
from context import Context, canonical_uuid, MEMBERSHIP_PATTERN
import capture_create_handler as protected
from capture_edit_handler import EditEvidence
from capture_history import OwnReadObservation
import capture_read as read
from questionnaire import parse_definition

write=protected.write
create=protected.create
MAX_CHILDREN=1000
MAX_RESPONSE_BYTES=1024*1024
READ='kdg_capture.capture.read.own'
EDIT='kdg_capture.capture.edit.own'
STATUS={**protected.WRITE_STATUS,'provision_unavailable':503}

class OwnEditObservation(EditEvidence):
    expires_at: datetime

class CreateAllEvidence(Context):
    permission: Literal['kdg_capture.capture.create.all']
class CreateAssignedEvidence(Context):
    permission: Literal['kdg_capture.capture.create.assigned']
class CreateAllObservation(CreateAllEvidence):
    expires_at: datetime
class CreateAssignedObservation(CreateAssignedEvidence):
    expires_at: datetime

class Assignment(read.Closed):
    assignment_id: read.Identifier
    assignment_revision: read.Revision
class Child(read.Closed):
    child_id: read.Identifier
    child_label: Annotated[read.Label,Field(max_length=200)]
    child_revision: read.Revision
    child_eligibility_ref: Annotated[str,Field(strict=True,min_length=43,max_length=43,pattern=r'^[A-Za-z0-9_-]{43}$')]
    create_permission: Literal['kdg_capture.capture.create.all','kdg_capture.capture.create.assigned']
    assignment: Assignment|None
    checked_at: read.DeviceTime
    expires_at: read.DeviceTime
class PublishedQuestionnaire(read.Closed):
    questionnaire_id: read.Identifier
    questionnaire_version_id: read.Identifier
    questionnaire_version: read.Revision
    definition: read.QuestionnaireDefinition
class Provision(read.Closed):
    schema_version: Literal[1]
    org_id: read.Identifier
    account_id: read.Identifier
    actor_id: read.Identifier
    membership_id: Annotated[str,Field(strict=True,pattern=MEMBERSHIP_PATTERN)]
    read_observation: OwnReadObservation
    edit_observation: OwnEditObservation|None
    create_all_observation: CreateAllObservation|None
    create_assigned_observation: CreateAssignedObservation|None
    create_state: Literal['ready','not_permitted','no_eligible_children','no_published_questionnaire']
    children: Annotated[list[Child],Field(max_length=MAX_CHILDREN)]
    questionnaire: PublishedQuestionnaire|None

CHILDREN='''SELECT id,org_id,display_name,active,revision FROM kdg_capture.child
WHERE org_id=CAST(:org AS uuid) AND active ORDER BY id LIMIT :row_limit'''
ASSIGNED_CHILDREN='''SELECT ch.id,ch.org_id,ch.display_name,ch.active,ch.revision FROM kdg_capture.child ch
JOIN kdg_capture.child_assignment a ON a.org_id=ch.org_id AND a.child_id=ch.id
WHERE ch.org_id=CAST(:org AS uuid) AND ch.active AND a.account_id=CAST(:account AS uuid)
AND a.membership_id=:member AND a.active ORDER BY ch.id LIMIT :row_limit'''
# PostgreSQL evaluates output expressions after ORDER BY when they are not sort
# keys (PostgreSQL17 SELECT/SELECT List). The volatile lock expression is not a
# sort/group/distinct key: every exact existing child key is acquired in UUID order.
LOCK_CHILDREN="""SELECT child_id,pg_advisory_xact_lock(hashtextextended(
'kdg_capture:child:v1:' || :org || ':' || child_id::text,0)) AS locked
FROM unnest(CAST(:children AS uuid[])) AS requested(child_id) ORDER BY child_id"""
CHILDREN_AFTER_LOCK='''SELECT id,org_id,display_name,active,revision FROM kdg_capture.child
WHERE org_id=CAST(:org AS uuid) AND id=ANY(CAST(:children AS uuid[])) ORDER BY id'''
ASSIGNED_AFTER_LOCK='''SELECT ch.id,ch.org_id,ch.display_name,ch.active,ch.revision,
a.id AS assignment_id,a.org_id AS assignment_org_id,a.child_id AS assignment_child_id,
a.account_id AS assignment_account_id,a.membership_id AS assignment_membership_id,
a.active AS assignment_active,a.revision AS assignment_revision
FROM kdg_capture.child ch LEFT JOIN kdg_capture.child_assignment a
ON a.org_id=ch.org_id AND a.child_id=ch.id AND a.account_id=CAST(:account AS uuid)
WHERE ch.org_id=CAST(:org AS uuid) AND ch.id=ANY(CAST(:children AS uuid[])) ORDER BY ch.id'''
VERSION='''SELECT id,org_id,questionnaire_id,display_version,definition FROM kdg_capture.questionnaire_version
WHERE org_id=CAST(:org AS uuid) AND questionnaire_id=CAST(:questionnaire AS uuid)
ORDER BY display_version DESC LIMIT 1'''
BIND_ISSUANCE="""SELECT set_config('app.provision_membership_id', :member, true),
set_config('app.provision_create_permission', :permission, true)"""
ISSUE_BATCH='''INSERT INTO kdg_capture.child_eligibility
(org_id,ref,account_id,membership_id,child_id,child_revision,observed_active,create_permission,assignment_id,assignment_revision,issued_by)
SELECT CAST(:org AS uuid),item.ref,CAST(:account AS uuid),:member,item.child,item.revision,true,:permission,
item.assignment,item.assignment_revision,CAST(:actor AS uuid)
FROM jsonb_to_recordset(CAST(:issues AS jsonb))
AS item(ref text,child uuid,revision bigint,assignment uuid,assignment_revision bigint)
RETURNING ref,child_id,issued_at'''

def _normalize(row):
    return {key:str(value) if isinstance(value,UUID) else value for key,value in dict(row).items()}
def _revision(value):
    if type(value) is not int or not 0<value<=9223372036854775807:raise ValueError('revision')
    return str(value)
def _observation(model,evidence):
    if evidence is None:return None
    return model.model_validate({**evidence.model_dump(mode='json'),'expires_at':evidence.checked_at+timedelta(days=7)})
def _timestamp(value):
    if not isinstance(value,datetime) or value.utcoffset() is None:raise ValueError('timestamp')
    return value.astimezone(timezone.utc).isoformat().replace('+00:00','Z')

def _transaction(conn,budget,context,questionnaire_id,evidence):
    if type(context) is not write.VerifiedContext or context.mode!='own_write':raise write.WriteError('invalid_write_context')
    entry,edit,all_create,assigned=evidence
    permission=create.ALL if all_create else create.ASSIGNED if assigned else None
    parameters=dict(org=context.org_id,account=context.account_id,actor=context.actor_id,
        member=int(entry.membership_id),questionnaire=questionnaire_id,row_limit=MAX_CHILDREN+1)
    try:
        with write.transaction(conn,budget,context):
            if permission is not None:
                # Owner-local evidence binding. Transaction-local settings cannot
                # survive commit/rollback or renew the verified Access observation.
                write.execute(conn,budget,BIND_ISSUANCE,{'member':entry.membership_id,'permission':permission})
            version=create._one(conn,budget,VERSION,parameters)
            questionnaire=None
            if version is not None:
                version=_normalize(version)
                if (version['org_id'],version['questionnaire_id'])!=(context.org_id,questionnaire_id):raise ValueError('foreign_version')
                questionnaire=PublishedQuestionnaire(questionnaire_id=questionnaire_id,
                    questionnaire_version_id=canonical_uuid(version['id']),questionnaire_version=_revision(version['display_version']),
                    definition=parse_definition(json.dumps(version['definition'],allow_nan=False,ensure_ascii=False,separators=(',',':'))))
            children=[]
            if permission:
                rows=write.execute(conn,budget,CHILDREN if all_create else ASSIGNED_CHILDREN,parameters).mappings().all()
                if len(rows)>MAX_CHILDREN:raise ValueError('excess_children')
                ids=[]
                for row in rows:
                    row=_normalize(row)
                    child=canonical_uuid(row['id'])
                    if row['org_id']!=context.org_id or row['active'] is not True or (ids and child<=ids[-1]):raise ValueError('invalid_child_set')
                    ids.append(child)
                if ids:
                    args={**parameters,'children':ids,'permission':permission}
                    locked=write.execute(conn,budget,LOCK_CHILDREN,args).mappings().all()
                    if [canonical_uuid(str(row['child_id'])) for row in locked]!=ids:raise ValueError('incomplete_locks')
                    # This is a separate READ COMMITTED statement after every lock.
                    # It observes changes committed while coordination was awaited.
                    current=write.execute(conn,budget,CHILDREN_AFTER_LOCK if all_create else ASSIGNED_AFTER_LOCK,args).mappings().all()
                    if len(current)!=len(ids):raise ValueError('changed_child_set')
                    planned=[];issues=[]
                    for child,raw in zip(ids,current,strict=True):
                        row=_normalize(raw)
                        if (row['id'],row['org_id'],row['active'])!=(child,context.org_id,True) or row['active'] is not True:raise ValueError('changed_child')
                        revision=_revision(row['revision']);assignment=None
                        if permission==create.ASSIGNED:
                            if (row['assignment_org_id'],row['assignment_child_id'],row['assignment_account_id'],row['assignment_membership_id'])!=(context.org_id,child,context.account_id,int(entry.membership_id)) or type(row['assignment_membership_id']) is not int or row['assignment_active'] is not True:raise ValueError('changed_assignment')
                            assignment=Assignment(assignment_id=canonical_uuid(row['assignment_id']),assignment_revision=_revision(row['assignment_revision']))
                        ref=secrets.token_urlsafe(32)
                        planned.append(dict(child_id=child,child_label=row['display_name'],child_revision=revision,
                            child_eligibility_ref=ref,create_permission=permission,assignment=assignment))
                        issues.append(dict(child=child,ref=ref,revision=int(revision),
                            assignment=assignment.assignment_id if assignment else None,
                            assignment_revision=int(assignment.assignment_revision) if assignment else None))
                    returned=write.execute(conn,budget,ISSUE_BATCH,{**args,'issues':json.dumps(issues,separators=(',',':'),allow_nan=False)}).mappings().all()
                    if len(returned)!=len(planned):raise ValueError('incomplete_issuance')
                    expected={item['ref']:item['child'] for item in issues};issued={}
                    for raw in returned:
                        row=_normalize(raw);ref=row['ref']
                        if ref not in expected or ref in issued or row['child_id']!=expected[ref]:raise ValueError('invalid_issuance')
                        checked=row['issued_at']
                        issued[ref]=(_timestamp(checked),_timestamp(checked+timedelta(days=7)))
                    if len(issued)!=len(planned):raise ValueError('incomplete_issuance')
                    for item in planned:
                        checked,expires=issued[item['child_eligibility_ref']]
                        children.append(Child(**item,checked_at=checked,expires_at=expires))
            state='not_permitted' if permission is None else 'no_published_questionnaire' if questionnaire is None else 'no_eligible_children' if not children else 'ready'
            result=Provision(schema_version=1,org_id=context.org_id,account_id=context.account_id,actor_id=context.actor_id,membership_id=entry.membership_id,
                read_observation=_observation(OwnReadObservation,entry),edit_observation=_observation(OwnEditObservation,edit),
                create_all_observation=_observation(CreateAllObservation,all_create),create_assigned_observation=_observation(CreateAssignedObservation,assigned),
                create_state=state,children=children,questionnaire=questionnaire)
            if len(result.model_dump_json().encode('utf-8'))>MAX_RESPONSE_BYTES:raise ValueError('excess_response')
            budget.remaining()
        budget.remaining()
        return result
    except (ValueError,TypeError,KeyError,RecursionError,OverflowError):
        raise write.WriteError('provision_unavailable') from None

class _Checker(protected.CreateHandler):
    def __init__(self,permission,model,**kwargs):
        super().__init__(**kwargs);self._permissions=(permission,);self._evidence_type=model

class ProvisionHandler(protected.CreateHandler):
    def __init__(self,*,questionnaire_id,**kwargs):
        super().__init__(**kwargs)
        try:self.questionnaire_id=canonical_uuid(questionnaire_id)
        except (ValueError,TypeError):raise RuntimeError('kdg_provision_configuration_invalid') from None
    async def authorize(self,token,budget):
        async def check(permission,model):
            checker=_Checker(permission,model,org_id=self.org_id,access_url=self.access_url,service_key=self._service_key,transport=self._transport)
            try:
                decision=await checker._authorize(token,budget)
            except protected.HandlerError as error:
                if error.status==403 and error.error_id=='access_denied' and permission!=READ:return None
                raise
            # CreateHandler represents a denied create.all check as no decision.
            if decision is None and permission==create.ALL:return None
            return decision
        try:
            async with asyncio.timeout(min(protected.ACCESS_SECONDS,budget.remaining())):
                # Mandatory admission comes first: denial launches no optional work.
                entry=await check(READ,Context)
                try:
                    # Independent capabilities share the original Access deadline.
                    # TaskGroup drains cancellation/failure before any DB admission.
                    async with asyncio.TaskGroup() as group:
                        optional=[group.create_task(check(permission,model)) for permission,model in
                            ((EDIT,EditEvidence),(create.ALL,CreateAllEvidence),(create.ASSIGNED,CreateAssignedEvidence))]
                except* protected.HandlerError as errors:
                    raise errors.exceptions[0] from None
                values=[];observed=None
                for decision in (entry,*(task.result() for task in optional)):
                    if decision is None:
                        values.append(None);continue
                    item,instant=decision
                    if values and (item.account_id,item.actor_id,item.membership_id)!=(values[0].account_id,values[0].actor_id,values[0].membership_id):raise protected.HandlerError(503,'authorization_unavailable')
                    observed=instant if observed is None else min(observed,instant)
                    values.append(item)
                budget.remaining()
                return tuple(values),observed
        except TimeoutError:raise protected.HandlerError(503,'authorization_unavailable') from None
    async def execute(self,conn,authorization):
        budget=write.Budget()
        try:
            if type(authorization) is not str or not re.fullmatch(r'Bearer [A-Za-z0-9\-._~+/]+=*',authorization,flags=re.IGNORECASE):raise protected.HandlerError(401,'authentication_required')
            if conn.in_transaction() or conn.connection.driver_connection.autocommit:raise write.WriteError('invalid_write_context')
            evidence,observed=await self.authorize('Bearer '+authorization.split(' ',1)[1],budget)
            context=write.VerifiedContext(self.org_id,evidence[0].account_id,evidence[0].actor_id,'own_write',observed)
            return await protected._complete_worker(conn,budget,context,self.questionnaire_id,evidence,_transaction)
        except write.WriteError as error:
            code=str(error)
            if code in ('internal_error','operation_verification_unavailable'):code='provision_unavailable'
            raise protected.HandlerError(STATUS.get(code,500),code if code in STATUS else 'internal_error') from None
        except SQLAlchemyError:raise protected.HandlerError(503,'provision_unavailable') from None
