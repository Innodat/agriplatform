import { z } from 'zod'

export const OrgMemberRowSchema = z.object({
  id: z.number(),
  org_id: z.string().uuid(),
  user_id: z.string().uuid(),
  is_owner: z.boolean(),
  deleted_at: z.string().datetime({ offset: true }).nullable(),
  created_by: z.string().uuid().nullable(),
  created_at: z.string().datetime({ offset: true }),
  updated_by: z.string().uuid().nullable(),
  updated_at: z.string().datetime({ offset: true }),
})

export type OrgMemberRow = z.infer<typeof OrgMemberRowSchema>

export const OrgMemberInsertSchema = z.object({
  id: z.number().optional(),
  org_id: z.string().uuid(),
  user_id: z.string().uuid(),
  is_owner: z.boolean().optional(),
  deleted_at: z.string().datetime({ offset: true }).nullable().optional(),
  created_by: z.string().uuid().nullable().optional(),
  created_at: z.string().datetime({ offset: true }).optional(),
  updated_by: z.string().uuid().nullable().optional(),
  updated_at: z.string().datetime({ offset: true }).optional(),
})

export type OrgMemberInsert = z.infer<typeof OrgMemberInsertSchema>

export const OrgMemberUpdateSchema = OrgMemberInsertSchema.partial().extend({
  id: z.number(),
})

export type OrgMemberUpdate = z.infer<typeof OrgMemberUpdateSchema>
