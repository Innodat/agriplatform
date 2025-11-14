import { z } from "zod";

const dateRegex = /^\d{4}-\d{2}-\d{2}$/;

export const receiptRowSchema = z.object({
  id: z.number(),
  supplier: z.string().nullable(),
  content_id: z.string().uuid().nullable(),
  is_active: z.boolean().nullable(),
  created_by: z.string().uuid().nullable(),
  updated_by: z.string().uuid().nullable(),
  created_at: z.string().datetime({ offset: true, precision: 6 }).nullable(),
  updated_at: z.string().datetime({ offset: true, precision: 6 }).nullable(),
  created_timestamp: z.string().datetime({ offset: true, precision: 6 }).nullable(),
  created_user_id: z.string().nullable(),
  modified_timestamp: z.string().datetime({ offset: true, precision: 6 }).nullable(),
  modified_user_id: z.string().nullable(),
  receipt_date: z.string().regex(dateRegex).nullable(),
});
export type ReceiptRow = z.infer<typeof receiptRowSchema>;

export const receiptInsertSchema = z.object({
  id: z.number().optional(),
  supplier: z.string().nullable().optional(),
  content_id: z.string().uuid().nullable().optional(),
  is_active: z.boolean().optional(),
  created_by: z.string().uuid().nullable().optional(),
  updated_by: z.string().uuid().nullable().optional(),
  created_at: z.string().datetime().optional(),
  updated_at: z.string().datetime().optional(),
});
export type ReceiptInsert = z.infer<typeof receiptInsertSchema>;

export const receiptUpdateSchema = receiptInsertSchema.partial().extend({
  id: z.number(),
});
export type ReceiptUpdate = z.infer<typeof receiptUpdateSchema>;
