import { z } from "zod";

const uuid = z.string().uuid();
const isoDateTime = z.string().datetime({ offset: true });
const metadataSchema = z.record(z.string(), z.unknown(), {
  invalid_type_error: "metadata must be an object",
});
const mimeTypeSchema = z.string({
  required_error: "mime_type is required",
}).min(1, { message: "mime_type is required" });
const contentIdSchema = z.string({
  required_error: "content_id is required",
}).uuid({ message: "content_id must be a valid uuid" });
const sizeBytesSchema = z.number({
  invalid_type_error: "size_bytes must be a number",
});

/**
 * cs.content_store row schema
 */
export const contentStoreRowSchema = z.object({
  id: uuid,
  source_id: uuid,
  external_key: z.string().min(1),
  mime_type: z.string().min(1),
  size_bytes: z.number().int().nonnegative().nullable(),
  checksum: z.string().min(1).nullable(),
  metadata: metadataSchema.nullable(),
  is_active: z.boolean(),
  created_by: uuid.nullable(),
  created_at: isoDateTime.nullable(),
  updated_by: uuid.nullable(),
  updated_at: isoDateTime.nullable(),
});
export type ContentStoreRow = z.infer<typeof contentStoreRowSchema>;

export const contentStoreInsertSchema = contentStoreRowSchema.omit({
  id: true,
  created_at: true,
  updated_at: true,
  updated_by: true,
  is_active: true,
}).extend({
  id: uuid.optional(),
  is_active: z.boolean().optional(),
});
export type ContentStoreInsert = z.infer<typeof contentStoreInsertSchema>;

export const contentStoreUpdateSchema = contentStoreInsertSchema.partial().extend({
  id: uuid,
});
export type ContentStoreUpdate = z.infer<typeof contentStoreUpdateSchema>;

/**
 * Edge function request/response contracts
 */
export const csUploadContentRequestSchema = z.object({
  mime_type: mimeTypeSchema,
  size_bytes: sizeBytesSchema.optional(),
  checksum: z.string().min(1).optional(),
  metadata: metadataSchema.optional(),
  source_id: uuid.optional(),
});
export type CsUploadContentRequest = z.infer<typeof csUploadContentRequestSchema>;

export const csUploadContentResponseSchema = z.object({
  content_id: uuid,
  upload_url: z.string().url(),
  external_key: z.string().min(1),
  expires_at: isoDateTime,
});
export type CsUploadContentResponse = z.infer<typeof csUploadContentResponseSchema>;

export const csUpdateContentRequestSchema = z.object({
  content_id: contentIdSchema,
  mime_type: mimeTypeSchema.optional(),
  size_bytes: sizeBytesSchema.optional(),
  checksum: z.string().min(1).optional(),
  metadata: metadataSchema.optional(),
});
export type CsUpdateContentRequest = z.infer<typeof csUpdateContentRequestSchema>;

export const csUpdateContentResponseSchema = csUploadContentResponseSchema;
export type CsUpdateContentResponse = CsUploadContentResponse;

export const csFinalizeContentRequestSchema = z.object({
  content_id: contentIdSchema,
});
export type CsFinalizeContentRequest = z.infer<typeof csFinalizeContentRequestSchema>;

export const csFinalizeContentResponseSchema = z.object({
  success: z.literal(true),
  content_id: uuid,
  external_key: z.string().min(1),
  verified_size: z.number().int().nonnegative().nullable(),
});
export type CsFinalizeContentResponse = z.infer<typeof csFinalizeContentResponseSchema>;

export const csGenerateSignedUrlParamsSchema = z.object({
  id: contentIdSchema,
});
export type CsGenerateSignedUrlParams = z.infer<typeof csGenerateSignedUrlParamsSchema>;

export const csGenerateSignedUrlResponseSchema = z.object({
  signed_url: z.string().url(),
  expires_at: isoDateTime,
});
export type CsGenerateSignedUrlResponse = z.infer<typeof csGenerateSignedUrlResponseSchema>;
