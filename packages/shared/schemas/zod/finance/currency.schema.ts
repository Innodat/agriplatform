import { z } from "zod";

export const currencyRowSchema = z.object({
  id: z.number(),
  name: z.string(),
  description: z.string().nullable(),
  symbol: z.string().nullable(),
  created_user_id: z.string().nullable(),
  modified_user_id: z.string().nullable(),
  is_active: z.boolean().nullable(),
  created_timestamp: z.string().datetime().nullable(),
  modified_timestamp: z.string().datetime().nullable(),
});
export type CurrencyRow = z.infer<typeof currencyRowSchema>;

export const currencyInsertSchema = z.object({
  id: z.number().optional(),
  name: z.string(),
  description: z.string().nullable().optional(),
  symbol: z.string().nullable().optional(),
  created_user_id: z.string().nullable().optional(),
  modified_user_id: z.string().nullable().optional(),
  is_active: z.boolean().optional(),
  created_timestamp: z.string().datetime().optional(),
  modified_timestamp: z.string().datetime().optional(),
});
export type CurrencyInsert = z.infer<typeof currencyInsertSchema>;

export const currencyUpdateSchema = z.object({
  id: z.number().optional(),
  name: z.string().optional(),
  description: z.string().nullable().optional(),
  symbol: z.string().nullable().optional(),
  created_user_id: z.string().nullable().optional(),
  modified_user_id: z.string().nullable().optional(),
  is_active: z.boolean().nullable().optional(),
  created_timestamp: z.string().datetime().nullable().optional(),
  modified_timestamp: z.string().datetime().nullable().optional(),
});
export type CurrencyUpdate = z.infer<typeof currencyUpdateSchema>;
