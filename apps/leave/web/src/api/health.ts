// Create-once owner seed. Business requests use this application's own API.
import type { HealthResponse } from './generated/types.gen';
export type HealthResult = {ok: true; health: HealthResponse} | {ok: false; error_id: 'api_unavailable' | 'invalid_response' | 'request_failed'};
export async function getHealth(request: typeof fetch = fetch): Promise<HealthResult> {
 try {
  const response = await request('/api/health', {method:'GET', credentials:'same-origin', redirect:'error', signal:AbortSignal.timeout(5000)});
  if (!response.ok) return {ok:false,error_id:response.status>=500?'api_unavailable':'request_failed'};
  let body: unknown;
  try { body = await response.json(); }
  catch (error) {
   if (error instanceof SyntaxError) return {ok:false,error_id:'invalid_response'};
   throw error;
  }
  if (!body || typeof body!=='object' || !('status' in body) || body.status!=='ok') return {ok:false,error_id:'invalid_response'};
  const health: HealthResponse = {status:body.status};
  return {ok:true,health};
 } catch { return {ok:false,error_id:'api_unavailable'}; }
}
