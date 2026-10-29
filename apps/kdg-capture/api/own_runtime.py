"""Explicit configured own API composition; existing candidates own every request.

No connection, migration, seeding, administrative write or startup background work.
"""
import importlib
from copy import deepcopy
from pathlib import Path
import sys

from sqlalchemy.engine import make_url

DATABASE='KDG_OWN_DATABASE_URL'
QUESTIONNAIRE='KDG_QUESTIONNAIRE_ID'
SETTINGS=(DATABASE,QUESTIONNAIRE)
MODULES=('provision','create','edit','edit_context','recovery','read','history')


def handlers():
    source=str(Path(__file__).resolve().parents[1]/'write-candidate')
    sys.path.insert(0,source)
    try:
        for name in MODULES:
            importlib.import_module(name+'_openapi')
        return tuple(importlib.import_module(name+'_http') for name in MODULES)
    finally:
        sys.path.remove(source)


def applications(authorities,engines,org_id,questionnaire_id):
    modules=handlers()
    return [module._create_app(authority,engine,org_id,questionnaire_id)
            if name=='provision' else module._create_app(authority,engine,org_id)
            for name,module,authority,engine in zip(MODULES,modules,authorities,engines,strict=True)]



def schemas(owners):
    """Qualify owner DTO names while preserving every owning declaration/ref.

    Existing isolated owners legitimately use names such as CaptureReceipt for
    differing wire declarations. The configured contract gives each one a stable
    owner namespace; the strict merger still rejects an actual namespace collision.
    """
    result=[]
    for name,owner in zip(MODULES,owners,strict=True):
        schema=deepcopy(owner.openapi())
        prefix='Own'+''.join(part.title() for part in name.split('_'))
        definitions=schema.get('components',{}).get('schemas',{})
        renamed={key:prefix+key for key in definitions}
        references={'#/components/schemas/'+key:'#/components/schemas/'+value for key,value in renamed.items()}
        def rewrite(value):
            if isinstance(value,dict):return {key:rewrite(child) for key,child in value.items()}
            if isinstance(value,list):return [rewrite(child) for child in value]
            return references.get(value,value) if isinstance(value,str) else value
        schema=rewrite(schema)
        schema['components']['schemas']={renamed[key]:value for key,value in schema['components']['schemas'].items()}
        result.append(schema)
    return result


def compose(app,configuration,*,transport=None):
    try:
        from context import canonical_uuid
        from admin_runtime import compose_schema
        database=configuration[DATABASE]
        if make_url(database).username!='kdg_capture_runtime':
            raise ValueError()
        questionnaire=canonical_uuid(configuration[QUESTIONNAIRE])
        modules=handlers()
        common=dict(org_id=configuration['KDG_ORG_ID'],access_url=configuration['KDG_ACCESS_URL'],
                    service_key=configuration['KDG_SERVICE_KEY'],transport=transport)
        provision,create,edit,edit_context,recovery,read,history=modules
        # All authority/configuration validation precedes engine construction.
        authorities=[provision.recovery.ProvisionHandler(questionnaire_id=questionnaire,**common),
            create.handler.CreateHandler(**common),edit.handler.EditHandler(**common),
            edit_context.recovery.EditContextHandler(**common),recovery.recovery.RecoveryHandler(**common),
            read.recovery.ReadHandler(**common),history.recovery.HistoryHandler(**common)]
        engines=[module._engine(database) for module in modules]
        owners=applications(authorities,engines,common['org_id'],questionnaire)
        base=app.openapi()
        title='KDG Capture configured API' if '/api/v1/admin/captures' in base['paths'] else 'KDG Capture configured own API'
        schema=compose_schema(base,*schemas(owners),title=title)
    except Exception:
        raise RuntimeError('kdg_own_configuration_invalid') from None
    # FastAPI retains merged lifespans. Existing closures keep their engine/state;
    # GET/POST and GET/PUT sharing a legitimate path remain distinct operations.
    for owner in owners:
        app.include_router(owner.router)
    app.router.redirect_slashes=False
    app.openapi_schema=schema
    app.openapi=lambda:schema
    return app
