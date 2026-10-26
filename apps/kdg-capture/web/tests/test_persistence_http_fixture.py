"""Focused synthetic fixture guards; no native database or process cleanup."""
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('persistence_fixture',Path(__file__).with_name('persistence-http-fixture.py'))
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)

class FixtureGuards(unittest.TestCase):
    def test_unknown_sql_refuses(self):
        connection=fixture.Connection(fixture.Store())
        with connection.begin(),self.assertRaisesRegex(AssertionError,'unmodeled_synthetic_sql'):
            connection.execute('SELECT invented_synthetic_success',{})
    def test_lookup_scope_is_explicit(self):
        connection=fixture.Connection(fixture.Store())
        valid=dict(org=fixture.ORG,account=fixture.ACCOUNT,child=fixture.CHILD,version=fixture.VERSION,ref='synthetic')
        with connection.begin():
            for sql in (fixture.create.CHILD,fixture.create.ELIGIBILITY,fixture.create.ASSIGNMENT,fixture.create.VERSION):
                self.assertIsNotNone(connection.execute(sql,valid).value)
                self.assertIsNone(connection.execute(sql,dict(valid,org=fixture.UNKNOWN)).value)
            for sql in (fixture.create.ELIGIBILITY,fixture.create.ASSIGNMENT):
                self.assertIsNone(connection.execute(sql,dict(valid,account=fixture.UNKNOWN)).value)
                self.assertIsNone(connection.execute(sql,dict(valid,child=fixture.UNKNOWN)).value)

    def test_read_models_original_provenance_and_scope_without_answer_aliasing(self):
        from datetime import date
        store=fixture.Store();connection=fixture.Connection(store)
        parameters=dict(org=fixture.ORG,account=fixture.ACCOUNT,actor=fixture.ACTOR,child=fixture.CHILD,
            version=fixture.VERSION,questionnaire=fixture.QUESTIONNAIRE,capture=fixture.CAPTURE,
            date=date(2026,10,26),answers='{}',device='2026-10-26t10:00:00.123456789z')
        with connection.begin():
            connection.execute(fixture.create.CAPTURE_INSERT,parameters)
            original=connection.execute(fixture.read.DETAIL,parameters).value
            connection.execute(fixture.edit.UPDATE,dict(parameters,date=date(2026,10,27),revision=2))
            detail=connection.execute(fixture.read.DETAIL,parameters).value
            self.assertEqual((detail['revision'],detail['observation_date']),(2,date(2026,10,27)))
            for key in ('captured_at','created_at','created_by','owner_actor_id','definition'):
                self.assertEqual(detail[key],original[key])
            self.assertEqual(detail['captured_at'],parameters['device'])
            detail['answers']['mutated']={'value':False}
            self.assertEqual(connection.execute(fixture.read.DETAIL,parameters).value['answers'],{})
            for scope in ('org','account','capture'):
                self.assertIsNone(connection.execute(fixture.read.DETAIL,dict(parameters,**{scope:fixture.UNKNOWN})).value)

if __name__=='__main__':unittest.main()
