import { Buffer } from 'buffer';


/**
 * Image utility functions
 * Handles getting image metadata like MIME type and file size
 * Platform-agnostic implementation
 */

export interface ImageInfo {
  mimeType: string;
  sizeBytes: number;
}

/**
 * Get MIME type from file extension
 */
export function getMimeTypeFromUri(uri: string): string {
  const extension = uri.split('.').pop()?.toLowerCase() || '';
  
  const mimeTypes: Record<string, string> = {
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'webp': 'image/webp',
    'bmp': 'image/bmp',
    'heic': 'image/heic',
  };
  
  return mimeTypes[extension] || 'image/jpeg';
}

/**
 * Get file information from URI
 * Note: This is a simplified version. For production, you may want to use
 * expo-file-system or react-native-fs for actual file stats
 */
export async function getImageInfo(uri: string): Promise<ImageInfo> {
  const mimeType = getMimeTypeFromUri(uri);
  
  // For now, estimate size or return 0 if we can't get actual size
  // In a production app, you would use expo-file-system or react-native-fs
  // to get actual file size
  let sizeBytes = 0;
  
  try {
    // Attempt to get file info using fetch (works for http/https URLs)
    if (uri.startsWith('http://') || uri.startsWith('https://')) {
      const response = await fetch(uri, { method: 'HEAD' });
      const contentLength = response.headers.get('content-length');
      if (contentLength) {
        sizeBytes = parseInt(contentLength, 10);
      }
    }
  } catch (error) {
    // If we can't get size, we'll proceed without it
    console.warn('Could not get file size:', error);
  }
  
  return {
    mimeType,
    sizeBytes,
  };
}

/**
 * Convert image URI to Blob (for upload)
 * This is useful for platforms that need Blob objects
 */
export async function uriToBlob(uri: string): Promise<Blob> {
  const response = await fetch(uri);
  return response.blob();
}

// vanilla RN-friendly conversion; works for most file:// and many content:// URIs
export async function uriToArrayBuffer(uri: string): Promise<ArrayBuffer> {
  const resp = await fetch(uri);
  if (!resp.ok) {
    const txt = await resp.text().catch(() => '');
    throw new Error(`Failed to read file: ${resp.status} ${txt}`);
  }
  return await resp.arrayBuffer();
}

/**
 * Convert image URI to Base64 string
 */
export async function uriToBase64(uri: string): Promise<string> {
  const response = await fetch(uri);
  const blob = await response.blob();
  
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      if (typeof reader.result === 'string') {
        resolve(reader.result.split(',')[1]); // Remove data URL prefix
      } else {
        reject(new Error('Failed to convert to base64'));
      }
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

/**
 * Calculate checksum for image data (base64 encoded SHA-256)
 * This is optional but recommended for data integrity
 */
export async function calculateChecksum(base64Data: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(base64Data);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashBase64 = btoa(String.fromCharCode(...hashArray));
  return hashBase64;
}
