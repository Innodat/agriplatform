import { useState } from "react";
import type { PostgrestError } from "@supabase/supabase-js";
import {
  createPurchase,
  updatePurchase,
  archivePurchase,
  type PurchaseFilters,
} from "../../services/finance/purchase.service";
import type {
  PurchaseInsert,
  PurchaseRow,
  PurchaseUpdate,
} from "../../types/finance";

export interface UsePurchaseMutationsResult {
  loading: boolean;
  error: Error | null;
  create: (payload: PurchaseInsert) => Promise<PurchaseRow | null>;
  update: (payload: PurchaseUpdate) => Promise<PurchaseRow | null>;
  archive: (id: number) => Promise<PurchaseRow | null>;
  lastFilters?: PurchaseFilters;
}

function toError(err: unknown): Error {
  if (err instanceof Error) return err;
  if (typeof err === "string") return new Error(err);
  return new Error("Unknown error");
}

function handlePostgrestError(error: PostgrestError | null): void {
  if (error) {
    throw new Error(error.message);
  }
}

export function usePurchaseMutations(
  lastFilters?: PurchaseFilters
): UsePurchaseMutationsResult {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  async function execute<T>(fn: () => Promise<{ data: T; error: PostgrestError | null }>): Promise<T | null> {
    setLoading(true);
    setError(null);

    try {
      const { data, error } = await fn();
      handlePostgrestError(error);
      return data;
    } catch (err) {
      const normalized = toError(err);
      setError(normalized);
      return null;
    } finally {
      setLoading(false);
    }
  }

  return {
    loading,
    error,
    lastFilters,
    create: (payload) =>
      execute(() => createPurchase(payload)),
    update: (payload) =>
      execute(() => updatePurchase(payload)),
    archive: (id) =>
      execute(() => archivePurchase(id)),
  };
}
