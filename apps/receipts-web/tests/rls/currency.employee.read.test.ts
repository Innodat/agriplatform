// tests/rls/currency.employee.read.test.ts
import { beforeAll, afterAll, describe, it, expect } from 'vitest';
import { createClient, type SupabaseClient } from '@supabase/supabase-js';

const url = process.env.SUPABASE_URL!;
const anon = process.env.SUPABASE_PUBLISHABLE_KEY!;
const service = process.env.SUPABASE_SECRET_KEY!;
const EMAIL = process.env.TEST_USER_EMAIL!;
const PASS  = process.env.TEST_USER_PASSWORD!;

let serviceClient: SupabaseClient;
let userClient: SupabaseClient;

beforeAll(async () => {
  serviceClient = createClient(url, service, { auth: { persistSession: false } });
  userClient    = createClient(url, anon,    { auth: { persistSession: false } });

  // 1) Ensure user exists with expected role in JWT
  await serviceClient.auth.admin.createUser({
    email: EMAIL,
    password: PASS,
    email_confirm: true,
    // In your tokens, user_role is top-level; setting app_metadata.user_role often mirrors to top-level
    app_metadata: { user_role: 'employee' },
  }).catch(() => { /* OK if already exists */ });

  // 2) Sign in as employee
  const { error: loginErr } = await userClient.auth.signInWithPassword({ email: EMAIL, password: PASS });
  if (loginErr) throw loginErr;

  // 3) Seed some currencies via service (bypass RLS)
  await serviceClient.from('finance.currency').insert([
    { name: 'USD', description: 'US Dollar', symbol: '$', deleted_at: null },
    { name: 'EUR', description: 'Euro',      symbol: '€', deleted_at: null },
    { name: 'ZAR', description: 'Rand',      symbol: 'R', deleted_at: new Date().toISOString() },
  ]).throwOnError();
});

afterAll(async () => {
  await serviceClient.from('finance.currency').delete().neq('id', -1);
  const { data: list } = await serviceClient.auth.admin.listUsers();
  const u = list?.users?.find(x => x.email === EMAIL);
  if (u) await serviceClient.auth.admin.deleteUser(u.id).catch(() => {});
});

describe('finance.currency — employee read behavior', () => {
  it('debugs RBAC with identity.debug_authorize', async () => {
    const { data, error } = await userClient
      .rpc('identity.debug_authorize', { requested_permission: 'finance.currency.read' });

    expect(error).toBeNull();
    expect(data).toBeTruthy();

    // If multiple rows ever appear, use data[0]
    const row = Array.isArray(data) ? data[0] : data;

    // Useful diagnostics
    // console.log('debug_authorize:', row);

    // Expectations
    expect(row.supa_role).toBe('authenticated');       // must be authenticated
    expect(row.jwt_role).toBe('employee');             // from your token sample
    expect(row.can).toBe(true);                        // authorize('finance.currency.read') should be TRUE
    expect(row.raw_jwt).toBeTruthy();                  // optional: inspect claim placement during a failure
  });

  it('selects currencies for employee (per policy)', async () => {
    const { data, error } = await userClient
      .from('finance.currency')
      .select('id, name, deleted_at')
      .order('id', { ascending: true });

    // If there's a failure, this message helps distinguish GRANT issues vs. RLS
    if (error) {
      // Helpful triage output for test runner
      // eslint-disable-next-line no-console
      console.error('currency select error:', error);
    }

    expect(error).toBeNull();            // should succeed after grants + correct authorize resolution
    expect(Array.isArray(data)).toBe(true);
    expect(data!.length).toBeGreaterThanOrEqual(2); // all seeded active rows (USD, EUR)
  });
});