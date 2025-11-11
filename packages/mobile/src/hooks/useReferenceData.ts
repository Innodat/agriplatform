import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import {
  getCurrencies,
  getExpenseCategories,
  getExpenseTypes,
  type CurrencyRow,
  type ExpenseCategoryRow,
  type ExpenseTypeRow,
} from '@agriplatform/shared';

interface UseReferenceDataResult {
  currencies: CurrencyRow[];
  categories: ExpenseCategoryRow[];
  expenseTypes: ExpenseTypeRow[];
  loading: boolean;
  error: string | null;
}

export function useReferenceData(): UseReferenceDataResult {
  const [currencies, setCurrencies] = useState<CurrencyRow[]>([]);
  const [categories, setCategories] = useState<ExpenseCategoryRow[]>([]);
  const [expenseTypes, setExpenseTypes] = useState<ExpenseTypeRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReferenceData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [currenciesResult, categoriesResult, typesResult] = await Promise.all([
          getCurrencies(supabase),
          getExpenseCategories(supabase),
          getExpenseTypes(supabase),
        ]);

        if (currenciesResult.error) {
          throw new Error(currenciesResult.error.message);
        }
        if (categoriesResult.error) {
          throw new Error(categoriesResult.error.message);
        }
        if (typesResult.error) {
          throw new Error(typesResult.error.message);
        }

        setCurrencies(currenciesResult.data);
        setCategories(categoriesResult.data);
        
        // Enrich expense types with category names
        const enrichedExpenseTypes = typesResult.data.map(type => {
          const category = categoriesResult.data.find(cat => cat.id === type.expense_category_id);
          return {
            ...type,
            categoryName: category?.name || 'Other',
          };
        });
        
        setExpenseTypes(enrichedExpenseTypes as ExpenseTypeRow[]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch reference data');
      } finally {
        console.log("TEst:", currencies)
        setLoading(false);
      }
    };

    fetchReferenceData();
  }, []);

  return {
    currencies,
    categories,
    expenseTypes,
    loading,
    error,
  };
}
