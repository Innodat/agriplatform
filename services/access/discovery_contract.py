"""Closed, bounded discovery observations; never reusable authorization."""
import base64
import re
from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID
from pydantic import Field, field_validator
from capability_contract import Closed

APP_PATTERN=r'^[a-z][a-z0-9_]{1,63}$'
CATALOGUE_LIMIT=128

def cursor_encode(value):return base64.urlsafe_b64encode(str(value).encode('ascii')).decode('ascii').rstrip('=')

def cursor_decode(value):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9_-]{48}',value):raise ValueError('cursor')
    raw=base64.b64decode(value,altchars=b'-_',validate=True).decode('ascii')
    result=UUID(raw)
    if not result.int or str(result)!=raw or cursor_encode(result)!=value:raise ValueError('cursor')
    return result

class DiscoveryOrganization(Closed):
    org_id: UUID
    name: str
    membership_id: Annotated[str,Field(pattern=r'^[1-9][0-9]{0,18}$')]

class OrganizationsDiscovery(Closed):
    organizations: Annotated[list[DiscoveryOrganization],Field(max_length=100)]
    next_cursor: str | None

class DiscoveryApplication(Closed):
    app_id: Annotated[str,Field(pattern=APP_PATTERN)]
    eligible_scope_kinds: Annotated[list[Literal['account','organization']],Field(min_length=1,max_length=2)]
    @field_validator('eligible_scope_kinds')
    @classmethod
    def canonical(cls,value):
        if value not in (['account'],['organization'],['account','organization']):raise ValueError('scope')
        return value

class ApplicationsDiscovery(Closed):
    applications: Annotated[list[DiscoveryApplication],Field(max_length=CATALOGUE_LIMIT)]
    checked_at: datetime

class DiscoveryError(Closed):
    error_id: Literal['authentication_required','service_access_denied','access_denied','validation_failed','authorization_unavailable','internal_error']
    error: str='Request could not be completed'
    details: Closed=Field(default_factory=Closed)

def query(request,applications):
    fields={}
    allowed=set() if applications else {'application','cursor','page_size'}
    for key,value in request.query_params.multi_items():
        if key not in allowed or key in fields:raise ValueError('query')
        fields[key]=value
    if applications:return None,None,None
    app=fields.get('application')
    if not isinstance(app,str) or not re.fullmatch(APP_PATTERN,app) or app not in ('leave','reference'):raise ValueError('application')
    size=fields.get('page_size','100')
    if not re.fullmatch(r'[1-9][0-9]{0,2}',size) or int(size)>100:raise ValueError('size')
    after=cursor_decode(fields['cursor']) if 'cursor' in fields else None
    return app,after,int(size)
