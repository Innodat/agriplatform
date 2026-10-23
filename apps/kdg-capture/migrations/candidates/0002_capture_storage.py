"""Unapplied linked storage candidate, deliberately outside active versions.

Only controlled future migration execution may apply this DDL. No engines, target
configuration, seed data, role/schema provisioning or startup registration live here.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = '0002_kdg_capture_storage'
down_revision = '0001_kdg_foundation'
branch_labels = None
depends_on = None
SCHEMA = 'kdg_capture'
ZERO = '00000000-0000-0000-0000-000000000000'
# Python str.strip whitespace, including Unicode/control separators; trim only for
# the blankness predicate. Stored input is never normalized.
WHITESPACE = (*range(9, 14), *range(28, 33), 133, 160, 5760,
              *range(8192, 8203), 8232, 8233, 8239, 8287, 12288)


def nonblank(column):
    characters = ' || '.join(f'chr({value})' for value in WHITESPACE)
    return f"length(btrim({column}, {characters})) > 0"



def uid(name, nullable=False, **options):
    return sa.Column(name, UUID(), nullable=nullable, **options)


def bigint(name, **options):
    return sa.Column(name, sa.BigInteger(), nullable=False, **options)


def text(name, **options):
    return sa.Column(name, sa.Text(), nullable=False, **options)


def timestamp(name):
    return sa.Column(name, sa.DateTime(timezone=True), nullable=False,
                     server_default=sa.text('statement_timestamp()'))


def mutable_attribution():
    return [uid('created_by'), timestamp('created_at'), uid('updated_by'), timestamp('updated_at')]


def table(name, *items):
    # Plain DDL construction convenience, not an inventory verifier or runtime engine.
    checks = [sa.CheckConstraint(f"{column.name} <> '{ZERO}'::uuid",
                                name=f'ck_{name}_{column.name}_nonzero')
              for column in items if isinstance(column, sa.Column) and isinstance(column.type, UUID)]
    return op.create_table(name, *items, *checks, schema=SCHEMA)


def local_fk(columns, parent, targets, **options):
    return sa.ForeignKeyConstraint(columns, [f'{SCHEMA}.{parent}.{name}' for name in targets],
                                   ondelete='RESTRICT', **options)


def upgrade():
    table('questionnaire', uid('id', primary_key=True), uid('org_id'), uid('created_by'),
          timestamp('created_at'), sa.UniqueConstraint('org_id', 'id'))
    table('questionnaire_version', uid('id', primary_key=True), uid('org_id'),
          uid('questionnaire_id'), bigint('display_version'),
          sa.Column('definition', JSONB(), nullable=False),
          text('definition_hash'), uid('published_by'), timestamp('published_at'),
          sa.UniqueConstraint('org_id', 'questionnaire_id', 'id'),
          sa.UniqueConstraint('org_id', 'questionnaire_id', 'display_version'),
          local_fk(['org_id', 'questionnaire_id'], 'questionnaire', ['org_id', 'id']),
          sa.CheckConstraint('display_version > 0'),
          sa.CheckConstraint("definition_hash ~ '^[0-9a-f]{64}$'"),
          sa.CheckConstraint("jsonb_typeof(definition) = 'object' AND octet_length(definition::text) <= 131072"))
    table('child', uid('id', primary_key=True), uid('org_id'), text('display_name'),
          sa.Column('active', sa.Boolean(), nullable=False), bigint('revision'),
          *mutable_attribution(), sa.UniqueConstraint('org_id', 'id'),
          sa.CheckConstraint('revision > 0'),
          sa.CheckConstraint(nonblank('display_name') + ' AND length(display_name) <= 200'))
    table('child_assignment', uid('id', primary_key=True), uid('org_id'), uid('child_id'),
          uid('account_id'), bigint('membership_id'),
          sa.Column('active', sa.Boolean(), nullable=False), bigint('revision'),
          *mutable_attribution(), sa.UniqueConstraint('org_id', 'id', 'child_id', 'account_id'),
          sa.UniqueConstraint('org_id', 'child_id', 'account_id'),
          local_fk(['org_id', 'child_id'], 'child', ['org_id', 'id']),
          sa.CheckConstraint('membership_id > 0 AND revision > 0'))
    table('child_eligibility', uid('org_id', primary_key=True), text('ref', primary_key=True),
          uid('account_id'), bigint('membership_id'), uid('child_id'), bigint('child_revision'),
          sa.Column('observed_active', sa.Boolean(), nullable=False), text('create_permission'),
          uid('assignment_id', nullable=True),
          sa.Column('assignment_revision', sa.BigInteger(), nullable=True),
          uid('issued_by'), timestamp('issued_at'),
          sa.UniqueConstraint('org_id', 'ref', 'account_id', 'membership_id', 'child_id'),
          local_fk(['org_id', 'child_id'], 'child', ['org_id', 'id']),
          local_fk(['org_id', 'assignment_id', 'child_id', 'account_id'], 'child_assignment',
                   ['org_id', 'id', 'child_id', 'account_id']),
          sa.CheckConstraint('membership_id > 0 AND child_revision > 0 AND observed_active'),
          sa.CheckConstraint(nonblank('ref') + ' AND length(ref) <= 200'),
          sa.CheckConstraint("(create_permission = 'kdg_capture.capture.create.assigned' "
                             'AND assignment_id IS NOT NULL AND assignment_revision IS NOT NULL AND assignment_revision > 0) OR '
                             "(create_permission = 'kdg_capture.capture.create.all' "
                             'AND assignment_id IS NULL AND assignment_revision IS NULL)'))
    table('capture', uid('id', primary_key=True), uid('org_id'), uid('child_id'),
          uid('questionnaire_id'), uid('questionnaire_version_id'), uid('owner_account_id'),
          uid('owner_actor_id'), text('child_eligibility_ref'), bigint('creator_membership_id'),
          sa.Column('observation_date', sa.Date(), nullable=False),
          sa.Column('answers', JSONB(), nullable=False), text('captured_at'), bigint('revision'),
          *mutable_attribution(),
          sa.UniqueConstraint('org_id', 'id'),
          sa.UniqueConstraint('org_id', 'id', 'owner_account_id', 'owner_actor_id',
                              'child_id', 'questionnaire_id', 'questionnaire_version_id'),
          local_fk(['org_id', 'child_id'], 'child', ['org_id', 'id']),
          local_fk(['org_id', 'questionnaire_id', 'questionnaire_version_id'],
                   'questionnaire_version', ['org_id', 'questionnaire_id', 'id']),
          local_fk(['org_id', 'child_eligibility_ref', 'owner_account_id', 'creator_membership_id', 'child_id'],
                   'child_eligibility', ['org_id', 'ref', 'account_id', 'membership_id', 'child_id']),
          sa.CheckConstraint('revision > 0 AND creator_membership_id > 0'),
          sa.CheckConstraint("observation_date BETWEEN DATE '0001-01-01' AND DATE '9999-12-31'"),
          sa.CheckConstraint("jsonb_typeof(answers) = 'object' AND octet_length(answers::text) <= 131072"),
          sa.CheckConstraint("captured_at ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt]([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]+)?([Zz]|\\+00:00)$' "
                             'AND captured_at::timestamptz IS NOT NULL'))
    table('operation_outcome', uid('id', primary_key=True), uid('org_id'),
          uid('executor_account_id'), uid('executor_actor_id'), text('command_type'),
          uid('operation_id'), sa.Column('command_version', sa.Integer(), nullable=False),
          sa.Column('result_version', sa.Integer(), nullable=False),
          sa.Column('result', JSONB(), nullable=False), uid('initiator_actor_id', nullable=True),
          timestamp('committed_at'),
          sa.Column('capture_id', UUID(), sa.Computed("(result->>'capture_id')::uuid", persisted=True), nullable=False),
          sa.Column('result_revision', sa.BigInteger(), sa.Computed("(result->>'revision')::bigint", persisted=True), nullable=False),
          sa.UniqueConstraint('org_id', 'executor_account_id', 'command_type', 'operation_id'),
          sa.UniqueConstraint('org_id', 'id', 'executor_account_id', 'executor_actor_id',
                              'command_type', 'operation_id', 'capture_id', 'result_revision'),
          local_fk(['org_id', 'capture_id'], 'capture', ['org_id', 'id']),
          sa.CheckConstraint('id <> operation_id AND command_version > 0 AND result_version > 0 AND result_revision > 0'),
          sa.CheckConstraint("command_type IN ('capture.create', 'capture.edit')"),
          sa.CheckConstraint("command_type <> 'capture.create' OR result_revision = 1"),
          sa.CheckConstraint("jsonb_typeof(result) = 'object' AND octet_length(result::text) <= 8192 "
                             "AND result - 'capture_id' - 'revision' = '{}'::jsonb "
                             "AND jsonb_typeof(result->'capture_id') = 'string' "
                             "AND jsonb_typeof(result->'revision') = 'string' "
                             "AND result->>'capture_id' = capture_id::text "
                             "AND result->>'revision' = result_revision::text"))
    op.create_index('uq_capture_create_outcome', 'operation_outcome', ['org_id', 'capture_id'],
                    schema=SCHEMA, unique=True,
                    postgresql_where=sa.text("command_type = 'capture.create'"))
    table('capture_revision', uid('org_id', primary_key=True), uid('capture_id', primary_key=True),
          bigint('revision', primary_key=True), uid('owner_account_id'), uid('owner_actor_id'),
          uid('child_id'), uid('questionnaire_id'), uid('questionnaire_version_id'),
          sa.Column('observation_date', sa.Date(), nullable=False),
          sa.Column('answers', JSONB(), nullable=False), text('captured_at'),
          uid('executor_account_id'), uid('executor_actor_id'),
          uid('initiator_actor_id', nullable=True), uid('outcome_id'),
          text('command_type'), uid('operation_id'), timestamp('created_at'),
          sa.UniqueConstraint('outcome_id'),
          local_fk(['org_id', 'capture_id', 'owner_account_id', 'owner_actor_id', 'child_id',
                    'questionnaire_id', 'questionnaire_version_id'], 'capture',
                   ['org_id', 'id', 'owner_account_id', 'owner_actor_id', 'child_id',
                    'questionnaire_id', 'questionnaire_version_id']),
          local_fk(['org_id', 'outcome_id', 'executor_account_id', 'executor_actor_id',
                    'command_type', 'operation_id', 'capture_id', 'revision'], 'operation_outcome',
                   ['org_id', 'id', 'executor_account_id', 'executor_actor_id',
                    'command_type', 'operation_id', 'capture_id', 'result_revision']),
          sa.CheckConstraint("(revision = 1 AND command_type = 'capture.create') OR "
                             "(revision > 1 AND command_type = 'capture.edit')"),
          sa.CheckConstraint("jsonb_typeof(answers) = 'object' AND octet_length(answers::text) <= 131072"))
    op.create_foreign_key('fk_capture_current_revision', 'capture', 'capture_revision',
                          ['org_id', 'id', 'revision'], ['org_id', 'capture_id', 'revision'],
                          source_schema=SCHEMA, referent_schema=SCHEMA,
                          ondelete='RESTRICT', deferrable=True, initially='DEFERRED')
    op.create_foreign_key('fk_outcome_reported_revision', 'operation_outcome', 'capture_revision',
                          ['org_id', 'capture_id', 'result_revision'], ['org_id', 'capture_id', 'revision'],
                          source_schema=SCHEMA, referent_schema=SCHEMA,
                          ondelete='RESTRICT', deferrable=True, initially='DEFERRED')
    _guards()
    _access()


def _guards():
    op.execute('''CREATE FUNCTION kdg_capture.reject_immutable_change() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog AS $$
BEGIN RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = 'immutable_record'; END $$''')
    for name in ('questionnaire', 'questionnaire_version', 'child_eligibility',
                 'operation_outcome', 'capture_revision'):
        op.execute(f'CREATE TRIGGER immutable_record BEFORE UPDATE OR DELETE ON kdg_capture.{name} '
                   'FOR EACH ROW EXECUTE FUNCTION kdg_capture.reject_immutable_change()')
    op.execute('''CREATE FUNCTION kdg_capture.stamp_capture() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog AS $$
DECLARE actor uuid := current_setting('app.actor_id', true)::uuid;
BEGIN
 IF actor IS NULL THEN RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = 'invalid_actor'; END IF;
 IF TG_OP = 'INSERT' THEN
  IF NEW.revision <> 1 OR NEW.owner_actor_id <> actor THEN
   RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = 'invalid_creation'; END IF;
  NEW.created_by := actor; NEW.created_at := statement_timestamp();
 ELSE
  IF ROW(NEW.id,NEW.org_id,NEW.owner_account_id,NEW.owner_actor_id,NEW.child_id,
         NEW.questionnaire_id,NEW.questionnaire_version_id,NEW.child_eligibility_ref,
         NEW.creator_membership_id,NEW.captured_at,NEW.created_by,NEW.created_at)
     IS DISTINCT FROM
     ROW(OLD.id,OLD.org_id,OLD.owner_account_id,OLD.owner_actor_id,OLD.child_id,
         OLD.questionnaire_id,OLD.questionnaire_version_id,OLD.child_eligibility_ref,
         OLD.creator_membership_id,OLD.captured_at,OLD.created_by,OLD.created_at) THEN
   RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = 'immutable_capture_facts'; END IF;
  IF ROW(NEW.observation_date,NEW.answers) IS NOT DISTINCT FROM ROW(OLD.observation_date,OLD.answers) THEN
   IF NEW.revision <> OLD.revision THEN
    RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = 'invalid_revision'; END IF;
   RETURN OLD;
  END IF;
  IF NEW.revision <> OLD.revision + 1 THEN
   RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = 'invalid_revision'; END IF;
 END IF;
 NEW.updated_by := actor; NEW.updated_at := statement_timestamp();
 RETURN NEW;
END $$''')
    op.execute('CREATE TRIGGER stamp_capture BEFORE INSERT OR UPDATE ON kdg_capture.capture '
               'FOR EACH ROW EXECUTE FUNCTION kdg_capture.stamp_capture()')
    # History/outcome executor identity is checked by RLS; server replaces supplied time.
    op.execute('''CREATE FUNCTION kdg_capture.stamp_evidence_time() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog AS $$
BEGIN
 IF TG_TABLE_NAME = 'operation_outcome' THEN NEW.committed_at := statement_timestamp();
 ELSE
  IF NOT EXISTS (SELECT 1 FROM kdg_capture.capture c
                  WHERE c.org_id = NEW.org_id AND c.id = NEW.capture_id
                    AND ROW(c.revision,c.observation_date,c.answers,c.captured_at,c.updated_by)
                        IS NOT DISTINCT FROM
                        ROW(NEW.revision,NEW.observation_date,NEW.answers,NEW.captured_at,NEW.executor_actor_id)) THEN
   RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = 'history_snapshot_invalid'; END IF;
  IF NOT EXISTS (SELECT 1 FROM kdg_capture.operation_outcome o
                  WHERE o.org_id = NEW.org_id AND o.id = NEW.outcome_id
                    AND o.initiator_actor_id IS NOT DISTINCT FROM NEW.initiator_actor_id) THEN
   RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = 'history_initiator_invalid'; END IF;
  NEW.created_at := statement_timestamp();
 END IF;
 RETURN NEW;
END $$''')
    for name in ('operation_outcome', 'capture_revision'):
        op.execute(f'CREATE TRIGGER stamp_evidence_time BEFORE INSERT ON kdg_capture.{name} '
                   'FOR EACH ROW EXECUTE FUNCTION kdg_capture.stamp_evidence_time()')
    op.execute('''CREATE FUNCTION kdg_capture.require_capture_snapshot() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog AS $$
BEGIN
 IF TG_OP = 'UPDATE' AND NEW.revision = OLD.revision THEN RETURN NULL; END IF;
 IF NOT EXISTS (SELECT 1 FROM kdg_capture.capture_revision r
                WHERE r.org_id = NEW.org_id AND r.capture_id = NEW.id
                  AND ROW(r.revision,r.observation_date,r.answers,r.captured_at,r.executor_actor_id)
                      IS NOT DISTINCT FROM
                      ROW(NEW.revision,NEW.observation_date,NEW.answers,NEW.captured_at,NEW.updated_by)) THEN
  RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = 'capture_snapshot_missing'; END IF;
 RETURN NULL;
END $$''')
    op.execute('CREATE CONSTRAINT TRIGGER capture_snapshot_present AFTER INSERT OR UPDATE '
               'ON kdg_capture.capture DEFERRABLE INITIALLY DEFERRED FOR EACH ROW '
               'EXECUTE FUNCTION kdg_capture.require_capture_snapshot()')
    for function in ('reject_immutable_change', 'stamp_capture', 'stamp_evidence_time', 'require_capture_snapshot'):

        op.execute(f'REVOKE ALL ON FUNCTION kdg_capture.{function}() FROM PUBLIC,kdg_capture_runtime,kdg_capture_operator')


def _access():
    org = "org_id = current_setting('app.org_id', true)::uuid"
    account = "current_setting('app.account_id', true)::uuid"
    actor = "current_setting('app.actor_id', true)::uuid"
    mode = "current_setting('app.mode', true)"
    scope = f"({org} AND {account} IS NOT NULL AND {actor} IS NOT NULL AND {mode} IN ('own_read','all_read','own_write','all_write'))"
    write = f"{mode} IN ('own_write','all_write')"
    all_mode = f"{mode} IN ('all_read','all_write')"
    names = ('questionnaire', 'questionnaire_version', 'child', 'child_assignment',
             'child_eligibility', 'capture', 'operation_outcome', 'capture_revision')
    for name in names:
        op.execute(f'REVOKE ALL ON kdg_capture.{name} FROM PUBLIC,kdg_capture_runtime,kdg_capture_operator')
        op.execute(f'ALTER TABLE kdg_capture.{name} ENABLE ROW LEVEL SECURITY')
        op.execute(f'ALTER TABLE kdg_capture.{name} FORCE ROW LEVEL SECURITY')
        if name in ('capture', 'capture_revision'):
            read = f'{scope} AND (owner_account_id = {account} OR {all_mode})'
        elif name == 'child_assignment':
            read = f'{scope} AND (account_id = {account} OR {all_mode})'
        elif name == 'child_eligibility':
            read = f'{scope} AND account_id = {account}'
        elif name == 'operation_outcome':
            read = f'{scope} AND executor_account_id = {account}'
        else:
            read = scope
        op.execute(f'GRANT SELECT ON kdg_capture.{name} TO kdg_capture_runtime')
        op.execute(f'CREATE POLICY runtime_read ON kdg_capture.{name} FOR SELECT TO kdg_capture_runtime USING ({read})')
    capture_write = f'{scope} AND {write} AND (owner_account_id = {account} OR {mode} = \'all_write\')'
    op.execute('GRANT INSERT ON kdg_capture.capture,kdg_capture.operation_outcome,kdg_capture.capture_revision TO kdg_capture_runtime')
    op.execute('GRANT UPDATE (observation_date,answers,revision) ON kdg_capture.capture TO kdg_capture_runtime')
    op.execute(f'CREATE POLICY runtime_create ON kdg_capture.capture FOR INSERT TO kdg_capture_runtime '
               f'WITH CHECK ({scope} AND {write} AND owner_account_id = {account} AND owner_actor_id = {actor})')
    op.execute(f'CREATE POLICY runtime_update ON kdg_capture.capture FOR UPDATE TO kdg_capture_runtime '
               f'USING ({capture_write}) WITH CHECK ({capture_write})')
    for name in ('operation_outcome', 'capture_revision'):
        check = f'{scope} AND {write} AND executor_account_id = {account} AND executor_actor_id = {actor}'
        if name == 'operation_outcome':
            check += (f' AND EXISTS (SELECT 1 FROM kdg_capture.capture c '
                      f'WHERE c.org_id = operation_outcome.org_id AND c.id = operation_outcome.capture_id '
                      f'AND (c.owner_account_id = {account} OR {mode} = \'all_write\'))')
        if name == 'capture_revision':
            check += f' AND (owner_account_id = {account} OR {mode} = \'all_write\')'
        op.execute(f'CREATE POLICY runtime_append ON kdg_capture.{name} FOR INSERT TO kdg_capture_runtime WITH CHECK ({check})')


def downgrade():
    raise RuntimeError('kdg_migration_downgrade_prohibited')
