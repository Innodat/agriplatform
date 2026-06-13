import { z } from 'zod'

export const OrgRowSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  slug: z.string(),
  settings: z.object({}).passthrough(),
  deleted_at: z.string().datetime({ offset: true }).nullable(),
  created_by: z.string().uuid().nullable(),
  created_at: z.string().datetime({ offset: true }),
  updated_by: z.string().uuid().nullable(),
  updated_at: z.string().datetime({ offset: true }),
})

export type OrgRow = z.infer<typeof OrgRowSchema>

export const OrgInsertSchema = z.object({
  id: z.string().uuid().optional(),
  name: z.string(),
  slug: z.string(),
  settings: z.object({}).passthrough().optional(),
  deleted_at: z.string().datetime({ offset: true }).nullable().optional(),
  created_by: z.string().uuid().nullable().optional(),
  created_at: z.string().datetime({ offset: true }).optional(),
  updated_by: z.string().uuid().nullable().optional(),
  updated_at: z.string().datetime({ offset: true }).optional(),
})

export type OrgInsert = z.infer<typeof OrgInsertSchema>

export const OrgUpdateSchema = OrgInsertSchema.partial().extend({
  id: z.string().uuid(),
})

export type OrgUpdate = z.infer<typeof OrgUpdateSchema>
