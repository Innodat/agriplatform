"""Make JSONB operand grouping explicit in metadata correspondence validation."""
from alembic import op
revision='scribeswell_studies_0009'
down_revision='scribeswell_studies_0008'
branch_labels=None
depends_on=None

def upgrade():
 op.get_bind().exec_driver_sql("""
CREATE OR REPLACE FUNCTION scribeswell_studies.validate_note_metadata() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE current_value jsonb; expected_highlights jsonb; expected_references jsonb;
BEGIN
 SELECT n.value INTO current_value FROM scribeswell_studies.notes n
 JOIN scribeswell_studies.studies s ON s.account_id=n.account_id AND s.id=n.study_id
 WHERE n.account_id=NEW.account_id AND n.study_id=NEW.study_id AND n.id=NEW.note_id AND n.revision=NEW.revision AND n.active AND s.active;
 IF current_value IS NULL THEN
  RAISE EXCEPTION 'note metadata scope invalid' USING ERRCODE='23514';
 END IF;
 SELECT COALESCE(jsonb_agg(jsonb_build_object('id',h->'id','anchor',h->'anchor') ORDER BY ordinal),'[]'::jsonb)
 INTO expected_highlights FROM jsonb_array_elements((current_value->'highlights')) WITH ORDINALITY a(h,ordinal);
 SELECT COALESCE(jsonb_agg(DISTINCT reference),'[]'::jsonb) INTO expected_references FROM (
 SELECT c->'reference' AS reference FROM jsonb_array_elements((current_value->'connections')) c
 UNION ALL SELECT segment->'reference' FROM jsonb_array_elements((current_value->'highlights')) h CROSS JOIN LATERAL jsonb_array_elements(h->'anchor'->'segments') segment
 UNION ALL SELECT i->'reference' FROM jsonb_path_query(current_value,'$.document.blocks[*].content[*]') i WHERE i->>'type'='passage_link'
 UNION ALL SELECT i->'reference' FROM jsonb_path_query(current_value,'$.document.blocks[*].items[*][*].content[*]') i WHERE i->>'type'='passage_link'
 ) refs;
 IF (NEW.metadata->'connections') IS DISTINCT FROM (current_value->'connections')
 OR (NEW.metadata->'highlights') IS DISTINCT FROM expected_highlights
 OR jsonb_typeof((NEW.metadata->'references')) IS DISTINCT FROM 'array'
 OR NOT ((NEW.metadata->'references') @> expected_references AND expected_references @> (NEW.metadata->'references'))
 OR jsonb_array_length((NEW.metadata->'references'))<>jsonb_array_length(expected_references) THEN
  RAISE EXCEPTION 'note metadata correspondence invalid' USING ERRCODE='23514';
 END IF;
 RETURN NEW;
END $$;
""")

def downgrade():
 raise RuntimeError('Forward recovery only; preserve validated note history')
