import "https://deno.land/x/dotenv/load.ts";
import {
  assert,
  assertEquals,
} from "https://deno.land/std@0.168.0/testing/asserts.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// Load environment variables for integration tests
const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "http://localhost:54321";
const SUPABASE_PUBLISHABLE_KEY = Deno.env.get("SUPABASE_PUBLISHABLE_KEY")!;
const SUPABASE_SECRET_KEY = Deno.env.get("SUPABASE_SECRET_KEY")!;

Deno.test({
  name: "content flow integration test",
  async fn() {
    // 1. Setup clients
    const supabase = createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY);
    const adminAuth = createClient(SUPABASE_URL, SUPABASE_SECRET_KEY, {
      auth: {
        autoRefreshToken: false,
        persistSession: false,
      },
    });

    // 2. Create test user
    const email = `test-${crypto.randomUUID()}@example.com`;
    const password = "test-password";
    const { data: { user }, error: signUpError } = await adminAuth.auth.admin.createUser({
      email,
      password,
      email_confirm: true,
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
    const headers = {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    };

    try {
      // 4. Step 1: Upload Content (Initialize)
      const uploadRes = await fetch(`${SUPABASE_URL}/functions/v1/cs-upload-content`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          // source_id is now determined from org settings (from JWT token)
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
      const uploadUrl = uploadData.upload_url;

      // 5. Step 2: Upload actual blob data to Azure (Azurite)
      // The uploadUrl is a SAS URL. We can PUT to it.
      const blobContent = new TextEncoder().encode("Hello World!");
      const blobUploadRes = await fetch(uploadUrl, {
        method: "PUT",
        headers: {
          "x-ms-blob-type": "BlockBlob",
          "Content-Type": "text/plain",
        },
        body: blobContent,
      });
      
      assertEquals(blobUploadRes.status, 201, "Blob upload failed");

      // 6. Step 3: Update Content (Optional Metadata)
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

      // 7. Step 4: Finalize Upload
      const finalizeRes = await fetch(`${SUPABASE_URL}/functions/v1/cs-finalize-upload`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          content_id: contentId,
        }),
      });

      const finalizeData = await finalizeRes.json();
      assertEquals(finalizeRes.status, 200, `Finalize failed: ${JSON.stringify(finalizeData)}`);
      assertEquals(finalizeData.success, true);
      assertEquals(finalizeData.verified_size, 12);

      // 8. Step 5: Generate Signed URL (Read)
      const signRes = await fetch(`${SUPABASE_URL}/functions/v1/cs-generate-signed-url?id=${contentId}`, {
        method: "GET",
        headers,
      });

      const signData = await signRes.json();
      assertEquals(signRes.status, 200, `Sign URL failed: ${JSON.stringify(signData)}`);
      assert(signData.signed_url, "Missing signed_url");

      // 9. Verify Read
      const readRes = await fetch(signData.signed_url);
      const readText = await readRes.text();
      assertEquals(readText, "Hello World!");

    } finally {
      // Cleanup: Delete user
      await adminAuth.auth.admin.deleteUser(user.id);
    }
  },
});
