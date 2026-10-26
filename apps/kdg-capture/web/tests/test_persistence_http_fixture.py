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

if __name__=='__main__':unittest.main()
