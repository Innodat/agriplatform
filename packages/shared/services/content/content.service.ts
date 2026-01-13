/**
 * Content Service for uploading images to the content store
 * Handles the 3-step upload process:
 * 1. Request upload URL (cs-upload-content)
 * 2. Upload to presigned URL
 * 3. Finalize upload (cs-finalize-upload)
 */

import { getImageInfo, uriToArrayBuffer } from '../../lib/image-utils';

export interface UploadImageResult {
  contentId: string;
  externalKey: string;
}

export interface UploadImageOptions {
  supabaseUrl: string;
  accessToken: string;
  onProgress?: (progress: number) => void;
}

/**
 * Upload an image to the content store
 * 
 * @param imageUri - Local URI of the image to upload
 * @param options - Supabase configuration and optional progress callback
 * @returns Object containing contentId and externalKey
 * @throws Error if upload fails at any stage
 */
export async function uploadImage(
  imageUri: string,
  options: UploadImageOptions
): Promise<UploadImageResult> {
  const { supabaseUrl, accessToken, onProgress } = options;

  try {
    // Step 1: Get image info (MIME type, size)
    const { mimeType, sizeBytes } = await getImageInfo(imageUri);
    onProgress?.(10);

    // Step 2: Request upload URL from cs-upload-content edge function
    const uploadContentResponse = await requestUploadUrl(
      supabaseUrl,
      accessToken,
      {
        mime_type: mimeType,
        size_bytes: sizeBytes || undefined,
        checksum: undefined, // Optional: can add checksum for data integrity
        metadata: {
          source: 'mobile-receipt-capture',
          timestamp: new Date().toISOString(),
        },
      }
    );
    onProgress?.(20);

    const { content_id, upload_url, external_key } = uploadContentResponse;

    // Step 3: Upload image to presigned URL
    await uploadToPresignedUrl(upload_url, imageUri, mimeType);
    onProgress?.(80);

    // Step 4: Finalize upload to mark content as active
    await finalizeUpload(supabaseUrl, accessToken, content_id);
    onProgress?.(100);

    return {
      contentId: content_id,
      externalKey: external_key,
    };
  } catch (error) {
    console.error('Image upload failed:', error);
    throw error instanceof Error ? error : new Error('Failed to upload image');
  }
}

/**
 * Step 1: Request upload URL from cs-upload-content edge function
 */
export interface RequestUploadUrlParams {
  mime_type: string;
  size_bytes?: number;
  checksum?: string;
  metadata?: any;
}

export interface RequestUploadUrlResponse {
  content_id: string;
  upload_url: string;
  external_key: string;
  expires_at: string;
}

export async function requestUploadUrl(
  supabaseUrl: string,
  accessToken: string,
  params: RequestUploadUrlParams
): Promise<RequestUploadUrlResponse> {
  const functionUrl = `${supabaseUrl}/functions/v1/cs-upload-content`;
  
  const response = await fetch(functionUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`,
    },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to request upload URL: ${error}`);
  }

  const data = await response.json();
  return data;
}

/**
 * Step 3: Upload image to presigned URL
 */
export async function uploadToPresignedUrl(
  uploadUrl: string,
  imageUri: string,
  mimeType: string
): Promise<void> {
    
  const safeUrl = uploadUrl.replace(/&amp;/g, '&');
  console.log('safeUrl', safeUrl);
  try {
    // Convert URI to Blob for upload
    //const blob = await uriToBlob(imageUri);
    // const blob = new TextEncoder().encode('hello').buffer;
    const data = await uriToArrayBuffer(imageUri);
    const response = await fetch(safeUrl, {
      method: 'PUT',
      headers: {
        'x-ms-blob-type': 'BlockBlob',
        'Content-Type': mimeType,
      },
      body: data,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to upload image: ${response.status} - ${errorText}`);
    }

    console.log('Image uploaded successfully to:', safeUrl);
  } catch (error) {
    console.error('Upload to presigned URL failed...:', safeUrl, 'Error', error);
    throw error;
  }
}

/**
 * Step 4: Finalize upload to mark content as active
 */
export interface FinalizeUploadParams {
  content_id: string;
}

export interface FinalizeUploadResponse {
  success: boolean;
  content_id: string;
  external_key: string;
  verified_size: number | null;
}

export async function finalizeUpload(
  supabaseUrl: string,
  accessToken: string,
  contentId: string
): Promise<FinalizeUploadResponse> {
  const functionUrl = `${supabaseUrl}/functions/v1/cs-finalize-upload`;
  
  const response = await fetch(functionUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`,
    },
    body: JSON.stringify({
      content_id: contentId,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to finalize upload: ${error}`);
  }

  const data = await response.json();
  return data;
}
