"""Optional deterministic offline lock-v1 comparison; no database or application startup.

Use the approved WRITE test Python with its existing rfc8785 oracle dependency.
The emitted runtime does not import that dependency. This is not a general JCS proof.
"""
import importlib.util
from pathlib import Path
import sys
import json
from hashlib import sha256
from uuid import UUID
import rfc8785

source=Path(__file__).resolve().parents[1]/'templates/application/write-tools/transaction_context.py'
spec=importlib.util.spec_from_file_location('lock_compatibility_context',source)
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
for index in range(100):
    key=module.OutcomeKey('s'+'x'*(index%63),str(UUID(int=index+1)),str(UUID(int=index+1000)),
        'capture.'+'a'*(index%193),str(UUID(int=index+5000)))
    value=dict(lock_version=1,owner_schema=key.owner_schema,scope_kind='organization',
        scope_id=key.org_id,caller_kind='account',caller_id=key.account_id,
        command_type=key.command_type,operation_id=key.operation_id)
    expected=rfc8785.dumps(value)
    actual=json.dumps(value,sort_keys=True,separators=(',',':')).encode('utf-8')
    if actual!=expected or module.outcome_lock_key(key)!=int.from_bytes(sha256(expected).digest()[:8],'big',signed=True):
        raise SystemExit('lock_v1_compatibility_failed')
print('100 fixed-shape ASCII JCS compatibility cases passed; no general JCS claim')
