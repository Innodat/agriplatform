import { handleCors as defaultHandleCors, mergeCorsHeaders as defaultMergeCors } from "../_shared/cors.ts";
import {
  blobExists as defaultBlobExists,
  resolveContainerName as defaultResolveContainerName,
} from "../_shared/azure-blob.ts";
import { supabaseAdmin } from "../_shared/supabase.ts";
import { HttpError, hasRole, requireAuth as defaultRequireAuth } from "../_shared/auth.ts";
import { csFinalizeContentRequestSchema } from "@shared";
import { ZodError } from "zod";

type SupabaseLike = typeof supabaseAdmin;

interface Dependencies {
  handleCors: typeof defaultHandleCors;
  mergeCorsHeaders: typeof defaultMergeCors;
  blobExists: typeof defaultBlobExists;
  resolveContainerName: typeof defaultResolveContainerName;
  supabase: SupabaseLike;
  requireAuth: typeof defaultRequireAuth;
}

const defaultDeps: Dependencies = {
  handleCors: defaultHandleCors,
  mergeCorsHeaders: defaultMergeCors,
  blobExists: defaultBlobExists,
  resolveContainerName: defaultResolveContainerName,
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
    source: { settings: { container_name: string; connection_secret: string } };
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

      const connectionString = Deno.env.get(
        record.source.settings.connection_secret,
      );
      if (!connectionString) {
        throw new HttpError(
          `Missing secret ${record.source.settings.connection_secret}`,
          500,
        );
      }

      const containerName = deps.resolveContainerName(
        record.source.settings.container_name,
      );

      const exists = await deps.blobExists({
        connectionString,
        containerName,
        blobName: record.external_key,
      });

      if (!exists.exists) {
        throw new HttpError("Blob not found. Please re-upload before finalizing.", 400);
      }

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
