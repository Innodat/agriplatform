import type { PostgrestError, SupabaseClient } from "@supabase/supabase-js";
import {
  receiptInsertSchema,
  receiptRowSchema,
  receiptUpdateSchema,
  type ReceiptInsert,
  type ReceiptRow,
  type ReceiptUpdate,
} from "../../";

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
  return rows.map((row, index) => {
      console.log("Parse", index, row);
      const result = receiptRowSchema.safeParse(row);
      if (!result.success) {
        console.error(`❌ Receipt row at index ${index} failed validation:`);
        console.error(JSON.stringify(result.error.format(), null, 2));
        throw result.error;
      }
      return result.data;
  });
}

export async function getReceipts(
  supabase: SupabaseClient,
  filters: ReceiptFilters = {}
): Promise<{ data: ReceiptRow[]; error: PostgrestError | null }> {
  let query = supabase.schema("finance").from("receipt").select("*").order("created_at", {
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
  console.log("Receipts", data)
  if (error || !data) {
    console.error("Error retrieving the receipts", error)
    return { data: [], error };
  }

  return {
    data: parseReceiptRows(data),
    error: null,
  };
}

export async function getReceiptById(
  supabase: SupabaseClient,
  id: number
): Promise<{ data: ReceiptWithPurchases | null; error: PostgrestError | null }> {
  const { data, error } = await supabase
    .schema("finance").from("receipt")
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
  supabase: SupabaseClient,
  payload: ReceiptInsert
): Promise<{ data: ReceiptRow | null; error: PostgrestError | null }> {
  const validated = receiptInsertSchema.parse(payload);

  const { data, error } = await supabase
    .schema("finance").from("receipt")
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
  supabase: SupabaseClient,
  payload: ReceiptUpdate
): Promise<{ data: ReceiptRow | null; error: PostgrestError | null }> {
  const validated = receiptUpdateSchema.parse(payload);

  const { data, error } = await supabase
    .schema("finance").from("receipt")
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
  supabase: SupabaseClient,
  id: number
): Promise<{ data: ReceiptRow | null; error: PostgrestError | null }> {
  return updateReceipt(supabase, {
    id,
    is_active: false,
  });
}
