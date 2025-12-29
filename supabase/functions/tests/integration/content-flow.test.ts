import "https://deno.land/x/dotenv/load.ts";
import {
  assert,
  assertEquals,
} from "https://deno.land/std@0.168.0/testing/asserts.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

/**
 * Integration Test for Content Flow
 * 
 * PREREQUISITE: Run `python scripts/seed.py` before running this test.
 * The test relies on:
 * - cs.content_source table with default Supabase Storage source
 * - content bucket (will be created by seed.py or lazy creation)
 * 
 * This test validates the complete content lifecycle:
 * 1. Initialize upload → 2. Upload blob → 3. Update metadata →
 * 4. Finalize upload → 5. Generate signed URL → 6. Read content
 */

// Load environment variables for integration tests
const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "http://localhost:54321";
const SUPABASE_PUBLISHABLE_KEY = Deno.env.get("SUPABASE_PUBLISHABLE_KEY")!;
const SUPABASE_SECRET_KEY = Deno.env.get("SUPABASE_SECRET_KEY")!;

Deno.test({
  name: "content flow integration test",
  async fn() {
    //1. Setup clients
    const supabase = createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY);
    const adminAuth = createClient(SUPABASE_URL, SUPABASE_SECRET_KEY, {
      auth: {
        autoRefreshToken: false,
        persistSession: false,
      },
    });

    // 2. Create test user with mock org_id in user_metadata
    const orgId = crypto.randomUUID();
    const email = `test-${crypto.randomUUID()}@example.com`;
    const password = "test-password";

    const { data: { user }, error: signUpError } = await adminAuth.auth.admin.createUser({
      email,
      password,
      email_confirm: true,
      user_metadata: {
        current_org_id: orgId,
      },
    });

    if (signUpError || !user) {
      throw new Error(`Failed to create test user: ${signUpError?.message}`);
    }

    // 3. Login as user to get token
    const { data: { session }, error: loginError } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (loginError || !session) {
      throw new Error(`Failed to login: ${loginError?.message}`);
    }

    const token = session.access_token;

    // Debug: Decode JWT to see what claims are present
    const jwtPayload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
    console.log("JWT payload:", JSON.stringify(jwtPayload, null, 2));

    const headers = {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    };

    try {
      console.log("Step 1: Upload Content (Initialize)");
      const uploadRes = await fetch(`${SUPABASE_URL}/functions/v1/cs-upload-content`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          mime_type: "text/plain",
          size_bytes: 12,
          metadata: { test: "integration" },
        }),
      });

      const uploadData = await uploadRes.json();
      assertEquals(uploadRes.status, 200, `Upload failed: ${JSON.stringify(uploadData)}`);
      assert(uploadData.content_id, "Missing content_id");
      assert(uploadData.upload_url, "Missing upload_url");
      assert(uploadData.external_key, "Missing external_key");

      const contentId = uploadData.content_id;
      
      const local_dev_kong_url = 'http://kong:8000'
      const local_kong_url = Deno.env.get("KONG_URL") || local_dev_kong_url;
      const uploadUrl = uploadData.upload_url.replace(local_dev_kong_url, local_kong_url);

      console.log("Step 2: Upload actual blob data using Supabase upload URL", uploadUrl);
      const blobContent = new TextEncoder().encode("Hello World!");
      const blobUploadRes = await fetch(uploadUrl, {
        method: "PUT",
        headers: {
          "Content-Type": "text/plain",
        },
        body: blobContent,
      });

      assertEquals(blobUploadRes.status, 200, `Blob upload failed: ${await blobUploadRes.text()}`);

      console.log("Step 3: Finalize Upload");
      const finalizeRes = await fetch(`${SUPABASE_URL}/functions/v1/cs-finalize-upload`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          content_id: contentId,
        }),
      });

      const finalizeData = await finalizeRes.json();
      console.log(finalizeData.verified_size)
      assertEquals(finalizeRes.status, 200, `Finalize failed: ${JSON.stringify(finalizeData)}`);
      assertEquals(finalizeData.success, true, "The result returned 'failure'");
      assertEquals(finalizeData.verified_size, 12);

      console.log("Step 4: Generate Signed URL (Read)");
      const signRes = await fetch(`${SUPABASE_URL}/functions/v1/cs-generate-signed-url?id=${contentId}`, {
        method: "GET",
        headers,
      });

      const signData = await signRes.json();
      assertEquals(signRes.status, 200, `Sign URL failed: ${JSON.stringify(signData)}`);
      assert(signData.signed_url, "Missing signed_url");

      console.log("Step 5. Verify Read");
      const readRes = await fetch(signData.signed_url);
      const readText = await readRes.text();
      assertEquals(readText, "Hello World!");

      console.log("Step 6: Update Content (Optional Metadata)", contentId);
      const updateRes = await fetch(`${SUPABASE_URL}/functions/v1/cs-update-content`, {
        method: "PUT",
        headers,
        body: JSON.stringify({
          content_id: contentId,
          metadata: { test: "integration", updated: true },
        }),
      });

      const updateData = await updateRes.json();
      assertEquals(updateRes.status, 200, `Update failed: ${JSON.stringify(updateData)}`);
      assertEquals(updateData.content_id, contentId);

      
      const uploadUpdateUrl = uploadData.upload_url.replace(local_dev_kong_url, local_kong_url);
      console.log("Step 7: Upload actual update blob data using Supabase upload URL", uploadUpdateUrl);
      const blobUpdateContent = new TextEncoder().encode("Hello World Updated!");
      const blobUpdateUploadRes = await fetch(uploadUpdateUrl, {
        method: "PUT",
        headers: {
          "Content-Type": "text/plain",
        },
        body: blobUpdateContent,
      });

      console.log("Step 6: Finalize Update Upload");
      const finalizeUpdateRes = await fetch(`${SUPABASE_URL}/functions/v1/cs-finalize-upload`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          content_id: contentId,
        }),
      });

      const finalizeUpdateData = await finalizeUpdateRes.json();
      assertEquals(finalizeUpdateRes.status, 200, `Finalize failed: ${JSON.stringify(finalizeUpdateData)}`);
      assertEquals(finalizeUpdateData.success, true);
      assertEquals(finalizeUpdateData.verified_size, 20);

      console.log("Step 9: Generate Signed URL (Read)");
      const signUpdateReadRes = await fetch(`${SUPABASE_URL}/functions/v1/cs-generate-signed-url?id=${contentId}`, {
        method: "GET",
        headers,
      });

      const signUpdateReadData = await signUpdateReadRes.json();
      assertEquals(signUpdateReadRes.status, 200, `Sign URL failed: ${JSON.stringify(signUpdateReadData)}`);
      assert(signUpdateReadData.signed_url, "Missing signed_url");

      console.log("10. Verify Read");
      const readUpdateRes = await fetch(signUpdateReadData.signed_url);
      const readUpdateText = await readUpdateRes.text();
      assertEquals(readUpdateText, "Hello World Updated!");

    } finally {
      // Cleanup is best-effort - we don't delete buckets or content sources
      // as they may be needed for debugging
    }
  },
});
