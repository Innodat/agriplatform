"""Offline configured own/combined exports; no environment, engine or authority I/O."""
import json
from pathlib import Path
import sys


def schema(*,include_administrator=False):
    from main import create_app
    from own_runtime import MODULES,applications,schemas
    from admin_runtime import compose_schema
    if include_administrator:
        from export_configured_admin_openapi import schema as admin_schema
        base=admin_schema()
    else:
        base=create_app().openapi()
    owners=applications([None]*len(MODULES),[None]*len(MODULES),None,None)
    return compose_schema(base,*schemas(owners),title='KDG Capture configured API' if include_administrator else 'KDG Capture configured own API')


def main():
    if sys.argv[1:] not in ([],['--check']):
        print('configured_own_openapi_arguments_invalid',file=sys.stderr)
        return 1
    try:
        for name,include in [('configured-own.openapi.json',False),('configured.openapi.json',True)]:
            destination=Path(__file__).with_name(name)
            if destination.is_symlink():raise ValueError()
            encoded=json.dumps(schema(include_administrator=include),sort_keys=True,indent=2)+'\n'
            if sys.argv[1:]:
                if not destination.is_file() or destination.read_text(encoding='utf-8')!=encoded:
                    print('configured_own_openapi_stale',file=sys.stderr)
                    return 1
            else:
                destination.write_text(encoded,encoding='utf-8')
        print('configured_own_openapi_current' if sys.argv[1:] else 'configured_own_openapi_exported')
        return 0
    except Exception:
        print('configured_own_openapi_export_failed',file=sys.stderr)
        return 1


if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    raise SystemExit(main())
