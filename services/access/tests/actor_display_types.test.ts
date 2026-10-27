import type {
  ActorDisplayResponse, ResolvedActorDisplay, UnavailableActorDisplay,
  IdentityActorDisplaysData, IdentityActorDisplaysError, IdentityActorDisplaysErrors,
} from '../contracts/actor-display-generated/types.gen.js';

const actor = '44444444-4444-4444-8444-444444444444';
const org = '33333333-3333-4333-8333-333333333333';
const request: IdentityActorDisplaysData = {
  url: '/v2/identity/actor-displays', body: {org_id: org, actor_ids: [actor]},
};
const success: ActorDisplayResponse = {org_id: org, labels: [
  {actor_id: actor, status: 'resolved', display_name: 'Current retained name'},
  {actor_id: org, status: 'unavailable'},
]};
for (const label of success.labels) {
  if (label.status === 'resolved') {
    const name: string = label.display_name;
    void name;
  } else {
    // @ts-expect-error Unmapped names are absent, not null or a guessed label.
    label.display_name;
  }
}
const outage: IdentityActorDisplaysErrors[503] = {
  error_id: 'identity.actor_display_unavailable', error: 'Request could not be completed', details: {},
};
function failure(error: IdentityActorDisplaysError): 'denied' | 'invalid' | 'unavailable' {
  switch (error.error_id) {
    case 'service_access_denied': return 'denied';
    case 'validation_failed': return 'invalid';
    case 'identity.actor_display_unavailable': return 'unavailable';
  }
}
// @ts-expect-error Resolved labels require their name.
const missing: ResolvedActorDisplay = {actor_id: actor, status: 'resolved'};
// @ts-expect-error Unavailable labels cannot carry a name.
const invented: UnavailableActorDisplay = {actor_id: actor, status: 'unavailable', display_name: 'System'};
// @ts-expect-error The status discriminates the success union.
const unknown: ActorDisplayResponse = {org_id: org, labels: [{actor_id: actor, status: 'missing'}]};
// @ts-expect-error The error identifier is a closed union.
const badError: IdentityActorDisplaysError = {error_id: 'deleted', error: 'Request could not be completed', details: {}};
// @ts-expect-error Errors disclose no private details.
const details: IdentityActorDisplaysError = {error_id: 'validation_failed', error: 'Request could not be completed', details: {actor_id: actor}};
// @ts-expect-error No query selectors are allowed.
const query: IdentityActorDisplaysData = {...request, query: {actor_id: actor}};
// @ts-expect-error The request has no account selector.
const account: IdentityActorDisplaysData = {...request, body: {org_id: org, actor_ids: [actor], account_id: actor}};
void [request, success, outage, failure, missing, invented, unknown, badError, details, query, account];
