import { z } from "zod";

export const expenseCategoryRowSchema = z.object({
  id: z.number(),
  name: z.string(),
  description: z.string().nullable(),
  is_active: z.boolean().nullable(),
  created_by: z.string().uuid().nullable(),
  updated_by: z.string().uuid().nullable(),
  created_at: z.string().datetime().nullable(),
  updated_at: z.string().datetime().nullable(),
});
export type ExpenseCategoryRow = z.infer<typeof expenseCategoryRowSchema>;

export const expenseCategoryInsertSchema = z.object({
  id: z.number().optional(),
  name: z.string(),
  description: z.string().nullable().optional(),
  is_active: z.boolean().optional(),
  created_by: z.string().uuid().nullable().optional(),
  updated_by: z.string().uuid().nullable().optional(),
  created_at: z.string().datetime().optional(),
  updated_at: z.string().datetime().optional(),
});
export type ExpenseCategoryInsert = z.infer<typeof expenseCategoryInsertSchema>;

export const expenseCategoryUpdateSchema = expenseCategoryInsertSchema
  .partial()
  .extend({ id: z.number() });
export type ExpenseCategoryUpdate = z.infer<typeof expenseCategoryUpdateSchema>;
