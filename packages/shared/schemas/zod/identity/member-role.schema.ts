import { z } from 'zod'

export const AppRoleEnum = z.enum(['admin', 'financeadmin', 'employee'])
export type AppRole = z.infer<typeof AppRoleEnum>

export const MemberRoleRowSchema = z.object({
  id: z.number(),
  member_id: z.number(),
  role: AppRoleEnum,
  is_active: z.boolean(),
  created_by: z.string().uuid().nullable(),
  created_at: z.string().datetime({ offset: true }),
  updated_by: z.string().uuid().nullable(),
  updated_at: z.string().datetime({ offset: true }),
})

export type MemberRoleRow = z.infer<typeof MemberRoleRowSchema>

export const MemberRoleInsertSchema = z.object({
  id: z.number().optional(),
  member_id: z.number(),
  role: AppRoleEnum,
  is_active: z.boolean().optional(),
  created_by: z.string().uuid().nullable().optional(),
  created_at: z.string().datetime({ offset: true }).optional(),
  updated_by: z.string().uuid().nullable().optional(),
  updated_at: z.string().datetime({ offset: true }).optional(),
})

export type MemberRoleInsert = z.infer<typeof MemberRoleInsertSchema>

export const MemberRoleUpdateSchema = MemberRoleInsertSchema.partial().extend({
  id: z.number(),
})

export type MemberRoleUpdate = z.infer<typeof MemberRoleUpdateSchema>
