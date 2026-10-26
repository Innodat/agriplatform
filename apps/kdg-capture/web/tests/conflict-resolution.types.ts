import type {openHistoryStore,ConflictPin,ReviewedConflict} from '../src/history-store.js';
import type {ConflictResolutionStore,ConflictResolutionResult} from '../src/conflict-resolution.js';
import {createConflictResolutionEntry} from '../src/conflict-resolution-entry.js';
declare const store:Awaited<ReturnType<typeof openHistoryStore>>,pin:ConflictPin,reviewed:ReviewedConflict;
const compatible:ConflictResolutionStore=store;
void compatible;void pin;void reviewed;void createConflictResolutionEntry;
const result:ConflictResolutionResult={kind:'adopted',decision_id:'retained'};void result;
