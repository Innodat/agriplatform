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
    _ = (
        supabase.schema("identity").table("org")
        .upsert(
            {
                "name": "Liseli",
                "slug": "liseli",
                "is_active": True,
            },
            on_conflict="slug",
            returning="minimal",  # default; body may be empty
        )
        .execute()
    )
    res = (
        supabase.schema("identity").table("org")
        .select("id")
        .eq("slug", "liseli")
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
    supabase.schema("identity").table("member_role").upsert(
        {
            "member_id": member_id,
            "role": role,
            "is_active": True,
        },
        on_conflict="member_id,role",
    ).execute()


def mark_platform_admin(user_id: str, is_platform_admin: bool) -> None:
    supabase.schema("identity").table("users").update({"is_platform_admin": is_platform_admin}).eq("id", user_id).execute()


def get_content_source_by_name(name: str) -> str:
    """Get content source ID by name"""
    res = (
        supabase.schema("cs").table("content_source")
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
        supabase.schema("identity").table("org")
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
    supabase.schema("identity").table("org").update({
        "settings": {"content_source_id": content_source_id}
    }).eq("id", org_id).execute()


def create_supabase_bucket(bucket_name: str, is_public: bool = False) -> None:
    """Create a Supabase Storage bucket"""
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


def create_azure_container_dev(container_name: str) -> None:
    """Create Azure container in Azurite (dev environment only)"""
    # Azure containers are typically created via Azure Portal/CLI
    # For dev with Azurite, this would need to use Azure SDK
    # Since we're using environment variables for connection,
    # we'll skip this and rely on lazy creation in handlers
    if ENV in ("development", "dev"):
        print(f"ℹ️  Azure container {container_name} will be created lazily via handlers (dev environment)")
    else:
        print(f"ℹ️  Skipping Azure container creation in {ENV} environment")


def create_content_source(name: str, provider: str, settings: dict) -> str:
    """Create a content source record and return its ID"""
    res = (
        supabase.schema("cs").table("content_source")
        .upsert(
            {
                "name": name,
                "provider": provider,
                "settings": settings,
                "is_active": True,
            },
            on_conflict="name",
        )
        .select("id")
        .single()
        .execute()
    )
    source_id = res.data["id"]
    print(f"✅ Created content source: {name} (provider={provider}, id={source_id})")
    return source_id


def seed_org_storage(org_slug: str, org_id: str, provider: str) -> str:
    """Complete storage setup for an organization"""
    bucket_name = f"content-{org_slug}"
    
    print(f"\n{'='*60}")
    print(f"Setting up storage for org: {org_slug}")
    print(f"  Bucket/Container: {bucket_name}")
    print(f"  Provider: {provider}")
    print(f"{'='*60}")
    
    # Create bucket/container
    if provider == "supabase_storage":
        create_supabase_bucket(bucket_name, is_public=False)
    elif provider == "azure_blob":
        create_azure_container_dev(bucket_name)
    
    # Create content source
    source_name = f"{org_slug.replace('-', ' ').title()} Storage"
    source_id = create_content_source(
        name=source_name,
        provider=provider,
        settings={"bucket_name": bucket_name},
    )
    
    # Link to org
    set_org_content_source(org_id, source_id)
    print(f"✅ Linked org {org_slug} to content source: {source_name}")
    
    return source_id


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

    supabase.schema("finance").table("receipt").insert(receipts).execute()

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

    supabase.schema("finance").table("purchase").insert(purchases).execute()
    print(f"Seeded {len(receipts)} receipts and {len(purchases)} purchases")


if __name__ == "__main__":

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SECRET_KEY")

    print("SUPABASE_URL:", url)
    print("SUPABASE_SECRET_KEY present:", bool(key))

    # Decode claims WITHOUT verifying signature
    claims = jwt.decode(key, options={"verify_signature": False})
    print("JWT role claim:", claims.get("role"))
    print("JWT iss:", claims.get("iss"))  # should match your project URL domain

    if ENV not in ("development", "dev"):
        # Create default fallback content source (if not exists)
        try:
            default_source_id = create_content_source(
                name="Default Supabase Storage",
                provider="supabase_storage",
                settings={"bucket_name": "content"},
            )
        except Exception as e:
            print(f"ℹ️  Default Supabase Storage might already exist: {e}")
            default_source_id = get_content_source_by_name("Default Supabase Storage")
        
        # ==================== LISELI ORG ====================
        admin_id = seed_user("admin@liselifoundation.org", "Admin123!")
        finance_id = seed_user("finance@liselifoundation.org", "Finance123!")
        employee_id = seed_user("employee@liselifoundation.org", "Employee123!")

        # ensure org exists
        liseli_org_id = get_liseli_org_id()
        
        # Set up storage for Liseli org (Azure Blob)
        seed_org_storage("liseli", liseli_org_id, provider="azure_blob")

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
        
        # Set up storage for Kok Home org (Supabase Storage)
        seed_org_storage("kok-home", kok_home_org_id, provider="supabase_storage")

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
