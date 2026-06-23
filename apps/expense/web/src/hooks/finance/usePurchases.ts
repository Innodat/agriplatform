import { useCallback, useMemo } from "react";
import type {
  UseSupabaseQueryOptions,
  UseSupabaseQueryResult,
} from "../useSupabaseQuery";
import { useSupabaseQuery } from "../useSupabaseQuery";
import { getPurchases } from "../../services/finance/purchase.service";
import type { PurchaseFilters } from "../../services/finance/purchase.service";
import type { PurchaseRow } from "../../types/finance";

function normalizeFilters(filters?: PurchaseFilters): PurchaseFilters | undefined {
  if (!filters) {
    return undefined;
  }

  return {
    ...filters,
    receiptId: filters.receiptId ?? undefined,
    userId: filters.userId ?? undefined,
    isActive:
      typeof filters.isActive === "boolean" ? filters.isActive : undefined,
    capturedOn: filters.capturedOn ?? undefined,
  };
}

export function usePurchases(
  filters?: PurchaseFilters,
  options?: UseSupabaseQueryOptions<PurchaseRow>
): UseSupabaseQueryResult<PurchaseRow> {
  const normalizedFilters = useMemo(
    () => normalizeFilters(filters),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [JSON.stringify(filters ?? {})]
  );

  const queryFn = useCallback(
    () => getPurchases(normalizedFilters ?? {}),
    [normalizedFilters]
  );

  return useSupabaseQuery(queryFn, options);
}
