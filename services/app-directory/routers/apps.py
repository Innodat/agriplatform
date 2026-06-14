"""
App Directory — /me/apps, /me/context, /apps endpoints.

Phase 2 entitlement rule:
  - Anonymous (no JWT): returns empty apps list + null context.
  - Authenticated (valid JWT): returns all enabled apps + resolved context.

Extension point (Phase 3+): filter apps by org/role/license.
"""
from fastapi import APIRouter
from auth.jwt_optional import OptionalUser
from catalog import get_enabled_apps, get_all_apps
from schemas.app_schemas import AppEntry, MeContext, MeAppsResponse

router = APIRouter()


def _resolve_context(user: dict | None) -> MeContext:
    """Extract org_id, member_id, roles from JWT payload."""
    if not user:
        return MeContext()
    return MeContext(
        org_id=user.get("org_id"),
        member_id=user.get("member_id"),
        roles=user.get("user_roles") or [],
    )


@router.get(
    "/me/apps",
    response_model=MeAppsResponse,
    summary="Get apps available to the current user",
    tags=["me"],
)
async def get_my_apps(user: OptionalUser) -> MeAppsResponse:
    """
    Returns the list of enabled apps the current user can access,
    plus their resolved identity context.

    Phase 2 rule: signed-in → all enabled apps; anonymous → empty list.
    """
    context = _resolve_context(user)
    apps = get_enabled_apps() if user else []
    return MeAppsResponse(apps=apps, context=context)


@router.get(
    "/me/context",
    response_model=MeContext,
    summary="Get the current user's identity context",
    tags=["me"],
)
async def get_my_context(user: OptionalUser) -> MeContext:
    """Returns org_id, member_id, and roles from the JWT."""
    return _resolve_context(user)


@router.get(
    "/apps",
    response_model=list[AppEntry],
    summary="Get the full app catalog (admin)",
    tags=["apps"],
)
async def list_all_apps(user: OptionalUser) -> list[AppEntry]:
    """
    Returns the full catalog including disabled apps.
    Phase 2: open to any caller (no admin gate yet).
    Phase 3+: gate behind admin role.
    """
    return get_all_apps()
