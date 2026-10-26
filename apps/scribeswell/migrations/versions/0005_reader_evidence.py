"""Narrow read-only publication routine; no publication/operator metadata grants."""
from alembic import op
revision='scribeswell_0005'
down_revision='scribeswell_0004'
branch_labels=None
depends_on=None
DDL=r'''
CREATE FUNCTION scribeswell.reader_verse_evidence(request_book text, request_chapter integer, request_verse integer)
RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog AS $$
 WITH candidates AS (SELECT jsonb_build_object('version',1,'status','ready','source_id',p.source_id,
 'source_revision',p.source_revision::text,'catalogue_version',p.header->>'catalogue_version',
 'versification_id',p.header->>'versification_id','tokenization_version',p.header->>'tokenization_version',
 'book',v.book,'chapter',v.chapter,'verse',v.verse,'verse_token_digest',v.verse_token_digest,
 'observed_word_ids',v.word_ids) AS evidence
 FROM scribeswell.current_corpus_publication p JOIN scribeswell.corpus_manifest_verse v USING(source_revision)
 WHERE v.book=request_book AND v.chapter=request_chapter AND v.verse=request_verse)
 SELECT CASE WHEN count(*)=1 THEN jsonb_agg(evidence)->0 ELSE NULL END FROM candidates
$$;
REVOKE ALL ON FUNCTION scribeswell.reader_verse_evidence(text,integer,integer) FROM PUBLIC,anon,authenticated,service_role,scribeswell_import;
GRANT EXECUTE ON FUNCTION scribeswell.reader_verse_evidence(text,integer,integer) TO scribeswell_runtime;
'''
def upgrade():op.execute(DDL)
def downgrade():raise RuntimeError('Forward recovery only')
