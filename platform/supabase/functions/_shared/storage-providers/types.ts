/**
 * Storage Provider Types
 * 
 * Defines the interface for storage providers (Azure Blob, Supabase Storage, etc.)
 * to enable multi-provider content storage architecture.
 */

export type Permission = 'r' | 'w' | 'rw';

export interface SignedUrlResult {
  url: string;
  expiresAt: Date;
}

export interface UploadUrlParams {
  bucketOrContainer: string;
  path: string;
  contentType?: string;
  expectedSizeBytes?: number;
  checksumBase64?: string;
  expiresInMinutes?: number; // default 15
}

export interface ReadUrlParams {
  bucketOrContainer: string;
  path: string;
  expiresInMinutes?: number;
  permissions?: Permission; // typically 'r'
}

export interface ExistsParams {
  bucketOrContainer: string;
  path: string;
}

export interface DeleteParams {
  bucketOrContainer: string;
  path: string;
}

export interface ExistsResult {
  exists: boolean;
  size?: number;
}

/**
 * StorageProvider interface
 * 
 * All storage providers must implement this interface to be compatible
 * with the content store system.
 */
export interface StorageProvider {
  /**
   * Generate a signed URL for reading content
   */
  generateReadUrl(params: ReadUrlParams): Promise<SignedUrlResult>;

  /**
   * Generate a signed URL for uploading content
   */
  generateUploadUrl(params: UploadUrlParams): Promise<SignedUrlResult>;

  /**
   * Check if content exists at given path
   */
  exists(params: ExistsParams): Promise<ExistsResult>;

  /**
   * Delete content at given path
   */
  delete(params: DeleteParams): Promise<void>;

  /**
   * Ensure bucket/container exists, create if it doesn't
   * Optional method - providers can implement if they support creation
   */
  ensureBucketExists?(params: {
    bucketOrContainer: string;
    isPublic?: boolean;
  }): Promise<void>;
}

/**
 * Provider settings type (flexible for different provider configurations)
 */
export type ProviderSettings = Record<string, unknown>;
