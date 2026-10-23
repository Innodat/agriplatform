# GENERATED neutral control-flow tests; synthetic connections are not native SQL proof.
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError

spec=importlib.util.spec_from_file_location('generated_transaction_context',Path(__file__).with_name('transaction_context.py'))
context=importlib.util.module_from_spec(spec);sys.modules[spec.name]=context;spec.loader.exec_module(context)
ORG='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
ACCOUNT='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'
ACTOR='cccccccc-cccc-4ccc-8ccc-cccccccccccc'

class Connection:
    """Records adapter calls only; does not simulate RLS, rollback or pool cleanup."""
    def __init__(self):
        self.calls=[];self.active=False;self.autocommit=False;self.isolation='READ COMMITTED'
        self.options={};self.fail_execute=False;self.fail_commit=False;self.on_commit=lambda:None
        self.connection=SimpleNamespace(driver_connection=self)
    def in_transaction(self):return self.active
    def get_execution_options(self):return self.options
    def get_isolation_level(self):return self.isolation
    def execute(self,sql,parameters):
        if self.fail_execute:raise SQLAlchemyError('secret input and credentials')
        self.calls.append((str(sql),parameters));return 'synthetic_result'
    @contextmanager
    def begin(self):
        self.calls.append(('BEGIN',{}));self.active=True
        try:
            yield self
            if self.fail_commit:raise SQLAlchemyError('secret commit details')
            self.calls.append(('COMMIT',{}));self.on_commit()
        except BaseException:
            self.calls.append(('EXIT_WITH_ERROR',{}));raise
        finally:self.active=False

class BoundedContext(unittest.TestCase):
    def setUp(self):
        self.now=100.0;self.clock=patch.object(context.time,'monotonic',side_effect=lambda:self.now);self.clock.start()
        self.addCleanup(self.clock.stop)
    def verified(self,**changes):
        values=dict(org_id=ORG,account_id=ACCOUNT,actor_id=ACTOR,mode='own_write',observed_at=self.now);values.update(changes)
        return context.VerifiedContext(**values)
    def test_binds_exact_transaction_local_verified_values(self):
        db=Connection();budget=context.Budget()
        with context.transaction(db,budget,self.verified()):
            self.assertEqual(context.execute(db,budget,'SELECT :value',{'value':7}),'synthetic_result')
        scope=[(sql,args) for sql,args in db.calls if "set_config('app.org_id'" in sql]
        self.assertEqual(len(scope),1)
        sql,args=scope[0]
        self.assertEqual({k:args[k] for k in ('org','account','actor','mode')},dict(org=ORG,account=ACCOUNT,actor=ACTOR,mode='own_write'))
        self.assertEqual(sql.count(', true)'),5)
        self.assertEqual(db.calls[-1][0],'COMMIT')
    def test_context_is_strict_and_redacted(self):
        for field,value in [('org_id',ORG.upper()),('account_id','00000000-0000-0000-0000-000000000000'),('actor_id',b'actor'),('mode','admin'),('observed_at',True),('observed_at',float('nan'))]:
            with self.subTest(field=field),self.assertRaisesRegex(context.WriteError,'^invalid_write_context$'):self.verified(**{field:value})
        self.assertEqual(repr(self.verified()),'<VerifiedContext redacted>')
    def test_invalid_connection_modes_refuse_before_begin(self):
        for field,value in [('active',True),('autocommit',True),('isolation','REPEATABLE READ'),('options',{'isolation_level':'AUTOCOMMIT'})]:
            db=Connection();setattr(db,field,value)
            with self.subTest(field=field),self.assertRaises(context.WriteError):
                with context.transaction(db,context.Budget(),self.verified()):self.fail('yielded')
            self.assertEqual(db.calls,[])
        with self.assertRaises(context.WriteError):
            with context.transaction(Connection(),context.Budget(),object()):self.fail('yielded')
    def test_stale_future_and_pre_execution_observation_refuse(self):
        budget=context.Budget();self.now=100.5
        for observed in (99.9,99.0,101.0):
            db=Connection()
            with self.subTest(observed=observed),self.assertRaisesRegex(context.WriteError,'authorization_observation_expired'):
                with context.transaction(db,budget,self.verified(observed_at=observed)):self.fail('yielded')
            self.assertEqual(db.calls,[])
    def test_in_budget_observation_older_than_one_second_refuses(self):
        budget=context.Budget();observed=self.now;self.now+=1.01
        with self.assertRaisesRegex(context.WriteError,'authorization_observation_expired'):
            with context.transaction(Connection(),budget,self.verified(observed_at=observed)):self.fail('yielded')
    def test_all_limits_are_positive_and_capped_by_original_remaining_budget(self):
        budget=context.Budget();self.now=109.8;db=Connection()
        with context.transaction(db,budget,self.verified()):context.execute(db,budget,'SELECT 1')
        for _,args in db.calls:
            for key in ('statement','lock','total'):
                if key in args:self.assertTrue(0<int(args[key])<=200)
        self.now=110
        with self.assertRaisesRegex(context.WriteError,'execution_timeout'):budget.remaining()
    def test_default_statement_lock_and_total_caps(self):
        db=Connection()
        with context.transaction(db,context.Budget(),self.verified()):pass
        self.assertEqual(db.calls[1][1],{'statement':'5000','lock':'2000'})
        self.assertEqual(db.calls[2][1]['total'],'10000')
    def test_sub_millisecond_and_expired_budget_do_not_disable_limits(self):
        for now in (109.9999,110.0):
            self.now=100;budget=context.Budget();self.now=now;db=Connection()
            with self.subTest(now=now),self.assertRaisesRegex(context.WriteError,'execution_timeout'):
                with context.transaction(db,budget,self.verified()):self.fail('yielded')
            self.assertFalse(any('set_config' in sql for sql,_ in db.calls))
    def test_sql_and_commit_failures_have_safe_identifiers(self):
        for failure in ('fail_execute','fail_commit'):
            db=Connection();setattr(db,failure,True)
            with self.subTest(failure=failure),self.assertRaises(context.WriteError) as failed:
                with context.transaction(db,context.Budget(),self.verified()):pass
            self.assertEqual(str(failed.exception),'internal_error')
            self.assertTrue(failed.exception.__suppress_context__)
            self.assertFalse(db.active)
    def test_owner_exception_exits_without_success(self):
        db=Connection()
        with self.assertRaisesRegex(ValueError,'owner_failure'):
            with context.transaction(db,context.Budget(),self.verified()):raise ValueError('owner_failure')
        self.assertNotIn('COMMIT',[sql for sql,_ in db.calls])
    def test_owner_sql_failure_maps_safely_without_commit(self):
        class FailingOwnerSql(Connection):
            def execute(self,sql,parameters):
                if str(sql)=='SELECT private_owner_value':raise SQLAlchemyError('secret owner SQL details')
                return super().execute(sql,parameters)
        db=FailingOwnerSql();budget=context.Budget()
        with self.assertRaisesRegex(context.WriteError,'^internal_error$') as failed:
            with context.transaction(db,budget,self.verified()):
                context.execute(db,budget,'SELECT private_owner_value')
        self.assertTrue(failed.exception.__suppress_context__)
        self.assertNotIn('COMMIT',[sql for sql,_ in db.calls])
    def test_subsequent_statements_shrink_limits_without_resetting_budget(self):
        db=Connection();budget=context.Budget()
        with context.transaction(db,budget,self.verified()):
            context.execute(db,budget,'SELECT first')
            self.now=109.5
            context.execute(db,budget,'SELECT second')
        first=next(i for i,(sql,_) in enumerate(db.calls) if sql=='SELECT first')
        second=next(i for i,(sql,_) in enumerate(db.calls) if sql=='SELECT second')
        self.assertEqual(db.calls[first-1][1],{'statement':'5000','lock':'2000'})
        self.assertEqual(db.calls[second-1][1],{'statement':'500','lock':'500'})
    def test_late_owner_sql_acknowledgement_never_commits(self):
        owner=self
        class LateSql(Connection):
            def execute(self,sql,parameters):
                result=super().execute(sql,parameters)
                if str(sql)=='SELECT slow_owner_work':owner.now=111
                return result
        db=LateSql();budget=context.Budget()
        with self.assertRaisesRegex(context.WriteError,'execution_timeout'):
            with context.transaction(db,budget,self.verified()):
                context.execute(db,budget,'SELECT slow_owner_work')
        self.assertNotIn('COMMIT',[sql for sql,_ in db.calls])
    def test_late_commit_acknowledgement_is_uncertain_not_rollback(self):
        db=Connection();db.on_commit=lambda:setattr(self,'now',111)
        with self.assertRaisesRegex(context.WriteError,'execution_timeout'):
            with context.transaction(db,context.Budget(),self.verified()):pass
        self.assertEqual(db.calls[-1][0],'COMMIT')

if __name__=='__main__':unittest.main()
