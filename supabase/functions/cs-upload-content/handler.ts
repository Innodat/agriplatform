import {
  mergeCorsHeaders as defaultMergeCors,
  handleCors as defaultHandleCors,
} from "../_shared/cors.ts";
import { supabaseAdmin } from "../_shared/supabase.ts";
import { HttpError, requireAuth as defaultRequireAuth } from "../_shared/auth.ts";
import { csUploadContentRequestSchema } from "@shared";
// @ts-ignore: Deno/Node interop
import { ZodError } from "zod";
import { getProvider, resolveBucketOrContainerName } from "../_shared/storage-providers/registry.ts";
import type { StorageProvider } from "../_shared/storage-providers/types.ts";

const DEFAULT_PREFIX = "receipts";

function buildExternalKey(mimeType: string, userId: string) {
  const extension = mimeType.split("/")[1] ?? "bin";
  return `${DEFAULT_PREFIX}/${userId}/${crypto.randomUUID()}.${extension}`;
}

type SupabaseLike = typeof supabaseAdmin;

interface Dependencies {
  handleCors: typeof defaultHandleCors;
  mergeCorsHeaders: typeof defaultMergeCors;
  resolveContentSource: typeof defaultResolveContentSource;
  getProvider: typeof getProvider;
  resolveBucketOrContainerName: typeof resolveBucketOrContainerName;
  supabase: SupabaseLike;
  requireAuth: typeof defaultRequireAuth;
}

const defaultDeps: Dependencies = {
  handleCors: defaultHandleCors,
  mergeCorsHeaders: defaultMergeCors,
  resolveContentSource: defaultResolveContentSource,
  getProvider,
  resolveBucketOrContainerName,
  supabase: supabaseAdmin,
  requireAuth: defaultRequireAuth,
};

async function defaultResolveContentSource(
  supabase: SupabaseLike,
  orgId?: string,
) {
  let contentSourceId: string | null = null;
  
  // Step 1: Try to get content_source_id from org settings
  if (orgId) {
    const { data: org, error: orgError } = await supabase
      .schema("identity")
      .from("org")
      .select("settings")
      .eq("id", orgId)
      .single();
    
    // Throw error if org lookup fails
    if (orgError) {
      throw new HttpError(`Failed to lookup organization: ${orgError.message}`, 500);
    }
    
    if (org?.settings) {
      contentSourceId = org.settings.content_source_id as string;
    }
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
    settings: Record<string, any>; //{ container_name: string; bucket_name: string; connection_secret: string };
    is_active: boolean;
    provider: string;
    name: string;
  };
}

export function createUploadHandler(overrides: Partial<Dependencies> = {}) {
  const deps = { ...defaultDeps, ...overrides };

  return async function handler(req: Request): Promise<Response> {
    try {
      const corsResponse = deps.handleCors(req);
      if (corsResponse) {
        return corsResponse;
      }

      if (req.method !== "POST") {
        throw new HttpError("Method not allowed", 405);
      }

      const auth = await deps.requireAuth(req);
      const _reqJson = await req.json()
      console.log("request: ",  _reqJson)
      const payload = csUploadContentRequestSchema.parse(_reqJson);
      const orgId = auth.payload.org_id as string | undefined; // From JWT token
      const source = await deps.resolveContentSource(
        deps.supabase,
        orgId,
      );

      // Get the storage provider for this content source
      const provider = deps.getProvider(source.provider, source.settings);

      // Resolve bucket/container name with environment substitution
      const bucketOrContainer = deps.resolveBucketOrContainerName(
        source.settings.container_name ?? source.settings.bucket_name
      );

      const externalKey = buildExternalKey(payload.mime_type, auth.userId);

      // Create content_store record (inactive until finalized)
      const { data: inserted, error: insertError } = await deps.supabase
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
          headers: deps.mergeCorsHeaders({ "Content-Type": "application/json" }),
        },
      );
    } catch (error) {
      if (error instanceof ZodError) {
        const issue = error.issues[0];
        return new Response(JSON.stringify({ error: issue?.message ?? "Invalid payload" }), {
          status: 400,
          headers: deps.mergeCorsHeaders({ "Content-Type": "application/json" }),
        });
      }

      if (error instanceof HttpError) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: error.status,
          headers: deps.mergeCorsHeaders({ "Content-Type": "application/json" }),
        });
      }

      console.error("cs-upload-content error:", error);
      return new Response(JSON.stringify({ error: "Internal Server Error" }), {
        status: 500,
        headers: deps.mergeCorsHeaders({ "Content-Type": "application/json" }),
      });
    }
  };
}

export const handler = createUploadHandler();
