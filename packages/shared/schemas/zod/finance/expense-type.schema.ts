import { z } from "zod";

export const expenseTypeRowSchema = z.object({
  id: z.number(),
  expense_category_id: z.number().nullable(),
  name: z.string(),
  description: z.string().nullable(),
  created_user_id: z.string().nullable(),
  modified_user_id: z.string().nullable(),
  is_active: z.boolean().nullable(),
  created_timestamp: z.string().datetime().nullable(),
  modified_timestamp: z.string().datetime().nullable(),
});
export type ExpenseTypeRow = z.infer<typeof expenseTypeRowSchema>;

export const expenseTypeInsertSchema = z.object({
  id: z.number().optional(),
  expense_category_id: z.number().nullable().optional(),
  name: z.string(),
  description: z.string().nullable().optional(),
  created_user_id: z.string().nullable().optional(),
  modified_user_id: z.string().nullable().optional(),
  is_active: z.boolean().optional(),
  created_timestamp: z.string().datetime().optional(),
  modified_timestamp: z.string().datetime().optional(),
});
export type ExpenseTypeInsert = z.infer<typeof expenseTypeInsertSchema>;

export const expenseTypeUpdateSchema = z.object({
  id: z.number().optional(),
  expense_category_id: z.number().nullable().optional(),
  name: z.string().optional(),
  description: z.string().nullable().optional(),
  created_user_id: z.string().nullable().optional(),
  modified_user_id: z.string().nullable().optional(),
  is_active: z.boolean().nullable().optional(),
  created_timestamp: z.string().datetime().nullable().optional(),
  modified_timestamp: z.string().datetime().nullable().optional(),
});
export type ExpenseTypeUpdate = z.infer<typeof expenseTypeUpdateSchema>;
