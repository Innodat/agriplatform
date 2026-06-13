#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Setting up Supabase dev environment"

# 1. Ensure Supabase CLI exists
if ! command -v supabase &> /dev/null
then
    echo "📦 Installing Supabase CLI…"
    curl -fsSL https://supabase.com/cli/install | sh
fi

# 2. Ensure .env exists (create from template if missing)
if [[ ! -f ".env" ]]; then
    echo "📄 Creating .env from template…"
    if [[ -f ".env.example" ]]; then
        cp .env.example .env
    else
        echo "❌ No .env or .env.example found"
        exit 1
    fi
fi

# 3. Sync secrets
echo "🔄 Syncing secrets to Supabase…"
grep -v '^\s*$' ".env" | grep -v '^\s*#' | supabase secrets set --from-stdin

# 4. Start services
echo "▶️ Starting Supabase stack locally…"
supabase start

# Symlink shared package for reac-native mobile app
cd ../supabase/functions/_shared; ln -s ../../../packages/shared .; cd ../../../;


echo "🎉 Environment ready!"