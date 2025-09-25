import { z } from "zod";

export const purchaseRowSchema = z.object({
  id: z.number(),
  expense_type_id: z.number().nullable(),
  other_category: z.string().nullable(),
  currency_id: z.number().nullable(),
  user_id: z.string().uuid().nullable(),
  amount: z.number(),
  captured_timestamp: z.string().datetime(),
  created_user_id: z.string().nullable(),
  modified_user_id: z.string().nullable(),
  is_active: z.boolean().nullable(),
  created_timestamp: z.string().datetime().nullable(),
  modified_timestamp: z.string().datetime().nullable(),
  reimbursable: z.boolean(),
  receipt_id: z.number().nullable(),
});
export type PurchaseRow = z.infer<typeof purchaseRowSchema>;

export const purchaseInsertSchema = z.object({
  id: z.number().optional(),
  expense_type_id: z.number().nullable().optional(),
  other_category: z.string().nullable().optional(),
  currency_id: z.number().nullable().optional(),
  user_id: z.string().uuid().nullable().optional(),
  amount: z.number(),
  captured_timestamp: z.string().datetime(),
  created_user_id: z.string().nullable().optional(),
  modified_user_id: z.string().nullable().optional(),
  is_active: z.boolean().optional(),
  created_timestamp: z.string().datetime().optional(),
  modified_timestamp: z.string().datetime().optional(),
  reimbursable: z.boolean(),
  receipt_id: z.number().nullable().optional(),
});
export type PurchaseInsert = z.infer<typeof purchaseInsertSchema>;

export const purchaseUpdateSchema = z.object({
  id: z.number().optional(),
  expense_type_id: z.number().nullable().optional(),
  other_category: z.string().nullable().optional(),
  currency_id: z.number().nullable().optional(),
  user_id: z.string().uuid().nullable().optional(),
  amount: z.number().optional(),
  captured_timestamp: z.string().datetime().optional(),
  created_user_id: z.string().nullable().optional(),
  modified_user_id: z.string().nullable().optional(),
  is_active: z.boolean().nullable().optional(),
  created_timestamp: z.string().datetime().nullable().optional(),
  modified_timestamp: z.string().datetime().nullable().optional(),
  reimbursable: z.boolean().optional(),
  receipt_id: z.number().nullable().optional(),
});
export type PurchaseUpdate = z.infer<typeof purchaseUpdateSchema>;
