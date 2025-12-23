import {
  mergeCorsHeaders as defaultMergeCors,
  handleCors as defaultHandleCors,
} from "../_shared/cors.ts";
import {
  generateSignedBlobUrl as defaultGenerateSignedBlobUrl,
  resolveContainerName as defaultResolveContainerName,
} from "../_shared/azure-blob.ts";
import { supabaseAdmin } from "../_shared/supabase.ts";
import { HttpError, requireAuth as defaultRequireAuth } from "../_shared/auth.ts";
import { csUploadContentRequestSchema } from "@shared";
// @ts-ignore: Deno/Node interop
import { ZodError } from "zod";

const DEFAULT_PREFIX = "receipts";

function buildExternalKey(mimeType: string, userId: string) {
  const extension = mimeType.split("/")[1] ?? "bin";
  return `${DEFAULT_PREFIX}/${userId}/${crypto.randomUUID()}.${extension}`;
}

type SupabaseLike = typeof supabaseAdmin;

interface Dependencies {
  handleCors: typeof defaultHandleCors;
  mergeCorsHeaders: typeof defaultMergeCors;
  generateSignedBlobUrl: typeof defaultGenerateSignedBlobUrl;
  resolveContainerName: typeof defaultResolveContainerName;
  resolveContentSource: typeof defaultResolveContentSource;
  supabase: SupabaseLike;
  requireAuth: typeof defaultRequireAuth;
}

const defaultDeps: Dependencies = {
  handleCors: defaultHandleCors,
  mergeCorsHeaders: defaultMergeCors,
  generateSignedBlobUrl: defaultGenerateSignedBlobUrl,
  resolveContainerName: defaultResolveContainerName,
  resolveContentSource: defaultResolveContentSource,
  supabase: supabaseAdmin,
  requireAuth: defaultRequireAuth,
};

async function defaultResolveContentSource(
  supabase: SupabaseLike,
  sourceId?: string,
) {
  let query = supabase.schema("cs").from("content_source")
    .select("id, settings")
    .eq("is_active", true);

  if (sourceId) {
    query = query.eq("id", sourceId);
  } else {
    query = query.order("created_at", { ascending: true }).limit(1);
  }

  const { data, error } = await query.single();
  if (error || !data) {
    throw new HttpError("Unable to resolve content source for [" + sourceId + "]", 400);
  }

  return data as unknown as {
    id: string;
    settings: { container_name: string; connection_secret: string };
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
      const source = await deps.resolveContentSource(
        deps.supabase,
        payload.source_id,
      );

      const connectionString = Deno.env.get(source.settings.connection_secret);
      if (!connectionString) {
        throw new HttpError(
          `Missing secret ${source.settings.connection_secret}`,
          500,
        );
      }

      const containerName = deps.resolveContainerName(
        source.settings.container_name,
      );
      const externalKey = buildExternalKey(payload.mime_type, auth.userId);

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

      const sas = deps.generateSignedBlobUrl({
        connectionString,
        containerName,
        blobName: externalKey,
        permissions: "w",
        expiresInMinutes: 15,
      });

      return new Response(
        JSON.stringify({
          content_id: inserted.id,
          upload_url: sas.url,
          external_key: externalKey,
          expires_at: sas.expiresAt.toISOString(),
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
