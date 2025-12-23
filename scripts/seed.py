import os
import subprocess
from datetime import datetime, timedelta

from dotenv import load_dotenv
from supabase import Client, create_client

# Load environment variables from .env
load_dotenv()

ENV = os.getenv("ENV", "dev")

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SECRET_KEY"))


def seed_secrets():
    command = ["supabase", "secrets", "set"]
    secrets = ["LISELI_AZURE_STORAGE_CONNECTION", "ALLOWED_ORIGINS"]
    for s in secrets:
        command.append(f"{s}={os.getenv(s)}")

    try:
        subprocess.run(command, check=True)
        print("✅ Secrets successfully pushed to Supabase Vault!")
    except subprocess.CalledProcessError as e:
        print("❌ Error pushing secrets:", e)


def seed_user(email: str, password: str) -> str:
    user = supabase.auth.admin.create_user({
        "email": email,
        "password": password,
    })
    user_id = user.user.id

    print(f"Seeded user with user_id={user_id} email={email}")
    return user_id


def get_liseli_org_id() -> str:
    # finance seed inserts org too, but we may run this script without SQL seeds.
    # Use upsert-by-slug semantics.
    res = (
        supabase.table("identity.org")
        .upsert(
            {
                "name": "Liseli",
                "slug": "liseli",
                "is_active": True,
            },
            on_conflict="slug",
        )
        .select("id")
        .single()
        .execute()
    )
    return res.data["id"]


def seed_org_member(org_id: str, user_id: str, is_owner: bool) -> int:
    res = (
        supabase.table("identity.org_member")
        .upsert(
            {
                "org_id": org_id,
                "user_id": user_id,
                "is_owner": is_owner,
                "is_active": True,
            },
            on_conflict="org_id,user_id",
        )
        .select("id")
        .single()
        .execute()
    )
    return int(res.data["id"])


def seed_member_role(member_id: int, role: str) -> None:
    # role is identity.app_role enum
    supabase.table("identity.member_role").upsert(
        {
            "member_id": member_id,
            "role": role,
            "is_active": True,
        },
        on_conflict="member_id,role",
    ).execute()


def mark_platform_admin(user_id: str, is_platform_admin: bool) -> None:
    supabase.table("identity.users").update({"is_platform_admin": is_platform_admin}).eq("id", user_id).execute()


def get_content_source_by_name(name: str) -> str:
    """Get content source ID by name"""
    res = (
        supabase.table("cs.content_source")
        .select("id")
        .eq("name", name)
        .eq("is_active", True)
        .limit(1)
        .single()
        .execute()
    )
    return res.data["id"]


def get_kok_home_org_id() -> str:
    res = (
        supabase.table("identity.org")
        .upsert(
            {
                "name": "Kok Home",
                "slug": "kok-home",
                "is_active": True,
            },
            on_conflict="slug",
        )
        .select("id")
        .single()
        .execute()
    )
    return res.data["id"]


def set_org_content_source(org_id: str, content_source_id: str) -> None:
    supabase.table("identity.org").update({
        "settings": {"content_source_id": content_source_id}
    }).eq("id", org_id).execute()


def seed_receipts(user_id: str, org_id: str):
    # Insert 5 receipts, 2 for today
    receipts = []
    for i in range(1, 6):
        receipts.append(
            {
                "id": i,
                "org_id": org_id,
                "receipt_date": datetime.today().date()
                if i <= 2
                else (datetime.today().date() - timedelta(days=i * 2)),
                "is_active": True,
                "created_at": datetime.now().isoformat(),
                "created_by": user_id,
                "updated_by": user_id,
                "updated_at": datetime.now().isoformat(),
            }
        )

    supabase.table("finance.receipt").insert(receipts).execute()

    # Insert purchases linked to receipt 1..5
    purchases = [
        {
            "receipt_id": 1,
            "expense_type_id": 1,
            "currency_id": 1,
            "user_id": user_id,
            "amount": 150.00,
            "reimbursable": True,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": datetime.now().isoformat(),
        },
        {
            "receipt_id": 1,
            "expense_type_id": 2,
            "currency_id": 2,
            "user_id": user_id,
            "amount": 75.50,
            "reimbursable": False,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": datetime.now().isoformat(),
        },
        {
            "receipt_id": 2,
            "expense_type_id": 3,
            "currency_id": 3,
            "user_id": user_id,
            "amount": 200.00,
            "reimbursable": True,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": datetime.now().isoformat(),
        },
        {
            "receipt_id": 3,
            "expense_type_id": 4,
            "currency_id": 4,
            "user_id": user_id,
            "amount": 50.00,
            "reimbursable": False,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=2)).isoformat(),
        },
        {
            "receipt_id": 4,
            "expense_type_id": 5,
            "currency_id": 5,
            "user_id": user_id,
            "amount": 300.00,
            "reimbursable": True,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=5)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=5)).isoformat(),
        },
        {
            "receipt_id": 5,
            "expense_type_id": 6,
            "currency_id": 1,
            "user_id": user_id,
            "amount": 120.00,
            "reimbursable": False,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=10)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=10)).isoformat(),
        },
    ]

    supabase.table("finance.purchase").insert(purchases).execute()
    print(f"Seeded {len(receipts)} receipts and {len(purchases)} purchases")


if __name__ == "__main__":
    if ENV in ("development", "dev"):
        # Get content source IDs
        default_source_id = get_content_source_by_name("Default Supabase Storage")
        liseli_azure_source_id = get_content_source_by_name("Liseli Azure Storage")
        
        # ==================== LISELI ORG ====================
        admin_id = seed_user("admin@liselifoundation.org", "Admin123!")
        finance_id = seed_user("finance@liselifoundation.org", "Finance123!")
        employee_id = seed_user("employee@liselifoundation.org", "Employee123!")

        # ensure org exists
        liseli_org_id = get_liseli_org_id()
        
        # Set content source for Liseli org (Liseli Azure Storage)
        set_org_content_source(liseli_org_id, liseli_azure_source_id)

        # memberships
        admin_member_id = seed_org_member(liseli_org_id, admin_id, is_owner=True)
        finance_member_id = seed_org_member(liseli_org_id, finance_id, is_owner=False)
        employee_member_id = seed_org_member(liseli_org_id, employee_id, is_owner=False)

        # member roles (multi-role supported)
        seed_member_role(admin_member_id, "admin")
        seed_member_role(finance_member_id, "financeadmin")
        seed_member_role(employee_member_id, "employee")

        # platform admins (org creation is platform-admin only)
        mark_platform_admin(admin_id, True)

        # receipts demo data seeded under org
        seed_receipts(employee_id, liseli_org_id)
        
        # ==================== KOK HOME ORG ====================
        kok_admin_id = seed_user("admin@kokhome.org", "Admin123!")
        kok_finance_id = seed_user("finance@kokhome.org", "Finance123!")
        kok_employee_id = seed_user("employee@kokhome.org", "Employee123!")

        # ensure org exists
        kok_home_org_id = get_kok_home_org_id()
        
        # memberships
        kok_admin_member_id = seed_org_member(kok_home_org_id, kok_admin_id, is_owner=True)
        kok_finance_member_id = seed_org_member(kok_home_org_id, kok_finance_id, is_owner=False)
        kok_employee_member_id = seed_org_member(kok_home_org_id, kok_employee_id, is_owner=False)

        # member roles
        seed_member_role(kok_admin_member_id, "admin")
        seed_member_role(kok_finance_member_id, "financeadmin")
        seed_member_role(kok_employee_member_id, "employee")

        # platform admins
        mark_platform_admin(kok_admin_id, True)

        # receipts demo data for Kok Home
        seed_receipts(kok_employee_id, kok_home_org_id)
        
        # ==================== SECRETS ====================
        seed_secrets()
