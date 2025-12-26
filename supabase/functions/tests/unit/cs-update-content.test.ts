import { createUpdateHandler } from "../../cs-update-content/handler.ts";
import { jsonRequest, parseJson } from "../helpers/request.ts";
import {
  createSupabaseMock,
  createAuthMock,
  createStorageProviderMock,
  noopCors,
} from "../helpers/mocks.ts";

Deno.test("cs-update-content requires content_id", async () => {
  const supabase = createSupabaseMock();
  const auth = createAuthMock();
  const provider = createStorageProviderMock();

  const handler = createUpdateHandler({
    handleCors: noopCors.handleCors,
    mergeCorsHeaders: noopCors.mergeCorsHeaders,
    supabase: supabase as any,
    requireAuth: auth.requireAuth as any,
    getProvider: () => provider as any,
    resolveBucketOrContainerName: (name: string) => name.replace("{env}", "test"),
  });

  const req = jsonRequest("https://example.com/update", "PUT", {});
  const res = await handler(req);
  const body = await parseJson(res);

  if (res.status !== 400 || body.error !== "content_id is required") {
    throw new Error(`Expected 400 content_id error, got ${res.status} ${body.error}`);
  }
});

Deno.test("cs-update-content updates metadata and returns signed URL with versioning", async () => {
  const supabase = createSupabaseMock();
  supabase._setSelectResult({
    id: "00000000-0000-0000-0000-000000000001",
    external_key: "receipts/user-123/file.png",
    mime_type: "image/png",
    size_bytes: 1024,
    checksum: "abc123",
    metadata: { original: true },
    created_by: "user-123",
    source: { 
      id: "source-1",
      provider: "azure_blob",
      settings: { container_name: "content_{env}", connection_secret: "CONN" } 
    },
  });

  const auth = createAuthMock();
  const provider = createStorageProviderMock();

  const handler = createUpdateHandler({
    handleCors: noopCors.handleCors,
    mergeCorsHeaders: noopCors.mergeCorsHeaders,
    supabase: supabase as any,
    requireAuth: auth.requireAuth as any,
    getProvider: () => provider as any,
    resolveBucketOrContainerName: (name: string) => name.replace("{env}", "test"),
  });

  Deno.env.set("CONN", "UseDevelopmentStorage=true");

  const req = jsonRequest(
    "https://example.com/update",
    "PUT",
    { content_id: "00000000-0000-0000-0000-000000000001", mime_type: "image/jpeg" },
  );

  const res = await handler(req);
  const body = await parseJson(res);

  if (res.status !== 200) {
    throw new Error(`Expected 200, got ${res.status}: ${JSON.stringify(body)}`);
  }

  if (!body.upload_url) {
    throw new Error("Missing upload_url in response");
  }

  if (!body.version_archived) {
    throw new Error("Missing version_archived in response");
  }

  // Verify that a version record was inserted
  const insertedRows = supabase._getInsertedRows();
  const versionInsert = insertedRows.find((row: any) => row.version_number !== undefined);
  if (!versionInsert) {
    throw new Error("Expected version record to be inserted");
  }
});
