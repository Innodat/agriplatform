import { beforeAll, afterAll, describe, it, expect } from 'vitest';
import { createClient, type SupabaseClient } from '@supabase/supabase-js';

const url = process.env.SUPABASE_URL!;
const anon = process.env.SUPABASE_PUBLISHABLE_KEY!;
const service = process.env.SUPABASE_SECRET_KEY!;

const EMP_EMAIL = process.env.TEST_USER_EMAIL!;              // e.g., employee@...
const EMP_PASS  = process.env.TEST_USER_PASSWORD!;           // e.g., SuperSecret123!

const ADM_EMAIL = process.env.TEST_ADMIN_EMAIL ?? 'fa@test.local';
const ADM_PASS  = process.env.TEST_ADMIN_PASSWORD ?? 'AdminSecret123!';

const OTHER_EMAIL = process.env.TEST_OTHER_EMAIL ?? 'other@test.local';
const OTHER_PASS  = process.env.TEST_OTHER_PASSWORD ?? 'OtherSecret123!';

let serviceClient: SupabaseClient;
let employeeClient: SupabaseClient;
let adminClient: SupabaseClient;

let employeeId: string;
let adminId: string;
let otherId: string;

let employeeReceiptId: number;
let otherReceiptId: number;

beforeAll(async () => {
  serviceClient  = createClient(url, service, { auth: { persistSession: false } });
  employeeClient = createClient(url, anon,    { auth: { persistSession: false } });
  adminClient    = createClient(url, anon,    { auth: { persistSession: false } });

  // 1) Create users with roles (JWT must carry `user_role`)
  await serviceClient.auth.admin.createUser({
    email: EMP_EMAIL,
    password: EMP_PASS,
    email_confirm: true,
    app_metadata: { user_role: 'employee' },
  }).catch(() => {});

  await serviceClient.auth.admin.createUser({
    email: ADM_EMAIL,
    password: ADM_PASS,
    email_confirm: true,
    app_metadata: { user_role: 'financeadmin' },
  }).catch(() => {});

  await serviceClient.auth.admin.createUser({
    email: OTHER_EMAIL,
    password: OTHER_PASS,
    email_confirm: true,
    app_metadata: { user_role: 'employee' },
  }).catch(() => {});

  // 2) Sign in to resolve auth UIDs
  const eLogin = await employeeClient.auth.signInWithPassword({ email: EMP_EMAIL,  password: EMP_PASS });
  if (eLogin.error) throw eLogin.error;
  const aLogin = await adminClient.auth.signInWithPassword({ email: ADM_EMAIL, password: ADM_PASS });
  if (aLogin.error) throw aLogin.error;

  const eUser = await employeeClient.auth.getUser();
  const aUser = await adminClient.auth.getUser();

  if (!eUser.data.user || !aUser.data.user) throw new Error('Failed to resolve users after sign-in');

  employeeId = eUser.data.user.id;
  adminId    = aUser.data.user.id;

  // For "other" create a throwaway client to fetch id
  const otherClient = createClient(url, anon, { auth: { persistSession: false } });
  const oLogin = await otherClient.auth.signInWithPassword({ email: OTHER_EMAIL, password: OTHER_PASS });
  if (oLogin.error) throw oLogin.error;
  const oUser = await otherClient.auth.getUser();
  if (!oUser.data.user) throw new Error('Failed to resolve OTHER after sign-in');
  otherId = oUser.data.user.id;

  // 3) identity.users rows to satisfy FK (created_by references identity.users.id)
  await serviceClient.from('identity.users').upsert({ id: employeeId, username: 'employee' }).throwOnError();
  await serviceClient.from('identity.users').upsert({ id: adminId,    username: 'financeadmin' }).throwOnError();
  await serviceClient.from('identity.users').upsert({ id: otherId,    username: 'other' }).throwOnError();

  // 4) Seed receipts (via service; bypass RLS)
  const empSeed = await serviceClient
    .from('finance.receipt')
    .insert({ supplier: 'Emp Supplier', created_by: employeeId })
    .select('id')
    .single();
  if (empSeed.error) throw empSeed.error;
  employeeReceiptId = empSeed.data.id;

  const otherSeed = await serviceClient
    .from('finance.receipt')
    .insert({ supplier: 'Other Supplier', created_by: otherId })
    .select('id')
    .single();
  if (otherSeed.error) throw otherSeed.error;
  otherReceiptId = otherSeed.data.id;
});

afterAll(async () => {
  // Clean up receipts
  await serviceClient.from('finance.receipt').delete().neq('id', -1);

  // Clean up identity.users rows (optional)
  await serviceClient.from('identity.users').delete().in('id', [employeeId, adminId, otherId]).catch(() => {});

  // Clean up users
  const users = await serviceClient.auth.admin.listUsers();
  const idsToDelete = [EMP_EMAIL, ADM_EMAIL, OTHER_EMAIL]
    .map(e => users.data?.users?.find(u => u.email === e)?.id)
    .filter(Boolean) as string[];

  for (const uid of idsToDelete) {
    await serviceClient.auth.admin.deleteUser(uid).catch(() => {});
  }
});

describe('RLS: finance.receipt — employee behavior', () => {
  it('employee can SELECT only their own receipts', async () => {
    const { data, error } = await employeeClient
      .from('finance.receipt')
      .select('id, supplier, created_by')
      .order('id', { ascending: true });

    expect(error).toBeNull();
    expect(Array.isArray(data)).toBe(true);
    expect(data!.length).toBeGreaterThanOrEqual(1);
    // Ensure no foreign receipts leak through RLS
    expect(data!.every(r => r.created_by === employeeId)).toBe(true);

    // Direct select on another user’s row should return 0 rows (RLS filter), not error
    const single = await employeeClient
      .from('finance.receipt')
      .select('id, created_by')
      .eq('id', otherReceiptId);

    expect(single.error).toBeNull();
    expect(single.data?.length ?? 0).toBe(0);
  });

  it('employee can INSERT only with created_by = self', async () => {
    const ok = await employeeClient
      .from('finance.receipt')
      .insert({ supplier: 'Emp Insert OK', created_by: employeeId })
      .select('id, created_by')
      .single();

    expect(ok.error).toBeNull();
    expect(ok.data?.created_by).toBe(employeeId);

    const bad = await employeeClient
      .from('finance.receipt')
      .insert({ supplier: 'Emp Insert BAD', created_by: otherId })
      .select('id');

    expect(bad.error).toBeTruthy();
  });

  it('employee can UPDATE own receipt and cannot UPDATE others', async () => {
    // Update own
    const upOwn = await employeeClient
      .from('finance.receipt')
      .update({ supplier: 'Emp Updated' })
      .eq('id', employeeReceiptId)
      .select('supplier')
      .single();

    expect(upOwn.error).toBeNull();
    expect(upOwn.data?.supplier).toBe('Emp Updated');

    // Update other (without changing created_by) must fail via WITH CHECK
    const upOther = await employeeClient
      .from('finance.receipt')
      .update({ supplier: 'Should Not Update' })
      .eq('id', otherReceiptId);

    expect(upOther.error).toBeTruthy();
  });

  it('employee can SOFT DELETE own receipt (set deleted_at), cannot soft delete others', async () => {
    const softOwn = await employeeClient
      .from('finance.receipt')
      .update({ deleted_at: new Date().toISOString() })
      .eq('id', employeeReceiptId)
      .select('deleted_at')
      .single();

    expect(softOwn.error).toBeNull();
    expect(softOwn.data?.deleted_at).toBeTruthy();

    const softOther = await employeeClient
      .from('finance.receipt')
      .update({ deleted_at: new Date().toISOString() })
      .eq('id', otherReceiptId);

    expect(softOther.error).toBeTruthy();
  });

  it.todo('guardrail: employee must NOT be able to "take over" another user\'s row by updating created_by to self', async () => {
    /**
     * This test documents a potential gap:
     * - Your UPDATE policies only set WITH CHECK (no USING).
     * - WITH CHECK validates the *new* row.
     * - If a user updates another row AND sets created_by to themselves,
     *   the WITH CHECK may pass, allowing a row takeover.
     *
     * To harden: add a USING clause limiting which rows are updatable:
     *
     *   create policy "Allow update for self or admin"
     *   on finance.receipt for update
     *   using ((created_by = auth.uid()) or identity.authorize('finance.receipt.admin'))
     *   with check (
     *     ((created_by = auth.uid()) and deleted_at IS NULL)
     *     or (identity.authorize('finance.receipt.admin') and deleted_at IS NULL)
     *   );
     *
     *   -- And same pattern for your "soft delete" update policy (USING with created_by check).
     */
  });
});

describe('RLS: finance.receipt — financeadmin behavior', () => {
  it('financeadmin can SELECT all receipts', async () => {
    const { data, error } = await adminClient
      .from('finance.receipt')
      .select('id, created_by')
      .order('id', { ascending: true });

    expect(error).toBeNull();
    expect(Array.isArray(data)).toBe(true);
    // Should include both employee and other receipts
    const ids = (data ?? []).map(r => r.id);
    expect(ids).toEqual(expect.arrayContaining([employeeReceiptId, otherReceiptId]));
  });

  it('financeadmin can UPDATE any receipt', async () => {
    const upOther = await adminClient
      .from('finance.receipt')
      .update({ supplier: 'Admin Updated' })
      .eq('id', otherReceiptId)
      .select('supplier')
      .single();

    expect(upOther.error).toBeNull();
    expect(upOther.data?.supplier).toBe('Admin Updated');
  });

  it('financeadmin can SOFT DELETE any receipt', async () => {
    const softOther = await adminClient
      .from('finance.receipt')
      .update({ deleted_at: new Date().toISOString() })
      .eq('id', otherReceiptId)
      .select('deleted_at')
      .single();

    expect(softOther.error).toBeNull();
    expect(softOther.data?.deleted_at).toBeTruthy();
  });
});