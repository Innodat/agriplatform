import {A,O,C,Q,detail,pending} from './read-fixture.mjs';
import {observation} from './history-fixture.mjs';
export {A,O,C,Q,detail,pending};
export const context=(changes={})=>({capture:detail(),editable_fields:['observation_date','answers'],read_observation:observation(),edit_observation:{...observation(),permission:'kdg_capture.capture.edit.own'},...changes});
export const response=(value=context(),status=200)=>new Response(JSON.stringify(value),{status,headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}});
