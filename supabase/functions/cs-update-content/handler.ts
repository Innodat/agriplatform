import { handleCors as defaultHandleCors, mergeCorsHeaders as defaultMergeCors } from "../_shared/cors.ts";
import {
  generateSignedBlobUrl as defaultGenerateSignedBlobUrl,
  resolveContainerName as defaultResolveContainerName,
} from "../_shared/azure-blob.ts";
import { supabaseAdmin } from "../_shared/supabase.ts";
import { HttpError, hasRole, requireAuth as defaultRequireAuth } from "../_shared/auth.ts";
import { csUpdateContentRequestSchema } from "@shared";
import { ZodError } from "zod";

type SupabaseLike = typeof supabaseAdmin;

interface Dependencies {
  handleCors: typeof defaultHandleCors;
  mergeCorsHeaders: typeof defaultMergeCors;
  generateSignedBlobUrl: typeof defaultGenerateSignedBlobUrl;
  resolveContainerName: typeof defaultResolveContainerName;
  supabase: SupabaseLike;
  requireAuth: typeof defaultRequireAuth;
}

const defaultDeps: Dependencies = {
  handleCors: defaultHandleCors,
  mergeCorsHeaders: defaultMergeCors,
  generateSignedBlobUrl: defaultGenerateSignedBlobUrl,
  resolveContainerName: defaultResolveContainerName,
  supabase: supabaseAdmin,
  requireAuth: defaultRequireAuth,
};

async function fetchContentRecord(
  supabase: SupabaseLike,
  contentId: string,
) {
  const { data, error } = await supabase
    .schema("cs")
    .from("content_store")
    .select(
      `
      id,
      source_id,
      external_key,
      mime_type,
      created_by,
      source:cs.content_source (
        id,
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
    mime_type: string;
    created_by: string;
    source: { settings: { container_name: string; connection_secret: string } };
  };
}

export function createUpdateHandler(overrides: Partial<Dependencies> = {}) {
  const deps = { ...defaultDeps, ...overrides };

  return async function handler(req: Request): Promise<Response> {
    try {
      const corsResponse = deps.handleCors(req);
      if (corsResponse) return corsResponse;

      if (req.method !== "PUT") {
        throw new HttpError("Method not allowed", 405);
      }

      const auth = await deps.requireAuth(req);
      const payload = csUpdateContentRequestSchema.parse(await req.json());

      const record = await fetchContentRecord(deps.supabase, payload.content_id);

      const isOwner = auth.userId === record.created_by;
      const isAdmin = hasRole(auth, ["admin", "financeadmin"]);
      if (!isOwner && !isAdmin) {
        throw new HttpError("Forbidden", 403);
      }

      const connectionString = Deno.env.get(
        record.source.settings.connection_secret,
      );
      if (!connectionString) {
        throw new HttpError(
          `Missing secret ${record.source.settings.connection_secret}`,
          500,
        );
      }

      const updates: Record<string, unknown> = {
        updated_by: auth.userId,
        is_active: false,
      };

      if (payload.mime_type) updates.mime_type = payload.mime_type;
      if (payload.size_bytes !== undefined) updates.size_bytes = payload.size_bytes;
      if (payload.checksum !== undefined) updates.checksum = payload.checksum;
      if (payload.metadata !== undefined) updates.metadata = payload.metadata;

      const { error: updateError } = await deps.supabase
        .schema("cs")
        .from("content_store")
        .update(updates)
        .eq("id", record.id);

      if (updateError) {
        throw new HttpError("Failed to update content metadata", 500);
      }

      const containerName = deps.resolveContainerName(
        record.source.settings.container_name,
      );

      const sas = deps.generateSignedBlobUrl({
        connectionString,
        containerName,
        blobName: record.external_key,
        permissions: "w",
        expiresInMinutes: 15,
      });

      return new Response(
        JSON.stringify({
          content_id: record.id,
          upload_url: sas.url,
          external_key: record.external_key,
          expires_at: sas.expiresAt.toISOString(),
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

      console.error("cs-update-content error:", error);
      return new Response(JSON.stringify({ error: "Internal Server Error" }), {
        status: 500,
        headers: deps.mergeCorsHeaders({ "Content-Type": "application/json" }),
      });
    }
  };
}

export const handler = createUpdateHandler();
