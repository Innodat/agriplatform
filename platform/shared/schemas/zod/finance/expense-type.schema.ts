import { z } from "zod";

export const expenseTypeRowSchema = z.object({
  id: z.number(),
  org_id: z.string().uuid(),
  expense_category_id: z.number().nullable(),
  name: z.string(),
  description: z.string().nullable(),
  deleted_at: z.string().datetime({ offset: true }).nullable(),
  created_by: z.string().uuid().nullable(),
  created_at: z.string().datetime({ offset: true }).nullable(),
  updated_by: z.string().uuid().nullable(),
  updated_at: z.string().datetime({ offset: true }).nullable(),
});
export type ExpenseTypeRow = z.infer<typeof expenseTypeRowSchema>;

export const expenseTypeInsertSchema = z.object({
  id: z.number().optional(),
  org_id: z.string().uuid().optional(),
  expense_category_id: z.number().nullable().optional(),
  name: z.string(),
  description: z.string().nullable().optional(),
  deleted_at: z.string().datetime({ offset: true }).nullable().optional(),
  created_by: z.string().uuid().nullable().optional(),
  created_at: z.string().datetime({ offset: true }).optional(),
  updated_by: z.string().uuid().nullable().optional(),
  updated_at: z.string().datetime({ offset: true }).optional(),
});
export type ExpenseTypeInsert = z.infer<typeof expenseTypeInsertSchema>;

export const expenseTypeUpdateSchema = expenseTypeInsertSchema
  .partial()
  .extend({ id: z.number() });
export type ExpenseTypeUpdate = z.infer<typeof expenseTypeUpdateSchema>;
