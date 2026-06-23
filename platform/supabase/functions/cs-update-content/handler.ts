import { handleCors as defaultHandleCors, mergeCorsHeaders as defaultMergeCors } from "../_shared/cors.ts";
import { HttpError, hasRole, requireAuth as defaultRequireAuth } from "../_shared/auth.ts";
import { supabaseAdmin } from "../_shared/supabase.ts";
import { csUpdateContentRequestSchema } from "@shared";
import { getProvider as getProviderRegistry, resolveBucketOrContainerName } from "../_shared/storage-providers/registry.ts";

const DEFAULT_PREFIX = "receipts";

function buildExternalKey(mimeType: string, userId: string) {
  const extension = mimeType.split("/")[1] ?? "bin";
  return `${DEFAULT_PREFIX}/${userId}/${crypto.randomUUID()}.${extension}`;
}

async function fetchContentRecord(supabase: typeof supabaseAdmin, contentId: string) {
  const { data, error } = await supabase
    .schema("cs")
    .from("content_store")
    .select(
      `
      id,
      source_id,
      external_key,
      mime_type,
      size_bytes,
      checksum,
      metadata,
      created_by,
      source:content_source (
        id,
        provider,
        settings
      )
    `,
    )
    .eq("id", contentId)
    .single();
  
  if (error || !data) {
    console.error("Error", error);
    throw new HttpError("Content not found", 404);
  }

  return data as unknown as {
    id: string;
    source_id: string;
    external_key: string;
    mime_type: string;
    size_bytes: number | null;
    checksum: string | null;
    metadata: Record<string, unknown> | null;
    created_by: string;
    source: { 
      id: string;
      provider: string;
      settings: Record<string, any>;
    };
  };
}

export async function handleUpdateContent(
  req: Request,
  options: {
    supabase?: typeof supabaseAdmin;
    requireAuth?: typeof defaultRequireAuth;
    handleCors?: typeof defaultHandleCors;
    mergeCorsHeaders?: typeof defaultMergeCors;
    getProvider?: typeof getProviderRegistry;
    resolveBucketOrContainerName?: typeof resolveBucketOrContainerName;
  } = {},
): Promise<Response> {
  const {
    supabase = supabaseAdmin,
    requireAuth = defaultRequireAuth,
    handleCors = defaultHandleCors,
    mergeCorsHeaders = defaultMergeCors,
    getProvider = getProviderRegistry,
    resolveBucketOrContainerName: resolveContainer = resolveBucketOrContainerName,
  } = options;

  try {
    const corsResponse = handleCors(req);
    if (corsResponse) return corsResponse;

    if (req.method !== "PUT") {
      throw new HttpError("Method not allowed", 405);
    }

    const auth = await requireAuth(req);
    const payload = csUpdateContentRequestSchema.parse(await req.json());
    const record = await fetchContentRecord(supabase, payload.content_id);

    const isOwner = auth.userId === record.created_by;
    const isAdmin = hasRole(auth, ["admin", "financeadmin"]);
    if (!isOwner && !isAdmin) {
      throw new HttpError("Forbidden", 403);
    }

    // Get the storage provider
    const provider = getProvider?.(record.source.provider, record.source.settings) ?? 
      getProviderRegistry(record.source.provider, record.source.settings);
    // const provider = getProvider!(record.source.provider, record.source.settings);

    // Resolve bucket/container name
    const bucketOrContainer = resolveContainer(
      record.source.settings.container_name ?? record.source.settings.bucket_name
    );

    // Archive current version before updating
    // Get the next version number
    const { data: versions } = await supabase
      .schema("cs")
      .from("content_version")
      .select("version_number")
      .eq("content_id", record.id)
      .order("version_number", { ascending: false })
      .limit(1);

    const nextVersion = (versions && versions.length > 0 ? versions[0].version_number : 0) + 1;

    // Insert the current version into content_version table
    const { error: versionError } = await supabase
      .schema("cs")
      .from("content_version")
      .insert({
        content_id: record.id,
        version_number: nextVersion,
        external_key: record.external_key,
        mime_type: record.mime_type,
        size_bytes: record.size_bytes,
        checksum: record.checksum,
        metadata: record.metadata,
        replaced_by: auth.userId,
      });

    if (versionError) {
      console.error("Failed to create version record:", versionError);
      throw new HttpError("Failed to archive current version", 500);
    }

    // Generate new external key for the updated content
    const newMimeType = payload.mime_type ?? record.mime_type;
    const newExternalKey = buildExternalKey(newMimeType, auth.userId);

    // Update content_store with new key and mark inactive
    const updates: Record<string, unknown> = {
      external_key: newExternalKey,
      updated_by: auth.userId,
      deleted_at: new Date().toISOString(),
    };

    if (payload.mime_type) updates.mime_type = payload.mime_type;
    if (payload.size_bytes !== undefined) updates.size_bytes = payload.size_bytes;
    if (payload.checksum !== undefined) updates.checksum = payload.checksum;
    if (payload.metadata !== undefined) updates.metadata = payload.metadata;

    const { error: updateError } = await supabase
      .schema("cs")
      .from("content_store")
      .update(updates)
      .eq("id", record.id);

    if (updateError) {
      throw new HttpError("Failed to update content metadata", 500);
    }

    // Generate upload URL for the new content
    const uploadUrlResult = await provider.generateUploadUrl({
      bucketOrContainer,
      path: newExternalKey,
      contentType: newMimeType,
      expectedSizeBytes: payload.size_bytes,
      checksumBase64: payload.checksum,
      expiresInMinutes: 15,
    });

    return new Response(
      JSON.stringify({
        content_id: record.id,
        upload_url: uploadUrlResult.url,
        external_key: newExternalKey,
        expires_at: uploadUrlResult.expiresAt.toISOString(),
        version_archived: nextVersion,
      }),
      { headers: mergeCorsHeaders({ "Content-Type": "application/json" }) },
    );
  } catch (error) {
    // Check for ZodError by checking for 'issues' property
    // (Zod may be loaded from different module instances)
    const isZodError = error && typeof error === "object" && "issues" in error && Array.isArray((error as any).issues);
    if (isZodError) {
      const issue = (error as any).issues[0];
      return new Response(JSON.stringify({ error: issue?.message ?? "Invalid payload" }), {
        status: 400,
        headers: mergeCorsHeaders({ "Content-Type": "application/json" }),
      });
    }

    if (error instanceof HttpError) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: error.status,
        headers: mergeCorsHeaders({ "Content-Type": "application/json" }),
      });
    }

    console.error("cs-update-content error:", error);
    return new Response(JSON.stringify({ error: "Internal Server Error" }), {
      status: 500,
      headers: mergeCorsHeaders({ "Content-Type": "application/json" }),
    });
  }
}

// Default export for Supabase Functions
export const handler = handleUpdateContent;
