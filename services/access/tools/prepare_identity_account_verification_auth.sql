-- Separate restricted Auth-owner preparation, before controlled Identity upgrade.
-- Existing policy names refuse; this is not runtime or startup work.
BEGIN;
GRANT USAGE ON SCHEMA auth TO identity_account_verification_owner;
GRANT SELECT(id,deleted_at) ON auth.users TO identity_account_verification_owner;
CREATE POLICY identity_account_actor_verification ON auth.users FOR SELECT
 TO identity_account_verification_owner USING(true);
COMMIT;
