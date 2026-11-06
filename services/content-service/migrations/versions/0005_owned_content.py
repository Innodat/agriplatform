"""Add typed ownership alongside unchanged legacy objects and event history."""
from alembic import op
revision='content_0005'
down_revision='content_0004'
branch_labels=None
depends_on=None


def upgrade():
    op.execute('''
    CREATE POLICY adoption_inventory_objects ON content.objects FOR SELECT TO content_migrator USING(true);
    CREATE POLICY adoption_inventory_events ON content.events FOR SELECT TO content_migrator USING(true);
    CREATE TABLE content.owned_objects(
      id text PRIMARY KEY, application_id text NOT NULL CHECK(application_id ~ '^[a-z][a-z0-9-]{0,62}$'),
      scope_kind text NOT NULL,org_id uuid,account_id uuid,
      sha256 text NOT NULL CHECK(sha256 ~ '^[a-f0-9]{64}$'),size bigint NOT NULL CHECK(size>0 AND size<=134217728),
      media_type text NOT NULL CHECK(media_type IN ('application/pdf','image/jpeg','image/png','text/plain','application/xml','text/html','application/json','application/octet-stream')),
      state text NOT NULL DEFAULT 'pending' CHECK(state IN ('pending','finalizing','ready','failed')),
      claim_id uuid,provider_bucket text,provider_key text,provider_version text,provider_etag text,
      created_at timestamptz NOT NULL DEFAULT clock_timestamp(),created_by uuid NOT NULL DEFAULT current_setting('app.actor_id')::uuid,
      updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),updated_by uuid NOT NULL DEFAULT current_setting('app.actor_id')::uuid,
      initiator_actor_id uuid,initiator_account_id uuid,
      CHECK((scope_kind='application' AND org_id IS NULL AND account_id IS NULL) OR
            (scope_kind='organization' AND org_id IS NOT NULL AND account_id IS NULL) OR
            (scope_kind='account' AND org_id IS NULL AND account_id IS NOT NULL)),
      CHECK((initiator_actor_id IS NULL)=(initiator_account_id IS NULL)),
      CHECK(state<>'finalizing' OR claim_id IS NOT NULL),
      CHECK(state<>'ready' OR (provider_bucket IS NOT NULL AND provider_key IS NOT NULL AND provider_etag IS NOT NULL)));
    CREATE UNIQUE INDEX owned_active_hash ON content.owned_objects(application_id,scope_kind,org_id,account_id,sha256) NULLS NOT DISTINCT WHERE state<>'failed';
    CREATE UNIQUE INDEX owned_fixed_key ON content.owned_objects(provider_bucket,provider_key) WHERE provider_key IS NOT NULL;
    ALTER TABLE content.owned_objects ENABLE ROW LEVEL SECURITY;
    ALTER TABLE content.owned_objects FORCE ROW LEVEL SECURITY;
    CREATE POLICY owned_scope ON content.owned_objects USING(
      application_id=current_setting('app.content_app',true) AND scope_kind=current_setting('app.content_kind',true)
      AND coalesce(org_id::text,'')=current_setting('app.content_org',true)
      AND coalesce(account_id::text,'')=current_setting('app.content_account',true)) WITH CHECK(
      application_id=current_setting('app.content_app',true) AND scope_kind=current_setting('app.content_kind',true)
      AND coalesce(org_id::text,'')=current_setting('app.content_org',true)
      AND coalesce(account_id::text,'')=current_setting('app.content_account',true));
    CREATE POLICY migration_inventory ON content.owned_objects FOR SELECT TO content_migrator USING(true);
    CREATE FUNCTION content.protect_owned() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN
      IF TG_OP='DELETE' THEN RAISE EXCEPTION 'immutable_content_identity'; END IF;
      IF TG_OP='UPDATE' THEN
        IF (NEW.id,NEW.application_id,NEW.scope_kind,NEW.org_id,NEW.account_id,NEW.sha256,NEW.size,NEW.media_type,NEW.created_at,NEW.created_by,NEW.initiator_actor_id,NEW.initiator_account_id)
           IS DISTINCT FROM (OLD.id,OLD.application_id,OLD.scope_kind,OLD.org_id,OLD.account_id,OLD.sha256,OLD.size,OLD.media_type,OLD.created_at,OLD.created_by,OLD.initiator_actor_id,OLD.initiator_account_id)
           OR OLD.state IN ('ready','failed') OR (OLD.state='pending' AND NEW.state<>'finalizing')
           OR (OLD.state='finalizing' AND NEW.state NOT IN ('ready','failed'))
           OR (NEW.state='failed' AND current_user<>'content_migrator') THEN RAISE EXCEPTION 'immutable_content_identity'; END IF;
      END IF;
      IF TG_OP='INSERT' AND current_user<>'content_migrator' AND (NEW.state<>'pending' OR NEW.claim_id IS NOT NULL OR NEW.provider_key IS NOT NULL OR NEW.provider_bucket IS NOT NULL OR NEW.provider_version IS NOT NULL OR NEW.provider_etag IS NOT NULL) THEN RAISE EXCEPTION 'publication_requires_verification'; END IF;
      IF NEW.state<>'ready' AND (NEW.provider_bucket IS NOT NULL OR NEW.provider_key IS NOT NULL OR NEW.provider_version IS NOT NULL OR NEW.provider_etag IS NOT NULL) THEN RAISE EXCEPTION 'publication_requires_verification'; END IF;
      IF TG_OP='UPDATE' AND OLD.state='finalizing' AND NEW.claim_id IS DISTINCT FROM OLD.claim_id THEN RAISE EXCEPTION 'immutable_finalization_claim'; END IF;
      NEW.updated_at=clock_timestamp();NEW.updated_by=current_setting('app.actor_id')::uuid;
      IF TG_OP='INSERT' THEN NEW.created_at=clock_timestamp();NEW.created_by=current_setting('app.actor_id')::uuid; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER protect_owned BEFORE INSERT OR UPDATE OR DELETE ON content.owned_objects FOR EACH ROW EXECUTE FUNCTION content.protect_owned();
    CREATE TABLE content.owned_events(
      id uuid PRIMARY KEY,content_id text NOT NULL REFERENCES content.owned_objects(id),
      event_type text NOT NULL,event_version int NOT NULL DEFAULT 1 CHECK(event_version=1),
      operation_id uuid NOT NULL,executor_actor_id uuid NOT NULL DEFAULT current_setting('app.actor_id')::uuid,
      initiator_actor_id uuid,initiator_account_id uuid,created_at timestamptz NOT NULL DEFAULT clock_timestamp());
    ALTER TABLE content.owned_events ENABLE ROW LEVEL SECURITY;
    ALTER TABLE content.owned_events FORCE ROW LEVEL SECURITY;
    CREATE POLICY owned_event_scope ON content.owned_events USING(EXISTS(SELECT 1 FROM content.owned_objects o WHERE o.id=content_id)) WITH CHECK(EXISTS(SELECT 1 FROM content.owned_objects o WHERE o.id=content_id) AND executor_actor_id=current_setting('app.actor_id')::uuid);
    CREATE FUNCTION content.attribute_owned_event() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN
      NEW.executor_actor_id=current_setting('app.actor_id')::uuid;NEW.created_at=clock_timestamp();RETURN NEW;
    END $$;
    CREATE TRIGGER attribute_owned_event BEFORE INSERT ON content.owned_events FOR EACH ROW EXECUTE FUNCTION content.attribute_owned_event();
    CREATE FUNCTION content.immutable_owned_evidence() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'immutable_content_evidence'; END $$;
    CREATE TRIGGER immutable_owned_events BEFORE UPDATE OR DELETE ON content.owned_events FOR EACH ROW EXECUTE FUNCTION content.immutable_owned_evidence();
    CREATE TABLE content.legacy_adoptions(
      source_org_id uuid NOT NULL,source_content_id text NOT NULL,content_id text NOT NULL UNIQUE REFERENCES content.owned_objects(id),
      manifest_sha256 text NOT NULL,source_associations jsonb NOT NULL,source_created_by text NOT NULL,
      source_created_at timestamptz NOT NULL,adopted_at timestamptz NOT NULL DEFAULT clock_timestamp(),
      adopted_by uuid NOT NULL DEFAULT current_setting('app.actor_id')::uuid,
      PRIMARY KEY(source_org_id,source_content_id),FOREIGN KEY(source_org_id,source_content_id) REFERENCES content.objects(org_id,id));
    ALTER TABLE content.legacy_adoptions ENABLE ROW LEVEL SECURITY;ALTER TABLE content.legacy_adoptions FORCE ROW LEVEL SECURITY;
    CREATE POLICY migration_adoption ON content.legacy_adoptions TO content_migrator USING(true) WITH CHECK(true);
    CREATE TRIGGER immutable_adoption BEFORE UPDATE OR DELETE ON content.legacy_adoptions FOR EACH ROW EXECUTE FUNCTION content.immutable_owned_evidence();
    GRANT SELECT,INSERT ON content.owned_objects TO content_runtime;
    GRANT UPDATE(state,claim_id,provider_bucket,provider_key,provider_version,provider_etag) ON content.owned_objects TO content_runtime;
    GRANT INSERT ON content.owned_events TO content_runtime;
    REVOKE ALL ON content.legacy_adoptions FROM PUBLIC,content_runtime;
    REVOKE ALL ON content.alembic_version FROM PUBLIC,content_runtime;
    ''')


def downgrade():
    raise RuntimeError('Forward recovery required; preserve published bytes and adoption evidence')
