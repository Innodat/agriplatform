/** Browser current-entry boundary. Auth owns sessions; KDG owns current admission. */
import type {Context} from '../../contracts/generated/types.gen';

export type Session = Readonly<{account_id: string; access_token: string}>;
type FailureKind = 'authentication_required' | 'access_denied' | 'actor_setup_required' |
  'authorization_unavailable' | 'invalid_response' | 'cancelled';
export type EntryContext = Readonly<Omit<Context, 'authorization_scope' | 'resource_scope'> & {
  authorization_scope: Readonly<Context['authorization_scope']>;
  resource_scope: Readonly<Context['resource_scope']>;
}>;
export type ContextResult = Readonly<{kind: 'authorized'; context: EntryContext}> | Readonly<{kind: FailureKind}>;
export type EntryState = ContextResult | Readonly<{kind: 'signed_out' | 'checking' | 'superseded'}>;
type Options = {request?: typeof fetch; signal?: AbortSignal; timeoutMs?: number};
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
const NIL = '00000000-0000-0000-0000-000000000000';
const id = (value: unknown): value is string => typeof value === 'string' && UUID.test(value) && value !== NIL;
class InvalidResponse extends Error {}
const invalid = (): never => {throw new InvalidResponse();};
function object(value: unknown, keys: string[]): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value) ||
      Object.keys(value).sort().join(',') !== [...keys].sort().join(',')) return invalid();
  return value as Record<string, unknown>;
}
function utc(value: unknown): value is string {
  if (typeof value !== 'string') return false;
  const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?Z$/.exec(value);
  if (!match || Number(match[1]) < 1) return false;
  const date = new Date(value);
  return [date.getUTCFullYear(),date.getUTCMonth()+1,date.getUTCDate(),date.getUTCHours(),date.getUTCMinutes(),date.getUTCSeconds()]
    .every((field,index) => field === Number(match[index+1]));
}
function context(value: unknown, account: string, org: string): EntryContext {
  const body = object(value,['account_id','actor_id','membership_id','authorization_scope','resource_scope','permission','decision_id','checked_at']);
  const scope = object(body.authorization_scope,['kind','org_id']);
  const resource = object(body.resource_scope,['kind','account_id']);
  if (!id(body.account_id) || !id(body.actor_id) || !id(body.decision_id) ||
      body.account_id !== account || scope.kind !== 'organization' || scope.org_id !== org ||
      resource.kind !== 'own_account' || resource.account_id !== account ||
      body.permission !== 'kdg_capture.capture.read.own' || typeof body.membership_id !== 'string' ||
      !/^[1-9][0-9]{0,18}$/.test(body.membership_id) || BigInt(body.membership_id) > 9223372036854775807n || !utc(body.checked_at)) return invalid();
  return Object.freeze({account_id:body.account_id,actor_id:body.actor_id,decision_id:body.decision_id,
    membership_id:body.membership_id,permission:body.permission,checked_at:body.checked_at,
    authorization_scope:Object.freeze({kind:'organization',org_id:org}),
    resource_scope:Object.freeze({kind:'own_account',account_id:account})});
}
function errorKind(status: number, body: unknown): FailureKind {
  let identifier: unknown;
  if (body && typeof body === 'object' && !Array.isArray(body)) {
    const record = body as Record<string, unknown>;
    identifier = record.error_id;
    if (identifier === undefined && record.detail && typeof record.detail === 'object') {
      identifier = (record.detail as Record<string,unknown>).code;
    }
  }
  if (status === 401 && identifier === 'authentication_required') return 'authentication_required';
  if (status === 403 && identifier === 'access_denied') return 'access_denied';
  if (status === 409 && identifier === 'identity.actor_setup_required') return 'actor_setup_required';
  if (status === 422 && identifier === 'validation_failed') return 'invalid_response';
  return 'authorization_unavailable';
}

export async function getCurrentContext(session: Session, org: string, options: Options = {}): Promise<ContextResult> {
  const account = session.account_id, token = session.access_token;
  if (!id(account) || typeof token !== 'string' || !/^[\x21-\x7e]+$/.test(token)) return {kind:'authentication_required'};
  if (!id(org)) return {kind:'invalid_response'};
  if (options.signal?.aborted) return {kind:'cancelled'};
  const duration = options.timeoutMs ?? 10000;
  if (!Number.isFinite(duration) || duration <= 0 || duration > 10000) return {kind:'invalid_response'};
  const controller = new AbortController();
  let reader: ReadableStreamDefaultReader<Uint8Array> | undefined;
  let stop!: (value: ContextResult) => void;
  const stopped = new Promise<ContextResult>(resolve => {stop=resolve;});
  const cancel = () => {controller.abort();stop({kind:'cancelled'});};
  options.signal?.addEventListener('abort',cancel,{once:true});
  const timer = setTimeout(() => {controller.abort();stop({kind:'authorization_unavailable'});},duration);
  const work = async (): Promise<ContextResult> => {
    try {
      const response = await (options.request ?? fetch)('/api/v1/context',{
        method:'GET',headers:{Authorization:'Bearer '+token},credentials:'same-origin',mode:'same-origin',
        cache:'no-store',redirect:'error',signal:controller.signal});
      if (controller.signal.aborted) {
        if (response.body) void response.body.cancel().catch(() => {});
        return {kind:'cancelled'};
      }
      if (response.redirected || !response.body) return invalid();
      reader = response.body.getReader();
      const chunks: Uint8Array[] = [];let size=0;
      while (true) {
        const chunk = await reader.read();
        if (chunk.done) break;
        size += chunk.value.byteLength;
        if (size > 16384) return invalid();
        chunks.push(chunk.value);
      }
      const bytes = new Uint8Array(size);let offset=0;
      for (const chunk of chunks) {bytes.set(chunk,offset);offset+=chunk.byteLength;}
      let body: unknown;
      try {body=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));}
      catch {return invalid();}
      return response.status === 200 ? {kind:'authorized',context:context(body,account,org)} : {kind:errorKind(response.status,body)};
    } catch (error) {return {kind:error instanceof InvalidResponse ? 'invalid_response' : 'authorization_unavailable'};}
  };
  try {return await Promise.race([work(),stopped]);}
  finally {
    clearTimeout(timer);options.signal?.removeEventListener('abort',cancel);controller.abort();
    if (reader) void reader.cancel().catch(() => {});
  }
}

/** Call check/clear on every Auth event. This does not implement or persist Auth. */
export function createEntryBoundary(org: string, publish: (state: EntryState) => void, request: typeof fetch = fetch) {
  let current: EntryState=Object.freeze({kind:'signed_out'}), generation=0, disposed=false;
  let active: AbortController | undefined;
  const reset = () => {generation++;active?.abort();active=undefined;};
  const set = (next: EntryState) => {current=Object.freeze(next);publish(current);};
  return {
    state: (): EntryState => current,
    async check(session: Session | null): Promise<EntryState> {
      if (disposed) return {kind:'superseded'};
      reset();const execution=generation;
      if (!session) {set({kind:'signed_out'});return current;}
      active=new AbortController();const signal=active.signal;
      const pinned={account_id:session.account_id,access_token:session.access_token};
      set({kind:'checking'});
      const result=await getCurrentContext(pinned,org,{request,signal});
      if (disposed || execution !== generation) return {kind:'superseded'};
      active=undefined;set(result);return result;
    },
    clear() {if (!disposed) {reset();set({kind:'signed_out'});}},
    dispose() {reset();disposed=true;current=Object.freeze({kind:'signed_out'});},
  };
}
