"""Dormant transaction-bound writer fence; no publication or caller authority."""
revision = 'scribeswell_0002'
down_revision = 'scribeswell_0001'
branch_labels = None
depends_on = None

DDL = r"""
CREATE TABLE scribeswell.corpus_fence_control (
 singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
 enforcement boolean NOT NULL DEFAULT false
);
INSERT INTO scribeswell.corpus_fence_control VALUES (true,false);
CREATE TABLE scribeswell.corpus_epoch (
 singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
 source_id text NOT NULL CHECK (source_id ~ '^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$'),
 generation bigint NOT NULL CHECK (generation > 0),
 attempt_id uuid NOT NULL CHECK (attempt_id <> '00000000-0000-0000-0000-000000000000'::uuid),
 input_sha256 text NOT NULL CHECK (input_sha256 ~ '^[0-9a-f]{64}$'),
 state text NOT NULL CHECK (state IN ('updating','closed')),
 created_by_actor_id uuid NOT NULL CHECK (created_by_actor_id <> '00000000-0000-0000-0000-000000000000'::uuid),
 updated_by_actor_id uuid NOT NULL CHECK (updated_by_actor_id <> '00000000-0000-0000-0000-000000000000'::uuid),
 created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
 updated_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE TABLE scribeswell.corpus_write_binding (
 login name NOT NULL,
 backend_pid integer NOT NULL,
 transaction_id xid8 NOT NULL,
 source_id text NOT NULL,
 generation bigint NOT NULL,
 attempt_id uuid NOT NULL,
 input_sha256 text NOT NULL,
 PRIMARY KEY (login,backend_pid,transaction_id)
);
REVOKE ALL ON scribeswell.corpus_fence_control, scribeswell.corpus_epoch,
 scribeswell.corpus_write_binding FROM PUBLIC, anon, authenticated, service_role,
 scribeswell_runtime, scribeswell_import;
CREATE FUNCTION scribeswell.bind_corpus_write(p_source text,p_generation bigint,p_attempt uuid,p_input text)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $body$
DECLARE enabled boolean;
BEGIN
 SELECT enforcement INTO enabled FROM scribeswell.corpus_fence_control WHERE singleton FOR SHARE;
 IF NOT FOUND OR session_user <> 'scribeswell_import' THEN
  RAISE EXCEPTION USING ERRCODE='42501', MESSAGE='scribeswell_corpus_write_denied';
 END IF;
 PERFORM 1 FROM scribeswell.corpus_epoch WHERE singleton AND source_id=p_source
  AND generation=p_generation AND attempt_id=p_attempt AND input_sha256=p_input
  AND state='updating' FOR SHARE;
 IF NOT FOUND THEN
  RAISE EXCEPTION USING ERRCODE='42501', MESSAGE='scribeswell_corpus_write_denied';
 END IF;
 INSERT INTO scribeswell.corpus_write_binding
 VALUES (session_user,pg_backend_pid(),pg_current_xact_id(),p_source,p_generation,p_attempt,p_input)
 ON CONFLICT (login,backend_pid,transaction_id) DO UPDATE SET
 source_id=EXCLUDED.source_id,generation=EXCLUDED.generation,
 attempt_id=EXCLUDED.attempt_id,input_sha256=EXCLUDED.input_sha256;
END
$body$;
CREATE FUNCTION scribeswell.guard_corpus_write() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $body$
DECLARE enabled boolean;
BEGIN
 SELECT enforcement INTO enabled FROM scribeswell.corpus_fence_control WHERE singleton FOR SHARE;
 IF NOT FOUND THEN
  RAISE EXCEPTION USING ERRCODE='42501', MESSAGE='scribeswell_corpus_write_denied';
 END IF;
 IF NOT enabled THEN RETURN NULL; END IF;
 IF session_user <> 'scribeswell_import' THEN
  RAISE EXCEPTION USING ERRCODE='42501', MESSAGE='scribeswell_corpus_write_denied';
 END IF;
 PERFORM 1 FROM scribeswell.corpus_epoch e JOIN scribeswell.corpus_write_binding b
 ON b.source_id=e.source_id AND b.generation=e.generation AND b.attempt_id=e.attempt_id
 AND b.input_sha256=e.input_sha256
 WHERE e.singleton AND e.state='updating' AND b.login=session_user
 AND b.backend_pid=pg_backend_pid() AND b.transaction_id=pg_current_xact_id()
 FOR SHARE OF e;
 IF NOT FOUND THEN
  RAISE EXCEPTION USING ERRCODE='42501', MESSAGE='scribeswell_corpus_write_denied';
 END IF;
 RETURN NULL;
END
$body$;
CREATE FUNCTION scribeswell.cleanup_corpus_write_binding() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $body$
BEGIN
 DELETE FROM scribeswell.corpus_write_binding WHERE login=NEW.login
 AND backend_pid=NEW.backend_pid AND transaction_id=NEW.transaction_id;
 RETURN NULL;
END
$body$;
REVOKE ALL ON FUNCTION scribeswell.bind_corpus_write(text,bigint,uuid,text),
 scribeswell.guard_corpus_write(),scribeswell.cleanup_corpus_write_binding()
 FROM PUBLIC,anon,authenticated,service_role,scribeswell_runtime,scribeswell_import;
CREATE CONSTRAINT TRIGGER corpus_binding_cleanup AFTER INSERT ON scribeswell.corpus_write_binding
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION scribeswell.cleanup_corpus_write_binding();
ALTER TABLE scribeswell.corpus_write_binding ENABLE ALWAYS TRIGGER corpus_binding_cleanup;
"""
for table in ('book','chapter','verse','word','morpheme'):
    DDL += f"""
CREATE TRIGGER corpus_write_fence BEFORE INSERT OR UPDATE OR DELETE OR TRUNCATE
 ON scribeswell.{table} FOR EACH STATEMENT EXECUTE FUNCTION scribeswell.guard_corpus_write();
ALTER TABLE scribeswell.{table} ENABLE ALWAYS TRIGGER corpus_write_fence;
"""

def upgrade():
    from alembic import op
    op.get_bind().exec_driver_sql(DDL)

def downgrade():
    raise RuntimeError('scribeswell_downgrade_prohibited')
