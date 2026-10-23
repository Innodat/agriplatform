"""Pure build-time release contract. Expected custody is not Identity verification."""
import hashlib
import json
import math
import re
from uuid import UUID

PROFILE_ENV = 'SCRIBESWELL_MIGRATION_PROFILE'
CUSTODY_ENV = 'SCRIBESWELL_MIGRATION_CUSTODY_JSON'
OPTION_KEYS = {PROFILE_ENV, CUSTODY_ENV}
PROFILES = ('dormant', 'prepared-controller-v1', 'controller-history-v1')
REVISIONS = (None, 'scribeswell_0001', 'scribeswell_0002', 'scribeswell_0003')
FIELDS = {'schema_version','source_id','executor_actor_id','actor_kind','actor_key','preparation_evidence_ref'}


def invalid():
    raise ValueError('scribeswell_release_profile_invalid')


def validate_custody(value):
    if type(value) is not dict or set(value) != FIELDS:
        invalid()
    if type(value['schema_version']) is not int or value['schema_version'] != 1 or value['actor_kind'] != 'service':
        invalid()
    for name, pattern in (('source_id',r'[A-Za-z0-9][A-Za-z0-9._:-]{0,63}'),
                          ('actor_key',r'[a-z][a-z0-9_.:-]{0,127}'),
                          ('preparation_evidence_ref',r'[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}')):
        if type(value[name]) is not str or re.fullmatch(pattern,value[name],flags=re.ASCII) is None:
            invalid()
    try:
        actor = UUID(value['executor_actor_id'])
        if actor.int == 0 or str(actor) != value['executor_actor_id']:
            invalid()
    except (ValueError, TypeError, AttributeError):
        invalid()
    return dict(value)


def strict_json(raw, limit):
    if type(raw) is not str or len(raw.encode('utf-8')) > limit:
        invalid()
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                invalid()
            result[key] = value
        return result
    def finite_float(raw):
        value=float(raw)
        if not math.isfinite(value):
            invalid()
        return value
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: invalid(),parse_float=finite_float)
    except (ValueError, TypeError, RecursionError):
        invalid()


def selection(value):
    if type(value) is not dict or set(value) != {'profile', 'custody'}:
        invalid()
    profile = value['profile']
    if type(profile) is not str or profile not in PROFILES:
        invalid()
    if profile == 'dormant':
        if value['custody'] is not None:
            invalid()
        return dict(profile=profile, custody=None)
    return dict(profile=profile, custody=validate_custody(value['custody']))


def from_environ(environ):
    allowed = OPTION_KEYS | {'SCRIBESWELL_MIGRATION_DATABASE_URL'}
    if any(key.startswith('SCRIBESWELL_MIGRATION_') and key not in allowed for key in environ):
        invalid()
    profile = environ.get(PROFILE_ENV, 'dormant')
    supplied = CUSTODY_ENV in environ
    if (profile == 'dormant' and supplied) or (profile != 'dormant' and not supplied):
        invalid()
    if supplied and (type(environ[CUSTODY_ENV]) is not str or '\n' in environ[CUSTODY_ENV] or '\r' in environ[CUSTODY_ENV]):
        invalid()
    return selection(dict(profile=profile, custody=strict_json(environ[CUSTODY_ENV],4096) if supplied else None))


def evidence(value):
    value = selection(value)
    encoded = json.dumps(value['custody'],sort_keys=True,separators=(',',':')).encode('ascii')
    return dict(profile=value['profile'], custody_sha256=None if value['custody'] is None else hashlib.sha256(encoded).hexdigest())


def valid_result(result, expected):
    """A worker success must include the native post-COMMIT marker's evidence."""
    return (type(result) is dict and set(result) == {'before','after','validation'}
            and result['before'] in REVISIONS and result['after'] == 'scribeswell_0003'
            and (expected['profile'] == 'dormant' or result['before'] == 'scribeswell_0003')
            and result['validation'] == evidence(expected))


def successful_report(report, expected):
    if type(report) is not dict or set(report) != {'owners','complete'} or report['complete'] is not True:
        return False
    owners = report['owners']
    if type(owners) is not dict or set(owners) != {'scribeswell'}:
        return False
    entry = owners['scribeswell']
    return (type(entry) is dict and set(entry) == {'status','before','after','requested_validation','validation'}
            and entry['status'] == 'succeeded' and entry['requested_validation'] == evidence(expected)
            and valid_result({key:entry[key] for key in ('before','after','validation')},expected))


def safe_failure(report, expected):
    """Select safe failure observations; never copy unvalidated child payloads."""
    entry={'status':'failed','outcome_requires_reconciliation':True}
    if type(report) is dict and type(report.get('owners')) is dict:
        observed=report['owners'].get('scribeswell')
        if type(observed) is dict:
            if observed.get('status') in ('failed','unknown','not_attempted','running'):
                entry['status']=observed['status']
            if 'before' in observed and observed['before'] in REVISIONS:
                entry['before']=observed['before']
            if observed.get('requested_validation') == evidence(expected):
                entry['requested_validation']=evidence(expected)
    return {'complete':False,'code':'scribeswell_migration_failed','owners':{'scribeswell':entry}}
