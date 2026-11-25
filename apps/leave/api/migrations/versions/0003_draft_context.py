"""Leave-owned minimum timezone configuration; no draft or administration tables."""
from alembic import op
revision='0003_draft_context'
down_revision='0002_selection'
branch_labels=None
depends_on=None

def upgrade():
    # btree_gist is a protected deployment prerequisite, never startup bootstrap.
    op.execute('''
    CREATE TABLE leave.work_profile (
      id uuid PRIMARY KEY CHECK(id<>'00000000-0000-0000-0000-000000000000'),
      org_id uuid NOT NULL CHECK(org_id<>'00000000-0000-0000-0000-000000000000'),
      display_name text NOT NULL CHECK(length(display_name) BETWEEN 1 AND 200),
      archived_at timestamptz,
      revision bigint NOT NULL DEFAULT 1 CHECK(revision>0),
      created_by uuid NOT NULL,created_at timestamptz NOT NULL,
      updated_by uuid NOT NULL,updated_at timestamptz NOT NULL,
      UNIQUE(org_id,id)
    );
    CREATE TABLE leave.organization_settings (
      org_id uuid PRIMARY KEY CHECK(org_id<>'00000000-0000-0000-0000-000000000000'),
      default_profile_id uuid,
      revision bigint NOT NULL DEFAULT 1 CHECK(revision>0),
      created_by uuid NOT NULL,created_at timestamptz NOT NULL,
      updated_by uuid NOT NULL,updated_at timestamptz NOT NULL,
      FOREIGN KEY(org_id,default_profile_id) REFERENCES leave.work_profile(org_id,id) ON DELETE RESTRICT
    );
    CREATE TABLE leave.work_profile_version (
      id uuid PRIMARY KEY CHECK(id<>'00000000-0000-0000-0000-000000000000'),
      org_id uuid NOT NULL,profile_id uuid NOT NULL,
      effective_from timestamptz NOT NULL CHECK(isfinite(effective_from)),
      effective_until timestamptz CHECK(isfinite(effective_until) AND effective_until>effective_from),
      work_timezone text CHECK(length(work_timezone) BETWEEN 1 AND 255),
      created_by uuid NOT NULL,created_at timestamptz NOT NULL,
      FOREIGN KEY(org_id,profile_id) REFERENCES leave.work_profile(org_id,id) ON DELETE RESTRICT,
      EXCLUDE USING gist(org_id public.gist_uuid_ops WITH =,profile_id public.gist_uuid_ops WITH =,tstzrange(effective_from,effective_until,'[)') WITH &&)
    );
    CREATE TABLE leave.employment_settings (
      id uuid PRIMARY KEY CHECK(id<>'00000000-0000-0000-0000-000000000000'),
      org_id uuid NOT NULL CHECK(org_id<>'00000000-0000-0000-0000-000000000000'),
      employment_id uuid NOT NULL CHECK(employment_id<>'00000000-0000-0000-0000-000000000000'),
      profile_id uuid,timezone_override text CHECK(length(timezone_override) BETWEEN 1 AND 255),
      effective_from timestamptz NOT NULL CHECK(isfinite(effective_from)),
      effective_until timestamptz CHECK(isfinite(effective_until) AND effective_until>effective_from),
      revision bigint NOT NULL DEFAULT 1 CHECK(revision>0),
      created_by uuid NOT NULL,created_at timestamptz NOT NULL,
      updated_by uuid NOT NULL,updated_at timestamptz NOT NULL,
      FOREIGN KEY(org_id,profile_id) REFERENCES leave.work_profile(org_id,id) ON DELETE RESTRICT,
      EXCLUDE USING gist(org_id public.gist_uuid_ops WITH =,employment_id public.gist_uuid_ops WITH =,tstzrange(effective_from,effective_until,'[)') WITH &&)
    );
    CREATE FUNCTION leave.context_scope(name text) RETURNS uuid LANGUAGE plpgsql STABLE AS $$
    BEGIN RETURN nullif(current_setting(name,true),'')::uuid;
    EXCEPTION WHEN invalid_text_representation THEN RETURN NULL; END $$;
    REVOKE ALL ON FUNCTION leave.context_scope(text) FROM PUBLIC;
    GRANT EXECUTE ON FUNCTION leave.context_scope(text) TO leave_runtime;
    CREATE FUNCTION leave.stamp_configuration() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE actor uuid:=leave.context_scope('app.actor_id');
    BEGIN
      IF actor IS NULL OR actor='00000000-0000-0000-0000-000000000000' THEN RAISE EXCEPTION 'configuration_actor_required'; END IF;
      IF TG_OP='INSERT' THEN
        NEW.created_by:=actor;NEW.created_at:=statement_timestamp();NEW.revision:=1;
      ELSE
        IF NEW.org_id<>OLD.org_id OR NEW.created_by<>OLD.created_by OR NEW.created_at<>OLD.created_at THEN RAISE EXCEPTION 'configuration_immutable'; END IF;
        IF TG_TABLE_NAME='work_profile' THEN
          IF NEW.id<>OLD.id THEN RAISE EXCEPTION 'configuration_immutable'; END IF;
        END IF;
        IF TG_TABLE_NAME='employment_settings' THEN
          IF NEW.id<>OLD.id OR NEW.employment_id<>OLD.employment_id THEN RAISE EXCEPTION 'configuration_immutable'; END IF;
        END IF;
        NEW.revision:=OLD.revision+1;
      END IF;
      NEW.updated_by:=actor;NEW.updated_at:=statement_timestamp();RETURN NEW;
    END $$;
    CREATE FUNCTION leave.stamp_timezone_version() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE actor uuid:=leave.context_scope('app.actor_id');
    BEGIN
      IF TG_OP<>'INSERT' THEN RAISE EXCEPTION 'timezone_version_immutable'; END IF;
      IF actor IS NULL OR actor='00000000-0000-0000-0000-000000000000' THEN RAISE EXCEPTION 'configuration_actor_required'; END IF;
      NEW.created_by:=actor;NEW.created_at:=statement_timestamp();RETURN NEW;
    END $$;
    REVOKE ALL ON FUNCTION leave.stamp_configuration(),leave.stamp_timezone_version() FROM PUBLIC;
    CREATE TRIGGER stamp_profile BEFORE INSERT OR UPDATE ON leave.work_profile FOR EACH ROW EXECUTE FUNCTION leave.stamp_configuration();
    CREATE TRIGGER stamp_organization_settings BEFORE INSERT OR UPDATE ON leave.organization_settings FOR EACH ROW EXECUTE FUNCTION leave.stamp_configuration();
    CREATE TRIGGER stamp_employment_settings BEFORE INSERT OR UPDATE ON leave.employment_settings FOR EACH ROW EXECUTE FUNCTION leave.stamp_configuration();
    CREATE TRIGGER stamp_timezone_version BEFORE INSERT OR UPDATE OR DELETE ON leave.work_profile_version FOR EACH ROW EXECUTE FUNCTION leave.stamp_timezone_version();
    ''')
    for name in ('work_profile','organization_settings','work_profile_version','employment_settings'):
        employment=" AND employment_id=leave.context_scope('app.employment_id')" if name=='employment_settings' else ''
        op.execute(f'''ALTER TABLE leave.{name} ENABLE ROW LEVEL SECURITY;
          ALTER TABLE leave.{name} FORCE ROW LEVEL SECURITY;
          CREATE POLICY context_read ON leave.{name} FOR SELECT TO leave_runtime USING(
            org_id=leave.context_scope('app.org_id') AND current_setting('app.mode',true)='own_read'{employment});
          GRANT SELECT ON leave.{name} TO leave_runtime;''')

def downgrade():raise RuntimeError('forward_recovery_required')
