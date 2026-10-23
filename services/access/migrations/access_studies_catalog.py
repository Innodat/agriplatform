"""Ordinary Studies role/table guards alongside native behavioral qualification."""
from sqlalchemy import text
from access_baseline import BaselineError
from studies_migration_support import verify_roles
TABLES=('studies_runtime_principal','studies_account_grant','studies_enrollment_outcome','studies_assignment_event')
TABLE_NAMES=(*TABLES,*(name+'_pkey' for name in TABLES),'studies_assignment_event_account_id_key')
FUNCTION_NAMES=('studies_registration_ready','studies_executor','studies_evidence_immutable','guard_studies_principal','guard_studies_grant','enroll_studies_account','check_studies_permission')
def verify_extension(connection):
    verify_roles(connection,'access')
    for table in TABLES:
        row=connection.execute(text("SELECT pg_get_userbyid(relowner),relrowsecurity,relforcerowsecurity FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' AND relname=:table"),{'table':table}).one_or_none()
        if row is None or tuple(row)!=('access_migrator',True,True):raise BaselineError('access_studies_table_unsafe')
        if connection.execute(text("SELECT has_table_privilege('access_studies_runtime',(SELECT c.oid FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' AND c.relname=:table),'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') OR has_any_column_privilege('access_studies_runtime',(SELECT c.oid FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' AND c.relname=:table),'SELECT,INSERT,UPDATE,REFERENCES')"),{'table':table}).scalar_one():
            raise BaselineError('access_studies_runtime_privileges_unsafe')
    for signature in ('enroll_studies_account(uuid,uuid)','check_studies_permission(uuid)'):
        if not connection.execute(text("SELECT has_function_privilege('access_studies_runtime',(SELECT p.oid FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname=:signature),'EXECUTE')"),{'signature':signature.split('(')[0]}).scalar_one():raise BaselineError('access_studies_runtime_privileges_unsafe')
