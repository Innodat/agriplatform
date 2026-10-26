"""Component-only fixture harness: no public DB lifecycle, unchanged HTTP assertions."""
import os
import sys
os.environ.update(SCRIBESWELL_DATABASE_URL='postgresql://scribeswell_runtime:fixture@127.0.0.1:1/fixture',SUPABASE_URL='http://127.0.0.1:1',SUPABASE_SECRET_KEY='',SUPABASE_SERVICE_ROLE_KEY='',SCRIBESWELL_STUDIES_ENABLED='false',SCRIBESWELL_STUDIES_DATABASE_URL='',SCRIBESWELL_STUDIES_ACCESS_URL='',SCRIBESWELL_STUDIES_SERVICE_KEY='')
import pytest
class Hermetic:
 @pytest.fixture(autouse=True)
 def no_database_lifecycle(self,monkeypatch):
  import main
  monkeypatch.setattr(main,'open_database',lambda:None)
  monkeypatch.setattr(main,'close_database',lambda:None)
raise SystemExit(pytest.main(['-q','apps/scribeswell/tests/test_reader_integrity.py'],plugins=[Hermetic()]))
