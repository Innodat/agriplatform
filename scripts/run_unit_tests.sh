#!/bin/bash

# Run unit tests for Supabase Functions

echo "Running unit tests..."
# Tests provide their own mocked supabase clients via dependency injection
# Set dummy env vars to prevent import-time errors
SUPABASE_URL="http://localhost:54321" \
SUPABASE_SECRET_KEY="test-key" \
deno test --allow-all --import-map supabase/functions/deno.json supabase/functions/tests/unit/
