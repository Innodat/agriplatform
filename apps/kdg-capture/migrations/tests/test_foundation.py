"""Offline candidate contract tests; not PostgreSQL/ACL/native isolation evidence."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import runpy,importlib.util,os
ROOT=Path(__file__).resolve().parents[4]
MIGRATIONS=ROOT/'apps/kdg-capture/migrations'
sys.path.insert(0,str(MIGRATIONS))
import policy

class CandidateTests(unittest.TestCase):
    def values(self):return dict(KDG_MIGRATION_TARGET_ID='kdg-local',KDG_MIGRATION_ENVIRONMENT_KIND='local_disposable',KDG_MIGRATION_DATABASE_URL='postgresql+psycopg://kdg_capture_migrator:SYNTHETIC@127.0.0.1:55482/kdg_schema_'+'1'*32)
    def test_explicit_known_disposable_policy_is_validated_without_io(self):
        with patch('sqlalchemy.create_engine',side_effect=AssertionError('network')):
            value=policy.connection_url(self.values())
        self.assertEqual(value.username,policy.POLICY.migrator);self.assertEqual(value.host,'127.0.0.1')
    def test_missing_configuration_has_safe_failure(self):
        for key in self.values():
            values=self.values();values.pop(key)
            with self.assertRaisesRegex(policy.MigrationError,'^kdg_migration_configuration_invalid$'):policy.connection_url(values)
    def test_wrong_targets_privileged_urls_or_queries_are_refused(self):
        urls=['postgresql+psycopg://admin:PRIVATE@127.0.0.1:55482/kdg_schema_'+'1'*32,
              self.values()['KDG_MIGRATION_DATABASE_URL'].replace(':55482',':54322'),
              self.values()['KDG_MIGRATION_DATABASE_URL'].replace('127.0.0.1','remote.invalid'),
              self.values()['KDG_MIGRATION_DATABASE_URL']+'?options=PRIVATE',
              self.values()['KDG_MIGRATION_DATABASE_URL'].replace('kdg_schema_'+'1'*32,'postgres')]
        for url in urls:
            values=self.values();values['KDG_MIGRATION_DATABASE_URL']=url
            with self.assertRaisesRegex(policy.MigrationError,'configuration_invalid') as error:policy.connection_url(values)
            self.assertNotIn('PRIVATE',str(error.exception))
    def test_only_online_upgrade_head_is_allowed(self):
        policy.guard_command('upgrade','head')
        for command,target in [('stamp','head'),('downgrade','base'),('upgrade','0001_kdg_foundation'),('current',None)]:
            with self.assertRaisesRegex(policy.MigrationError,'upgrade_head_only'):policy.guard_command(command,target)
        with self.assertRaisesRegex(policy.MigrationError,'upgrade_head_only'):policy.guard_command('upgrade','head',offline=True)
    def test_alembic_history_is_single_owner_and_revision(self):
        from alembic.config import Config
        from alembic.script import ScriptDirectory
        scripts=ScriptDirectory.from_config(Config(str(ROOT/'apps/kdg-capture/alembic.ini')))
        self.assertEqual(scripts.get_heads(),[policy.POLICY.revision]);self.assertEqual([r.revision for r in scripts.walk_revisions()],[policy.POLICY.revision])
        migration=scripts.get_revision(policy.POLICY.revision).module
        with self.assertRaisesRegex(RuntimeError,'downgrade_prohibited'):migration.downgrade()

class WiringTests(unittest.TestCase):
    def engine(self):
        spec=importlib.util.spec_from_file_location('emitted_schema_tests',ROOT/'apps/kdg-capture/database-tools/test_owned_migration.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        engine=module.Engine();c=engine.connection
        def change(value):
            if isinstance(value,str):return value.replace('sample',policy.POLICY.schema)
            if isinstance(value,list):return [change(v) for v in value]
            if isinstance(value,dict):return {k:change(v) for k,v in value.items()}
            return value
        for key,value in vars(c).copy().items():setattr(c,key,change(value))
        c.history=[{'version_num':policy.POLICY.revision}]
        engine.disposed=False
        engine.dispose=lambda:setattr(engine,'disposed',True)
        return engine
    def run_env(self,engine,method='upgrade',broken=False):
        def upgrade():pass
        def stamp():pass
        captured={};effects=[]
        def configure(**values):captured.update(values)
        def migrate():
            effects.append('migration');engine.connection.tables=[dict(name='alembic_version',kind='r',owner=policy.POLICY.migrator)]
            if broken:engine.connection.history=[{'version_num':'unknown'}]
        fake=SimpleNamespace(config=SimpleNamespace(cmd_opts=SimpleNamespace(cmd=(upgrade,))),is_offline_mode=lambda:False,configure=configure,
            get_context=lambda:SimpleNamespace(opts=dict(fn=upgrade if method=='upgrade' else stamp,destination_rev='head')),run_migrations=migrate)
        with patch('alembic.context',fake),patch('sqlalchemy.create_engine',return_value=engine),patch.dict(os.environ,CandidateTests().values(),clear=True):
            runpy.run_path(str(MIGRATIONS/'env.py'))
        return captured,effects
    def test_actual_env_configures_local_history_and_commits_after_postcondition(self):
        engine=self.engine();config,effects=self.run_env(engine)
        self.assertEqual(effects,['migration']);self.assertEqual(config['version_table_schema'],'kdg_capture');self.assertTrue(config['transactional_ddl'])
        self.assertTrue(config['include_name']('kdg_capture','schema',{}));self.assertFalse(config['include_name']('another_owner','schema',{}))
        self.assertTrue(engine.committed);self.assertTrue(engine.disposed)
    def test_actual_env_wrong_direction_rolls_back_before_migration(self):
        engine=self.engine()
        with self.assertRaisesRegex(policy.MigrationError,'upgrade_head_only'):self.run_env(engine,method='stamp')
        self.assertTrue(engine.rolled_back);self.assertFalse(engine.committed);self.assertEqual(engine.connection.tables,[]);self.assertTrue(engine.disposed)
    def test_actual_env_bad_postcondition_rolls_back_and_disposes(self):
        engine=self.engine()
        with self.assertRaisesRegex(policy.MigrationError,'history_invalid'):self.run_env(engine,broken=True)
        self.assertTrue(engine.rolled_back);self.assertFalse(engine.committed);self.assertTrue(engine.disposed)

if __name__=='__main__':unittest.main()
