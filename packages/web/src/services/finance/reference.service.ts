import type { PostgrestError } from "@supabase/supabase-js";
import { supabase } from "../../lib/supabase/client";
import {
  expenseCategoryRowSchema,
  expenseTypeRowSchema,
  currencyRowSchema,
} from "@shared/schemas/zod/finance";
import type {
  ExpenseCategoryRow,
  ExpenseTypeRow,
  CurrencyRow,
} from "../../types/finance";

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

export async function getExpenseCategories(): Promise<{
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

export async function getCurrencies(): Promise<{
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
