import { handleCors as defaultHandleCors, mergeCorsHeaders as defaultMergeCors } from "../_shared/cors.ts";
import { HttpError, hasRole, requireAuth as defaultRequireAuth } from "../_shared/auth.ts";
import { supabaseAdmin } from "../_shared/supabase.ts";
import { csFinalizeContentRequestSchema } from "@shared";
import { getProvider as getProviderRegistry, resolveBucketOrContainerName } from "../_shared/storage-providers/registry.ts";

async function fetchContentRecord(supabase: typeof supabaseAdmin, contentId: string) {
  const { data, error } = await supabase
    .schema("cs")
    .from("content_store")
    .select(
      `
      id,
      source_id,
      external_key,
      size_bytes,
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
    throw new HttpError("Content not found", 404);
  }

  return data as unknown as {
    id: string;
    source_id: string;
    external_key: string;
    size_bytes: number | null;
    created_by: string;
    source: { 
      id: string;
      provider: string;
      settings: Record<string, any>;
    };
  };
}

export async function handleFinalizeUpload(
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
  console.log("Finalize Upload")
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

    if (req.method !== "POST") {
      throw new HttpError("Method not allowed", 405);
    }

    const auth = await requireAuth(req);
    const payload = csFinalizeContentRequestSchema.parse(await req.json());

    console.log("Fetch content record", payload.content_id)
    const record = await fetchContentRecord(supabase, payload.content_id);
    const isOwner = auth.userId === record.created_by;
    const isAdmin = hasRole(auth, ["admin", "financeadmin"]);

    if (!isOwner && !isAdmin) {
      throw new HttpError("Forbidden", 403);
    }

    // Get the storage provider
    console.log("Get the storage provider", record.source.provider, record.source.settings)
    const provider = getProvider?.(record.source.provider, record.source.settings) ?? 
      getProviderRegistry(record.source.provider, record.source.settings);

    // Resolve bucket/container name
    console.log("Resolve the bucket name")
    const bucketOrContainer = resolveContainer(
      record.source.settings.container_name ?? record.source.settings.bucket_name
    );

    // Check if the blob exists using the provider
    console.log("Does the file exist?")
    const exists = await provider.exists({
      bucketOrContainer,
      path: record.external_key,
    });

    if (!exists.exists) {
      console.error("The blob does not exist", exists)
      throw new HttpError("Blob not found. Please re-upload before finalizing.", 400);
    }

    // Update content_store to mark as active
    console.log("Mark the uploaded content as active")
    const { error: updateError } = await supabase
      .schema("cs")
      .from("content_store")
      .update({
        is_active: true,
        size_bytes: exists.size ?? record.size_bytes,
        updated_by: auth.userId,
      })
      .eq("id", record.id);

    if (updateError) {
      console.error(updateError);
      throw new HttpError("Failed to finalize content", 500);
    }

    return new Response(
      JSON.stringify({
        success: true,
        content_id: record.id,
        external_key: record.external_key,
        verified_size: exists.size ?? null,
      }),
      { headers: mergeCorsHeaders({ "Content-Type": "application/json" }) },
    );
  } catch (error) {
    // Check for ZodError by checking for 'issues' property
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

    console.error("cs-finalize-upload error:", error);
    return new Response(JSON.stringify({ error: "Internal Server Error" }), {
      status: 500,
      headers: mergeCorsHeaders({ "Content-Type": "application/json" }),
    });
  }
}

// Default export for Supabase Functions
export const handler = handleFinalizeUpload;
