# Auth Hook Registration Guide

## Problem
The `identity.custom_access_token_hook` function exists in the database but is not being called by Supabase Auth. This is because auth hooks must be explicitly registered in the Supabase Dashboard.

## Solution

### Step 1: Verify the Function Exists

Run this query in Supabase SQL Editor to confirm the function is created:

```sql
SELECT 
  proname as function_name,
  pg_get_functiondef(oid) as definition
FROM pg_proc 
WHERE proname = 'custom_access_token_hook' 
  AND pronamespace = 'identity'::regnamespace;
```

### Step 2: Register the Hook in Supabase Dashboard

1. **Open Supabase Dashboard**
   - Go to https://supabase.com/dashboard
   - Select your project: `tsbtiakfqhwpfgtokbwi`

2. **Navigate to Auth Hooks**
   - Click on "Authentication" in the left sidebar
   - Click on "Hooks" tab
   - Or go directly to: `https://supabase.com/dashboard/project/tsbtiakfqhwpfgtokbwi/auth/hooks`

3. **Add Custom Access Token Hook**
   - Find the "Custom Access Token" section
   - Click "Add a new hook" or "Enable hook"
   - Select "Postgres Function" as the hook type
   - Enter the function details:
     - **Schema**: `identity`
     - **Function Name**: `custom_access_token_hook`
   - Click "Save" or "Create"

### Step 3: Verify Hook Registration

After registering, you can verify by checking the auth configuration:

```sql
-- This query may not work in all Supabase versions
SELECT * FROM auth.config WHERE name LIKE '%hook%';
```

Or simply test by signing in and checking the JWT payload.

### Step 4: Test the Hook

1. **Sign out completely**:
   ```typescript
   await supabase.auth.signOut()
   ```

2. **Sign in again**:
   ```typescript
   await supabase.auth.signInWithPassword({
     email: 'employee@liselifoundation.org',
     password: 'your-password'
   })
   ```

3. **Check the JWT payload**:
   ```typescript
   const { data: { session } } = await supabase.auth.getSession()
   console.log('JWT Claims:', session?.user)
   
   // Decode the access_token to see all claims
   const token = session?.access_token
   if (token) {
     const payload = JSON.parse(atob(token.split('.')[1]))
     console.log('Full JWT Payload:', payload)
     console.log('user_role claim:', payload.user_role)
     console.log('role_ids claim:', payload.role_ids)
   }
   ```

### Expected JWT Payload After Fix

```json
{
  "iss": "https://tsbtiakfqhwpfgtokbwi.supabase.co/auth/v1",
  "sub": "8080f75c-5406-4bf3-a0cb-4d08be333373",
  "aud": "authenticated",
  "exp": 1761746355,
  "iat": 1761742755,
  "email": "employee@liselifoundation.org",
  "phone": "",
  "app_metadata": {
    "provider": "email",
    "providers": ["email"]
  },
  "user_metadata": {
    "email_verified": true
  },
  "role": "authenticated",
  "aal": "aal1",
  "amr": [
    {
      "method": "password",
      "timestamp": 1761742755
    }
  ],
  "session_id": "b9bff25e-b6ef-4019-85f0-b4c74a91d2d4",
  "is_anonymous": false,
  "user_role": "employee",           // ← NEW: Custom claim
  "role_ids": [1, 2],                // ← NEW: Custom claim
  "department_ids": []               // ← NEW: Custom claim
}
```

## Troubleshooting

### Hook Not Executing

If the hook still doesn't execute after registration:

1. **Check function permissions**:
   ```sql
   -- Verify grants
   SELECT 
     grantee, 
     privilege_type 
   FROM information_schema.routine_privileges 
   WHERE routine_name = 'custom_access_token_hook' 
     AND routine_schema = 'identity';
   ```

2. **Check user has roles**:
   ```sql
   -- Replace with actual user UUID
   SELECT * FROM identity.user_roles 
   WHERE user_id = '8080f75c-5406-4bf3-a0cb-4d08be333373'
     AND deleted_at = NULL;
   ```

3. **Test function manually**:
   ```sql
   -- Test the function with mock event
   SELECT identity.custom_access_token_hook(
     jsonb_build_object(
       'user_id', '8080f75c-5406-4bf3-a0cb-4d08be333373',
       'claims', '{}'::jsonb
     )
   );
   ```

### Common Issues

1. **Function not found**: Re-run the migration to create the function
2. **Permission denied**: Ensure `supabase_auth_admin` role has EXECUTE permission
3. **Hook not registered**: Must be done via Dashboard, cannot be done via SQL
4. **Old tokens cached**: Sign out completely and sign in again

## Alternative: Manual Hook Registration via SQL (Advanced)

If the Dashboard method doesn't work, you may need to contact Supabase support or use their CLI:

```bash
# Using Supabase CLI (if available)
supabase functions deploy custom_access_token_hook \
  --project-ref tsbtiakfqhwpfgtokbwi
```

## References

- [Supabase Auth Hooks Documentation](https://supabase.com/docs/guides/auth/auth-hooks)
- [Custom Access Token Hook](https://supabase.com/docs/guides/auth/auth-hooks#hook-custom-access-token)
- Migration file: `supabase/migrations/20251029T1249_fix_auth_hook_user_role_claim.sql`
