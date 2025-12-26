/**
 * Supabase Storage Provider
 * 
 * Implements the StorageProvider interface for Supabase Storage.
 */

import { createClient, SupabaseClient } from "https://esm.sh/@supabase/supabase-js@2";

import type {
  StorageProvider,
  SignedUrlResult,
  UploadUrlParams,
  ReadUrlParams,
  ExistsParams,
  DeleteParams,
  ExistsResult,
  ProviderSettings,
} from "./types.ts";

export interface SupabaseStorageSettings extends ProviderSettings {
  bucket_name: string;
  connection_secret?: string; // Optional: defaults to SUPABASE_SERVICE_ROLE_KEY
}

export class SupabaseStorageProvider implements StorageProvider {
  private client: SupabaseClient;
  private bucketName: string;

  constructor(settings: SupabaseStorageSettings) {
    this.bucketName = settings.bucket_name;
    
    // Get connection secret (defaults to SUPABASE_SERVICE_ROLE_KEY)
    const connectionSecret = settings.connection_secret ?? "SUPABASE_SERVICE_ROLE_KEY";
    const serviceRoleKey = Deno.env.get(connectionSecret);
    
    if (!serviceRoleKey) {
      throw new Error(`Missing service role key for secret: ${connectionSecret}`);
    }

    const supabaseUrl = Deno.env.get("SUPABASE_URL") ?? "http://localhost:54321";
    
    this.client = createClient(supabaseUrl, serviceRoleKey, {
      auth: {
        autoRefreshToken: false,
        persistSession: false,
      },
    });
  }

  async generateReadUrl(params: ReadUrlParams): Promise<SignedUrlResult> {
    const expiresInMinutes = params.expiresInMinutes ?? 15;
    const expiresInSeconds = expiresInMinutes * 60;

    const { data, error } = await this.client.storage
      .from(params.bucketOrContainer)
      .createSignedUrl(params.path, expiresInSeconds);

    if (error || !data) {
      throw new Error(`Failed to generate read URL: ${error?.message ?? "Unknown error"}`);
    }

    const expiresAt = new Date(Date.now() + expiresInMinutes * 60 * 1000);

    return {
      url: data.signedUrl,
      expiresAt,
    };
  }

  async generateUploadUrl(params: UploadUrlParams): Promise<SignedUrlResult> {
    const expiresInMinutes = params.expiresInMinutes ?? 15;
    const expiresInSeconds = expiresInMinutes * 60;

    // Try to use createSignedUploadUrl if available
    const storage = this.client.storage.from(params.bucketOrContainer);
    
    // Check if createSignedUploadUrl exists (newer versions of supabase-js)
    if (typeof (storage as any).createSignedUploadUrl === "function") {
      const { data, error } = await (storage as any).createSignedUploadUrl(
        params.path,
        {
          upsert: true,
        }
      );

      if (error || !data) {
        throw new Error(`Failed to generate upload URL: ${error?.message ?? "Unknown error"}`);
      }

      const expiresAt = new Date(Date.now() + expiresInMinutes * 60 * 1000);

      return {
        url: data.signedUrl,
        expiresAt,
      };
    }

    // Fallback: Generate a signed URL for upload using createSignedUrl with longer expiry
    // Note: This is less secure but works with older supabase-js versions
    const { data, error } = await storage.createSignedUrl(params.path, expiresInSeconds);

    if (error || !data) {
      throw new Error(`Failed to generate upload URL: ${error?.message ?? "Unknown error"}`);
    }

    const expiresAt = new Date(Date.now() + expiresInMinutes * 60 * 1000);

    return {
      url: data.signedUrl,
      expiresAt,
    };
  }

  async exists(params: ExistsParams): Promise<ExistsResult> {
    try {
      // Try to list the file to check if it exists
      const { data, error } = await this.client.storage
        .from(params.bucketOrContainer)
        .list(this.getDirectoryPath(params.path), {
          limit: 1,
          search: this.getFileName(params.path),
        });

      if (error) {
        // If we get an error, try downloading to check existence
        const { data: downloadData, error: downloadError } = await this.client.storage
          .from(params.bucketOrContainer)
          .download(params.path);

        if (downloadError) {
          if (downloadError.message.includes("not found") || downloadError.message.includes("404")) {
            return { exists: false };
          }
          throw downloadError;
        }

        return {
          exists: true,
          size: downloadData?.size,
        };
      }

      if (!data || data.length === 0) {
        return { exists: false };
      }

      const file = data.find((f) => f.name === this.getFileName(params.path));
      
      if (!file) {
        return { exists: false };
      }

      return {
        exists: true,
        size: file.metadata?.size,
      };
    } catch (error) {
      console.error("Error checking file existence:", error);
      return { exists: false };
    }
  }

  async delete(params: DeleteParams): Promise<void> {
    const { error } = await this.client.storage
      .from(params.bucketOrContainer)
      .remove([params.path]);

    if (error) {
      throw new Error(`Failed to delete file: ${error.message}`);
    }
  }

  /**
   * Helper to extract directory path from full path
   */
  private getDirectoryPath(path: string): string {
    const lastSlash = path.lastIndexOf("/");
    return lastSlash > 0 ? path.substring(0, lastSlash) : "";
  }

  /**
   * Helper to extract filename from full path
   */
  private getFileName(path: string): string {
    const lastSlash = path.lastIndexOf("/");
    return lastSlash >= 0 ? path.substring(lastSlash + 1) : path;
  }
}
