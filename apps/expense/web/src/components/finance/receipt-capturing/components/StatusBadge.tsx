import { Badge } from "@/components/ui/badge";
import type { PurchaseStatus } from "@/types";

const statusStyles: Record<PurchaseStatus, string> = {
  pending: "bg-yellow-100 text-yellow-800",
  approved: "bg-green-100 text-green-800",
  rejected: "bg-red-100 text-red-800",
  querying: "bg-blue-100 text-blue-800",
};

export function StatusBadge({ status }: { status: PurchaseStatus }) {
  return <Badge className={statusStyles[status]}>{status}</Badge>;
}
