import type {AdminHistoryPage, AdminHistoryData, AdminHistoryResponse, AdminDetailResponse} from '../../contracts/admin-generated';
import type {HistoryPage, OwnReadObservation} from '../../contracts/history-generated';
import type {CaptureDetail} from '../../contracts/read-generated';

declare const admin: AdminHistoryPage;
declare const detail: AdminDetailResponse;
declare const response: AdminHistoryResponse;
const sameDetail: CaptureDetail=detail;
const samePage: AdminHistoryPage=response;
const explicitDates: AdminHistoryData={query:{from_date:'2026-10-01',to_date:'2026-10-26'},url:'/api/v1/admin/captures'};
// @ts-expect-error organization admin page supplies no own offline observation
const own: HistoryPage=admin;
// @ts-expect-error no own offline capability can be renewed from this page
const observation: OwnReadObservation=admin.observation;
// @ts-expect-error no offline expiry is present
const expiry: string=admin.expires_at;
// @ts-expect-error no all-edit authority is present
const edit: unknown=admin.edit_observation;
// @ts-expect-error explicit dates are required
const missingDates: AdminHistoryData={url:'/api/v1/admin/captures'};
void sameDetail;void samePage;void explicitDates;void own;void observation;void expiry;void edit;void missingDates;

// @ts-expect-error original owner is never a client query selector
const ownerSelector: AdminHistoryData={query:{from_date:'2026-10-01',to_date:'2026-10-26',owner_account_id:'a'},url:'/api/v1/admin/captures'};
// @ts-expect-error organization scope is verified server-side, never a query selector
const orgSelector: AdminHistoryData={query:{from_date:'2026-10-01',to_date:'2026-10-26',org_id:'o'},url:'/api/v1/admin/captures'};
void ownerSelector;void orgSelector;
