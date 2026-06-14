"""
Optional JWT verifier — vendored from platform/builder-cli/templates/backend/auth/jwt_optional.py.
"""
from typing import Annotated, Optional
from fastapi import Depends, Request
from jose import JWTError, jwt

from config import settings

ALGORITHM = "HS256"


def _extract_token(request: Request) -> Optional[str]:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return None


def _decode_token(token: str) -> Optional[dict]:
    if not settings.supabase_jwt_secret:
        return None
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=[ALGORITHM],
            options={"verify_aud": False},
        )
        return payload
    except JWTError:
        return None


async def get_optional_user(request: Request) -> Optional[dict]:
    token = _extract_token(request)
    if not token:
        return None
    return _decode_token(token)


async def get_required_user(request: Request) -> dict:
    from errors import UnauthorizedError
    token = _extract_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")
    payload = _decode_token(token)
    if not payload:
        raise UnauthorizedError("Invalid or expired token")
    return payload


OptionalUser = Annotated[Optional[dict], Depends(get_optional_user)]
RequiredUser = Annotated[dict, Depends(get_required_user)]
