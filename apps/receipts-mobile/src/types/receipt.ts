import { ReceiptRow } from '@agriplatform/shared';

export interface ReceiptWithTotal extends ReceiptRow {
  totalAmount: number;
  currency: string;
}
