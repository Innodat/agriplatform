"""Narrow Studies-only migration helpers; no runtime provisioning authority."""
from sqlalchemy import text

ROLES={
 'identity':('identity_studies_owner','identity_studies_reader_runtime','identity_studies_setup_runtime'),
 'access':('access_studies_owner','access_studies_runtime'),
}
def verify_roles(connection,owner):
    migrator=owner+'_migrator'
    for role in ROLES[owner]:
        row=connection.execute(text('SELECT rolsuper,rolinherit,rolcreaterole,rolcreatedb,rolcanlogin,rolreplication,rolbypassrls FROM pg_roles WHERE rolname=:role'),{'role':role}).one_or_none()
        if row is None or tuple(row)!=(False,False,False,False,role.endswith('_runtime'),False,False):
            raise RuntimeError('studies_role_prerequisite_missing_or_unsafe')
        edges=connection.execute(text("SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),admin_option,coalesce(to_jsonb(m)->>'inherit_option','false'),coalesce(to_jsonb(m)->>'set_option','true') FROM pg_auth_members m WHERE roleid=(SELECT oid FROM pg_roles WHERE rolname=:role) OR member=(SELECT oid FROM pg_roles WHERE rolname=:role)"),{'role':role}).all()
        expected=[(role,migrator,False,'false','true')] if role.endswith('_owner') else []
        if [tuple(row) for row in edges]!=expected:raise RuntimeError('studies_role_membership_unsafe')

def strip_acl(connection,schema,routines):
    for routine in routines:
        objects=connection.execute(text("SELECT p.oid::regprocedure::text,CASE WHEN a.grantee=0 THEN NULL ELSE pg_get_userbyid(a.grantee) END FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace CROSS JOIN LATERAL aclexplode(coalesce(p.proacl,acldefault('f',p.proowner))) a WHERE n.nspname=:schema AND p.proname=:routine AND a.grantee<>p.proowner"),{'schema':schema,'routine':routine}).all()
        for signature,role in objects:
            # Identifiers originate in pg_catalog; quote every identifier.
            target='PUBLIC' if role is None else '"'+role.replace('"','""')+'"'
            connection.exec_driver_sql('REVOKE ALL ON FUNCTION '+signature+' FROM '+target)

def secure_tables(connection,schema,tables,owner,guard):
    for table in tables:
        objects=connection.execute(text("SELECT CASE WHEN a.grantee=0 THEN NULL ELSE pg_get_userbyid(a.grantee) END FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace CROSS JOIN LATERAL aclexplode(coalesce(c.relacl,acldefault('r',c.relowner))) a WHERE n.nspname=:schema AND c.relname=:table AND a.grantee<>c.relowner"),{'schema':schema,'table':table}).scalars()
        for role in objects:
            target='PUBLIC' if role is None else '"'+role.replace('"','""')+'"'
            connection.exec_driver_sql('REVOKE ALL ON '+schema+'.'+table+' FROM '+target)
        connection.exec_driver_sql('ALTER TABLE '+schema+'.'+table+' ENABLE ROW LEVEL SECURITY')
        connection.exec_driver_sql('ALTER TABLE '+schema+'.'+table+' FORCE ROW LEVEL SECURITY')
        connection.exec_driver_sql('CREATE POLICY migration_owner ON '+schema+'.'+table+' TO '+schema+'_migrator USING(true) WITH CHECK(true)')
        if not table.endswith('_principal'):
            connection.exec_driver_sql('CREATE TRIGGER studies_immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON '+schema+'.'+table+' FOR EACH STATEMENT EXECUTE FUNCTION '+schema+'.'+guard+'()')

def transfer_functions(connection,schema,owner,signatures):
    connection.exec_driver_sql('GRANT CREATE ON SCHEMA '+schema+' TO '+owner)
    for signature in signatures:connection.exec_driver_sql('ALTER FUNCTION '+schema+'.'+signature+' OWNER TO '+owner)
    connection.exec_driver_sql('REVOKE CREATE ON SCHEMA '+schema+' FROM '+owner)
