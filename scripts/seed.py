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
    command = ["npx", "supabase", "secrets", "set"]
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
        "email_confirm": True
    })
    user_id = user.user.id

    print(f"Seeded user with user_id={user_id} email={email}")
    return user_id


def get_org_id_by_slug(slug: str) -> str:
    """Get org ID by slug (org must already exist)"""
    res = (
        supabase.schema("identity").table("org")
        .select("id")
        .eq("slug", slug)
        .limit(1)
        .single()
        .execute()
    )
    return res.data["id"]


def upsert_org_id(name: str, slug: str) -> str:
    # Create or update org (used for orgs not in SQL seeds)
    _ = (
        supabase.schema("identity").table("org")
        .upsert(
            {
                "name": name,
                "slug": slug,
                "deleted_at": None,
            },
            on_conflict="slug",
            returning="minimal",  # default; body may be empty
        )
        .execute()
    )
    res = (
        supabase.schema("identity").table("org")
        .select("id")
        .eq("slug", slug)
        .limit(1)
        .single()
        .execute()
    )

    return res.data["id"]



def seed_org_member(org_id: str, user_id: str, is_owner: bool) -> int:
    res = (
        supabase.schema("identity").table("org_member")
        .upsert(
            {
                "org_id": org_id,
                "user_id": user_id,
                "is_owner": is_owner,
                "deleted_at": None,
            },
            on_conflict="org_id,user_id",
            returning="representation"

        )
        .execute()
    )
    return int(res.data[0]["id"])


def seed_member_role(member_id: int, role: str) -> None:
    # role is identity.app_role enum
    supabase.schema("identity").table("member_role").upsert(
        {
            "member_id": member_id,
            "role": role,
            "deleted_at": None,
        },
        on_conflict="member_id,role",
    ).execute()


def mark_platform_admin(user_id: str, is_platform_admin: bool) -> None:
    supabase.schema("identity").table("users").update({"is_platform_admin": is_platform_admin}).eq("id", user_id).execute()


def create_supabase_bucket(bucket_name: str, is_public: bool = False) -> None:
    """Create a Supabase Storage bucket (idempotent)"""
    try:
        res = supabase.storage.create_bucket(
            bucket_name,
            options={"public": is_public},
        )
        print(f"✅ Created Supabase bucket: {bucket_name} (public={is_public})")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"ℹ️  Bucket {bucket_name} already exists, skipping creation")
        else:
            raise


def seed_receipts(user_id: str, org_id: str):
    # Insert 5 receipts, 2 for today
    receipts = []
    today = datetime.today().date()
    for i in range(1, 6):
        receipt_date = today if i <= 2 else (today - timedelta(days=i * 2))
        receipt_date_str = receipt_date.isoformat()
        status = "pending" if i <= 2 else "approved"
        receipts.append(
            {
                "org_id": org_id,
                "receipt_date": receipt_date_str,
                "status": status,
                "deleted_at": None,
                "created_at": datetime.now().isoformat(),
                "created_by": user_id,
                "updated_by": user_id,
                "updated_at": datetime.now().isoformat(),
            }
        )

    receipt_result = supabase.schema("finance").table("receipt").insert(receipts).execute()

    receipt_rows = receipt_result.data or []
    receipt_ids = [row.get("id") for row in receipt_rows if row.get("id") is not None]

    # Insert purchases linked to receipt 1..5
    purchases = [
        {
            "receipt_id": receipt_ids[0] if len(receipt_ids) > 0 else None,
            "expense_type_id": 1,
            "currency_id": 1,
            "user_id": user_id,
            "amount": 150.00,
            "reimbursable": True,
            "deleted_at": None,
            "created_at": datetime.now().isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": datetime.now().isoformat(),
        },
        {
            "receipt_id": receipt_ids[0] if len(receipt_ids) > 0 else None,
            "expense_type_id": 2,
            "currency_id": 2,
            "user_id": user_id,
            "amount": 75.50,
            "reimbursable": False,
            "deleted_at": None,
            "created_at": datetime.now().isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": datetime.now().isoformat(),
        },
        {
            "receipt_id": receipt_ids[1] if len(receipt_ids) > 1 else None,
            "expense_type_id": 3,
            "currency_id": 3,
            "user_id": user_id,
            "amount": 200.00,
            "reimbursable": True,
            "deleted_at": None,
            "created_at": datetime.now().isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": datetime.now().isoformat(),
        },
        {
            "receipt_id": receipt_ids[2] if len(receipt_ids) > 2 else None,
            "expense_type_id": 4,
            "currency_id": 4,
            "user_id": user_id,
            "amount": 50.00,
            "reimbursable": False,
            "deleted_at": None,
            "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=2)).isoformat(),
        },
        {
            "receipt_id": receipt_ids[3] if len(receipt_ids) > 3 else None,
            "expense_type_id": 5,
            "currency_id": 5,
            "user_id": user_id,
            "amount": 300.00,
            "reimbursable": True,
            "deleted_at": None,
            "created_at": (datetime.now() - timedelta(days=5)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=5)).isoformat(),
        },
        {
            "receipt_id": receipt_ids[4] if len(receipt_ids) > 4 else None,
            "expense_type_id": 6,
            "currency_id": 1,
            "user_id": user_id,
            "amount": 120.00,
            "reimbursable": False,
            "deleted_at": None,
            "created_at": (datetime.now() - timedelta(days=10)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=10)).isoformat(),
        },
    ]

    purchases = [row for row in purchases if row["receipt_id"] is not None]
    supabase.schema("finance").table("purchase").insert(purchases).execute()
    print(f"Seeded {len(receipts)} receipts and {len(purchases)} purchases")


if __name__ == "__main__":
    if ENV in ("development", "dev"):
        # ==================== LISELI ORG ====================
        admin_id = seed_user("admin@liselifoundation.org", "Admin123!")
        finance_id = seed_user("finance@liselifoundation.org", "Finance123!")
        employee_id = seed_user("employee@liselifoundation.org", "Employee123!")

        # get org from DB (created in SQL seed)
        liseli_org_id = get_org_id_by_slug("liseli")

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
        kok_home_org_id = upsert_org_id("Kok Home", "kok-home")

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
        # seed_secrets()  # Not needed for local supabase cli, env file is used
