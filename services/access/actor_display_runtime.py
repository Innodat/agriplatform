"""Explicit native activation of the reviewed Identity retained-display owner.

Construction validates policy only: no connection, migration, retry or label cache.
An absent policy keeps the route closed before reading a request body.
"""
from collections.abc import Mapping

from actor_display_http import ACTIVE, PREVIOUS, ORG, ActorDisplayPolicy
from actor_display_http import create_router as owner_router

DATABASE = 'IDENTITY_ACTOR_DISPLAY_DATABASE_URL'
SETTINGS = (ACTIVE, PREVIOUS, ORG, DATABASE)


async def _disabled(selected, deadline):
    # The disabled owner policy refuses before invoking this collaborator.
    raise RuntimeError('identity_actor_display_unavailable')


def create_router(configuration: Mapping[str, str]):
    if not any(name in configuration for name in SETTINGS):
        return owner_router({}, _disabled)
    try:
        # Validate the dedicated active/previous credentials and every other supplied
        # service key before constructing the private native dependency.
        ActorDisplayPolicy(configuration)
        if ACTIVE not in configuration or ORG not in configuration:
            raise ValueError()
        database = configuration[DATABASE]
        if not isinstance(database, str) or not database.strip():
            raise ValueError()
        from actor_display_native import PrivateConnection, NativeActorDisplayReader
        reader = NativeActorDisplayReader(PrivateConnection(database))
    except Exception:
        raise RuntimeError('actor_display_configuration_invalid') from None
    return owner_router(configuration, reader)
