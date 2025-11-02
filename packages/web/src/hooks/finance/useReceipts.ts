import { useCallback, useMemo } from "react";
import type {
  UseSupabaseQueryOptions,
  UseSupabaseQueryResult,
} from "../useSupabaseQuery";
import { useSupabaseQuery } from "../useSupabaseQuery";
import { getReceipts } from "../../services/finance/receipt.service";
import type { ReceiptFilters } from "../../services/finance/receipt.service";
import type { ReceiptRow } from "../../types/finance";

function normalizeFilters(filters?: ReceiptFilters): ReceiptFilters | undefined {
  if (!filters) {
    return undefined;
  }

  return {
    ...filters,
    supplier: filters.supplier ?? undefined,
    isActive:
      typeof filters.isActive === "boolean" ? filters.isActive : undefined,
    createdAfter: filters.createdAfter ?? undefined,
    createdBefore: filters.createdBefore ?? undefined,
  };
}

export function useReceipts(
  filters?: ReceiptFilters,
  options?: UseSupabaseQueryOptions<ReceiptRow>
): UseSupabaseQueryResult<ReceiptRow> {
  const normalizedFilters = useMemo(
    () => normalizeFilters(filters),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [JSON.stringify(filters ?? {})]
  );

  const queryFn = useCallback(
    () => getReceipts(normalizedFilters ?? {}),
    [normalizedFilters]
  );

  return useSupabaseQuery(queryFn, options);
}
