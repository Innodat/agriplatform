"""SELECT-only independent retained Studies inspection. Prints no credentials."""
import json
from pathlib import Path
import psycopg
from sqlalchemy.engine import make_url
if not __debug__:
 raise RuntimeError('studies_inspection_optimized_python_prohibited')

def main():
 ROOT=Path(__file__).resolve().parents[3]
 BASE=ROOT/'platform/deployment/.local/identity-baseline'
 old=BASE/'organization-check-reviewed3-20261022'
 frame=BASE/'studies-enrollment-final-20261023'
 assert json.loads((old/'run.json').read_text())['run_id']=='99b7231c-0a5b-4bdb-98e8-3329564c526a'
 url=make_url(json.loads((old/'credentials.json').read_text())['databases']['bridge'])
 assert url.host in ('localhost','127.0.0.1') and url.port==55482 and not url.query
 private=json.loads((frame/'private.json').read_text())
 account=json.loads((frame/'provider.json').read_text())['account']
 name=private['databases']['upgrade']
 assert name.startswith('ida_99b7231c0a5b_studies_')
 with psycopg.connect(url.set(username='supabase_admin',database=name).render_as_string(hide_password=False),connect_timeout=3) as conn:
  with conn.cursor() as c:
   c.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
   c.execute("SET LOCAL statement_timeout='2s'")
   c.execute('SELECT version_num FROM identity.alembic_version');assert c.fetchone()==('identity_0021',)
   c.execute('SELECT version_num FROM access.alembic_version');assert c.fetchone()==('access_0016',)
   c.execute('SELECT count(*) FROM identity.org_member WHERE user_id=%s',(account,));assert c.fetchone()==(0,)
   c.execute("SELECT count(*) FROM access.studies_runtime_principal p JOIN identity.studies_runtime_principal i ON i.executor_actor_id=p.executor_actor_id JOIN identity.actor a ON a.id=p.executor_actor_id WHERE a.kind='service' AND a.actor_key IS NOT NULL");assert c.fetchone()==(1,)
   c.execute('SELECT count(*) FROM access.studies_enrollment_outcome o JOIN access.studies_account_grant g USING(account_id) WHERE o.actor_id<>g.actor_id OR o.initiator_actor_id<>g.actor_id');assert c.fetchone()==(0,)
   c.execute('SELECT count(*) FROM access.studies_assignment_event e JOIN access.studies_enrollment_outcome o USING(database_login,account_id,command_version,operation_id) WHERE e.actor_id<>o.actor_id OR e.executor_actor_id<>o.executor_actor_id OR e.initiator_actor_id<>o.initiator_actor_id');assert c.fetchone()==(0,)
   c.execute('SELECT count(*) FROM (SELECT account_id FROM access.studies_assignment_event GROUP BY account_id HAVING count(*)>1) d');assert c.fetchone()==(0,)
   c.execute("SELECT count(*) FROM pg_class t JOIN pg_namespace n ON n.oid=t.relnamespace WHERE n.nspname IN ('identity','access') AND t.relname LIKE 'studies_%' AND t.relkind='r' AND NOT(t.relrowsecurity AND t.relforcerowsecurity)");assert c.fetchone()==(0,)
   c.execute("SELECT count(*) FROM pg_class t JOIN pg_namespace n ON n.oid=t.relnamespace CROSS JOIN (VALUES ('access_studies_runtime'),('identity_studies_reader_runtime'),('identity_studies_setup_runtime')) roles(name) WHERE n.nspname IN ('identity','access') AND t.relkind='r' AND (has_table_privilege(roles.name,t.oid,'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') OR has_any_column_privilege(roles.name,t.oid,'INSERT,UPDATE,REFERENCES'))");assert c.fetchone()==(0,)
   c.execute('SELECT count(*) FROM access.studies_account_grant');grants=c.fetchone()[0]
   c.execute('SELECT count(*) FROM access.studies_assignment_event');events=c.fetchone()[0]
   c.execute('SELECT count(*) FROM access.studies_enrollment_outcome');outcomes=c.fetchone()[0]
   print(json.dumps({'status':'passed','zero_memberships':True,'grants':grants,'events':events,'outcomes':outcomes,'runtime_table_writes':False,'read_only':True}))

if __name__=='__main__':
 try:main()
 except Exception:
  print('studies_retained_inspection_failed',file=__import__('sys').stderr)
  raise SystemExit(1) from None
