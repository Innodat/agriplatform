import type {AdminPortalController,PortalState} from '../src/admin-portal.js';
declare const portal:AdminPortalController;
const state:PortalState=portal.snapshot();
// @ts-expect-error Raw sessions are never a published review property.
state.session;
// @ts-expect-error Bearers remain inside trusted execution leases.
state.access_token;
if(state.kind==='history'){
 const label:string=state.rows[0].capture.child_label;
 // @ts-expect-error Immutable validated business data cannot be edited here.
 state.rows[0].capture.child_label=label;
 // @ts-expect-error Admission is not inferred from an own context.
 state.permission;
}
if(state.kind==='detail'){
 const revision:string=state.audit.current_revision;
 // @ts-expect-error Revision identifiers preserve exact server strings.
 const numericRevision:number=revision;
}
