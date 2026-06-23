import { useState, useEffect, useCallback } from 'react';
import { supabase } from '../lib/supabase';
import { getReceipts } from '@agriplatform/shared';
import { ReceiptWithTotal } from '../types/receipt';

interface UseReceiptsResult {
  receipts: ReceiptWithTotal[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  loadMore: () => Promise<void>;
  hasMore: boolean;
}

const ITEMS_PER_PAGE = 20;

export function useReceipts(): UseReceiptsResult {
  const [receipts, setReceipts] = useState<ReceiptWithTotal[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);

  const fetchReceipts = useCallback(async (pageNum: number, append: boolean = false) => {
    try {
      if (!append) {
        setLoading(true);
      }
      setError(null);

      const { data, error: fetchError } = await getReceipts(supabase as any);

      if (fetchError) {
        throw new Error(fetchError.message);
      }

      // Fetch purchases for all receipts to calculate totals
      const { data: purchases, error: purchasesError } = await supabase
        .schema('finance')
        .from('purchase_read')
        .select('receipt_id, amount, currency:currency_id(symbol)')
        .in('receipt_id', data.map(r => r.id));

      if (purchasesError) {
        throw new Error(purchasesError.message);
      }

      // Enrich receipts with total amounts
      const enrichedReceipts: ReceiptWithTotal[] = data.map(receipt => {
        const receiptPurchases = purchases?.filter(p => p.receipt_id === receipt.id) || [];
        const totalAmount = receiptPurchases.reduce((sum, p) => sum + Number(p.amount), 0);
        const currencyData = receiptPurchases[0]?.currency as any;
        const currency = currencyData?.symbol || '₹';

        return {
          ...receipt,
          totalAmount,
          currency,
        };
      });

      // Sort by date (newest first)
      const sortedReceipts = enrichedReceipts.sort((a, b) => {
        const dateA = a.receipt_date || '';
        const dateB = b.receipt_date || '';
        return new Date(dateB).getTime() - new Date(dateA).getTime();
      });

      // Implement pagination
      const start = pageNum * ITEMS_PER_PAGE;
      const end = start + ITEMS_PER_PAGE;
      const paginatedReceipts = sortedReceipts.slice(start, end);

      if (append) {
        setReceipts(prev => [...prev, ...paginatedReceipts]);
      } else {
        setReceipts(paginatedReceipts);
      }

      setHasMore(end < sortedReceipts.length);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch receipts');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchReceipts(0);
  }, [fetchReceipts]);

  const refresh = useCallback(async () => {
    setRefreshing(true);
    setPage(0);
    await fetchReceipts(0);
  }, [fetchReceipts]);

  const loadMore = useCallback(async () => {
    if (!loading && hasMore) {
      const nextPage = page + 1;
      setPage(nextPage);
      await fetchReceipts(nextPage, true);
    }
  }, [loading, hasMore, page, fetchReceipts]);

  return {
    receipts,
    loading: loading && !refreshing,
    error,
    refresh,
    loadMore,
    hasMore,
  };
}
