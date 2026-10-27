import {validateOrganizations,validateApplications,accessFailure,AccessDependencyFailure} from '../contracts/adapter';
import type {OrganizationsDiscovery,ApplicationsDiscovery} from '../contracts/generated/types.gen';
const org='33333333-3333-4333-8333-333333333333';
function ok(value: unknown): asserts value {if (!value) throw new Error('assertion_failed');}
function refuses(run: () => unknown) {try {run();} catch (e) {ok(e instanceof AccessDependencyFailure);return;}throw new Error('expected_refusal');}
const organizations: OrganizationsDiscovery={organizations:[{org_id:org,name:'For Profit Limited',membership_id:'9223372036854775807'}],next_cursor:null};
ok(validateOrganizations(organizations)===organizations);
const page={...organizations,next_cursor:btoa(org)};ok(validateOrganizations(page,1)===page);
const apps: ApplicationsDiscovery={applications:[{app_id:'pts',eligible_scope_kinds:['account']},{app_id:'reference',eligible_scope_kinds:['account','organization']}],checked_at:'2026-10-27T12:00:00Z'};
ok(validateApplications(apps)===apps);
for (const value of [
 {...organizations,account_id:org}, {...organizations,next_cursor:'garbage'},
 {...organizations,organizations:[{...organizations.organizations[0],membership_id:1}]},
 {...organizations,organizations:[{...organizations.organizations[0],membership_id:'9223372036854775808'}]},
 {...organizations,organizations:[...organizations.organizations,...organizations.organizations]},
 {...organizations,next_cursor:btoa('44444444-4444-4444-8444-444444444444')},
]) refuses(()=>validateOrganizations(value));
refuses(()=>validateOrganizations(organizations,100,org));
for (const value of [
 {...apps,org_id:org}, {...apps,checked_at:'2026-02-30T12:00:00Z'},
 {...apps,applications:[{app_id:'pts',eligible_scope_kinds:[]}]},
 {...apps,applications:[{app_id:'pts',eligible_scope_kinds:['organization','account']}]},
 {...apps,applications:[{app_id:'pts',eligible_scope_kinds:['account','account']}]},
 {...apps,applications:[{app_id:'pts',eligible_scope_kinds:['account'],org_id:org}]},
 {...apps,applications:[...apps.applications].reverse()},
 {...apps,applications:Array.from({length:129},(_,i)=>({app_id:'app'+String(i).padStart(3,'0'),eligible_scope_kinds:['account']}))},
]) refuses(()=>validateApplications(value));
ok(accessFailure(500,{error_id:'internal_error',error:'safe',details:{}})==='unavailable');
ok(accessFailure(403,{error_id:'service_access_denied',error:'safe',details:{}})==='unavailable');
ok(accessFailure(403,{error_id:'access_denied',error:'safe',details:{}})==='denied');
