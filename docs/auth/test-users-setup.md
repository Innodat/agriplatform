# Test Users Setup Guide

This guide explains how to create test users for development and testing of the authentication system.

## Overview

The authentication system requires users to be created in Supabase Auth, then linked to the `identity.users` table, and finally assigned roles in the `identity.user_roles` table.

## Test User Credentials

| Role | Email | Password | Description |
|------|-------|----------|-------------|
| Admin | admin@liselifoundation.org | Admin123! | Full system access, can approve/reject all purchases |
| Finance Admin | finance@liselifoundation.org | Finance123! | Finance department admin, can manage finance operations |
| Employee | employee@liselifoundation.org | Employee123! | Regular employee, can submit receipts |

## Method 1: Supabase Dashboard (Recommended)

### Step 1: Create Users in Supabase Auth

1. Go to your Supabase project dashboard
2. Navigate to **Authentication** → **Users**
3. Click **Add user** button
4. For each test user:
   - Enter the email address (e.g., `admin@liselifoundation.org`)
   - Enter the password (e.g., `Admin123!`)
   - Check **Auto Confirm User** (for development)
   - Click **Create user**
5. **Important**: Copy the UUID of each created user - you'll need these in the next steps

### Step 2: Create Identity Records

1. Navigate to **SQL Editor** in Supabase Dashboard
2. Run the following SQL for each user (replace UUIDs with actual values):

```sql
-- Admin User
UPDATE identity.users SET username = 'Admin User' where id = 'PASTE-ADMIN-UUID-HERE';
UPDATE identity.users SET username = 'Finance Admin' where id = 'PASTE-FINANCE-UUID-HERE';
UPDATE identity.users SET username = 'Employee User' where id = 'PASTE-EMPLOYEE-UUID-HERE';

-- if it does not exist for some reason:
INSERT INTO identity.users (id, username, is_system)
VALUES ('PASTE-ADMIN-UUID-HERE', 'Admin User', false);

-- Finance Admin User
INSERT INTO identity.users (id, username, is_system)
VALUES ('PASTE-FINANCE-UUID-HERE', 'Finance Admin', false);

-- Employee User
INSERT INTO identity.users (id, username, is_system)
VALUES ('PASTE-EMPLOYEE-UUID-HERE', 'Employee User', false);
```

### Step 3: Assign Roles

Run the following SQL to assign roles (replace UUIDs with actual values):

```sql
-- Admin Role
INSERT INTO identity.user_roles (user_id, role)
VALUES ('PASTE-ADMIN-UUID-HERE', 'admin');

-- Finance Admin Role
INSERT INTO identity.user_roles (user_id, role)
VALUES ('PASTE-FINANCE-UUID-HERE', 'financeadmin');

-- Employee Role
INSERT INTO identity.user_roles (user_id, role)
VALUES ('PASTE-EMPLOYEE-UUID-HERE', 'employee');
```

### Step 4: Verify Setup

Run these verification queries:

```sql
-- Check all test users
SELECT 
  u.id,
  u.email,
  iu.username,
  ur.role,
  ur.deleted_at as role_active
FROM auth.users u
LEFT JOIN identity.users iu ON u.id = iu.id
LEFT JOIN identity.user_roles ur ON u.id = ur.user_id
WHERE u.email LIKE '%@liselifoundation.org'
ORDER BY u.email;
```

Expected output should show 3 users with their respective roles.

## Method 2: Supabase CLI

### Prerequisites

- Supabase CLI installed (`npm install -g supabase`)
- Project linked (`supabase link --project-ref YOUR_PROJECT_REF`)

### Step 1: Create Users

```bash
# Admin user
supabase auth users create admin@liselifoundation.org --password Admin123!

# Finance admin user
supabase auth users create finance@liselifoundation.org --password Finance123!

# Employee user
supabase auth users create employee@liselifoundation.org --password Employee123!
```

### Step 2: Get User UUIDs

```bash
# List all users to get their UUIDs
supabase auth users list
```

### Step 3: Create Identity Records and Assign Roles

Use the SQL commands from Method 1, Steps 2 and 3, replacing UUIDs with the values from the CLI output.

## Method 3: Application Signup (Future)

Once the signup flow is implemented in the application:

1. Navigate to the signup page
2. Register each test user with their credentials
3. Manually assign roles via SQL (Step 3 from Method 1)

## Testing the Authentication

### Test Login

1. Start the development server:
   ```bash
   cd packages/web
   npm run dev
   ```

2. Navigate to `http://localhost:5173`

3. You should see the Liseli login page

4. Test each user:
   - **Admin**: Should see Overview, Today's Receipts, and Admin Panel tabs
   - **Finance Admin**: Should see Overview, Today's Receipts, and Admin Panel tabs
   - **Employee**: Should see Overview and Today's Receipts tabs only (no Admin Panel)

### Test Role-Based Access

**As Employee:**
- ✅ Can view Overview page
- ✅ Can view Today's Receipts page
- ✅ Can submit new receipts
- ✅ Can delete own receipts
- ❌ Cannot see Admin Panel tab
- ❌ Cannot approve/reject purchases

**As Admin/Finance Admin:**
- ✅ Can view Overview page
- ✅ Can view Today's Receipts page
- ✅ Can view Admin Panel tab
- ✅ Can approve/reject all purchases
- ✅ Can view all employee receipts

### Test RLS Policies

Once RLS policies are enabled, test that:

1. **Employee** can only see their own receipts in Today's Receipts
2. **Admin** can see all receipts in Admin Panel
3. Unauthorized users cannot access data without authentication

## Troubleshooting

### Issue: User created but can't log in

**Solution**: Ensure the user is confirmed in Supabase Auth:
1. Go to Authentication → Users
2. Find the user
3. Check if email is confirmed
4. If not, click the user and manually confirm

### Issue: User logs in but has no role

**Solution**: Check if role was assigned:
```sql
SELECT * FROM identity.user_roles WHERE user_id = 'USER-UUID-HERE';
```

If no role exists, run the INSERT statement from Step 3.

### Issue: Admin tab not showing for admin user

**Solution**: 
1. Check if role is active:
   ```sql
   SELECT * FROM identity.user_roles 
   WHERE user_id = 'USER-UUID-HERE' AND deleted_at = NULL;
   ```
2. Clear browser cache and localStorage
3. Log out and log back in

### Issue: "User not found" error

**Solution**: Ensure `identity.users` record exists:
```sql
SELECT * FROM identity.users WHERE id = 'USER-UUID-HERE';
```

If missing, run the INSERT statement from Step 2.

## Cleanup

To remove test users:

```sql
-- Remove roles
DELETE FROM identity.user_roles 
WHERE user_id IN (
  SELECT id FROM auth.users WHERE email LIKE '%@liselifoundation.org'
);

-- Remove identity records
DELETE FROM identity.users 
WHERE id IN (
  SELECT id FROM auth.users WHERE email LIKE '%@liselifoundation.org'
);
```

Then delete users from Supabase Dashboard:
1. Go to Authentication → Users
2. Find each test user
3. Click the three dots → Delete user

## Security Notes

⚠️ **IMPORTANT**: 
- These test users should **ONLY** be created in development environments
- **NEVER** use these credentials in production
- Change all passwords before deploying to production
- Consider using environment-specific email domains (e.g., `@dev.liselifoundation.org`)

## Next Steps

After creating test users:

1. Test the complete authentication flow
2. Verify role-based UI rendering
3. Test RLS policies with different user roles
4. Test password reset functionality
5. Test Microsoft OAuth (if configured)

## Reference Files

- SQL Script: `supabase/seed_test_users.sql`
- Auth Context: `packages/web/src/contexts/AuthContext.tsx`
- Login Page: `packages/web/src/components/auth/LoginPage.tsx`
