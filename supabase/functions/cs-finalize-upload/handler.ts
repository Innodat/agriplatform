import { handleCors as defaultHandleCors, mergeCorsHeaders as defaultMergeCors } from "../_shared/cors.ts";
import { supabaseAdmin } from "../_shared/supabase.ts";
import { HttpError, hasRole, requireAuth as defaultRequireAuth } from "../_shared/auth.ts";
import { csFinalizeContentRequestSchema } from "@shared";
import { ZodError } from "zod";
import { getProvider, resolveBucketOrContainerName } from "../_shared/storage-providers/registry.ts";
import type { StorageProvider } from "../_shared/storage-providers/types.ts";

type SupabaseLike = typeof supabaseAdmin;

interface Dependencies {
  handleCors: typeof defaultHandleCors;
  mergeCorsHeaders: typeof defaultMergeCors;
  getProvider: typeof getProvider;
  resolveBucketOrContainerName: typeof resolveBucketOrContainerName;
  supabase: SupabaseLike;
  requireAuth: typeof defaultRequireAuth;
}

const defaultDeps: Dependencies = {
  handleCors: defaultHandleCors,
  mergeCorsHeaders: defaultMergeCors,
  getProvider,
  resolveBucketOrContainerName,
  supabase: supabaseAdmin,
  requireAuth: defaultRequireAuth,
};

async function fetchContentRecord(supabase: SupabaseLike, contentId: string) {
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
      source:cs.content_source (
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

export function createFinalizeHandler(overrides: Partial<Dependencies> = {}) {
  const deps = { ...defaultDeps, ...overrides };

  return async function handler(req: Request): Promise<Response> {
    try {
      const corsResponse = deps.handleCors(req);
      if (corsResponse) return corsResponse;

      if (req.method !== "POST") {
        throw new HttpError("Method not allowed", 405);
      }

      const auth = await deps.requireAuth(req);
      const payload = csFinalizeContentRequestSchema.parse(await req.json());

      const record = await fetchContentRecord(deps.supabase, payload.content_id);
      const isOwner = auth.userId === record.created_by;
      const isAdmin = hasRole(auth, ["admin", "financeadmin"]);

      if (!isOwner && !isAdmin) {
        throw new HttpError("Forbidden", 403);
      }

      // Get the storage provider
      const provider = deps.getProvider(record.source.provider, record.source.settings);

      // Resolve bucket/container name
      const bucketOrContainer = deps.resolveBucketOrContainerName(
        record.source.settings.container_name ?? record.source.settings.bucket_name
      );

      // Check if the blob exists using the provider
      const exists = await provider.exists({
        bucketOrContainer,
        path: record.external_key,
      });

      if (!exists.exists) {
        throw new HttpError("Blob not found. Please re-upload before finalizing.", 400);
      }

      // Update content_store to mark as active
      const { error: updateError } = await deps.supabase
        .schema("cs")
        .from("content_store")
        .update({
          is_active: true,
          size_bytes: exists.size ?? record.size_bytes,
          updated_by: auth.userId,
        })
        .eq("id", record.id);

      if (updateError) {
        throw new HttpError("Failed to finalize content", 500);
      }

      return new Response(
        JSON.stringify({
          success: true,
          content_id: record.id,
          external_key: record.external_key,
          verified_size: exists.size ?? null,
        }),
        { headers: deps.mergeCorsHeaders({ "Content-Type": "application/json" }) },
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

      console.error("cs-finalize-upload error:", error);
      return new Response(JSON.stringify({ error: "Internal Server Error" }), {
        status: 500,
        headers: deps.mergeCorsHeaders({ "Content-Type": "application/json" }),
      });
    }
  };
}

export const handler = createFinalizeHandler();
