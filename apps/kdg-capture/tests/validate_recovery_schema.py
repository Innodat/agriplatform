"""Local test-tool adapter; no application dependency or package installation.

Run with existing /usr/bin/python3 + jsonschema4.10.3; owner API stays on its
approved Python3.15 environment. Input contains synthetic contract fixtures only.
"""
from importlib.metadata import version
import json
import sys
from jsonschema import Draft202012Validator, RefResolver


def main():
    if version('jsonschema')!='4.10.3':
        print('recovery_schema_tool_unqualified',file=sys.stderr)
        return 2
    data=json.load(sys.stdin)
    validator=Draft202012Validator(data['schema'],resolver=RefResolver.from_schema(data['document']))
    print(json.dumps({'valid':validator.is_valid(data['value'])}))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
