import { useMemo } from "react";
import { useSupabaseQuery } from "../useSupabaseQuery";
import type {
  UseSupabaseQueryOptions,
  UseSupabaseQueryResult,
} from "../useSupabaseQuery";
import {
  getExpenseCategories,
  getExpenseTypes,
  getCurrencies,
} from "../../services/finance/reference.service";
import type {
  ExpenseCategoryRow,
  ExpenseTypeRow,
  CurrencyRow,
} from "../../types/finance";

export function useExpenseCategories(
  options?: UseSupabaseQueryOptions<ExpenseCategoryRow>
): UseSupabaseQueryResult<ExpenseCategoryRow> {
  const queryFn = useMemo(() => () => getExpenseCategories(), []);
  return useSupabaseQuery(queryFn, options);
}

export function useExpenseTypes(
  expenseCategoryId?: number,
  options?: UseSupabaseQueryOptions<ExpenseTypeRow>
): UseSupabaseQueryResult<ExpenseTypeRow> {
  const queryFn = useMemo(
    () => () => getExpenseTypes(expenseCategoryId),
    [expenseCategoryId]
  );
  return useSupabaseQuery(queryFn, options);
}

export function useCurrencies(
  options?: UseSupabaseQueryOptions<CurrencyRow>
): UseSupabaseQueryResult<CurrencyRow> {
  const queryFn = useMemo(() => () => getCurrencies(), []);
  return useSupabaseQuery(queryFn, options);
}
