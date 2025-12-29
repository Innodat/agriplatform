import {
  mergeCorsHeaders as defaultMergeCors,
  handleCors as defaultHandleCors,
} from "../_shared/cors.ts";
import { HttpError, requireAuth as defaultRequireAuth } from "../_shared/auth.ts";
import { supabaseAdmin } from "../_shared/supabase.ts";
import { csUploadContentRequestSchema } from "@shared";
import { getProvider as getProviderRegistry, resolveBucketOrContainerName } from "../_shared/storage-providers/registry.ts";

const DEFAULT_PREFIX = "receipts";

function buildExternalKey(mimeType: string, userId: string) {
  const extension = mimeType.split("/")[1] ?? "bin";
  return `${DEFAULT_PREFIX}/${userId}/${crypto.randomUUID()}.${extension}`;
}

async function resolveContentSource(
  supabase: typeof supabaseAdmin,
  orgId: string,
) {
  let contentSourceId: string | null = null;
  
  // Step 1: Try to get content_source_id from org settings
  // Skip if identity schema doesn't exist (e.g., in test environment)
  const { data: org, error: orgError } = await supabase
    .schema("identity")
    .from("org")
    .select("settings")
    .eq("id", orgId)
    .single();
  
  // Only throw error if org lookup fails for non-schema reasons
  if (orgError && !orgError.message.includes("Invalid schema")) {
    throw new HttpError(`Failed to lookup organization: ${orgError.message}`, 500);
  }
  
  if (org?.settings) {
    contentSourceId = org.settings.content_source_id as string;
  }
  
  // Step 2: Fall back to default global source by name
  if (!contentSourceId) {
    const { data: defaultSource, error: defaultError } = await supabase
      .schema("cs")
      .from("content_source")
      .select("id")
      .eq("name", "Default Supabase Storage")
      .eq("is_active", true)
      .limit(1)
      .single();
    
    if (defaultError || !defaultSource) {
      console.error(defaultError)
      throw new HttpError("No content source available", 500);
    }
    
    contentSourceId = defaultSource.id;
  }
  
  // Step 3: Query the content source
  const { data, error } = await supabase
    .schema("cs")
    .from("content_source")
    .select("id, settings, is_active, provider, name")
    .eq("id", contentSourceId)
    .single();
  
  if (error || !data) {
    throw new HttpError("Unable to resolve content source", 500);
  }
  
  return data as unknown as {
    id: string;
    settings: Record<string, any>;
    is_active: boolean;
    provider: string;
    name: string;
  };
}

export async function handleUploadContent(
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
    getProvider: getProviderOption,
    resolveBucketOrContainerName: resolveContainer = resolveBucketOrContainerName,
  } = options;

  try {
    const corsResponse = handleCors(req);
    if (corsResponse) {
      return corsResponse;
    }

    if (req.method !== "POST") {
      throw new HttpError("Method not allowed", 405);
    }

    const auth = await requireAuth(req);
    const _reqJson = await req.json()
    console.log("request: ", _reqJson)
    const payload = csUploadContentRequestSchema.parse(_reqJson);
    
    // Get org_id from JWT payload (if auth hook is running) or fall back to user_metadata
    let orgId = auth.payload?.org_id as string | undefined;
    if (!orgId && auth.payload?.user_metadata) {
      orgId = (auth.payload.user_metadata as any).current_org_id as string | undefined;
    }
    if (!orgId) {
      throw new HttpError("Organization ID is required", 400);
    }
    
    const source = await resolveContentSource(supabase, orgId);

    // Get the storage provider for this content source
    const provider = getProviderOption?.(source.provider, source.settings) ?? 
      getProviderRegistry(source.provider, source.settings);

    // Resolve bucket/container name with environment substitution
    const bucketOrContainer = resolveContainer(source.settings.container_name ?? source.settings.bucket_name);

    // Ensure bucket/container exists (lazy creation)
    if (provider.ensureBucketExists) {
      try {
        await provider.ensureBucketExists({
          bucketOrContainer,
          isPublic: false,
        });
      } catch (error) {
        console.warn(`Failed to ensure bucket exists: ${error}. Continuing anyway...`);
      }
    }

    const externalKey = buildExternalKey(payload.mime_type, auth.userId);

    // Create content_store record (inactive until finalized)
    const { data: inserted, error: insertError } = await supabase
      .schema("cs")
      .from("content_store")
      .insert({
        source_id: source.id,
        external_key: externalKey,
        mime_type: payload.mime_type,
        size_bytes: payload.size_bytes ?? null,
        checksum: payload.checksum ?? null,
        metadata: payload.metadata ?? null,
        is_active: false,
        created_by: auth.userId,
      })
      .select("id")
      .single();

    if (insertError || !inserted) {
      throw new HttpError("Failed to create content_store record", 500);
    }

    // Generate upload URL using the provider
    const uploadUrlResult = await provider.generateUploadUrl({
      bucketOrContainer,
      path: externalKey,
      contentType: payload.mime_type,
      expectedSizeBytes: payload.size_bytes,
      checksumBase64: payload.checksum,
      expiresInMinutes: 15,
    });

    return new Response(
      JSON.stringify({
        content_id: inserted.id,
        upload_url: uploadUrlResult.url,
        external_key: externalKey,
        expires_at: uploadUrlResult.expiresAt.toISOString(),
      }),
      {
        headers: mergeCorsHeaders({ "Content-Type": "application/json" }),
      },
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

    console.error("cs-upload-content error:", error);
    return new Response(JSON.stringify({ error: "Internal Server Error" }), {
      status: 500,
      headers: mergeCorsHeaders({ "Content-Type": "application/json" }),
    });
  }
}

// Default export for Supabase Functions
export const handler = handleUploadContent;
