import { HttpError } from "../../_shared/auth.ts";

type SelectResult = { row: Record<string, unknown> | null; error: Error | null };

export function createSupabaseMock() {
  let selectResult: SelectResult = { row: null, error: null };
  const insertedRows: Record<string, unknown>[] = [];
  const updatedRows: Record<string, unknown>[] = [];

  const mock = {
    _setSelectResult(row: Record<string, unknown> | null, error: Error | null = null) {
      selectResult = { row, error };
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
      if (selectResult.error) {
        return { data: null, error: selectResult.error };
      }
      if (!selectResult.row) {
        return { data: null, error: new HttpError("Not found", 404) };
      }
      return { data: selectResult.row, error: null };
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

export function createAuthMock(userId = "user-123", roles: string[] = []) {
  return {
    requireAuth: () =>
      Promise.resolve({
        userId,
        roles,
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
