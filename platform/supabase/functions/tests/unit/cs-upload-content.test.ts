import { handleUploadContent } from "../../cs-upload-content/handler.ts";
import { jsonRequest, parseJson } from "../helpers/request.ts";
import {
  createSupabaseMock,
  createAuthMock,
  createStorageProviderMock,
} from "../helpers/mocks.ts";
import { noopCors } from "../helpers/mocks.ts";
import { supabaseAdmin } from "../../_shared/supabase.ts";

Deno.test("cs-upload-content rejects requests without mime_type", async () => {
  const supabase = createSupabaseMock();
  const auth = createAuthMock();
  const provider = createStorageProviderMock();

  const req = jsonRequest("https://example.com", "POST", {});
  const res = await handleUploadContent(req, {
    supabase: supabase as any,
    requireAuth: auth.requireAuth as any,
    getProvider: () => provider as any,
    resolveBucketOrContainerName: (name: string) => name.replace("{env}", "test"),
    handleCors: noopCors.handleCors,
    mergeCorsHeaders: noopCors.mergeCorsHeaders,
  });
  const body = await parseJson(res);

  if (res.status !== 400) {
    throw new Error(`Expected status 400, received ${res.status}`);
  }

  if (body.error !== "mime_type is required") {
    throw new Error(`Unexpected error message: ${body.error}`);
  }
});

Deno.test("cs-upload-content creates record and returns signed URL", async () => {
  const supabase = createSupabaseMock();
  const auth = createAuthMock();
  const provider = createStorageProviderMock();

  // Mock the database queries:
  // 1. Get org settings (no content_source_id set, so will fall back to default)
  // 2. Get default content source by name
  // 3. Get the actual content source details
  supabase._setSelectResults([
    { 
      row: { id: "org-123", settings: {} }, 
      error: null 
    },
    { 
      row: { id: "source-default", name: "Default Supabase Storage", deleted_at: null }, 
      error: null 
    },
    { 
      row: { 
        id: "source-default", 
        settings: { bucket_name: "content-test" },
        deleted_at: null,
        provider: "supabase_storage",
        name: "Default Supabase Storage"
      }, 
      error: null 
    },
  ]);

  const req = jsonRequest(
    "https://example.com",
    "POST",
    {
      mime_type: "image/png",
      size_bytes: 123,
    },
  );

  const res = await handleUploadContent(req, {
    supabase: supabase as any,
    requireAuth: auth.requireAuth as any,
    getProvider: () => provider as any,
    resolveBucketOrContainerName: (name: string) => name.replace("{env}", "test"),
    handleCors: noopCors.handleCors,
    mergeCorsHeaders: noopCors.mergeCorsHeaders,
  });
  if (res.status !== 200) {
    const body = await parseJson(res);
    throw new Error(
      `Expected status 200, received ${res.status} (${JSON.stringify(body)})`,
    );
  }

  const body = await parseJson(res);
  if (!body.content_id || !body.upload_url) {
    throw new Error("Response missing content_id or upload_url");
  }
});
