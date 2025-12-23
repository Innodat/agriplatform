import { createFinalizeHandler } from "../../cs-finalize-upload/handler.ts";
import { jsonRequest, parseJson } from "../helpers/request.ts";
import {
  createSupabaseMock,
  createAuthMock,
  createAzureMock,
  noopCors,
} from "../helpers/mocks.ts";

Deno.test("cs-finalize-upload requires content_id", async () => {
  const handler = createFinalizeHandler({
    handleCors: noopCors.handleCors,
    mergeCorsHeaders: noopCors.mergeCorsHeaders,
    supabase: createSupabaseMock() as any,
    requireAuth: createAuthMock().requireAuth as any,
    blobExists: createAzureMock().blobExists,
    resolveContainerName: createAzureMock().resolveContainerName,
  });

  const req = jsonRequest("https://example.com/finalize", "POST", {});
  const res = await handler(req);
  const body = await parseJson(res);

  if (res.status !== 400 || body.error !== "content_id is required") {
    throw new Error(`Expected 400 content_id error, got ${res.status} ${body.error}`);
  }
});

Deno.test("cs-finalize-upload verifies blob and marks active", async () => {
  const supabase = createSupabaseMock();
  supabase._setSelectResult({
    id: "00000000-0000-0000-0000-000000000001",
    external_key: "receipts/user-123/file.jpg",
    size_bytes: 512,
    created_by: "user-123",
    source: { settings: { container_name: "content_{env}", connection_secret: "CONN" } },
  });

  const auth = createAuthMock();
  const azure = createAzureMock();

  const handler = createFinalizeHandler({
    handleCors: noopCors.handleCors,
    mergeCorsHeaders: noopCors.mergeCorsHeaders,
    supabase: supabase as any,
    requireAuth: auth.requireAuth as any,
    blobExists: azure.blobExists,
    resolveContainerName: azure.resolveContainerName,
  });

  Deno.env.set("CONN", "UseDevelopmentStorage=true");

  const req = jsonRequest(
    "https://example.com/finalize",
    "POST",
    { content_id: "00000000-0000-0000-0000-000000000001" },
  );

  const res = await handler(req);
  const body = await parseJson(res);

  if (res.status !== 200) {
    throw new Error(`Expected 200, got ${res.status}: ${JSON.stringify(body)}`);
  }

  if (!body.success || body.content_id !== "00000000-0000-0000-0000-000000000001") {
    throw new Error("Finalize response missing success or content_id");
  }
});
