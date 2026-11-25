"""Leave-owned timezone chain, selected by retained UTC applicability intervals."""
import asyncio,time
from dataclasses import dataclass
from datetime import datetime,timezone,timedelta,time as local_time
from zoneinfo import ZoneInfo
import psycopg
from psycopg.rows import dict_row
from runtime_database import validated_url
from access_client import Failure

@dataclass(frozen=True,repr=False)
class TimezoneObservation:
    zone:str|None
    notice:str|None
    evidence:dict

@dataclass(frozen=True,repr=False)
class DatedWindow:
    valid_until:datetime
    zone:str
    as_of_date:str

    def check(self,clock,deadline):
        """The already selected local timeout includes all remaining work/COMMIT.

        Reject an interval that can reach a date/source boundary instead of relying
        on the duration of the next SQL statement or shortening the agreed timeout.
        """
        from drafts import DraftFailure
        # Sample elapsed time first: clock evaluation may itself take time, so
        # this ordering overestimates rather than shortens the wall-clock horizon.
        remaining=deadline-time.monotonic()
        now=clock()
        if not isinstance(now,datetime) or now.tzinfo is None:raise DraftFailure(503,'dependency_unavailable')
        if remaining<=0:raise DraftFailure(503,'leave.draft_preparation_changed')
        horizon=now+timedelta(seconds=remaining)
        zone=ZoneInfo(self.zone);local=now.astimezone(zone);end=horizon.astimezone(zone)
        if (horizon>=self.valid_until or local.date().isoformat()!=self.as_of_date
                or end.date().isoformat()!=self.as_of_date or local.utcoffset()!=end.utcoffset()):
            raise DraftFailure(503,'leave.draft_preparation_changed')

def resolve(row,org,employment,now):
    missing=lambda:TimezoneObservation(None,'work_timezone_missing',{})
    invalid=lambda:TimezoneObservation(None,'work_timezone_invalid',{})
    if not row:return missing()
    assignment=row.get('assignment');settings=row.get('settings');profile=row.get('profile');version=row.get('version')
    for value in (settings,assignment,profile,version):
        if value is not None and value['org_id']!=org:return invalid()
    if assignment is not None and assignment['employment_id']!=employment:return invalid()
    selected=assignment['profile_id'] if assignment and assignment['profile_id'] is not None else settings['default_profile_id'] if settings else None
    if selected is None:return missing()
    if profile is None or profile['id']!=selected or profile['archived_at'] is not None:return invalid()
    if version is None:return missing()
    if version['profile_id']!=selected:return invalid()
    # The database selects by UTC, and these checks retain that noncircular basis.
    from datetime import datetime
    def stamp(v):return datetime.fromisoformat(v.replace('Z','+00:00'))
    for value in (assignment,version):
        if value is not None and not(stamp(value['effective_from'])<=now and (value['effective_until'] is None or now<stamp(value['effective_until']))):return invalid()
    zone=assignment['timezone_override'] if assignment and assignment['timezone_override'] is not None else version['work_timezone']
    if zone is None:return missing()
    try:
        if type(zone) is not str or not zone or len(zone)>255 or zone in ('localtime','posixrules') or zone.startswith(('/',':','posix/','right/')):raise ValueError()
        ZoneInfo(zone)
    except (ValueError,KeyError):return invalid()
    return TimezoneObservation(zone,None,{'settings':settings,'assignment':assignment,'profile':profile,'version':version,'resolved_at':now.isoformat()})

class ConfigurationRepository:
    def __init__(self,url):self.url=validated_url(url).set(drivername='postgresql').render_as_string(hide_password=False)
    def __repr__(self):return '<LeaveConfigurationRepository private>'
    async def timezone(self,context,employment,budget,now):
        conn=None;expiry=None
        try:
            async with asyncio.timeout_at(budget.deadline):
                conn=await psycopg.AsyncConnection.connect(self.url,connect_timeout=max(1,min(3,int(budget.remaining()))),row_factory=dict_row)
                expiry=asyncio.get_running_loop().call_at(budget.deadline,conn.pgconn.finish)
                async with conn.transaction():
                    await conn.execute('SET TRANSACTION READ ONLY')
                    await conn.execute("SELECT set_config('transaction_timeout',%s,true),set_config('statement_timeout',%s,true),set_config('lock_timeout',%s,true),set_config('app.org_id',%s,true),set_config('app.actor_id',%s,true),set_config('app.employment_id',%s,true),set_config('app.mode','own_read',true)",(str(budget.milliseconds(2)),str(budget.milliseconds(2)),str(budget.milliseconds(1)),context.decision.authorization_scope.org_id,context.decision.actor_id,employment))
                    # One statement/snapshot covers default, explicit assignment,
                    # profile and applicable version; no external HTTP in this scope.
                    cursor=await conn.execute('''SELECT to_jsonb(s) settings,to_jsonb(a) assignment,to_jsonb(p) profile,to_jsonb(v) version
                        FROM (SELECT %s::uuid org_id) o
                        LEFT JOIN leave.organization_settings s ON s.org_id=o.org_id
                        LEFT JOIN leave.employment_settings a ON a.org_id=o.org_id AND a.employment_id=%s::uuid AND a.effective_from<=%s AND (a.effective_until IS NULL OR %s<a.effective_until)
                        LEFT JOIN leave.work_profile p ON p.org_id=o.org_id AND p.id=coalesce(a.profile_id,s.default_profile_id)
                        LEFT JOIN leave.work_profile_version v ON v.org_id=p.org_id AND v.profile_id=p.id AND v.effective_from<=%s AND (v.effective_until IS NULL OR %s<v.effective_until)''',(context.decision.authorization_scope.org_id,employment,now,now,now,now))
                    rows=await cursor.fetchall()
                    if len(rows)!=1:raise ValueError()
                budget.remaining()
                return resolve(rows[0],context.decision.authorization_scope.org_id,employment,now)
        except asyncio.CancelledError:raise
        except Exception:raise Failure(503,'dependency_unavailable') from None
        finally:
            if expiry is not None:expiry.cancel()
            if conn is not None:
                conn.pgconn.finish()
                try:
                    async with asyncio.timeout(.1):await conn.close()
                except BaseException:pass

    async def guard(self,conn,prepared,budget,clock,deadline):
        """Protect and revalidate only a dated interpretation, including absent rows."""
        from drafts import DraftFailure
        from zoneinfo import ZoneInfo
        org=prepared.public.org_id;employment=prepared.public.employment_id
        await conn.execute("SELECT pg_advisory_xact_lock_shared(hashtextextended('leave.timezone.configuration',0))")
        # Lock acquisition may cross midnight/applicability. Select with a fresh
        # clock, then refresh again after the awaited statement before accepting it.
        now=clock()
        row=await (await conn.execute('''SELECT to_jsonb(s) settings,to_jsonb(a) assignment,to_jsonb(p) profile,to_jsonb(v) version,
          (SELECT min(boundary) FROM (
            SELECT effective_from boundary FROM leave.employment_settings WHERE org_id=o.org_id AND employment_id=%s::uuid AND effective_from>%s
            UNION ALL SELECT effective_until FROM leave.employment_settings WHERE org_id=o.org_id AND employment_id=%s::uuid AND effective_until>%s
            UNION ALL SELECT effective_from FROM leave.work_profile_version WHERE org_id=o.org_id AND profile_id=p.id AND effective_from>%s
            UNION ALL SELECT effective_until FROM leave.work_profile_version WHERE org_id=o.org_id AND profile_id=p.id AND effective_until>%s
          ) transitions) next_boundary
          FROM (SELECT %s::uuid org_id) o
          LEFT JOIN leave.organization_settings s ON s.org_id=o.org_id
          LEFT JOIN leave.employment_settings a ON a.org_id=o.org_id AND a.employment_id=%s::uuid AND a.effective_from<=%s AND (a.effective_until IS NULL OR %s<a.effective_until)
          LEFT JOIN leave.work_profile p ON p.org_id=o.org_id AND p.id=coalesce(a.profile_id,s.default_profile_id)
          LEFT JOIN leave.work_profile_version v ON v.org_id=p.org_id AND v.profile_id=p.id AND v.effective_from<=%s AND (v.effective_until IS NULL OR %s<v.effective_until)''',(employment,now,employment,now,now,now,org,employment,now,now,now,now))).fetchall()
        now=clock()
        current=resolve(row[0],org,employment,now) if len(row)==1 else None
        original=prepared.timezone
        if current is None or current.zone!=original.zone or {k:v for k,v in current.evidence.items() if k!='resolved_at'}!={k:v for k,v in original.evidence.items() if k!='resolved_at'} or now.astimezone(ZoneInfo(original.zone)).date().isoformat()!=prepared.observation['as_of_date']:
            raise DraftFailure(503,'leave.draft_preparation_changed')
        local=now.astimezone(ZoneInfo(original.zone))
        midnight=datetime.combine(local.date()+timedelta(days=1),local_time.min,tzinfo=ZoneInfo(original.zone)).astimezone(timezone.utc)
        boundary=row[0]['next_boundary']
        window=DatedWindow(min(midnight,boundary) if boundary is not None else midnight,original.zone,prepared.observation['as_of_date'])
        window.check(clock,deadline)
        return window
