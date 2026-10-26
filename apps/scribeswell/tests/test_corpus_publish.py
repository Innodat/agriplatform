"""Controlled publication protocol; doubles never qualify native permissions."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
import corpus_publish as publisher


def test_stable_suboperation_identity():
    operation = '11111111-1111-4111-8111-111111111111'
    assert publisher.suboperation_id(operation, 'revision') == publisher.suboperation_id(operation, 'revision')
    assert publisher.suboperation_id(operation, 'revision') != publisher.suboperation_id(operation, 'complete')

from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
import pytest
from corpus_manifest import ManifestCandidate, VerseCandidate
from test_corpus_publication_input import command, encode, source_bytes

OPERATION='44444444-4444-4444-8444-444444444444'
ACTOR='22222222-2222-4222-8222-222222222222'


class Rows:
    def __init__(self,value): self.value=value
    def fetchone(self): return (self.value,)


class Connection:
    def __init__(self):
        self.row_factory=object(); self.events=[]; self.outcomes={}; self.fail=None
        self.pending=None; self.lost=set(); self.denied=False
    @contextmanager
    def transaction(self):
        self.events.append('begin'); self.pending=None
        try:
            yield
            if self.pending:
                request,receipt=self.pending
                if self.fail==request['command']:
                    raise RuntimeError('private-driver-marker')
                self.outcomes[request['operation_id']]=(deepcopy(request),receipt)
                self.events.append('commit:'+request['command'])
                if request['command'] in self.lost:
                    self.lost.remove(request['command'])
                    raise RuntimeError('private-lost-ack')
        finally: self.pending=None
    def execute(self,sql,params=None):
        if params is None: return Rows(None)
        if self.denied:
            error=RuntimeError('private-denial'); error.sqlstate='42501'; raise error
        request=deepcopy(params[0].obj); self.events.append(request['command'])
        self.events.append('lookup' if 'lookup_' in sql else 'execute')
        previous=self.outcomes.get(request['operation_id'])
        if previous:
            if previous[0]!=request:
                error=RuntimeError('private-conflict');error.sqlstate='P0001';raise error
            return Rows(previous[1])
        if 'lookup_' in sql: return Rows(None)
        receipt=dict(version=1,operation_id=request['operation_id'],command=request['command'],
                     source_revision=request['source_revision'],source_id=request['seal']['scope']['source_id'],
                     attempt_id=request['seal']['payload']['expected_attempt_id'],
                     generation=request['seal']['payload']['expected_generation'],executor_actor_id=ACTOR,
                     status={'publication.stage':'staged','publication.batch':'batched',
                             'publication.complete':'complete','publication.activate':'published'}[request['command']])
        self.pending=(request,receipt)
        return Rows(receipt)


def setup(monkeypatch, *, verses=39):
    raw=source_bytes(); body=command('seal',raw)
    db=Connection(); calls=[]
    monkeypatch.setattr(publisher,'_idle',lambda db:None)
    def audit(connection,command_raw,source_raw,*,source_revision):
        calls.append(source_revision)
        return ManifestCandidate(source_id=body['scope']['source_id'],**body['payload']['input'],
            source_revision=source_revision,executor_actor_id=ACTOR,
            attempt_id=body['payload']['expected_attempt_id'],generation=int(body['payload']['expected_generation']),
            verses=tuple(VerseCandidate('Gen',1,n+1,'a'*64,(str(n+1),)) for n in range(verses)))
    monkeypatch.setattr(publisher,'audit_closed_attempt',audit)
    return db,body,raw,calls


def publish(db,body,raw):
    return publisher.publish_closed_attempt(db,encode(body),raw,operation_id=OPERATION)


def test_canonical_encoding_is_exact_version_bound_and_has_no_surfaces(monkeypatch):
    db,body,raw,calls=setup(monkeypatch)
    manifest=publisher.audit_closed_attempt(db,encode(body),raw,source_revision=OPERATION)
    encoded=publisher.encode_manifest(manifest)
    decoded=json.loads(encoded)
    assert decoded[:3]==['scribeswell.manifest.v1',publisher.AUDITOR_VERSION,'tanakh']
    assert decoded[10]==body['payload']['expected_generation']
    assert decoded[-1][0]==['Gen',1,1,'a'*64,['1']]
    assert encoded==json.dumps(decoded,ensure_ascii=False,separators=(',',':')).encode('utf8')
    assert b'publication' not in encoded and 'אָב'.encode() not in encoded
    monkeypatch.setattr(publisher,'AUDITOR_VERSION','future-version')
    assert publisher.encode_manifest(manifest)!=encoded


def test_audits_internally_stages_complete_manifest_and_acknowledges_only_committed_activation(monkeypatch):
    db,body,raw,calls=setup(monkeypatch); factory=db.row_factory
    receipt=publish(db,body,raw)
    assert receipt.status=='published' and receipt.operation_id==OPERATION
    assert calls==[publisher.suboperation_id(OPERATION,'revision')]
    assert db.events[-1]=='commit:publication.activate'
    assert db.row_factory is factory
    requests=[v[0] for v in db.outcomes.values()]
    assert [r['command'] for r in requests]==['publication.stage','publication.batch','publication.complete','publication.activate']
    header=requests[0]['header']
    assert header['verse_count']==39 and header['token_count']==39
    assert header['digest']==requests[2]['digest']
    assert requests[1]['first_ordinal']==0 and len(requests[1]['rows'])==39


@pytest.mark.parametrize('boundary',['publication.stage','publication.batch','publication.complete','publication.activate'])
def test_lost_commit_acknowledgement_reconciles_original_boundary(monkeypatch,boundary):
    db,body,raw,calls=setup(monkeypatch);db.lost.add(boundary)
    result=publish(db,body,raw)
    assert result.status=='published'
    assert len(db.outcomes)==4
    before=deepcopy(db.outcomes)
    assert publish(db,body,raw)==result
    assert db.outcomes==before and len(calls)==1


def test_original_activation_reconciles_without_reaudit_after_recovery(monkeypatch):
    db,body,raw,calls=setup(monkeypatch);result=publish(db,body,raw)
    def retired(*args,**kwargs): raise AssertionError('must not audit a retired attempt')
    monkeypatch.setattr(publisher,'audit_closed_attempt',retired)
    assert publish(db,body,raw)==result
    assert publisher.lookup_publication(db,encode(body),raw,operation_id=OPERATION)==result


def test_changed_retry_semantics_conflict_before_audit(monkeypatch):
    db,body,raw,calls=setup(monkeypatch);publish(db,body,raw)
    body['evidence_ref']='changed:valid'
    with pytest.raises(publisher.PublishError,match='conflict'):publish(db,body,raw)
    assert len(calls)==1


@pytest.mark.parametrize('boundary',['publication.stage','publication.batch','publication.complete','publication.activate'])
def test_uncommitted_failure_cannot_return_publication_and_retry_preserves_identities(monkeypatch,boundary):
    db,body,raw,calls=setup(monkeypatch);db.fail=boundary;factory=db.row_factory
    with pytest.raises(publisher.PublishError,match='unknown_outcome') as observed:publish(db,body,raw)
    assert 'private' not in str(observed.value) and observed.value.__context__ is None
    assert OPERATION not in db.outcomes and db.row_factory is factory
    previous=set(db.outcomes);db.fail=None
    assert publish(db,body,raw).status=='published'
    assert previous <= set(db.outcomes)


def test_batches_are_bounded_contiguous_and_stable(monkeypatch):
    db,body,raw,calls=setup(monkeypatch,verses=2001);publish(db,body,raw)
    batches=[v[0] for v in db.outcomes.values() if v[0]['command']=='publication.batch']
    assert [len(r['rows']) for r in batches]==[1000,1000,1]
    assert [r['first_ordinal'] for r in batches]==[0,1000,2000]
    assert [r['batch_index'] for r in batches]==[0,1,2]
    assert [r['operation_id'] for r in batches]==[publisher.suboperation_id(OPERATION,'batch:'+str(i)) for i in range(3)]


def test_current_authority_denial_blocks_historical_receipt(monkeypatch):
    db,body,raw,calls=setup(monkeypatch);publish(db,body,raw);db.denied=True
    with pytest.raises(publisher.PublishError,match='access_denied'):publish(db,body,raw)
    assert len(calls)==1


@pytest.mark.parametrize('change',['source','command','operation'])
def test_strict_prequalification_precedes_sql(monkeypatch,change):
    db,body,raw,calls=setup(monkeypatch)
    if change=='source':raw=b'{}'
    if change=='command':body=command('begin',raw)
    operation='not-a-uuid' if change=='operation' else OPERATION
    with pytest.raises(publisher.PublishError,match='input_invalid'):
        publisher.publish_closed_attempt(db,encode(body),raw,operation_id=operation)
    assert db.events==[] and calls==[]


def test_audit_failure_never_stages(monkeypatch):
    db,body,raw,calls=setup(monkeypatch)
    def failed(*args,**kwargs):raise publisher.ClosedAuditError('corpus_mismatch')
    monkeypatch.setattr(publisher,'audit_closed_attempt',failed)
    with pytest.raises(publisher.PublishError,match='corpus_mismatch'):publish(db,body,raw)
    assert not db.outcomes


def test_manifest_size_limit_precedes_staging(monkeypatch):
    db,body,raw,calls=setup(monkeypatch);monkeypatch.setattr(publisher,'MAX_MANIFEST_BYTES',1)
    with pytest.raises(publisher.PublishError,match='input_invalid'):publish(db,body,raw)
    assert not db.outcomes


def test_encoding_matches_independent_literal_oracle():
    candidate=ManifestCandidate('tanakh','cat-v1','vers-v1','tok-v1','0'*64,
        OPERATION,ACTOR,'33333333-3333-4333-8333-333333333333',7,
        (VerseCandidate('Gen',1,2,'f'*64,('11','9223372036854775807')),))
    expected=('['
        '"scribeswell.manifest.v1","scribeswell.closed_audit.v1","tanakh","cat-v1","vers-v1","tok-v1",'
        '"0000000000000000000000000000000000000000000000000000000000000000",'
        '"44444444-4444-4444-8444-444444444444","22222222-2222-4222-8222-222222222222",'
        '"33333333-3333-4333-8333-333333333333","7",'
        '[["Gen",1,2,"ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",["11","9223372036854775807"]]]]'
    ).encode('utf8')
    assert publisher.encode_manifest(candidate)==expected
    assert publisher.encode_manifest(replace(candidate,executor_actor_id=OPERATION))!=expected
    assert publisher.encode_manifest(replace(candidate,generation=8))!=expected


def test_nonconnection_is_fixed_safe_failure_before_factory_access():
    with pytest.raises(publisher.PublishError,match='unavailable') as error:
        publisher.publish_closed_attempt(object(),b'',b'',operation_id=OPERATION)
    assert error.value.__context__ is None


@pytest.mark.parametrize('change',[{'status':'complete'},{'version':True},{'generation':'1'},
                                   {'executor_actor_id':'bad'},{'extra':'private'}])
def test_malformed_committed_receipt_is_never_acknowledged(monkeypatch,change):
    db,body,raw,calls=setup(monkeypatch)
    activation=publisher._activation(publisher._prepare(encode(body),raw,OPERATION),OPERATION)
    receipt=dict(version=1,operation_id=OPERATION,command='publication.activate',
                 source_revision=activation['source_revision'],source_id='tanakh',
                 attempt_id=body['payload']['expected_attempt_id'],generation=body['payload']['expected_generation'],
                 executor_actor_id=ACTOR,status='published')|change
    db.outcomes[OPERATION]=(activation,receipt)
    with pytest.raises(publisher.PublishError,match='unknown_outcome'):publish(db,body,raw)
    assert calls==[]
