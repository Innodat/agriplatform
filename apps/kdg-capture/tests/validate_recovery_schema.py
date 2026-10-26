"""Local test-tool adapter; no application dependency or package installation.

Run with existing /usr/bin/python3 + jsonschema4.10.3; owner API stays on its
approved Python3.15 environment. Input contains synthetic contract fixtures only.
"""
from importlib.metadata import version
import json
from datetime import datetime
import sys
from jsonschema import Draft202012Validator, RefResolver, FormatChecker


def main():
    if version('jsonschema')!='4.10.3':
        print('recovery_schema_tool_unqualified',file=sys.stderr)
        return 2
    data=json.load(sys.stdin)
    checker=FormatChecker()
    if 'date-time' not in checker.checkers:
        # The retained jsonschema tool has no optional RFC3339 package. Use the
        # standard-library calendar parser via FormatChecker; owner patterns
        # constrain UTC syntax. No calendar rules are implemented here.
        @checker.checks('date-time',raises=ValueError)
        def date_time(value):
            if not isinstance(value,str):return True
            parsed=datetime.fromisoformat(value.upper())
            return 'T' in value.upper() and parsed.utcoffset() is not None
    validator=Draft202012Validator(data['schema'],resolver=RefResolver.from_schema(data['document']),format_checker=checker)
    print(json.dumps({'valid':validator.is_valid(data['value'])}))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
