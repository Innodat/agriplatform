import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from target_contract import database_url


@pytest.mark.parametrize('timeout', ['0', '11', '-1', 'abc', '1.5', '', '2&connect_timeout=3'])
def test_invalid_connect_timeout_rejected(timeout):
    with pytest.raises(ValueError, match='connect_timeout'):
        database_url('postgresql://scribeswell_runtime:fixture@db.stage.supabase.co/postgres?sslmode=require&connect_timeout=' + timeout, 'https://stage.supabase.co', 'scribeswell_runtime')


@pytest.mark.parametrize('timeout', ['1', '5', '10'])
def test_finite_connect_timeout_accepted(timeout):
    url = 'postgresql://scribeswell_runtime:fixture@db.stage.supabase.co/postgres?sslmode=require&connect_timeout=' + timeout
    assert database_url(url, 'https://stage.supabase.co', 'scribeswell_runtime') == url
