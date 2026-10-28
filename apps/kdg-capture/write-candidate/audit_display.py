"""Closed aggregate and one-original-Budget composition, without storage ownership changes."""
import asyncio
import time
from typing import Annotated, Literal
from pydantic import Field
import audit_http as source
import audit_read as audit
from identity_actor_display import Label, FINAL_SECONDS, FINAL_RESERVE

MAX_RESPONSE_BYTES=321*1024

class LoadedDisplays(audit.read.Closed):
    status: Literal['loaded']
    labels: Annotated[list[Label],Field(min_length=1,max_length=203)]

class UnavailableDisplays(audit.read.Closed):
    status: Literal['temporarily_unavailable']

class AuditDetails(audit.read.Closed):
    audit: audit.AuditPage
    actor_display: Annotated[LoadedDisplays|UnavailableDisplays,Field(discriminator='status')]


def selected_actor_ids(page):
    actors={page.owner_actor_id,page.created_by,page.updated_by}
    for event in page.events:
        actors.add(event.executor_actor_id)
        if event.initiator_actor_id is not None:actors.add(event.initiator_actor_id)
    return tuple(sorted(actors))


def _binding(evidence):
    # checked_at is a fresh observation, not part of the authority identity.
    return evidence.model_dump(include={'account_id','actor_id','membership_id','permission','authorization_scope','resource_scope'})


async def compose(authority,engine,identity,token,org_id,query,budget):
    evidence,observed_at=await authority._authorize(token,budget)
    context=audit.write.VerifiedContext(org_id,evidence.account_id,evidence.actor_id,'all_read',observed_at)
    audit.position(query,context)
    page=await audit.protected._complete_worker(engine,budget,context,query,evidence,source._acquired_transaction)
    page=audit.AuditPage.model_validate(page)
    if len(page.model_dump_json().encode('utf-8'))>audit.MAX_RESPONSE_BYTES:raise audit.write.WriteError('capture_read_unavailable')
    budget.remaining()
    labels=await identity.lookup(org_id,selected_actor_ids(page),budget)
    budget.remaining()
    final_deadline=min(time.monotonic()+FINAL_SECONDS,budget.deadline-FINAL_RESERVE)
    if final_deadline<=time.monotonic():raise audit.write.WriteError('execution_timeout')
    try:
        async with asyncio.timeout_at(final_deadline):
            final,_=await authority._authorize(token,budget)
    except TimeoutError:raise audit.protected.HandlerError(503,'authorization_unavailable') from None
    if _binding(final)!=_binding(evidence):raise audit.protected.HandlerError(503,'authorization_observation_expired')
    budget.remaining()
    displays=UnavailableDisplays(status='temporarily_unavailable') if labels is None else LoadedDisplays(status='loaded',labels=labels)
    return AuditDetails(audit=page,actor_display=displays)
