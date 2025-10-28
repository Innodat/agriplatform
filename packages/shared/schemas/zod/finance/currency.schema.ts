import { z } from "zod";

export const currencyRowSchema = z.object({
  id: z.number(),
  name: z.string(),
  description: z.string().nullable(),
  symbol: z.string().nullable(),
  is_active: z.boolean().nullable(),
  created_by: z.string().uuid().nullable(),
  updated_by: z.string().uuid().nullable(),
  created_at: z.string().datetime().nullable(),
  updated_at: z.string().datetime().nullable(),
});
export type CurrencyRow = z.infer<typeof currencyRowSchema>;

export const currencyInsertSchema = z.object({
  id: z.number().optional(),
  name: z.string(),
  description: z.string().nullable().optional(),
  symbol: z.string().nullable().optional(),
  is_active: z.boolean().optional(),
  created_by: z.string().uuid().nullable().optional(),
  updated_by: z.string().uuid().nullable().optional(),
  created_at: z.string().datetime().optional(),
  updated_at: z.string().datetime().optional(),
});
export type CurrencyInsert = z.infer<typeof currencyInsertSchema>;

export const currencyUpdateSchema = currencyInsertSchema
  .partial()
  .extend({ id: z.number() });
export type CurrencyUpdate = z.infer<typeof currencyUpdateSchema>;
