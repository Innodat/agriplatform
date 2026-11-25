"""Read-only E1 preparation; D1 owns draft persistence and scope summaries."""
from datetime import datetime,timezone
from dataclasses import dataclass
import time
from typing import Annotated,Literal
from pydantic import Field,field_validator
from contracts import Closed,identifier
from access_client import Failure

class Editable(Closed):status:Literal['editable']
class ReadOnly(Closed):
    status:Literal['read_only']
    reason:Literal['permission_missing','employment_ended','employment_periods_missing']
class Notice(Closed):code:Literal['work_timezone_missing','work_timezone_invalid']
class ContextScope(Closed):
    org_id:str
    @field_validator('org_id')
    @classmethod
    def ids(cls,value):return identifier(value)
class Ready(ContextScope):
    status:Literal['ready']
    employment_id:str
    editability:Annotated[Editable|ReadOnly,Field(discriminator='status')]
    setup_notices:list[Notice]
    @field_validator('employment_id')
    @classmethod
    def employment(cls,value):return identifier(value)
class Setup(ContextScope):
    status:Literal['setup_required']
    reason:Literal['employment_missing','identity_person_link_required','identity_actor_setup_required']
Context=Annotated[Ready|Setup,Field(discriminator='status')]

@dataclass(frozen=True,repr=False)
class Prepared:
    public:Ready|Setup
    authority:object=None
    observation:dict|None=None
    timezone:object=None
    observed_at:float|None=None

async def prepare(access,people,configuration,authorization,org,budget,clock,*,retain=False):
    observed_at=time.monotonic()
    def result(public,authority=None,observation=None,timezone=None):
        return Prepared(public,authority,observation,timezone,observed_at) if retain else public
    try:context=await access.own(authorization,org,budget)
    except Failure as e:
        if e.status==409 and e.error_id in ('identity.person_link_required','identity.actor_setup_required'):return result(Setup(status='setup_required',org_id=org,reason=e.error_id.replace('.','_')))
        raise
    if people is None:raise Failure(503,'dependency_unavailable')
    decision=context.decision
    discovery=await people.read(authorization,org,decision.person_id,budget)
    if discovery['status']=='not_found':return result(Setup(status='setup_required',org_id=org,reason='employment_missing'))
    employment=discovery['employment_id'];notices=[];observation=None;shared=discovery
    if not context.manage:editability=ReadOnly(status='read_only',reason='permission_missing')
    elif not discovery['has_periods']:editability=ReadOnly(status='read_only',reason='employment_periods_missing')
    else:
        if configuration is None:raise Failure(503,'dependency_unavailable')
        now=clock()
        if not isinstance(now,datetime) or now.tzinfo is None:raise Failure(503,'dependency_unavailable')
        observation=await configuration.timezone(context,employment,budget,now.astimezone(timezone.utc))
        editability=Editable(status='editable')
        if observation.notice:notices=[Notice(code=observation.notice)]
        if observation.zone is not None:
            from zoneinfo import ZoneInfo
            as_of=now.astimezone(ZoneInfo(observation.zone)).date().isoformat()
            effective=await people.read(authorization,org,decision.person_id,budget,employment,as_of)
            shared=effective
            if effective['status']!='effective':raise Failure(503,'dependency_unavailable')
            if effective['employment_state']=='ended':editability=ReadOnly(status='read_only',reason='employment_ended')
            elif effective['employment_state']=='setup_required':editability=ReadOnly(status='read_only',reason='employment_periods_missing')
    budget.remaining()
    return result(Ready(status='ready',org_id=org,employment_id=employment,editability=editability,setup_notices=notices),context,shared,observation)
