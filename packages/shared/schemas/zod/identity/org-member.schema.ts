import { z } from 'zod'

export const OrgMemberRowSchema = z.object({
  id: z.number(),
  org_id: z.string().uuid(),
  user_id: z.string().uuid(),
  is_owner: z.boolean(),
  is_active: z.boolean(),
  created_by: z.string().uuid().nullable(),
  created_at: z.string().datetime({ offset: true, precision: 6 }),
  updated_by: z.string().uuid().nullable(),
  updated_at: z.string().datetime({ offset: true, precision: 6 }),
})

export type OrgMemberRow = z.infer<typeof OrgMemberRowSchema>

export const OrgMemberInsertSchema = z.object({
  id: z.number().optional(),
  org_id: z.string().uuid(),
  user_id: z.string().uuid(),
  is_owner: z.boolean().optional(),
  is_active: z.boolean().optional(),
  created_by: z.string().uuid().nullable().optional(),
  created_at: z.string().datetime({ offset: true, precision: 6 }).optional(),
  updated_by: z.string().uuid().nullable().optional(),
  updated_at: z.string().datetime({ offset: true, precision: 6 }).optional(),
})

export type OrgMemberInsert = z.infer<typeof OrgMemberInsertSchema>

export const OrgMemberUpdateSchema = OrgMemberInsertSchema.partial().extend({
  id: z.number(),
})

export type OrgMemberUpdate = z.infer<typeof OrgMemberUpdateSchema>
