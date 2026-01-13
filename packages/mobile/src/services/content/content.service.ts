import { Platform } from 'react-native';
import { getImageInfo } from '@agriplatform/shared';
import {
  requestUploadUrl,
  finalizeUpload,
  type UploadImageResult,
  type UploadImageOptions,
} from '@agriplatform/shared';

// Re-export shared types for convenience
export type { UploadImageResult, UploadImageOptions };

/**
 * Upload a local image (file:// or content://) to an Azure SAS URL using fetch.
 * - Android content:// → RNFS read (base64) → convert to ArrayBuffer → upload
 * - Others (file://, http(s)) → fetch(uri).arrayBuffer() → upload
 */
export async function uploadToPresignedUrl(
  uploadUrl: string,
  imageUri: string,
  mimeType: string
): Promise<void> {
  // Ensure raw '&' between SAS params (defensive only)
  const safeUrl = uploadUrl.replace(/&/g, '&');
  console.log('safeUrl RN', safeUrl);

  // Inline reader: URI -> ArrayBuffer
  async function uriToArrayBuffer(uri: string): Promise<ArrayBuffer> {
    // --- ANDROID: handle both content:// and file:// with RNFS ---
    if (Platform.OS === 'android') {
      // read with RNFS for content://
      if (uri.startsWith('content://')) {
        console.log('Android + content:// -> using RNFS');
        const RNFS = (await import('react-native-fs')).default;
        const base64 = await RNFS.readFile(uri, 'base64'); // RNFS returns base64 for content://
        // convert base64 -> bytes (upload binary, not base64)
        // eslint-disable-next-line @typescript-eslint/no-var-requires
        const { Buffer } = require('buffer');
        const buf = Buffer.from(base64, 'base64');
        return buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength);
      }

      // read with RNFS for file:// (strip scheme to real FS path)
      if (uri.startsWith('file://')) {
        console.log('Android + file:// -> using RNFS');
        const path = uri.replace('file://', ''); // RNFS prefers a real path
        const RNFS = (await import('react-native-fs')).default;
        const base64 = await RNFS.readFile(path, 'base64');
        // eslint-disable-next-line @typescript-eslint/no-var-requires
        const { Buffer } = require('buffer');
        const buf = Buffer.from(base64, 'base64');
        return buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength);
      }
    }

    // --- iOS file:// (and remote http(s) URLs) usually fine via fetch ---
    console.log('iOS file:// or remote URL -> using fetch', uri);
    const resp = await fetch(uri);
    if (!resp.ok) {
      const txt = await resp.text().catch(() => '');
      throw new Error(`Read failed: ${resp.status} ${txt}`);
    }
    return await resp.arrayBuffer();
  }


  // Read bytes and PUT with required Azure headers
  console.log('Convert image');
  const data = await uriToArrayBuffer(imageUri);
  console.log('PUT');
  const response = await fetch(safeUrl, {
    method: 'PUT',
    headers: {
      'x-ms-blob-type': 'BlockBlob', // REQUIRED by Azure Put Blob
      'Content-Type': mimeType, // e.g., image/jpeg
    },
    body: data, // ArrayBuffer -> fixed Content-Length
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => '(no body)');
    throw new Error(`Failed to upload image: ${response.status} - ${errorText}`);
  }

  console.log('Image uploaded successfully to:', safeUrl);
}

/**
 * React Native wrapper for uploadImage - uses shared logic but RN upload function
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
    // Step 1: Get image info (from shared utilities)
    const { mimeType, sizeBytes } = await getImageInfo(imageUri);
    onProgress?.(10);

    // Step 2: Request upload URL (from shared service)
    const uploadContentResponse = await requestUploadUrl(
      supabaseUrl,
      accessToken,
      {
        mime_type: mimeType,
        size_bytes: sizeBytes || undefined,
        checksum: undefined,
        metadata: {
          source: 'mobile-receipt-capture',
          timestamp: new Date().toISOString(),
        },
      }
    );
    onProgress?.(20);

    const { content_id, upload_url, external_key } = uploadContentResponse;

    // Step 3: Upload using RN-specific implementation
    console.log("Step 3: Upload using RN-specific implementation");
    await uploadToPresignedUrl(upload_url, imageUri, mimeType);
    console.log("Progress: 80%");
    onProgress?.(80);

    // Step 4: Finalize upload (from shared service)
    console.log("Step 4: Finalize upload (from shared service)");
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