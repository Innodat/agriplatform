import { z } from "zod";

export const currencyRowSchema = z.object({
  id: z.number(),
  org_id: z.string().uuid(),
  name: z.string(),
  description: z.string().nullable(),
  symbol: z.string().nullable(),
  is_active: z.boolean().nullable(),
  created_by: z.string().uuid().nullable(),
  created_at: z.string().datetime({ offset: true, precision: 6 }).nullable(),
  updated_by: z.string().uuid().nullable(),
  updated_at: z.string().datetime({ offset: true, precision: 6 }).nullable(),
});
export type CurrencyRow = z.infer<typeof currencyRowSchema>;

export const currencyInsertSchema = z.object({
  id: z.number().optional(),
  org_id: z.string().uuid().optional(),
  name: z.string(),
  description: z.string().nullable().optional(),
  symbol: z.string().nullable().optional(),
  is_active: z.boolean().optional(),
  created_by: z.string().uuid().nullable().optional(),
  created_at: z.string().datetime({ offset: true, precision: 6 }).optional(),
  updated_by: z.string().uuid().nullable().optional(),
  updated_at: z.string().datetime({ offset: true, precision: 6 }).optional(),
});
export type CurrencyInsert = z.infer<typeof currencyInsertSchema>;

export const currencyUpdateSchema = currencyInsertSchema
  .partial()
  .extend({ id: z.number() });
export type CurrencyUpdate = z.infer<typeof currencyUpdateSchema>;
