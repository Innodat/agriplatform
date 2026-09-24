-- Identity-owner integration, run explicitly after legacy identity migrations.
-- Restricts both current actor and selected organization, never trusts JWT role claims.
GRANT USAGE ON SCHEMA identity TO access_runtime;
GRANT SELECT (id,deleted_at) ON identity.org TO access_runtime;
GRANT SELECT (user_id,org_id,deleted_at) ON identity.org_member TO access_runtime;
CREATE POLICY access_current_org ON identity.org FOR SELECT TO access_runtime
USING (id::text = current_setting('app.org_id',true));
CREATE POLICY access_current_member ON identity.org_member FOR SELECT TO access_runtime
USING (org_id::text = current_setting('app.org_id',true) AND user_id::text = current_setting('app.actor_id',true));
