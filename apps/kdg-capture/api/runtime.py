"""Explicit configured API factory. Reading policy performs no network or setup I/O."""
import os
from collections.abc import Mapping

from main import create_app as context_app


def create_app(environment: Mapping[str, str] | None = None, *, transport=None):
    selected = os.environ if environment is None else environment
    org_id, access_url, service_key = (
        selected.get(key) for key in ('KDG_ORG_ID', 'KDG_ACCESS_URL', 'KDG_SERVICE_KEY'))
    if not all(isinstance(value, str) and value for value in (org_id, access_url, service_key)):
        raise RuntimeError('kdg_context_configuration_invalid')
    return context_app(org_id=org_id, access_url=access_url, service_key=service_key,
                       transport=transport)
