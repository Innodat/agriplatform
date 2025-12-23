import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { handleCors, mergeCorsHeaders } from "../_shared/cors.ts";
import {
  generateSignedBlobUrl,
  resolveContainerName,
} from "../_shared/azure-blob.ts";
import { supabaseAdmin } from "../_shared/supabase.ts";
import { HttpError, hasRole, requireAuth } from "../_shared/auth.ts";
import { csGenerateSignedUrlParamsSchema } from "@shared";
import { ZodError } from "zod";

serve(async (req) => {
  try {
    const corsResponse = handleCors(req);
    if (corsResponse) return corsResponse;

    if (req.method !== "GET") {
      throw new HttpError("Method not allowed", 405);
    }

    const { searchParams } = new URL(req.url);
    const params = csGenerateSignedUrlParamsSchema.parse({
      id: searchParams.get("id"),
    });
    const contentStoreId = params.id;

    const auth = await requireAuth(req);

    const { data, error } = await supabaseAdmin
      .schema("cs")
      .from("content_store")
      .select(
        `
        id,
        external_key,
        is_active,
        created_by,
        source:cs.content_source (
          settings
        )
      `,
      )
      .eq("id", contentStoreId)
      .single();

    if (error || !data) {
      throw new HttpError("Not found", 404);
    }

    if (!data.is_active) {
      throw new HttpError("Content not finalized", 409);
    }

    const isOwner = data.created_by === auth.userId;
    const isAdmin = hasRole(auth, ["admin", "financeadmin"]);
    if (!isOwner && !isAdmin) {
      throw new HttpError("Forbidden", 403);
    }

    const settings = data.source.settings;
    const secretName = settings.connection_secret;
    const connectionString = Deno.env.get(secretName);
    if (!connectionString) {
      throw new HttpError(`Secret ${secretName} not found`, 500);
    }

    const containerName = resolveContainerName(settings.container_name);

    const sas = generateSignedBlobUrl({
      connectionString,
      containerName,
      blobName: data.external_key,
      permissions: "r",
      expiresInMinutes: 15,
    });

    return new Response(
      JSON.stringify({
        signed_url: sas.url,
        expires_at: sas.expiresAt.toISOString(),
      }),
      {
        headers: mergeCorsHeaders({ "Content-Type": "application/json" }),
      },
    );
  } catch (error) {
    if (error instanceof ZodError) {
      const issue = error.issues[0];
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

    console.error("cs-generate-signed-url error:", error);
    return new Response(JSON.stringify({ error: "Internal Server Error" }), {
      status: 500,
      headers: mergeCorsHeaders({ "Content-Type": "application/json" }),
    });
  }
});
