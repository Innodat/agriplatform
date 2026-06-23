import { HttpError } from "../../_shared/auth.ts";

type SelectResult = { row: Record<string, unknown> | null; error: Error | null };

export function createSupabaseMock() {
  let selectResults: SelectResult[] = [{ row: null, error: null }];
  let selectIndex = 0;
  const insertedRows: Record<string, unknown>[] = [];
  const updatedRows: Record<string, unknown>[] = [];

  const mock = {
    _setSelectResult(row: Record<string, unknown> | null, error: Error | null = null) {
      selectResults = [{ row, error }];
      selectIndex = 0;
    },
    _setSelectResults(results: (SelectResult | null)[]) {
      selectResults = results.map(r => r ?? { row: null, error: null });
      selectIndex = 0;
    },
    _getInsertedRows() {
      return insertedRows;
    },
    _getUpdatedRows() {
      return updatedRows;
    },
    schema() {
      return this;
    },
    from() {
      return this;
    },
    select() {
      return this;
    },
    eq() {
      return this;
    },
    order() {
      return this;
    },
    limit() {
      return this;
    },
    single() {
      const currentResult = selectResults[selectIndex] || selectResults[selectResults.length - 1];
      selectIndex++;
      if (currentResult.error) {
        return { data: null, error: currentResult.error };
      }
      if (!currentResult.row) {
        return { data: null, error: new HttpError("Not found", 404) };
      }
      return { data: currentResult.row, error: null };
    },
    insert(payload: Record<string, unknown>) {
      insertedRows.push(payload);
      return {
        select: () => ({
          single: () => {
            if (!payload) {
              return { data: null, error: new HttpError("Insert failed", 500) };
            }
            return { data: { id: crypto.randomUUID() }, error: null };
          },
        }),
      };
    },
    update(payload: Record<string, unknown>) {
      updatedRows.push(payload);
      return {
        eq: () => ({ error: null }),
      };
    },
  };

  return mock;
}

export function createAuthMock(userId = "user-123", roles: string[] = [], payload?: Record<string, unknown>) {
  return {
    requireAuth: () =>
      Promise.resolve({
        userId,
        roles,
        payload: payload ?? { org_id: "org-123" },
      }),
  };
}

export function createAzureMock() {
  let blobState = { exists: true, size: 256 };

  return {
    generateSignedBlobUrl: () => ({
      url: "https://example.com/blob",
      expiresAt: new Date(),
    }),
    resolveContainerName: (template: string) => template.replace("{env}", "test"),
    blobExists: () => Promise.resolve(blobState),
    _setBlobState(state: { exists: boolean; size: number }) {
      blobState = state;
    },
  };
}

export const noopCors = {
  handleCors: () => null,
  mergeCorsHeaders: (headers: HeadersInit = {}) => new Headers(headers),
};

/**
 * Create a mock StorageProvider for testing
 */
export function createStorageProviderMock() {
  let blobState: { exists: boolean; size?: number } = { exists: true, size: 256 };

  return {
    generateReadUrl: () =>
      Promise.resolve({
        url: "https://example.com/read",
        expiresAt: new Date(Date.now() + 15 * 60 * 1000),
      }),
    generateUploadUrl: () =>
      Promise.resolve({
        url: "https://example.com/upload",
        expiresAt: new Date(Date.now() + 15 * 60 * 1000),
      }),
    exists: () => Promise.resolve(blobState),
    delete: () => Promise.resolve(),
    _setBlobState(state: { exists: boolean; size?: number }) {
      blobState = state;
    },
  };
}
