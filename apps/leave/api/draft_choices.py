"""Scoped published choice metadata; one snapshot, no policy/date interpretation."""
import asyncio,base64,json,re,unicodedata
from typing import Annotated,Literal
import psycopg
from psycopg.rows import dict_row
from pydantic import Field,field_validator
from contracts import Closed,identifier,json_object
from access_client import Failure
from runtime_database import validated_url
Mode=Literal['full_days','half_day','hours']
MODES=('full_days','half_day','hours')
# Python str.strip/isspace defines configuration boundary whitespace; FEFF is a
# valid format character. Other layers must preserve the same Unicode semantics.
def name(value):
    if type(value) is not str or not 1<=len(value)<=120 or value!=value.strip() or any(unicodedata.category(c) in ('Cc','Cs') for c in value):raise ValueError('name')
    return value
def configuration_name(value):return name(value.strip())
class Choice(Closed):
    type_id:str
    version_id:str
    name:str
    revision:Annotated[str,Field(strict=True,pattern=r'^[1-9][0-9]{0,18}$')]
    permitted_modes:list[Mode]=Field(min_length=1,max_length=3)
    @field_validator('type_id','version_id')
    @classmethod
    def ids(cls,value):return identifier(value)
    @field_validator('name')
    @classmethod
    def text(cls,value):return name(value)
    @field_validator('revision')
    @classmethod
    def counter(cls,value):
        if int(value)>9223372036854775807:raise ValueError('revision')
        return value
    @field_validator('permitted_modes')
    @classmethod
    def modes(cls,value):
        if len(value)!=len(set(value)):raise ValueError('modes')
        return value
class NotRequested(Closed):status:Literal['not_requested']
class Obsolete(Closed):status:Literal['obsolete']
class Available(Closed):
    status:Literal['available']
    choice:Choice
class Choices(Closed):
    choices:list[Choice]=Field(max_length=100)
    next_cursor:str|None
    selected:Annotated[NotRequested|Obsolete|Available,Field(discriminator='status')]
def encode_cursor(org,last):
    value={'version':1,'org_id':identifier(org),'after':identifier(last)}
    return base64.urlsafe_b64encode(json.dumps(value,separators=(',',':'),sort_keys=True).encode()).decode().rstrip('=')
def decode_cursor(value,org):
    if type(value) is not str or not re.fullmatch(r'[A-Za-z0-9_-]{1,256}',value):raise ValueError('cursor')
    raw=base64.b64decode(value+'='*((-len(value))%4),altchars=b'-_',validate=True);parsed=json_object(raw)
    if set(parsed)!={'version','org_id','after'} or type(parsed['version']) is not int or parsed['version']!=1 or parsed['org_id']!=org:raise ValueError('cursor')
    after=identifier(parsed['after'])
    if encode_cursor(org,after)!=value:raise ValueError('cursor')
    return after
def choice(row,org):
    if str(row['org_id'])!=org or row['archived_at'] is not None or row['choice_version_id'] is None or str(row['choice_version_id'])!=str(row['version_id']) or row['published_at'] is None:raise ValueError('configuration')
    return Choice(type_id=str(row['id']),version_id=str(row['version_id']),name=row['name'],revision=str(row['revision']),permitted_modes=row['permitted_modes'])
def resolve_rows(rows,selected,org,selected_id):
    offered=[choice(row,org) for row in rows]
    if any(a.type_id>=b.type_id for a,b in zip(offered,offered[1:])):raise ValueError('order')
    result=NotRequested(status='not_requested') if selected_id is None else Obsolete(status='obsolete')
    if selected is not None and str(selected['org_id'])!=org:raise ValueError('scope')
    if selected is not None and selected['archived_at'] is None and selected['choice_version_id'] is not None:
        resolved=choice(selected,org)
        if resolved.type_id!=selected_id:raise ValueError('selection')
        result=Available(status='available',choice=resolved)
    return Choices(choices=offered[:100],next_cursor=encode_cursor(org,offered[99].type_id) if len(offered)>100 else None,selected=result)
class ChoicesRepository:
    def __init__(self,url):self.url=validated_url(url).set(drivername='postgresql').render_as_string(hide_password=False)
    def __repr__(self):return '<LeaveChoicesRepository private>'
    async def choices(self,context,org,selected,after,budget):
        connection=None;expiry=None
        try:
            async with asyncio.timeout_at(budget.deadline):
                connection=await psycopg.AsyncConnection.connect(self.url,connect_timeout=max(1,min(3,int(budget.remaining()))),row_factory=dict_row)
                expiry=asyncio.get_running_loop().call_at(budget.deadline,connection.pgconn.finish)
                async with connection.transaction():
                    await connection.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
                    await connection.execute("SELECT set_config('transaction_timeout',%s,true),set_config('statement_timeout',%s,true),set_config('lock_timeout',%s,true),set_config('app.org_id',%s,true),set_config('app.actor_id',%s,true),set_config('app.mode','own_read',true)",(str(budget.milliseconds(2)),str(budget.milliseconds(2)),str(budget.milliseconds(1)),org,context.decision.actor_id))
                    sql='''SELECT t.id,t.org_id,t.archived_at,t.choice_version_id,t.revision,v.id version_id,v.name,v.permitted_modes,v.published_at FROM leave.leave_type t LEFT JOIN leave.leave_type_version v ON v.org_id=t.org_id AND v.leave_type_id=t.id AND v.id=t.choice_version_id WHERE t.org_id=%s::uuid'''
                    cursor=await connection.execute(sql+''' AND t.archived_at IS NULL AND t.choice_version_id IS NOT NULL AND (%s::uuid IS NULL OR t.id>%s::uuid) ORDER BY t.id LIMIT 101''',(org,after,after));rows=await cursor.fetchall()
                    selected_row=None
                    if selected:
                        cursor=await connection.execute(sql+' AND t.id=%s::uuid',(org,selected));selected_row=await cursor.fetchone()
                    result=resolve_rows(rows,selected_row,org,selected)
                budget.remaining();return result
        except asyncio.CancelledError:raise
        except Exception:raise Failure(503,'dependency_unavailable') from None
        finally:
            if expiry is not None:expiry.cancel()
            if connection is not None:
                connection.pgconn.finish()
                try:
                    async with asyncio.timeout(.1):await connection.close()
                except BaseException:pass
