"""
App Directory — Pydantic schemas.

AppEntry mirrors the Zod schema in platform/app-directory-client/src/schemas.ts.
Keep these two in sync — they are the cross-app contract.
"""
from pydantic import BaseModel, HttpUrl
from typing import Optional


class AppEntry(BaseModel):
    """A single app in the catalog."""
    id: str
    name: str
    url: str          # HttpUrl serialises to str in JSON; keep as str for simplicity
    icon: str         # lucide-react icon name, e.g. "book-open", "network"
    description: str
    enabled: bool = True


class MeContext(BaseModel):
    """Resolved identity context for the current request."""
    org_id: Optional[str] = None
    member_id: Optional[int] = None
    roles: list[str] = []


class MeAppsResponse(BaseModel):
    apps: list[AppEntry]
    context: MeContext
