import {
  BlobSASPermissions,
  BlobServiceClient,
  StorageSharedKeyCredential,
  generateBlobSASQueryParameters,
} from "npm:@azure/storage-blob";

export type SasPermission = "r" | "w" | "rw";

const PERMISSIONS_MAP: Record<SasPermission, string> = {
  r: "r",
  w: "cw",
  rw: "rcw",
};

export interface SignedUrlResult {
  url: string;
  expiresAt: Date;
}

export function resolveContainerName(
  template: string,
  env = Deno.env.get("ENV") ?? "dev",
) {
  return template.replace(/\{env\}/g, env);
}

function getServiceClientWithCredential(connectionString: string) {
  const serviceClient = BlobServiceClient.fromConnectionString(connectionString);
  const credential = serviceClient.credential as
    | StorageSharedKeyCredential
    | undefined;

  if (!credential) {
    throw new Error("Azure credential is not available on the BlobServiceClient");
  }

  return { serviceClient, credential };
}

export function generateSignedBlobUrl(params: {
  connectionString: string;
  containerName: string;
  blobName: string;
  permissions?: SasPermission;
  expiresInMinutes?: number;
}): SignedUrlResult {
  const { serviceClient, credential } = getServiceClientWithCredential(
    params.connectionString,
  );

  const permissions = BlobSASPermissions.parse(
    PERMISSIONS_MAP[params.permissions ?? "w"],
  );

  const expiresInMinutes = params.expiresInMinutes ?? 15;
  const startsOn = new Date(Date.now() - 5 * 60 * 1000); // clock skew tolerance
  const expiresAt = new Date(Date.now() + expiresInMinutes * 60 * 1000);

  const sasToken = generateBlobSASQueryParameters(
    {
      containerName: params.containerName,
      blobName: params.blobName,
      permissions,
      startsOn,
      expiresOn: expiresAt,
    },
    credential,
  ).toString();

  const url =
    `https://${serviceClient.accountName}.blob.core.windows.net/${params.containerName}/${params.blobName}?${sasToken}`;

  return { url, expiresAt };
}

export async function blobExists(params: {
  connectionString: string;
  containerName: string;
  blobName: string;
}): Promise<{ exists: boolean; size?: number }> {
  const serviceClient = BlobServiceClient.fromConnectionString(
    params.connectionString,
  );
  const containerClient = serviceClient.getContainerClient(params.containerName);
  const blobClient = containerClient.getBlobClient(params.blobName);

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

export async function uploadBlob(params: {
  connectionString: string;
  containerName: string;
  blobName: string;
  data: Uint8Array;
  contentType?: string;
}) {
  const serviceClient = BlobServiceClient.fromConnectionString(
    params.connectionString,
  );
  const containerClient = serviceClient.getContainerClient(params.containerName);
  const blobClient = containerClient.getBlockBlobClient(params.blobName);

  await blobClient.uploadData(params.data, {
    blobHTTPHeaders: {
      blobContentType: params.contentType,
    },
  });
}
