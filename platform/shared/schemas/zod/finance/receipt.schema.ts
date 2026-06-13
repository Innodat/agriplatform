import { z } from "zod";

const dateRegex = /^\d{4}-\d{2}-\d{2}$/;

export const receiptStatusEnum = z.enum([
  "pending",
  "querying",
  "approved",
  "rejected",
]);

export const receiptRowSchema = z.object({
  id: z.number(),
  org_id: z.string().uuid(),
  supplier: z.string().nullable(),
  content_id: z.string().uuid().nullable(),
  deleted_at: z.string().datetime({ offset: true }).nullable(),
  status: receiptStatusEnum,
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
  deleted_at: z.string().datetime({ offset: true }).nullable().optional(),
  status: receiptStatusEnum.optional().default("pending"),
  receipt_date: z.string().regex(dateRegex).optional(),
  created_by: z.string().uuid().nullable().optional(),
  created_at: z.string().datetime({ offset: true }).optional(),
  updated_by: z.string().uuid().nullable().optional(),
  updated_at: z.string().datetime({ offset: true }).optional(),
});
export type ReceiptInsert = z.infer<typeof receiptInsertSchema>;

export const receiptUpdateSchema = receiptInsertSchema.partial().extend({
  id: z.number(),
});
export type ReceiptUpdate = z.infer<typeof receiptUpdateSchema>;
