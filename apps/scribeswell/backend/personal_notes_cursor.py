"""Owner/parent bound keyset positions, never an authorization credential."""
import base64
import json
import re
from pydantic import TypeAdapter
from personal_notes_contract import Identifier,UtcTimestamp,_unique_object
from personal_notes_access import NotesError

def encode(resource,account_id,study_id,created_at,identifier):
    return base64.urlsafe_b64encode(json.dumps(['scribeswell.list.v1',resource,account_id,study_id,created_at,identifier],separators=(',',':')).encode()).decode().rstrip('=')

def decode(cursor,resource,account_id,study_id):
    try:
        if not isinstance(cursor,str) or not 1<=len(cursor)<=512 or not re.fullmatch('[A-Za-z0-9_-]+',cursor): raise ValueError
        raw=base64.b64decode(cursor+'='*((-len(cursor))%4),altchars=b'-_',validate=True)
        value=json.loads(raw.decode('utf8'),object_pairs_hook=_unique_object)
        if not isinstance(value,list) or len(value)!=6 or value[:4]!=['scribeswell.list.v1',resource,account_id,study_id]: raise ValueError
        TypeAdapter(UtcTimestamp).validate_python(value[4]); TypeAdapter(Identifier).validate_python(value[5])
        if encode(resource,account_id,study_id,value[4],value[5])!=cursor: raise ValueError
        return value[4:]
    except Exception: raise NotesError('scribeswell_personal_notes_input_invalid') from None
