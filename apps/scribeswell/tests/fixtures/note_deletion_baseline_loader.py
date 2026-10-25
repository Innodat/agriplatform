"""Load byte-frozen baseline SQL/DTO with an isolated old-format binding."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def load():
 root=Path(__file__).with_name('note_deletion_baseline')
 manifest=json.loads((root/'manifest.json').read_text())
 for name,entry in manifest['files'].items():
  assert hashlib.sha256((root/name).read_bytes()).hexdigest()==entry['sha256']
 def module(name,path):
  spec=importlib.util.spec_from_file_location(name,path)
  result=importlib.util.module_from_spec(spec);sys.modules[name]=result;spec.loader.exec_module(result);return result
 contract=module('note_deletion_baseline_contract',root/'personal_notes_contract.py')
 previous=sys.modules.get('personal_notes_contract')
 try:
  sys.modules['personal_notes_contract']=contract
  storage=module('note_deletion_baseline_storage',root/'personal_notes_storage.py')
 finally:
  if previous is None:sys.modules.pop('personal_notes_contract',None)
  else:sys.modules['personal_notes_contract']=previous
 assert storage.NoteView is contract.NoteView
 return contract,storage
