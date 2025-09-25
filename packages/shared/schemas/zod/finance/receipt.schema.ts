import { z } from "zod";

export const receiptRowSchema = z.object({
  id: z.number(),
  created_user_id: z.string().nullable(),
  modified_user_id: z.string().nullable(),
  is_active: z.boolean().nullable(),
  created_timestamp: z.string().datetime().nullable(),
  modified_timestamp: z.string().datetime().nullable(),
});
export type ReceiptRow = z.infer<typeof receiptRowSchema>;

export const receiptInsertSchema = z.object({
  // id is identity; optional if BY DEFAULT allows manual supply
  id: z.number().optional(),
  created_user_id: z.string().nullable().optional(),
  modified_user_id: z.string().nullable().optional(),
  is_active: z.boolean().optional(), // default true at DB
  created_timestamp: z.string().datetime().optional(), // default now
  modified_timestamp: z.string().datetime().optional(), // default now
});
export type ReceiptInsert = z.infer<typeof receiptInsertSchema>;

export const receiptUpdateSchema = z.object({
  id: z.number().optional(),
  created_user_id: z.string().nullable().optional(),
  modified_user_id: z.string().nullable().optional(),
  is_active: z.boolean().nullable().optional(),
  created_timestamp: z.string().datetime().nullable().optional(),
  modified_timestamp: z.string().datetime().nullable().optional(),
});
export type ReceiptUpdate = z.infer<typeof receiptUpdateSchema>;
