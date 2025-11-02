import type { PostgrestError, SupabaseClient } from "@supabase/supabase-js";
import {
  expenseCategoryRowSchema,
  expenseTypeRowSchema,
  currencyRowSchema,
  type ExpenseCategoryRow,
  type ExpenseTypeRow,
  type CurrencyRow,
} from "../../schemas/zod/finance";

export type ReferenceDataType = "categories" | "types" | "currencies";

function parseExpenseCategories(rows: unknown[]): ExpenseCategoryRow[] {
  return rows.map((row) => expenseCategoryRowSchema.parse(row));
}

function parseExpenseTypes(rows: unknown[]): ExpenseTypeRow[] {
  return rows.map((row) => expenseTypeRowSchema.parse(row));
}

function parseCurrencies(rows: unknown[]): CurrencyRow[] {
  return rows.map((row) => currencyRowSchema.parse(row));
}

export async function getExpenseCategories(
  supabase: SupabaseClient
): Promise<{
  data: ExpenseCategoryRow[];
  error: PostgrestError | null;
}> {
  const { data, error } = await supabase
    .schema("finance").from("expense_category")
    .select("*")
    .eq("is_active", true)
    .order("name", { ascending: true });

  if (error || !data) {
    return { data: [], error };
  }

  return { data: parseExpenseCategories(data), error: null };
}

export async function getExpenseTypes(
  supabase: SupabaseClient,
  categoryId?: number
): Promise<{ data: ExpenseTypeRow[]; error: PostgrestError | null }> {
  let query = supabase
    .schema("finance").from("expense_type")
    .select("*")
    .eq("is_active", true)
    .order("name", { ascending: true });

  if (categoryId) {
    query = query.eq("expense_category_id", categoryId);
  }

  const { data, error } = await query;

  if (error || !data) {
    return { data: [], error };
  }

  return { data: parseExpenseTypes(data), error: null };
}

export async function getCurrencies(
  supabase: SupabaseClient
): Promise<{
  data: CurrencyRow[];
  error: PostgrestError | null;
}> {
  const { data, error } = await supabase
    .schema("finance").from("currency")
    .select("*")
    .eq("is_active", true)
    .order("name", { ascending: true });

  if (error || !data) {
    return { data: [], error };
  }

  return { data: parseCurrencies(data), error: null };
}
