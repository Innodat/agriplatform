import { useCallback, useEffect, useState } from "react";
import type { PostgrestError, SupabaseClient } from "@supabase/supabase-js";
import { supabase } from "../lib/supabase/client";

type QueryFn<T> = (
  client: SupabaseClient
) => PromiseLike<{ data: T[] | null; error: PostgrestError | null }>;

export interface UseSupabaseQueryOptions<T> {
  enabled?: boolean;
  initialData?: T[];
  onError?: (error: Error) => void;
}

export interface UseSupabaseQueryResult<T> {
  data: T[];
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useSupabaseQuery<T>(
  queryFn: QueryFn<T>,
  options: UseSupabaseQueryOptions<T> = {}
): UseSupabaseQueryResult<T> {
  const { enabled = true, initialData = [], onError } = options;

  const [data, setData] = useState<T[]>(initialData);
  const [loading, setLoading] = useState(enabled);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    if (!enabled) return;

    setLoading(true);
    setError(null);

    try {
      const { data: result, error: queryError } = await queryFn(supabase);

      if (queryError) {
        throw queryError;
      }

      setData(result ?? []);
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Unknown error");
      setError(error);
      onError?.(error);
    } finally {
      setLoading(false);
    }
  }, [enabled, onError, queryFn]);

  useEffect(() => {
    void fetchData();
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    refetch: fetchData,
  };
}
