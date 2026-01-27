import type { PostgrestError } from "@supabase/supabase-js";
import { supabase } from "../../lib/supabase/client";
import {
  purchaseInsertSchema,
  purchaseRowSchema,
  purchaseUpdateSchema,
} from "@shared/schemas/zod/finance";
import type {
  PurchaseInsert,
  PurchaseRow,
  PurchaseUpdate,
} from "../../types/finance";

export interface PurchaseFilters {
  receiptId?: number;
  userId?: string;
  isActive?: boolean;
  capturedOn?: string;
}

function parsePurchaseRows(rows: unknown[]): PurchaseRow[] {
  return rows.map((row) => purchaseRowSchema.parse(row));
}

export async function getPurchases(
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

export async function archivePurchase(
  id: number
): Promise<{ data: PurchaseRow | null; error: PostgrestError | null }> {
  return updatePurchase({
    id,
    is_active: false,
  });
}
