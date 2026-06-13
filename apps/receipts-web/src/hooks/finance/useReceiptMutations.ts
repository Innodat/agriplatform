import { useState } from "react";
import type { PostgrestError } from "@supabase/supabase-js";
import {
  createReceipt,
  updateReceipt,
  archiveReceipt,
  type ReceiptFilters,
} from "../../services/finance/receipt.service";
import type {
  ReceiptInsert,
  ReceiptRow,
  ReceiptUpdate,
} from "../../types/finance";

export interface UseReceiptMutationsResult {
  loading: boolean;
  error: Error | null;
  create: (payload: ReceiptInsert) => Promise<ReceiptRow | null>;
  update: (payload: ReceiptUpdate) => Promise<ReceiptRow | null>;
  archive: (id: number) => Promise<ReceiptRow | null>;
  lastFilters?: ReceiptFilters;
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

export function useReceiptMutations(
  lastFilters?: ReceiptFilters
): UseReceiptMutationsResult {
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
      execute(() => createReceipt(payload)),
    update: (payload) =>
      execute(() => updateReceipt(payload)),
    archive: (id) => execute(() => archiveReceipt(id)),
  };
}
