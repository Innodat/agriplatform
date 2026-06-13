import subprocess
import sys
from pathlib import Path

def run_sync():
    repo_root = Path(__file__).resolve().parents[2]
    sync_script = repo_root / "platform/shared/schemas/sync/sync-zod-to-json.ts"
    if not sync_script.exists():
        print(f"❌ Sync script not found: {sync_script}")
        sys.exit(1)

    print(f"🔄 Syncing Zod → JSON Schema via: {sync_script}")
    result = subprocess.run(["ts-node", str(sync_script)], shell=(sys.platform == "win32"))
    if result.returncode != 0:
        print("❌ Sync failed.")
        sys.exit(result.returncode)


def check_diff():
    # Compare old vs new schema files (basic stub)
    # You can later use deepdiff or jsondiff for smarter comparisons
    print("🧠 Checking for schema changes...")
    # For now, assume changes exist
    proceed = input("🚦 Schema changes detected. Proceed? (y/N): ").strip().lower()
    if proceed != 'y':
        print("❌ Aborted by user.")
        sys.exit(0)


def main():
    run_sync()
    print("✅ Schema sync complete.")

if __name__ == "__main__":
    main()