-- =====================================================
-- Test Users Seed Script
-- =====================================================
-- This script creates test users with different roles for
-- development and testing purposes.
--
-- IMPORTANT: This script should ONLY be run in development
-- environments. DO NOT run in production.
-- =====================================================

-- Note: Supabase Auth handles password hashing automatically
-- when users are created through the auth.users table.
-- For manual insertion, we need to use the auth admin API
-- or create users through the Supabase dashboard.

-- This script provides the SQL structure for reference.
-- Actual user creation should be done via:
-- 1. Supabase Dashboard (Authentication → Users → Add User)
-- 2. Supabase CLI: supabase auth users create
-- 3. Application signup flow

-- =====================================================
-- Test User Credentials (for manual creation)
-- =====================================================
-- 
-- Admin User:
--   Email: admin@liseli.org
--   Password: Admin123!
--   Role: admin
--
-- Finance Admin User:
--   Email: finance@liseli.org
--   Password: Finance123!
--   Role: financeadmin
--
-- Employee User:
--   Email: employee@liseli.org
--   Password: Employee123!
--   Role: employee
--
-- =====================================================

-- =====================================================
-- Step 1: Create users in auth.users (via Dashboard/CLI)
-- =====================================================
-- After creating users via Dashboard or CLI, their UUIDs
-- will be automatically generated. Use those UUIDs below.

-- =====================================================
-- Step 2: Create identity.users records
-- =====================================================
-- Replace the UUIDs below with actual UUIDs from auth.users

-- Example (replace UUIDs with actual values):
/*
INSERT INTO identity.users (id, username, is_active, is_system)
VALUES 
  ('REPLACE-WITH-ADMIN-UUID', 'Admin User', true, false),
  ('REPLACE-WITH-FINANCE-UUID', 'Finance Admin', true, false),
  ('REPLACE-WITH-EMPLOYEE-UUID', 'Employee User', true, false);
*/

-- =====================================================
-- Step 3: Assign roles to users
-- =====================================================
-- Replace the UUIDs below with actual UUIDs from auth.users

-- Example (replace UUIDs with actual values):
/*
INSERT INTO identity.user_roles (user_id, role, is_active)
VALUES 
  ('REPLACE-WITH-ADMIN-UUID', 'admin', true),
  ('REPLACE-WITH-FINANCE-UUID', 'financeadmin', true),
  ('REPLACE-WITH-EMPLOYEE-UUID', 'employee', true);
*/

-- =====================================================
-- Verification Queries
-- =====================================================
-- After creating users, run these queries to verify:

-- Check auth.users
-- SELECT id, email, created_at FROM auth.users WHERE email LIKE '%@liseli.org';

-- Check identity.users
-- SELECT id, username, is_active FROM identity.users;

-- Check user_roles
-- SELECT ur.user_id, u.username, ur.role, ur.is_active
-- FROM identity.user_roles ur
-- JOIN identity.users u ON ur.user_id = u.id;

-- =====================================================
-- Cleanup (if needed)
-- =====================================================
-- To remove test users:
/*
DELETE FROM identity.user_roles WHERE user_id IN (
  SELECT id FROM auth.users WHERE email LIKE '%@liseli.org'
);

DELETE FROM identity.users WHERE id IN (
  SELECT id FROM auth.users WHERE email LIKE '%@liseli.org'
);

-- Note: Deleting from auth.users should be done via Supabase Dashboard
-- or auth admin API to ensure proper cleanup
*/
