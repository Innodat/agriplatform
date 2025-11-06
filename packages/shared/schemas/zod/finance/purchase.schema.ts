import { z } from "zod";

export const purchaseStatusEnum = z.enum([
  "pending",
  "approved",
  "rejected",
  "querying",
]);

export const purchaseRowSchema = z.object({
  id: z.number(),
  expense_type_id: z.number().nullable(),
  other_category: z.string().nullable(),
  currency_id: z.number().nullable(),
  user_id: z.string().uuid().nullable(),
  amount: z.coerce.number(),
  captured_timestamp: z.string(),
  is_active: z.boolean().nullable(),
  reimbursable: z.boolean(),
  receipt_id: z.number().nullable(),
  created_by: z.string().uuid().nullable(),
  updated_by: z.string().uuid().nullable(),
  created_at: z.string().datetime({ offset: true, precision: 6 }).nullable(),
  updated_at: z.string().datetime({ offset: true, precision: 6 }).nullable(),
  status: purchaseStatusEnum,
});
export type PurchaseRow = z.infer<typeof purchaseRowSchema>;

export const purchaseInsertSchema = z.object({
  id: z.number().optional(),
  expense_type_id: z.number().nullable().optional(),
  other_category: z.string().nullable().optional(),
  currency_id: z.number().nullable().optional(),
  user_id: z.string().uuid().nullable().optional(),
  amount: z.coerce.number(),
  captured_timestamp: z.string(),
  is_active: z.boolean().optional(),
  reimbursable: z.boolean(),
  receipt_id: z.number().nullable().optional(),
  created_by: z.string().uuid().nullable().optional(),
  updated_by: z.string().uuid().nullable().optional(),
  created_at: z.string().datetime().optional(),
  updated_at: z.string().datetime().optional(),
  status: purchaseStatusEnum.optional().default("pending"),
});
export type PurchaseInsert = z.infer<typeof purchaseInsertSchema>;

export const purchaseUpdateSchema = purchaseInsertSchema
  .partial()
  .extend({ id: z.number() });
export type PurchaseUpdate = z.infer<typeof purchaseUpdateSchema>;
