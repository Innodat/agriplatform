import type {FocusEventHandler} from 'react';
/** Fixed DMY text grammar. Calendar selection is a value conversion, never a locale guess. */
export function dateEntryValue(text:string):string|null{
 const match=/^ *([0-9]{1,2})\/([0-9]{1,2})\/([0-9]{4}) *$/.exec(text);if(!match)return null;
 const day=Number(match[1]),month=Number(match[2]),year=Number(match[3]);if(year<1||month<1||month>12||day<1)return null;
 const date=new Date(0);date.setUTCFullYear(year,month-1,day);date.setUTCHours(0,0,0,0);
 return date.getUTCFullYear()===year&&date.getUTCMonth()===month-1&&date.getUTCDate()===day?`${match[3]}-${String(month).padStart(2,'0')}-${String(day).padStart(2,'0')}`:null;
}
export function dateEntryProblem(text:string):string|null{return /^ *$/.test(text)||dateEntryValue(text)!==null?null:'Complete a valid date as day/month/year. Your entered text is preserved.';}
export function DateEntry({id,label,value,onChange,onBlur,error,disabled=false}:{id:string;label:string;value:string;onChange:(value:string)=>void;onBlur?:FocusEventHandler<HTMLInputElement>;error?:string|null;disabled?:boolean}){
 return <div className="date-entry"><label htmlFor={id}>{label}</label><div className="date-entry-controls"><input id={id} type="text" inputMode="numeric" value={value} onChange={e=>onChange(e.target.value)} onBlur={onBlur} disabled={disabled} aria-invalid={!!error} aria-describedby={`${id}-hint${error?' '+id+'-error':''}`}/><label className="date-calendar">Calendar<span className="task-sr-only"> for {label.toLowerCase()}</span><input type="date" aria-label={`Calendar for ${label.toLowerCase()}`} value={dateEntryValue(value)??''} disabled={disabled} onChange={e=>{if(e.target.value===''){onChange('');return;}const match=/^([0-9]{4})-([0-9]{2})-([0-9]{2})$/.exec(e.target.value);if(match)onChange(`${match[3]}/${match[2]}/${match[1]}`);}}/></label></div><p id={`${id}-hint`} className="field-hint">Day/month/year</p>{error&&<p id={`${id}-error`} className="field-error">{error}</p>}</div>;
}
export function DateRange({start,end}:{start:Parameters<typeof DateEntry>[0];end:Parameters<typeof DateEntry>[0]}){return <fieldset className="date-range"><legend>Dates</legend><DateEntry {...start}/><DateEntry {...end}/></fieldset>;}
