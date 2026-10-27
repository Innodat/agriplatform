"""Explicit server-only caller credentials and exact endpoint/capability policy."""
import secrets
from dataclasses import dataclass

POLICIES={
 'leave':{'leave.request.own.read':'organization','leave.request.own.manage':'organization'},
 'pts':{'pts.poetry.read':'account','pts.poetry.export':'account','pts.poetry.documents':'account'},
 'reference':{'reference.record.read':'organization','reference.record.create':'organization','reference.account.read':'account'},
 'people':{},
 'directory':{},
}
KEY_NAMES={name:name.upper()+'_SERVICE_KEY' for name in POLICIES}
ALL_KEYS=tuple(KEY_NAMES.values())+('KDG_SERVICE_KEY','SCRIBESWELL_SERVICE_KEY','CONTENT_SERVICE_KEY')

@dataclass(frozen=True)
class Caller:
    name: str
    key: str
    permissions: tuple

class CallerPolicy:
    def __init__(self,environment):
        seen=set();self.callers=[]
        for field in ALL_KEYS:
            key=environment.get(field,'')
            if not key:continue
            if not isinstance(key,str) or any(not 33<=ord(c)<=126 for c in key) or key in seen:
                raise RuntimeError('kdg_check_configuration_invalid' if field=='KDG_SERVICE_KEY' else 'capability_configuration_invalid')
            seen.add(key)
        for name,field in KEY_NAMES.items():
            if environment.get(field):
                self.callers.append(Caller(name,environment[field],tuple(POLICIES[name].items())))
    def caller(self,key):
        if not key:return None
        for caller in self.callers:
            if secrets.compare_digest(caller.key.encode(),key.encode('utf-8')):return caller
        return None
    def scope(self,caller,permission):return dict(caller.permissions).get(permission)
