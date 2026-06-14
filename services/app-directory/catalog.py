"""
App catalog — source of truth for all apps in the platform suite.

Phase 2 entitlement rule: signed-in users see all enabled apps.
Extension point: filter by org/role when licensing is introduced (Phase 3+).

To add a new app: append an AppEntry to APP_CATALOG.
icon: lucide-react icon name (kebab-case), e.g. "book-open", "network", "wallet"
url: set via environment variable in production; defaults to localhost for dev.
"""
from schemas.app_schemas import AppEntry
from config import settings

APP_CATALOG: list[AppEntry] = [
    AppEntry(
        id="scribeswell",
        name="Scribeswell",
        url=settings.app_url_scribeswell,
        icon="book-open",
        description="Hebrew Bible reader with morphological analysis",
        enabled=True,
    ),
    AppEntry(
        id="system-engineering",
        name="System Engineering",
        url=settings.app_url_system_engineering,
        icon="network",
        description="Sites, components, requirements and maintenance",
        enabled=False,  # not yet built — hidden until live
    ),
    AppEntry(
        id="budgeting",
        name="Budgeting",
        url=settings.app_url_budgeting,
        icon="wallet",
        description="Budgets, approvals and financial controls",
        enabled=False,
    ),
    AppEntry(
        id="school-management",
        name="School Management",
        url=settings.app_url_school_management,
        icon="school",
        description="Learners, classes, staff and administration",
        enabled=False,
    ),
    AppEntry(
        id="modelling-simulation",
        name="Modelling & Simulation",
        url=settings.app_url_modelling_simulation,
        icon="flask-conical",
        description="System model snapshots and scenario simulation",
        enabled=False,
    ),
]


def get_enabled_apps() -> list[AppEntry]:
    """Return all enabled apps from the catalog."""
    return [app for app in APP_CATALOG if app.enabled]


def get_all_apps() -> list[AppEntry]:
    """Return the full catalog (admin use)."""
    return APP_CATALOG
