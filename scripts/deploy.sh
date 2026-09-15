# login
npx supabase login

# supabase secrets
npx supabase secrets set ENV="prod"
npx supabase secrets set LISELI_AZURE_BLOB_CONNECTION="..."

# DB migrations
npx supabase db push
npx supabase db seed

# functions
cd ../supabase/functions/_shared; ln -s ../../../packages/shared .; cd ../../../;
npx supabase functions deploy