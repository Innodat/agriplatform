import { createUpdateHandler } from "../../cs-update-content/handler.ts";
import { jsonRequest, parseJson } from "../helpers/request.ts";
import {
  createSupabaseMock,
  createAuthMock,
  createAzureMock,
  noopCors,
} from "../helpers/mocks.ts";

Deno.test("cs-update-content requires content_id", async () => {
  const supabase = createSupabaseMock();
  const auth = createAuthMock();
  const azure = createAzureMock();

  const handler = createUpdateHandler({
    handleCors: noopCors.handleCors,
    mergeCorsHeaders: noopCors.mergeCorsHeaders,
    supabase: supabase as any,
    requireAuth: auth.requireAuth as any,
    generateSignedBlobUrl: azure.generateSignedBlobUrl,
    resolveContainerName: azure.resolveContainerName,
  });

  const req = jsonRequest("https://example.com/update", "PUT", {});
  const res = await handler(req);
  const body = await parseJson(res);

  if (res.status !== 400 || body.error !== "content_id is required") {
    throw new Error(`Expected 400 content_id error, got ${res.status} ${body.error}`);
  }
});

Deno.test("cs-update-content updates metadata and returns signed URL", async () => {
  const supabase = createSupabaseMock();
  supabase._setSelectResult({
    id: "00000000-0000-0000-0000-000000000001",
    external_key: "receipts/user-123/file.png",
    created_by: "user-123",
    source: { settings: { container_name: "content_{env}", connection_secret: "CONN" } },
  });

  const auth = createAuthMock();
  const azure = createAzureMock();

  const handler = createUpdateHandler({
    handleCors: noopCors.handleCors,
    mergeCorsHeaders: noopCors.mergeCorsHeaders,
    supabase: supabase as any,
    requireAuth: auth.requireAuth as any,
    generateSignedBlobUrl: azure.generateSignedBlobUrl,
    resolveContainerName: azure.resolveContainerName,
  });

  Deno.env.set("CONN", "UseDevelopmentStorage=true");

  const req = jsonRequest(
    "https://example.com/update",
    "PUT",
    { content_id: "00000000-0000-0000-0000-000000000001", mime_type: "image/png" },
  );

  const res = await handler(req);
  const body = await parseJson(res);

  if (res.status !== 200) {
    throw new Error(`Expected 200, got ${res.status}: ${JSON.stringify(body)}`);
  }

  if (!body.upload_url) {
    throw new Error("Missing upload_url in response");
  }
});
