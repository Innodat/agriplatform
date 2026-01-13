import { z } from 'zod'

/**
 * Application role enum
 */
export const AppRoleEnum = z.enum(['admin', 'financeadmin', 'employee'])

/**
 * User role row schema (from identity.user_roles table)
 */
export const UserRoleRowSchema = z.object({
  id: z.number(),
  user_id: z.string().uuid(),
  role: AppRoleEnum,
  is_active: z.boolean().nullable().default(true),
  created_by: z.string().nullable(),
  updated_by: z.string().nullable(),
  created_at: z.string().datetime({ offset: true }).nullable(),
  updated_at: z.string().datetime({ offset: true }).nullable(),
})

/**
 * Inferred TypeScript types
 */
export type UserRoleRow = z.infer<typeof UserRoleRowSchema>
export type AppRole = z.infer<typeof AppRoleEnum>
