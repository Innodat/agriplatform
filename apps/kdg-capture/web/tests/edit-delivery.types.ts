import {deliverSavedEdit,type SavedEditAction,type EditDeliveryOptions,type EditDeliveryResult} from '../src/edit-delivery';
import {createEditDeliveryEntry} from '../src/edit-delivery-entry';
import type {Session} from '../src/entry';
import type {AuthEntryOptions} from '../src/auth-entry';
declare const session:Session,action:SavedEditAction,options:EditDeliveryOptions,auth:AuthEntryOptions;
const outcome:Promise<EditDeliveryResult>=deliverSavedEdit(session,action,options);
const entry=createEditDeliveryEntry({...auth,store:options.store});
const throughAuth:Promise<EditDeliveryResult>=entry.deliver(action);
options.store.lookupPreparedEdit(action,{signal:options.signal,isCurrent:options.isCurrent});
// @ts-expect-error pinned account/organization/action are required
entry.deliver({action_id:'action'});
// @ts-expect-error delivery requires one current execution fence
void deliverSavedEdit(session,action,{store:options.store,signal:options.signal});
// @ts-expect-error Auth lease acquisition remains private to the boundary
entry.acquireExecution();
// @ts-expect-error action scope is immutable
 action.org_id='replacement';
// @ts-expect-error result cannot claim that all local work is Synced
const incorrect:EditDeliveryResult={kind:'Synced'};
void [outcome,throughAuth,incorrect];
