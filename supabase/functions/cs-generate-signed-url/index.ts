// Follow this setup guide to integrate the Deno language server with your editor:
// https://deno.land/manual/getting_started/setup_your_environment
// This enables autocomplete, go to definition, etc.

// Setup type definitions for built-in Supabase Runtime APIs
// functions/generate-signed-url/index.ts
// functions/get-signed-url/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import {
  BlobServiceClient,
  generateBlobSASQueryParameters,
  BlobSasPermissions,
  StorageSharedKeyCredential,
} from "npm:@azure/storage-blob";

const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const supabase = createClient(supabaseUrl, supabaseServiceKey);

serve(async (req: Request) => {
  try {
    const { searchParams } = new URL(req.url);
    const contentStoreId = searchParams.get("id");
    if (!contentStoreId) {
      return new Response("Missing content_store id", { status: 400 });
    }

    // 1. Look up content_store + content_source
    const { data, error } = await supabase
      .from("cs.content_store")
      .select(`
        external_key,
        source:cs.content_source (
          settings
        )
      `)
      .eq("id", contentStoreId)
      .single();

    if (error || !data) {
      return new Response("Not found", { status: 404 });
    }

    const externalKey = data.external_key;
    const settings = data.source.settings;
    const secretName = settings.connection_secret;
    const containerName = settings.container_name;

    // 2. Resolve connection string from Vault (injected as env var)
    const connStr = Deno.env.get(secretName);
    if (!connStr) {
      return new Response(`Secret ${secretName} not found`, { status: 500 });
    }

    // 3. Connect to Azure Blob
    const blobServiceClient = BlobServiceClient.fromConnectionString(connStr);
    const accountName = blobServiceClient.accountName;
    const accountKey = (blobServiceClient as any).credential.accountKey;
    const sharedKeyCredential = new StorageSharedKeyCredential(
      accountName,
      accountKey,
    );

    // 4. Generate SAS token (read-only, 15 min)
    const sasToken = generateBlobSASQueryParameters(
      {
        containerName,
        blobName: externalKey,
        permissions: BlobSasPermissions.parse("r"),
        startsOn: new Date(),
        expiresOn: new Date(new Date().valueOf() + 15 * 60 * 1000),
      },
      sharedKeyCredential,
    ).toString();

    const url =
      `https://${accountName}.blob.core.windows.net/${containerName}/${externalKey}?${sasToken}`;

    return new Response(JSON.stringify({ signed_url: url }), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (err) {
    return new Response(`Error: ${err.message}`, { status: 500 });
  }
});

/* To invoke locally:

  1. Run `supabase start` (see: https://supabase.com/docs/reference/cli/supabase-start)
  2. Make an HTTP request:

  curl -i --location --request POST 'http://127.0.0.1:54321/functions/v1/cs-generate-signed-url' \
    --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0' \
    --header 'Content-Type: application/json' \
    --data '{"name":"Functions"}'

*/
