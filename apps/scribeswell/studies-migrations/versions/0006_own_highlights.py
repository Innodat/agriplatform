"""Immutable validated per-revision anchor/reference metadata; no historical body."""
from alembic import op
revision='scribeswell_studies_0006'
down_revision='scribeswell_studies_0005'
branch_labels=None
depends_on=None

def upgrade():
 op.execute('''
CREATE TABLE scribeswell_studies.note_revision_metadata(
 account_id uuid NOT NULL, study_id uuid NOT NULL, note_id uuid NOT NULL,
 revision bigint NOT NULL CHECK(revision>0), metadata jsonb NOT NULL CHECK(jsonb_typeof(metadata)='object' AND metadata ?& ARRAY['connections','highlights','references'] AND metadata-ARRAY['connections','highlights','references']='{}'::jsonb),
 created_by uuid NOT NULL CHECK(created_by<>'00000000-0000-0000-0000-000000000000'),
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 PRIMARY KEY(account_id,note_id,revision),
 FOREIGN KEY(account_id,study_id,note_id) REFERENCES scribeswell_studies.notes(account_id,study_id,id)
);
ALTER TABLE scribeswell_studies.note_revision_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE scribeswell_studies.note_revision_metadata FORCE ROW LEVEL SECURITY;
CREATE POLICY owner_metadata ON scribeswell_studies.note_revision_metadata USING(account_id=current_setting('app.account_id',true)::uuid) WITH CHECK(account_id=current_setting('app.account_id',true)::uuid);
REVOKE ALL ON scribeswell_studies.note_revision_metadata FROM PUBLIC;
GRANT SELECT,INSERT ON scribeswell_studies.note_revision_metadata TO scribeswell_studies_runtime;
CREATE FUNCTION scribeswell_studies.validate_note_metadata() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE current_value jsonb; expected_highlights jsonb; expected_references jsonb;
BEGIN
 SELECT n.value INTO current_value FROM scribeswell_studies.notes n
 JOIN scribeswell_studies.studies s ON s.account_id=n.account_id AND s.id=n.study_id
 WHERE n.account_id=NEW.account_id AND n.study_id=NEW.study_id AND n.id=NEW.note_id AND n.revision=NEW.revision AND n.active AND s.active;
 IF current_value IS NULL THEN
  RAISE EXCEPTION 'note metadata scope invalid' USING ERRCODE='23514';
 END IF;
 SELECT COALESCE(jsonb_agg(jsonb_build_object('id',h->'id','anchor',h->'anchor') ORDER BY ordinal),'[]'::jsonb)
 INTO expected_highlights FROM jsonb_array_elements(current_value->'highlights') WITH ORDINALITY a(h,ordinal);
 SELECT COALESCE(jsonb_agg(DISTINCT reference),'[]'::jsonb) INTO expected_references FROM (
 SELECT c->'reference' AS reference FROM jsonb_array_elements(current_value->'connections') c
 UNION ALL SELECT segment->'reference' FROM jsonb_array_elements(current_value->'highlights') h CROSS JOIN LATERAL jsonb_array_elements(h->'anchor'->'segments') segment
 UNION ALL SELECT i->'reference' FROM jsonb_path_query(current_value,'$.document.blocks[*].content[*]') i WHERE i->>'type'='passage_link'
 UNION ALL SELECT i->'reference' FROM jsonb_path_query(current_value,'$.document.blocks[*].items[*][*].content[*]') i WHERE i->>'type'='passage_link'
 ) refs;
 IF NEW.metadata->'connections' IS DISTINCT FROM current_value->'connections'
 OR NEW.metadata->'highlights' IS DISTINCT FROM expected_highlights
 OR jsonb_typeof(NEW.metadata->'references') IS DISTINCT FROM 'array'
 OR NOT (NEW.metadata->'references' @> expected_references AND expected_references @> NEW.metadata->'references')
 OR jsonb_array_length(NEW.metadata->'references')<>jsonb_array_length(expected_references) THEN
  RAISE EXCEPTION 'note metadata correspondence invalid' USING ERRCODE='23514';
 END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION scribeswell_studies.validate_note_metadata() FROM PUBLIC;
CREATE TRIGGER validate_note_metadata BEFORE INSERT ON scribeswell_studies.note_revision_metadata FOR EACH ROW EXECUTE FUNCTION scribeswell_studies.validate_note_metadata();
CREATE FUNCTION scribeswell_studies.protect_note_aggregate_version() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
 IF OLD.value->'format_version'='3'::jsonb AND NEW.active AND NEW.value->'format_version' IS DISTINCT FROM '3'::jsonb THEN
  RAISE EXCEPTION 'note format unsupported' USING ERRCODE='23514';
 END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION scribeswell_studies.protect_note_aggregate_version() FROM PUBLIC;
CREATE TRIGGER protect_note_aggregate_version BEFORE UPDATE ON scribeswell_studies.notes FOR EACH ROW EXECUTE FUNCTION scribeswell_studies.protect_note_aggregate_version();
CREATE FUNCTION scribeswell_studies.immutable_note_metadata() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN RAISE EXCEPTION 'immutable note metadata' USING ERRCODE='23514'; END $$;
REVOKE ALL ON FUNCTION scribeswell_studies.immutable_note_metadata() FROM PUBLIC;
CREATE TRIGGER immutable_note_metadata BEFORE UPDATE OR DELETE OR TRUNCATE ON scribeswell_studies.note_revision_metadata FOR EACH STATEMENT EXECUTE FUNCTION scribeswell_studies.immutable_note_metadata();
''')
def downgrade():raise RuntimeError('Forward recovery only')
