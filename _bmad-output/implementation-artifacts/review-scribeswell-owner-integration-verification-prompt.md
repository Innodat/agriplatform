Read `# Verification Gap Review

**Goal:** Find changed behavior that could break without reliable verification catching it. Ask one question — "if the behavior this change is supposed to produce broke where it's actually used, would verification fail?" Do not hunt for correctness bugs, but report genuine problems you notice while tracing verification.

The main verification gap shapes are:

1. **Regression gap:** the changed code regresses where it's used, and no test covering that use would fail.
2. **Missing-adoption gap:** a place that should now use the new behavior doesn't; it handles the same case its own way, or not at all, and no test would flag the omission.
3. **Broken-verification gap:** a test appears to cover the changed behavior, but would not actually protect it because it is skipped, flaky, not run in the normal verification path, or too weak to observe the regression.

## Evidence Rules

- Read a test before claiming what it covers, runs, asserts, or misses.
- Before claiming no test exists, search the whole repo by the symbol under test and by import references; expected file locations are not enough.
- Never assert what you did not verify. If a finding cannot be grounded, drop it.
- In a finding, say what you actually checked — "none of the tests I read cover this" — and show how far you looked. Say a test doesn't exist anywhere only when the symbol/import-reference search actually shows that.
- Do not assign severity, confidence, priority, or ranking.

## Review Sequence

### Step 1: Screen for behavioral change

Screen each part of the change separately. If a part is non-behavioral, skip it. Call a part non-behavioral only when the changed code does not alter return values, thrown errors, caller-visible side effects, or observable state (including iteration order and emitted messages). Once a part meets that test, move on; do not inspect callers or tests for extra confirmation.

Common non-behavioral examples: formatting, comments, whitespace; pure renames; trivial getters/setters and pass-throughs; type-only or compiler-enforced changes with no runtime effect; etc.

Only outcomes produced by deterministic code are worth automatically testing; tests are useless on static source text and brittle on LLM output. Skip those parts.

If every part is skipped, output the clean result (see Output Format).

### Step 2: Find the behavior that changed

Identify what behavior changed compared to the previous version: output, side effect, branch, error path, schema/event shape, config default, validation/authorization rule, external contract, etc. If the change affects more than one behavior, handle each separately.

Treat broad-impact changes as behavioral even when no single changed line looks important: dependency, toolchain, build/config, data-file, etc.

### Step 3: Trace where that behavior is used

Trace the changed behavior to the places that observe it. Start with direct callers and registered entry points (routes, commands, DI), contract consumers (schemas, events, APIs, database readers), and reverse-dependency info if already available.

Follow a path only while the changed behavior is reachable and unverified. Stop when a test at that boundary would fail, the consumer does not observe the changed behavior, or the next hop is guesswork (dynamic dispatch, reflection, outside-repo consumers, etc.). Prefer the nearest observable boundary, often one to three hops away, especially across contract, integration, or service edges. If there are more than five similar consumers, group obvious repeats and check representative paths; expand only when a consumer observes the behavior differently.

### Step 4: Qualify the consumer, then check its test

For each consumer, name the smallest realistic regression this consumer would observe: invert the branch, drop the default, omit the field, return the old error code, skip the integration call, etc. This is the Demonstration. If no such regression exists, drop the path; untested downstream code is not a finding.

A `Missing-adoption gap` qualifies not by the adoption failure alone but by a supersession signal: the change gives clear evidence the new behavior is meant to replace the local one — PR intent, naming or docs, a replaced sibling site, deleted duplicate logic, or a test defining the new rule — and the local site shares the same observable contract. Without a supersession signal and a shared observable contract, it is a refactor suggestion, not a verification-gap finding. Once both hold, check whether any test for that site would flag the non-adoption; missing coverage of the non-adoption is the gap itself, not a disqualifier.

Find and read the relevant test. Ask whether the Demonstration would make an assertion fail.

- If yes, the behavior is verified. No finding.
- For a regression-style Demonstration: if no test runs the path, the test is skipped/flaky/not run normally, or the test runs the code without checking the changed result, report a `Regression gap` or `Broken-verification gap`.
- For a qualifying Missing-adoption case: if none of the site tests you found assert it adopts the new behavior, report a `Missing-adoption gap`.

A test counts only if it runs normally and an assertion observes the changed output, branch, or contract. These do not count: no execution; source-text assertions that match a file's wording instead of running it; success/no-throw/snapshot-only checks; mock/log-call checks; human-only checks; tests that mock away the integration; e2e tests that pass through without checking the changed output; stale assertions or fixtures.

For example, `expect(x ?? DEFAULT).toBe(DEFAULT)` passes when `x` is missing.

Common patterns:

- **Caller-path gap** — helper test covers the branch, but caller values skip it.
- **Contract drift** — payload/schema/event changes must be verified at the consumer.
- **Migration compatibility** — tests only create new-format rows or fresh schemas.
- **Phantom exception** — handled partial-failure path has no test.
- **Missing-adoption gap** — sibling site should use the new rule/helper and does not.
- **Removed verification** — deleted test or weakened assertion leaves behavior unpinned; removing a source-text assertion is not this, since it never counted.

### Step 5: Confirm each finding is real

Before writing a finding, re-open the specific tests or search results the finding relies on. Verify the Demonstration would not make any test you checked fail, or that the absence claim is backed by the symbol/import-reference search. Do not claim more than you verified; drop any finding you cannot ground.

Explain why the test misses the bug using what the test sets up and checks.

Do not report: compiler/type-checker-enforced cases; behavior already verified by an integration, contract, or e2e test; implementation-detail or mock-only tests; low coverage or a missing test file by itself; legacy untested code the change did not affect.

Report genuine problems you noticed while tracing verification, even if they are not verification gaps. Put them under `Other findings` in the output. This permits reporting what you already reached, not extra hunting. A claim that code misbehaves is a defect, not a gap — it goes under `Other findings` for standard triage, however you found it.

## OUTPUT FORMAT

Emit each verification-gap finding as one block. No general advice, no severity or confidence. Triage trusts a gap finding as filed and does not re-verify it, so each block must stand on its own evidence.

```markdown
### <one-line title naming the gap>

- **Changed surface:** the exact behavior or contract that changed — `file:line`.
- **Impacted consumer or site:** named concretely with `file:line` (e.g. "the `createInvoice` mutation used by the billing dashboard at `billing/dashboard.ts:88`," not "callers of this function").
- **Existing test evidence:**
  - `Regression gap`: what the relevant test actually asserts, with `file:line`; or, if none, the symbol/import-reference searches run and their result.
  - `Missing-adoption gap`: tests for the impacted site, and whether any assert it adopts the new behavior.
  - `Broken-verification gap`: the apparent test or verification path, and why it does not count.
- **Missing verification:** the precise assertion or check that's absent.
- **Demonstration:**
  - `Regression gap` / `Broken-verification gap`: the concrete regression that would ship undetected, and why the tests you checked would not fail.
  - `Missing-adoption gap`: the case the site mishandles by not adopting the new behavior, and that none of the tests you read assert adoption.
- **Consequence:** the concrete thing that ships wrong — a regression the checked evidence would not catch, or a site that should use the new behavior and doesn't.
- **Disposition:** `patch` — name the test to add, fit to the repo's own way of verifying (don't impose a generic test pyramid) — or `defer` when the gap is real but not worth closing as part of this change, with one sentence of why.
```

If you noticed genuine non-gap problems while tracing verification, append:

```markdown
## Other findings

- <description only; no severity, confidence, priority, or ranking>
```

When you find no verification gaps and no other findings, output exactly this single line, not an empty response:

`No verification gaps found.`

## CONTENT SOURCE

"Review content:" in the message that launched you gives the content itself or a path to read it from. Read the file when it is a path; either way that is the content under review, and this instruction file never is. If no content is supplied, or the file it points to is missing, empty, or unreadable, say exactly that and stop — never report a clean review for content you could not read.
` completely and follow it as your review instructions.

Review content: the unified diff at `diff --git a/apps/scribeswell/tests/studies_owner_fixture.py b/apps/scribeswell/tests/studies_owner_fixture.py
new file mode 100644
index 0000000..584a045
--- /dev/null
+++ b/apps/scribeswell/tests/studies_owner_fixture.py
@@ -0,0 +1,319 @@
+"""One new disposable native fixture. Not a provisioner or release readiness gate.
+
+Only this module's newly allocated run is eligible for writes/normal stop. Owner
+migrations and Auth run against the same real provider database, with no clones.
+"""
+from __future__ import annotations
+if not __debug__:raise RuntimeError('qualification_optimized_python_prohibited')
+import argparse
+import json
+import os
+from pathlib import Path
+import secrets
+import signal
+import socket
+import subprocess
+import sys
+import time
+from uuid import UUID,uuid4
+
+ROOT=Path(__file__).resolve().parents[3]
+APP=ROOT/'apps/scribeswell'
+ACCESS=ROOT/'services/access'
+TARGET=ROOT/'platform/deployment/environments/kdg-local.json'
+PORTS=(5188,8188,8189,55480,55481,55482,55483,15484,8443)
+
+def private(path,value):
+    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
+    with os.fdopen(fd,'w') as out:json.dump(value,out,ensure_ascii=False,indent=2,default=str)
+
+def check_ports():
+    for port in PORTS:
+        with socket.socket() as listener:
+            try:listener.bind(('127.0.0.1',port))
+            except OSError:raise RuntimeError('qualification_port_occupied:'+str(port)) from None
+
+def wait_http(url,process):
+    import httpx
+    limit=time.monotonic()+30
+    while time.monotonic()<limit:
+        if process.poll() is not None:raise RuntimeError('qualification_process_exited')
+        try:
+            if httpx.get(url,timeout=1).status_code<500:return
+        except httpx.HTTPError:pass
+        time.sleep(.2)
+    raise RuntimeError('qualification_start_timeout')
+
+class Qualification:
+    def __init__(self,run_id,cli,proof):
+        if str(UUID(run_id))!=run_id or UUID(run_id).int==0:raise ValueError('canonical_new_run_required')
+        self.run_id=run_id;self.cli=Path(cli).resolve();self.proof=Path(proof).absolute()
+        self.run=ROOT/'platform/deployment/.local/kdg'/run_id
+        if self.run.exists():raise FileExistsError('existing_run_refused')
+        self.proof.mkdir(mode=0o700,parents=True,exist_ok=False)
+        self.events=[];self.processes=[];self.owned=False
+        from hashlib import sha256
+        sources=[Path(__file__),APP/'tools/py/qualify_studies_owner_integration.py',APP/'web/tests/studies-owner.integration.cjs',APP/'web/tests/studies-owner-reporter.cjs',APP/'web/playwright.owner-integration.config.cjs',APP/'web/vite.config.ts',APP/'web/package.json',ROOT/'platform/deployment/dev.py',ROOT/'platform/deployment/native_cli.py',TARGET]
+        sources.extend(ACCESS.glob('*.py'))
+        for directory in (ACCESS/'identity-migrations',ACCESS/'migrations',ACCESS/'tools',APP/'backend',APP/'studies-migrations',APP/'web/src'):
+            sources.extend(p for p in directory.rglob('*') if p.suffix in ('.py','.sql','.json','.ts','.tsx'))
+        self.sources={p:sha256(p.read_bytes()).hexdigest() for p in sorted(set(sources))}
+        private(self.proof/'sources.json',{str(p.relative_to(ROOT)):digest for p,digest in self.sources.items()})
+        self.environment={key:os.environ[key] for key in ('PATH','HOME') if key in os.environ}
+        self.environment.update({'LANG':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1'})
+
+    def command(self,label,args,env=None,cwd=ROOT,timeout=120,on_started=None):
+        path=self.proof/(label+'.log')
+        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
+        with os.fdopen(fd,'wb') as output:
+            process=subprocess.Popen([str(a) for a in args],env=env or self.environment,cwd=cwd,stdin=subprocess.DEVNULL,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
+            try:
+                if on_started:on_started(process)
+                code=process.wait(timeout=timeout)
+            except BaseException:
+                self.stop_process(process)
+                self.events.append({'stage':label,'outcome':'interrupted-or-timed-out'})
+                raise
+            # Reap any remaining owned launcher descendants before the next stage.
+            self.stop_process(process)
+        self.events.append({'stage':label,'command':[str(a) for a in args],'exit_code':code})
+        if code:raise RuntimeError('qualification_stage_failed:'+label)
+
+    def wrapper(self,action):
+        self.command('wrapper-'+action,[sys.executable,ROOT/'platform/deployment/dev.py',action,'--target',TARGET,'--run-id',self.run_id,'--supabase',self.cli],timeout=240)
+
+    def capture_status(self):
+        sys.path.insert(0,str(ROOT/'platform/deployment'))
+        import dev,native_cli
+        raw=dev.read(TARGET);target=dev.decode(raw)
+        native_cli.check_run(self.run,target,raw,self.run_id)
+        network=native_cli.network(target,self.run_id,False,self.run)
+        fd=os.open(self.proof/'status-private.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
+        with os.fdopen(fd,'wb') as output:
+            process=subprocess.Popen([str(self.cli),'--workdir',str(self.run),'--network-id',network,'status','-o','json'],env=native_cli.environment(self.run),cwd=self.run,stdin=subprocess.DEVNULL,stdout=output,stderr=subprocess.DEVNULL,start_new_session=True)
+            try:code=process.wait(timeout=30)
+            finally:self.stop_process(process)
+            if code:raise RuntimeError('qualification_status_capture_failed')
+        self.status={k.lower():v for k,v in json.loads((self.proof/'status-private.json').read_text()).items()}
+        from sqlalchemy.engine import make_url
+        self.admin=make_url(self.status['db_url']).set(username='supabase_admin')
+        if self.admin.host not in ('127.0.0.1','localhost') or self.admin.port!=55482 or self.admin.database!='postgres':raise ValueError('unexpected_native_database')
+        self.urls={}
+
+    def connect(self,role=None):
+        import psycopg
+        url=self.admin if role is None else self.urls[role]
+        return psycopg.connect(url.render_as_string(hide_password=False),connect_timeout=3,autocommit=True)
+
+    def prepare_owners(self):
+        from psycopg import sql
+        # Fresh cluster-only role setup; ordinary helpers own the additional roles.
+        roles=('identity_migrator','access_migrator','access_runtime','scribeswell_runtime')
+        with self.connect() as c:
+            if c.execute("SELECT 1 FROM pg_namespace WHERE nspname IN ('identity','access','scribeswell','scribeswell_studies')").fetchone():raise RuntimeError('nonempty_owner_fixture_refused')
+            c.execute('REVOKE TEMPORARY,CREATE ON DATABASE postgres FROM PUBLIC')
+            # The native image exposes extension diagnostics to PUBLIC. Empty
+            # owner-role qualification requires no inherited table reads. Confine
+            # these fixture ACL changes to this fresh disposable database.
+            public_reads=c.execute("SELECT n.nspname,c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema' AND c.relkind IN ('r','p','v','m','f') AND EXISTS(SELECT 1 FROM aclexplode(c.relacl) a WHERE a.grantee=0 AND a.privilege_type='SELECT')").fetchall()
+            private(self.proof/'fixture-public-read-preparation.json',{'tables':public_reads})
+            for schema,table in public_reads:c.execute(sql.SQL('REVOKE SELECT ON {}.{} FROM PUBLIC').format(sql.Identifier(schema),sql.Identifier(table)))
+            for role in roles:
+                password=secrets.token_urlsafe(32)
+                c.execute(sql.SQL('CREATE ROLE {} LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD {}').format(sql.Identifier(role),sql.Literal(password)))
+                self.urls[role]=self.admin.set(username=role,password=password)
+            # Reproduce the owner-verified native bootstrap graph, not inherited
+            # owner authority: postgres holds the exact ADMIN-only Identity edge.
+            c.execute('GRANT identity_migrator TO postgres WITH ADMIN TRUE, INHERIT FALSE, SET FALSE')
+            c.execute('GRANT access_migrator TO postgres WITH ADMIN TRUE, INHERIT FALSE, SET FALSE')
+            c.execute('SET SESSION AUTHORIZATION postgres;GRANT access_migrator TO postgres WITH ADMIN FALSE, INHERIT FALSE, SET TRUE;RESET SESSION AUTHORIZATION')
+            c.execute('CREATE SCHEMA identity AUTHORIZATION identity_migrator;CREATE SCHEMA access AUTHORIZATION access_migrator')
+            c.execute('SET ROLE access_migrator;GRANT USAGE ON SCHEMA access TO access_runtime;RESET ROLE')
+            c.execute('GRANT USAGE ON SCHEMA auth TO identity_migrator WITH GRANT OPTION;GRANT USAGE ON SCHEMA extensions TO identity_migrator;GRANT SELECT(id),REFERENCES(id),TRIGGER ON auth.users TO identity_migrator;GRANT CREATE,USAGE ON SCHEMA public TO identity_migrator')
+            for helper in ('prepare_identity_projection_role.sql','prepare_identity_operator_roles.sql','prepare_identity_command_role.sql','prepare_identity_target_roles.sql','prepare_identity_account_verification_role.sql','prepare_identity_account_verification_auth.sql','prepare_access_operator_roles.sql','prepare_access_check_reader.sql','prepare_studies_runtime_roles.sql','prepare_studies_auth_evidence.sql'):
+                c.execute((ACCESS/'tools'/helper).read_text())
+            # Access reader preparation predates Studies and requires its exact
+            # two existing owner edges. Stage the later Access edge afterwards.
+            c.execute('REVOKE access_studies_owner FROM access_migrator')
+            c.execute((APP/'tools/sql/prepare_personal_notes_roles.sql').read_text())
+            for role in ('identity_studies_reader_runtime','identity_studies_setup_runtime','access_studies_runtime','access_operator','scribeswell_studies_migrator','scribeswell_studies_runtime'):
+                password=secrets.token_urlsafe(32)
+                c.execute(sql.SQL('ALTER ROLE {} PASSWORD {}').format(sql.Identifier(role),sql.Literal(password)))
+                self.urls[role]=self.admin.set(username=role,password=password)
+        with self.connect() as c:
+            memberships=c.execute("SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),admin_option,to_jsonb(m)->>'inherit_option',to_jsonb(m)->>'set_option' FROM pg_auth_members m WHERE pg_get_userbyid(member) IN ('identity_migrator','access_runtime','authenticated','anon','service_role','supabase_auth_admin') OR pg_get_userbyid(roleid)='identity_migrator' ORDER BY 1,2").fetchall()
+            private(self.proof/'prepared-role-memberships.json',memberships)
+        # Separate owner processes avoid name collisions and preserve real Alembic guards.
+        for owner,config in (('identity','identity-alembic.ini'),):
+            self.migrate(owner,ACCESS/config)
+        with self.connect() as c:
+            c.execute((ACCESS/'tools/prepare_access_check_reader_execution.sql').read_text())
+            c.execute('GRANT access_studies_owner TO access_migrator WITH ADMIN FALSE, INHERIT FALSE, SET TRUE')
+        self.migrate('access',ACCESS/'alembic.ini')
+        self.migrate('scribeswell_studies',APP/'studies-alembic.ini')
+        self.prepare_principals()
+        self.prepare_corpus()
+        self.create_accounts()
+        private(self.proof/'credentials-private.json',{role:url.render_as_string(hide_password=False) for role,url in self.urls.items()})
+        self.observe('before-enrollment',initial=True)
+
+    def migrate(self,owner,config):
+        env={**self.environment,owner.upper()+'_MIGRATION_DATABASE_URL':self.urls[owner+'_migrator'].set(drivername='postgresql+psycopg').render_as_string(hide_password=False)}
+        self.command('migrate-'+owner,[sys.executable,'-I','-B','-m','alembic','-c',config,'upgrade','head'],env=env)
+
+    def prepare_principals(self):
+        self.actor=str(uuid4());self.service_key=secrets.token_urlsafe(32)
+        with self.connect('identity_migrator') as c:
+            c.execute("INSERT INTO identity.actor(id,kind,display_name,actor_key,created_by,updated_by) VALUES(%s,'service','Synthetic integration executor',%s,%s,%s)",(self.actor,'owner-integration.'+self.run_id,self.actor,self.actor))
+            c.execute("INSERT INTO identity.studies_runtime_principal(database_login,executor_actor_id,enabled,created_by,updated_by,operation_id) VALUES('identity_studies_setup_runtime',%s,true,%s,%s,%s)",(self.actor,self.actor,self.actor,str(uuid4())))
+        with self.connect('access_migrator') as c:
+            c.execute("INSERT INTO access.studies_runtime_principal(database_login,executor_actor_id,enabled,created_by,updated_by,operation_id) VALUES('access_studies_runtime',%s,true,%s,%s,%s)",(self.actor,self.actor,self.actor,str(uuid4())))
+            c.execute("INSERT INTO access.operator_principals(database_login,executor_actor_id,enabled,created_by,updated_by) VALUES('access_operator',%s,true,%s,%s)",(self.actor,self.actor,self.actor))
+            for command in ('application.register','permission.register','application.set_enabled'):
+                c.execute("INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,application_id,enabled,created_by,updated_by) VALUES(%s,'access_operator',%s,'platform','scribeswell',true,%s,%s)",(str(uuid4()),command,self.actor,self.actor))
+        for command,payload in (('application.register',{'app_id':'scribeswell','expected_absent':True}),('permission.register',{'app_id':'scribeswell','permission':'scribeswell.studies.use','scope_kind':'account','expected_absent':True}),('application.set_enabled',{'app_id':'scribeswell','enabled':True,'expected_revision':'1'})):
+            self.operator(command,payload)
+
+    def operator(self,command,payload):
+        # Run the existing protected command in its own module namespace.
+        envelope={'schema_version':1,'operation_id':str(uuid4()),'command':command,'scope':{'kind':'platform'},'payload':payload,'reason_code':'synthetic_fixture','evidence_ref':'synthetic:'+self.run_id}
+        path=self.proof/('operator-'+str(uuid4())+'.json');private(path,envelope)
+        code="import os,sys;from sqlalchemy import create_engine;from access_operator import execute;e=create_engine(os.environ['FIXTURE_OPERATOR_URL'],hide_parameters=True);c=e.connect();execute(c,open(sys.argv[1],'rb').read());c.close();e.dispose()"
+        self.command(path.stem,[sys.executable,'-c',code,path],env={**self.environment,'FIXTURE_OPERATOR_URL':self.urls['access_operator'].set(drivername='postgresql+psycopg').render_as_string(hide_password=False)},cwd=ACCESS)
+
+    def prepare_corpus(self):
+        with self.connect() as c:
+            c.execute((APP/'supabase/migrations/20260614000000_scribeswell_create_schema.sql').read_text())
+            c.execute("INSERT INTO scribeswell.book VALUES(1,'Gen','Genesis','בראשית','old','torah',1);INSERT INTO scribeswell.chapter(id,book_id,chapter_num) VALUES(1,1,1);INSERT INTO scribeswell.verse(id,chapter_id,verse_num,book_id,chapter_num) VALUES(1,1,1,1,1);INSERT INTO scribeswell.word(id,verse_id,position,surface_he,display_he) VALUES(1,1,1,'בְּרֵאשִׁית','בְּרֵאשִׁית')")
+            c.execute('GRANT USAGE ON SCHEMA scribeswell TO scribeswell_runtime;GRANT SELECT ON ALL TABLES IN SCHEMA scribeswell TO scribeswell_runtime')
+            for table in ('book','chapter','verse','word','morpheme'):
+                c.execute('CREATE POLICY integration_read ON scribeswell.'+table+' FOR SELECT TO scribeswell_runtime USING(true)')
+
+    def create_accounts(self):
+        import httpx
+        self.accounts=[]
+        api=self.status['api_url'];service=self.status['service_role_key']
+        headers={'apikey':service,'Authorization':'Bearer '+service}
+        with httpx.Client(timeout=5) as client:
+            for _ in range(2):
+                email='studies-'+uuid4().hex+'@example.invalid'
+                response=client.post(api+'/auth/v1/admin/users',headers=headers,json={'email':email,'email_confirm':True})
+                if response.status_code!=200:raise RuntimeError('provider_account_creation_failed')
+                account=response.json()['id']
+                response=client.post(api+'/auth/v1/admin/generate_link',headers=headers,params={'redirect_to':'http://localhost:5188/'},json={'type':'magiclink','email':email})
+                if response.status_code!=200:raise RuntimeError('provider_magic_link_failed')
+                body=response.json();properties=body.get('properties',body)
+                self.accounts.append({'account_id':account,'link':properties['action_link']})
+        private(self.proof/'browser-private.json',{'accounts':self.accounts,'service_key_sentinel':self.service_key,'provider_service_sentinel':self.status['service_role_key'],'proof':str(self.proof)})
+
+    def observe(self,label,initial=False):
+        with self.connect() as c:
+            c.execute('BEGIN READ ONLY')
+            rows=[]
+            for account in self.accounts:
+                id=account['account_id']
+                counts=c.execute('SELECT (SELECT count(*) FROM identity.users WHERE id=%s),(SELECT count(*) FROM identity.org_member WHERE user_id=%s),(SELECT count(*) FROM access.studies_account_grant WHERE account_id=%s),(SELECT count(*) FROM scribeswell_studies.studies WHERE account_id=%s)',(id,id,id,id)).fetchone()
+                if initial and tuple(counts)!=(1,0,0,0):raise AssertionError('fresh_account_owner_state_wrong')
+                rows.append({'account_id':id,'profile_membership_grant_study':list(counts)})
+            notes=c.execute('SELECT account_id,created_by,updated_by,value,revision FROM scribeswell_studies.notes').fetchall()
+            bindings=c.execute('SELECT account_id,actor_id FROM identity.account_actor').fetchall()
+            if initial:assert not bindings,'Check/registration created an account actor before explicit enrollment'
+            if not initial:
+                expected=json.loads((self.proof/'browser-result.json').read_text())
+                assert len(notes)==1 and str(notes[0][0])==self.accounts[0]['account_id']
+                assert notes[0][3]==expected['value']
+                assert (str(notes[0][0]),str(notes[0][1])) in [(str(a),str(b)) for a,b in bindings]
+                assert notes[0][1]==notes[0][2]
+                assert rows[0]['profile_membership_grant_study']==[1,0,1,1]
+                assert rows[1]['profile_membership_grant_study']==[1,0,1,0]
+                assert c.execute("SELECT count(*) FROM scribeswell_studies.receipts WHERE account_id=%s AND command='study.create' AND operation_id=%s",(self.accounts[0]['account_id'],expected['operation'])).fetchone()[0]==1
+                assert c.execute('SELECT count(*) FROM access.studies_enrollment_outcome WHERE account_id=%s AND operation_id=%s',(self.accounts[0]['account_id'],expected['enrollment'])).fetchone()[0]==1
+                for account in self.accounts:
+                    assert c.execute('SELECT count(*) FROM access.studies_assignment_event WHERE account_id=%s',(account['account_id'],)).fetchone()[0]==1
+            c.execute('ROLLBACK')
+        private(self.proof/(label+'.json'),{'accounts':rows,'note_count':len(notes),'actor_bindings':bindings,'independent_sql':True})
+
+    def spawn(self,label,args,env,cwd):
+        fd=os.open(self.proof/(label+'.log'),os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
+        with os.fdopen(fd,'wb') as out:
+            process=subprocess.Popen([str(a) for a in args],cwd=cwd,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
+        self.processes.append(process);return process
+
+    def start_apps(self):
+        owner_code="import os;from main import create_app;os.environ['SCRIBESWELL_SERVICE_KEY']=os.environ['FIXTURE_SERVICE_KEY'];from studies_identity import AsyncDatabase;app=create_app(object(),studies_db=AsyncDatabase(os.environ['FIXTURE_ACCESS_URL']),studies_identity_db=AsyncDatabase(os.environ['FIXTURE_IDENTITY_URL']),studies_setup_db=AsyncDatabase(os.environ['FIXTURE_SETUP_URL']));import uvicorn;uvicorn.run(app,host='127.0.0.1',port=8189,access_log=False,log_level='error')"
+        env={**self.environment,'FIXTURE_SERVICE_KEY':self.service_key,'SUPABASE_URL':self.status['api_url'],'SUPABASE_ANON_KEY':self.status['anon_key'],'FIXTURE_ACCESS_URL':self.urls['access_studies_runtime'].render_as_string(hide_password=False),'FIXTURE_IDENTITY_URL':self.urls['identity_studies_reader_runtime'].render_as_string(hide_password=False),'FIXTURE_SETUP_URL':self.urls['identity_studies_setup_runtime'].render_as_string(hide_password=False)}
+        owner=self.spawn('access-http',[sys.executable,'-c',owner_code],env,ACCESS)
+        wait_http('http://127.0.0.1:8189/health',owner)
+        env={**self.environment,'SCRIBESWELL_DATABASE_URL':self.urls['scribeswell_runtime'].render_as_string(hide_password=False),'SCRIBESWELL_STUDIES_ENABLED':'true','SCRIBESWELL_STUDIES_DATABASE_URL':self.urls['scribeswell_studies_runtime'].render_as_string(hide_password=False),'SCRIBESWELL_STUDIES_ACCESS_URL':'http://127.0.0.1:8189','SCRIBESWELL_STUDIES_SERVICE_KEY':self.service_key,'SUPABASE_URL':self.status['api_url'],'SUPABASE_SECRET_KEY':'','SUPABASE_SERVICE_ROLE_KEY':''}
+        app=self.spawn('scribeswell-http',[sys.executable,'-m','uvicorn','main:app','--host','127.0.0.1','--port','8188','--no-access-log','--log-level','error'],env,APP/'backend')
+        wait_http('http://127.0.0.1:8188/health',app)
+        env={**self.environment,'VITE_STUDIES_ENABLED':'true','VITE_APP_BASE':'/','VITE_PLATFORM_ORIGIN':'','VITE_SUPABASE_URL':self.status['api_url'],'VITE_SUPABASE_ANON_KEY':self.status['anon_key'],'VITE_API_BASE_URL':'http://127.0.0.1:8188','VITE_APP_DIRECTORY_URL':'http://127.0.0.1:8189'}
+        web=self.spawn('vite',['npm','run','dev','--','--host','localhost','--port','5188','--strictPort'],env,APP/'web')
+        wait_http('http://localhost:5188',web)
+
+    def browser(self):
+        def observe_denied_check(process):
+            limit=time.monotonic()+30
+            checkpoint=self.proof/'pre-enrollment-check.json'
+            while not checkpoint.exists():
+                if process.poll() is not None or time.monotonic()>=limit:raise RuntimeError('qualification_pre_enrollment_checkpoint_missing')
+                time.sleep(.05)
+            self.observe('after-protected-check',initial=True)
+            private(self.proof/'pre-enrollment-observed.json',{'zero_effects':True})
+        env={**self.environment,'SCRIBESWELL_OWNER_FIXTURE':str(self.proof/'browser-private.json')}
+        self.command('browser',['node',ROOT/'node_modules/@playwright/test/cli.js','test','--config',APP/'web/playwright.owner-integration.config.cjs'],env=env,cwd=APP/'web',timeout=120,on_started=observe_denied_check)
+
+    def stop_process(self,process):
+        # A launcher may exit while its child still owns our process group.
+        forced=False
+        try:os.killpg(process.pid,signal.SIGTERM)
+        except ProcessLookupError:pass
+        else:
+            limit=time.monotonic()+3
+            while time.monotonic()<limit:
+                process.poll() # Reap an exited leader before checking descendants.
+                try:os.killpg(process.pid,0)
+                except ProcessLookupError:break
+                time.sleep(.05)
+            else:
+                try:os.killpg(process.pid,signal.SIGKILL);forced=True
+                except ProcessLookupError:pass
+        process.wait(timeout=5)
+        self.events.append({'stage':'process-stopped','pid':process.pid,'forced':forced})
+
+    def execute(self):
+        try:
+            import importlib.util
+            for dependency in ('psycopg','sqlalchemy','alembic','httpx','rfc8785'):
+                if importlib.util.find_spec(dependency) is None:raise RuntimeError('qualification_dependency_missing:'+dependency)
+            check_ports();self.wrapper('prepare');self.owned=True
+            self.wrapper('up');self.wrapper('verify');self.capture_status()
+            self.prepare_owners();self.start_apps();self.browser();self.observe('after-browser')
+            self.operator('application.set_enabled',{'app_id':'scribeswell','enabled':False,'expected_revision':'2'})
+            self.command('browser-denied',['node',ROOT/'node_modules/@playwright/test/cli.js','test','--config',APP/'web/playwright.owner-integration.config.cjs','--grep','disabled'],env={**self.environment,'SCRIBESWELL_OWNER_FIXTURE':str(self.proof/'browser-private.json'),'SCRIBESWELL_OWNER_DENIED':'true'},cwd=APP/'web',timeout=90)
+            self.observe('after-denial')
+            from hashlib import sha256
+            if any(sha256(p.read_bytes()).hexdigest()!=digest for p,digest in self.sources.items()):raise RuntimeError('qualification_sources_changed')
+            self.events.append({'stage':'passed'})
+        except BaseException as error:
+            import traceback
+            private(self.proof/'failure.json',{'type':type(error).__name__,'code':str(error) if type(error) is RuntimeError and str(error).startswith('qualification_') else None,'sqlstate':getattr(error,'sqlstate',None),'frames':[{'file':f.filename,'line':f.lineno,'function':f.name} for f in traceback.extract_tb(error.__traceback__)]})
+            self.events.append({'stage':'failed'});raise
+        finally:
+            cleanup_failed=False
+            for process in reversed(self.processes):
+                try:self.stop_process(process)
+                except (OSError,subprocess.TimeoutExpired):
+                    cleanup_failed=True
+                    self.events.append({'stage':'process-stop-failed','pid':process.pid})
+            if self.owned:
+                try:self.wrapper('stop')
+                except Exception:self.events.append({'stage':'stop-failed'});cleanup_failed=True
+            private(self.proof/'result.json',{'run_id':self.run_id,'events':self.events,'scope':'HTTP/domain integration only; no default readiness, signup, release or device claim'})
+            if cleanup_failed:raise RuntimeError('qualification_exact_run_stop_failed')
+
+def qualify():
+    parser=argparse.ArgumentParser(description=__doc__)
+    parser.add_argument('--run-id',required=True);parser.add_argument('--supabase',required=True,type=Path);parser.add_argument('--proof',required=True,type=Path)
+    args=parser.parse_args()
+    Qualification(args.run_id,args.supabase,args.proof).execute()
diff --git a/apps/scribeswell/tests/test_studies_owner_integration.py b/apps/scribeswell/tests/test_studies_owner_integration.py
new file mode 100644
index 0000000..9d74f30
--- /dev/null
+++ b/apps/scribeswell/tests/test_studies_owner_integration.py
@@ -0,0 +1,152 @@
+"""Qualification control-flow acceptance; doubles never establish owner readiness."""
+from pathlib import Path
+import sys
+import uuid
+import pytest
+
+HERE=Path(__file__).parent
+sys.path.insert(0,str(HERE))
+
+def fixture_module():
+    import studies_owner_fixture
+    return studies_owner_fixture
+
+@pytest.fixture(autouse=True)
+def free_ports(monkeypatch):
+    monkeypatch.setattr(fixture_module(),"check_ports",lambda:None)
+
+def test_missing_capability_has_explicit_one_run_entry():
+    module=fixture_module()
+    assert callable(module.qualify)
+    assert (HERE.parent/'tools/py/qualify_studies_owner_integration.py').is_file()
+    assert (HERE.parent/'web/tests/studies-owner.integration.cjs').is_file()
+
+def test_failed_preparation_never_starts_apps_and_stops_only_owned_run(tmp_path):
+    module=fixture_module(); events=[]
+    class Failed(module.Qualification):
+        def wrapper(self,action):events.append(action)
+        def capture_status(self):events.append('status')
+        def prepare_owners(self):raise RuntimeError('synthetic_preparation_failure')
+        def start_apps(self):events.append('apps')
+    run=Failed(str(uuid.uuid4()),Path('/explicit/supabase'),tmp_path/'proof')
+    with pytest.raises(RuntimeError,match='synthetic_preparation_failure'):run.execute()
+    assert events==['prepare','up','verify','status','stop']
+    assert run.events[-1]['stage']=='failed'
+    assert (run.proof/'result.json').stat().st_mode&0o777==0o600
+
+def test_existing_proof_and_noncanonical_run_refuse(tmp_path):
+    module=fixture_module()
+    with pytest.raises(ValueError):module.Qualification('not-a-uuid',Path('/explicit/supabase'),tmp_path/'proof')
+    proof=tmp_path/'existing';proof.mkdir()
+    with pytest.raises(FileExistsError):module.Qualification(str(uuid.uuid4()),Path('/explicit/supabase'),proof)
+
+def test_collision_refuses_before_wrapper_or_adoption(tmp_path,monkeypatch):
+    module=fixture_module();run=module.Qualification(str(uuid.uuid4()),Path('/explicit/supabase'),tmp_path/'proof')
+    monkeypatch.setattr(module,'check_ports',lambda:(_ for _ in ()).throw(RuntimeError('occupied_port')))
+    called=[];monkeypatch.setattr(run,'wrapper',lambda action:called.append(action))
+    with pytest.raises(RuntimeError,match='occupied_port'):run.execute()
+    assert not called
+
+def test_interrupt_stops_owned_processes_and_exact_run(tmp_path):
+    module=fixture_module();events=[]
+    class Interrupted(module.Qualification):
+        def wrapper(self,action):events.append(action)
+        def capture_status(self):pass
+        def prepare_owners(self):raise KeyboardInterrupt()
+    with pytest.raises(KeyboardInterrupt):Interrupted(str(uuid.uuid4()),Path('/explicit/supabase'),tmp_path/'proof').execute()
+    assert events==['prepare','up','verify','stop']
+
+def test_exact_run_stop_failure_is_a_failure(tmp_path):
+    module=fixture_module()
+    class StopFailed(module.Qualification):
+        def wrapper(self,action):
+            if action=='stop':raise RuntimeError('synthetic_stop_failure')
+        def capture_status(self):pass
+        def prepare_owners(self):raise RuntimeError('synthetic_preparation_failure')
+    run=StopFailed(str(uuid.uuid4()),Path('/explicit/supabase'),tmp_path/'proof')
+    with pytest.raises(RuntimeError,match='qualification_exact_run_stop_failed'):run.execute()
+    assert run.events[-1]['stage']=='stop-failed'
+
+def test_exited_launcher_still_terminates_its_owned_group(tmp_path,monkeypatch):
+    module=fixture_module();signals=[]
+    class Process:
+        pid=100000
+        def poll(self):return 0
+        def wait(self,timeout):return 0
+    class Failed(module.Qualification):
+        def wrapper(self,action):pass
+        def capture_status(self):pass
+        def prepare_owners(self):raise RuntimeError('synthetic_failure')
+    def killpg(pid,signum):
+        signals.append((pid,signum))
+        if signum==0:raise ProcessLookupError()
+    monkeypatch.setattr(module.os,'killpg',killpg)
+    run=Failed(str(uuid.uuid4()),Path('/explicit/supabase'),tmp_path/'proof');run.processes.append(Process())
+    with pytest.raises(RuntimeError,match='synthetic_failure'):run.execute()
+    assert signals[0]==(100000,module.signal.SIGTERM)
+
+def test_process_cleanup_error_still_stops_exact_native_run(tmp_path):
+    module=fixture_module();actions=[]
+    class Process:pid=100000
+    class Failed(module.Qualification):
+        def wrapper(self,action):actions.append(action)
+        def capture_status(self):pass
+        def prepare_owners(self):raise RuntimeError('synthetic_failure')
+        def stop_process(self,process):raise OSError('synthetic_cleanup_failure')
+    run=Failed(str(uuid.uuid4()),Path('/explicit/supabase'),tmp_path/'proof');run.processes.append(Process())
+    with pytest.raises(RuntimeError,match='qualification_exact_run_stop_failed'):run.execute()
+    assert actions[-1]=='stop'
+    assert any(e['stage']=='process-stop-failed' for e in run.events)
+
+def test_callback_failure_never_writes_signed_url_diagnostics(tmp_path):
+    """Execute a throwing callback scenario through real Playwright failure output."""
+    import json
+    import subprocess
+    module=fixture_module();reporter=module.APP/'web/tests/studies-owner-reporter.cjs'
+    # A harness fault, not an Auth response/session/private HTTP substitute.
+    sentinel='http://provider.invalid/verify?token=private-synthetic-token'
+    test_file=module.APP/'web/tests'/('owner-safety-'+uuid.uuid4().hex+'.cjs')
+    config=tmp_path/'playwright.config.cjs'
+    config.write_text('module.exports='+json.dumps({'testDir':str(test_file.parent),'testMatch':test_file.name,'reporter':[[str(reporter)]],'outputDir':str(tmp_path/'results')})+';')
+    test_file.write_text("const {test}=require('@playwright/test');const {safeCall}=require('./studies-owner-reporter.cjs');test('callback failure',async()=>safeCall(async()=>{throw new Error("+json.dumps(sentinel)+");}));")
+    try:
+        result=subprocess.run(['node',str(module.ROOT/'node_modules/@playwright/test/cli.js'),'test','--config',str(config)],capture_output=True,text=True,timeout=30,env={**module.os.environ,'PLAYWRIGHT_NO_COPY_PROMPT':'1'})
+        assert result.returncode==1
+        diagnostics=result.stdout+result.stderr+'\n'.join(p.read_text(errors='replace') for p in (tmp_path/'results').rglob('*') if p.is_file())
+        assert sentinel not in diagnostics
+        assert 'private-synthetic-token' not in diagnostics
+        assert 'browser-case' in result.stdout
+    finally:test_file.unlink(missing_ok=True)
+
+@pytest.mark.parametrize('interrupt',[False,True])
+def test_timed_out_or_interrupted_command_stops_real_descendant_before_return(tmp_path,interrupt):
+    import os
+    import signal
+    import subprocess
+    import time
+    module=fixture_module();run=module.Qualification(str(uuid.uuid4()),Path('/explicit/supabase'),tmp_path/'proof')
+    pidfile=tmp_path/'descendant.pid'
+    child_code='import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(60)'
+    launcher='import subprocess,sys,time;from pathlib import Path;p=subprocess.Popen([sys.executable,"-c",'+repr(child_code)+']);Path('+repr(str(pidfile))+').write_text(str(p.pid));time.sleep(60)'
+    thread=None
+    if interrupt:
+        import threading
+        def interrupt_when_started():
+            limit=time.monotonic()+3
+            while not pidfile.exists() and time.monotonic()<limit:time.sleep(.01)
+            if pidfile.exists():os.kill(os.getpid(),signal.SIGINT)
+        thread=threading.Thread(target=interrupt_when_started,daemon=True);thread.start()
+    try:
+        with pytest.raises(KeyboardInterrupt if interrupt else subprocess.TimeoutExpired):
+            run.command('synthetic-child-boundary',[sys.executable,'-c',launcher],timeout=5 if interrupt else .5)
+        if thread:thread.join(timeout=3)
+        pid=int(pidfile.read_text())
+        state=Path('/proc')/str(pid)/'stat'
+        limit=time.monotonic()+.5
+        while state.exists() and state.read_text().split()[2]!='Z' and time.monotonic()<limit:time.sleep(.01)
+        assert not state.exists() or state.read_text().split()[2]=='Z','Owned command descendant still executes after timeout'
+        assert any(e.get('stage')=='process-stopped' and e.get('forced') for e in run.events)
+    finally:
+        if pidfile.exists():
+            try:os.kill(int(pidfile.read_text()),signal.SIGKILL)
+            except ProcessLookupError:pass
diff --git a/apps/scribeswell/tools/py/qualify_studies_owner_integration.py b/apps/scribeswell/tools/py/qualify_studies_owner_integration.py
new file mode 100644
index 0000000..e094dab
--- /dev/null
+++ b/apps/scribeswell/tools/py/qualify_studies_owner_integration.py
@@ -0,0 +1,14 @@
+"""Explicit single-use real owner integration; credentials stay in private evidence."""
+import sys
+import signal
+from pathlib import Path
+sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tests'))
+from studies_owner_fixture import qualify
+if __name__=='__main__':
+    def interrupted(signum,frame):raise KeyboardInterrupt()
+    signal.signal(signal.SIGTERM,interrupted)
+    try:qualify()
+    except KeyboardInterrupt:raise SystemExit(130) from None
+    except Exception as error:
+        print('studies_owner_integration_failed:'+type(error).__name__,file=sys.stderr)
+        raise SystemExit(1) from None
diff --git a/apps/scribeswell/web/playwright.owner-integration.config.cjs b/apps/scribeswell/web/playwright.owner-integration.config.cjs
new file mode 100644
index 0000000..8e2059f
--- /dev/null
+++ b/apps/scribeswell/web/playwright.owner-integration.config.cjs
@@ -0,0 +1,5 @@
+const {defineConfig}=require('@playwright/test');
+// Do not capture a private DOM snapshot in automatic failure context.
+process.env.PLAYWRIGHT_NO_COPY_PROMPT='1';
+if(!process.env.SCRIBESWELL_OWNER_FIXTURE)throw Error('Explicit newly owned fixture required');
+module.exports=defineConfig({testDir:'tests',testMatch:'studies-owner.integration.cjs',workers:1,retries:0,timeout:60000,reporter:[[require.resolve('./tests/studies-owner-reporter.cjs')]],outputDir:require('path').join(require('path').dirname(process.env.SCRIBESWELL_OWNER_FIXTURE),'browser-output'),use:{baseURL:'http://localhost:5188',headless:true,trace:'off',video:'off',screenshot:'off'}});
diff --git a/apps/scribeswell/web/tests/studies-owner.integration.cjs b/apps/scribeswell/web/tests/studies-owner.integration.cjs
new file mode 100644
index 0000000..e272531
--- /dev/null
+++ b/apps/scribeswell/web/tests/studies-owner.integration.cjs
@@ -0,0 +1,93 @@
+// Actual Auth and private HTTP throughout. No routes, fabricated sessions or tokens.
+const {test,expect}=require('@playwright/test');
+const {safeScenario}=require('./studies-owner-reporter.cjs');
+const fs=require('fs'),path=require('path'),crypto=require('crypto');
+const fixture=JSON.parse(fs.readFileSync(process.env.SCRIBESWELL_OWNER_FIXTURE,'utf8'));
+const proof=path.dirname(process.env.SCRIBESWELL_OWNER_FIXTURE);
+function stage(name){fs.appendFileSync(path.join(proof,'browser-stages.jsonl'),JSON.stringify({stage:name})+'\n',{mode:0o600});}
+const text='בְּרֵאשִׁית — e\u0301 שָׁלוֹם';
+async function request(page,route,method='GET',body){
+ const response=await page.evaluate(async({route,method,body})=>{
+  const {supabase}=await import('/src/lib/supabase.ts');const {data}=await supabase.auth.getSession();
+  const response=await fetch(route,{method,headers:{Authorization:'Bearer '+data.session.access_token,'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{})});
+  return {status:response.status,body:await response.json(),cache:response.headers.get('cache-control')};
+ },{route,method,body});
+ const known=['authentication_required','studies_access_denied','studies_access_unavailable','resource_unavailable','note_revision_conflict','operation_payload_mismatch','operation_unresolved','studies_storage_unavailable','request_deadline_exceeded','scribeswell_personal_notes_input_invalid'];
+ fs.appendFileSync(path.join(proof,'http-observations.jsonl'),JSON.stringify({path:new URL(route,'http://localhost:5188').pathname,method,status:response.status,code:known.includes(response.body.code)?response.body.code:null})+'\n',{mode:0o600});
+ return response;
+}
+async function login(page,account){
+ const statuses=[];
+ page.on('response',response=>{const u=new URL(response.url());if(['/auth/v1/verify','/auth/v1/user'].includes(u.pathname))statuses.push({path:u.pathname,status:response.status()});});
+ try{
+  try{await page.goto(account.link);}catch{throw Error('Provider callback navigation failed');}
+  await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();
+  await expect.poll(()=>new URL(page.url()).hash==='').toBe(true);
+  stage('provider-callback-confirmed');
+ }catch{
+  const u=new URL(page.url());
+  const observation={stage:'provider-callback-failed',origin:u.origin,path:u.pathname,query_keys:[...new URLSearchParams(u.search).keys()],fragment_keys:[...new URLSearchParams(u.hash.slice(1)).keys()],statuses};
+  // Only selected booleans and endpoint/status fields; never URLs with values,
+  // provider error bodies, tokens, email, page DOM or session contents.
+  observation.sign_in_visible=await page.getByRole('button',{name:'Sign in',exact:true}).first().isVisible().catch(()=>false);
+  observation.callback_notice=await page.getByText(/This confirmation link is invalid/).isVisible().catch(()=>false);
+  fs.appendFileSync(path.join(proof,'browser-stages.jsonl'),JSON.stringify(observation)+'\n',{mode:0o600});
+  throw Error('Provider callback was not acknowledged');
+ }
+}
+
+if(!process.env.SCRIBESWELL_OWNER_DENIED){
+ test('actual owner enrollment, lost completed replies, editor autosave, reload and second-account isolation',safeScenario(async({browser,page})=>{
+  let leaked=false;const scans=[];const sentinels=[fixture.service_key_sentinel,fixture.provider_service_sentinel];
+  function inspect(target){
+   target.on('request',req=>{if(Object.values(req.headers()).some(v=>sentinels.some(key=>v.includes(key))))leaked=true;});
+   target.on('response',response=>{if(new URL(response.url()).origin==='http://localhost:5188'&&/json|javascript|text/.test(response.headers()['content-type']||''))scans.push(response.text().then(body=>{if(sentinels.some(key=>body.includes(key)))leaked=true;}).catch(()=>{}));});
+  }
+  inspect(page);
+  stage('first-provider-callback');await login(page,fixture.accounts[0]);
+  stage('public-reader');await expect(page.getByText('בְּרֵאשִׁית',{exact:true}).first()).toBeVisible();
+  stage('before-enrollment-denial');const denied=await request(page,'/api/studies');expect(denied.status).toBe(503);expect(denied.body.code).toBe('studies_access_unavailable');
+  fs.writeFileSync(path.join(proof,'pre-enrollment-check.json'),JSON.stringify({status:denied.status,code:denied.body.code}),{flag:'wx',mode:0o600});
+  const oracleDeadline=Date.now()+30000;
+  while(!fs.existsSync(path.join(proof,'pre-enrollment-observed.json'))){if(Date.now()>oracleDeadline)throw Error('Independent pre-enrollment SQL observation unavailable');await new Promise(resolve=>setTimeout(resolve,50));}
+  await page.getByRole('button',{name:'Studies',exact:true}).click();
+  // A completed HTTP response is deliberately discarded, then original operation retried.
+  stage('enrollment-completed-reply-retry');const enrollment={operation_id:crypto.randomUUID()};
+  expect((await request(page,'/api/studies/enrollment','POST',enrollment)).status).toBe(200);
+  const replay=await request(page,'/api/studies/enrollment','POST',enrollment);expect(replay.status).toBe(200);expect(replay.body.operation_id).toBe(enrollment.operation_id);
+  stage('create-completed-reply-retry');const create={operation_id:crypto.randomUUID(),title:null};
+  expect((await request(page,'/api/studies','POST',create)).status).toBe(200);
+  const retried=await request(page,'/api/studies','POST',create);expect(retried.status).toBe(200);
+  const study=retried.body.study_id;
+  await page.reload();await page.getByRole('button',{name:'Studies',exact:true}).click();
+  await page.getByRole('button',{name:'Untitled study',exact:true}).click();
+  await page.getByRole('button',{name:'Add note',exact:true}).click();
+  stage('editor-autosave');const editor=page.getByLabel('Note text',{exact:true});await editor.fill(text);
+  await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
+  const notes=await request(page,`/api/studies/${study}/notes`);expect(notes.status).toBe(200);expect(notes.body.items.length===1).toBe(true);
+  const note=notes.body.items[0];expect(JSON.stringify(note.value).includes(text)).toBe(true);
+  await page.reload();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Untitled study',exact:true}).click();
+  await page.getByRole('button',{name:text,exact:true}).click();expect(await editor.textContent()===text).toBe(true);
+  stage('second-account-isolation');const context=await browser.newContext();const other=await context.newPage();inspect(other);await login(other,fixture.accounts[1]);
+  expect((await request(other,'/api/studies/enrollment','POST',{operation_id:crypto.randomUUID()})).status).toBe(200);
+  for(const route of [`/api/studies/${study}`,`/api/studies/${study}/notes/${note.id}`])expect((await request(other,route)).status).toBe(404);
+  expect((await request(other,`/api/studies/${study}/notes/${note.id}`,'PUT',{operation_id:crypto.randomUUID(),expected_revision:note.revision,value:note.value})).status).toBe(404);
+  expect((await request(other,`/api/operations/${create.operation_id}?command=study.create`)).body.status).toBe('unresolved');
+  expect((await request(other,'/api/studies')).body.items.length===0).toBe(true);
+  const stored=await context.storageState();fs.writeFileSync(path.join(proof,'other-context-private.json'),JSON.stringify(stored),{flag:'wx',mode:0o600});await context.close();
+  fs.writeFileSync(path.join(proof,'owner-context-private.json'),JSON.stringify(await page.context().storageState()),{flag:'wx',mode:0o600});
+  await Promise.all(scans);const result={study,note:note.id,operation:create.operation_id,enrollment:enrollment.operation_id,value:note.value,leaked};expect(leaked).toBe(false);
+  fs.writeFileSync(path.join(proof,'browser-result.json'),JSON.stringify(result),{flag:'wx',mode:0o600});
+ }));
+}else{
+ test('disabled authority refuses read write lookup and enrollment replay; public reading works',safeScenario(async({browser})=>{
+  stage('disabled-authority');const result=JSON.parse(fs.readFileSync(path.join(proof,'browser-result.json'),'utf8'));
+  const context=await browser.newContext({storageState:path.join(proof,'owner-context-private.json')});const page=await context.newPage();await page.goto('/');
+  for(const route of ['/api/studies',`/api/studies/${result.study}`,`/api/operations/${result.operation}?command=study.create`])expect((await request(page,route)).status).toBe(403);
+  expect((await request(page,'/api/studies','POST',{operation_id:result.operation,title:null})).status).toBe(403);
+  expect((await request(page,`/api/studies/${result.study}/notes/${result.note}`,'PUT',{operation_id:crypto.randomUUID(),expected_revision:'2',value:result.value})).status).toBe(403);
+  expect((await request(page,'/api/studies/enrollment','POST',{operation_id:result.enrollment})).status).toBe(403);
+  stage('public-reader');await expect(page.getByText('בְּרֵאשִׁית',{exact:true}).first()).toBeVisible();await context.close();
+  fs.writeFileSync(path.join(proof,'browser-denial-result.json'),JSON.stringify({read_write_lookup_enrollment_denied:true,public_reader_available:true}),{flag:'wx',mode:0o600});
+ }));
+}
diff --git a/apps/scribeswell/web/tests/studies-owner-reporter.cjs b/apps/scribeswell/web/tests/studies-owner-reporter.cjs
new file mode 100644
index 0000000..8b890a0
--- /dev/null
+++ b/apps/scribeswell/web/tests/studies-owner-reporter.cjs
@@ -0,0 +1,15 @@
+// Qualification diagnostics contain only source locations/status, never vendor
+// errors, browser console payloads, locator details or signed callback URLs.
+class SafeReporter {
+ onTestEnd(test,result){process.stdout.write(JSON.stringify({event:'browser-case',line:test.location.line,status:result.status,duration_ms:result.duration})+'\n');}
+ onError(){process.stdout.write(JSON.stringify({event:'browser-global-failure'})+'\n');}
+ onEnd(result){process.stdout.write(JSON.stringify({event:'browser-finished',status:result.status,duration_ms:result.duration})+'\n');}
+}
+async function safeCall(body){
+ try{return await body();}catch{throw new Error('Owner integration browser case failed; inspect safe stage and source references.');}
+}
+function safeScenario(body){return async ({browser,page})=>safeCall(()=>body({browser,page}));}
+module.exports=SafeReporter;
+module.exports.safeScenario=safeScenario;
+
+module.exports.safeCall=safeCall;
diff --git a/apps/scribeswell/web/playwright.session.config.cjs b/apps/scribeswell/web/playwright.session.config.cjs
index 19db8ff..3744d4d 100644
--- a/apps/scribeswell/web/playwright.session.config.cjs
+++ b/apps/scribeswell/web/playwright.session.config.cjs
@@ -1,7 +1,7 @@
 const {defineConfig}=require('@playwright/test');
 const path=require('node:path');
 const env={VITE_SUPABASE_URL:'https://pts-browser-test.supabase.co',VITE_SUPABASE_ANON_KEY:'test-public-key',VITE_APP_DIRECTORY_URL:'http://127.0.0.1:8001'};
-module.exports=defineConfig({testDir:'tests',testMatch:'*.integration.cjs',use:{baseURL:'http://localhost:5183',headless:true},workers:1,webServer:[
+module.exports=defineConfig({testDir:'tests',testMatch:'session.integration.cjs',use:{baseURL:'http://localhost:5183',headless:true},workers:1,webServer:[
  {command:'node tests/session-api-fixture.cjs',cwd:__dirname,url:'http://127.0.0.1:5185/health',reuseExistingServer:false},
  {command:'npm run dev -- --host localhost --port 5184',cwd:__dirname,url:'http://localhost:5184/scribeswell/',reuseExistingServer:false,env:{...env,VITE_API_BASE_URL:'http://127.0.0.1:5185',VITE_APP_BASE:'/scribeswell/',VITE_PLATFORM_ORIGIN:'http://localhost:5183'}},
  {command:'npm run dev -- --host localhost --port 5183',cwd:path.resolve(__dirname,'../../pts/web'),url:'http://localhost:5183',reuseExistingServer:false,env:{...env,VITE_PTS_API_URL:'http://127.0.0.1:8010',VITE_SCRIBESWELL_DEV_URL:'http://localhost:5184'}}
diff --git a/apps/scribeswell/docs/PERSONAL_NOTES_V1.md b/apps/scribeswell/docs/PERSONAL_NOTES_V1.md
index e3fdde6..4c8c77f 100644
--- a/apps/scribeswell/docs/PERSONAL_NOTES_V1.md
+++ b/apps/scribeswell/docs/PERSONAL_NOTES_V1.md
@@ -1,6 +1,6 @@
 # Personal study notes: first wire contract
 
-This app-owned contract supports the first create/write/reopen milestone. **Implemented:** strict DTOs, generated OpenAPI/TypeScript, bounded same-origin private API, explicit Access enrollment/check adapters, app-owned PostgreSQL persistence and receipt recovery, controlled private Alembic history, and Studies/Analysis note editing with autosave. **Activation remains disabled in production.** The runtime is an explicit development/test opt-in pending coordinated owner/migration/integration qualification; public reading and standalone signup remain independent. Native SQL and browser proof are recorded below; synthetic Access responses do not establish live Identity/Access authorization.
+This app-owned contract supports the first create/write/reopen milestone. **Implemented:** strict DTOs, generated OpenAPI/TypeScript, bounded same-origin private API, explicit Access enrollment/check adapters, app-owned PostgreSQL persistence and receipt recovery, controlled private Alembic history, and Studies/Analysis note editing with autosave. **Activation remains disabled in production.** The runtime is an explicit development/test opt-in pending coordinated startup/release qualification; public reading and standalone signup remain independent. Native SQL/browser proof and actual owner HTTP/domain integration are recorded below; synthetic Access responses alone do not establish live Identity/Access authorization.
 
 The canonical Studies SPEC, UX and accepted platform ADRs retain authority. This milestone is ordinary owner-only studies and notes. Sharing, private responses, study metadata editing, introduction/source metadata, passage lists, deliberate passage links, highlights, conflict copies, deletion and search retain their agreed requirements for later consuming slices. No product requirement is removed. This is partial D2 contract readiness, not D1–D5 closure.
 
@@ -102,9 +102,9 @@ ADR-0020 requires a controlled additive migration and qualified roles **before**
 
 | Existing acceptance scope | Evidence now | Remaining proof |
 | --- | --- | --- |
-| CAP-1/CAP-3 create/write/reopen | Native SQL + browser create/write/reopen and actual formatting toolbar/reload | Live owner/provider/integration qualification |
+| CAP-1/CAP-3 create/write/reopen | Native SQL + browser create/write/reopen and actual formatting toolbar/reload | Default owner startup/readiness and coordinated release qualification |
 | CAP-9 saving and lifecycle | Strict revisions, native no-op/replay/concurrency/lifecycle and browser delayed/unknown outcomes | Wider deferred copy/delete/richer-content workflows |
-| D1 identity/access | Bounded exact app HTTP binding consumes delivered owner contract | Coordinated current owner/provider and activation qualification |
+| D1 identity/access | Bounded exact app HTTP binding consumes delivered owner contract | Default owner startup/readiness and activation qualification |
 | D2 data/save | Versioned first wire, private schema and native permission/transaction proof | Catalogue anchors, private responses/copy/delete and richer content contracts |
 | D3/D4/D5 | Existing requirements preserved | Existing owner/release/browser evidence gates remain open |
 
@@ -176,3 +176,19 @@ Scaffold impact: installer-owned shared migration helper is consumed unchanged.
 UI: no promotion is justified yet for this app-specific editor/lane; no generic engine
 was added. Agent context and accepted ADRs: unchanged. Documentation: this contract and
 canonical companions now distinguish runtime evidence from activation/readiness.
+
+## Actual owner integration qualification — 2026-10-25
+
+The separate one-run fixture and Playwright configuration now pass through the actual
+app, Access/Identity owner SQL, native local Supabase Auth and provider-issued callbacks.
+[Owner integration evidence](STUDIES_OWNER_INTEGRATION_EVIDENCE.md) records the complete
+source-frozen run, independent SQL/actor/duplicate-effect observations, protected disable,
+second-account isolation, earlier failed preparations and exact-run normal stop.
+Actual initial checks preserve zero effects before explicit enrollment; the native
+owner returns a safe503 while no actor has been explicitly prepared. Both real browser
+cases and all independent SQL stages passed. Synthetic owner tests remain consuming
+contract evidence; this new result establishes the stated local HTTP/domain chain.
+Standalone signup, default Access startup/readiness, production release and physical
+devices remain unqualified. Owner implementations and retained runs were preserved.
+The separate broad browser regression had three failures that passed unchanged in
+isolated reruns. Their cause is not established; this is not a full broad pass.
diff --git a/apps/scribeswell/docs/STUDIES_OWNER_INTEGRATION_EVIDENCE.md b/apps/scribeswell/docs/STUDIES_OWNER_INTEGRATION_EVIDENCE.md
new file mode 100644
index 0000000..083025e
--- /dev/null
+++ b/apps/scribeswell/docs/STUDIES_OWNER_INTEGRATION_EVIDENCE.md
@@ -0,0 +1,145 @@
+# Personal Studies owner integration qualification
+
+**Actual local HTTP/domain integration passed on 2026-10-25** in one fresh native
+run, `41b8351e-bcc4-4128-ac22-d7ef3dc561b3`. Both real-provider browser scenarios,
+independent SQL observations and exact-run normal stop passed. This does not qualify
+standalone signup, default Access startup/readiness, production activation, coordinated
+release/backup/restore or physical devices. Wider Studies scope remains unchanged.
+Independent delivery review is still required.
+
+The approved source of intent is
+[spec-scribeswell-owner-integration.md](../../../_bmad-output/implementation-artifacts/spec-scribeswell-owner-integration.md).
+All three frontmatter context files were loaded before implementation. Owner code,
+migrations, generated references and provider configuration were preserved. The actual
+Access app uses its existing database-injection seam in a separate process; default
+release-artifact startup validation is explicitly outside this HTTP/domain proof.
+
+## Final executed native proof
+
+```sh
+/tmp/scribeswell-host-tests-312/bin/python apps/scribeswell/tools/py/qualify_studies_owner_integration.py --run-id 41b8351e-bcc4-4128-ac22-d7ef3dc561b3 --supabase /home/ck/repos/innodat/agriplatform/platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase --proof /tmp/scribeswell-owner-integration-41b8351e
+```
+
+Result: **exit 0**. Private evidence remains in the explicit proof directory; no
+credentials, signed links, sessions or private content are reproduced here. The
+fixture records 173 source hashes at entry and refuses success if those sources
+change. Independent inspection confirmed all 173 still match. `browser.log` records
+one passed case (6,484 ms); `browser-denied.log` records one passed case (1,865 ms).
+No owner integration case was skipped. All owned app groups stopped gracefully;
+no forced termination occurred in this successful run. `wrapper-stop.log` records
+exit 0 for this exact new project/run. Native data and private evidence are retained.
+
+The wrapper performs prepare/up/verify before ordinary Identity21, Access16 and
+Scribeswell private-head migrations. Fixture principal setup uses the actual owner
+migrator logins. App/permission registration and later disable use the existing
+protected Access operator; no user grants are seeded. Auth admin creates only fresh
+local synthetic accounts, with undelivered generated magic links. Browsers follow
+actual provider verification redirects to the supported reader root and use SDK-created
+sessions. No protected HTTP/Auth interception or session-storage injection is used.
+
+| Frozen matrix row | Executed evidence and result |
+| --- | --- |
+| Fresh verified reader: actual profile, zero memberships/grant/study; protected refusal; public reading | `before-enrollment.json` and `after-protected-check.json`: both accounts `[profile=1,membership=0,grant=0,study=0]`, zero actor bindings/notes. Actual callback confirmed and public Hebrew rendered. The actual fresh check returned503 `studies_access_unavailable`, matching the owner's missing-actor contract; check creates nothing. Browser pauses on a bounded fixture-only file checkpoint until independent SQL confirms zero effects, then may enroll. **Passed.** |
+| Explicit enrollment/create, Hebrew/combining marks, autosave/reload/reopen, durable attribution | Real app→Access→Identity/Auth checks and restricted app SQL. UI autosaves `בְּרֵאשִׁית — é שָׁלוֹם`; reload/reopen returns identical text. `after-browser.json` SQL oracle compares the full acknowledged aggregate, creation/update actor and durable `identity.account_actor` binding. One note, one owner study, zero memberships. **Passed.** |
+| Second account isolation; no browser service credentials | Second real callback/session/enrollment; foreign study/note read and replacement each404, foreign operation lookup unresolved, own list empty. Request-header/response-body sentinel checks across both contexts found neither server service credential. **Passed.** |
+| Completed enrollment/create reply discarded, original operation retried after current checks | Real completed replies are discarded, original operation/payload retried. Independent SQL confirms one original receipt, one study and one initial assignment event per account. Disabled original-operation replay later403. **Passed.** |
+| Protected operator disables authority; subsequent read/write/lookup deny; public reading works | Existing `application.set_enabled` command with current revision; separate real browser phase proves list/detail/write/lookup and original enrollment replay403, while public Hebrew remains available. `after-denial.json` verifies identical one-note/one-study effects and two actor bindings. **Passed.** |
+| Preparation/migration failure, occupied ports, interruption; no premature startup/adoption | Actual failed native preparations and actual collision refusals below started no apps. Focused tests prove interrupt/exact-stop ordering, cleanup failure propagation and real command-descendant termination on timeout/SIGINT. Only owned process groups and exact newly created runs are stopped. **Passed within those stated scopes.** |
+
+Selected HTTP observations: eight200, six403, three404 and the initial503. Diagnostic
+logs contain only safe stage/source references, endpoint paths, status and allowlisted
+closed error identifiers. Traces, screenshots, video, automatic DOM snapshots, raw
+errors and browser console payloads are disabled/suppressed. SDK session snapshots and
+private proof values are designated0600 evidence/configuration, never diagnostic dumps.
+
+## Preparation and acceptance failures retained
+
+Each native invocation used the exact final command prefix above with its listed
+`--run-id` and `--proof /tmp/scribeswell-owner-integration-<prefix>`. Every started
+owned native run received its own successful exact normal stop; none was resumed,
+reset, adopted or automatically reversed. Collision attempts performed no wrapper
+operation and no cleanup. Earlier attempts are diagnostic failures, not final proof.
+
+| Run ID | Proof suffix | Actual result |
+| --- | --- | --- |
+| `07d59362-a27f-4ecd-9dc4-bc020bf0389e` | `07d59362` | Native prepare/up/verify passed; Identity preflight refused `identity_authority_role_unsafe`. Native extension diagnostic views exposed inherited PUBLIC reads. Fixture now records/revokes only those PUBLIC table reads inside its own fresh database. No app startup. |
+| `dfa62b33-3682-48a2-90e4-29ec47333e04` | `dfa62b33` | Identity0020 refused `identity_catalog_mismatch:role_memberships`. No app startup. |
+| `ff78d96e-a4ef-49ea-b73b-51a10963f61d` | `ff78d96e` | Fresh reproduction retained selected role metadata/source hashes; same refusal. Fixture had omitted the trusted native ADMIN-only Identity migrator bootstrap edge. Exact existing native Access ADMIN-only/SET-only edges were also prepared; the later Access Studies edge is staged after its existing reader helper. No owner implementation/reference was changed. |
+| `b07d615c-dd38-4ea7-8878-4652beb91347` | `b07d615c` | Actual55481/55482 collision refused before wrapper prepare. Retained foreign run left untouched. |
+| `5f322229-d7db-4601-aa60-52b77d7df650` | `5f322229` | All ordinary owner/app migrations passed; fixture principal insertion under superuser refused42501. Fixture corrected to use the actual owner migrator logins. No app startup. |
+| `d421ca22-8e0c-4011-90ab-f5c71b08fa68` | `d421ca22` | Migrations/owner-login principal setup passed; protected operator import refused missing `rfc8785` in the selected interpreter. Installed the owner's existing pinned0.1.4 dependency in that isolated interpreter; no repository dependency baseline changed. No app startup. |
+| `7ef9008d-a72b-47ad-b81e-b84679db7f71` | `7ef9008d` | All setup, provider profiles and initial SQL passed; actual services/app started. Browser failed while last stage label was first-provider-callback. Original diagnosis remains provisional because this attempt lacked the later safe callback sub-stages. It is not proof of an Auth defect. |
+| `2e9f1f64-1951-4fa0-b28f-1d020ec66c6b` | `2e9f1f64` | Actual55482 collision refused before wrapper prepare; read-only follow-up confirmed active55481/55482 listeners. Foreign run left untouched. |
+| `d4ef1f59-d9f5-4225-99d6-d98ece9648c2` | `d4ef1f59` | Safe callback failure observer was not entered: login completed; the following public Hebrew assertion failed. Fixture had omitted `display_he`, which the actual reader renders. Minimal corpus sample corrected; no Auth/product change. |
+| `18c32e46-e361-4cd8-933d-599650b0f085` | `18c32e46` | Explicit callback-confirmed/public-reader stages passed; fixture incorrectly expected403 for a fresh account check. Existing owner `studies_access.py`54–55 and `STUDIES-ENROLLMENT.md` specify missing-actor503 without implicit setup. Expectation corrected to that documented safe contract; final run records the actual503/code before assertion and independently checks zero effects. |
+| `41b8351e-bcc4-4128-ac22-d7ef3dc561b3` | `41b8351e` | Complete source-frozen native/browser/SQL qualification passed; exact normal stop passed. |
+
+The first two attempts predate source snapshot capture and cannot supply source-bound
+success. The first test attempt using `.venv/bin/python` lacked pytest; the existing
+isolated interpreter was then used. Initial missing-capability acceptance observed
+five `ModuleNotFoundError` failures before the fixture was implemented. The signed-link
+redaction harness initially failed because its wrapper did not meet Playwright's
+fixture-destructuring contract; that fixture-only wrapper was corrected.
+
+A real-process acceptance test first demonstrated that `subprocess.run(timeout)` left
+an owned TERM-ignoring descendant executing. Command/status capture now use new process
+groups and bounded TERM/KILL cleanup before outer exact-run stop. An immediate `/proc`
+check also observed a killed process before kernel signal delivery completed; the
+unchanged stopped-state expectation is now observed within a bounded500 ms window.
+Real timeout and SIGINT cases both retain forced-termination evidence; cleanup failure
+still makes qualification fail. Exact red/green commands:
+
+```sh
+/tmp/scribeswell-host-tests-312/bin/python -m pytest apps/scribeswell/tests/test_studies_owner_integration.py -q -k timed_out
+/tmp/scribeswell-host-tests-312/bin/python -m pytest apps/scribeswell/tests/test_studies_owner_integration.py -q
+```
+
+Initial focused process result: one failure (live descendant). Final focused result:
+**11 passed**, including real timeout/SIGINT, safe signed-callback failure diagnostics,
+collision/ownership refusal, failed preparation, exact-stop failure and exited launcher
+cleanup. Doubles establish orchestration only; native proof above supplies actual SQL,
+provider and HTTP evidence. No skipped case is counted as proof.
+
+## Retained regression checks and limits
+
+```sh
+/tmp/scribeswell-host-tests-312/bin/python -m pytest apps/scribeswell/tests/test_studies_owner_integration.py apps/scribeswell/tests/test_personal_notes_contract.py apps/scribeswell/tests/test_personal_notes_api.py apps/scribeswell/tests/test_personal_notes_release.py -q
+/tmp/scribeswell-host-tests-312/bin/python -m pytest services/access/tests/test_studies_identity.py services/access/tests/test_studies_access.py services/access/tests/test_studies_readiness.py -q
+node node_modules/@playwright/test/cli.js test --config apps/scribeswell/web/playwright.session.config.cjs
+```
+
+The app command passed142 tests before the two real-process cases were added;
+subsequent final focused execution passed all11 cases. Owner characterization passed56;
+retained session checks passed12. Existing Starlette TestClient deprecation remains.
+The session configuration now selects exactly `session.integration.cjs`, preserving its
+suite while preventing accidental collection of the separately configured owner test.
+
+```sh
+node node_modules/@playwright/test/cli.js test --config apps/scribeswell/web/playwright.config.cjs --grep-invert 'native PostgreSQL browser reload'
+node node_modules/@playwright/test/cli.js test --config apps/scribeswell/web/playwright.config.cjs --project desktop --workers 1 --grep 'late chapter responses cannot replace the chosen chapter|callback recovery scrubs secrets and preserves prior session: incomplete'
+node node_modules/@playwright/test/cli.js test --config apps/scribeswell/web/playwright.config.cjs --project mobile --workers 1 --grep 'occurrence pages survive tabs, filter resets, errors retry and new words clear old results'
+```
+
+Broad desktop/mobile result: **203 passed / 3 failed** under six workers. Those exact
+unchanged failing desktop cases passed2/2 at one worker; the exact unchanged mobile
+occurrence case passed1/1 at one worker. No expected result/product source was changed.
+The original broad invocation remains failed; the cause of its three failures has not been established.
+The existing opt-in synthetic-owner native browser case was explicitly filtered out;
+it is not counted as integrated evidence. No regression browser run overlapped the
+successful final native qualification.
+
+`npm run build` in `apps/scribeswell/web` passed with the existing553.75 kB chunk
+warning. Python compilation and `node --check` on new CJS files passed. These checks
+also passed and wrote no generated/composed changes:
+
+```sh
+/tmp/scribeswell-host-tests-312/bin/python apps/scribeswell/tools/py/export_personal_notes_contract.py --check
+node --experimental-strip-types apps/scribeswell/tools/sync_personal_notes_database.mjs --check
+python3 tools/py/run_compose_supabase.py --check-only
+```
+
+Scaffold: reuse existing wrapper/migration/role helpers; no generic lifecycle or
+provisioner. Shared UI: unchanged. Agent context: unchanged. Documentation: this evidence
+and the consuming contract distinguish actual local proof from remaining gates. ADRs:
+unchanged. Canonical reconciliation/review is owned by the parent BMAD workflow. There
+is no root repository-wide verification claim.
`. Read that file — it is the content under review.

Do not invoke any skill, and do not spawn subagents of your own — you are the reviewer. If the instruction file is unreadable, report that exact failure and stop. Return your findings as text in your final message; do not route them through any findings-reporting tool the host may offer.
