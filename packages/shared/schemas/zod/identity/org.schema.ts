import { z } from 'zod'

export const OrgRowSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  slug: z.string(),
  settings: z.unknown(), // jsonb
  is_active: z.boolean(),
  created_by: z.string().uuid().nullable(),
  created_at: z.string().datetime({ offset: true, precision: 6 }),
  updated_by: z.string().uuid().nullable(),
  updated_at: z.string().datetime({ offset: true, precision: 6 }),
})

export type OrgRow = z.infer<typeof OrgRowSchema>

export const OrgInsertSchema = z.object({
  id: z.string().uuid().optional(),
  name: z.string(),
  slug: z.string(),
  settings: z.unknown().optional(),
  is_active: z.boolean().optional(),
  created_by: z.string().uuid().nullable().optional(),
  created_at: z.string().datetime({ offset: true, precision: 6 }).optional(),
  updated_by: z.string().uuid().nullable().optional(),
  updated_at: z.string().datetime({ offset: true, precision: 6 }).optional(),
})

export type OrgInsert = z.infer<typeof OrgInsertSchema>

export const OrgUpdateSchema = OrgInsertSchema.partial().extend({
  id: z.string().uuid(),
})

export type OrgUpdate = z.infer<typeof OrgUpdateSchema>
