import { createUploadHandler } from "../../cs-upload-content/handler.ts";
import { jsonRequest, parseJson } from "../helpers/request.ts";
import {
  createSupabaseMock,
  createAuthMock,
  createStorageProviderMock,
} from "../helpers/mocks.ts";

import { noopCors } from "../helpers/mocks.ts";

Deno.test("cs-upload-content rejects requests without mime_type", async () => {
  const supabase = createSupabaseMock();
  const auth = createAuthMock();
  const provider = createStorageProviderMock();

  const handler = createUploadHandler({
    handleCors: noopCors.handleCors,
    mergeCorsHeaders: noopCors.mergeCorsHeaders,
    supabase: supabase as any,
    requireAuth: auth.requireAuth as any,
    getProvider: () => provider as any,
    resolveBucketOrContainerName: (name: string) => name.replace("{env}", "test"),
    resolveContentSource: () =>
      Promise.resolve({
        id: "source-1",
        provider: "azure_blob",
        name: "Test Source",
        is_active: true,
        settings: { container_name: "content_{env}", connection_secret: "CONN" },
      }),
  });

  const req = jsonRequest("https://example.com", "POST", {});
  const res = await handler(req);
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

  const handler = createUploadHandler({
    handleCors: noopCors.handleCors,
    mergeCorsHeaders: noopCors.mergeCorsHeaders,
    supabase: supabase as any,
    requireAuth: auth.requireAuth as any,
    getProvider: () => provider as any,
    resolveBucketOrContainerName: (name: string) => name.replace("{env}", "test"),
    resolveContentSource: () =>
      Promise.resolve({
        id: "source-1",
        provider: "azure_blob",
        name: "Test Source",
        is_active: true,
        settings: { container_name: "content_{env}", connection_secret: "CONN" },
      }),
  });

  Deno.env.set("CONN", "UseDevelopmentStorage=true");

  const req = jsonRequest(
    "https://example.com",
    "POST",
    {
      mime_type: "image/png",
      size_bytes: 123,
    },
  );

  const res = await handler(req);
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
