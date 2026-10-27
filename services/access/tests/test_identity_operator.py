"""Owner-local command adapter acceptance; actual-login proof lives in qualifier."""
import importlib.util
from pathlib import Path
import sys
from datetime import datetime, timezone
from dataclasses import FrozenInstanceError
import hashlib
import json

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_account_actor_ensure_dispatch_and_scoped_recovery():
    import identity_operator as o
    from test_identity_operator_input import document, encode
    value = document('account_actor.ensure')
    class AccountConnection(Connection):
        def one_or_none(self):
            return ({'target':{k:value['payload'][k].lower() for k in ('account_id','actor_id')},
                'disposition':'created','revision':None,
                'event_id':'d1234567-1234-1234-1234-123456789abc'},1,1,datetime.now(timezone.utc))
    c=AccountConnection()
    receipt=o.execute(c,encode(value))
    assert c.committed and receipt.result.command=='account_actor.ensure'
    assert receipt.result.target.account_id==value['payload']['account_id'].lower()
    assert 'identity.ensure_account_actor' in c.calls[-1][0]
    lookup=AccountConnection()
    assert o.outcome(lookup,value['operation_id'],command='account_actor.ensure',
        account_id=value['payload']['account_id']).result==receipt.result
    assert 'identity.account_actor_outcome' in lookup.calls[-1][0]


def document():
    return dict(schema_version=1, operation_id='A1234567-1234-1234-1234-123456789ABC',
        command='actor.register_system',scope={'kind':'platform'},reason_code='synthetic_fixture',
        payload=dict(actor_id='B1234567-1234-1234-1234-123456789ABC',kind='service',
                     actor_key='synthetic:test',display_name='é\n\t\x0f🙂',expected_absent=True))


def test_complete_normalized_jcs_and_write_lock():
    import identity_operator as o
    value=document(); parsed=o.parse_command(json.dumps(value).encode())
    expected={**value,'operation_id':value['operation_id'].lower(),'evidence_ref':None,
              'payload':{**value['payload'],'actor_id':value['payload']['actor_id'].lower()}}
    assert o.canonical_command(parsed)==json.dumps(expected,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    lock={'lock_version':1,'owner_schema':'identity','scope_kind':'platform','scope_id':None,
          'caller_kind':'actor','caller_id':expected['payload']['actor_id'],
          'command_type':'actor.register_system','operation_id':expected['operation_id']}
    raw=json.dumps(lock,sort_keys=True,separators=(',',':')).encode()
    assert o.outcome_lock_key(lock['caller_id'].upper(),lock['operation_id'].upper())==int.from_bytes(hashlib.sha256(raw).digest()[:8],'big',signed=True)


class Connection:
    def __init__(self, *, busy=False, isolation='READ COMMITTED', failure=None, commit_failure=False, missing=False):
        self.busy=busy;self.isolation=isolation;self.failure=failure
        self.commit_failure=commit_failure;self.missing=missing;self.calls=[];self.committed=False;self.rolled_back=False
    def in_transaction(self):return self.busy
    def get_isolation_level(self):return self.isolation
    def begin(self):return self
    def __enter__(self):return self
    def __exit__(self,kind,value,trace):
        self.rolled_back=kind is not None
        if self.commit_failure:raise RuntimeError('PRIVATE SQL COMMIT')
        self.committed=kind is None
    def execute(self,sql,params):
        self.calls.append((str(sql),params))
        if 'set_config' not in str(sql) and self.failure:raise self.failure
        return self
    def one_or_none(self):
        if self.missing:return None
        return ({'target':{'actor_id':document()['payload']['actor_id'].lower()},'disposition':'created',
                'revision':None,'event_id':'c1234567-1234-1234-1234-123456789abc'},1,1,datetime.now(timezone.utc))


def test_receipt_only_after_commit_frozen_and_bound_settings():
    import identity_operator as o
    c=Connection();receipt=o.execute(c,json.dumps(document()).encode())
    assert c.committed and receipt.result.target.actor_id==document()['payload']['actor_id'].lower()
    assert c.calls[0][1]=={'name':'statement_timeout','value':'5000ms'}
    assert c.calls[1][1]=={'name':'lock_timeout','value':'2000ms'}
    with pytest.raises(FrozenInstanceError):receipt.result.disposition='other'
    with pytest.raises(FrozenInstanceError):receipt.result.target.actor_id='other'


@pytest.mark.parametrize('busy,isolation,code',[(True,'READ COMMITTED','connection_busy'),(False,'SERIALIZABLE','isolation_unsupported'),(False,'AUTOCOMMIT','isolation_unsupported')])
def test_busy_and_isolation_refuse_without_sql(busy,isolation,code):
    import identity_operator as o
    c=Connection(busy=busy,isolation=isolation)
    with pytest.raises(o.OperatorError) as error:o.execute(c,json.dumps(document()).encode())
    assert error.value.code==code and not c.calls


@pytest.mark.parametrize('surface',['option','driver'])
def test_autocommit_rejects_even_when_getter_reports_read_committed(surface):
    import identity_operator as o
    from types import SimpleNamespace
    c=Connection()
    if surface=='option':c.get_execution_options=lambda:{'isolation_level':'AUTOCOMMIT'}
    else:c.connection=SimpleNamespace(driver_connection=SimpleNamespace(autocommit=True))
    with pytest.raises(o.OperatorError) as error:o.execute(c,json.dumps(document()).encode())
    assert error.value.code=='isolation_unsupported' and not c.calls


@pytest.mark.parametrize('state,code',[('IC001','operation_busy'),('55P03','operation_unavailable'),('57014','operation_unavailable'),('IC002','access_denied'),('42501','access_denied'),('IC003','operation_conflict'),('IC004','operation_verification_unavailable'),('XX000','operation_unavailable')])
def test_only_exact_outcome_wait_is_busy_and_no_error_chain(state,code):
    import identity_operator as o
    class DriverError(RuntimeError):sqlstate=state
    class DatabaseError(RuntimeError):orig=DriverError('PRIVATE DRIVER SQL')
    c=Connection(failure=DatabaseError('PRIVATE SQL VALUES'))
    with pytest.raises(o.OperatorError) as error:o.execute(c,json.dumps(document()).encode())
    assert error.value.code==code and error.value.operation_id==document()['operation_id'].lower()
    assert error.value.__context__ is None and error.value.__cause__ is None
    assert 'PRIVATE' not in repr(error.value) and c.rolled_back


def test_commit_uncertainty_and_missing_outcome_are_truthful():
    import identity_operator as o
    with pytest.raises(o.OperatorError) as error:o.execute(Connection(commit_failure=True),json.dumps(document()).encode())
    assert error.value.code=='operation_unavailable' and error.value.operation_id==document()['operation_id'].lower()
    assert o.outcome(Connection(missing=True),document()['operation_id']) is None


def test_deadline_includes_parsing_and_no_sql_when_expired(monkeypatch):
    import identity_operator as o
    clock=iter([0,11]);monkeypatch.setattr(o.time,'monotonic',lambda:next(clock))
    c=Connection()
    with pytest.raises(o.OperatorError) as error:o.execute(c,json.dumps(document()).encode())
    assert error.value.code=='operation_unavailable' and not c.calls and c.rolled_back


@pytest.mark.parametrize('setup_return',[9.25,11.0])
def test_delayed_setup_rechecks_deadline_and_refreshes_dispatch_budget(monkeypatch,setup_return):
    import identity_operator as o
    clock=[0.0];monkeypatch.setattr(o.time,'monotonic',lambda:clock[0])
    class DelayedSetup(Connection):
        def execute(self,sql,params):
            result=super().execute(sql,params)
            if len(self.calls)==2:clock[0]=setup_return
            return result
    c=DelayedSetup()
    if setup_return>10:
        with pytest.raises(o.OperatorError) as error:o.execute(c,json.dumps(document()).encode())
        assert error.value.code=='operation_unavailable' and c.rolled_back
        assert len(c.calls)==2 and all('set_config' in sql for sql,_ in c.calls)
    else:
        assert o.execute(c,json.dumps(document()).encode()).status=='committed'
        assert c.calls[2][1]=={'statement':'750ms','lock':'750ms'}
        assert 'register_system' in c.calls[3][0]


@pytest.mark.parametrize('mutate',[lambda r:r[0].update(secret='PRIVATE'),lambda r:r[0].update(revision='1'),lambda r:r[0].update(event_id=None),lambda r:r.__setitem__(1,2)])
def test_receipt_strict_verification(mutate):
    import identity_operator as o
    row=list(Connection().one_or_none());mutate(row)
    with pytest.raises(o.OperatorError) as error:o._receipt(row,document()['operation_id'])
    assert error.value.code=='operation_verification_unavailable'


@pytest.mark.parametrize('kind', ['actor.register_system', 'account_actor.ensure',
                                 'membership.join', 'membership.retire'])
def test_typed_retry_identity_matches_complete_normalized_wire_contract(kind):
    import identity_operator as o
    from test_identity_operator_input import document, encode
    value = document(kind)
    value['operation_id'] = value['operation_id'].upper()
    for name in ('actor_id', 'account_id'):
        if name in value['payload']:
            value['payload'][name] = value['payload'][name].upper()
    if kind.startswith('membership.'):
        value['scope']['org_id'] = value['scope']['org_id'].upper()
    if kind == 'membership.retire':
        value['payload'].update(membership_id='9223372036854775807',
                                expected_revision='9007199254740993')
    if 'display_name' in value['payload']:
        value['payload']['display_name'] = 'é\n\t🙂'
    expected = json.loads(encode(value))
    expected['operation_id'] = expected['operation_id'].lower()
    for name in ('actor_id', 'account_id'):
        if name in expected['payload']:
            expected['payload'][name] = expected['payload'][name].lower()
    if kind.startswith('membership.'):
        expected['scope']['org_id'] = expected['scope']['org_id'].lower()
    if kind == 'membership.join':
        expected['payload']['is_owner'] = False
    parsed = o.parse_command(encode(value))
    raw = json.dumps(expected, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    assert o.canonical_command(parsed) == raw
    # Frozen independent stdlib-JSON/SHA-256 vectors for these exact fixtures.
    vectors = {
        'actor.register_system': ('07314c3107f4e58cf72a7eae4d39ca1f96fbbb67674a24ae336fef975d4e0c71', 891613029337455570),
        'account_actor.ensure': ('6a4279cdccc050b115d33c9c746522b4f3b7d8e1502c31770e9944fa4a74c729', 3663822995255640307),
        'membership.join': ('46adf94682cc69ede6e3fe0634984a5adda58e2d70f74dc2bea152828fe7aaa7', -7083049822897689957),
        'membership.retire': ('b51843604f3b66dea6805cfbba72537a8f865cee33eddbcf17277e7afb94fb67', 2367746705605816951),
    }
    assert hashlib.sha256(o.canonical_command(parsed)).hexdigest() == vectors[kind][0]
    assert o.canonical_command(o.parse_command(encode(expected))) == raw
    executor = 'B1234567-1234-1234-1234-123456789ABC'
    lock = dict(lock_version=1, owner_schema='identity', scope_kind=expected['scope']['kind'],
                scope_id=expected['scope'].get('org_id'), caller_kind='actor',
                caller_id=executor.lower(), command_type=kind,
                operation_id=expected['operation_id'])
    lock_bytes = json.dumps(lock, sort_keys=True, separators=(',', ':')).encode()
    assert o.command_outcome_lock_key(executor, parsed) == vectors[kind][1]
    assert o.command_outcome_lock_key(executor, parsed) == int.from_bytes(
        hashlib.sha256(lock_bytes).digest()[:8], 'big', signed=True)
    assert o.command_outcome_lock_key(executor.lower(), o.parse_command(encode(expected))) == o.command_outcome_lock_key(executor, parsed)
    if kind == 'actor.register_system':
        assert o.command_outcome_lock_key(executor, parsed) == o.outcome_lock_key(executor, parsed.operation_id)


def test_retry_key_binds_namespace_but_fingerprint_binds_payload():
    import identity_operator as o
    from test_identity_operator_input import document, encode
    from copy import deepcopy
    executor = 'b1234567-1234-1234-1234-123456789abc'
    value = document('membership.join')
    parsed = o.parse_command(encode(value))
    key = o.command_outcome_lock_key(executor, parsed)
    for field, replacement in [('account_id', executor),
                               ('expected_previous_membership_id', '9223372036854775807'),
                               ('is_owner', True)]:
        changed = deepcopy(value)
        changed['payload'][field] = replacement
        other = o.parse_command(encode(changed))
        assert o.canonical_command(other) != o.canonical_command(parsed)
        assert o.command_outcome_lock_key(executor, other) == key
    for field, replacement in [('reason_code', 'setup_correction'),
                               ('evidence_ref', 'setup:fixture/2')]:
        changed = deepcopy(value)
        changed[field] = replacement
        other = o.parse_command(encode(changed))
        assert o.canonical_command(other) != o.canonical_command(parsed)
        assert o.command_outcome_lock_key(executor, other) == key
    changed_org = deepcopy(value)
    changed_org['scope']['org_id'] = executor
    changed_operation = deepcopy(value)
    changed_operation['operation_id'] = executor
    keys = [key, o.command_outcome_lock_key(value['operation_id'], parsed)]
    keys += [o.command_outcome_lock_key(executor, o.parse_command(encode(v)))
             for v in (changed_org, changed_operation, document('membership.retire'),
                       document('account_actor.ensure'), document('actor.register_system'))]
    assert len(set(keys)) == len(keys)


@pytest.mark.parametrize('kind,field,replacement', [
    ('account_actor.ensure', 'account_id', 'c1234567-1234-1234-1234-123456789abc'),
    ('account_actor.ensure', 'actor_id', 'c1234567-1234-1234-1234-123456789abc'),
    ('account_actor.ensure', 'display_name', 'Changed account'),
    ('membership.retire', 'membership_id', '9223372036854775807'),
    ('membership.retire', 'expected_revision', '9007199254740993'),
])
def test_other_typed_payload_conflicts_share_retry_key(kind, field, replacement):
    import identity_operator as o
    from test_identity_operator_input import document, encode
    value = document(kind)
    original = o.parse_command(encode(value))
    value['payload'][field] = replacement
    changed = o.parse_command(encode(value))
    executor = 'c1234567-1234-1234-1234-123456789abc'
    assert o.canonical_command(original) != o.canonical_command(changed)
    assert o.command_outcome_lock_key(executor, original) == o.command_outcome_lock_key(executor, changed)


@pytest.mark.parametrize('kind', ['actor.register_system', 'account_actor.ensure'])
def test_canonical_strings_preserve_distinct_unicode_normalization_forms(kind):
    import identity_operator as o
    from test_identity_operator_input import document, encode
    value = document(kind)
    value['payload']['display_name'] = 'é'
    composed = o.parse_command(encode(value))
    value['payload']['display_name'] = 'e\u0301'
    decomposed = o.parse_command(encode(value))
    composed_bytes = o.canonical_command(composed)
    decomposed_bytes = o.canonical_command(decomposed)
    assert composed_bytes != decomposed_bytes
    assert json.loads(composed_bytes)['payload']['display_name'] == 'é'
    assert json.loads(decomposed_bytes)['payload']['display_name'] == 'e\u0301'
    executor = 'c1234567-1234-1234-1234-123456789abc'
    assert o.command_outcome_lock_key(executor, composed) == o.command_outcome_lock_key(executor, decomposed)


def test_join_dispatch_and_created_receipt():
    import identity_operator as o
    from test_identity_operator_input import document, encode
    class JoinConnection(Connection):
        def one_or_none(self):
            return ({'target':{'org_id':'c1234567-1234-1234-1234-123456789abc',
                'account_id':'b1234567-1234-1234-1234-123456789abc','membership_id':'91'},
                'disposition':'created','revision':'1','event_id':'d1234567-1234-1234-1234-123456789abc'},
                1,1,datetime.now(timezone.utc))
    c=JoinConnection()
    receipt=o.execute(c,encode(document('membership.join')))
    assert receipt.result.command=='membership.join' and receipt.result.disposition=='created'
    assert receipt.result.revision=='1' and c.committed
    assert 'identity.join_membership' in c.calls[-1][0]
    lookup=JoinConnection()
    assert o.outcome(lookup,document('membership.join')['operation_id'],command='membership.join',
        org_id='c1234567-1234-1234-1234-123456789abc',account_id='b1234567-1234-1234-1234-123456789abc').result==receipt.result
    assert 'identity.membership_join_outcome' in lookup.calls[-1][0]

@pytest.mark.parametrize('mutation', [
    lambda r:r['target'].update(account_id='00000000-0000-0000-0000-000000000000'),
    lambda r:r['target'].update(actor_id='B1234567-1234-1234-1234-123456789ABC'),
    lambda r:r['target'].update(extra='PRIVATE'),
    lambda r:r.update(revision='1'),
    lambda r:r.update(event_id=None),
    lambda r:r.update(disposition='changed'),
])
def test_account_actor_receipt_refuses_malformed_storage(mutation):
    import identity_operator as o
    result=dict(target=dict(account_id='a1234567-1234-1234-1234-123456789abc',
        actor_id='b1234567-1234-1234-1234-123456789abc'),disposition='created',revision=None,
        event_id='c1234567-1234-1234-1234-123456789abc')
    mutation(result)
    with pytest.raises(o.OperatorError,match='operation_verification_unavailable'):
        o._receipt((result,1,1,datetime.now(timezone.utc)),'a1234567-1234-1234-1234-123456789abc','account_actor.ensure')


@pytest.mark.parametrize('context', [dict(),dict(account_id=None),
    dict(account_id='00000000-0000-0000-0000-000000000000'),
    dict(account_id='b1234567-1234-1234-1234-123456789abc',org_id='c1234567-1234-1234-1234-123456789abc')])
def test_account_actor_lookup_requires_exact_platform_account_context(context):
    import identity_operator as o
    c=Connection()
    with pytest.raises(o.OperatorError,match='command_invalid'):
        o.outcome(c,'a1234567-1234-1234-1234-123456789abc',command='account_actor.ensure',**context)
    assert not c.calls
