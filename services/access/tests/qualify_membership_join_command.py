"""Fresh synthetic actual-login joins; reuses witnessed command/history locks."""
from pathlib import Path
import json,sys,uuid,subprocess,os,time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Event
from copy import deepcopy
from dataclasses import asdict
from hashlib import sha256
sys.path.insert(0,str(Path(__file__).resolve().parent))
from qualify_membership_retire_command import RetirementQualification
from qualify_actor_command import operator,engine,encode,fixture,text
from qualify_identity_baseline import baseline,ROOT,OWNER


class JoinQualification(RetirementQualification):
    def invoke(self,value,case='clean',lookup=False,url=None):
        db=engine(url or self.private['operator_urls'][case])
        try:
            with db.connect() as c:
                assert tuple(c.execute(text('SELECT session_user,current_user')).one())==('identity_operator','identity_operator')
                c.commit()
                return (operator.outcome(c,value['operation_id'],command=value['command'],org_id=value['scope']['org_id'],account_id=value['payload']['account_id']) if lookup else operator.execute(c,encode(value)))
        finally:db.dispose()

    def waiting_invocation(self,value,url,ready,start,lookup=False):
        db=engine(url)
        try:
            with db.connect() as c:
                ready.put(c.execute(text('SELECT pg_backend_pid()')).scalar_one());c.commit()
                assert start.wait(timeout=2)
                try:return operator.outcome(c,value['operation_id'],command=value['command'],org_id=value['scope']['org_id'],account_id=value['payload']['account_id']) if lookup else operator.execute(c,encode(value))
                except operator.OperatorError as error:return error.code
        finally:db.dispose()

    def value(self,account,org,previous=None,owner=False):
        return dict(schema_version=1,operation_id=str(uuid.uuid4()),command='membership.join',scope=dict(kind='organization',org_id=org),reason_code='synthetic_fixture',evidence_ref='synthetic:join/qualification',payload=dict(account_id=account,expected_previous_membership_id=previous,is_owner=owner))

    def account(self):
        account=str(uuid.uuid4())
        self.sql('clean','INSERT INTO auth.users(id,email) VALUES (:id,:email)',{'id':account,'email':'synthetic-'+account+'@example.invalid'},role='databases')
        return account

    def retire(self,value,receipt):
        command=deepcopy(value);command.update(command='membership.retire',operation_id=str(uuid.uuid4()))
        command['payload']=dict(account_id=value['payload']['account_id'],membership_id=receipt.result.target.membership_id,expected_revision='1')
        return command,self.invoke(command)

    def run(self):
        # Upgrade clean and exact committed16 independently; repeat is data preserving.
        self.command('join-clean-upgrade','legacy')
        self.command('join-exact16-upgrade','clean')
        self.command('join-previous16-upgrade','previous')
        before=self.data_state('clean');self.command('join-repeat','clean');assert self.data_state('clean')==before
        self.actor=self.authority_fixture()
        self.org=str(uuid.uuid4());self.sql('clean',"INSERT INTO identity.org(id,name,slug) VALUES (:id,'Synthetic join organization',:slug)",{'id':self.org,'slug':'synthetic-'+self.org})
        self.authority(self.actor,'membership.join','organization',self.org)
        self.authority(self.actor,'membership.retire','organization',self.org)
        account=self.account();value=self.value(account,self.org)
        first=self.invoke(value)
        assert first.result.disposition=='created' and first.result.revision=='1'
        assert self.invoke(value)==first and self.invoke(value,lookup=True)==first
        self.receipts=[asdict(first)]
        row=self.sql('clean','SELECT to_jsonb(m) FROM identity.org_member m WHERE id=CAST(:id AS bigint)',{'id':first.result.target.membership_id})[0][0]
        assert row['created_actor_id']==row['updated_actor_id']==self.actor and row['created_by'] is None and row['updated_by'] is None
        assert row['created_at']==row['updated_at'] and row['revision']==1 and not row['is_owner']
        self.deny(self.value(account,self.org),'operation_conflict')
        changed=deepcopy(value);changed['payload']['is_owner']=True;self.deny(changed)
        owner_authority=self.authority(self.actor,'membership.join_owner','organization',self.org)
        self.deny(changed,'operation_conflict')
        for field,replacement in [('reason_code','setup_correction'),('evidence_ref','synthetic:other')]:
            changed=deepcopy(value);changed[field]=replacement;self.deny(changed,'operation_conflict')
        # Retained predecessor and role evidence survive rejoin; no role copying.
        self.sql('clean',"INSERT INTO identity.member_role(member_id,role) VALUES (:id,'employee')",{'id':int(first.result.target.membership_id)})
        old_roles=self.sql('clean','SELECT to_jsonb(r) FROM identity.member_role r')
        retire,retired=self.retire(value,first)
        for previous in [None,'9223372036854775807']:
            self.deny(self.value(account,self.org,previous),'operation_conflict')
        rejoin=self.value(account,self.org,first.result.target.membership_id)
        replacement=self.invoke(rejoin);self.receipts.extend([asdict(retired),asdict(replacement)])
        assert int(replacement.result.target.membership_id)>int(first.result.target.membership_id)
        assert self.sql('clean','SELECT to_jsonb(r) FROM identity.member_role r')==old_roles
        assert self.sql('clean','SELECT count(*) FROM identity.member_role WHERE member_id=:id',{'id':int(replacement.result.target.membership_id)})==[(0,)]
        assert self.invoke(value)==first and self.invoke(value,lookup=True)==first and self.invoke(retire)==retired
        self.deny(self.value(account,self.org,first.result.target.membership_id),'operation_conflict')
        stale=deepcopy(retire);stale['operation_id']=str(uuid.uuid4());self.deny(stale,'operation_conflict')
        # owner authority applies to execution, replay and lookup of owned creations.
        owned=self.value(self.account(),self.org,owner=True);owned_receipt=self.invoke(owned);self.receipts.append(asdict(owned_receipt))
        self.sql('clean','UPDATE identity.operator_authorities SET enabled=false WHERE id=:id',{'id':owner_authority})
        self.deny(owned);self.deny(owned,lookup=True)
        self.sql('clean','UPDATE identity.operator_authorities SET enabled=true WHERE id=:id',{'id':owner_authority})
        assert self.invoke(owned,lookup=True)==owned_receipt
        self.passed('join-retire-rejoin-original-replay',actor_server_time=True,retained_roles=True,owner_policy=True)
        self.races()
        self.negative_references()
        self.cli(value,first)
        self.rollback()
        self.persist()
        (self.proof/'membership-join-receipts.json').write_text(json.dumps(self.receipts,default=str,indent=2)+'\n')

    def races(self):
        url=self.private['operator_urls']['clean']
        first=self.value(self.account(),self.org)
        key=operator.command_outcome_lock_key(self.actor,operator.parse_command(encode(first)))
        race=self.locked_race(first,first,[url,url],key)
        assert not isinstance(race[0],str) and race[0]==race[1]
        self.receipts.append(asdict(race[0]))
        other=self.value(self.account(),self.org);different=deepcopy(other);different['operation_id']=str(uuid.uuid4())
        history='identity:membership:v1:'+self.org+':'+other['payload']['account_id']
        key=int.from_bytes(sha256(history.encode()).digest()[:8],'big',signed=True)
        race=self.locked_race(other,different,[url,url],key)
        assert sum(isinstance(r,str) and r=='operation_conflict' for r in race)==1
        self.receipts.extend(asdict(r) for r in race if not isinstance(r,str))
        self.passed('join-first-same-and-distinct-operation-races',witnessed_waits=True)

    def negative_references(self):
        self.deny(self.value(str(uuid.uuid4()),self.org),'operation_conflict')
        for table in ['users','org']:
            account=self.account();org=self.org
            if table=='users':self.sql('clean','UPDATE identity.users SET deleted_at=statement_timestamp() WHERE id=:id',{'id':account})
            else:
                org=str(uuid.uuid4());self.sql('clean',"INSERT INTO identity.org(id,name,slug,deleted_at) VALUES (:id,'Retired synthetic',:slug,statement_timestamp())",{'id':org,'slug':'synthetic-'+org})
                self.authority(self.actor,'membership.join','organization',org)
            self.deny(self.value(account,org),'operation_conflict')
        self.sql('clean',"UPDATE identity.operator_principals SET enabled=false WHERE database_login='identity_operator'")
        value=self.value(self.account(),self.org);self.deny(value);self.deny(value,lookup=True)
        self.sql('clean',"UPDATE identity.operator_principals SET enabled=true WHERE database_login='identity_operator'")
        self.passed('join-local-reference-and-current-principal-denials')

    def cli(self,value=None,receipt=None):
        import operator_cli as cli
        from identity_operator_target import load_target
        from urllib.parse import urlsplit,urlunsplit
        run=json.loads((self.proof/'run.json').read_text())
        target=load_target(ROOT/'platform/deployment/.local/kdg'/run['run_id']/'identity-operator.json')
        native_fixture=ROOT/'platform/deployment/.local/identity-baseline/operator-target-gf2ef2d8/qualification-fixture.json'
        with cli.dev.directory(native_fixture.parent) as fd:stored=cli.dev.decode(cli.dev.read_at(fd,native_fixture.name,protected=True))
        assert stored['run_id']==target.run_id and stored['database']==target.database
        self.private['owner_urls']['cli']=stored['owner_url']
        self.private['databases']['cli']=urlunsplit(urlsplit(self.private['admin_url'])._replace(path='/'+target.database))
        try:
            self.command('join-native-cli-upgrade','cli')
            account=str(uuid.uuid4());org=str(uuid.uuid4())
            self.sql('cli','INSERT INTO auth.users(id,email) VALUES (:id,:email)',{'id':account,'email':'synthetic-'+account+'@example.invalid'},role='databases')
            self.sql('cli',"INSERT INTO identity.org(id,name,slug) VALUES (:id,'Synthetic join CLI',:slug)",{'id':org,'slug':'synthetic-'+org})
            actor=self.sql('cli',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")[0][0]
            self.sql('cli',"INSERT INTO identity.operator_authorities(id,database_login,command,scope_kind,org_id,target_account_id,enabled,created_by,updated_by) VALUES (:id,'identity_operator','membership.join','organization',:org,:account,true,:actor,:actor)",dict(id=str(uuid.uuid4()),org=org,account=account,actor=actor))
            value=self.value(account,org);work=target.path.parent/('join-'+uuid.uuid4().hex);work.mkdir(mode=0o700)
            with cli.dev.directory(work) as fd:__import__('native_cli').write_private(fd,'command.json',encode(value))
            launcher="import contextlib,io,json,sys;from pathlib import Path;sys.path.insert(0,str(Path(sys.argv[1]).parent));import operator_cli as c;output=io.StringIO()\nwith contextlib.redirect_stdout(output):status=c.main(sys.argv[2:])\nprint(json.dumps({'exit_status':status,'result':json.loads(output.getvalue())}))"
            base=['--owner','identity','--target',str(target.path)]
            def invoke(args):
                raw=cli.images.bounded_command([sys.executable,'-I','-B','-c',launcher,str(ROOT/'services/access/operator_cli.py'),*args],ROOT,{'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},16,8192)
                envelope=cli.dev.decode(raw);assert envelope['exit_status']==0,envelope
                return cli._receipt(envelope['result'],value['operation_id'],'membership.join')
            args=['execute',*base,'--command-file',str(work/'command.json')]
            receipt=invoke(args);assert invoke(args)==receipt
            assert invoke(['outcome',*base,'--command','membership.join','--operation-id',value['operation_id'],'--org-id',org,'--account-id',account])==receipt
            self.write_review_artifact('join-native-cli-'+uuid.uuid4().hex+'.json',dict(receipt=receipt,command=value,target=str(target.path),command_file=str(work/'command.json')))
            self.passed('join-actual-native-cli-execute-replay-recovery',prepared_target_unchanged=True)
        finally:
            self.private['owner_urls'].pop('cli',None);self.private['databases'].pop('cli',None)

    def additional(self):
        from queue import Queue
        from threading import Event
        from concurrent.futures import ThreadPoolExecutor
        saved=json.loads((self.proof/'membership-join-receipts.json').read_text())
        first=saved[0];self.org=first['result']['target']['org_id']
        self.actor=self.sql('clean',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")[0][0]
        # Same retry recovery after durable commit but lost response.
        value=self.value(self.account(),self.org)
        class LostCommit:
            def __init__(self,tx):self.tx=tx
            def __enter__(self):return self.tx.__enter__()
            def __exit__(self,*args):
                result=self.tx.__exit__(*args)
                if args[0] is None:raise RuntimeError('synthetic_lost_commit_response')
                return result
        class LostConnection:
            def __init__(self,c):self.c=c
            def __getattr__(self,name):return getattr(self.c,name)
            def begin(self):return LostCommit(self.c.begin())
        db=engine(self.private['operator_urls']['clean'])
        try:
            with db.connect() as c:
                try:operator.execute(LostConnection(c),encode(value))
                except operator.OperatorError as e:assert e.code=='operation_unavailable'
                else:raise AssertionError('lost_commit_response_success')
        finally:db.dispose()
        receipt=self.invoke(value,lookup=True);assert receipt is not None and self.invoke(value)==receipt
        authority=self.sql('clean',"SELECT id::text FROM identity.operator_authorities WHERE command='membership.join' AND org_id=:org",{'org':self.org})[0][0]
        # Both execute and lookup recheck authority after witnessed actual retry waits.
        for lookup in [False,True]:
            before=self.data_state('clean');owner=engine(self.private['owner_urls']['clean']);ready=Queue();start=Event()
            try:
                with ThreadPoolExecutor(max_workers=1) as pool:
                    with owner.begin() as holder:
                        blocker=holder.execute(text('SELECT pg_backend_pid()')).scalar_one()
                        holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':operator.command_outcome_lock_key(self.actor,operator.parse_command(encode(value)))})
                        pending=pool.submit(self.waiting_invocation,value,self.private['operator_urls']['clean'],ready,start,lookup)
                        pid=ready.get(timeout=1);start.set();self.witness_waiters(holder,[pid],blocker,[pending])
                        self.sql('clean','UPDATE identity.operator_authorities SET enabled=false WHERE id=:id',{'id':authority})
                    assert pending.result()=='access_denied'
            finally:
                start.set();owner.dispose();self.sql('clean','UPDATE identity.operator_authorities SET enabled=true WHERE id=:id',{'id':authority})
            after=self.data_state('clean');assert all(after[k]==v for k,v in before.items() if k!='operator_authorities')
        # Bounded exact retry-lock failure and same-operation recovery.
        owner=engine(self.private['owner_urls']['clean'])
        try:
            with owner.begin() as c:
                c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':operator.command_outcome_lock_key(self.actor,operator.parse_command(encode(value)))})
                self.deny(value,'operation_busy')
        finally:owner.dispose()
        assert self.invoke(value)==receipt
        # Runtime credentials and spoofed GUCs cannot select executor/authority.
        db=engine(self.private['runtime_urls']['clean'])
        try:
            with db.begin() as c:
                c.execute(text("SELECT set_config('app.actor_id',:actor,true),set_config('app.org_id',:org,true)"),{'actor':self.actor,'org':self.org})
                sp=c.begin_nested()
                try:c.execute(text('SELECT * FROM identity.membership_join_outcome(CAST(:op AS uuid),CAST(:org AS uuid),CAST(:account AS uuid))'),dict(op=value['operation_id'],org=self.org,account=value['payload']['account_id']))
                except Exception as e:assert e.orig.sqlstate=='42501'
                else:raise AssertionError('runtime_provisioning_accepted')
                finally:sp.rollback()
        finally:db.dispose()
        # Existing actor registration remains successful through the original login.
        from qualify_actor_command import CommandQualification,document
        self.authority(self.actor,'actor.register_system');q=CommandQualification(self.proof,self.private);actor_value=document()
        actor_receipt=q.invoke(actor_value);assert q.invoke(actor_value)==actor_receipt and q.invoke(actor_value,lookup=True)==actor_receipt
        self.passed('join-response-loss-bounded-busy-revoked-execute-and-lookup-waits-actor-regression',actual_waits=True,current_authority=True)
        self.persist()

    def boundaries(self):
        saved=json.loads((self.proof/'membership-join-receipts.json').read_text());self.org=saved[0]['result']['target']['org_id']
        self.actor=self.sql('clean',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")[0][0]
        account=self.account();before=self.data_state('clean');catalog=self.snapshot('clean')
        # Temporarily supply exactly the legacy writer privileges missing from postgres
        # in this scratch DB, and demand the owner trigger code, not a privilege error.
        db=self.admin('clean')
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text('SET LOCAL ROLE identity_migrator'))
                    c.execute(text('GRANT UPDATE(is_owner) ON identity.org_member TO postgres; GRANT USAGE ON SEQUENCE identity.org_member_id_seq TO postgres'))
                    c.execute(text('RESET ROLE'))
                    for statement,code in [("INSERT INTO identity.org_member(org_id,user_id) VALUES (:org,:account)",'identity_membership_join_owner_required'),("UPDATE identity.org_member SET is_owner=NOT is_owner WHERE org_id=:org",'identity_membership_owner_change_prohibited')]:
                        sp=c.begin_nested()
                        try:c.execute(text(statement),dict(org=self.org,account=account))
                        except Exception as e:assert e.orig.sqlstate=='23514' and e.orig.diag.message_primary==code
                        else:raise AssertionError('ordinary_writer_not_refused')
                        finally:sp.rollback()
                finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state('clean')==before and self.snapshot('clean')==catalog
        # Changed identical namespace racers: exactly one fingerprint wins.
        value=self.value(self.account(),self.org);changed=deepcopy(value);changed['reason_code']='setup_correction'
        key=operator.command_outcome_lock_key(self.actor,operator.parse_command(encode(value)));url=self.private['operator_urls']['clean']
        race=self.locked_race(value,changed,[url,url],key);assert sum(r=='operation_conflict' for r in race if isinstance(r,str))==1
        assert sum(not isinstance(r,str) for r in race)==1
        # Exact account/org policies and missing local org validation.
        org=str(uuid.uuid4());target=self.account();self.sql('clean',"INSERT INTO identity.org(id,name,slug) VALUES (:org,'Synthetic exact authority',:slug)",{'org':org,'slug':'synthetic-'+org})
        self.authority(self.actor,'membership.join','organization',org,target)
        self.deny(self.value(self.account(),org));self.deny(self.value(target,str(uuid.uuid4())))
        missing=str(uuid.uuid4());self.authority(self.actor,'membership.join','organization',missing,target)
        self.deny(self.value(target,missing),'operation_conflict')
        # The supported low-level wrapper rejects spoofed canonical input and context
        # cannot choose another executor even when every GUC is attacker controlled.
        receipt=next(r for r in race if not isinstance(r,str));db=engine(url)
        try:
            with db.begin() as c:
                c.execute(text("SELECT set_config('app.actor_id',:spoof,true),set_config('app.org_id',:spoof,true)"),{'spoof':str(uuid.uuid4())})
                stored=c.execute(text('SELECT * FROM identity.membership_join_outcome(CAST(:op AS uuid),CAST(:org AS uuid),CAST(:account AS uuid))'),dict(op=value['operation_id'],org=self.org,account=value['payload']['account_id'])).one()
                assert stored[0]['event_id']==receipt.result.event_id
            with db.begin() as c:
                sp=c.begin_nested()
                try:c.execute(text('SELECT * FROM identity.join_membership(CAST(:op AS uuid),CAST(:org AS uuid),CAST(:account AS uuid),NULL,false,\'synthetic_fixture\',NULL,:canonical)'),dict(op=str(uuid.uuid4()),org=self.org,account=account,canonical=b'forged'))
                except Exception as e:assert e.orig.sqlstate=='IC005'
                else:raise AssertionError('forged_canonical_accepted')
                finally:sp.rollback()
        finally:db.dispose()
        # Unsafe sequence state is refused, never silently repaired. All high-ID
        # preparation is rollback-only; the failed nextval remains consumed.
        value=self.value(account,self.org,'9223372036854775000');before=self.data_state('clean');db=self.admin('clean')
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text('SET LOCAL ROLE identity_migrator'))
                    c.execute(text('INSERT INTO identity.org_member(id,org_id,user_id,deleted_at) VALUES (9223372036854775000,:org,:account,statement_timestamp())'),dict(org=self.org,account=account))
                    c.execute(text('RESET ROLE'));c.execute(text('SET LOCAL SESSION AUTHORIZATION identity_operator'))
                    sp=c.begin_nested()
                    try:c.execute(text('SELECT * FROM identity.join_membership(CAST(:op AS uuid),CAST(:org AS uuid),CAST(:account AS uuid),9223372036854775000,false,\'synthetic_fixture\',:evidence,:canonical)'),dict(op=value['operation_id'],org=self.org,account=account,evidence=value['evidence_ref'],canonical=operator.canonical_command(operator.parse_command(encode(value)))))
                    except Exception as e:assert e.orig.sqlstate=='IC003' and e.orig.diag.message_primary=='identity_membership_sequence_conflict'
                    else:raise AssertionError('unsafe_sequence_accepted')
                    finally:sp.rollback()
                finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state('clean')==before
        self.passed('join-trigger-specific-writer-cutover-changed-race-spoof-denials-unsafe-sequence',temporary_grants_restored=True,all_failed_business_evidence_unchanged=True)

    def review_fixture(self,owner=False):
        """Fresh synthetic command scope; never reuse a committed membership fixture."""
        account=self.account();org=str(uuid.uuid4())
        self.sql('clean',"INSERT INTO identity.org(id,name,slug) VALUES (:id,'Synthetic review scope',:slug)",{'id':org,'slug':'synthetic-'+org})
        authorities={command:self.authority(self.actor,command,'organization',org,account)
                     for command in ['membership.join','membership.retire']+(['membership.join_owner'] if owner else [])}
        return self.value(account,org,owner=owner),authorities

    def review_rejoin_race(self):
        value,_=self.review_fixture();original=self.invoke(value)
        member=original.result.target.membership_id
        self.sql('clean',"INSERT INTO identity.member_role(member_id,role) VALUES (:member,'employee')",{'member':int(member)})
        retirement,retired=self.retire(value,original)
        predecessor=self.sql('clean','SELECT to_jsonb(m) FROM identity.org_member m WHERE id=:member',{'member':int(member)})
        roles=self.sql('clean','SELECT to_jsonb(r) FROM identity.member_role r WHERE member_id=:member',{'member':int(member)})
        first=self.value(value['payload']['account_id'],value['scope']['org_id'],member)
        second=deepcopy(first);second['operation_id']=str(uuid.uuid4())
        history='identity:membership:v1:'+first['scope']['org_id']+':'+first['payload']['account_id']
        key=int.from_bytes(sha256(history.encode()).digest()[:8],'big',signed=True)
        url=self.private['operator_urls']['clean'];race=self.locked_race(first,second,[url,url],key)
        assert len([r for r in race if r=='operation_conflict'])==1
        winner=next(r for r in race if not isinstance(r,str));assert int(winner.result.target.membership_id)>int(member)
        assert self.sql('clean','SELECT to_jsonb(m) FROM identity.org_member m WHERE id=:member',{'member':int(member)})==predecessor
        assert self.sql('clean','SELECT to_jsonb(r) FROM identity.member_role r WHERE member_id=:member',{'member':int(member)})==roles
        assert self.sql('clean','SELECT count(*),count(*) FILTER(WHERE deleted_at IS NULL) FROM identity.org_member WHERE org_id=:org AND user_id=:account',dict(org=value['scope']['org_id'],account=value['payload']['account_id']))==[(2,1)]
        assert self.sql('clean','SELECT count(*) FROM identity.member_role WHERE member_id=:member',{'member':int(winner.result.target.membership_id)})==[(0,)]
        for table,column in [('operation_outcome','operation_id'),('business_event','outcome_id')]:
            condition='operation_id IN (CAST(:first AS uuid),CAST(:second AS uuid))' if table=='operation_outcome' else 'outcome_id IN (SELECT id FROM identity.operation_outcome WHERE operation_id IN (CAST(:first AS uuid),CAST(:second AS uuid)))'
            assert self.sql('clean','SELECT count(*) FROM identity.'+table+' WHERE '+condition,dict(first=first['operation_id'],second=second['operation_id']))==[(1,)]
        loser=second if winner.operation_id==first['operation_id'] else first
        assert self.invoke(loser,lookup=True) is None
        assert self.invoke(value)==original and self.invoke(retirement)==retired
        self.write_review_artifact('join-review-rejoin-race-'+uuid.uuid4().hex+'.json',dict(commands=[first,second],winner=asdict(winner),predecessor=member,retirement=asdict(retired)))
        self.passed('join-review-distinct-explicit-rejoin-race',witnessed_history_waits=True,one_replacement_event_outcome=True,predecessor_roles_history_preserved=True)

    def review_history_revocation(self):
        for revoked in ['membership.join','membership.join_owner']:
            value,authorities=self.review_fixture(owner=True)
            before=self.data_state('clean');owner=engine(self.private['owner_urls']['clean']);ready=Queue();start=Event()
            history='identity:membership:v1:'+value['scope']['org_id']+':'+value['payload']['account_id']
            key=int.from_bytes(sha256(history.encode()).digest()[:8],'big',signed=True)
            try:
                with ThreadPoolExecutor(max_workers=1) as pool:
                    with owner.begin() as holder:
                        blocker=holder.execute(text('SELECT pg_backend_pid()')).scalar_one()
                        holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
                        pending=pool.submit(self.waiting_invocation,value,self.private['operator_urls']['clean'],ready,start)
                        pid=ready.get(timeout=1);start.set();self.witness_waiters(holder,[pid],blocker,[pending])
                        self.sql('clean','UPDATE identity.operator_authorities SET enabled=false WHERE id=:id',{'id':authorities[revoked]})
                    assert pending.result(timeout=5)=='access_denied'
            finally:start.set();owner.dispose()
            after=self.data_state('clean');assert all(after[k]==v for k,v in before.items() if k!='operator_authorities')
            states=dict(self.sql('clean','SELECT command,enabled FROM identity.operator_authorities WHERE org_id=:org',{'org':value['scope']['org_id']}))
            assert not states[revoked] and all(enabled for command,enabled in states.items() if command!=revoked)
            self.passed('join-review-history-wait-revoked-'+revoked,actual_shared_history_wait=True,denied=True,business_evidence_unchanged=True)

    def witness_reference_waiter(self,observer,pid,blocker,pending):
        """Witness a tuple/transaction lock wait, rather than infer a race from timing."""
        deadline=time.monotonic()+1
        while time.monotonic()<deadline:
            observer.execute(text('SELECT pg_stat_clear_snapshot()'))
            waiting=observer.execute(text("""SELECT EXISTS(SELECT 1 FROM pg_stat_activity a WHERE a.pid=:pid
             AND a.datname=current_database() AND :blocker=ANY(pg_blocking_pids(a.pid))
             AND EXISTS(SELECT 1 FROM pg_locks l WHERE l.pid=a.pid AND NOT l.granted AND l.locktype IN ('tuple','transactionid')))"""),dict(pid=pid,blocker=blocker)).scalar_one()
            if waiting:return
            assert not pending.done(),'reference_writer_completed_before_lock_witness'
        raise AssertionError('actual_reference_wait_not_witnessed')

    def retire_reference(self,table,target,ready,start):
        db=engine(self.private['owner_urls']['clean'])
        try:
            with db.begin() as c:
                c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                ready.put(c.execute(text('SELECT pg_backend_pid()')).scalar_one());assert start.wait(timeout=2)
                c.execute(text('UPDATE identity.'+table+' SET deleted_at=statement_timestamp() WHERE id=:id'),{'id':target})
        finally:db.dispose()

    def review_reference_ordering(self):
        for table in ['users','org']:
            # Retirement wins the reference row lock: validation waits, then refuses.
            value,_=self.review_fixture();target=value['payload']['account_id'] if table=='users' else value['scope']['org_id']
            before=self.data_state('clean');audit_before={r[0] for r in self.sql('clean','SELECT id::text FROM identity.audit_log')};owner=engine(self.private['owner_urls']['clean']);ready=Queue();start=Event()
            try:
                with ThreadPoolExecutor(max_workers=1) as pool:
                    with owner.begin() as holder:
                        holder.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                        blocker=holder.execute(text('SELECT pg_backend_pid()')).scalar_one()
                        holder.execute(text('UPDATE identity.'+table+' SET deleted_at=statement_timestamp() WHERE id=:id'),{'id':target})
                        pending=pool.submit(self.waiting_invocation,value,self.private['operator_urls']['clean'],ready,start)
                        pid=ready.get(timeout=1);start.set();self.witness_reference_waiter(holder,pid,blocker,pending)
                    assert pending.result(timeout=5)=='operation_conflict'
            finally:start.set();owner.dispose()
            after=self.data_state('clean');expected_changes={table,'audit_log'} if table=='users' else {table}
            assert all(after[k]==v for k,v in before.items() if k not in expected_changes)
            if table=='users':
                new_audit=[r for r in self.sql('clean','SELECT id::text,table_name,record_id,operation,column_changes FROM identity.audit_log') if r[0] not in audit_before]
                assert len(new_audit)==1 and new_audit[0][1:4]==('users',target,'UPDATE')
                changes=new_audit[0][4]
                assert set(changes)<={'deleted_at','updated_at','updated_by'} and changes['deleted_at']['old'] is None and changes['deleted_at']['new'] is not None
            assert self.invoke(value,lookup=True) is None
            self.passed('join-review-'+table+'-retirement-before-validation',witnessed_reference_row_wait=True,no_join_effects=True)
            # Join acquires both FOR SHARE reference locks before its test-only insert
            # gate; a later retirement is witnessed waiting on that operator backend.
            value,_=self.review_fixture();target=value['payload']['account_id'] if table=='users' else value['scope']['org_id']
            catalog=self.snapshot('clean');key=int.from_bytes(uuid.uuid4().bytes[:8],'big',signed=True)
            self.sql('clean',"CREATE FUNCTION identity.synthetic_join_reference_gate() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $$ BEGIN PERFORM pg_advisory_xact_lock("+str(key)+"); RETURN NEW; END $$; CREATE TRIGGER synthetic_join_reference_gate BEFORE INSERT ON identity.org_member FOR EACH ROW EXECUTE FUNCTION identity.synthetic_join_reference_gate()")
            owner=engine(self.private['owner_urls']['clean']);join_ready=Queue();join_start=Event();retire_ready=Queue();retire_start=Event()
            try:
                with ThreadPoolExecutor(max_workers=2) as pool:
                    with owner.begin() as holder:
                        blocker=holder.execute(text('SELECT pg_backend_pid()')).scalar_one();holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
                        joining=pool.submit(self.waiting_invocation,value,self.private['operator_urls']['clean'],join_ready,join_start)
                        join_pid=join_ready.get(timeout=1);join_start.set();self.witness_waiters(holder,[join_pid],blocker,[joining])
                        retiring=pool.submit(self.retire_reference,table,target,retire_ready,retire_start)
                        retire_pid=retire_ready.get(timeout=1);retire_start.set();self.witness_reference_waiter(holder,retire_pid,join_pid,retiring)
                    receipt=joining.result(timeout=5);assert not isinstance(receipt,str)
                    assert retiring.result(timeout=5) is None
            finally:
                join_start.set();retire_start.set();owner.dispose()
                self.sql('clean','DROP TRIGGER synthetic_join_reference_gate ON identity.org_member; DROP FUNCTION identity.synthetic_join_reference_gate()')
            assert self.snapshot('clean')==catalog
            assert self.sql('clean','SELECT deleted_at IS NOT NULL FROM identity.'+table+' WHERE id=:id',{'id':target})==[(True,)]
            assert self.invoke(value,lookup=True)==receipt
            # Separate fresh operation now observes the retired reference, so it cannot
            # issue another join even if the membership-history condition were absent.
            self.deny(self.value(value['payload']['account_id'],value['scope']['org_id']),'operation_conflict')
            self.write_review_artifact('join-review-reference-'+table+'-'+uuid.uuid4().hex+'.json',dict(command=value,receipt=asdict(receipt),join_first_reference_retired_afterward=True))
            self.passed('join-review-'+table+'-validation-before-retirement',witnessed_retirement_wait=True,join_committed_before_retirement=True,temporary_gate_removed=True)

    def review_maintenance(self):
        value,_=self.review_fixture();receipt=self.invoke(value);member=int(receipt.result.target.membership_id)
        before=self.data_state('clean');catalog=self.snapshot('clean');db=self.admin('clean')
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text('SET LOCAL ROLE identity_migrator'))
                    original=c.execute(text('SELECT to_jsonb(m) FROM identity.org_member m WHERE id=:id'),{'id':member}).scalar_one()
                    history={t:list(c.execute(text('SELECT to_jsonb(t) FROM identity.'+t+' t ORDER BY 1'))) for t in ['member_role','operation_outcome','business_event']}
                    c.execute(text('GRANT UPDATE(updated_by) ON identity.org_member TO postgres'))
                    c.execute(text('SET LOCAL ROLE postgres'));assert c.execute(text('SELECT current_user')).scalar_one()=='postgres'
                    c.execute(text('UPDATE identity.org_member SET updated_by=:actor WHERE id=:id'),{'id':member,'actor':value['payload']['account_id']})
                    c.execute(text('SET LOCAL ROLE identity_migrator'))
                    changed=c.execute(text('SELECT to_jsonb(m) FROM identity.org_member m WHERE id=:id'),{'id':member}).scalar_one()
                    assert changed==dict(original,updated_by=value['payload']['account_id'],revision=original['revision']+1)
                    c.execute(text('UPDATE identity.org_member SET is_owner=NOT is_owner WHERE id=:id'),{'id':member})
                    maintained=c.execute(text('SELECT to_jsonb(m) FROM identity.org_member m WHERE id=:id'),{'id':member}).scalar_one()
                    assert maintained==dict(changed,is_owner=not changed['is_owner'],revision=changed['revision']+1)
                    assert history=={t:list(c.execute(text('SELECT to_jsonb(t) FROM identity.'+t+' t ORDER BY 1'))) for t in history}
                finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state('clean')==before and self.snapshot('clean')==catalog
        self.passed('join-review-legacy-unrelated-change-and-migrator-owner-maintenance',actual_value_changes=True,revisions_incremented=True,actor_history_preserved=True,rollback_restored_rows_catalog=True)

    def review_lookup_account(self):
        # Deliberately grant this fresh organization broadly so authorized B reaches
        # the account predicate for A's saved operation, not an authorization denial.
        value,_=self.review_fixture();org=value['scope']['org_id']
        self.authority(self.actor,'membership.join','organization',org)
        original=self.invoke(value);other=deepcopy(value);other['payload']['account_id']=self.account()
        before=self.data_state('clean');assert self.invoke(other,lookup=True) is None
        assert self.invoke(value,lookup=True)==original and self.data_state('clean')==before
        self.passed('join-review-authorized-other-account-lookup-unresolved',org_wide_authority=True,no_effects=True,original_recovers=True)

    def review_gaps(self,remaining=False):
        self.actor=self.sql('clean',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")[0][0]
        if not remaining:self.review_rejoin_race();self.review_history_revocation()
        self.review_reference_ordering()
        self.review_maintenance();self.review_lookup_account();self.persist()

    def verify_retained(self):
        rows=self.sql('clean',"""SELECT o.operation_id::text,o.result,o.executor_actor_id::text,o.committed_at,
         e.event_id::text,e.event_type,e.executor_actor_id::text,e.created_at,e.target,e.target_key,e.transition,
         m.id::text,m.org_id::text,m.user_id::text,m.created_actor_id::text,m.created_at,m.is_owner,
         (SELECT count(*) FROM identity.business_event x WHERE x.outcome_id=o.id)
         FROM identity.operation_outcome o LEFT JOIN identity.business_event e ON e.outcome_id=o.id
         LEFT JOIN identity.org_member m ON m.id::text=o.result->'target'->>'membership_id'
         WHERE o.command_type='membership.join' ORDER BY o.operation_id""")
        assert rows
        for row in rows:
            op,result,actor,instant,event,event_type,event_actor,event_time,target,key,transition,member,org,account,created_actor,created_time,owner,count=row
            assert result==dict(target=dict(org_id=org,account_id=account,membership_id=member),disposition='created',revision='1',event_id=event)
            assert target==result['target'] and key==member and actor==event_actor==created_actor
            assert instant==event_time==created_time and event_type=='identity.membership_joined' and count==1
            assert transition['after']==dict(revision='1',retired=False,is_owner=owner)
            previous=transition['before']['previous_membership_id']
            if previous is not None:assert int(previous)<int(member)
        for case in ['clean','legacy','previous','characterization','failure','unsafe']:
            baseline.compare_catalog(baseline.catalog_fingerprints(self.snapshot(case)),baseline.trusted_membership_join_command_reference())
        self.write_review_artifact('join-verified-retained-'+uuid.uuid4().hex+'.json',dict(joins=len(rows),operation_ids=[r[0] for r in rows],catalogs_exact=True))
        self.passed('join-retained-receipt-event-member-consistency',joins=len(rows),all_catalogs_exact=True)

    def migration_matrix(self):
        # Existing legacy/adopt lane is unused in this frame: unsafe is fresh/empty.
        case='unsafe';self.legacy(case);self.original_ledger(case);ids=self.row_fixtures(case)
        rows={t:self.sql(case,'SELECT to_jsonb(t) FROM identity.'+t+' t ORDER BY id') for t in ['users','org','org_member','member_role']}
        external=self.external_state(case);ledger=self.data_state(case)['supabase_migrations.schema_migrations']
        self.command('join-adopt-upgrade',case,mode='adopt')
        for table,old in rows.items():
            new=self.sql(case,'SELECT to_jsonb(t) FROM identity.'+table+' t ORDER BY id')
            if table=='org_member':new=[({k:v for k,v in row.items() if k not in {'revision','created_actor_id','updated_actor_id'}},) for row, in new]
            assert old==new,table
        assert self.external_state(case)==external and self.data_state(case)['supabase_migrations.schema_migrations']==ledger
        before=self.data_state(case);self.command('join-adopt-repeat',case);assert self.data_state(case)==before
        # Exact16 retains representative old Identity and foreign-owner rows.
        case='characterization';ids=self.row_fixtures(case);before=self.data_state(case);external=self.external_state(case)
        self.command('join-exact16-data-upgrade',case)
        after=self.data_state(case);assert all(after[k]==v for k,v in before.items() if k!='identity.alembic_version')
        assert self.external_state(case)==external
        # Unknown history, function/ACL drift are rollback-only and cannot rewrite trust.
        case='unknown'
        for form in ['history','function','acl']:
            before=self.data_state(case);catalog=self.snapshot(case);db=engine(self.private['owner_urls'][case])
            try:
                with db.connect() as c:
                    tx=c.begin()
                    try:
                        c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                        if form=='history':c.execute(text("UPDATE identity.alembic_version SET version_num='identity_unknown'"))
                        elif form=='acl':c.execute(text('GRANT SELECT ON identity.org_member TO identity_operator'))
                        else:
                            definition=next(r[4] for r in catalog['functions'] if r[:3]==['identity','guard_org_member_revision',''])
                            c.exec_driver_sql(definition.replace('BEGIN\n','BEGIN\n -- synthetic drift\n',1),execution_options={'no_parameters':True})
                        changed=baseline.target_catalog_snapshot(c)
                        try:baseline.preflight(c,'clean')
                        except baseline.BaselineError as e:assert 'identity_unknown_history' in str(e) or 'identity_catalog_mismatch' in str(e)
                        else:raise AssertionError('untrusted_catalog_accepted')
                        assert baseline.target_catalog_snapshot(c)==changed
                    finally:tx.rollback()
            finally:db.dispose()
            assert before==self.data_state(case) and catalog==self.snapshot(case)
        # Transactional DDL failure after creation of the new join routine.
        case='failure';before=self.data_state(case);catalog=self.snapshot(case)
        self.sql(case,"""CREATE SEQUENCE public.synthetic_join_ddl_marker;
        CREATE FUNCTION public.synthetic_join_ddl_failure() RETURNS event_trigger LANGUAGE plpgsql AS $$ BEGIN
         IF to_regprocedure('identity.join_membership(uuid,uuid,uuid,bigint,boolean,text,text,bytea)') IS NOT NULL THEN
          PERFORM nextval('public.synthetic_join_ddl_marker'); RAISE EXCEPTION 'synthetic_join_ddl_failure'; END IF; END $$;
        CREATE EVENT TRIGGER synthetic_join_ddl_failure ON ddl_command_end WHEN TAG IN ('CREATE FUNCTION') EXECUTE FUNCTION public.synthetic_join_ddl_failure();
        GRANT USAGE ON SEQUENCE public.synthetic_join_ddl_marker TO identity_migrator;""",role='databases')
        try:
            self.command('join-injected-ddl-failure',case,expected='identity_migration_failed_requires_reconciliation')
            assert self.sql(case,'SELECT last_value,is_called FROM public.synthetic_join_ddl_marker',role='databases')==[(1,True)]
        finally:self.sql(case,'DROP EVENT TRIGGER synthetic_join_ddl_failure; DROP FUNCTION public.synthetic_join_ddl_failure(); DROP SEQUENCE public.synthetic_join_ddl_marker',role='databases')
        assert self.data_state(case)==before and self.snapshot(case)==catalog
        self.command('join-explicit-ddl-recovery',case)
        for case in ['clean','legacy','previous','characterization','failure','unsafe']:
            baseline.compare_catalog(baseline.catalog_fingerprints(self.snapshot(case)),baseline.trusted_membership_join_command_reference())
        self.passed('join-clean-adopt-exact16-repeat-drift-ddl-rollback-explicit-recovery',foreign_owners_retained=True,historical_catalogs_verified=True)

    def rollback(self):
        value=self.value(self.account(),self.org);before=self.data_state('clean')
        db=engine(self.private['owner_urls']['clean'])
        try:
            with db.begin() as c:
                c.execute(text("CREATE FUNCTION identity.synthetic_join_event_failure() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'synthetic_event_failure'; END $$; CREATE TRIGGER synthetic_join_event_failure BEFORE INSERT ON identity.business_event FOR EACH ROW EXECUTE FUNCTION identity.synthetic_join_event_failure()"))
            self.deny(value,'operation_unavailable')
        finally:
            with db.begin() as c:c.execute(text('DROP TRIGGER synthetic_join_event_failure ON identity.business_event; DROP FUNCTION identity.synthetic_join_event_failure()'))
            db.dispose()
        assert self.data_state('clean')==before
        self.passed('join-event-failure-atomic-rollback')


def main():
    if not __debug__:raise RuntimeError('qualification_optimized_python_prohibited')
    proof,private=fixture();q=JoinQualification(proof,private)
    paths=[*OWNER.glob('*.py'),*OWNER.glob('versions/*.py'),*OWNER.glob('*reference.json'),OWNER/'source-pins.json',OWNER/'uv.lock',OWNER/'pyproject.toml']
    paths.extend((ROOT/'services/access/tests').glob('qualify_*.py'))
    paths.extend(ROOT/'services/access'/name for name in ['identity_operator.py','identity_operator_input.py','identity_operator_target.py','operator_cli.py','identity-alembic.ini'])
    paths.extend((ROOT/'platform/deployment').glob('*.py'));paths.extend((ROOT/'platform/deployment').glob('*.json'))
    paths.extend((ROOT/'platform/deployment/schema').glob('*.json'));paths.extend((ROOT/'platform/deployment/environments').glob('*.json'))
    paths.extend((ROOT/'platform/supabase/migrations').glob('*.sql'));paths.extend(ROOT/name for name in baseline.SOURCES)
    import dev
    paths.extend(ROOT/name for name in dev.SOURCES)
    paths.extend([ROOT/'scripts/seed.py',ROOT/'tools/py/run_compose_supabase.py'])
    paths.extend((ROOT/'platform/supabase/seeds').rglob('*.sql'));paths=sorted(set(paths))
    captured={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths}
    witness=proof/('source-capture-'+uuid.uuid4().hex+'.json')
    witness.write_text(json.dumps(dict(stage=sys.argv[1:] or ['initial'],before=captured,status='started'),indent=2)+'\n');witness.chmod(0o600)
    if sys.argv[1:]==['--additional']:q.additional()
    elif sys.argv[1:]==['--matrix']:q.migration_matrix()
    elif sys.argv[1:]==['--boundaries']:q.boundaries()
    elif sys.argv[1:]==['--verify-retained']:q.verify_retained()
    elif sys.argv[1:]==['--review-gaps']:q.review_gaps()
    elif sys.argv[1:]==['--review-gaps-remaining']:q.review_gaps(remaining=True)
    elif not sys.argv[1:]:q.run()
    else:raise RuntimeError('qualification_arguments_invalid')
    assert captured=={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths},'qualification_source_changed'
    witness.write_text(json.dumps(dict(stage=sys.argv[1:] or ['initial'],before=captured,after=captured,status='passed'),indent=2)+'\n')


def entrypoint():
    try:
        main()
    except Exception:
        print('membership_join_qualification_failed',file=sys.stderr)
        return 1
    return 0


if __name__=='__main__':raise SystemExit(entrypoint())
