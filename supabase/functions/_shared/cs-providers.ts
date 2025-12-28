
interface StorageProvider {
  upload(file: Buffer, path: string): Promise<string>;
  delete(path: string): Promise<void>;
}

class AzureBlobProvider implements StorageProvider {
  async upload(file: Buffer, path: string) {
    // Azure upload logic
    return `azure://${path}`;
  }
  async delete(path: string) {
    // Azure delete logic
  }
}

class SupabaseS3Provider implements StorageProvider {
  async upload(file: Buffer, path: string) {
    // Supabase S3 upload logic
    return `supabase://${path}`;
  }
  async delete(path: string) {
    // Supabase delete logic
  }
}

const providers: Record<string, StorageProvider> = {
  azure_blob: new AzureBlobProvider(),
  supabase_s3: new SupabaseS3Provider(),
  // later: aws_s3, gcs, etc.
};

// Usage:
const provider = providers[data.provider];
await provider.upload(fileBuffer, 'path/to/file');
