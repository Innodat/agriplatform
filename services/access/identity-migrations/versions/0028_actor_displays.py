"""Retained actor names for a dedicated, selected-ID native reader."""
from alembic import op

revision = 'identity_0028'
down_revision = 'identity_0027'
branch_labels = None
depends_on = None

SQL = r'''
GRANT USAGE ON SCHEMA identity TO identity_actor_display_runtime;
CREATE FUNCTION identity.actor_displays(selected uuid[])
RETURNS TABLE(actor_id uuid, display_name text)
LANGUAGE plpgsql STABLE SECURITY DEFINER
SET search_path = pg_catalog, pg_temp AS $function$
BEGIN
 IF selected IS NULL OR array_ndims(selected) IS DISTINCT FROM 1
    OR cardinality(selected) NOT BETWEEN 1 AND 203
    OR EXISTS(SELECT 1 FROM unnest(selected) id WHERE id IS NULL OR id='00000000-0000-0000-0000-000000000000'::uuid)
    OR (SELECT count(DISTINCT id) FROM unnest(selected) id) <> cardinality(selected) THEN
  RAISE EXCEPTION USING ERRCODE='22023', MESSAGE='identity_actor_display_input_invalid';
 END IF;
 RETURN QUERY SELECT a.id,a.display_name FROM identity.actor a WHERE a.id=ANY(selected);
END;
$function$;
-- The source-bound native RED demonstrated that TEMP + PUBLIC trigger EXECUTE
-- could write an audit row. Installed triggers do not need callers to retain
-- EXECUTE; remove only direct attachment authority on these exact old helpers.
DO $restricted_execute$
DECLARE routine record; granted record; recipient text;
BEGIN
 FOR routine IN SELECT oid,proowner,oid::regprocedure signature FROM pg_proc
 WHERE oid IN ('identity.actor_displays(uuid[])'::regprocedure,
  'identity.log_audit()'::regprocedure,'identity.set_audit_fields()'::regprocedure,
  'identity.handle_new_user()'::regprocedure) LOOP
  IF routine.proowner<>(SELECT oid FROM pg_roles WHERE rolname=current_user) THEN
   RAISE EXCEPTION USING MESSAGE='identity_actor_display_owner_required';
  END IF;
  EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',routine.signature);
  FOR granted IN SELECT DISTINCT x.grantee FROM pg_proc p,
   LATERAL aclexplode(coalesce(p.proacl,acldefault('f',p.proowner))) x
   WHERE p.oid=routine.oid AND x.grantee<>routine.proowner AND x.grantee<>0 LOOP
   recipient:=quote_ident(pg_get_userbyid(granted.grantee));
   EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %s',routine.signature,recipient);
  END LOOP;
 END LOOP;
END;
$restricted_execute$;
GRANT EXECUTE ON FUNCTION identity.actor_displays(uuid[]) TO identity_actor_display_runtime;
'''

def upgrade():
    from identity_baseline import verify_catalog
    from identity_actor_display_catalog import verify_runtime
    connection=op.get_bind()
    verify_catalog(connection,'people_setup')
    verify_runtime(connection, staged=True)
    connection.exec_driver_sql(SQL, execution_options={'no_parameters':True})
    verify_runtime(connection)

def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
