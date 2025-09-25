import { z } from "zod";

export const expenseCategoryRowSchema = z.object({
  id: z.number(),
  name: z.string(),
  description: z.string().nullable(),
  created_user_id: z.string().nullable(),
  modified_user_id: z.string().nullable(),
  is_active: z.boolean().nullable(),
  created_timestamp: z.string().datetime().nullable(),
  modified_timestamp: z.string().datetime().nullable(),
});
export type ExpenseCategoryRow = z.infer<typeof expenseCategoryRowSchema>;

export const expenseCategoryInsertSchema = z.object({
  id: z.number().optional(),
  name: z.string(),
  description: z.string().nullable().optional(),
  created_user_id: z.string().nullable().optional(),
  modified_user_id: z.string().nullable().optional(),
  is_active: z.boolean().optional(),
  created_timestamp: z.string().datetime().optional(),
  modified_timestamp: z.string().datetime().optional(),
});
export type ExpenseCategoryInsert = z.infer<typeof expenseCategoryInsertSchema>;

export const expenseCategoryUpdateSchema = z.object({
  id: z.number().optional(),
  name: z.string().optional(),
  description: z.string().nullable().optional(),
  created_user_id: z.string().nullable().optional(),
  modified_user_id: z.string().nullable().optional(),
  is_active: z.boolean().nullable().optional(),
  created_timestamp: z.string().datetime().nullable().optional(),
  modified_timestamp: z.string().datetime().nullable().optional(),
});
export type ExpenseCategoryUpdate = z.infer<typeof expenseCategoryUpdateSchema>;
