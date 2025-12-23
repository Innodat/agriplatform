import type { PostgrestError, SupabaseClient } from "@supabase/supabase-js";
import {
  purchaseInsertSchema,
  purchaseRowSchema,
  purchaseUpdateSchema,
  purchaseStatusEnum,
  type PurchaseInsert,
  type PurchaseRow,
  type PurchaseUpdate,
} from "@schemas/finance";

export type PurchaseStatus = "pending" | "approved" | "rejected" | "querying";

export interface PurchaseFilters {
  receiptId?: number;
  userId?: string;
  status?: PurchaseStatus;
  isActive?: boolean;
  capturedOn?: string;
}

function parsePurchaseRows(rows: unknown[]): PurchaseRow[] {
  return rows.map((row) => purchaseRowSchema.parse(row));
}

export async function getPurchases(
  supabase: SupabaseClient,
  filters: PurchaseFilters = {}
): Promise<{ data: PurchaseRow[]; error: PostgrestError | null }> {
  let query = supabase.schema("finance").from("purchase").select("*").order("captured_timestamp", {
    ascending: false,
  });

  if (filters.receiptId) {
    query = query.eq("receipt_id", filters.receiptId);
  }

  if (filters.userId) {
    query = query.eq("user_id", filters.userId);
  }

  if (filters.status) {
    query = query.eq("status", filters.status);
  }

  if (typeof filters.isActive === "boolean") {
    query = query.eq("is_active", filters.isActive);
  }

  if (filters.capturedOn) {
    query = query.gte("captured_timestamp", filters.capturedOn);
  }

  const { data, error } = await query;

  if (error || !data) {
    return { data: [], error };
  }

  return {
    data: parsePurchaseRows(data),
    error: null,
  };
}

export async function createPurchase(
  supabase: SupabaseClient,
  payload: PurchaseInsert
): Promise<{ data: PurchaseRow | null; error: PostgrestError | null }> {
  const validated = purchaseInsertSchema.parse(payload);

  const { data, error } = await supabase
    .schema("finance").from("purchase")
    .insert(validated)
    .select()
    .maybeSingle();

  if (error || !data) {
    return { data: null, error };
  }

  return {
    data: purchaseRowSchema.parse(data),
    error: null,
  };
}

export async function updatePurchase(
  supabase: SupabaseClient,
  payload: PurchaseUpdate
): Promise<{ data: PurchaseRow | null; error: PostgrestError | null }> {
  const validated = purchaseUpdateSchema.parse(payload);

  const { data, error } = await supabase
    .schema("finance").from("purchase")
    .update(validated)
    .eq("id", validated.id)
    .select()
    .maybeSingle();

  if (error || !data) {
    return { data: null, error };
  }

  return {
    data: purchaseRowSchema.parse(data),
    error: null,
  };
}

export async function updatePurchaseStatus(
  supabase: SupabaseClient,
  id: number,
  status: PurchaseStatus
): Promise<{ data: PurchaseRow | null; error: PostgrestError | null }> {
  purchaseStatusEnum.parse(status);

  return updatePurchase(supabase, {
    id,
    status,
  });
}

export async function archivePurchase(
  supabase: SupabaseClient,
  id: number
): Promise<{ data: PurchaseRow | null; error: PostgrestError | null }> {
  return updatePurchase(supabase, {
    id,
    is_active: false,
  });
}
