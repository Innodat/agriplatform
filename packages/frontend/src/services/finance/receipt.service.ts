import type { PostgrestError } from "@supabase/supabase-js";
import { supabase } from "../../lib/supabase/client";
import {
  receiptInsertSchema,
  receiptRowSchema,
  receiptUpdateSchema,
} from "@shared/schemas/zod/finance";
import type {
  ReceiptInsert,
  ReceiptRow,
  ReceiptUpdate,
} from "../../types/finance";

export interface ReceiptFilters {
  supplier?: string;
  isActive?: boolean;
  createdAfter?: string;
  createdBefore?: string;
}

export type ReceiptWithPurchases = ReceiptRow & {
  purchases: unknown[];
};

function parseReceiptRows(rows: unknown[]): ReceiptRow[] {
  return rows.map((row) => receiptRowSchema.parse(row));
}

export async function getReceipts(
  filters: ReceiptFilters = {}
): Promise<{ data: ReceiptRow[]; error: PostgrestError | null }> {
  let query = supabase.from("receipt").select("*").order("created_at", {
    ascending: false,
  });

  if (filters.supplier) {
    query = query.ilike("supplier", `%${filters.supplier}%`);
  }

  if (typeof filters.isActive === "boolean") {
    query = query.eq("is_active", filters.isActive);
  }

  if (filters.createdAfter) {
    query = query.gte("created_at", filters.createdAfter);
  }

  if (filters.createdBefore) {
    query = query.lte("created_at", filters.createdBefore);
  }

  const { data, error } = await query;

  if (error || !data) {
    return { data: [], error };
  }

  return {
    data: parseReceiptRows(data),
    error: null,
  };
}

export async function getReceiptById(
  id: number
): Promise<{ data: ReceiptWithPurchases | null; error: PostgrestError | null }> {
  const { data, error } = await supabase
    .from("receipt")
    .select("*, purchases(*)")
    .eq("id", id)
    .maybeSingle();

  if (error || !data) {
    return { data: null, error };
  }

  return {
    data: {
      ...receiptRowSchema.parse(data),
      purchases: Array.isArray(data.purchases) ? data.purchases : [],
    },
    error: null,
  };
}

export async function createReceipt(
  payload: ReceiptInsert
): Promise<{ data: ReceiptRow | null; error: PostgrestError | null }> {
  const validated = receiptInsertSchema.parse(payload);

  const { data, error } = await supabase
    .from("receipt")
    .insert(validated)
    .select()
    .maybeSingle();

  if (error || !data) {
    return { data: null, error };
  }

  return {
    data: receiptRowSchema.parse(data),
    error: null,
  };
}

export async function updateReceipt(
  payload: ReceiptUpdate
): Promise<{ data: ReceiptRow | null; error: PostgrestError | null }> {
  const validated = receiptUpdateSchema.parse(payload);

  const { data, error } = await supabase
    .from("receipt")
    .update(validated)
    .eq("id", validated.id)
    .select()
    .maybeSingle();

  if (error || !data) {
    return { data: null, error };
  }

  return {
    data: receiptRowSchema.parse(data),
    error: null,
  };
}

export async function archiveReceipt(
  id: number
): Promise<{ data: ReceiptRow | null; error: PostgrestError | null }> {
  return updateReceipt({
    id,
    is_active: false,
  });
}
