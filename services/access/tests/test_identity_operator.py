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


def test_adapter_exists_and_rejects_unimplemented_command_before_sql():
    import identity_operator as operator
    from test_identity_operator_input import document, encode
    class Connection:
        def execute(self, *args):
            raise AssertionError('SQL must not execute')
    with pytest.raises(operator.OperatorError) as error:
        operator.execute(Connection(), encode(document('membership.join')))
    assert error.value.code == 'command_unsupported'


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


@pytest.mark.parametrize('state,code',[('IC001','operation_busy'),('55P03','operation_unavailable'),('57014','operation_unavailable'),('IC002','access_denied'),('IC003','operation_conflict'),('IC004','operation_verification_unavailable'),('XX000','operation_unavailable')])
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
