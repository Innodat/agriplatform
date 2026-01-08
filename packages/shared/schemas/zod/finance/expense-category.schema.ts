import { z } from "zod";

export const expenseCategoryRowSchema = z.object({
  id: z.number(),
  org_id: z.string().uuid(),
  name: z.string(),
  description: z.string().nullable(),
  is_active: z.boolean().nullable(),
  created_by: z.string().uuid().nullable(),
  created_at: z.string().datetime({ offset: true, precision: 6 }).nullable(),
  updated_by: z.string().uuid().nullable(),
  updated_at: z.string().datetime({ offset: true, precision: 6 }).nullable(),
});
export type ExpenseCategoryRow = z.infer<typeof expenseCategoryRowSchema>;

export const expenseCategoryInsertSchema = z.object({
  id: z.number().optional(),
  org_id: z.string().uuid().optional(),
  name: z.string(),
  description: z.string().nullable().optional(),
  is_active: z.boolean().optional(),
  created_by: z.string().uuid().nullable().optional(),
  created_at: z.string().datetime({ offset: true, precision: 6 }).optional(),
  updated_by: z.string().uuid().nullable().optional(),
  updated_at: z.string().datetime({ offset: true, precision: 6 }).optional(),
});
export type ExpenseCategoryInsert = z.infer<typeof expenseCategoryInsertSchema>;

export const expenseCategoryUpdateSchema = expenseCategoryInsertSchema
  .partial()
  .extend({ id: z.number() });
export type ExpenseCategoryUpdate = z.infer<typeof expenseCategoryUpdateSchema>;
