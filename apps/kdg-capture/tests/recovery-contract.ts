import type {
  RecoverOperationData, RecoverOperationResponse, RecoverOperationErrors,
  CaptureReceipt, Unresolved,
} from '../contracts/recovery-generated/index';

const request: RecoverOperationData = {
  url: '/api/v1/operations/{operation_id}',
  path: { operation_id: '11111111-1111-4111-8111-111111111111' },
  query: { command_type: 'capture.create' },
};
const edit: RecoverOperationData = { ...request, query: { command_type: 'capture.edit' } };
const receipt: CaptureReceipt = {
  operation_id: request.path.operation_id, command_type: 'capture.create', command_version: 1,
  status: 'committed', result: { capture_id: request.path.operation_id, revision: '9223372036854775807' },
};
const unresolved: Unresolved = {
  operation_id: request.path.operation_id, command_type: 'capture.create', status: 'unresolved',
};
function consume(response: RecoverOperationResponse): string | undefined {
  if (response.status === 'committed') return response.result.revision;
  const unknown: 'unresolved' = response.status;
  // @ts-expect-error Unresolved is not a committed receipt or proof of rollback.
  response.result;
  void unknown;
  return undefined;
}
const denied: RecoverOperationErrors[403] = { error: 'Safe message', error_id: 'access_denied' };
const unavailable: RecoverOperationErrors[503] = { error: 'Safe message', error_id: 'operation_verification_unavailable' };
// @ts-expect-error The required discriminator cannot be omitted.
const missingQuery: RecoverOperationData = { url: request.url, path: request.path };
// @ts-expect-error Unknown commands are outside this recovery contract.
const badCommand: RecoverOperationData['query'] = { command_type: 'capture.delete' };
// @ts-expect-error Caller-selected organization is not a recovery parameter.
const selector: RecoverOperationData['query'] = { command_type: 'capture.create', org_id: 'other' };
// @ts-expect-error A GET recovery request has no body.
const body: RecoverOperationData = { ...request, body: {} };
// @ts-expect-error Required wire status cannot be omitted merely because Python defaults it internally.
const missingStatus: Unresolved = { operation_id: request.path.operation_id, command_type: 'capture.create' };
// @ts-expect-error Revisions remain strings beyond JavaScript's safe integer range.
const numericRevision: CaptureReceipt['result'] = { capture_id: request.path.operation_id, revision: 1 };
// @ts-expect-error Unsupported command versions are not committed v1 receipts.
const badVersion: CaptureReceipt = { ...receipt, command_version: 2 };
// @ts-expect-error A committed receipt cannot omit its stored result.
const missingResult: CaptureReceipt = { operation_id: request.path.operation_id, command_type: 'capture.create', command_version: 1, status: 'committed' };
// @ts-expect-error Unknown upstream text is not a safe machine-readable identifier.
const unsafeError: RecoverOperationErrors[503] = { error: 'Message', error_id: 'raw_upstream_exception' };
// @ts-expect-error Authorization failure is not successful unresolved verification.
const falseAbsence: RecoverOperationResponse = { error: 'Unavailable', error_id: 'authorization_unavailable' };
// @ts-expect-error Error identifiers retain their declared HTTP status family.
const wrongStatus: RecoverOperationErrors[403] = unavailable;
void [request, edit, receipt, unresolved, consume, denied, unavailable, missingQuery,
  badCommand, selector, body, missingStatus, numericRevision, badVersion, missingResult,
  unsafeError, falseAbsence, wrongStatus];
