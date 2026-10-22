"""Additive compact receipt candidate; no command fingerprint or secret execution.

Uses historical transaction/lock primitives without invoking fingerprint functions.
The owner supplies command parsing, current authority and explicit domain SQL.
"""
import json
import math
from uuid import UUID
from atomic_write import (Budget, OutcomeKey, VerifiedContext, WriteError, execute,
                          outcome_lock, outcome_lock_key, transaction)


def receipt(result, *, command_type, command_version, result_version, target):
    """Validate the neutral sample acknowledgement, preserving original versions."""
    if (command_type not in ('record.create','record.edit')
            or type(command_version) is not int or command_version not in (1,2)
            or type(result_version) is not int or result_version != 1
            or type(result) is not dict or set(result) != {'record_id','revision'}):
        raise WriteError('operation_verification_unavailable')
    identity=result['record_id'];revision=result['revision']
    try:
        valid=(type(identity) is str and UUID(identity).int and str(UUID(identity))==identity
               and identity==target and type(revision) is str and revision.isascii()
               and revision.isdigit() and not revision.startswith('0')
               and len(revision)<=19 and int(revision)<=9223372036854775807)
    except (ValueError,TypeError,AttributeError):
        valid=False
    if not valid:
        raise WriteError('operation_verification_unavailable')
    return dict(command_type=command_type,command_version=command_version,
                result_version=result_version,result=dict(result))


def parse_json(data):
    """Strict bounded wire parsing; errors never include input or parser details."""
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise ValueError()
            result[key]=value
        return result
    def invalid(_):raise ValueError()
    try:
        if type(data) is not bytes or len(data)>8192:raise ValueError()
        result=json.loads(data.decode('utf-8'),object_pairs_hook=pairs,parse_constant=invalid)
        # Reject NUL and lone surrogates anywhere, including object keys.
        def strings(value):
            if type(value) is str:
                value.encode('utf-8')
                if '\0' in value:raise ValueError()
            elif type(value) is float and not math.isfinite(value):
                raise ValueError()
            elif type(value) is dict:
                for key,item in value.items():strings(key);strings(item)
            elif type(value) is list:
                for item in value:strings(item)
        strings(result)
        return result
    except (ValueError,UnicodeError,RecursionError):
        raise WriteError('invalid_command') from None
