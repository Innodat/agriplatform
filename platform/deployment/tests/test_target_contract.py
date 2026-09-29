import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from target_contract import database_url


class DatabaseTimeoutContract(unittest.TestCase):
    def test_invalid_connect_timeout_rejected(self):
        for timeout in ['0', '11', '-1', 'abc', '1.5', '', '2&connect_timeout=3']:
            with self.subTest(timeout=timeout):
                with self.assertRaisesRegex(ValueError, 'connect_timeout'):
                    database_url('postgresql://scribeswell_runtime:fixture@db.stage.supabase.co/postgres?sslmode=require&connect_timeout=' + timeout, 'https://stage.supabase.co', 'scribeswell_runtime')

    def test_finite_connect_timeout_accepted(self):
        for timeout in ['1', '5', '10']:
            with self.subTest(timeout=timeout):
                url = 'postgresql://scribeswell_runtime:fixture@db.stage.supabase.co/postgres?sslmode=require&connect_timeout=' + timeout
                self.assertEqual(database_url(url, 'https://stage.supabase.co', 'scribeswell_runtime'), url)
