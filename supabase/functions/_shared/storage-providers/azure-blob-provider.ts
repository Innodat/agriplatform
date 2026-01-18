/**
 * Azure Blob Storage Provider
 * 
 * Implements the StorageProvider interface for Azure Blob Storage.
 */

import {
  BlobSASPermissions,
  SASProtocol,
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
    const startsOn = new Date(Date.now() - 15 * 60 * 1000); // clock skew tolerance
    const expiresAt = new Date(Date.now() + expiresInMinutes * 60 * 1000);

    const sasToken = generateBlobSASQueryParameters(
      {
        containerName: params.bucketOrContainer,
        blobName: params.path,
        permissions,
        startsOn,
        expiresOn: expiresAt,
        protocol: SASProtocol.Https, // restrict to HTTPS
      },
      this.credential
    ).toString();

    const url = `https://${this.serviceClient.accountName}.blob.core.windows.net/${params.bucketOrContainer}/${params.path}?${sasToken}`;

    return { url, expiresAt };
  }

  async generateUploadUrl(params: UploadUrlParams): Promise<SignedUrlResult> {
    const permissions = BlobSASPermissions.parse(PERMISSIONS_MAP.w);

    const expiresInMinutes = params.expiresInMinutes ?? 15;
    const startsOn = new Date(Date.now() - 15 * 60 * 1000); // clock skew tolerance
    const expiresAt = new Date(Date.now() + expiresInMinutes * 60 * 1000);

    const sasToken = generateBlobSASQueryParameters(
      {
        containerName: params.bucketOrContainer,
        blobName: params.path,
        permissions,
        startsOn,
        expiresOn: expiresAt,
        protocol: SASProtocol.Https, // restrict to HTTPS
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

  async ensureBucketExists(params: {
    bucketOrContainer: string;
    isPublic?: boolean;
  }): Promise<void> {
    const env = Deno.env.get("ENV") ?? "dev";
    
    // Only create containers in dev environment (with Azurite)
    if (env !== "dev" && env !== "development") {
      console.log(`Skipping container creation in ${env} environment (not dev)`);
      return;
    }

    try {
      const containerClient = this.serviceClient.getContainerClient(params.bucketOrContainer);
      
      // Use createIfNotExists - handles the case where it already exists
      await containerClient.createIfNotExists();
      
      console.log(`Created or verified container ${params.bucketOrContainer} exists (dev environment)`);
    } catch (error) {
      // Handle gracefully - container might already exist
      if (error instanceof Error) {
        const errorStr = error.message.toLowerCase();
        if (errorStr.includes("container already exists") || 
            errorStr.includes("containerbeingcreated")) {
          console.log(`Container ${params.bucketOrContainer} already exists, skipping creation`);
          return;
        }
      }
      throw error;
    }
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
