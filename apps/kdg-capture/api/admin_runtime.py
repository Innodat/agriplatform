"""Configured composition of existing app-owned administrator read handlers.

No administrative write routes, engine checkout, migrations or ambient credentials.
Candidate closure state and router lifespans remain owned by their existing apps.
"""
from copy import deepcopy
import hmac
import importlib
from pathlib import Path
import sys

from sqlalchemy.engine import make_url

DATABASE = 'KDG_ADMIN_READ_DATABASE_URL'
IDENTITY_URL = 'KDG_IDENTITY_URL'
DISPLAY_KEY = 'KDG_ACTOR_DISPLAY_SERVICE_KEY'
SETTINGS = (DATABASE, IDENTITY_URL, DISPLAY_KEY)


def handlers():
    # These are sibling application modules, never another owner's server code.
    # Preserve ordinary API-only startup without SQL dependencies or candidate paths.
    source = str(Path(__file__).resolve().parents[1] / 'write-candidate')
    sys.path.insert(0, source)
    try:
        # Their factories import schema owners lazily. Load those app-local
        # dependencies while the explicit candidate source path is in scope too.
        importlib.import_module('admin_openapi')
        importlib.import_module('audit_display_openapi')
        return (importlib.import_module('admin_http'),
                importlib.import_module('audit_display_http'))
    finally:
        sys.path.remove(source)


def compose_schema(context, administrator, audit):
    """Merge owner-exported schemas, refusing ambiguous component identities."""
    result = deepcopy(context)
    result['info']['title'] = 'KDG Capture configured read API'
    for schema in (administrator, audit):
        for path, operation in schema['paths'].items():
            if path in result['paths']:
                raise RuntimeError('kdg_admin_schema_invalid')
            result['paths'][path] = deepcopy(operation)
        for category, definitions in schema.get('components', {}).items():
            selected = result.setdefault('components', {}).setdefault(category, {})
            for name, definition in definitions.items():
                if name in selected and selected[name] != definition:
                    raise RuntimeError('kdg_admin_schema_invalid')
                selected[name] = deepcopy(definition)
    operation = result['paths']['/api/v1/admin/captures/{capture_id}/audit-details']['get']
    operation['description'] = operation['description'].replace('; no active mount or UI.', '.')
    return result


def compose(app, configuration, *, transport=None, identity_transport=None):
    try:
        database = configuration[DATABASE]
        url = make_url(database)
        if url.username != 'kdg_capture_runtime':
            raise ValueError()
        admin, audit = handlers()
        common = dict(org_id=configuration['KDG_ORG_ID'],
                      access_url=configuration['KDG_ACCESS_URL'],
                      service_key=configuration['KDG_SERVICE_KEY'], transport=transport)
        # Validate both current-authorization policies and the dedicated Identity
        # policy before creating either lazy engine. No I/O happens in these owners.
        admin_authority = admin.recovery.AdminReadHandler(**common)
        audit_authority = audit.audit.AuditReadHandler(**common)
        identity = audit.IdentityDisplays(base_url=configuration[IDENTITY_URL],
            service_key=configuration[DISPLAY_KEY], access_service_key=common['service_key'],
            transport=identity_transport)
        for name, value in configuration.items():
            if name != DISPLAY_KEY and name.endswith('_SERVICE_KEY') and isinstance(value, str):
                if hmac.compare_digest(configuration[DISPLAY_KEY].encode('ascii'), value.encode('utf-8')):
                    raise ValueError()
        admin_app = admin._create_app(admin_authority, admin._engine(database), common['org_id'])
        audit_app = audit._create_app(audit_authority, audit.source._engine(database), identity, common['org_id'])
        schema = compose_schema(app.openapi(), admin_app.openapi(), audit_app.openapi())
    except Exception:
        raise RuntimeError('kdg_admin_configuration_invalid') from None
    # include_router preserves FastAPI's merged lifespan ownership. Each existing
    # candidate closure retains its own lazy engine and disposes it after draining.
    app.include_router(admin_app.router)
    app.include_router(audit_app.router)
    app.router.redirect_slashes = False
    app.openapi_schema = schema
    app.openapi = lambda: schema
    return app
