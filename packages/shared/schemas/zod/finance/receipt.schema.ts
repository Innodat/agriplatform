import { z } from "zod";

const dateRegex = /^\d{4}-\d{2}-\d{2}$/;

export const receiptRowSchema = z.object({
  id: z.number(),
  org_id: z.string().uuid(),
  supplier: z.string().nullable(),
  content_id: z.string().uuid().nullable(),
  is_active: z.boolean().nullable(),
  receipt_date: z.string().regex(dateRegex),
  created_by: z.string().uuid().nullable(),
  created_at: z.string().datetime({ offset: true }).nullable(),
  updated_by: z.string().uuid().nullable(),
  updated_at: z.string().datetime({ offset: true }).nullable(),
});
export type ReceiptRow = z.infer<typeof receiptRowSchema>;

export const receiptInsertSchema = z.object({
  id: z.number().optional(),
  org_id: z.string().uuid().optional(),
  supplier: z.string().nullable().optional(),
  content_id: z.string().uuid().nullable().optional(),
  is_active: z.boolean().optional(),
  receipt_date: z.string().regex(dateRegex).optional(),
  created_by: z.string().uuid().nullable().optional(),
  created_at: z.string().datetime({ offset: true, precision: 6 }).optional(),
  updated_by: z.string().uuid().nullable().optional(),
  updated_at: z.string().datetime({ offset: true, precision: 6 }).optional(),
});
export type ReceiptInsert = z.infer<typeof receiptInsertSchema>;

export const receiptUpdateSchema = receiptInsertSchema.partial().extend({
  id: z.number(),
});
export type ReceiptUpdate = z.infer<typeof receiptUpdateSchema>;
