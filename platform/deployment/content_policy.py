"""One fixed Content policy file for the frozen API UID; no general secret engine."""
import json
import os
from pathlib import Path
import re
import stat
from uuid import UUID
TARGET='/run/secrets/content-service-policy.json'


def environment(env_dir):
    values={}
    for line in (env_dir/'content.env').read_text().splitlines():
        key,separator,value=line.partition('=')
        if separator and key=='CONTENT_SERVICE_POLICY_FILE':
            if key in values:raise ValueError('content_policy_invalid')
            values[key]=value
    return values


def validate_policy(env_dir,values):
    """Read the exact descriptor, reject links and validate before any DB changes.

    Release runs with host authority sufficient to read UID65532's private file.
    The API performs its own current UID/schema verification when loading the mount.
    """
    path=Path(env_dir)/'content-service-policy.json'
    if values.get('CONTENT_SERVICE_POLICY_FILE')!=TARGET:raise ValueError('content_policy_mount_invalid')
    try:
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK)
        with os.fdopen(fd,'rb') as source:
            info=os.fstat(source.fileno())
            if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode)!=0o600 or info.st_uid!=65532:
                raise ValueError('content_policy_private_uid65532_required')
            raw=source.read(1024*1024+1)
            if len(raw)>1024*1024:raise ValueError('content_policy_invalid')
        def closed(pairs):
            result={}
            for key,value in pairs:
                if key in result:raise ValueError('content_policy_invalid')
                result[key]=value
            return result
        doc=json.loads(raw.decode('utf-8'),object_pairs_hook=closed)
        if not isinstance(doc,dict) or set(doc)!={'version','services'} or type(doc['version']) is not int or doc['version']!=1 or not isinstance(doc['services'],list):raise ValueError('content_policy_invalid')
        keys=set()
        for item in doc['services']:
            if not isinstance(item,dict) or set(item)!={'key','application_id','executor_actor_id','operations','scope_kinds'}:raise ValueError('content_policy_invalid')
            if not isinstance(item['key'],str) or not item['key'] or not item['key'].isascii() or item['key'] in keys:raise ValueError('content_policy_invalid')
            keys.add(item['key'])
            if not isinstance(item['application_id'],str) or re.fullmatch('[a-z][a-z0-9-]{0,62}',item['application_id']) is None:raise ValueError('content_policy_invalid')
            UUID(item['executor_actor_id'])
            for field,allowed in [('operations',{'create','finalize','metadata','read'}),('scope_kinds',{'application','organization','account'})]:
                if not isinstance(item[field],list) or not item[field] or any(not isinstance(value,str) or value not in allowed for value in item[field]):raise ValueError('content_policy_invalid')
    except Exception:raise ValueError('content_policy_validation_failed') from None
    return {'type':'bind','source':str(path),'target':TARGET,'read_only':True,'bind':{'create_host_path':False}}
