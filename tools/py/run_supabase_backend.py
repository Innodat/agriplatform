import subprocess
import sys
import os
from pathlib import Path
from pydantic import BaseModel, Field, ValidationError

from run_schema_sync import run_sync


class SupabaseArgs(BaseModel):
    command: str = Field(..., description="Supabase CLI command, e.g., 'db'")
    action: str = Field(..., description="Action, e.g., 'push', 'reset', 'migrate'")
    approve: bool = Field(default=False, description="Skip approval gate if True")

# Parse basic CLI args
raw = sys.argv[1:]
args_map = {}
if len(raw) >= 2:
    args_map['command'] = raw[0]
    args_map['action'] = raw[1]
if '--approve' in raw:
    args_map['approve'] = True

try:
    args = SupabaseArgs(**args_map)
except ValidationError as e:
    print("❌ Invalid CLI args:", e)
    sys.exit(1)

# Approval gate stub
if not args.approve:
    print(f"🚦 Approval required for: supabase {args.command} {args.action}")
    proceed = input("Proceed? (y/N): ").strip().lower()
    if proceed != 'y':
        print("❌ Aborted by user.")
        sys.exit(0)

# Before executing Supabase CLI
run_sync()
check_diff()

# Resolve Supabase CLI path
supabase_cmd = "supabase"  # Assumes Supabase CLI in PATH
# Could also resolve from node_modules/.bin if needed

cmd = [supabase_cmd, args.command, args.action]

print(f"▶ Running: {' '.join(cmd)}")
result = subprocess.run(cmd)
sys.exit(result.returncode)