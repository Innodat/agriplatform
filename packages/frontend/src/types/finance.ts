import type {
  ReceiptInsert,
  ReceiptRow,
  ReceiptUpdate,
  PurchaseInsert,
  PurchaseRow,
  PurchaseUpdate,
  ExpenseCategoryRow,
  ExpenseCategoryInsert,
  ExpenseCategoryUpdate,
  ExpenseTypeRow,
  ExpenseTypeInsert,
  ExpenseTypeUpdate,
  CurrencyRow,
  CurrencyInsert,
  CurrencyUpdate,
} from "@shared/schemas/zod/finance";

export type {
  ReceiptInsert,
  ReceiptRow,
  ReceiptUpdate,
  PurchaseInsert,
  PurchaseRow,
  PurchaseUpdate,
  ExpenseCategoryRow,
  ExpenseCategoryInsert,
  ExpenseCategoryUpdate,
  ExpenseTypeRow,
  ExpenseTypeInsert,
  ExpenseTypeUpdate,
  CurrencyRow,
  CurrencyInsert,
  CurrencyUpdate,
};

export type PurchaseStatus = PurchaseRow["status"];
