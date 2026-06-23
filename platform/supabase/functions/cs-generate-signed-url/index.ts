import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { handleCors, mergeCorsHeaders } from "../_shared/cors.ts";
import { supabaseAdmin } from "../_shared/supabase.ts";
import { HttpError, hasRole, requireAuth } from "../_shared/auth.ts";
import { csGenerateSignedUrlParamsSchema } from "@shared";
import { ZodError } from "zod";
import { getProvider, resolveBucketOrContainerName } from "../_shared/storage-providers/registry.ts";

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
        deleted_at,
        created_by,
        source:content_source (
          provider,
          settings
        )
      `,
      )
      .eq("id", contentStoreId)
      .single();

    if (error || !data) {
      throw new HttpError("Not found", 404);
    }

    const record = data as unknown as {
      id: string;
      external_key: string;
      deleted_at: boolean;
      created_by: string;
      source: {
        provider: string;
        settings: Record<string, any>;
      };
    };

    if (record.deleted_at != null) {
      throw new HttpError("Content not finalized", 409);
    }

    const isOwner = record.created_by === auth.userId;
    const isAdmin = hasRole(auth, ["admin", "financeadmin"]);
    if (!isOwner && !isAdmin) {
      throw new HttpError("Forbidden", 403);
    }

    // Get the storage provider
    const provider = getProvider(record.source.provider, record.source.settings);

    // Resolve bucket/container name
    const bucketOrContainer = resolveBucketOrContainerName(
      record.source.settings.container_name ?? record.source.settings.bucket_name
    );

    // Generate read URL using the provider
    const readUrlResult = await provider.generateReadUrl({
      bucketOrContainer,
      path: record.external_key,
      permissions: "r",
      expiresInMinutes: 15,
    });

    return new Response(
      JSON.stringify({
        signed_url: readUrlResult.url,
        expires_at: readUrlResult.expiresAt.toISOString(),
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
