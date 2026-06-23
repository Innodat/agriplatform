import { useMemo } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { useReceipts } from "@/hooks/finance/useReceipts";
import { usePurchases } from "@/hooks/finance/usePurchases";
import {
  useExpenseTypes,
  useCurrencies,
} from "@/hooks/finance/useReferenceData";
import { StatusBadge } from "../components/StatusBadge";

const fallbackCurrencyFormatter = new Intl.NumberFormat(undefined, {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 2,
});

const capturedFormatter = new Intl.DateTimeFormat(undefined, {
  year: "numeric",
  month: "short",
  day: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

export function OverviewPage() {
  const {
    data: receipts,
    loading: receiptsLoading,
    error: receiptsError,
  } = useReceipts({ isActive: true });

  const {
    data: purchases,
    loading: purchasesLoading,
    error: purchasesError,
  } = usePurchases({ isActive: true });

  const { data: expenseTypes } = useExpenseTypes(undefined, {
    enabled: !purchasesLoading,
  });

  const { data: currencies } = useCurrencies({
    enabled: !purchasesLoading,
  });

  const expenseTypeMap = useMemo(() => {
    const map = new Map<number, string>();
    expenseTypes.forEach((type) => {
      map.set(type.id, type.name);
    });
    return map;
  }, [expenseTypes]);

  const currencyMap = useMemo(() => {
    const map = new Map<number, string>();
    currencies.forEach((currency) => {
      map.set(currency.id, currency.symbol ?? currency.name);
    });
    return map;
  }, [currencies]);

  const stats = useMemo(() => {
    if (!purchases.length) {
      return {
        totalReceipts: receipts.length,
        totalAmount: 0,
        pending: 0,
        employees: 0,
      };
    }

    const totalAmount = purchases.reduce(
      (sum, purchase) => sum + purchase.amount,
      0
    );
    const pending = purchases.filter(
      (purchase) => purchase.status === "pending"
    ).length;
    const employees = new Set(
      purchases.map((purchase) => purchase.user_id).filter(Boolean)
    ).size;

    return {
      totalReceipts: receipts.length,
      totalAmount,
      pending,
      employees,
    };
  }, [purchases, receipts]);

  const topPurchases = useMemo(() => {
    const sorted = [...purchases].sort((a, b) => {
      const dateA = a.captured_timestamp
        ? new Date(a.captured_timestamp).getTime()
        : 0;
      const dateB = b.captured_timestamp
        ? new Date(b.captured_timestamp).getTime()
        : 0;
      return dateB - dateA;
    });

    return sorted.slice(0, 5);
  }, [purchases]);

  const isLoading = receiptsLoading || purchasesLoading;
  const hasError = receiptsError || purchasesError;

  const formatAmount = (amount: number, currencyId?: number | null) => {
    if (currencyId != null) {
      const symbol = currencyMap.get(currencyId);
      if (symbol) {
        return `${symbol} ${amount.toFixed(2)}`;
      }
    }
    return fallbackCurrencyFormatter.format(amount);
  };

  const formatCaptured = (captured?: string | null) => {
    if (!captured) {
      return "—";
    }
    return capturedFormatter.format(new Date(captured));
  };

  const resolveExpenseType = (expenseTypeId?: number | null) => {
    if (!expenseTypeId) {
      return "Other";
    }
    return expenseTypeMap.get(expenseTypeId) ?? `Type #${expenseTypeId}`;
  };

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Receipts</CardTitle>
            <span className="text-sm text-gray-400">📄</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? "…" : stats.totalReceipts}
            </div>
            <p className="text-xs text-muted-foreground">All submissions</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Amount</CardTitle>
            <span className="text-sm text-gray-400">💰</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading
                ? "…"
                : formatAmount(stats.totalAmount ?? 0)}
            </div>
            <p className="text-xs text-muted-foreground">Across purchases</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending</CardTitle>
            <span className="text-sm text-gray-400">📅</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? "…" : stats.pending}
            </div>
            <p className="text-xs text-muted-foreground">Awaiting approval</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Employees</CardTitle>
            <span className="text-sm text-gray-400">👥</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? "…" : stats.employees}
            </div>
            <p className="text-xs text-muted-foreground">Active submitters</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>
            Latest purchases submitted for approval
          </CardDescription>
        </CardHeader>
        <CardContent>
          {hasError ? (
            <div className="text-sm text-red-600">
              Failed to load receipts:{" "}
              {receiptsError?.message ?? purchasesError?.message}
            </div>
          ) : isLoading ? (
            <div className="flex items-center justify-center py-8 text-sm text-muted-foreground">
              Loading recent activity…
            </div>
          ) : topPurchases.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center text-sm text-muted-foreground">
              <span className="text-4xl mb-2">📄</span>
              No purchases recorded yet. Submit a receipt to see it here.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Amount</TableHead>
                  <TableHead>Expense Type</TableHead>
                  <TableHead>Captured</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {topPurchases.map((purchase) => (
                  <TableRow key={purchase.id}>
                    <TableCell>
                      {formatAmount(purchase.amount, purchase.currency_id)}
                    </TableCell>
                    <TableCell>
                      {resolveExpenseType(purchase.expense_type_id)}
                    </TableCell>
                    <TableCell>
                      {formatCaptured(purchase.captured_timestamp)}
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={purchase.status} />
                    </TableCell>
                    <TableCell>
                      {purchase.user_id ?? "—"}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm">
                        View
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
