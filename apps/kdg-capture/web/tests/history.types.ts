import {historyCaptures,type PendingHistory,type HistoryResult} from '../src/history';
const pending:PendingHistory={account_id:'a',org_id:'o',from_date:'2026-10-01',to_date:'2026-10-26'};
// @ts-expect-error no write command on a history read
const bad:PendingHistory={...pending,command_type:'capture.create'};
// @ts-expect-error explicit execution lease is required
historyCaptures({account_id:'a',access_token:'t'},pending,{});
function loaded(result:HistoryResult){if(result.kind==='loaded'){
 // @ts-expect-error immutable page
 result.page.next_cursor='x';
 // @ts-expect-error immutable details
 result.page.items[0].answers={};
 // @ts-expect-error immutable original definition
 result.page.items[0].definition.questions.push({});
}}
void bad;void loaded;
