"""Access18 preserves the trusted17 reference's entire historical source chain."""
import sys
from pathlib import Path
from hashlib import sha256
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'migrations'))
import access_capability_catalog as catalog


def test_all_recorded_historical_migration_sources_are_checked(tmp_path,monkeypatch):
    directory=tmp_path/'versions';directory.mkdir()
    sources={}
    for number in range(1,17):
        name=f'{number:04d}_historical.py';raw=f'unchanged historical source {number}'.encode()
        (directory/name).write_bytes(raw);sources[name]=sha256(raw).hexdigest()
    monkeypatch.setattr(catalog,'HERE',tmp_path)
    catalog.verify_predecessor_sources({'predecessor_sources':sources})
    for name in sources:
        path=directory/name;original=path.read_bytes();path.write_bytes(original+b'changed')
        with pytest.raises(catalog.BaselineError,match='capability_predecessor_unavailable'):catalog.verify_predecessor_sources({'predecessor_sources':sources})
        path.write_bytes(original)

@pytest.mark.parametrize('sources',[None,{}, {'../outside.py':'hash'}, {'0001_missing.py':'hash'}])
def test_missing_or_unsafe_source_chain_fails_closed(tmp_path,monkeypatch,sources):
    monkeypatch.setattr(catalog,'HERE',tmp_path)
    with pytest.raises(catalog.BaselineError,match='capability_predecessor_unavailable'):catalog.verify_predecessor_sources({'predecessor_sources':sources})
