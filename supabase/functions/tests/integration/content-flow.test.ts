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

    // 2. Create test user with org_id in user_metadata (will be picked up by auth hook)
    const email = `test-${crypto.randomUUID()}@example.com`;
    const password = "test-password";
    const testOrgId = crypto.randomUUID();
    
    const { data: { user }, error: signUpError } = await adminAuth.auth.admin.createUser({
      email,
      password,
      email_confirm: true,
      user_metadata: {
        current_org_id: testOrgId,
      },
    });

    if (signUpError || !user) {
      throw new Error(`Failed to create test user: ${signUpError?.message}`);
    }

    // 3. Create default content source for test
    const { error: sourceError } = await adminAuth
      .schema("cs")
      .from("content_source")
      .insert({
        name: "Default Supabase Storage",
        provider: "supabase_storage",
        settings: { bucket_name: "test-content" },
        is_active: true,
      });
    
    if (sourceError && !sourceError.message.includes("duplicate")) {
      console.log("Warning: Could not create content source:", sourceError.message);
    }

    // 4. Login as user to get token
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
      // 5. Step 1: Upload Content (Initialize)
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

      // 6. Step 2: Upload actual blob data using Supabase upload URL
      const blobContent = new TextEncoder().encode("Hello World!");
      const blobUploadRes = await fetch(uploadUrl, {
        method: "PUT",
        headers: {
          "Content-Type": "text/plain",
        },
        body: blobContent,
      });
      
      assertEquals(blobUploadRes.status, 200, "Blob upload failed");

      // 7. Step 3: Update Content (Optional Metadata)
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

      // 8. Step 4: Finalize Upload
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

      // 9. Step 5: Generate Signed URL (Read)
      const signRes = await fetch(`${SUPABASE_URL}/functions/v1/cs-generate-signed-url?id=${contentId}`, {
        method: "GET",
        headers,
      });

      const signData = await signRes.json();
      assertEquals(signRes.status, 200, `Sign URL failed: ${JSON.stringify(signData)}`);
      assert(signData.signed_url, "Missing signed_url");

      // 10. Verify Read
      const readRes = await fetch(signData.signed_url);
      const readText = await readRes.text();
      assertEquals(readText, "Hello World!");

    } finally {
      // Cleanup: Delete user
      await adminAuth.auth.admin.deleteUser(user.id);
    }
  },
});
