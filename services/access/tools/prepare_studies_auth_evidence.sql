-- Separate Auth-owner preparation before controlled Identity21 migration.
-- Required provider columns must already exist. This never alters provider schema.
BEGIN;
GRANT USAGE ON SCHEMA auth TO identity_studies_owner;
GRANT SELECT(id,deleted_at,email_confirmed_at,banned_until,is_anonymous)
 ON auth.users TO identity_studies_owner;
CREATE POLICY studies_current_account ON auth.users FOR SELECT TO identity_studies_owner
 USING(id::text=current_setting('app.account_id',true));
COMMIT;
