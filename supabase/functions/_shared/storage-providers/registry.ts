/**
 * Storage Provider Registry
 * 
 * Factory for creating storage provider instances based on provider type.
 */

import type { StorageProvider, ProviderSettings } from "./types.ts";
import { AzureBlobProvider, resolveContainerName, type AzureBlobSettings } from "./azure-blob-provider.ts";
import { SupabaseStorageProvider, type SupabaseStorageSettings } from "./supabase-provider.ts";

/**
 * Get a storage provider instance based on provider name and settings
 * 
 * @param providerName - The provider type (e.g., 'azure_blob', 'supabase_storage')
 * @param settings - Provider-specific configuration settings
 * @returns StorageProvider instance
 * @throws Error if provider is unknown
 */
export function getProvider(
  providerName: string,
  settings: ProviderSettings
): StorageProvider {
  switch (providerName) {
    case "azure_blob":
      return new AzureBlobProvider(settings as AzureBlobSettings);
    
    case "supabase_storage":
      return new SupabaseStorageProvider(settings as SupabaseStorageSettings);
    
    default:
      throw new Error(`Unknown storage provider: ${providerName}`);
  }
}

/**
 * Helper function to resolve bucket/container name with environment variable substitution
 * Works for both Azure containers and Supabase buckets
 * 
 * @param template - Template string with {env} placeholder
 * @param env - Environment name (defaults to ENV env var or 'dev')
 * @returns Resolved bucket/container name
 */
export function resolveBucketOrContainerName(
  template: string,
  env = Deno.env.get("ENV") ?? "dev"
): string {
  return resolveContainerName(template, env);
}

// Re-export types for convenience
export type { StorageProvider, ProviderSettings } from "./types.ts";
