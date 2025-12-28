import { handleFinalizeUpload } from "../../cs-finalize-upload/handler.ts";
import { jsonRequest, parseJson } from "../helpers/request.ts";
import {
  createSupabaseMock,
  createAuthMock,
  createStorageProviderMock,
  noopCors,
} from "../helpers/mocks.ts";

Deno.test("cs-finalize-upload requires content_id", async () => {
  const supabase = createSupabaseMock();
  const auth = createAuthMock();
  const provider = createStorageProviderMock();

  const req = jsonRequest("https://example.com/finalize", "POST", {});
  const res = await handleFinalizeUpload(req, {
    supabase: supabase as any,
    requireAuth: auth.requireAuth as any,
    getProvider: () => provider as any,
    resolveBucketOrContainerName: (name: string) => name.replace("{env}", "test"),
    handleCors: noopCors.handleCors,
    mergeCorsHeaders: noopCors.mergeCorsHeaders,
  });
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
    source: { 
      id: "source-1",
      provider: "azure_blob",
      settings: { container_name: "content_{env}", connection_secret: "CONN" } 
    },
  });

  const auth = createAuthMock();
  const provider = createStorageProviderMock();

  const req = jsonRequest(
    "https://example.com/finalize",
    "POST",
    { content_id: "00000000-0000-0000-0000-000000000001" },
  );

  const res = await handleFinalizeUpload(req, {
    supabase: supabase as any,
    requireAuth: auth.requireAuth as any,
    getProvider: () => provider as any,
    resolveBucketOrContainerName: (name: string) => name.replace("{env}", "test"),
    handleCors: noopCors.handleCors,
    mergeCorsHeaders: noopCors.mergeCorsHeaders,
  });
  const body = await parseJson(res);

  if (res.status !== 200) {
    throw new Error(`Expected 200, got ${res.status}: ${JSON.stringify(body)}`);
  }

  if (!body.success || body.content_id !== "00000000-0000-0000-0000-000000000001") {
    throw new Error("Finalize response missing success or content_id");
  }
});
