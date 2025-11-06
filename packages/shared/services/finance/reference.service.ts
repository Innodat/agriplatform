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
  console.log("gc_test", data, error)
  if (error || !data) {
    console.log("WHY")
    return { data: [], error };
  }
  console.log("PARSING!")
  
  const results = data.map((row) => currencyRowSchema.safeParse(row));

  results.forEach((res, i) => {
    if (!res.success) {
      console.log(`Row ${i} failed:`, res.error.format())
      console.error(`Row ${i} failed:`, res.error.format());
    }
  });
  console.log("PARSED!", results)

  var currency_list = data.map((row) => currencyRowSchema.parse(row))
  console.log("get_currencies", currency_list)

  return { data: parseCurrencies(data), error: null };
}
