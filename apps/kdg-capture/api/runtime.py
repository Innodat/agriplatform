"""Explicit configured API factory. Reading policy performs no network or setup I/O."""
import os
from collections.abc import Mapping

from main import create_app as context_app


def create_app(environment: Mapping[str, str] | None = None, *, transport=None, identity_transport=None):
    selected = os.environ if environment is None else environment
    org_id, access_url, service_key = (
        selected.get(key) for key in ('KDG_ORG_ID', 'KDG_ACCESS_URL', 'KDG_SERVICE_KEY'))
    if not all(isinstance(value, str) and value for value in (org_id, access_url, service_key)):
        raise RuntimeError('kdg_context_configuration_invalid')
    app = context_app(org_id=org_id, access_url=access_url, service_key=service_key,
                      transport=transport)
    own_settings = ('KDG_OWN_DATABASE_URL', 'KDG_QUESTIONNAIRE_ID')
    own_enabled = any(name in selected for name in own_settings)
    if own_enabled and not all(isinstance(selected.get(name), str) and selected[name] for name in own_settings):
        raise RuntimeError('kdg_own_configuration_invalid')
    settings = ('KDG_ADMIN_READ_DATABASE_URL', 'KDG_IDENTITY_URL', 'KDG_ACTOR_DISPLAY_SERVICE_KEY')
    if any(name in selected for name in settings):
        if not all(isinstance(selected.get(name), str) and selected[name] for name in settings):
            raise RuntimeError('kdg_admin_configuration_invalid')
        from admin_runtime import compose
        app = compose(app, selected, transport=transport, identity_transport=identity_transport)
    if own_enabled:
        from own_runtime import compose
        app = compose(app, selected, transport=transport)
    return app
