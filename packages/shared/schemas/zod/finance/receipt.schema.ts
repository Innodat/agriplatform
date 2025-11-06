import { z } from "zod";

export const receiptRowSchema = z.object({
  id: z.number(),
  supplier: z.string().nullable(),
  content_id: z.string().uuid().nullable(),
  is_active: z.boolean().nullable(),
  created_by: z.string().uuid().nullable(),
  updated_by: z.string().uuid().nullable(),
  created_at: z.string().datetime().nullable(),
  updated_at: z.string().datetime().nullable(),
  created_timestamp: z.string().datetime().nullable(),
  created_user_id: z.string().nullable(),
  modified_timestamp: z.string().datetime().nullable(),
  modified_user_id: z.string().nullable(),
  captured_at: z.string().datetime().nullable(),
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
