/**
 * Azure Blob Storage Provider
 * 
 * Implements the StorageProvider interface for Azure Blob Storage.
 */

import {
  BlobSASPermissions,
  BlobServiceClient,
  StorageSharedKeyCredential,
  generateBlobSASQueryParameters,
} from "npm:@azure/storage-blob";

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

const PERMISSIONS_MAP = {
  r: "r",
  w: "cw",
  rw: "rcw",
};

export interface AzureBlobSettings extends ProviderSettings {
  connection_secret: string;
  container_name: string;
  account_name?: string;
}

export class AzureBlobProvider implements StorageProvider {
  private connectionString: string;
  private serviceClient: BlobServiceClient;
  private credential: StorageSharedKeyCredential;

  constructor(settings: AzureBlobSettings) {
    const connectionSecret = settings.connection_secret;
    this.connectionString = Deno.env.get(connectionSecret) ?? "";
    
    if (!this.connectionString) {
      throw new Error(`Missing connection string for secret: ${connectionSecret}`);
    }

    this.serviceClient = BlobServiceClient.fromConnectionString(this.connectionString);
    const credential = this.serviceClient.credential as StorageSharedKeyCredential | undefined;

    if (!credential) {
      throw new Error("Azure credential is not available on the BlobServiceClient");
    }

    this.credential = credential;
  }

  async generateReadUrl(params: ReadUrlParams): Promise<SignedUrlResult> {
    const permissions = BlobSASPermissions.parse(
      PERMISSIONS_MAP[params.permissions ?? "r"]
    );

    const expiresInMinutes = params.expiresInMinutes ?? 15;
    const startsOn = new Date(Date.now() - 5 * 60 * 1000); // clock skew tolerance
    const expiresAt = new Date(Date.now() + expiresInMinutes * 60 * 1000);

    const sasToken = generateBlobSASQueryParameters(
      {
        containerName: params.bucketOrContainer,
        blobName: params.path,
        permissions,
        startsOn,
        expiresOn: expiresAt,
      },
      this.credential
    ).toString();

    const url = `https://${this.serviceClient.accountName}.blob.core.windows.net/${params.bucketOrContainer}/${params.path}?${sasToken}`;

    return { url, expiresAt };
  }

  async generateUploadUrl(params: UploadUrlParams): Promise<SignedUrlResult> {
    const permissions = BlobSASPermissions.parse(PERMISSIONS_MAP.w);

    const expiresInMinutes = params.expiresInMinutes ?? 15;
    const startsOn = new Date(Date.now() - 5 * 60 * 1000); // clock skew tolerance
    const expiresAt = new Date(Date.now() + expiresInMinutes * 60 * 1000);

    const sasToken = generateBlobSASQueryParameters(
      {
        containerName: params.bucketOrContainer,
        blobName: params.path,
        permissions,
        startsOn,
        expiresOn: expiresAt,
      },
      this.credential
    ).toString();

    const url = `https://${this.serviceClient.accountName}.blob.core.windows.net/${params.bucketOrContainer}/${params.path}?${sasToken}`;

    return { url, expiresAt };
  }

  async exists(params: ExistsParams): Promise<ExistsResult> {
    const containerClient = this.serviceClient.getContainerClient(params.bucketOrContainer);
    const blobClient = containerClient.getBlobClient(params.path);

    try {
      const properties = await blobClient.getProperties();
      return {
        exists: true,
        size: properties.contentLength ?? undefined,
      };
    } catch (error) {
      if (
        typeof error === "object" &&
        error !== null &&
        "statusCode" in error &&
        (error as { statusCode?: number }).statusCode === 404
      ) {
        return { exists: false };
      }
      throw error;
    }
  }

  async delete(params: DeleteParams): Promise<void> {
    const containerClient = this.serviceClient.getContainerClient(params.bucketOrContainer);
    const blobClient = containerClient.getBlockBlobClient(params.path);
    
    await blobClient.delete();
  }
}

/**
 * Helper function to resolve container name with environment variable substitution
 */
export function resolveContainerName(
  template: string,
  env = Deno.env.get("ENV") ?? "dev"
): string {
  return template.replace(/\{env\}/g, env);
}
