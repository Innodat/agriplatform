import type {openHistoryStore,ConflictPin,ReviewedLocalConflict,LocalResolutionSelection} from '../src/history-store.js';
declare const store:Awaited<ReturnType<typeof openHistoryStore>>,pin:ConflictPin,reviewed:ReviewedLocalConflict,selection:LocalResolutionSelection;
void store.openLocalConflict(pin,'current');
void store.openLocalConflict(pin,'replacement',{signal:new AbortController().signal,isCurrent:()=>true});
void store.useLocalCurrent(reviewed,'decision');
void store.saveLocalConflictReplacement(reviewed,'decision','action',{observation_date:'2026-10-25',answers:{}});
void store.lookupLocalResolution(selection);
// @ts-expect-error local reviews cannot be supplied as confirmed server selections
void store.lookupResolution({reviewed,decision_id:'decision',action_id:null,changes:null});
