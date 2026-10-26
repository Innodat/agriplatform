"""Validate bounded multirow appends once while preserving immutable header locking."""
from alembic import op
revision='scribeswell_0006'
down_revision='scribeswell_0005'
branch_labels=None
depends_on=None
DDL=r"""
CREATE OR REPLACE FUNCTION scribeswell.protect_corpus_publication_record() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $body$
DECLARE header_actor uuid;
BEGIN
 -- Set attribution per row; correspondence/locking is checked once per statement.
 IF TG_OP='INSERT' AND TG_TABLE_NAME IN ('corpus_manifest_batch','corpus_manifest_verse','corpus_manifest_word_identity') THEN
  NEW.created_at=transaction_timestamp();
  RETURN NEW;
 END IF;
 IF TG_OP IN ('DELETE','TRUNCATE') OR (TG_OP='UPDATE' AND TG_TABLE_NAME NOT IN ('corpus_current_publication','corpus_publication_authority')) THEN
  RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
 IF TG_OP='UPDATE' THEN
  IF NEW.created_at<>OLD.created_at OR NEW.created_by_actor_id<>OLD.created_by_actor_id THEN
   RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
  IF TG_TABLE_NAME='corpus_publication_authority' THEN
   IF NEW.database_login<>OLD.database_login OR NEW.source_id<>OLD.source_id OR NEW.revision<=OLD.revision THEN
    RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
  END IF;
 ELSE
  IF TG_TABLE_NAME IN ('corpus_manifest_batch','corpus_manifest_verse','corpus_manifest_word_identity','corpus_manifest_completion') THEN
   -- All alternate appends and completion serialize on the same immutable header.
   SELECT created_by_actor_id INTO header_actor FROM scribeswell.corpus_manifest_header
    WHERE source_revision=NEW.source_revision FOR UPDATE;
   IF NOT FOUND OR NEW.created_by_actor_id IS DISTINCT FROM header_actor THEN
    RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
  END IF;
  IF TG_TABLE_NAME IN ('corpus_manifest_batch','corpus_manifest_verse','corpus_manifest_word_identity') THEN
   IF EXISTS(SELECT FROM scribeswell.corpus_manifest_completion WHERE source_revision=NEW.source_revision) THEN
    RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
  ELSIF TG_TABLE_NAME='corpus_manifest_completion' THEN
   PERFORM scribeswell.validate_corpus_manifest_completion(NEW.source_revision);
   IF NOT EXISTS(SELECT FROM scribeswell.corpus_manifest_header h WHERE h.source_revision=NEW.source_revision
    AND h.header->>'auditor_version'=NEW.auditor_version AND h.header->>'digest'=NEW.digest
    AND (h.header->>'verse_count')::integer=NEW.verse_count AND (h.header->>'token_count')::integer=NEW.token_count
    AND h.created_by_actor_id=NEW.created_by_actor_id) THEN
    RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
  END IF;
  NEW.created_at=transaction_timestamp();
 END IF;
 IF TG_TABLE_NAME IN ('corpus_current_publication','corpus_publication_authority') THEN NEW.updated_at=transaction_timestamp(); END IF;
 RETURN NEW;
END
$body$;
CREATE FUNCTION scribeswell.check_corpus_publication_append() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $body$
DECLARE appended record; header_actor uuid;
BEGIN
 -- Stable order also bounds deadlock exposure for a multi-revision owner statement.
 FOR appended IN SELECT DISTINCT source_revision FROM corpus_appended ORDER BY source_revision LOOP
  SELECT created_by_actor_id INTO header_actor FROM scribeswell.corpus_manifest_header
   WHERE source_revision=appended.source_revision FOR NO KEY UPDATE;
  IF NOT FOUND OR EXISTS(SELECT FROM corpus_appended a WHERE a.source_revision=appended.source_revision
       AND a.created_by_actor_id IS DISTINCT FROM header_actor)
   OR EXISTS(SELECT FROM scribeswell.corpus_manifest_completion c WHERE c.source_revision=appended.source_revision) THEN
   RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict';
  END IF;
 END LOOP;
 RETURN NULL;
END
$body$;
REVOKE ALL ON FUNCTION scribeswell.check_corpus_publication_append() FROM PUBLIC,anon,authenticated,service_role,scribeswell_runtime,scribeswell_import;
CREATE TRIGGER corpus_publication_append AFTER INSERT ON scribeswell.corpus_manifest_batch
 REFERENCING NEW TABLE AS corpus_appended FOR EACH STATEMENT EXECUTE FUNCTION scribeswell.check_corpus_publication_append();
ALTER TABLE scribeswell.corpus_manifest_batch ENABLE ALWAYS TRIGGER corpus_publication_append;
CREATE TRIGGER corpus_publication_append AFTER INSERT ON scribeswell.corpus_manifest_verse
 REFERENCING NEW TABLE AS corpus_appended FOR EACH STATEMENT EXECUTE FUNCTION scribeswell.check_corpus_publication_append();
ALTER TABLE scribeswell.corpus_manifest_verse ENABLE ALWAYS TRIGGER corpus_publication_append;
CREATE TRIGGER corpus_publication_append AFTER INSERT ON scribeswell.corpus_manifest_word_identity
 REFERENCING NEW TABLE AS corpus_appended FOR EACH STATEMENT EXECUTE FUNCTION scribeswell.check_corpus_publication_append();
ALTER TABLE scribeswell.corpus_manifest_word_identity ENABLE ALWAYS TRIGGER corpus_publication_append;
"""
DDL+=r"""
CREATE OR REPLACE FUNCTION scribeswell.corpus_publication_internal(request jsonb, lookup_only boolean) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $body$
DECLARE principal record; authority record; previous record; epoch record; attempt record; stage record;
 source text; operation uuid; revision_id uuid; variant text; seal jsonb; identity jsonb; h jsonb;
 allowed text[]; item jsonb; id_value jsonb; index_value integer; start_value integer; n integer;
 receipt jsonb;
 books text[] := ARRAY['Gen','Exod','Lev','Num','Deut','Josh','Judg','1Sam','2Sam','1Kgs','2Kgs','Isa','Jer','Ezek','Hos','Joel','Amos','Obad','Jonah','Mic','Nah','Hab','Zeph','Hag','Zech','Mal','Ps','Prov','Job','Song','Ruth','Lam','Eccl','Esth','Dan','Ezra','Neh','1Chr','2Chr'];
BEGIN
 IF current_setting('lock_timeout')::interval=interval '0' OR current_setting('lock_timeout')::interval>interval '2 seconds' THEN
  PERFORM set_config('lock_timeout','2s',true); END IF;
 IF current_setting('transaction_isolation')<>'read committed' OR current_setting('transaction_read_only')<>'off' THEN
  RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='corpus_publish.unavailable'; END IF;
 IF request IS NULL OR jsonb_typeof(request)<>'object' OR octet_length(request::text)>70000000 THEN
  RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publish.input_invalid'; END IF;
 variant=request->>'command'; seal=request->'seal';
 IF variant NOT IN ('publication.stage','publication.batch','publication.complete','publication.activate') OR variant IS NULL
 OR request->'version' IS DISTINCT FROM '1'::jsonb OR request->>'version' IS DISTINCT FROM '1' OR jsonb_typeof(request->'operation_id') IS DISTINCT FROM 'string'
 OR request->>'operation_id' !~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
 OR request->>'operation_id'='00000000-0000-0000-0000-000000000000'
 OR jsonb_typeof(request->'source_revision') IS DISTINCT FROM 'string'
 OR request->>'source_revision' !~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
 OR request->>'source_revision'='00000000-0000-0000-0000-000000000000' THEN
  RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publish.input_invalid'; END IF;
 allowed=ARRAY['command','operation_id','seal','source_revision','version'];
 IF variant='publication.stage' THEN allowed=array_append(allowed,'header');
 ELSIF variant='publication.batch' THEN allowed=allowed||ARRAY['batch_index','first_ordinal','rows'];
 ELSIF variant='publication.complete' THEN allowed=allowed||ARRAY['auditor_version','digest','token_count','verse_count']; END IF;
 IF (SELECT array_agg(k ORDER BY k) FROM jsonb_object_keys(request) k) IS DISTINCT FROM
    (SELECT array_agg(k ORDER BY k) FROM unnest(allowed) k) THEN
  RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publish.input_invalid'; END IF;
 PERFORM scribeswell.validate_corpus_command(seal);
 IF seal->>'command'<>'corpus.seal' THEN RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publish.input_invalid'; END IF;
 source=seal#>>'{scope,source_id}'; identity=seal#>'{payload,input}';
 operation=(request->>'operation_id')::uuid; revision_id=(request->>'source_revision')::uuid;
 IF session_user<>'scribeswell_corpus_operator' OR NOT EXISTS
  (SELECT FROM pg_roles r WHERE r.rolname=session_user AND r.rolcanlogin AND NOT r.rolinherit
   AND NOT r.rolsuper AND NOT r.rolbypassrls AND NOT r.rolcreatedb AND NOT r.rolcreaterole AND NOT r.rolreplication
   AND NOT EXISTS (SELECT FROM pg_auth_members m WHERE m.member=r.oid OR m.roleid=r.oid)) THEN
  RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='corpus_publish.access_denied'; END IF;
 SELECT * INTO principal FROM scribeswell.corpus_operator_principal WHERE database_login=session_user FOR SHARE;
 IF NOT FOUND OR NOT principal.enabled THEN RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='corpus_publish.access_denied'; END IF;
 SELECT * INTO authority FROM scribeswell.corpus_publication_authority
  WHERE database_login=session_user AND source_id=source FOR SHARE;
 IF NOT FOUND OR NOT authority.enabled THEN RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='corpus_publish.access_denied'; END IF;
 PERFORM pg_advisory_xact_lock(hashtextextended(session_user::text||':'||operation::text,31003));
 IF EXISTS(SELECT FROM scribeswell.corpus_command_outcome WHERE database_login=session_user AND operation_id=operation) THEN
  RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
 SELECT * INTO previous FROM scribeswell.corpus_publication_outcome WHERE database_login=session_user AND operation_id=operation;
 IF FOUND THEN
  IF previous.semantic_command<>request OR previous.created_by_actor_id<>principal.executor_actor_id THEN
   RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
  RETURN previous.result;
 END IF;
 IF lookup_only THEN RETURN NULL; END IF;
 PERFORM FROM scribeswell.corpus_fence_control WHERE singleton AND enforcement FOR SHARE;
 IF NOT FOUND THEN RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='corpus_publish.unavailable'; END IF;
 PERFORM pg_advisory_xact_lock(31003,1);
 SELECT * INTO epoch FROM scribeswell.corpus_epoch WHERE singleton FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
 SELECT * INTO attempt FROM scribeswell.corpus_attempt WHERE attempt_id=epoch.attempt_id FOR UPDATE;
 IF NOT FOUND OR epoch.state<>'closed' OR attempt.state<>'closed' OR epoch.source_id<>source
 OR epoch.attempt_id<>(seal#>>'{payload,expected_attempt_id}')::uuid
 OR epoch.generation<>(seal#>>'{payload,expected_generation}')::bigint
 OR attempt.source_id<>source OR attempt.generation<>epoch.generation OR attempt.input_sha256<>epoch.input_sha256
 OR epoch.input_sha256<>identity->>'source_sha256' OR attempt.catalogue_version<>identity->>'catalogue_version'
 OR attempt.versification_id<>identity->>'versification_id' OR attempt.tokenization_version<>identity->>'tokenization_version' THEN
  RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
 -- The original seal must be an acknowledged exact operation by this principal.
 PERFORM FROM scribeswell.corpus_command_outcome WHERE database_login=session_user
  AND operation_id=(seal->>'operation_id')::uuid AND semantic_command=seal
  AND executor_actor_id=principal.executor_actor_id AND attempt_id=epoch.attempt_id AND generation=epoch.generation;
 IF NOT FOUND THEN RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
 SELECT * INTO stage FROM scribeswell.corpus_manifest_header WHERE source_revision=revision_id FOR UPDATE;
 IF variant='publication.stage' THEN
  h=request->'header';
  IF jsonb_typeof(h) IS DISTINCT FROM 'object' THEN RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publish.input_invalid'; END IF;
  IF (SELECT array_agg(k ORDER BY k) FROM jsonb_object_keys(h) k) IS DISTINCT FROM
   ARRAY['auditor_version','batch_count','catalogue_version','digest','encoded_bytes','executor_actor_id','inventory','source_sha256','token_count','tokenization_version','verse_count','versification_id']
  OR h->>'auditor_version' IS DISTINCT FROM 'scribeswell.closed_audit.v1'
  OR h->>'executor_actor_id' IS DISTINCT FROM principal.executor_actor_id::text
  OR h->'catalogue_version' IS DISTINCT FROM identity->'catalogue_version'
  OR h->'versification_id' IS DISTINCT FROM identity->'versification_id'
  OR h->'tokenization_version' IS DISTINCT FROM identity->'tokenization_version'
  OR h->'source_sha256' IS DISTINCT FROM identity->'source_sha256'
  OR jsonb_typeof(h->'digest') IS DISTINCT FROM 'string' OR h->>'digest' !~ '^[0-9a-f]{64}$'
  OR jsonb_typeof(h->'inventory') IS DISTINCT FROM 'array' THEN
   RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publish.input_invalid'; END IF;
  FOREACH source IN ARRAY ARRAY['verse_count','token_count','encoded_bytes','batch_count'] LOOP
   IF jsonb_typeof(h->source) IS DISTINCT FROM 'number' OR h->>source !~ '^[1-9][0-9]{0,8}$' THEN
    RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publish.input_invalid'; END IF;
  END LOOP;
  source=seal#>>'{scope,source_id}';
  IF (h->>'verse_count')::integer NOT BETWEEN 39 AND 50000 OR (h->>'token_count')::integer NOT BETWEEN 39 AND 1000000
  OR (h->>'encoded_bytes')::integer>67108864 OR (h->>'batch_count')::integer<>((h->>'verse_count')::integer+999)/1000
  OR jsonb_array_length(h->'inventory')<>(h->>'verse_count')::integer THEN
   RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publish.input_invalid'; END IF;
  -- The controlled auditor declares the complete qualified source inventory.
  -- Validate its shape/order now, and exact correspondence with staged rows below.
  n=0;
  FOR item IN SELECT value FROM jsonb_array_elements(h->'inventory') LOOP
   IF jsonb_typeof(item)<>'array' OR jsonb_array_length(item)<>5 OR jsonb_typeof(item->0) IS DISTINCT FROM 'string'
   OR array_position(books,item->>0) IS NULL OR jsonb_typeof(item->1) IS DISTINCT FROM 'number'
   OR jsonb_typeof(item->2) IS DISTINCT FROM 'number' OR jsonb_typeof(item->3) IS DISTINCT FROM 'string'
   OR jsonb_typeof(item->4) IS DISTINCT FROM 'number' OR item->>1 !~ '^[1-9][0-9]{0,2}$'
   OR item->>2 !~ '^[1-9][0-9]{0,2}$' OR item->>4 !~ '^[1-9][0-9]{0,2}$'
   OR (item->>1)::integer>150 OR (item->>2)::integer>176 OR (item->>4)::integer>512
   OR item->>3 !~ '^[0-9a-f]{64}$' THEN
    RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publish.input_invalid'; END IF;
   IF n>0 AND ROW(array_position(books,item->>0),(item->>1)::integer,(item->>2)::integer)<=
    ROW(array_position(books,h#>>ARRAY['inventory',(n-1)::text,'0']),
        (h#>>ARRAY['inventory',(n-1)::text,'1'])::integer,(h#>>ARRAY['inventory',(n-1)::text,'2'])::integer) THEN
    RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publish.input_invalid'; END IF;
   n=n+1;
  END LOOP;
  IF (SELECT count(DISTINCT value->>0) FROM jsonb_array_elements(h->'inventory'))<>39
   OR (SELECT sum((value->>4)::integer) FROM jsonb_array_elements(h->'inventory'))<>(h->>'token_count')::integer THEN
   RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publish.input_invalid'; END IF;
  IF stage.source_revision IS NOT NULL THEN
   IF stage.seal<>seal OR stage.header<>h OR stage.created_by_actor_id<>principal.executor_actor_id THEN
    RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
  ELSE
   INSERT INTO scribeswell.corpus_manifest_header(source_revision,source_id,attempt_id,generation,seal,header,created_by_actor_id)
    VALUES(revision_id,source,epoch.attempt_id,epoch.generation,seal,h,principal.executor_actor_id);
  END IF;
 ELSE
  IF stage.source_revision IS NULL OR stage.seal<>seal OR stage.created_by_actor_id<>principal.executor_actor_id THEN
   RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
  h=stage.header;
  IF variant='publication.batch' THEN
   IF jsonb_typeof(request->'batch_index') IS DISTINCT FROM 'number' OR request->>'batch_index' !~ '^(0|[1-9][0-9]?)$'
   OR jsonb_typeof(request->'first_ordinal') IS DISTINCT FROM 'number' OR request->>'first_ordinal' !~ '^(0|[1-9][0-9]{0,4})$'
   OR jsonb_typeof(request->'rows') IS DISTINCT FROM 'array' THEN
    RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publish.input_invalid'; END IF;
   index_value=(request->>'batch_index')::integer; start_value=(request->>'first_ordinal')::integer;
   SELECT * INTO previous FROM scribeswell.corpus_manifest_batch WHERE source_revision=revision_id AND batch_index=index_value;
   IF FOUND THEN
    IF previous.first_ordinal<>start_value OR previous.rows<>request->'rows' THEN
     RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
   ELSE
    IF EXISTS(SELECT FROM scribeswell.corpus_manifest_completion WHERE source_revision=revision_id)
    OR index_value<>(SELECT count(*) FROM scribeswell.corpus_manifest_batch WHERE source_revision=revision_id)
    OR start_value<>index_value*1000 OR index_value>=(h->>'batch_count')::integer
    OR jsonb_array_length(request->'rows')<>least(1000,(h->>'verse_count')::integer-start_value) THEN
     RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
    -- Expand the complete immutable inventory once, rather than copying its
    -- large nested JSONB value for every submitted verse/word loop iteration.
    IF EXISTS(SELECT FROM jsonb_array_elements(request->'rows') submitted(item)
      WHERE CASE WHEN jsonb_typeof(submitted.item)<>'array' THEN true
       ELSE jsonb_array_length(submitted.item)<>5 OR jsonb_typeof(submitted.item->4) IS DISTINCT FROM 'array' END) THEN
     RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publish.input_invalid'; END IF;
    IF EXISTS(
      WITH expected AS MATERIALIZED (
       SELECT e.item,e.ordinal FROM jsonb_array_elements(h->'inventory') WITH ORDINALITY e(item,ordinal)
       WHERE e.ordinal>start_value AND e.ordinal<=start_value+jsonb_array_length(request->'rows'))
      SELECT FROM jsonb_array_elements(request->'rows') WITH ORDINALITY submitted(item,ordinal)
      LEFT JOIN expected ON expected.ordinal=start_value+submitted.ordinal
      WHERE expected.item IS NULL OR jsonb_build_array(submitted.item->0,submitted.item->1,
       submitted.item->2,submitted.item->3,jsonb_array_length(submitted.item->4))<>expected.item) THEN
     RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
    IF EXISTS(SELECT FROM jsonb_array_elements(request->'rows') submitted(item)
      CROSS JOIN LATERAL jsonb_array_elements(submitted.item->4) ids(id)
      WHERE CASE WHEN jsonb_typeof(ids.id)<>'string' OR ids.id#>>'{}' !~ '^[1-9][0-9]{0,18}$' THEN true
       ELSE (ids.id#>>'{}')::numeric>9223372036854775807 END) THEN
     RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publish.input_invalid'; END IF;
    INSERT INTO scribeswell.corpus_manifest_batch(source_revision,batch_index,first_ordinal,rows,created_by_actor_id)
     VALUES(revision_id,index_value,start_value,request->'rows',principal.executor_actor_id);
    INSERT INTO scribeswell.corpus_manifest_verse(source_revision,ordinal,batch_index,book,chapter,verse,verse_token_digest,word_ids,created_by_actor_id)
     SELECT revision_id,start_value+ordinal_value::integer-1,index_value,v->>0,(v->>1)::integer,(v->>2)::integer,v->>3,v->4,principal.executor_actor_id
     FROM jsonb_array_elements(request->'rows') WITH ORDINALITY e(v,ordinal_value);
    INSERT INTO scribeswell.corpus_manifest_word_identity(source_revision,ordinal,position,word_id,created_by_actor_id)
     SELECT revision_id,start_value+ordinal_value::integer-1,position_value::integer,id::bigint,principal.executor_actor_id
     FROM jsonb_array_elements(request->'rows') WITH ORDINALITY e(v,ordinal_value)
     CROSS JOIN LATERAL jsonb_array_elements_text(v->4) WITH ORDINALITY w(id,position_value);
   END IF;
  ELSE
   IF variant='publication.complete' THEN
    IF request->'auditor_version' IS DISTINCT FROM h->'auditor_version' OR request->'digest' IS DISTINCT FROM h->'digest'
    OR request->'verse_count' IS DISTINCT FROM h->'verse_count' OR request->'token_count' IS DISTINCT FROM h->'token_count' THEN
     RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
    INSERT INTO scribeswell.corpus_manifest_completion(source_revision,auditor_version,digest,verse_count,token_count,created_by_actor_id)
     VALUES(revision_id,h->>'auditor_version',h->>'digest',(h->>'verse_count')::integer,(h->>'token_count')::integer,principal.executor_actor_id)
     ON CONFLICT(source_revision) DO NOTHING;
   ELSE
    PERFORM FROM scribeswell.corpus_manifest_completion WHERE source_revision=revision_id AND auditor_version=h->>'auditor_version'
     AND digest=h->>'digest' AND verse_count=(h->>'verse_count')::integer AND token_count=(h->>'token_count')::integer
     AND created_by_actor_id=principal.executor_actor_id;
    IF NOT FOUND THEN RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
    INSERT INTO scribeswell.corpus_current_publication(singleton,source_revision,created_by_actor_id,updated_by_actor_id)
     VALUES(true,revision_id,principal.executor_actor_id,principal.executor_actor_id)
     ON CONFLICT(singleton) DO UPDATE SET source_revision=excluded.source_revision,updated_by_actor_id=excluded.updated_by_actor_id;
   END IF;
  END IF;
 END IF;
 receipt=jsonb_build_object('version',1,'operation_id',operation::text,'command',variant,'source_revision',revision_id::text,
  'source_id',source,'attempt_id',epoch.attempt_id::text,'generation',epoch.generation::text,'executor_actor_id',principal.executor_actor_id::text,
  'status',CASE variant WHEN 'publication.stage' THEN 'staged' WHEN 'publication.batch' THEN 'batched' WHEN 'publication.complete' THEN 'complete' ELSE 'published' END);
 INSERT INTO scribeswell.corpus_publication_outcome(database_login,operation_id,semantic_command,source_revision,result,principal_revision,authority_revision,created_by_actor_id)
  VALUES(session_user,operation,request,revision_id,receipt,principal.revision,authority.revision,principal.executor_actor_id);
 RETURN receipt;
EXCEPTION WHEN unique_violation OR foreign_key_violation OR check_violation THEN
 RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict';
WHEN invalid_text_representation OR numeric_value_out_of_range OR invalid_parameter_value THEN
 RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publish.input_invalid';
END
$body$;
"""
DDL+=r"""
CREATE OR REPLACE FUNCTION scribeswell.validate_corpus_manifest_completion(revision_id uuid) RETURNS void
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $body$
DECLARE stage record; h jsonb; source text; inventory jsonb; actual_verse_count bigint; tokens bigint;
 encoded text; calculated_digest text;
BEGIN
 SELECT * INTO stage FROM scribeswell.corpus_manifest_header WHERE source_revision=revision_id FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
 h=stage.header; source=stage.source_id;
 -- Every persisted batch must match exactly its normalized contiguous verse slice.
 -- Aggregate each normalized slice once. Correlated access to the large
 -- toasted batch JSON for every verse exhausted the unchanged statement budget.
 IF EXISTS(
  WITH actual AS MATERIALIZED (
   SELECT v.batch_index,min(v.ordinal) AS first_ordinal,max(v.ordinal) AS last_ordinal,
    jsonb_agg(jsonb_build_array(v.book,v.chapter,v.verse,v.verse_token_digest,v.word_ids) ORDER BY v.ordinal) AS rows
   FROM scribeswell.corpus_manifest_verse v WHERE v.source_revision=revision_id GROUP BY v.batch_index)
  SELECT FROM scribeswell.corpus_manifest_batch b LEFT JOIN actual a USING(batch_index)
  WHERE b.source_revision=revision_id AND
   (b.batch_index<0 OR b.batch_index>=(h->>'batch_count')::integer
    OR b.first_ordinal<>b.batch_index*1000
    OR jsonb_array_length(b.rows)<>least(1000,(h->>'verse_count')::integer-b.first_ordinal)
    OR b.rows IS DISTINCT FROM a.rows OR a.first_ordinal<b.first_ordinal
    OR a.last_ordinal>=b.first_ordinal+jsonb_array_length(b.rows))) THEN
  RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
    SELECT count(*),sum(jsonb_array_length(word_ids)) INTO actual_verse_count,tokens FROM scribeswell.corpus_manifest_verse WHERE source_revision=revision_id;
    IF actual_verse_count<>(h->>'verse_count')::integer OR tokens<>(h->>'token_count')::integer
    OR (SELECT count(*) FROM scribeswell.corpus_manifest_batch WHERE source_revision=revision_id)<>(h->>'batch_count')::integer
    OR (SELECT count(*) FROM scribeswell.corpus_manifest_word_identity WHERE source_revision=revision_id)<>tokens
    OR EXISTS(SELECT FROM scribeswell.corpus_manifest_word_identity w JOIN scribeswell.corpus_manifest_verse v
      USING(source_revision,ordinal) WHERE w.source_revision=revision_id AND (v.word_ids->>(w.position-1)) IS DISTINCT FROM w.word_id::text)
    THEN RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
    SELECT jsonb_agg(jsonb_build_array(book,chapter,verse,verse_token_digest,jsonb_array_length(word_ids)) ORDER BY ordinal)
     INTO inventory FROM scribeswell.corpus_manifest_verse WHERE source_revision=revision_id;
    IF inventory IS DISTINCT FROM h->'inventory' OR (SELECT min(ordinal)<>0 OR max(ordinal)<>count(*)-1 FROM scribeswell.corpus_manifest_verse WHERE source_revision=revision_id) THEN
     RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
    encoded=left(scribeswell.corpus_manifest_compact(jsonb_build_array('scribeswell.manifest.v1',h->>'auditor_version',source,
     h->>'catalogue_version',h->>'versification_id',h->>'tokenization_version',h->>'source_sha256',revision_id::text,
     stage.created_by_actor_id::text,stage.attempt_id::text,stage.generation::text)),-1)||','||
     scribeswell.corpus_manifest_rows_compact(revision_id)||']';
    calculated_digest=encode(sha256(convert_to(encoded,'UTF8')),'hex');
    IF octet_length(encoded)<>(h->>'encoded_bytes')::integer OR octet_length(encoded)>67108864 OR calculated_digest<>h->>'digest' THEN
     RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publish.conflict'; END IF;
END
$body$;
"""
DDL+=r"""
CREATE FUNCTION scribeswell.corpus_manifest_rows_compact(revision_id uuid) RETURNS text
LANGUAGE sql STABLE STRICT SET search_path=pg_catalog AS $body$
 -- Called only after the owning completion validator's count, inventory and
 -- exact word-identity checks. Typed scalar JSON serialization preserves bytes;
 -- no whole-corpus JSONB reconstruction or second grammar validator is needed.
 SELECT '['||coalesce(string_agg(
  '['||to_jsonb(v.book)::text||','||v.chapter::text||','||v.verse::text||','||to_jsonb(v.verse_token_digest)::text||',['||
   coalesce((SELECT string_agg(w.item::text,',' ORDER BY w.position)
    FROM jsonb_array_elements(v.word_ids) WITH ORDINALITY w(item,position)),'')||']]',',' ORDER BY v.ordinal),'')||']'
 FROM scribeswell.corpus_manifest_verse v WHERE v.source_revision=revision_id
$body$;
REVOKE ALL ON FUNCTION scribeswell.corpus_manifest_rows_compact(uuid) FROM PUBLIC,anon,authenticated,service_role,scribeswell_runtime,scribeswell_import;

"""
def upgrade():op.get_bind().exec_driver_sql(DDL)
def downgrade():raise RuntimeError('Forward recovery only')
