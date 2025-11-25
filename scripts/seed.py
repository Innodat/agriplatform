import os
from supabase import create_client, Client
from dotenv import load_dotenv

from datetime import datetime, timedelta


# Load environment variables from .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
ENV = os.getenv("ENV", "development")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def seed_secrets():
    # Build the CLI command
    command = ["supabase", "secrets", "set"]
    secrets = ["LISELI_AZURE_STORAGE_CONNECTION"]
    for s in secrets:
        command.append(f"{s}={os.getenv(s)}")

    # Execute the command
    try:
        subprocess.run(command, check=True)
        print("✅ Secrets successfully pushed to Supabase Vault!")
    except subprocess.CalledProcessError as e:
        print("❌ Error pushing secrets:", e)


def seed_user(email: str, password: str):
    # Create the auth user
    user = supabase.auth.admin.create_user({
        "email": email,
        "password": password,
    })
    user_id = user.user.id

    print(f"Seeded employee with user_id={user_id}")
    return user_id


def seed_employee():
    user_id = seed_user('employee@liselifoundation.org', 'Employee123!')
    
    from datetime import datetime, timedelta


def seed_receipts(user_id: str):
    # Insert 5 receipts, 2 for today
    receipts = []
    for i in range(1, 6):
        receipts.append({
            "id": i,
            "receipt_date": datetime.today().date() if i <= 2 else (datetime.today().date() - timedelta(days=i*2)),
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": datetime.now().isoformat(),
        })
    supabase.table("finance.receipt").insert(receipts).execute()

    # Insert purchases linked to receipt 1
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
        from datetime import datetime, timedelta

def build_purchases(user_id: str):
    purchases = [
        {
            "receipt_id": 6,
            "expense_type_id": 1,
            "currency_id": 2,
            "user_id": user_id,
            "amount": 180.00,
            "reimbursable": True,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=11)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=11)).isoformat(),
        },
        {
            "receipt_id": 7,
            "expense_type_id": 2,
            "currency_id": 3,
            "user_id": user_id,
            "amount": 90.00,
            "reimbursable": False,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=12)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=12)).isoformat(),
        },
        {
            "receipt_id": 8,
            "expense_type_id": 3,
            "currency_id": 4,
            "user_id": user_id,
            "amount": 210.00,
            "reimbursable": True,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=13)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=13)).isoformat(),
        },
        {
            "receipt_id": 9,
            "expense_type_id": 4,
            "currency_id": 5,
            "user_id": user_id,
            "amount": 60.00,
            "reimbursable": False,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=14)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=14)).isoformat(),
        },
        {
            "receipt_id": 10,
            "expense_type_id": 5,
            "currency_id": 1,
            "user_id": user_id,
            "amount": 320.00,
            "reimbursable": True,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=15)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=15)).isoformat(),
        },
        {
            "receipt_id": 11,
            "expense_type_id": 6,
            "currency_id": 2,
            "user_id": user_id,
            "amount": 130.00,
            "reimbursable": False,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=16)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=16)).isoformat(),
        },
        {
            "receipt_id": 12,
            "expense_type_id": 1,
            "currency_id": 3,
            "user_id": user_id,
            "amount": 170.00,
            "reimbursable": True,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=17)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=17)).isoformat(),
        },
        {
            "receipt_id": 13,
            "expense_type_id": 2,
            "currency_id": 4,
            "user_id": user_id,
            "amount": 95.00,
            "reimbursable": False,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=18)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=18)).isoformat(),
        },
        {
            "receipt_id": 14,
            "expense_type_id": 3,
            "currency_id": 5,
            "user_id": user_id,
            "amount": 220.00,
            "reimbursable": True,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=19)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=19)).isoformat(),
        },
        {
            "receipt_id": 15,
            "expense_type_id": 4,
            "currency_id": 1,
            "user_id": user_id,
            "amount": 70.00,
            "reimbursable": False,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=20)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=20)).isoformat(),
        },
        {
            "receipt_id": 16,
            "expense_type_id": 5,
            "currency_id": 2,
            "user_id": user_id,
            "amount": 340.00,
            "reimbursable": True,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=21)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=21)).isoformat(),
        },
        {
            "receipt_id": 17,
            "expense_type_id": 6,
            "currency_id": 3,
            "user_id": user_id,
            "amount": 140.00,
            "reimbursable": False,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=22)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=22)).isoformat(),
        },
        {
            "receipt_id": 18,
            "expense_type_id": 1,
            "currency_id": 4,
            "user_id": user_id,
            "amount": 160.00,
            "reimbursable": True,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=23)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=23)).isoformat(),
        },
        {
            "receipt_id": 19,
            "expense_type_id": 2,
            "currency_id": 5,
            "user_id": user_id,
            "amount": 85.00,
            "reimbursable": False,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=24)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=24)).isoformat(),
        },
        {
            "receipt_id": 20,
            "expense_type_id": 3,
            "currency_id": 1,
            "user_id": user_id,
            "amount": 230.00,
            "reimbursable": True,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=25)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=25)).isoformat(),
        },
        {
            "receipt_id": 21,
            "expense_type_id": 4,
            "currency_id": 2,
            "user_id": user_id,
            "amount": 80.00,
            "reimbursable": False,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=26)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=26)).isoformat(),
        },
        {
            "receipt_id": 22,
            "expense_type_id": 5,
            "currency_id": 3,
            "user_id": user_id,
            "amount": 360.00,
            "reimbursable": True,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=27)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=27)).isoformat(),
        },
        {
            "receipt_id": 23,
            "expense_type_id": 9,
            "currency_id": 4,
            "user_id": user_id,
            "amount": 150.00,
            "reimbursable": False,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=27)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=27)).isoformat(),
        },
        {
            "receipt_id": 24,
            "expense_type_id": 1,
            "currency_id": 1,
            "user_id": user_id,
            "amount": 190.00,
            "reimbursable": True,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=27)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=27)).isoformat(),
        },
        {
            "receipt_id": 25,
            "expense_type_id": 2,
            "currency_id": 5,
            "user_id": user_id,
            "amount": 105.00,
            "reimbursable": False,
            "is_active": True,
            "created_at": (datetime.now() - timedelta(days=27)).isoformat(),
            "created_by": user_id,
            "updated_by": user_id,
            "updated_at": (datetime.now() - timedelta(days=27)).isoformat(),
        }
    ]
    supabase.table("finance.purchase").insert(purchases).execute()
    print(f"Seeded {len(receipts)} receipts and {len(purchases)} purchases for user {user_id}")


if __name__ == "__main__":
    if ENV == "development":
        seed_user('admin@liselifoundation.org', 'Admin123!')
        seed_user('finance@liselifoundation.org', 'Finance123!')
        seed_employee()
        seed_secrets()
