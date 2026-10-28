import type { AuditDetails, LoadedDisplays, UnavailableDisplays, ResolvedLabel, UnavailableLabel, AuditDisplayError503 } from '../contracts/audit-display-generated/types.gen.js';

const resolved: ResolvedLabel = {actor_id: '00000000-0000-4000-8000-000000000001', status: 'resolved', display_name: 'Retained name'};
const unmapped: UnavailableLabel = {actor_id: '00000000-0000-4000-8000-000000000002', status: 'unavailable'};
const loaded: LoadedDisplays = {status: 'loaded', labels: [resolved, unmapped]};
const outage: UnavailableDisplays = {status: 'temporarily_unavailable'};
const safe: AuditDisplayError503 = {error_id: 'authorization_observation_expired', error: 'Safe'};
function consume(result: AuditDetails): string[] {
  if (result.actor_display.status === 'temporarily_unavailable') return [];
  return result.actor_display.labels.map(label => label.status === 'resolved' ? label.display_name : 'Name unavailable');
}
// @ts-expect-error Unmapped labels never carry a guessed name.
const guessed: UnavailableLabel = {actor_id: 'id', status: 'unavailable', display_name: 'System'};
// @ts-expect-error Resolved labels require an actual name.
const missing: ResolvedLabel = {actor_id: 'id', status: 'resolved'};
// @ts-expect-error Batch outages do not disclose partial labels.
const partial: UnavailableDisplays = {status: 'temporarily_unavailable', labels: [resolved]};
// @ts-expect-error Status discriminator is closed.
const status: LoadedDisplays = {status: 'partial', labels: []};
// @ts-expect-error Dependency errors never become KDG user authorization outcomes.
const upstream: AuditDisplayError503 = {error_id: 'identity.actor_display_unavailable', error: 'Safe'};
// @ts-expect-error The aggregate requires its authorized audit page.
const noPage: AuditDetails = {actor_display: loaded};
void [loaded, outage, safe, consume, guessed, missing, partial, status, upstream, noPage];
